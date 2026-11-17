"""Arm C (Direct): the LLM answers from the natural-language problem, no solver.

    python code/arm_c.py F01 --out results/pilot_c_f01.jsonl
    python code/arm_c.py --out results/arm_c_raw.jsonl

Same protocol as arm B (see README_B.md): same public `statement` and
`answer_format`, same model (qwen2.5:3b), temperature 0, seed 0, 4096 output
tokens, one run per problem, same Ollama cache (`arm_b.complete`). Never reads
problems/ground_truth/. Writes ungraded JSONL; grade it with evaluate_c.py.

Parsing. The answer is first parsed strictly (json.loads of the whole reply,
exactly as arm B's parser). If that fails, the first {...} block in the reply is
extracted (lenient mode), so a Markdown fence does not cost C an answer it
actually gave. `parse_mode` records which one worked: strict | extracted | failed.

Detectability without ground truth. The only checks possible without the
reference answer are format checks against the PUBLIC answer_format: reply is
parseable, every key is present, every value is in allowed_values. They are
recorded as `format_errors`; an answer that passes them has no internal signal.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
from pathlib import Path

from arm_b import PUBLIC, ROOT, complete

# Prompt v2. Pilot v1 (results/pilot_c_f01.jsonl) showed the model copying the
# answer_format structure ({"keys": ..., "allowed_values": ...}) instead of answering;
# v2 adds a skeleton built only from the PUBLIC keys. Fixed before the full run.
PROMPT = """Resuelve el siguiente problema razonando internamente.
Devuelve solo un objeto JSON válido, sin Markdown ni explicaciones.
La respuesta NO repite answer_format: es un objeto plano con exactamente estas claves,
reemplazando cada "?" por uno de los valores permitidos para esa clave:
{skeleton}

Enunciado:
{statement}

answer_format (claves y valores permitidos):
{answer_format}
"""


def prompt_for(problem):
    skeleton = "{" + ", ".join(f'"{k}": "?"' for k in problem["answer_format"]["keys"]) + "}"
    return PROMPT.format(statement=problem["statement"], skeleton=skeleton,
                         answer_format=json.dumps(problem["answer_format"], ensure_ascii=False))


def parse_answer(text):
    """Return (answer | None, parse_mode)."""
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value, "strict"
    except (json.JSONDecodeError, TypeError):
        pass
    match = re.search(r"\{.*?\}", text or "", re.DOTALL)
    if match:
        try:
            value = json.loads(match.group(0))
            if isinstance(value, dict):
                return value, "extracted"
        except json.JSONDecodeError:
            pass
    return None, "failed"


def _norm(v):
    return str(v).strip().upper()


def format_errors(answer, answer_format):
    """Checks that need only the public answer_format, never the ground truth."""
    if answer is None:
        return ["unparseable"]
    errors = []
    allowed = answer_format["allowed_values"]
    for key in answer_format["keys"]:
        if key not in answer:
            errors.append(f"missing:{key}")
        elif _norm(answer[key]) not in {_norm(v) for v in allowed[key]}:
            errors.append(f"out_of_domain:{key}={answer[key]}")
    return errors


def run_problem(problem, args, call=complete):
    messages = [{"role": "user", "content": prompt_for(problem)}]
    start = time.perf_counter()
    try:
        response = call(messages, args.model, args.temperature, args.seed, args.timeout, args.url)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        elapsed = time.perf_counter() - start
        return {"problem_id": problem["id"], "difficulty": problem["difficulty"], "arm": "C",
                "answer": None, "parse_mode": "llm_error", "format_errors": [],
                "solver_status": "llm_error", "attempts": 1, "llm_s": elapsed, "solver_s": 0,
                "wall_s": elapsed, "tokens_in": None, "tokens_out": None, "model": args.model,
                "seed": args.seed, "temperature": args.temperature,
                "error_message": f"{type(exc).__name__}: {exc}", "text": "", "done_reason": None}
    call_elapsed = time.perf_counter() - start
    answer, mode = parse_answer(response["text"])
    errors = format_errors(answer, problem["answer_format"])
    # Same timing rule as B: original inference time, even when replayed from cache.
    wall_s = response["llm_s"] + time.perf_counter() - start - call_elapsed
    return {"problem_id": problem["id"], "difficulty": problem["difficulty"], "arm": "C",
            "answer": answer, "parse_mode": mode, "format_errors": errors, "solver_status": "none",
            "attempts": 1, "llm_s": response["llm_s"], "solver_s": 0, "wall_s": wall_s,
            "tokens_in": response.get("tokens_in"), "tokens_out": response.get("tokens_out"),
            "model": response.get("model", args.model), "seed": args.seed,
            "temperature": args.temperature, "error_message": "; ".join(errors),
            "text": response["text"], "done_reason": response.get("done_reason")}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ids", nargs="*", help="problem IDs (default: all)")
    parser.add_argument("--model", default="qwen2.5:3b")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--url", default=os.environ.get("OLLAMA_URL", "http://localhost:11434"))
    parser.add_argument("--out", type=Path, default=ROOT / "results/arm_c_raw.jsonl")
    args = parser.parse_args(argv)
    problems = json.loads(PUBLIC.read_text(encoding="utf-8"))["problems"]
    if args.ids:
        unknown = set(args.ids) - {p["id"] for p in problems}
        if unknown:
            parser.error(f"unknown problem IDs: {', '.join(sorted(unknown))}")
        problems = [p for p in problems if p["id"] in args.ids]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as out:  # never overwrite results
        for problem in problems:
            rec = run_problem(problem, args)
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            print(f"{problem['id']}: parse={rec['parse_mode']} format_errors={rec['format_errors']} "
                  f"llm_s={rec['llm_s']:.1f}", flush=True)


if __name__ == "__main__":
    main()
