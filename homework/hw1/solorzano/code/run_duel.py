"""Corre un sistema sobre las 80 instancias y guarda una fila por instancia en un CSV.

Sistemas (--arm):
- classical: búsqueda de la Parte 1, revisada con el mismo validador que el LLM. --solver astar (por defecto, la referencia de óptimo) o bfs (para mostrar que el
validador marca a BFS como "legal pero subóptimo" en los grids)
- llm: el modelo solo, recibe el problema en texto y responde
- tool: el modelo puede llamar a nuestro A*. Escribe la llamada en JSON, nosotros corremos la búsqueda con los argumentos que él escribió (si copia mal, cuenta como su error) y le devolvemos el resultado. Máximo MAX_TOOL_ROUNDS llamadas por instancia
  --tool-protocol native (por defecto): herramientas nativas de Ollama -> duel_tool.csv
  --tool-protocol text: v1, la herramienta descrita en el prompt -> duel_tool_text.csv

Ejemplos:
    python run_duel.py --arm classical
    python run_duel.py --arm llm  --backend ollama --model qwen2.5:3b
    python run_duel.py --arm tool --backend ollama --model qwen2.5:3b
    python run_duel.py --arm llm  --backend manual --n-per-level 5
"""
import argparse
import csv
import time
from pathlib import Path

from duel_problems import (build_instances, check_grid,
                           index_moves_to_letters, select, solvable8,
                           solve_8puzzle, solve_grid)
from gridworld import GridProblem
from llm import DEFAULT_CACHE, LLM, BackendError, BackendUnavailable
from prompts import (NATIVE_TOOLS, llm_messages, native_tool_messages,
                     native_tool_result_messages, tool_messages,
                     tool_result_message)
from search import EightPuzzle, search
from validator import (normalized_path, parse_answer, parse_tool_call,
                       validate)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
MAX_TOOL_ROUNDS = 2
FIELDS = ["arm", "solver", "tool_protocol", "backend", "model", "domain", "level", "instance_id", "key", "category",
          "cost_reported_ok", "optimal_cost", "actual_cost", "reported_cost", "detail", "answer",
          "tool_used", "tool_calls", "tool_errors", "n_llm_calls", "latency_s", "cache_hits"]


#the tool
def normalize_start(start):
    """Accept the board as 9 numbers, as a 3x3 nested list, or as text like '1 2 3 / 4 _ 6 ...'.
    Only formatting is forgiven; wrong numbers are passed through and rejected or solved as given."""
    if isinstance(start, str):
        toks = [t for t in start.replace("_", " 0 ").replace(",", " ").split() if t.lstrip("-").isdigit()]
        return [int(t) for t in toks]
    if isinstance(start, list) and start and all(isinstance(r, list) for r in start):
        start = [v for r in start for v in r]
    if isinstance(start, list):
        try:
            return [int(v) for v in start]
        except (TypeError, ValueError):
            return start
    return start


def normalize_grid(rows):
    """Accept the rows with or without the spaces shown in the prompt, or one multi-line string."""
    if isinstance(rows, str):
        rows = [r for r in rows.splitlines() if r.strip()]
    if isinstance(rows, list) and all(isinstance(r, str) for r in rows):
        return ["".join(r.split()) for r in rows]
    return rows


def run_tool(domain, args):
    """Run Part-1 A* on the arguments the model wrote. -> (result_dict, is_error)."""
    try:
        if not isinstance(args, dict):
            raise ValueError("`args` must be a JSON object")
        if domain == "8puzzle":
            start = normalize_start(args.get("start"))
            if not isinstance(start, list) or sorted(start) != list(range(9)):
                raise ValueError("`start` must list the numbers 0..8 exactly once (9 numbers)")
            if not solvable8(tuple(start)):
                raise ValueError("this 8-puzzle configuration is unsolvable")
            moves, cost, _ = solve_8puzzle(start)
            return {"path": moves, "cost": cost}, False
        rows = normalize_grid(args.get("grid"))
        check_grid(rows)
        cells, cost, _ = solve_grid(rows)
        return {"path": [list(c) for c in cells], "cost": cost}, False
    except (ValueError, TypeError, KeyError) as e:
        return {"error": str(e)}, True


#arms
def classical_answer(inst, solver):
    if solver == "astar":
        if inst["domain"] == "8puzzle":
            moves, cost, _ = solve_8puzzle(inst["start"])
            return {"path": moves, "cost": cost}
        cells, cost, _ = solve_grid(inst["rows"])
        return {"path": [list(c) for c in cells], "cost": cost}
    # BFS from Part 1 (search.py, fifo frontier)
    if inst["domain"] == "8puzzle":
        node, _ = search(EightPuzzle(tuple(inst["start"])), "fifo")
        return {"path": index_moves_to_letters(inst["start"], node.path()), "cost": node.g}
    problem = GridProblem(inst["rows"])
    node, _ = search(problem, "fifo")
    cells = [problem.initial]
    for m in node.path():
        cells.append(problem.result(cells[-1], m))
    return {"path": [list(c) for c in cells], "cost": node.g}


def run_classical(inst, solver):
    t0 = time.perf_counter()
    answer = classical_answer(inst, solver)
    return answer, {"latency_s": time.perf_counter() - t0, "n_llm_calls": 0, "tool_used": "",
                    "tool_calls": 0, "tool_errors": 0, "cache_hits": 0}


def run_llm(inst, llm, seed):
    text = llm.chat(llm_messages(inst), seed=seed)
    return parse_answer(text), {"latency_s": llm.last["latency_s"], "n_llm_calls": 1, "tool_used": False,
                                "tool_calls": 0, "tool_errors": 0, "cache_hits": int(llm.last["cached"])}


def run_tool_arm(inst, llm, seed):
    messages = tool_messages(inst)
    calls = errors = hits = n_llm = 0
    latency = 0.0
    answer = None
    while True:
        text = llm.chat(messages, seed=seed)
        n_llm += 1
        hits += int(llm.last["cached"])
        latency += llm.last["latency_s"]
        call = parse_tool_call(text)
        if call is None or call.get("tool") != "astar" or calls >= MAX_TOOL_ROUNDS:
            answer = parse_answer(text)          #final answer (or no usable answer)
            break
        calls += 1
        result, is_err = run_tool(inst["domain"], call.get("args"))
        errors += int(is_err)
        messages = messages + [{"role": "assistant", "content": text}, tool_result_message(result)]
    return answer, {"latency_s": latency, "n_llm_calls": n_llm, "tool_used": calls > 0,
                    "tool_calls": calls, "tool_errors": errors, "cache_hits": hits}


def run_tool_arm_native(inst, llm, seed):
    """Tool arm with Ollama's native tool calling (default)."""
    tools = NATIVE_TOOLS[inst["domain"]]
    messages = native_tool_messages(inst)
    calls = errors = hits = n_llm = 0
    latency = 0.0
    answer = None
    while True:
        text = llm.chat(messages, seed=seed, tools=tools)
        n_llm += 1
        hits += int(llm.last["cached"])
        latency += llm.last["latency_s"]
        native = llm.last.get("tool_calls") or []
        call = native[0] if native else None
        if call is None:                                  #the model may also write the call as text
            t = parse_tool_call(text)
            if t is not None and t.get("tool") == "astar":
                call = {"name": "astar", "arguments": t.get("args", {})}
        if call is None or calls >= MAX_TOOL_ROUNDS:
            answer = parse_answer(text)                   #final answer
            break
        calls += 1
        result, is_err = run_tool(inst["domain"], call.get("arguments"))
        errors += int(is_err)
        messages = messages + native_tool_result_messages(text, call, result)
    return answer, {"latency_s": latency, "n_llm_calls": n_llm, "tool_used": calls > 0,
                    "tool_calls": calls, "tool_errors": errors, "cache_hits": hits}


#main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["classical", "llm", "tool"], required=True)
    ap.add_argument("--solver", choices=["astar", "bfs"], default="astar", help="classical arm only")
    ap.add_argument("--tool-protocol", choices=["native", "text"], default="native",
                    help="tool arm: native = Ollama tool calling (default); text = v1, tool described in the prompt")
    ap.add_argument("--backend", default="ollama", choices=["ollama", "manual"])
    ap.add_argument("--model", default="qwen2.5:3b")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--timeout", type=int, default=600, help="seconds per LLM call")
    ap.add_argument("--n-per-level", type=int, default=None, help="use 5 for the manual backend")
    ap.add_argument("--domains", nargs="+", default=["8puzzle", "grid"])
    ap.add_argument("--levels", nargs="+", type=int, default=None)
    ap.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    ap.add_argument("--results-dir", default=str(RESULTS_DIR))
    ap.add_argument("--out", default=None, help="output CSV name (default duel_<arm>.csv)")
    ap.add_argument("--only-category", default=None,
                    help="with --from-csv: run only the instances that got this category there")
    ap.add_argument("--from-csv", default=None, help="a previous duel CSV (for --only-category)")
    a = ap.parse_args()

    if a.backend == "mock" and (Path(a.results_dir).resolve() == RESULTS_DIR.resolve()
                                or Path(a.cache_dir).resolve() == DEFAULT_CACHE.resolve()):
        raise SystemExit("--backend mock is for testing only: pass --results-dir and --cache-dir "
                         "pointing to a temporary folder")
    insts = select(build_instances(), a.domains, a.levels, a.n_per_level)
    if a.only_category:
        if not a.from_csv or a.out is None:
            raise SystemExit("--only-category needs --from-csv and a new --out name")
        with open(a.from_csv, newline="", encoding="utf-8") as fh:
            keep = {row["key"] for row in csv.DictReader(fh) if row["category"] == a.only_category}
        insts = [i for i in insts if i["key"] in keep]
        print(f"re-running {len(insts)} instances that were '{a.only_category}' in {a.from_csv}")
    mock_fn = None
    
    llm = None if a.arm == "classical" else LLM(a.backend, a.model, a.cache_dir, a.temperature, a.seed,
                                                a.host, a.max_tokens, a.timeout, mock_fn)

    out_dir = Path(a.results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if a.arm == "tool" and a.backend == "manual" and a.tool_protocol == "native":
        raise SystemExit("the manual backend cannot do native tool calls: add --tool-protocol text")
    default_name = {"classical": f"duel_classical_{a.solver}.csv", "llm": "duel_llm.csv",
                    "tool": "duel_tool.csv" if a.tool_protocol == "native" else "duel_tool_text.csv"}[a.arm]
    name = a.out or default_name
    out_path = out_dir / name
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for k, inst in enumerate(insts, start=1):
            err = backend_msg = None
            try:
                if a.arm == "classical":
                    answer, meta = run_classical(inst, a.solver)
                elif a.arm == "llm":
                    answer, meta = run_llm(inst, llm, a.seed)
                elif a.tool_protocol == "native":
                    answer, meta = run_tool_arm_native(inst, llm, a.seed)
                else:
                    answer, meta = run_tool_arm(inst, llm, a.seed)
            except BackendUnavailable as e:
                raise SystemExit(f"\nSTOPPED: {e}\nRows written so far are in {out_path}; "
                                 "re-running continues from the cache.")
            except BackendError as e:
                #Ollama answers HTTP 500 "error parsing tool call" when the MODEL writes a malformed
                #tool call: that is the model's failure (no usable answer), not a timeout.
                backend_msg = str(e)
                low = backend_msg.lower()
                #Model failures that Ollama reports as HTTP 500: a malformed tool call, or the model
                #looping on the same tokens until Ollama aborts. Not timeouts.
                model_fault = "tool call" in low or "repeat limit" in low
                answer, err = None, (None if model_fault else "timeout")
                meta = {"latency_s": 0.0, "n_llm_calls": 0, "tool_used": "", "tool_calls": 0,
                        "tool_errors": 0, "cache_hits": 0}
                print(f"  ! {inst['key']}: {e}")
            res = validate(inst, answer, arm_error=err)
            if backend_msg:
                if "repeat limit" in backend_msg.lower():
                    res["detail"] = "model stuck repeating tokens (Ollama aborted): " + backend_msg[:150]
                elif err is None:
                    res["detail"] = "model wrote a malformed tool call: " + backend_msg[:150]
                else:
                    res["detail"] = backend_msg[:200]
            row = {"arm": a.arm, "solver": a.solver if a.arm == "classical" else "",
                   "tool_protocol": a.tool_protocol if a.arm == "tool" else "",
                   "backend": a.backend if llm else "", "model": a.model if llm else "",
                   "domain": inst["domain"], "level": inst["level"], "instance_id": inst["instance_id"],
                   "key": inst["key"], "answer": normalized_path(inst["domain"], answer)[:400], **res, **meta}
            w.writerow({f: row.get(f, "") for f in FIELDS})
            fh.flush()
            print(f"[{k}/{len(insts)}] {inst['key']:15s} {res['category']:20s}"
                  + ("  (cache)" if meta.get("cache_hits") else f"  {meta['latency_s']:.1f}s"))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
