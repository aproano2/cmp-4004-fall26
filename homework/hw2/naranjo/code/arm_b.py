"""Run paired B and B' against Ollama; never reads ground truth.

Writes ungraded JSONL records. Evaluate separately with evaluate_b.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from csp_spec import SpecError, solve

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "problems/public/problems.json"
CACHE = ROOT / ".llm_cache"
PROMPT = """Traduce el problema a un CSP. Devuelve solo un objeto JSON válido, sin Markdown.
Usa exactamente las claves y dominios de answer_format como variables de salida;
puedes añadir variables auxiliares si hacen falta. Codifica todas las reglas.
Formato: {{"variables": {{"X": [1, 2]}}, "constraints": [{{"id": "R1", "expr": "X != 1"}}]}}.
Cada expr usa sintaxis de expresión Python: + - * // %, comparaciones, and/or/not,
listas y funciones abs, min, max, alldiff(*variables), count(valor, *variables),
implies(condición, condición). Cadenas dentro de expr llevan comillas simples.
No uses funciones ni sintaxis fuera de esa lista.

Enunciado:
{statement}

answer_format:
{answer_format}
"""


def prompt_for(problem):
    return PROMPT.format(statement=problem["statement"],
                         answer_format=json.dumps(problem["answer_format"], ensure_ascii=False))


def complete(messages, model, temperature, seed, timeout, url, cache_dir=CACHE):
    body = {"model": model, "messages": messages, "stream": False,
            "options": {"temperature": temperature, "seed": seed, "num_predict": 4096}}
    key = hashlib.sha256(json.dumps({"url": url, "body": body}, sort_keys=True,
                                    ensure_ascii=False).encode()).hexdigest()
    path = cache_dir / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    req = urllib.request.Request(url.rstrip("/") + "/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.load(response)
    record = {"request": body, "text": data.get("message", {}).get("content", ""),
              "llm_s": time.perf_counter() - start,
              "tokens_in": data.get("prompt_eval_count"), "tokens_out": data.get("eval_count"),
              "done_reason": data.get("done_reason"), "model": data.get("model", model)}
    cache_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def run_solver(text):
    start = time.perf_counter()
    try:
        spec = json.loads(text)
        result = solve(spec, max_solutions=2)
        status = result["status"]
        answer = result["solutions"][0] if status in ("unique", "multiple") else None
        error = "" if answer is not None else f"solver returned {status}"
    except (json.JSONDecodeError, SpecError, ArithmeticError, TypeError, ValueError, RecursionError) as exc:
        status, answer, error = "spec_error", None, f"{type(exc).__name__}: {exc}"
    return {"solver_status": status, "answer": answer, "error": error,
            "solver_s": time.perf_counter() - start}


def run_problem(problem, args, call=complete):
    messages = [{"role": "user", "content": prompt_for(problem)}]
    attempts = []
    for iteration in range(4):
        start = time.perf_counter()
        try:
            response = call(messages, args.model, args.temperature, args.seed, args.timeout, args.url)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            elapsed = time.perf_counter() - start
            attempts.append({"text": "", "llm_s": elapsed, "wall_s": elapsed, "tokens_in": None, "tokens_out": None,
                             "solver_s": 0, "solver_status": "llm_error", "answer": None,
                             "error": f"{type(exc).__name__}: {exc}"})
            break  # A transport failure is not solver feedback.
        call_elapsed = time.perf_counter() - start
        attempt = {**response, **run_solver(response["text"])}
        # Use the original inference time even when a cached response is replayed.
        attempt["wall_s"] = response["llm_s"] + time.perf_counter() - start - call_elapsed
        attempts.append(attempt)
        if attempt["solver_status"] not in ("spec_error", "unsat") or iteration == 3:
            break
        messages = messages + [{"role": "assistant", "content": response["text"]},
                               {"role": "user", "content": attempt["error"]}]
    return attempts


def record(problem, arm, attempts, args):
    last = attempts[-1]
    def total(field):
        values = [a.get(field) for a in attempts]
        return sum(values) if all(v is not None for v in values) else None
    return {"problem_id": problem["id"], "difficulty": problem["difficulty"], "arm": arm,
            "answer": last["answer"], "solver_status": last["solver_status"],
            "attempts": len(attempts), "llm_s": total("llm_s"), "solver_s": total("solver_s"),
            "wall_s": total("wall_s"), "tokens_in": total("tokens_in"),
            "tokens_out": total("tokens_out"), "model": args.model, "seed": args.seed,
            "temperature": args.temperature, "error_message": last["error"],
            "attempt_log": attempts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids", nargs="*", help="problem IDs (default: all)")
    parser.add_argument("--model", default="qwen2.5:3b")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--url", default=os.environ.get("OLLAMA_URL", "http://localhost:11434"))
    parser.add_argument("--out", type=Path, default=ROOT / "results/arm_b_raw.jsonl")
    args = parser.parse_args(argv)
    problems = json.loads(PUBLIC.read_text(encoding="utf-8"))["problems"]
    if args.ids:
        unknown = set(args.ids) - {p["id"] for p in problems}
        if unknown:
            parser.error(f"unknown problem IDs: {', '.join(sorted(unknown))}")
        problems = [p for p in problems if p["id"] in args.ids]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental loss of experimental results.
    with args.out.open("x", encoding="utf-8") as out:
        for problem in problems:
            attempts = run_problem(problem, args)
            for arm, subset in (("B", attempts[:1]), ("B'", attempts)):
                out.write(json.dumps(record(problem, arm, subset, args), ensure_ascii=False) + "\n")
            out.flush()
            print(f"{problem['id']}: B={attempts[0]['solver_status']} B'={attempts[-1]['solver_status']} attempts={len(attempts)}", flush=True)


if __name__ == "__main__":
    main()
