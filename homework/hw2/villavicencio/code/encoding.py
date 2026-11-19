"""Reference (arm A) SAT encoding for graph k-colouring + decoding/validation helpers."""

# Difficulty metric: number of clauses of the reference CNF = n (ALO) + n*C(k,2) (AMO) + m*k (edges)
# For k=3 this is 4n + 3m. Bands are fixed *before* running any model.
DIFFICULTY_BANDS = {"easy": (0, 40), "medium": (41, 70), "hard": (71, 10**9)}


def reference_clause_count(problem):
    n, k, m = len(problem["vertices"]), len(problem["colors"]), len(problem["edges"])
    return n + n * (k * (k - 1) // 2) + m * k


def difficulty_from_clauses(c):
    for name, (lo, hi) in DIFFICULTY_BANDS.items():
        if lo <= c <= hi:
            return name


def var_id(vertex_index, color_index, k=3):
    return vertex_index * k + color_index + 1


def expected_num_vars(problem):
    return len(problem["vertices"]) * len(problem["colors"])


def encode_graph(problem):
    vertices, colors = problem["vertices"], problem["colors"]
    n, k = len(vertices), len(colors)
    clauses = []
    for vi in range(n):                                   # at least one colour
        clauses.append([var_id(vi, ci, k) for ci in range(k)])
    for vi in range(n):                                   # at most one colour
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                clauses.append([-var_id(vi, c1, k), -var_id(vi, c2, k)])
    index = {v: i for i, v in enumerate(vertices)}
    for a, b in problem["edges"]:                         # adjacent vertices differ
        for ci in range(k):
            clauses.append([-var_id(index[a], ci, k), -var_id(index[b], ci, k)])
    return n * k, clauses


def decode_with_diagnosis(problem, model):
    """Return (assignment|None, issues). Uses only the solver model + variable convention (no ground truth)."""
    k = len(problem["colors"])
    result, issues = {}, []
    for vi, vertex in enumerate(problem["vertices"]):
        chosen = [ci for ci in range(k) if model.get(var_id(vi, ci, k), False)]
        if len(chosen) == 1:
            result[vertex] = problem["colors"][chosen[0]]
        else:
            issues.append(f"el vértice {vertex} tiene {len(chosen)} colores asignados en el modelo (debe tener exactamente 1)")
    return (None if issues else result), issues


def decode_model(problem, model):
    return decode_with_diagnosis(problem, model)[0]


def structural_issues(problem, assignment):
    """Schema-level checks any consumer can do without knowing the answer."""
    if not isinstance(assignment, dict):
        return ["la respuesta no es un objeto vértice->color"]
    issues = []
    missing = [v for v in problem["vertices"] if v not in assignment]
    extra = [v for v in assignment if v not in problem["vertices"]]
    bad = [v for v, c in assignment.items() if c not in problem["colors"]]
    if missing: issues.append(f"faltan vértices: {missing}")
    if extra: issues.append(f"vértices desconocidos: {extra}")
    if bad: issues.append(f"colores inválidos en: {bad}")
    return issues


def violated_edges(problem, assignment):
    return [(a, b) for a, b in problem["edges"] if assignment.get(a) == assignment.get(b)]


def assignment_is_valid(problem, assignment):
    return not structural_issues(problem, assignment) and not violated_edges(problem, assignment)
