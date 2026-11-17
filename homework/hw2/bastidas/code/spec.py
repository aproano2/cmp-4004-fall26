"""El formato JSON del modelo CSP, su parser y su validador.

El mismo formato lo usan los tres brazos que pasan por el solver:
  * brazo A: el modelo escrito a mano (problems/problems.json, campo "spec");
  * brazos B y B′: el modelo que escribe el LLM.

    {"variables": {"Ana": [1, 2, 3, 4], "red": [1, 2, 3, 4], ...},
     "constraints": [
        {"type": "alldiff", "vars": ["Ana", "Ben", ...]},
        {"type": "eq",  "a": "Ana", "b": "red"}     # Ana == red   (variable)
        {"type": "eq",  "a": "Ana", "b": 2}         # Ana == 2     (número)
        {"type": "neq", "a": "Ana", "b": "cat"}     # Ana != cat   / Ana != 3
        {"type": "lt",  "a": "Ana", "b": "red"}     # Ana < red    (a la izquierda)
        {"type": "next_to", "a": "Ana", "b": "cat"} # |Ana - cat| == 1
        {"type": "offset",  "a": "Ana", "b": "cat", "k": 1}   # Ana == cat + k
     ]}

Errores que distingue `build_csp` (son la base de la taxonomía):
  ParseError   la respuesta no contiene JSON válido            -> sintaxis mala
  SchemaError  JSON válido pero no es un CSP en este formato    -> sintaxis mala
  ScopeError   un CSP bien formado cuyas restricciones apuntan a
               variables no declaradas, valores fuera del dominio
               o tienen la aridad equivocada                    -> alcance/aridad
Los tres se detectan SIN la respuesta correcta y sus mensajes son lo único que
el bucle de refinamiento (brazo B′) le devuelve al modelo.
"""
import json
import re

from csp_solver import CSP

TYPES = {"alldiff", "eq", "neq", "lt", "gt", "next_to", "offset"}


class ParseError(Exception):
    pass


class SchemaError(Exception):
    pass


class ScopeError(Exception):
    pass


# ---------------------------------------------------------------- extracción --
def json_objects(text):
    """Todos los objetos {...} balanceados de primer nivel que cargan como JSON,
    en orden de aparición. Tolera prosa y bloques ```json alrededor."""
    out, i = [], 0
    errors = []
    while text and i < len(text):
        start = text.find("{", i)
        if start == -1:
            break
        depth, in_str, esc, end = 0, False, False, None
        for j in range(start, len(text)):
            ch = text[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = j
                    break
        if end is None:
            errors.append("unbalanced braces: the JSON object is never closed")
            break
        chunk = text[start:end + 1]
        try:
            out.append(json.loads(chunk))
        except json.JSONDecodeError as e:
            errors.append(f"invalid JSON: {e}")
        i = end + 1
    return out, errors


def parse_spec_json(text):
    """El objeto JSON con la especificación (el primero que tenga 'variables';
    si ninguno lo tiene, el primero que cargue)."""
    if not text or not text.strip():
        raise ParseError("empty reply")
    objs, errors = json_objects(text)
    for o in objs:
        if isinstance(o, dict) and "variables" in o:
            return o
    if objs:
        return objs[0]
    if errors:
        raise ParseError(errors[0])
    raise ParseError("no JSON object found in the reply")


def parse_answer_json(text):
    """Brazo C: el ÚLTIMO objeto JSON de la respuesta (el modelo puede razonar antes)."""
    if not text or not text.strip():
        raise ParseError("empty reply")
    objs, errors = json_objects(text)
    dicts = [o for o in objs if isinstance(o, dict) and o]
    if dicts:
        return dicts[-1]
    raise ParseError(errors[0] if errors else "no JSON object found in the reply")


# ---------------------------------------------------------------- validación --
def _num(x):
    """'3' -> 3; 3.0 -> 3; deja lo demás igual."""
    if isinstance(x, bool):
        return x
    if isinstance(x, float) and x.is_integer():
        return int(x)
    if isinstance(x, str) and re.fullmatch(r"\s*-?\d+\s*", x):
        return int(x)
    return x


def normalize_spec(spec):
    """Comprueba la FORMA del JSON y devuelve (variables, domains, constraints).
    Lanza SchemaError si no es un CSP en este formato."""
    if not isinstance(spec, dict):
        raise SchemaError("the top-level JSON value must be an object")
    if "variables" not in spec:
        raise SchemaError("missing key 'variables'")
    raw = spec["variables"]
    if isinstance(raw, list):              # [{"name": .., "domain": ..}] -> dict
        try:
            raw = {d["name"]: d["domain"] for d in raw}
        except (TypeError, KeyError):
            raise SchemaError("'variables' must map each name to its domain list")
    if not isinstance(raw, dict) or not raw:
        raise SchemaError("'variables' must be a non-empty object {name: [values]}")
    domains = {}
    for name, dom in raw.items():
        if not isinstance(dom, list) or not dom:
            raise SchemaError(f"variable {name!r}: the domain must be a non-empty list")
        domains[str(name)] = [_num(x) for x in dom]
    cons = spec.get("constraints", [])
    if not isinstance(cons, list):
        raise SchemaError("'constraints' must be a list")
    for i, c in enumerate(cons):
        if not isinstance(c, dict) or "type" not in c:
            raise SchemaError(f"constraint #{i + 1} must be an object with a 'type'")
        t = str(c["type"]).lower()
        if t not in TYPES:
            raise SchemaError(f"constraint #{i + 1}: unknown type {c['type']!r} "
                              f"(allowed: {', '.join(sorted(TYPES))})")
        need = ["vars"] if t == "alldiff" else ["a", "b"] + (["k"] if t == "offset" else [])
        for key in need:
            if key not in c:
                raise SchemaError(f"constraint #{i + 1} ({t}) is missing field {key!r}")
    return list(domains), domains, cons


def build_csp(spec):
    """JSON -> CSP resoluble. Lanza SchemaError o ScopeError (ver arriba)."""
    variables, domains, cons = normalize_spec(spec)
    csp = CSP(variables, domains)
    varset = set(variables)

    def is_var(x):
        return isinstance(x, str) and x in varset

    def need_var(x, i, t, field):
        if not is_var(x):
            raise ScopeError(f"constraint #{i} ({t}): {field}={x!r} is not a declared variable")
        return x

    def need_numeric(v, i, t):
        if not all(isinstance(x, int) for x in domains[v]):
            raise ScopeError(f"constraint #{i} ({t}): variable {v!r} has a non-numeric "
                             f"domain, so {t} cannot compare it")

    for i, c in enumerate(cons, start=1):
        t = str(c["type"]).lower()
        if t == "alldiff":
            vs = c["vars"]
            if not isinstance(vs, list) or len(vs) < 2:
                raise ScopeError(f"constraint #{i} (alldiff) needs a list of at least 2 variables")
            for v in vs:
                need_var(v, i, t, "vars")
            if len(set(vs)) != len(vs):
                raise ScopeError(f"constraint #{i} (alldiff) lists the same variable twice")
            csp.add_alldiff(list(vs))
            continue

        a = need_var(c["a"], i, t, "a")
        b = c["b"] if is_var(c["b"]) else _num(c["b"])
        if t in ("eq", "neq"):
            if is_var(b):
                pred = (lambda x, y: x == y) if t == "eq" else (lambda x, y: x != y)
                csp.add_binary(a, b, pred)
            else:
                if b not in domains[a]:
                    raise ScopeError(f"constraint #{i} ({t}): b={c['b']!r} is neither a "
                                     f"declared variable nor a value in the domain of {a!r}")
                if t == "eq":
                    csp.add_unary(a, lambda x, v=b: x == v)
                else:
                    csp.add_unary(a, lambda x, v=b: x != v)
            continue

        need_numeric(a, i, t)
        if is_var(b):
            need_numeric(b, i, t)
        elif not isinstance(b, int):
            raise ScopeError(f"constraint #{i} ({t}): b={c['b']!r} is neither a declared "
                             f"variable nor a number")
        if t in ("lt", "gt"):
            op = (lambda x, y: x < y) if t == "lt" else (lambda x, y: x > y)
        elif t == "next_to":
            op = lambda x, y: abs(x - y) == 1
        else:  # offset: a == b + k
            k = _num(c["k"])
            if not isinstance(k, int):
                raise ScopeError(f"constraint #{i} (offset): k={c['k']!r} must be an integer")
            op = lambda x, y, k=k: x == y + k
        if is_var(b):
            csp.add_binary(a, b, op)
        else:
            csp.add_unary(a, lambda x, v=b, op=op: op(x, v))
    return csp


def holds(c, sol):
    """¿La restricción c (formato JSON) se cumple en la asignación sol?
    Se usa para comparar el modelo del LLM con el modelo a mano."""
    t = str(c["type"]).lower()
    if t == "alldiff":
        vals = [sol[v] for v in c["vars"]]
        return len(set(vals)) == len(vals)
    x = sol[c["a"]]
    y = sol[c["b"]] if isinstance(c["b"], str) and c["b"] in sol else _num(c["b"])
    return {"eq": lambda: x == y, "neq": lambda: x != y, "lt": lambda: x < y,
            "gt": lambda: x > y, "next_to": lambda: abs(x - y) == 1,
            "offset": lambda: x == y + _num(c["k"])}[t]()


# ------------------------------------------------- nombres modelo <-> verdad --
def _tokens(name):
    s = re.sub(r"([a-z])([A-Z])", r"\1_\2", str(name))
    return [t for t in re.split(r"[^a-z0-9]+", s.lower()) if t]


def match_names(gold_keys, model_keys):
    """Empareja cada nombre de la respuesta correcta ('ana', 'red', 'cat') con
    una variable del modelo ('Ana', 'red_house', 'color_red'...). Primero por
    igualdad exacta (sin mayúsculas ni signos), luego por token; si hay más de
    un candidato el nombre queda sin emparejar. Es tolerante a favor del modelo."""
    norm = {k: "".join(_tokens(k)) for k in model_keys}
    toks = {k: set(_tokens(k)) for k in model_keys}
    mapping = {}
    for g in gold_keys:
        gn = "".join(_tokens(g))
        exact = [k for k in model_keys if norm[k] == gn]
        if len(exact) == 1:
            mapping[g] = exact[0]
            continue
        cand = [k for k in model_keys if gn in toks[k]]
        mapping[g] = cand[0] if len(cand) == 1 else None
    return mapping


def grade_assignment(assign, gold):
    """Compara una asignación del modelo (nombres del modelo) con la verdad.
    Devuelve (correcto, mapeada, faltantes)."""
    mapping = match_names(list(gold), list(assign))
    mapped = {g: (_num(assign[m]) if m is not None else None) for g, m in mapping.items()}
    missing = [g for g, m in mapping.items() if m is None]
    ok = not missing and all(mapped[g] == gold[g] for g in gold)
    return ok, mapped, missing
