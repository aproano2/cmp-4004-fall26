"""Verify the HW2 ground truth before anyone uses it to grade an arm.

    python code/verify_ground_truth.py            # all problems
    python code/verify_ground_truth.py D15 M08    # some problems

For every problem it checks, independently:
  1. the stored solution is inside the domains and satisfies every constraint;
  2. backtracking (MRV + forward checking, csp_spec.solve) enumerates ALL solutions
     and finds exactly one, equal to the stored one;
  3. plain brute force (itertools.product, no pruning, no shared search code)
     also finds exactly one, equal to the stored one;
  4. every natural-language rule is encoded by at least one constraint;
  5. the public file has the same ids and leaks no model/solution fields.

Note: checks 2 and 3 share the expression evaluator in csp_spec.py, so they
validate the search, not the translation. Whether each expression faithfully
encodes its sentence is the MANUAL review (see formulations.md).

Writes results/ground_truth_check.csv and exits with code 1 if anything fails.
"""
from __future__ import annotations

import csv
import itertools
import json
import sys
import time
from pathlib import Path

from csp_spec import FUNCS, _holds, check_assignment, load_spec, solve

ROOT = Path(__file__).resolve().parent.parent
GT = ROOT / "problems" / "ground_truth" / "ground_truth.json"
PUB = ROOT / "problems" / "public" / "problems.json"
OUT = ROOT / "results" / "ground_truth_check.csv"
BRUTE_LIMIT = 5_000_000
PUBLIC_KEYS = {"id", "title", "area", "difficulty", "statement", "answer_format"}


def brute_force(spec):
    variables, domains, cons = load_spec(spec)
    found = []
    for values in itertools.product(*(domains[v] for v in variables)):
        env = dict(FUNCS)
        env.update(zip(variables, values))
        if all(_holds(code, env) for _, _, code, _ in cons):
            found.append(dict(zip(variables, values)))
            if len(found) > 1:
                break
    return found


def main(selected):
    gt = json.loads(GT.read_text(encoding="utf-8"))["problems"]
    pub = json.loads(PUB.read_text(encoding="utf-8"))["problems"] if PUB.exists() else []
    pub_by_id = {p["id"]: p for p in pub}
    rows, failures = [], 0
    for p in gt:
        if selected and p["id"] not in selected:
            continue
        spec, sol = p["model"], p["solution"]
        notes = []
        valid = all(ok for *_, ok in check_assignment(spec, sol))
        if not valid:
            notes.append("solucion guardada viola restricciones")
        t0 = time.perf_counter()
        r = solve(spec, max_solutions=None)
        t_bt = time.perf_counter() - t0
        bt_ok = r["status"] == "unique" and r["solutions"][0] == sol
        if not bt_ok:
            notes.append(f"backtracking: {r['status']} ({len(r['solutions'])} sol)")
        variables, domains, _ = load_spec(spec)
        space = 1
        for d in domains.values():
            space *= len(d)
        if space <= BRUTE_LIMIT:
            t0 = time.perf_counter()
            bf = brute_force(spec)
            t_bf = time.perf_counter() - t0
            bf_ok = len(bf) == 1 and bf[0] == sol
            bf_status = "unique" if len(bf) == 1 else ("unsat" if not bf else "multiple")
            if not bf_ok:
                notes.append(f"fuerza bruta: {bf_status}")
        else:
            bf_ok, bf_status, t_bf = None, "omitido (espacio grande)", 0.0
        covered = {c["rule"] for c in spec["constraints"]}
        rules_ok = covered == set(range(1, len(p["rules_nl"]) + 1))
        if not rules_ok:
            notes.append("hay reglas sin restricción o restricciones sin regla")
        pp = pub_by_id.get(p["id"])
        leak_ok = pp is not None and set(pp) <= PUBLIC_KEYS
        if not leak_ok:
            notes.append("falta en public/ o tiene campos privados")
        ok = valid and bt_ok and bf_ok is not False and rules_ok and leak_ok
        failures += not ok
        rows.append({"id": p["id"], "difficulty": p["difficulty"], "ok": ok,
                     "solution_valid": valid, "backtracking": r["status"], "backtracking_nodes": r["nodes"],
                     "backtracking_s": f"{t_bt:.4f}", "bruteforce": bf_status, "bruteforce_s": f"{t_bf:.3f}",
                     "search_space": space, "all_rules_encoded": rules_ok, "public_ok": leak_ok,
                     "manual_review": p["review"]["manual_review"],
                     "reviewed_by": p["review"].get("reviewed_by") or "", "notes": "; ".join(notes)})
        print(f"{p['id']}: {'OK ' if ok else 'FAIL'}  bt={r['status']:<8} bf={bf_status:<8} "
              f"space={space:>9,}  {'; '.join(notes)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{len(rows) - failures}/{len(rows)} problemas verificados -> {OUT.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(set(sys.argv[1:])))
