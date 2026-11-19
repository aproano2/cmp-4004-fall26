"""Part 2 runner: LLM arm, tool-augmented arm, reproducibility test.

Examples (run from cevallos/code/):
    python run_duel.py --system llm  --backend anthropic --model <MODEL>
    python run_duel.py --system tool --backend anthropic --model <MODEL>
    python run_duel.py --system llm  --backend manual --per-level 5
    python run_duel.py --repro --system llm --backend anthropic --model <MODEL>
    python run_duel.py --import-responses responses.md

Outputs (append-safe, one row per call):
    results/duel_raw.csv      every attempt, with the validator's verdict
    results/duel_repro.csv    the 5-identical-calls experiment
    results/reference_optimal.csv   A* optimal cost for every instance
    .llm_cache/*.json         full transcripts
"""
import argparse
import csv
import sys

from duel_common import (RESULTS_DIR, SYSTEM, TOOL_SYSTEM, build_prompt,
                         execute_tool, load_instances, parse_answer,
                         parse_tool_call, reference_solution, validate)
from llm_backends import (NeedManual, get_backend, import_responses,
                          write_pending)

RAW_FIELDS = [
    "system", "backend", "model", "temperature", "domain", "level", "instance",
    "sample", "category", "parsed", "legal", "optimal", "cost_correct",
    "reported_cost", "true_cost", "ref_cost", "n_moves", "reason",
    "tool_calls", "tool_args_correct", "turns", "latency_s", "in_tokens",
    "out_tokens", "cached", "key",
]


# --------------------------------------------------------------------------
# One attempt
# --------------------------------------------------------------------------

def run_llm(backend, inst, ref_cost, sample=0):
    msgs = [{"role": "user", "content": build_prompt(inst)}]
    out = backend.call(SYSTEM, msgs, sample)
    v = validate(inst, out["text"], ref_cost)
    return v, dict(tool_calls=0, tool_args_correct="", turns=1,
                   latency_s=out["latency_s"], in_tokens=out["in_tokens"],
                   out_tokens=out["out_tokens"], cached=out["cached"],
                   key=out["key"], text=out["text"])


def run_tool(backend, inst, ref_cost, sample=0, max_calls=2):
    """Model emits a JSON tool call -> we run YOUR A* -> we send the result back."""
    msgs = [{"role": "user", "content": build_prompt(inst)}]
    calls, matches = 0, []
    lat, tin, tout, cached, first_key = 0.0, 0, 0, True, None
    for turn in range(max_calls + 2):
        out = backend.call(TOOL_SYSTEM, msgs, sample)
        first_key = first_key or out["key"]
        lat += out["latency_s"] or 0
        tin += out["in_tokens"] or 0
        tout += out["out_tokens"] or 0
        cached &= out["cached"]
        text = out["text"]
        call = parse_tool_call(text)
        if parse_answer(text) is None and call and calls < max_calls:
            calls += 1
            result, match = execute_tool(inst, call)
            matches.append(match)
            msgs += [{"role": "assistant", "content": text},
                     {"role": "user", "content": "Tool result:\n" + __import__("json").dumps(result)}]
            continue
        break
    v = validate(inst, text, ref_cost)
    return v, dict(tool_calls=calls,
                   tool_args_correct=(all(matches) if matches else ""),
                   turns=turn + 1, latency_s=lat, in_tokens=tin,
                   out_tokens=tout, cached=cached, key=first_key, text=text)


def make_row(system, backend, inst, sample, v, extra):
    return dict(system=system, backend=backend.name, model=backend.model,
                temperature=backend.temperature, domain=inst["domain"],
                level=inst["level"], instance=inst["idx"], sample=sample,
                category=v["category"], parsed=v["parsed"], legal=v["legal"],
                optimal=v["optimal"], cost_correct=v["cost_correct"],
                reported_cost=v["reported_cost"], true_cost=v["true_cost"],
                ref_cost=v["ref_cost"], n_moves=v["n_moves"], reason=v["reason"],
                **{k: extra[k] for k in ("tool_calls", "tool_args_correct", "turns",
                                         "latency_s", "in_tokens", "out_tokens",
                                         "cached", "key")})


# --------------------------------------------------------------------------
# Reference (ground truth) file
# --------------------------------------------------------------------------

def write_reference(instances):
    RESULTS_DIR.mkdir(exist_ok=True)
    refs = {}
    with open(RESULTS_DIR / "reference_optimal.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["domain", "level", "instance", "optimal_cost", "optimal_length"])
        for inst in instances:
            cost, path = reference_solution(inst)
            if inst["domain"] == "puzzle":
                assert cost == inst["level"], "puzzle depth mismatch: bug in instance or A*"
            refs[(inst["domain"], inst["level"], inst["idx"])] = cost
            w.writerow([inst["domain"], inst["level"], inst["idx"], cost, len(path)])
    return refs


def save_rows(rows, name, fields):
    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def load_rows(name):
    p = RESULTS_DIR / name
    if not p.exists():
        return []
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--system", choices=["llm", "tool"], default="llm")
    ap.add_argument("--backend", choices=["manual", "ollama", "anthropic"], default="manual")
    ap.add_argument("--model", default="")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--per-level", type=int, default=10)
    ap.add_argument("--domains", nargs="+", default=["puzzle", "grid"])
    ap.add_argument("--repro", action="store_true",
                    help="5 identical calls on one instance per domain")
    ap.add_argument("--repro-n", type=int, default=5)
    ap.add_argument("--import-responses", metavar="FILE")
    a = ap.parse_args()

    if a.import_responses:
        print(f"imported {import_responses(a.import_responses)} responses")
        return

    # Ground truth for ALL 10 instances/level, regardless of --per-level.
    all_inst = [i for d in ("puzzle", "grid") for i in load_instances(d, 10)]
    refs = write_reference(all_inst)

    backend = get_backend(a.backend, a.model, a.temperature)
    runner = run_llm if a.system == "llm" else run_tool
    label = "LLM" if a.system == "llm" else "LLM+A*"

    pending, new_rows = [], []

    if a.repro:
        # Fixed choice: the first instance of the 3rd difficulty level of each domain
        # (puzzle depth 12, grid 12x12). Change it only if you say so in the report.
        for d in a.domains:
            insts = load_instances(d, 10)
            levels = sorted({i["level"] for i in insts})
            inst = next(i for i in insts if i["level"] == levels[2] and i["idx"] == 0)
            ref = refs[(d, inst["level"], inst["idx"])]
            for s in range(a.repro_n):
                try:
                    v, ex = runner(backend, inst, ref, sample=s)
                except NeedManual as n:
                    pending.append(n)
                    continue
                r = make_row(label, backend, inst, s, v, ex)
                r["answer_key"] = v["answer_key"]
                new_rows.append(r)
        fields = RAW_FIELDS + ["answer_key"]
        old = [r for r in load_rows("duel_repro.csv")
               if not (r["system"] == label and r["model"] == backend.model
                       and float(r["temperature"]) == backend.temperature)]
        save_rows(old + new_rows, "duel_repro.csv", fields)
        for d in a.domains:
            ks = {r["answer_key"] for r in new_rows if r["domain"] == d}
            print(f"[{d}] {len(ks)} distinct answers in "
                  f"{sum(r['domain'] == d for r in new_rows)} calls")
    else:
        for d in a.domains:
            for inst in load_instances(d, a.per_level):
                ref = refs[(d, inst["level"], inst["idx"])]
                try:
                    v, ex = runner(backend, inst, ref)
                except NeedManual as n:
                    pending.append(n)
                    continue
                new_rows.append(make_row(label, backend, inst, 0, v, ex))
                print(f"{d:6} L{inst['level']:>2} #{inst['idx']}: {v['category']:16} {v['reason']}")
        # keep rows from other (system, model, temperature) combos; replace this one
        old = [r for r in load_rows("duel_raw.csv")
               if not (r["system"] == label and r["model"] == backend.model
                       and float(r["temperature"]) == backend.temperature
                       and r["domain"] in a.domains)]
        save_rows(old + new_rows, "duel_raw.csv", RAW_FIELDS)
        print(f"\nsaved {len(new_rows)} rows -> results/duel_raw.csv")

    if pending:
        p = write_pending(pending)
        print(f"\n{len(pending)} prompts need a manual reply -> open {p}")
        print("Paste replies into responses.md as '### <KEY>' blocks, then:")
        print("  python run_duel.py --import-responses responses.md  (and re-run the same command)")
        sys.exit(2)


if __name__ == "__main__":
    main()
