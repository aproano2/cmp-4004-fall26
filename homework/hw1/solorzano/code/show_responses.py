"""Muestra el texto que escribió el modelo (guardado en .llm_cache/) detrás de cada fila de un CSV del duelo
    python show_responses.py                                   #filas sin respuesta legible de duel_llm.csv
    python show_responses.py --category illegal_path --limit 5
    python show_responses.py --csv ../results/duel_tool.csv --category all
En el brazo con herramienta también muestra qué le pasó el modelo a A* (y si coincide con el problema real), qué devolvió A* y la respuesta final del modelo. Así se ve en qué paso falló: no llamó a la herramienta, copió mal el problema o copió mal la
respuesta. El resultado se guarda en results/<nombre>_responses.txt.
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from duel_problems import build_instances, get
from llm import DEFAULT_CACHE, read_record
from prompts import NATIVE_SYSTEM, TOOL_INSTRUCTIONS, llm_messages, problem_text
from run_duel import normalize_grid, normalize_start

RESULTS = Path(__file__).resolve().parent.parent / "results"


def load_cache(cache_dir):
    recs = []
    for f in Path(cache_dir).glob("*.json"):
        try:
            recs.append(read_record(f))
        except (ValueError, KeyError):
            continue
    return recs


def reply_summary(text, rec, tail):
    extra = ""
    if text.count("{") > text.count("}"):
        extra += ", JSON opened but never closed (likely cut off)"
    if "eval_count" in rec:
        extra += f", tokens generated {rec['eval_count']}, done_reason={rec.get('done_reason')}"
    return f"    reply: {len(text)} characters, {len(text.split())} words{extra}\n    ...{text[-tail:]}"


def same_problem(inst, args):
    if not isinstance(args, dict):
        return "args not an object"
    if inst["domain"] == "8puzzle":
        got = normalize_start(args.get("start"))
        return "matches the problem" if got == list(inst["start"]) else f"DIFFERENT board: {got}"
    got = normalize_grid(args.get("grid"))
    if got == list(inst["rows"]):
        return "matches the problem"
    if not isinstance(got, list):
        return f"not a list of rows: {str(got)[:80]}"
    bad = [i for i, (a, b) in enumerate(zip(got, inst["rows"])) if a != b]
    return (f"DIFFERENT grid: {len(got)} rows (real {len(inst['rows'])}), "
            f"{len(bad)} rows differ{f' (first: row {bad[0]})' if bad else ''}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(RESULTS / "duel_llm.csv"))
    ap.add_argument("--category", default="unparseable", help="a category name, or 'all'")
    ap.add_argument("--limit", type=int, default=0, help="0 = all rows")
    ap.add_argument("--tail", type=int, default=600, help="characters to show from the end of each reply")
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--temperature", type=float, default=0.0, help="of the run the CSV came from")
    ap.add_argument("--seed", type=int, default=0, help="of the run the CSV came from")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    csv_path = Path(a.csv)
    out = Path(a.out) if a.out else RESULTS / (csv_path.stem.replace("duel_", "") + "_responses.txt")
    df = pd.read_csv(csv_path)
    arm = str(df.arm.iloc[0]) if len(df) else "llm"
    if a.category != "all":
        df = df[df.category == a.category]
    if a.limit:
        df = df.head(a.limit)

    #only the calls of THIS run: repro.py reuses the same prompts with other seeds/temperatures
    recs = [x for x in load_cache(a.cache_dir)
            if float(x.get("temperature", 0.0)) == a.temperature and int(x.get("seed", 0)) == a.seed]
    instances = build_instances()
    lines, lengths = [], []

    for _, r in df.iterrows():
        inst = get(instances, r.domain, int(r.level), int(r.instance_id))
        head = f"=== {r.key} | {r.category} | {r.detail}"
        if arm != "tool":
            want = json.dumps(llm_messages(inst), sort_keys=True)
            match = [x for x in recs if json.dumps(x["messages"], sort_keys=True) == want]
            if not match:
                lines.append(f"{head}\n    no cached reply found\n")
                continue
            text = match[0]["response"]
            lengths.append(len(text))
            lines.append(f"{head}\n{reply_summary(text, match[0], a.tail)}\n")
            continue

        #tool arm: every cached turn of this conversation, shortest first
        system = NATIVE_SYSTEM if str(r.get("tool_protocol", "native")) != "text" else TOOL_INSTRUCTIONS
        user = problem_text(inst)
        turns = sorted((x for x in recs if len(x["messages"]) >= 2
                        and x["messages"][0].get("content") == system
                        and x["messages"][1].get("content") == user),
                       key=lambda x: len(x["messages"]))
        if not turns:
            lines.append(f"{head}\n    no cached conversation found\n")
            continue
        block = [head]
        for t in turns:
            for call in t.get("tool_calls") or []:
                block.append(f"    tool call -> {same_problem(inst, call.get('arguments'))}")
            tool_msgs = [m for m in t["messages"] if m.get("role") == "tool"]
            if tool_msgs and t is turns[-1]:
                block.append(f"    A* returned: {tool_msgs[-1]['content'][:300]}")
        final = turns[-1]
        if not final.get("tool_calls"):
            lengths.append(len(final["response"]))
            block.append(reply_summary(final["response"], final, a.tail))
        lines.append("\n".join(block) + "\n")

    if lengths:
        s = pd.Series(lengths)
        lines.insert(0, f"{len(df)} rows. Final reply length in characters: min {s.min()}, "
                        f"median {int(s.median())}, max {s.max()}\n")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(lines[0] if lines else "no rows")
    print("wrote", out)

if __name__ == "__main__":
    main()
