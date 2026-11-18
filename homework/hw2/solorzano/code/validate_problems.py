"""HW2 - soundness check + difficulty metrics for a problem bank
 For EVERY problem it:

  1. checks the record (id, level, puzzle, gold) and that every gold variable
     name appears in the natural-language text (arms B/C must be able to name it);
  2. checks the arm-A model declares exactly the gold's variables and that each
     gold value is in its domain;
  3. enumerates ALL solutions of the arm-A model with an independent
     interpreter of the raw JSON spec (does not use csp.py nor logic_lm's
     _SpecCSP), and asserts there is EXACTLY ONE and that it equals the gold;
  4. re-solves with the course pipeline (build_csp + backtrack_search, fc+MRV,
     the same call classify_arm_b makes) and asserts it returns the gold;
  5. checks the declared level matches the difficulty rule (by #variables);
  6. writes the difficulty metrics to a CSV.

"""
import argparse
import csv
import importlib
import json
import math
import re
import sys
from pathlib import Path

from csp import backtrack_search
from logic_lm import build_csp

HERE = Path(__file__).resolve().parent
LEVELS = ("easy", "medium", "hard")

def level_for(n_vars):
    """Difficulty rule: number of variables the model must declare."""
    if n_vars <= 4:
        return "easy"
    if n_vars <= 6:
        return "medium"
    return "hard"

#independent enumerator
def _checks(spec):
    """Turn the raw spec into predicate checks, using the same semantics as
    build_csp (neq whose 'b' is a variable name is binary, else unary)."""
    names = set(spec["variables"])
    checks = []  #(vars_involved, predicate(assignment) -> bool)
    for con in spec.get("constraints", []):
        t = con["type"]
        if t == "alldiff":
            vs = list(con["vars"])
            for i, a in enumerate(vs):
                for b in vs[i + 1:]:
                    checks.append(((a, b), lambda s, a=a, b=b: s[a] != s[b]))
        elif t == "neq":
            a, b = con["a"], con["b"]
            if isinstance(b, str) and b in names:
                checks.append(((a, b), lambda s, a=a, b=b: s[a] != s[b]))
            else:
                checks.append(((a,), lambda s, a=a, b=b: s[a] != b))
        elif t == "eq":
            a, b = con["a"], con["b"]
            checks.append(((a,), lambda s, a=a, b=b: s[a] == b))
        else:
            raise ValueError(f"unknown constraint type {t!r}")
    return checks

def enumerate_solutions(spec, cap=1000):
    order = list(spec["variables"])
    pos = {v: i for i, v in enumerate(order)}
    checks = _checks(spec)
    due = {v: [] for v in order}
    for vars_, pred in checks:
        due[max(vars_, key=lambda v: pos[v])].append(pred)
    sols, assign = [], {}
    def rec(i):
        if len(sols) >= cap:
            return
        if i == len(order):
            sols.append(dict(assign))
            return
        v = order[i]
        for val in spec["variables"][v]:
            assign[v] = val
            if all(p(assign) for p in due[v]):
                rec(i + 1)
            del assign[v]
    rec(0)
    return sols

#metrics 
def metrics(spec, puzzle_text):
    cons = spec["constraints"]
    names = set(spec["variables"])
    kinds = {"alldiff": 0, "neq_var": 0, "neq_val": 0, "eq": 0}
    for c in cons:
        if c["type"] == "neq":
            b = c["b"]
            kinds["neq_var" if isinstance(b, str) and b in names else "neq_val"] += 1
        else:
            kinds[c["type"]] += 1
    doms = [len(d) for d in spec["variables"].values()]
    plain_sol, plain = backtrack_search(build_csp(spec), limit=2_000_000)
    fcmrv_sol, fcmrv = backtrack_search(build_csp(spec), use_fc=True, use_mrv=True)
    return {
        "n_vars": len(names),
        "n_constraints": len(cons),
        **{f"n_{k}": v for k, v in kinds.items()},
        "max_domain": max(doms),
        "log10_search_space": round(sum(math.log10(d) for d in doms), 2),
        "plain_bt_calls": plain["calls"],
        "fc_mrv_calls": fcmrv["calls"],
        "puzzle_words": len(puzzle_text.split()),
    }, fcmrv_sol

#per-problem verification
def verify_one(p, make_model):
    pid = p.get("id", "<?>")
    for field in ("id", "level", "puzzle", "gold"):
        assert field in p, f"{pid}: missing field {field!r}"
    assert p["level"] in LEVELS, f"{pid}: level must be one of {LEVELS}"

    words = set(re.findall(r"[A-Za-z0-9_]+", p["puzzle"]))
    missing = [v for v in p["gold"] if v not in words]
    assert not missing, f"{pid}: gold variables not named in the puzzle text: {missing}"

    spec = make_model()
    assert set(spec["variables"]) == set(p["gold"]), (
        f"{pid}: model variables {sorted(spec['variables'])} != gold keys {sorted(p['gold'])}")
    for v, val in p["gold"].items():
        assert val in spec["variables"][v], f"{pid}: gold {v}={val!r} not in domain"

    sols = enumerate_solutions(spec)
    assert len(sols) >= 1, f"{pid}: NO solution -- model is over-constrained"
    assert len(sols) == 1, f"{pid}: AMBIGUOUS -- {len(sols)} solutions, e.g. {sols[0]} / {sols[1]}"
    assert sols[0] == p["gold"], f"{pid}: unique solution {sols[0]} != gold {p['gold']}"

    m, sol = metrics(spec, p["puzzle"])
    assert sol == p["gold"], f"{pid}: backtrack_search returned {sol}, not the gold"

    expected = level_for(m["n_vars"])
    assert p["level"] == expected, (
        f"{pid}: declared level {p['level']!r} but rule gives {expected!r} (V={m['n_vars']})")
    return m

def load_models(module_names):
    models = {}
    for name in module_names:
        mod = importlib.import_module(name)
        dup = set(models) & set(mod.MODELS)
        if dup:
            raise SystemExit(f"FAIL duplicate model ids across modules: {sorted(dup)}")
        models.update(mod.MODELS)
    return models

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default=str(HERE.parent / "problems" / "problems_p1.json"))
    ap.add_argument("--models", nargs="+", default=["arm_a_p1"])
    ap.add_argument("--csv", default=str(HERE.parent / "results" / "difficulty_p1.csv"))
    args = ap.parse_args()

    with open(args.bank, encoding="utf-8") as fh:
        puzzles = json.load(fh)["puzzles"]
    models = load_models(args.models)

    ids = [p["id"] for p in puzzles]
    if len(set(ids)) != len(ids):
        sys.exit(f"FAIL duplicate puzzle ids: {ids}")
    no_model = [i for i in ids if i not in models]
    if no_model:
        sys.exit(f"FAIL no arm-A model for: {no_model}")

    rows, failed = [], 0
    for p in puzzles:
        try:
            m = verify_one(p, models[p["id"]])
        except AssertionError as e:
            print(f"  FAIL {e}")
            failed += 1
            continue
        rows.append({"id": p["id"], "level": p["level"], **m})
        print(f"  ok  {p['id']}  {p['level']:<6}  unique + matches gold  "
              f"V={m['n_vars']:<3} C={m['n_constraints']:<3} "
              f"log10|S|={m['log10_search_space']:<6} plain={m['plain_bt_calls']:<5} "
              f"fc+mrv={m['fc_mrv_calls']}")

    if rows:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  metrics -> {args.csv}")
        for lv in LEVELS:
            n = sum(r["level"] == lv for r in rows)
            print(f"  {lv:<6}: {n} problem(s)")

    if failed:
        print(f"\n{failed}/{len(puzzles)} problems UNSOUND")
        sys.exit(1)
    print(f"\nALL {len(puzzles)} PROBLEMS SOUND")

if __name__ == "__main__":
    main()
