"""Classify arm-B failures. Two layers:
1. *Announced* categories come straight from what the pipeline observed (parse / schema / UNSAT / timeout / decode).
2. *Silent* categories need the reference CNF (analysis-time only; never shown to the model): semantic comparison
   plus a clause-level diff that says WHICH premise was dropped or hallucinated.
"""
from encoding import encode_graph
from prompts import extract_json
from sat_solver import solve


def has_counterexample(num_vars, left, right):
    """True if some model of `left` falsifies at least one clause of `right` (left is weaker than right)."""
    for clause in right:
        if solve(num_vars, left + [[-lit] for lit in clause], timeout_s=2.0)["status"] == "SAT":
            return True
    return False


def semantic_class(problem, clauses):
    nv, ref = encode_graph(problem)
    under = has_counterexample(nv, clauses, ref)      # model admits something the reference forbids
    over = has_counterexample(nv, ref, clauses)       # model forbids something the reference allows
    return {(False, False): "equivalent", (True, False): "under-constrained",
            (False, True): "over-constrained", (True, True): "different-problem"}[(under, over)]


def clause_diff(problem, clauses):
    """Human-readable list of dropped / hallucinated premises (syntactic, set-of-literals comparison)."""
    k, vertices = len(problem["colors"]), problem["vertices"]
    nv, ref = encode_graph(problem)
    labels, n = {}, len(vertices)
    for vi in range(n):
        labels[frozenset(ref[vi])] = ("ALO", vertices[vi])
    amo_start = n
    per = k * (k - 1) // 2
    for vi in range(n):
        for j in range(per):
            labels[frozenset(ref[amo_start + vi * per + j])] = ("AMO", vertices[vi])
    e_start = n + n * per
    for ei, (a, b) in enumerate(problem["edges"]):
        for ci in range(k):
            labels[frozenset(ref[e_start + ei * k + ci])] = ("EDGE", f"{a}-{b}")
    model_set = {frozenset(c) for c in clauses}
    missing = [labels[c] for c in labels if c not in model_set]
    notes = []
    alo = sorted({v for t, v in missing if t == "ALO"})
    amo = sorted({v for t, v in missing if t == "AMO"})
    edge_missing = {}
    for t, e in missing:
        if t == "EDGE":
            edge_missing[e] = edge_missing.get(e, 0) + 1
    if alo: notes.append(f"falta 'al menos un color' en {alo}")
    if amo: notes.append(f"falta 'a lo sumo un color' (parcial o total) en {amo}")
    if edge_missing:
        full = sorted(e for e, c in edge_missing.items() if c == k)
        part = sorted(e for e, c in edge_missing.items() if c < k)
        if full: notes.append(f"restricción de arista omitida por completo: {full}")
        if part: notes.append(f"restricción de arista incompleta (faltan algunos colores): {part}")
    # extra clauses
    index = {v: i for i, v in enumerate(vertices)}
    edge_set = {frozenset(e) for e in problem["edges"]}
    halluc, other = set(), 0
    for c in model_set - set(labels):
        if len(c) == 2 and all(l < 0 for l in c):
            (v1, c1), (v2, c2) = [divmod(abs(l) - 1, k) for l in c]
            if c1 == c2 and v1 != v2 and 0 <= v1 < n and 0 <= v2 < n:
                pair = frozenset((vertices[v1], vertices[v2]))
                if pair not in edge_set:
                    halluc.add("-".join(sorted(pair)))
                    continue
        other += 1
    if halluc: notes.append(f"aristas alucinadas (no están en el problema): {sorted(halluc)}")
    if other: notes.append(f"{other} cláusulas extra de otro tipo (variables/índices incorrectos u otras)")
    return "; ".join(notes) if notes else "sin diferencias sintácticas con el modelo de referencia"


def classify_attempt(problem, trace_rec):
    """-> {category, detectable_without_ground_truth, semantic_class, subcause}. Works on one trace record."""
    st = trace_rec.get("status")
    base = {"semantic_class": "", "subcause": trace_rec.get("detail", "")}
    if st == "LLM_ERROR":
        return {**base, "category": "Infrastructure error (excluded from analysis)", "detectable_without_ground_truth": "n/a"}
    if st == "PARSE_ERROR":
        trunc = " [salida truncada por num_predict]" if trace_rec.get("done_reason") == "length" else ""
        return {**base, "category": "Malformed syntax (won't parse)", "detectable_without_ground_truth": "Yes",
                "subcause": base["subcause"] + trunc}
    if st == "SCHEMA_ERROR":
        return {**base, "category": "Arity / index error (invalid literal, var count or schema)",
                "detectable_without_ground_truth": "Yes"}
    if st == "TIMEOUT":
        return {**base, "category": "Solver timeout", "detectable_without_ground_truth": "Yes"}
    # From here on the CNF parsed and passed validation: we can compare it with the reference.
    try:
        obj = extract_json(trace_rec["raw_output"])
        clauses = obj["clauses"]
        sem = semantic_class(problem, clauses)
        diff = clause_diff(problem, clauses)
    except Exception as exc:       # should not happen; make it visible rather than hide it
        return {**base, "category": f"Classifier error: {exc}", "detectable_without_ground_truth": "?"}
    if st == "SAT" and trace_rec.get("answer_valid"):
        tag = "equivalent to reference" if sem == "equivalent" else f"RIGHT FOR THE WRONG REASONS ({sem})"
        return {"category": "Correct", "detectable_without_ground_truth": "n/a", "semantic_class": sem,
                "subcause": f"{tag} | {diff}"}
    if st == "UNSAT":
        return {"category": "Valid syntax, over-constrained (UNSAT)", "detectable_without_ground_truth": "Yes",
                "semantic_class": sem, "subcause": diff}
    if st == "DECODE_ERROR":
        return {"category": "Valid syntax, under-constrained — caught by decoder (vertex without exactly one colour)",
                "detectable_without_ground_truth": "Yes (decoder)", "semantic_class": sem,
                "subcause": f"{trace_rec.get('detail','')} | {diff}"}
    # st == "SAT" and the decoded answer was invalid (otherwise it would not be a failure)
    if sem == "different-problem":
        cat = "Valid model of the wrong problem (dropped AND hallucinated premises) — silent"
    elif sem == "under-constrained":
        cat = "Valid syntax, under-constrained (wrong solution returned) — silent"
    elif sem == "over-constrained":
        cat = "Valid syntax, over-constrained but satisfiable (wrong solution returned) — silent"
    else:
        cat = "HARNESS BUG: model equivalent to reference but answer invalid"
    return {"category": cat, "detectable_without_ground_truth": "No (needs a verifier / reference)",
            "semantic_class": sem, "subcause": diff}
