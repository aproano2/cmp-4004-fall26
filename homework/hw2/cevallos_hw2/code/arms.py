"""Arm runners: A (hand), B / B' (LLM -> CNF -> DPLL, B' with solver-only feedback), C (direct).

Protocol notes
- B' attempt 1 is *the same call* as B (same prompt/seed -> same cached response), so B' >= B by construction
  and the B vs B' delta is a paired comparison.
- The refinement loop only ever sees solver/validator messages. Ground truth is never passed in.
  `DECODE_ERROR` feedback uses only the solver model + the variable convention stated in the prompt.
- Every attempt is kept in `trace` so the refinement analysis can see what happened in rounds 1..3.
"""
import json, os
from time import perf_counter

import llm
from encoding import (encode_graph, expected_num_vars, decode_with_diagnosis, assignment_is_valid,
                      structural_issues, violated_edges)
from prompts import translation_prompt, direct_prompt, extract_json
from sat_solver import solve, validate_cnf, unsat_core

SOLVER_TIMEOUT_S = float(os.getenv("SOLVER_TIMEOUT_S", "5"))
# Failures that the *pipeline itself* reports (no ground truth needed).
ANNOUNCED = {"PARSE_ERROR", "SCHEMA_ERROR", "UNSAT", "TIMEOUT", "DECODE_ERROR"}


def _outcome(answer, correct):
    return "no-answer" if answer is None else ("correct" if correct else "incorrect")


def _totals(trace, t0):
    llm_t = sum(r.get("llm_time_s", 0.0) for r in trace)
    real_llm = sum(r.get("llm_time_s", 0.0) for r in trace if not r.get("cached"))
    solver_t = sum(r.get("solver_time_s", 0.0) for r in trace)
    overhead = max(0.0, (perf_counter() - t0) - real_llm)
    pt = sum(r.get("prompt_tokens", 0) for r in trace)
    ct = sum(r.get("completion_tokens", 0) for r in trace)
    return {"llm_time_s": llm_t, "solver_time_s": solver_t, "wall_time_s": llm_t + overhead,
            "prompt_tokens": pt, "completion_tokens": ct, "tokens": pt + ct,
            "all_cached": bool(trace) and all(r.get("cached") for r in trace)}


# ------------------------------------------------------------------ A
def run_hand(problem):
    t0 = perf_counter()
    nv, clauses = encode_graph(problem)
    s = solve(nv, clauses, SOLVER_TIMEOUT_S)
    answer = decode_with_diagnosis(problem, s["model"])[0] if s["status"] == "SAT" else None
    correct = bool(answer) and assignment_is_valid(problem, answer)
    rec = {"arm": "A", "answer": answer, "status": s["status"], "correct": correct,
           "outcome": _outcome(answer, correct), "attempts": 1, "trajectory": s["status"],
           "announced_failure": False, "violated_edges": 0,
           "raw_output": json.dumps({"num_vars": nv, "clauses": clauses}), "trace": []}
    rec.update({"llm_time_s": 0.0, "solver_time_s": s["time_s"], "wall_time_s": perf_counter() - t0,
                "prompt_tokens": 0, "completion_tokens": 0, "tokens": 0, "all_cached": False})
    return rec


# ------------------------------------------------------------------ B / B'
def _evaluate_translation(problem, raw, feedback_level):
    out = {"status": None, "detail": "", "feedback": None, "answer": None, "solver_time_s": 0.0}
    try:
        obj = extract_json(raw)
    except ValueError as exc:
        out.update(status="PARSE_ERROR", detail=str(exc), feedback=f"La salida no es JSON válido: {exc}")
        return out
    expected = expected_num_vars(problem)
    try:
        nv, clauses = obj["num_vars"], obj["clauses"]
        validate_cnf(nv, clauses)
        if nv != expected:
            raise ValueError(f"num_vars debe ser {expected} (3 por vértice) y fue {nv}")
    except KeyError as exc:
        out.update(status="SCHEMA_ERROR", detail=f"falta la clave {exc}", feedback=f"Falta la clave {exc} en el JSON.")
        return out
    except ValueError as exc:
        out.update(status="SCHEMA_ERROR", detail=str(exc), feedback=f"CNF inválida: {exc}")
        return out
    s = solve(nv, clauses, SOLVER_TIMEOUT_S)
    out["solver_time_s"] = s["time_s"]
    if s["status"] == "TIMEOUT":
        out.update(status="TIMEOUT", detail="timeout", feedback=f"El solver excedió el límite de {SOLVER_TIMEOUT_S:g} s.")
    elif s["status"] == "UNSAT":
        msg = "El solver devolvió UNSAT: las cláusulas no tienen ninguna solución."
        if feedback_level == "rich":
            t1 = perf_counter()
            core = unsat_core(nv, clauses)
            out["solver_time_s"] += perf_counter() - t1
            msg += f" Un subconjunto de cláusulas ya insatisfacible (índices desde 0): {core}."
        out.update(status="UNSAT", detail="unsat", feedback=msg)
    else:
        answer, issues = decode_with_diagnosis(problem, s["model"])
        if issues:
            out.update(status="DECODE_ERROR", detail="; ".join(issues),
                       feedback="El solver devolvió SAT pero el modelo no se interpreta como un coloreado: "
                                + "; ".join(issues[:6]) + ".")
        else:
            out.update(status="SAT", answer=answer)
    return out


def run_hybrid(problem, refinement=False, max_attempts=3, temperature=0.0, seed=0, feedback_level="basic"):
    t0 = perf_counter()
    allowed = max_attempts if refinement else 1
    feedback = previous = None
    trace, answer = [], None
    for attempt in range(1, allowed + 1):
        call = llm.call_llm(translation_prompt(problem, feedback, previous), temperature, seed)
        raw = call.get("response", "")
        rec = {"attempt": attempt, "raw_output": raw, "feedback_in": feedback,
               "prompt_tokens": call.get("prompt_tokens", 0), "completion_tokens": call.get("completion_tokens", 0),
               "llm_time_s": call.get("llm_time_s", 0.0), "cached": call.get("cached", False),
               "done_reason": call.get("done_reason", ""), "solver_time_s": 0.0}
        if call.get("error"):
            rec.update(status="LLM_ERROR", detail=call["error"]); trace.append(rec); break
        ev = _evaluate_translation(problem, raw, feedback_level)
        rec.update(status=ev["status"], detail=ev["detail"], solver_time_s=ev["solver_time_s"], feedback_out=ev["feedback"])
        trace.append(rec)
        if ev["status"] == "SAT":                # nothing the solver can complain about -> stop
            answer = ev["answer"]
            rec["answer_valid"] = assignment_is_valid(problem, answer)
            break
        feedback, previous = ev["feedback"], raw
    final = trace[-1]
    correct = bool(answer) and assignment_is_valid(problem, answer)
    rec = {"arm": "B_prime" if refinement else "B", "answer": answer, "status": final["status"], "correct": correct,
           "outcome": _outcome(answer, correct), "attempts": len(trace),
           "trajectory": ">".join(r["status"] for r in trace),
           "announced_failure": (not correct) and final["status"] in ANNOUNCED,
           "violated_edges": len(violated_edges(problem, answer)) if answer else "",
           "raw_output": final["raw_output"], "trace": trace, "error": final.get("detail") if final["status"] == "LLM_ERROR" else ""}
    rec.update(_totals(trace, t0))
    return rec


# ------------------------------------------------------------------ C
def _normalise_colors(obj):
    if not isinstance(obj, dict):
        return obj
    return {str(k).strip(): (str(v).strip().lower() if isinstance(v, str) else v) for k, v in obj.items()}


def run_direct(problem, temperature=0.0, seed=0):
    t0 = perf_counter()
    call = llm.call_llm(direct_prompt(problem), temperature, seed)
    raw = call.get("response", "")
    answer, status, detail = None, "ANSWER", ""
    if call.get("error"):
        status, detail = "LLM_ERROR", call["error"]
    else:
        try:
            obj = extract_json(raw).get("colors")
            obj = _normalise_colors(obj)
            issues = structural_issues(problem, obj)
            if issues:
                status, detail = "SCHEMA_ERROR", "; ".join(issues)
            else:
                answer = obj
        except ValueError as exc:
            status, detail = "PARSE_ERROR", str(exc)
    correct = bool(answer) and assignment_is_valid(problem, answer)
    trace = [{"attempt": 1, "status": status, "detail": detail, "raw_output": raw, "cached": call.get("cached", False),
              "prompt_tokens": call.get("prompt_tokens", 0), "completion_tokens": call.get("completion_tokens", 0),
              "llm_time_s": call.get("llm_time_s", 0.0), "solver_time_s": 0.0, "done_reason": call.get("done_reason", "")}]
    rec = {"arm": "C", "answer": answer, "status": status, "correct": correct, "outcome": _outcome(answer, correct),
           "attempts": 1, "trajectory": status,
           # C "announces" a failure only through schema checks; an answer that parses but breaks an edge is silent.
           "announced_failure": (not correct) and status in {"PARSE_ERROR", "SCHEMA_ERROR", "LLM_ERROR"},
           "violated_edges": len(violated_edges(problem, answer)) if answer else "",
           "raw_output": raw, "trace": trace, "error": detail}
    rec.update(_totals(trace, t0))
    return rec
