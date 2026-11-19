"""Checks on the dataset + reference arm. Independent of the DPLL solver and of encode_graph where possible."""
import json, re, itertools
from pathlib import Path
from encoding import (encode_graph, decode_model, assignment_is_valid, reference_clause_count, difficulty_from_clauses)
from sat_solver import solve, validate_cnf

ROOT = Path(__file__).resolve().parents[1]
problems = json.loads((ROOT / "problems" / "dataset.json").read_text(encoding="utf-8"))


def backtrack_colourable(p):
    """Independent oracle: plain backtracking, no SAT, no encoding."""
    adj = {v: set() for v in p["vertices"]}
    for a, b in p["edges"]: adj[a].add(b); adj[b].add(a)
    order, col = p["vertices"], {}
    def go(i):
        if i == len(order): return True
        for c in p["colors"]:
            if all(col.get(u) != c for u in adj[order[i]]):
                col[order[i]] = c
                if go(i + 1): return True
                del col[order[i]]
        return False
    return go(0)


assert len(problems) >= 20
assert len({p["id"] for p in problems}) == len(problems)
assert len({frozenset(map(frozenset, p["edges"])) for p in problems}) == len(problems), "duplicate graph"
assert {p["difficulty"] for p in problems} == {"easy", "medium", "hard"}
for p in problems:
    n, m = len(p["vertices"]), len(p["edges"])
    # --- NL prompt <-> structured data must agree (the ground truth is derived from the data, the model reads the prompt)
    txt = p["prompt_es"]
    edges_txt = [tuple(x.split("-")) for x in re.search(r"Aristas: (.*?)\.", txt).group(1).split(", ")]
    assert edges_txt == [tuple(e) for e in p["edges"]], (p["id"], "prompt edges != data edges")
    assert int(re.search(r"con (\d+) v", txt).group(1)) == n, p["id"]
    assert all(v in txt for v in p["vertices"])
    # --- structural sanity
    assert all(a != b and a in p["vertices"] and b in p["vertices"] for a, b in p["edges"]), p["id"]
    assert len({frozenset(e) for e in p["edges"]}) == m, (p["id"], "repeated edge")
    # --- difficulty metric and bands
    c = reference_clause_count(p)
    assert p["difficulty_metric"] == {"vertices": n, "boolean_variables": 3 * n, "edges": m, "reference_clauses": c}, p["id"]
    assert difficulty_from_clauses(c) == p["difficulty"], (p["id"], c, p["difficulty"])
    # --- ground truth, independent oracle, reference arm
    assert assignment_is_valid(p, p["ground_truth"]), p["id"]
    assert backtrack_colourable(p), p["id"]
    nv, cnf = encode_graph(p)
    assert len(cnf) == c
    validate_cnf(nv, cnf)
    r = solve(nv, cnf)
    assert r["status"] == "SAT", (p["id"], r["status"])
    assert assignment_is_valid(p, decode_model(p, r["model"])), p["id"]
    # --- the checker must reject a corrupted ground truth (guards against a vacuous validator)
    bad = dict(p["ground_truth"]); a, b = p["edges"][0]; bad[a] = bad[b]
    assert not assignment_is_valid(p, bad), p["id"]
# a K4 cannot be 3-coloured: reference arm must say UNSAT
k4 = {"vertices": list("ABCD"), "colors": ["rojo", "azul", "verde"], "edges": list(itertools.combinations("ABCD", 2))}
assert solve(*encode_graph(k4))["status"] == "UNSAT" and not backtrack_colourable(k4)
print(f"OK: {len(problems)} problems — prompts match data, labels match metric, GT valid, oracle agrees, K4 UNSAT.")
