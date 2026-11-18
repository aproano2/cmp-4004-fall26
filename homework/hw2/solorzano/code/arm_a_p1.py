"""HW2 - Arm A (hand-written models)
Each model is written by hand from the natural-language statement, in the exact JSON schema that logic_lm.build_csp accepts (alldiff / neq / eq)

The gold answers live in problems/problems_p1.json and were derived by hand independently of these models. validate_problems.py checks that each model has exactly one solution and that it equals the gold.

"""
import csv
import json
import sys
import time
from pathlib import Path
from csp import backtrack_search
from logic_lm import build_csp
HERE = Path(__file__).resolve().parent
BANK = HERE.parent / "problems" / "problems_p1.json"

#helpers
def V(names, domain):
    return {n: list(domain) for n in names}
def alldiff(*vs):
    return {"type": "alldiff", "vars": list(vs)}
def is_(x, value):
    return {"type": "eq", "a": x, "b": value}
def not_(x, *values):
    return [{"type": "neq", "a": x, "b": v} for v in values]

def differs(x, y):
    return {"type": "neq", "a": x, "b": y}

#7 hand-written models
def m_q01():  # coworkers -> drink
    ppl = ["Dana", "Eric", "Fay", "Gus"]
    return {"variables": V(ppl, ["coffee", "tea", "juice", "water"]),
            "constraints": [alldiff(*ppl), is_("Dana", "tea"),
                            *not_("Eric", "coffee", "water"),
                            *not_("Fay", "water"), *not_("Gus", "juice")]}

def m_q02():  # plants -> shelf (1 = top, 4 = bottom)
    plants = ["Fern", "Cactus", "Orchid", "Ivy"]
    return {"variables": V(plants, [1, 2, 3, 4]),
            "constraints": [alldiff(*plants), is_("Ivy", 4),
                            *not_("Cactus", 1, 2), *not_("Fern", 2)]}

def m_q03():  # rooms -> colour, repeats allowed (NO alldiff)
    rooms = [f"Room{i}" for i in range(1, 6)]
    return {"variables": V(rooms, ["cream", "mint", "sky"]),
            "constraints": [is_("Room1", "cream"),
                            differs("Room2", "Room1"), *not_("Room2", "sky"),
                            *not_("Room3", "cream", "mint"),
                            differs("Room4", "Room3"), *not_("Room4", "mint"),
                            differs("Room5", "Room4"), *not_("Room5", "sky")]}

def m_q04():  # students -> position 1..6
    st = ["Hana", "Ivo", "Jun", "Kai", "Lia", "Moe"]
    return {"variables": V(st, range(1, 7)),
            "constraints": [alldiff(*st), is_("Jun", 1), is_("Ivo", 6),
                            *not_("Lia", 3, 4, 5), *not_("Hana", 4, 5),
                            *not_("Moe", 4)]}

def m_q05():  # guests -> seat 1..3, one alldiff PER TABLE
    t1, t2 = ["Ann", "Ben", "Cat"], ["Dan", "Eve", "Fay"]
    return {"variables": V(t1 + t2, [1, 2, 3]),
            "constraints": [alldiff(*t1), alldiff(*t2), is_("Cat", 1),
                            *not_("Ann", 3), differs("Dan", "Cat"),
                            differs("Eve", "Ann"), differs("Fay", "Ben"),
                            *not_("Dan", 3)]}

def m_q06():  # 4x4 mini-sudoku
    cell = lambda r, c: f"R{r}C{c}"
    cells = [cell(r, c) for r in range(1, 5) for c in range(1, 5)]
    rows = [alldiff(*[cell(r, c) for c in range(1, 5)]) for r in range(1, 5)]
    cols = [alldiff(*[cell(r, c) for r in range(1, 5)]) for c in range(1, 5)]
    boxes = [alldiff(*[cell(r, c) for r in (br, br + 1) for c in (bc, bc + 1)])
             for br in (1, 3) for bc in (1, 3)]
    givens = [is_("R1C1", 1), is_("R2C2", 4), is_("R2C4", 2),
              is_("R3C3", 4), is_("R3C4", 3), is_("R4C1", 4)]
    return {"variables": V(cells, [1, 2, 3, 4]),
            "constraints": rows + cols + boxes + givens}

def m_q07():  # stations -> channel, repeats allowed; neq per overlapping pair
    towns = ["Arden", "Brook", "Cliff", "Dale", "Elm", "Fern", "Glen", "Heath"]
    edges = [("Arden", "Brook"), ("Arden", "Cliff"), ("Arden", "Dale"),
             ("Brook", "Cliff"), ("Brook", "Dale"), ("Cliff", "Dale"),
             ("Elm", "Brook"), ("Elm", "Cliff"), ("Elm", "Dale"),
             ("Fern", "Cliff"), ("Fern", "Dale"), ("Fern", "Elm"),
             ("Glen", "Dale"), ("Glen", "Elm"), ("Glen", "Fern"),
             ("Heath", "Elm"), ("Heath", "Fern"), ("Heath", "Glen")]
    # 'tallest antenna' is a distractor: no constraint.
    return {"variables": V(towns, [1, 2, 3, 4]),
            "constraints": [differs(a, b) for a, b in edges] +
                           [is_("Arden", 1), is_("Brook", 2), is_("Cliff", 3)]}

MODELS = {f"q{n:02d}": globals()[f"m_q{n:02d}"] for n in range(1, 8)}

def load_bank(path=BANK):
    with open(path, encoding="utf-8") as fh:
        return {p["id"]: p for p in json.load(fh)["puzzles"]}

def run(out_csv=None):
    """Arm A runner with the instrumentation HW2 asks for. Arm A has no LLM, so
    llm_time and tokens are 0; solver_time is measured separately."""
    bank = load_bank()
    rows, solved = [], 0
    print(f"  {'id':<5}{'level':<8}{'result':<10}{'calls':>6}{'solver_s':>10}")
    for pid, make in MODELS.items():
        t0 = time.perf_counter()
        sol, counter = backtrack_search(build_csp(make()), use_fc=True, use_mrv=True)
        dt = time.perf_counter() - t0
        gold = bank[pid]["gold"]
        if sol in (None, "TIMEOUT"):
            result = "no_answer"
        else:
            result = "correct" if sol == gold else "incorrect"
        solved += result == "correct"
        rows.append({"id": pid, "arm": "A", "level": bank[pid]["level"],
                     "result": result, "wall_clock_s": round(dt, 6),
                     "llm_time_s": 0.0, "solver_time_s": round(dt, 6),
                     "tokens_in": 0, "tokens_out": 0,
                     "solver_calls": counter["calls"]})
        print(f"  {pid:<5}{bank[pid]['level']:<8}{result:<10}"
              f"{counter['calls']:>6}{dt:>10.5f}")
    print(f"\n  Arm A: {solved}/{len(MODELS)} correct")
    if out_csv:
        with open(out_csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"  wrote {out_csv}")
    return rows

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)
