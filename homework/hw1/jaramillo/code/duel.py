"""Parte 2 - el duelo. Las mismas 80 instancias, tres sistemas:

    classical   A* con la heurística Manhattan admisible
    llm         el modelo solo, con la instancia como texto
    tool        el modelo + nuestro A* como herramienta (llamada en JSON)

Se corre desde la carpeta del deber (Ollama debe estar abierto, ver README.md):

    python code/duel.py                         # qwen2.5:3b, 10 por nivel
    python code/duel.py --model qwen2.5:1.5b    # modelo más pequeño
    python code/duel.py --backend manual --per-level 5

Se puede reanudar: cada llamada al modelo queda en .llm_cache/, así que si se
corta, al volver a correrlo sigue donde quedó.

Escribe results/duel_runs.csv, duel_summary.csv, repro.csv y failures.md.

Los prompts están en inglés a propósito: es el idioma en que mejor rinde un
modelo pequeño, y el validador busca las etiquetas PATH: y COST:.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from domains import (all_instances, make_problem, admissible_h, render_grid,   # noqa: E402
                     render_puzzle, is_solvable, GridProblem, EightPuzzle, TERRAIN)
from search import astar                                                     # noqa: E402
from validator import validate, parse_reply, CATEGORIES                      # noqa: E402
from llm import LLM                                                          # noqa: E402

RESULTS = Path(__file__).resolve().parent.parent / "results"
MAX_TURNS = 4                 # brazo tool: máximo 4 turnos del modelo por instancia
REPRO_INSTANCE = ("grid", 8, 0)

ANSWER_FORMAT = (
    "Format your final answer as exactly two lines:\n"
    "PATH: <letters U/D/L/R, no separators>\n"
    "COST: <integer>\n"
)


# ---------------------------------------------------------------------------
# Prompts (en inglés, ver nota arriba)
# ---------------------------------------------------------------------------

def instance_text(domain, inst):
    if domain == "grid":
        return (
            "Find the minimum-cost path from S to G on this grid.\n"
            "Terrain costs: '.' = 1, ',' = 3, '~' = 8. Entering G costs 1.\n"
            "The cost of a path is the sum of the costs of every cell you enter "
            "(the starting cell S is not counted).\n"
            "Moves: U (up), D (down), L (left), R (right). No diagonal moves, "
            "and you cannot leave the grid.\n"
            f"Grid ({len(inst)} rows x {len(inst[0])} columns, cells separated "
            "by spaces):\n" + render_grid(inst) + "\n"
        )
    return (
        "Solve this 8-puzzle in the minimum number of moves.\n"
        "'_' is the blank. A move slides the blank one cell: U (blank goes up), "
        "D (down), L (left), R (right). The blank cannot leave the 3x3 board.\n"
        "Every move costs 1, so the cost is the number of moves.\n"
        "Start:\n" + render_puzzle(inst) + "\n"
        "Goal:\n1 2 3\n4 5 6\n7 8 _\n"
    )


def prompt_llm(domain, inst):
    return instance_text(domain, inst) + "\n" + ANSWER_FORMAT


TOOL_SYSTEM = (
    "You can call one tool, astar_solve, an exact A* solver that returns the "
    "optimal path and its cost.\n"
    "To call it, reply with ONLY one JSON object and nothing else:\n"
    '  grid:     {"tool": "astar_solve", "domain": "grid", "grid": ["S.,", "~.G"]}\n'
    "            (one string per row, copy every cell, no spaces)\n"
    '  8-puzzle: {"tool": "astar_solve", "domain": "puzzle", '
    '"state": [1, 2, 3, 4, 5, 6, 7, 0, 8]}\n'
    "            (the 9 cells row by row, 0 for the blank)\n"
    "You will receive the tool result as JSON. Then give your final answer.\n"
    "Never write the tool result yourself: you do not know the answer until "
    "the tool replies.\n"
)
# Historia de este prompt (ver REPORT.md, "Dónde pudimos haber sido injustos"):
# la primera versión pedía en el MISMO mensaje llamar a la herramienta y el
# formato de la respuesta final; el modelo se inventaba el "tool_result" y
# contestaba de una vez. Ahora el primer mensaje solo pide la llamada y el
# formato de respuesta se da después del resultado.


# ---------------------------------------------------------------------------
# La herramienta
# ---------------------------------------------------------------------------

def extract_json(text):
    """Primer objeto JSON que aparezca en la respuesta, o None."""
    dec = json.JSONDecoder()
    for i, ch in enumerate(text or ""):
        if ch == "{":
            try:
                obj, _ = dec.raw_decode(text[i:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    return None


def extract_call(text):
    """La llamada a la herramienta dentro de una respuesta, o None. Se prefiere
    un objeto con "tool": "astar_solve"; si no hay, se acepta uno que traiga
    los argumentos ("grid" o "state"). Un objeto inventado como
    {"tool_result": ...} NO es una llamada."""
    dec, found = json.JSONDecoder(), []
    for i, ch in enumerate(text or ""):
        if ch == "{":
            try:
                obj, _ = dec.raw_decode(text[i:])
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                found.append(obj)
    for obj in found:
        if obj.get("tool") == "astar_solve":
            return obj
    for obj in found:
        if "grid" in obj or "state" in obj:
            return obj
    return None


def run_tool(call):
    """Corre A* sobre los argumentos QUE ESCRIBIÓ EL MODELO (no sobre la
    instancia real: si el modelo copia mal la instancia, la herramienta resuelve
    otro problema y el validador lo detecta). Devuelve
    (dict_resultado, instancia_leída o None)."""
    # Tolerancia (igual que el parser de PATH): si falta "domain" se deduce de
    # los argumentos, y el grid puede venir como lista de filas o como un solo
    # string con saltos de línea. Lo que NO se arregla es el contenido: si las
    # celdas están mal copiadas, se resuelve lo que el modelo escribió.
    domain = call.get("domain")
    if domain not in ("grid", "puzzle"):
        domain = "grid" if "grid" in call else "puzzle" if "state" in call else None
    try:
        if domain == "grid":
            rows = call["grid"]
            if isinstance(rows, str):
                rows = rows.replace("\\n", "\n").splitlines()
            grid = [str(row).replace(" ", "") for row in rows]
            if not grid or len({len(r) for r in grid}) != 1:
                return {"error": "rows must all have the same length"}, None
            flat = "".join(grid)
            if flat.count("S") != 1 or flat.count("G") != 1:
                return {"error": "grid needs exactly one S and one G"}, None
            if set(flat) - set(TERRAIN):
                return {"error": "unknown cell symbols"}, None
            inst, problem = grid, GridProblem(grid)
        elif domain == "puzzle":
            state = tuple(int(v) for v in call["state"])
            if sorted(state) != list(range(9)):
                return {"error": "state must contain 0..8 exactly once"}, None
            if not is_solvable(state):
                return {"error": "this state cannot reach the goal"}, None
            inst, problem = state, EightPuzzle(state)
        else:
            return {"error": "domain must be 'grid' or 'puzzle'"}, None
    except (KeyError, TypeError, ValueError) as e:
        return {"error": f"bad arguments: {e}"}, None
    r = astar(problem, admissible_h(domain))
    return {"path": "".join(r.path), "cost": r.cost,
            "expansions": r.expansions}, inst


# ---------------------------------------------------------------------------
# Los tres brazos
# ---------------------------------------------------------------------------

def base_row(arm, domain, level, idx, verdict, latency, tin, tout, status):
    return {"arm": arm, "domain": domain, "level": level, "instance": idx,
            "category": verdict.category, "detail": verdict.detail,
            "path": verdict.path or "", "reported_cost": verdict.reported_cost,
            "true_cost": verdict.true_cost, "optimal_cost": verdict.optimal_cost,
            "latency_s": round(latency, 6), "tokens_in": tin, "tokens_out": tout,
            "status": status, "tool_calls": "", "tool_args_match": "",
            "tool_expansions": ""}


def arm_classical(domain, level, idx, inst, optimum):
    r = astar(make_problem(domain, inst), admissible_h(domain))
    v = validate(domain, inst, "".join(r.path), r.cost, optimum.cost)
    row = base_row("classical", domain, level, idx, v, r.time_s, "", "", r.status)
    row["tool_expansions"] = r.expansions
    return row


def arm_llm(model, domain, level, idx, inst, optimum):
    rec = model.chat([{"role": "user", "content": prompt_llm(domain, inst)}])
    path, cost = parse_reply(rec["text"])
    v = validate(domain, inst, path, cost, optimum.cost)
    if rec["status"] != "ok":
        v.detail = f"{rec['status']} del modelo"
    return base_row("llm", domain, level, idx, v, rec["latency_s"],
                    rec["tokens_in"], rec["tokens_out"], rec["status"])


def arm_tool(model, domain, level, idx, inst, optimum):
    messages = [{"role": "system", "content": TOOL_SYSTEM},
                {"role": "user", "content": instance_text(domain, inst) + "\n" +
                 "Call the tool now: reply with ONLY the JSON object."}]
    latency, tin, tout = 0.0, 0, 0
    calls, match, expansions, status, text = 0, "", 0, "ok", ""
    true_inst = list(inst) if domain == "grid" else tuple(inst)
    for _ in range(MAX_TURNS):
        rec = model.chat(messages)
        latency += rec["latency_s"]
        tin += rec["tokens_in"] or 0
        tout += rec["tokens_out"] or 0
        status, text = rec["status"], rec["text"]
        call = extract_call(text) if status == "ok" else None
        if not call:
            break                              # esta respuesta es la final
        calls += 1
        result, parsed = run_tool(call)
        if parsed is not None:
            match = (parsed == true_inst)
            expansions += result["expansions"]
        messages = messages + [
            {"role": "assistant", "content": text},
            {"role": "user", "content": "TOOL RESULT: " + json.dumps(result) + (
                "\nFix the call and send the JSON again." if "error" in result
                else "\nNow give your final answer.\n" + ANSWER_FORMAT)}]
    path, cost = parse_reply(text)
    v = validate(domain, inst, path, cost, optimum.cost)
    if status != "ok":
        v.detail = f"{status} del modelo"
    row = base_row("tool", domain, level, idx, v, latency, tin, tout, status)
    row.update({"tool_calls": calls, "tool_args_match": match,
                "tool_expansions": expansions})
    return row


def reproducibility(model):
    """Una instancia, cinco llamadas idénticas, se cuentan las respuestas
    distintas. Se hace dos veces: temperatura 0 (semilla fija) y temperatura 0.8
    (semilla = número de llamada, porque con semilla fija Ollama se repite por
    construcción)."""
    domain, level, idx = REPRO_INSTANCE
    inst = [i for d, lv, k, i in all_instances() if (d, lv, k) == REPRO_INSTANCE][0]
    optimum = astar(make_problem(domain, inst), admissible_h(domain))
    prompt = [{"role": "user", "content": prompt_llm(domain, inst)}]
    rows = []
    for temp in (0.0, 0.8):
        for rep in range(5):
            seed = 0 if temp == 0.0 else rep
            rec = model.chat(prompt, temperature=temp, seed=seed, rep=rep)
            path, cost = parse_reply(rec["text"])
            v = validate(domain, inst, path, cost, optimum.cost)
            rows.append({"system": "llm", "domain": domain, "level": level,
                         "instance": idx, "temperature": temp, "call": rep + 1,
                         "path": path or "", "reported_cost": cost,
                         "category": v.category})
    for rep in range(5):                      # el lado clásico, misma prueba
        r = astar(make_problem(domain, inst), admissible_h(domain))
        rows.append({"system": "classical", "domain": domain, "level": level,
                     "instance": idx, "temperature": "", "call": rep + 1,
                     "path": "".join(r.path), "reported_cost": r.cost,
                     "category": "correct"})
    return rows


# ---------------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------------

def write_csv(name, rows):
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  escrito results/{name} ({len(rows)} filas)")


def summarize(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["arm"], r["domain"], r["level"]), []).append(r)
        groups.setdefault((r["arm"], r["domain"], "all"), []).append(r)
        groups.setdefault((r["arm"], "both", "all"), []).append(r)
    out = []
    for (arm, domain, level), rs in groups.items():
        row = {"arm": arm, "domain": domain, "level": level, "n": len(rs)}
        for c in CATEGORIES:
            row[c] = sum(r["category"] == c for r in rs)
        row["optimal_path_rate"] = round((row["correct"] + row["wrong_cost"]) / len(rs), 3)
        row["fully_correct_rate"] = round(row["correct"] / len(rs), 3)
        lat = [float(r["latency_s"]) for r in rs]
        row["latency_median_s"] = round(float(np.median(lat)), 6)
        row["latency_p95_s"] = round(float(np.percentile(lat, 95)), 6)
        toks = [(r["tokens_in"] or 0) + (r["tokens_out"] or 0) for r in rs
                if r["tokens_in"] != ""]
        row["tokens_median"] = int(np.median(toks)) if toks else ""
        exps = [r["tool_expansions"] for r in rs if r["tool_expansions"] != ""]
        row["expansions_median"] = float(np.median(exps)) if exps else ""
        out.append(row)
    return out


def write_failures(rows, repro, model):
    lines = [f"# Ejemplos de fallas ({model.backend} / {model.model})", "",
             "Un ejemplo por (sistema, categoría de falla), tomado de "
             "`duel_runs.csv`. Las respuestas completas están en `.llm_cache/`.", ""]
    for arm in ("llm", "tool"):
        for cat in CATEGORIES[1:]:
            hits = [r for r in rows if r["arm"] == arm and r["category"] == cat]
            lines.append(f"## {arm} - {cat}: {len(hits)} de "
                         f"{sum(r['arm'] == arm for r in rows)}")
            if hits:
                r = hits[0]
                lines.append(f"- {r['domain']} nivel {r['level']} instancia "
                             f"{r['instance']}: PATH `{r['path']}`, costo reportado "
                             f"{r['reported_cost']}, costo real {r['true_cost']}, "
                             f"óptimo {r['optimal_cost']}. {r['detail']}")
            lines.append("")
    tool = [r for r in rows if r["arm"] == "tool"]
    if tool:
        lines += ["## brazo tool - cómo se usó la herramienta",
                  f"- instancias sin llamada a la herramienta: "
                  f"{sum(r['tool_calls'] == 0 for r in tool)} de {len(tool)}",
                  f"- herramienta llamada con la instancia mal copiada: "
                  f"{sum(r['tool_args_match'] is False for r in tool)} de {len(tool)}",
                  ""]
    for temp in (0.0, 0.8):
        ans = {(r["path"], r["reported_cost"]) for r in repro
               if r["system"] == "llm" and r["temperature"] == temp}
        lines.append(f"- reproducibilidad, temperatura {temp}: {len(ans)} respuestas "
                     f"distintas en 5 llamadas")
    (RESULTS / "failures.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  escrito results/failures.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ollama", choices=["ollama", "manual"])
    ap.add_argument("--model", default="qwen2.5:3b")
    ap.add_argument("--per-level", type=int, default=10)
    args = ap.parse_args()
    model = LLM(args.backend, args.model)

    todo = [t for t in all_instances() if t[2] < args.per_level]
    rows = []
    for n, (domain, level, idx, inst) in enumerate(todo, 1):
        optimum = astar(make_problem(domain, inst), admissible_h(domain))
        rows.append(arm_classical(domain, level, idx, inst, optimum))
        rows.append(arm_llm(model, domain, level, idx, inst, optimum))
        rows.append(arm_tool(model, domain, level, idx, inst, optimum))
        print(f"[{n}/{len(todo)}] {domain} nivel {level} #{idx}: "
              f"llm={rows[-2]['category']}  tool={rows[-1]['category']}", flush=True)
    repro = reproducibility(model)

    write_csv("duel_runs.csv", rows)
    write_csv("duel_summary.csv", summarize(rows))
    write_csv("repro.csv", repro)
    write_failures(rows, repro, model)
    stale = model.prune()
    if stale:
        print(f"  .llm_cache: borrados {stale} transcripts de corridas anteriores "
              f"que ya no respaldan ningún resultado")
    print("Listo. Ahora corre:  python code/plots.py")


if __name__ == "__main__":
    main()
