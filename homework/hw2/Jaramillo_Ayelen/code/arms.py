"""Los cuatro brazos del duelo: A (a mano), B (híbrido), B′ (híbrido con
auto-refinamiento) y C (directo).

Regla de oro del brazo B′: al modelo solo se le devuelve el MENSAJE DEL SOLVER
(o del parser). Nunca la respuesta correcta, nunca "tu respuesta está mal", y
tampoco si la solución es única o no: el bucle se detiene en cuanto el solver
devuelve una solución, sea correcta o no. Así la mejora de B a B′ mide solo si
el error del solver sirve como señal de aprendizaje.
"""
import json
import time

from csp_solver import solve
from spec import (ParseError, SchemaError, ScopeError, build_csp, grade_assignment,
                  parse_answer_json, parse_spec_json)

SOLVER_LIMIT = 200_000
MAX_REFINE = 3                # rondas de corrección después del primer intento

# Ejemplo resuelto (NO pertenece al banco): se da igual a B y a C.
EXAMPLE_PUZZLE = """Three houses stand in a row, numbered 1 to 3 from left to right. Each house has a different owner and a different colour.
Owners: Zoe, Yuri, Xena.
Colours: pink, grey, brown.
Clues:
1. Zoe lives in the grey house.
2. The pink house is immediately to the left of Yuri's house.
3. Xena's house is not house 1.
Give the house number of every owner and every colour."""

EXAMPLE_SPEC = """{"variables": {"Zoe": [1, 2, 3], "Yuri": [1, 2, 3], "Xena": [1, 2, 3],
               "pink": [1, 2, 3], "grey": [1, 2, 3], "brown": [1, 2, 3]},
 "constraints": [
  {"type": "alldiff", "vars": ["Zoe", "Yuri", "Xena"]},
  {"type": "alldiff", "vars": ["pink", "grey", "brown"]},
  {"type": "eq", "a": "Zoe", "b": "grey"},
  {"type": "offset", "a": "Yuri", "b": "pink", "k": 1},
  {"type": "neq", "a": "Xena", "b": 1}
 ]}"""

EXAMPLE_ANSWER = '{"Zoe": 1, "grey": 1, "Xena": 2, "pink": 2, "Yuri": 3, "brown": 3}'

SYSTEM_B = ("You translate logic puzzles into constraint satisfaction problems (CSP) "
            "written in JSON. You never solve the puzzle yourself.")

PROMPT_B = """Translate the puzzle into a CSP in JSON. Do not solve it. Output only the JSON object.

Rules:
- Make one variable for every person, colour and pet named in the puzzle, using the names exactly as written.
- The value of every variable is a house number, so every domain is the list of house numbers [1, ..., N].
- Use only these constraint types:
  {{"type": "alldiff", "vars": ["A", "B", ...]}}    the listed variables all take different values
  {{"type": "eq", "a": "A", "b": "B"}}              A equals variable B (or "b": 3 for A equals the number 3)
  {{"type": "neq", "a": "A", "b": "B"}}             A differs from variable B (or "b": 3 for A is not 3)
  {{"type": "lt", "a": "A", "b": "B"}}              A < B (A is somewhere to the left of B)
  {{"type": "next_to", "a": "A", "b": "B"}}         |A - B| = 1 (A and B are neighbours)
  {{"type": "offset", "a": "A", "b": "B", "k": 1}}  A = B + k (with k = 1: A is immediately to the right of B)

Example puzzle:
{example}

Example JSON:
{example_spec}

Puzzle:
{puzzle}

JSON:"""

SYSTEM_C = "You are good at solving logic puzzles."

PROMPT_C = """Solve the puzzle. You may reason briefly first. End your reply with one JSON object that maps every person, colour and pet to its house number.

Example puzzle:
{example}

Example final answer:
{example_answer}

Puzzle:
{puzzle}"""

FEEDBACK = {
    "parse": "The JSON could not be parsed: {err}. Output the complete corrected JSON object only.",
    "schema": "The JSON is not a CSP in the required format: {err}. Output the complete corrected JSON object only.",
    "scope": "The solver rejected a constraint: {err}. Output the complete corrected JSON object only.",
    "unsat": ("The solver proved that your constraints have NO solution, so at least one "
              "constraint does not match the puzzle. Re-read the clues, fix the constraints "
              "and output the complete corrected JSON object only."),
    "timeout": ("The solver timed out on your CSP. Re-read the clues, fix the constraints "
                "and output the complete corrected JSON object only."),
}


def b_messages(puzzle):
    return [{"role": "system", "content": SYSTEM_B},
            {"role": "user", "content": PROMPT_B.format(example=EXAMPLE_PUZZLE,
                                                        example_spec=EXAMPLE_SPEC,
                                                        puzzle=puzzle)}]


def c_messages(puzzle):
    return [{"role": "system", "content": SYSTEM_C},
            {"role": "user", "content": PROMPT_C.format(example=EXAMPLE_PUZZLE,
                                                        example_answer=EXAMPLE_ANSWER,
                                                        puzzle=puzzle)}]


# ----------------------------------------------------------- evaluar un modelo --
def evaluate_spec_reply(text, problem):
    """Pasa una respuesta (texto con el JSON del CSP) por parser + solver.

    stage: 'parse' | 'schema' | 'scope' | 'timeout' | 'unsat' | 'solved'
    Todo lo que no es 'solved' se detecta sin la respuesta correcta.
    """
    out = {"stage": None, "error": "", "n_solutions": 0, "solution": None,
           "solver_time_s": 0.0, "solver_calls": 0, "correct": False,
           "missing": [], "spec": None}
    try:
        spec = parse_spec_json(text)
        out["spec"] = spec
        csp = build_csp(spec)
    except ParseError as e:
        out.update(stage="parse", error=str(e))
        return out
    except SchemaError as e:
        out.update(stage="schema", error=str(e))
        return out
    except ScopeError as e:
        out.update(stage="scope", error=str(e))
        return out
    # max_solutions=2: además de resolver, sabemos si el modelo admite >1 solución
    res = solve(csp, max_solutions=2, limit=SOLVER_LIMIT)
    out["solver_time_s"], out["solver_calls"] = res["time_s"], res["calls"]
    if res["status"] == "timeout" and not res["solutions"]:
        out.update(stage="timeout", error=f"solver call limit {SOLVER_LIMIT} exceeded")
        return out
    if not res["solutions"]:
        out.update(stage="unsat", error="no solution exists")
        return out
    sol = res["solutions"][0]          # la que el sistema devolvería
    ok, mapped, missing = grade_assignment(sol, problem["gold"])
    out.update(stage="solved", n_solutions=len(res["solutions"]), solution=sol,
               correct=ok, missing=missing)
    return out


def coverage_ok(assign, problem):
    """Monitor SIN la respuesta correcta: ¿la asignación nombra a todos los
    elementos que el enunciado lista, con casas 1..N distintas dentro de cada
    grupo? Solo usa las listas del propio enunciado."""
    from spec import match_names, _num
    n = problem["n_houses"]
    for items in problem["groups"].values():
        m = match_names(items, list(assign))
        if any(v is None for v in m.values()):
            return False, "missing_items"
        vals = [_num(assign[m[x]]) for x in items]
        if any(not isinstance(v, int) or not 1 <= v <= n for v in vals):
            return False, "out_of_range"
        if len(set(vals)) != len(vals):
            return False, "duplicate_house"
    return True, ""


# ------------------------------------------------------------------- filas --
def base_row(arm, problem, temperature, seed, rep):
    return {"arm": arm, "problem": problem["id"], "level": problem["level"],
            "n_vars": problem["n_vars"], "n_clues": problem["n_clues"],
            "temperature": temperature, "seed": seed, "rep": rep,
            "outcome": "", "category": "", "stage": "", "detectable": "",
            "signal": "", "n_solutions": "", "llm_calls": 0, "iterations": 0,
            "tokens_in": 0, "tokens_out": 0, "prompt_chars": 0, "truncated": 0,
            "llm_time_s": 0.0, "solver_time_s": 0.0, "wall_s": 0.0,
            "error": "", "answer": ""}


def run_arm_a(problem):
    """Brazo A: el modelo escrito a mano (problems.json -> spec) y el solver."""
    t0 = time.perf_counter()
    ev = evaluate_spec_reply(json.dumps(problem["spec"]), problem)
    row = base_row("A", problem, "", "", 0)
    row.update(outcome="correct" if ev["correct"] else "incorrect",
               stage=ev["stage"], n_solutions=ev["n_solutions"],
               solver_time_s=ev["solver_time_s"], wall_s=time.perf_counter() - t0,
               answer=json.dumps(ev["solution"]))
    return row


def _account(row, rec, messages):
    row["llm_calls"] += 1
    row["tokens_in"] += rec.get("tokens_in") or 0
    row["tokens_out"] += rec.get("tokens_out") or 0
    row["prompt_chars"] += sum(len(m["content"]) for m in messages)
    row["llm_time_s"] += rec.get("latency_s") or 0.0
    row["truncated"] += rec.get("done_reason") == "length"  # se acabó max_tokens


def _fill_from_eval(row, ev, problem):
    row["stage"] = ev["stage"]
    row["n_solutions"] = ev["n_solutions"]
    row["error"] = ev["error"]
    if ev["stage"] != "solved":
        row["outcome"] = "no_answer"
        row["detectable"], row["signal"] = True, ev["stage"]
        return
    row["answer"] = json.dumps(ev["solution"])
    row["outcome"] = "correct" if ev["correct"] else "incorrect"
    # monitores sin verdad: unicidad y cobertura de nombres
    cov, why = coverage_ok(ev["solution"], problem)
    if ev["n_solutions"] > 1:
        row["signal"] = "non_unique"
    elif not cov:
        row["signal"] = why
    row["detectable"] = bool(row["signal"])


def run_arm_b(model, problem, temperature=0.0, seed=0, rep=0, max_refine=MAX_REFINE):
    """Brazos B y B′ en una sola pasada: B es el primer intento; B′ sigue
    con hasta `max_refine` rondas de corrección. Devuelve (fila_B, fila_B′,
    lista de intentos)."""
    messages = b_messages(problem["text"])
    rowb = base_row("B", problem, temperature, seed, rep)
    rowp = base_row("B'", problem, temperature, seed, rep)
    attempts = []
    t0 = time.perf_counter()
    for it in range(max_refine + 1):
        rec = model.chat(messages, temperature=temperature, seed=seed)
        _account(rowp, rec, messages)
        if rec["status"] != "ok":
            ev = {"stage": "llm_" + rec["status"], "error": rec["status"], "n_solutions": 0,
                  "solution": None, "solver_time_s": 0.0, "correct": False, "spec": None}
        else:
            ev = evaluate_spec_reply(rec["text"], problem)
        rowp["solver_time_s"] += ev["solver_time_s"]
        attempts.append({"iteration": it, "text": rec.get("text", ""), **ev})
        if it == 0:
            _account(rowb, rec, messages)
            rowb["solver_time_s"] = ev["solver_time_s"]
            rowb["wall_s"] = time.perf_counter() - t0
            _fill_from_eval(rowb, ev, problem)
        if ev["stage"] not in FEEDBACK or it == max_refine:
            break
        err = ev["error"]
        messages = messages + [{"role": "assistant", "content": rec["text"]},
                               {"role": "user", "content": FEEDBACK[ev["stage"]].format(err=err)}]
    rowp["wall_s"] = time.perf_counter() - t0
    rowp["iterations"] = len(attempts) - 1
    _fill_from_eval(rowp, attempts[-1], problem)
    return rowb, rowp, attempts


def run_arm_c(model, problem, temperature=0.0, seed=0, rep=0):
    """Brazo C: el modelo responde directo desde el enunciado."""
    messages = c_messages(problem["text"])
    row = base_row("C", problem, temperature, seed, rep)
    t0 = time.perf_counter()
    rec = model.chat(messages, temperature=temperature, seed=seed)
    _account(row, rec, messages)
    row["wall_s"] = time.perf_counter() - t0
    text = rec.get("text", "")
    try:
        ans = parse_answer_json(text)
    except ParseError as e:
        row.update(outcome="no_answer", stage="parse", error=str(e),
                   detectable=True, signal="parse")
        return row, text
    ok, mapped, missing = grade_assignment(ans, problem["gold"])
    row["answer"] = json.dumps(ans)
    cov, why = coverage_ok(ans, problem)
    if missing or not cov:
        # respuesta incompleta o imposible: se ve sin conocer la verdad
        row.update(outcome="no_answer" if missing else ("correct" if ok else "incorrect"),
                   stage="answered", detectable=True, signal=why or "missing_items")
        if ok:
            row["detectable"], row["signal"] = "", ""
        return row, text
    row.update(outcome="correct" if ok else "incorrect", stage="answered",
               detectable=False if not ok else "", signal="")
    return row, text
