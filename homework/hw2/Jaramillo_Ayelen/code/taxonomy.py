"""Clasificación de cada falla del brazo B (y B′) en la taxonomía del deber.

La categoría principal se asigna en este orden (la primera que aplica):

  malformed_syntax   el JSON no carga o no tiene la forma de un CSP
  timeout            el solver agotó su límite de llamadas
  scope_arity        una restricción cubre las variables equivocadas o tiene la
                     aridad equivocada: apunta a una variable no declarada, mezcla
                     un valor con una variable, o un alldiff abarca grupos distintos
                     (dueño con color) o deja fuera a un miembro de su grupo
  over_constrained   el modelo es válido pero el solver prueba que no hay solución
  under_constrained  el modelo admite más de una solución y el sistema devolvió una
                     equivocada
  wrong_problem      el modelo tiene una única solución pero es la de otro problema
                     (premisas inventadas, perdidas o invertidas), o le faltan
                     elementos del enunciado

Aparte de la categoría se registran las CAUSAS que se ven al comparar con el
modelo a mano (esto sí usa la verdad, es solo para el análisis):
  hallucinated  restricciones del LLM que la respuesta correcta viola
  dropped       pistas del modelo a mano que alguna solución del LLM viola
  reversed      restricciones del LLM que fallan pero su versión invertida se cumple
"""
from csp_solver import solve
from spec import _num, build_csp, holds, match_names, normalize_spec

CATEGORIES = ["malformed_syntax", "scope_arity", "over_constrained",
              "under_constrained", "wrong_problem", "timeout"]

# Detectable sin la verdad, según la tabla del enunciado (se llena con los datos)
NOMINAL = {"malformed_syntax": "Sí", "over_constrained": "Sí", "under_constrained": "A veces",
           "wrong_problem": "No", "scope_arity": "A veces", "timeout": "Sí"}


def _ctext(c):
    t = c.get("type")
    if t == "alldiff":
        return f"alldiff({', '.join(map(str, c.get('vars', [])))})"
    k = f", k={c.get('k')}" if t == "offset" else ""
    return f"{t}({c.get('a')}, {c.get('b')}{k})"


def _reverse(c):
    t = c["type"]
    if t == "lt":
        return {**c, "type": "gt"}
    if t == "gt":
        return {**c, "type": "lt"}
    if t == "offset":
        return {**c, "k": -_num(c["k"])} if isinstance(_num(c["k"]), int) else None
    return None


def analyze(spec, problem, stage):
    """Compara el modelo del LLM con el modelo a mano. Devuelve un dict con
    causas y la categoría principal."""
    info = {"category": None, "missing": [], "extra": [], "alldiff_issues": [],
            "hallucinated": [], "reversed": [], "dropped": []}
    if stage in ("parse", "schema") or spec is None:
        info["category"] = "malformed_syntax"
        return info
    if stage in ("llm_timeout", "llm_error"):
        info["category"] = "malformed_syntax"
        return info
    if stage == "timeout":
        info["category"] = "timeout"
    try:
        variables, domains, cons = normalize_spec(spec)
    except Exception:
        info["category"] = "malformed_syntax"
        return info

    gold = problem["gold"]
    groups = problem["groups"]
    m = match_names(list(gold), variables)
    info["missing"] = [g for g, v in m.items() if v is None]
    inv = {v: g for g, v in m.items() if v is not None}
    info["extra"] = [v for v in variables if v not in inv]
    group_of = {x: grp for grp, items in groups.items() for x in items}

    # alcance de los alldiff
    covered = {grp: False for grp in groups}
    touched = {grp: False for grp in groups}
    for c in cons:
        if str(c.get("type")).lower() != "alldiff" or not isinstance(c.get("vars"), list):
            continue
        gs = {group_of.get(inv.get(v)) for v in c["vars"]} - {None}
        if len(gs) > 1:
            # un alldiff entre grupos es un error de alcance SOLO si la verdad lo
            # viola; alldiff(red, rabbit) para "el conejo no vive en la casa roja"
            # es una forma rara pero correcta de escribir un neq
            vals = [gold.get(inv.get(v)) for v in c["vars"]]
            if None in vals or len(set(vals)) != len(vals):
                info["alldiff_issues"].append(f"alldiff mezcla grupos {sorted(gs)}: {_ctext(c)}")
        for grp, items in groups.items():
            names = {m[x] for x in items if m[x] is not None}
            if names & set(c["vars"]):
                touched[grp] = True
            if names and names <= set(c["vars"]):
                covered[grp] = True
    for grp in groups:
        if touched[grp] and not covered[grp]:
            info["alldiff_issues"].append(f"un alldiff deja fuera a miembros del grupo '{grp}'")
        elif not touched[grp]:
            info["dropped"].append(f"alldiff del grupo '{grp}' (premisa 'cada casa es distinta')")

    # restricciones que la verdad viola (inventadas / invertidas)
    gold_in_model = {v: gold[g] for v, g in inv.items()}
    for c in cons:
        if str(c.get("type")).lower() == "alldiff":
            continue
        try:
            names = [c["a"]] + ([c["b"]] if isinstance(c["b"], str) and c["b"] in domains else [])
            if not all(n in gold_in_model for n in names):
                continue
            if not holds(c, gold_in_model):
                rev = _reverse(c)
                if rev is not None and holds(rev, gold_in_model):
                    info["reversed"].append(_ctext(c))
                else:
                    info["hallucinated"].append(_ctext(c))
        except Exception:
            continue

    # pistas del modelo a mano que se pierden: alguna solución del LLM las viola
    if stage == "solved":
        try:
            sols = solve(build_csp(spec), max_solutions=50)["solutions"]
        except Exception:
            sols = []
        for c, clue in zip(problem["spec"]["constraints"][len(groups):], problem["clues"]):
            for s in sols:
                as_gold = {g: s[v] for g, v in m.items() if v is not None}
                needed = [c["a"]] + ([c["b"]] if isinstance(c["b"], str) else [])
                if all(n in as_gold for n in needed) and not holds(c, as_gold):
                    info["dropped"].append(_ctext(c))
                    break

    if info["category"]:
        return info
    if stage == "scope" or info["alldiff_issues"] and stage in ("unsat", "solved"):
        info["category"] = "scope_arity"
    elif stage == "unsat":
        info["category"] = "over_constrained"
    elif info["missing"]:
        info["category"] = "wrong_problem"
    else:
        info["category"] = None          # se decide con el número de soluciones
    return info


def classify(attempt, problem):
    """attempt: salida de arms.evaluate_spec_reply (+ 'text'). Devuelve
    (categoría, info) para una falla; categoría None si el intento es correcto."""
    if attempt["stage"] == "solved" and attempt["correct"]:
        return None, None
    info = analyze(attempt.get("spec"), problem, attempt["stage"])
    cat = info["category"]
    if cat is None:
        cat = "under_constrained" if attempt["n_solutions"] > 1 else "wrong_problem"
    info["category"] = cat
    return cat, info
