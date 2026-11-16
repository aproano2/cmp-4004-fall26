"""Construye el banco de 40 problemas (problems/problems.json + PROBLEMS.md).

Cada problema es un acertijo tipo "zebra" sobre casas en fila, numeradas de
izquierda a derecha. Para cada uno:
  1. se sortea una solución oculta (semilla fija -> reproducible);
  2. se generan todas las pistas VERDADERAS para esa solución (de 7 tipos);
  3. se agregan pistas al azar hasta que el solver encuentra una única solución;
  4. se quitan las pistas redundantes (si sin ella la solución sigue siendo
     única, se elimina) -> un conjunto mínimo;
  5. se redacta el texto en lenguaje natural y el modelo CSP a mano (brazo A).

Niveles de dificultad (métrica: número de variables del CSP):
  L1  4 casas, dueños                      ->  4 variables
  L2  4 casas, dueños + colores            ->  8 variables
  L3  5 casas, dueños + colores            -> 10 variables
  L4  5 casas, dueños + colores + mascotas -> 15 variables
10 problemas por nivel = 40 (el mínimo de la scorecard del curso:
cuatro tamaños, diez instancias cada uno). La verdad se comprueba aparte, por fuerza bruta y
sin usar este código, en verify_problems.py.
"""
import json
import random
from pathlib import Path

from csp_solver import solve
from spec import build_csp

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "problems"

PEOPLE = ["Ana", "Ben", "Carla", "Dev", "Elena", "Felix", "Gina", "Hugo", "Iris",
          "Jon", "Kai", "Lucia", "Mateo", "Nora", "Omar", "Paula", "Raul", "Sara",
          "Tomas", "Vera"]
COLOURS = ["red", "blue", "green", "yellow", "white", "black", "orange", "purple"]
PETS = ["cat", "dog", "fish", "bird", "rabbit", "horse", "turtle", "hamster"]
NUM_WORD = {4: "Four", 5: "Five"}

LEVELS = {1: (4, ["person"]),
          2: (4, ["person", "colour"]),
          3: (5, ["person", "colour"]),
          4: (5, ["person", "colour", "pet"])}
PER_LEVEL = 10

# peso de cada tipo de pista al sortearlas (menos pistas "X es la casa k",
# que vuelven el acertijo trivial)
WEIGHTS = {"at": 0.4, "not_at": 0.8, "same": 2.0, "differ": 0.8, "left_of": 1.5,
           "right_next": 1.5, "next_to": 1.5}


def role_of(item, roles):
    for r, items in roles.items():
        if item in items:
            return r


def H(item, roles, cap=True):
    """Frase para 'la casa de X'."""
    r = role_of(item, roles)
    s = {"person": f"{item}'s house", "colour": f"the {item} house",
         "pet": f"the house with the {item}"}[r]
    return s[0].upper() + s[1:] if cap else s


def clue_text(c, roles):
    k, x, y = c["kind"], c["x"], c.get("y")
    if k == "at":
        return f"{H(x, roles)} is house {y}."
    if k == "not_at":
        return f"{H(x, roles)} is not house {y}."
    if k == "left_of":
        return f"{H(x, roles)} is somewhere to the left of {H(y, roles, False)}."
    if k == "right_next":       # y está inmediatamente a la derecha de x
        return f"{H(x, roles)} is immediately to the left of {H(y, roles, False)}."
    if k == "next_to":
        return f"{H(x, roles)} and {H(y, roles, False)} are next to each other."
    rx, ry = role_of(x, roles), role_of(y, roles)
    pair = {rx: x, ry: y}
    neg = k == "differ"
    if {rx, ry} == {"person", "colour"}:
        return f"{pair['person']} {'does not live' if neg else 'lives'} in the {pair['colour']} house."
    if {rx, ry} == {"person", "pet"}:
        return f"{pair['person']} {'does not own' if neg else 'owns'} the {pair['pet']}."
    return (f"The {pair['pet']} {'does not live' if neg else 'lives'} "
            f"in the {pair['colour']} house.")


def clue_constraint(c):
    k, x, y = c["kind"], c["x"], c.get("y")
    return {"at": {"type": "eq", "a": x, "b": y},
            "not_at": {"type": "neq", "a": x, "b": y},
            "same": {"type": "eq", "a": x, "b": y},
            "differ": {"type": "neq", "a": x, "b": y},
            "left_of": {"type": "lt", "a": x, "b": y},
            "right_next": {"type": "offset", "a": y, "b": x, "k": 1},
            "next_to": {"type": "next_to", "a": x, "b": y}}[k]


def make_spec(n, roles, clues):
    variables = {v: list(range(1, n + 1)) for items in roles.values() for v in items}
    cons = [{"type": "alldiff", "vars": list(items)} for items in roles.values()]
    cons += [clue_constraint(c) for c in clues]
    return {"variables": variables, "constraints": cons}


def n_solutions(n, roles, clues, cap=2):
    res = solve(build_csp(make_spec(n, roles, clues)), max_solutions=cap)
    return len(res["solutions"])


def true_clues(sol, roles):
    items = list(sol)
    n = max(sol.values())
    out = []
    for x in items:
        for k in range(1, n + 1):
            out.append({"kind": "at" if sol[x] == k else "not_at", "x": x, "y": k})
    for i, x in enumerate(items):
        for y in items:
            if x == y:
                continue
            same_role = role_of(x, roles) == role_of(y, roles)
            if not same_role and items.index(y) > i:
                out.append({"kind": "same" if sol[x] == sol[y] else "differ", "x": x, "y": y})
            if sol[x] < sol[y]:
                out.append({"kind": "left_of", "x": x, "y": y})
            if sol[y] == sol[x] + 1:
                out.append({"kind": "right_next", "x": x, "y": y})
            if abs(sol[x] - sol[y]) == 1 and items.index(y) > i:
                out.append({"kind": "next_to", "x": x, "y": y})
    return out


def make_problem(level, idx):
    n, role_names = LEVELS[level]
    rng = random.Random(1000 * level + idx)
    pools = {"person": PEOPLE, "colour": COLOURS, "pet": PETS}
    roles = {r: rng.sample(pools[r], n) for r in role_names}
    sol = {}
    for r, items in roles.items():
        pos = list(range(1, n + 1))
        rng.shuffle(pos)
        sol.update(dict(zip(items, pos)))

    pool = true_clues(sol, roles)
    # sorteo ponderado sin reemplazo (clave de Efraimidis-Spirakis)
    pool.sort(key=lambda c: -rng.random() ** (1 / WEIGHTS[c["kind"]]))
    clues = []
    for c in pool:
        clues.append(c)
        if n_solutions(n, roles, clues) == 1:
            break
    # quitar redundantes: el conjunto final es mínimo
    for c in list(clues):
        trial = [d for d in clues if d is not c]
        if n_solutions(n, roles, trial) == 1:
            clues = trial
    rng.shuffle(clues)

    spec = make_spec(n, roles, clues)
    sols = solve(build_csp(spec), max_solutions=2)["solutions"]
    assert len(sols) == 1 and sols[0] == sol, "el generador no produjo solución única"
    hard = solve(build_csp(spec), max_solutions=1, use_fc=False, use_mrv=False)

    lines = []
    if role_names == ["person"]:
        names = ", ".join(roles["person"][:-1]) + " and " + roles["person"][-1]
        lines.append(f"{NUM_WORD[n]} friends -- {names} -- live in {n} houses in a row, "
                     f"numbered 1 to {n} from left to right. Each friend lives in a "
                     f"different house.")
        ask = "Give the house number of every friend."
    else:
        attrs = {"colour": "a different colour", "pet": "a different pet"}
        parts = ["a different owner"] + [attrs[r] for r in role_names[1:]]
        extra = ", ".join(parts[:-1]) + " and " + parts[-1]
        lines.append(f"{NUM_WORD[n]} houses stand in a row, numbered 1 to {n} from left "
                     f"to right. Each house has {extra}.")
        lines.append("Owners: " + ", ".join(roles["person"]) + ".")
        lines.append("Colours: " + ", ".join(roles["colour"]) + ".")
        if "pet" in roles:
            lines.append("Pets: " + ", ".join(roles["pet"]) + ".")
        ask = ("Give the house number of every owner and every colour." if "pet" not in roles
               else "Give the house number of every owner, every colour and every pet.")
    lines.append("Clues:")
    lines += [f"{i}. {clue_text(c, roles)}" for i, c in enumerate(clues, start=1)]
    lines.append(ask)

    return {"id": f"L{level}-{idx:02d}", "level": level, "n_houses": n,
            "n_vars": sum(len(v) for v in roles.values()), "n_clues": len(clues),
            "n_constraints": len(spec["constraints"]),
            "plain_bt_calls": hard["calls"],
            "groups": roles, "text": "\n".join(lines), "clues": clues,
            "spec": spec, "gold": sol}


def write_markdown(problems):
    md = ["# Banco de problemas — Duelo 2 (CSP)", "",
          "40 acertijos de casas en fila, 10 por nivel. Generados por",
          "`code/generate_problems.py` (semillas fijas) y verificados por fuerza bruta",
          "con `code/verify_problems.py`, que no usa el solver ni el parser de los brazos.",
          "", "| Nivel | Casas | Grupos | Variables | Pistas (rango) |", "|---|---|---|---|---|"]
    for lv in sorted(LEVELS):
        ps = [p for p in problems if p["level"] == lv]
        n, roles = LEVELS[lv]
        md.append(f"| L{lv} | {n} | {', '.join(roles)} | {ps[0]['n_vars']} | "
                  f"{min(p['n_clues'] for p in ps)}–{max(p['n_clues'] for p in ps)} |")
    md.append("")
    for p in problems:
        md += [f"## {p['id']}  (nivel {p['level']}, {p['n_vars']} variables, "
               f"{p['n_clues']} pistas)", "", "```", p["text"], "```", "",
               "**Respuesta correcta (única):**", ""]
        for grp, items in p["groups"].items():
            row = ", ".join(f"{x}={p['gold'][x]}" for x in sorted(items, key=p["gold"].get))
            md.append(f"- {grp}: {row}")
        md.append("")
    (OUT / "PROBLEMS.md").write_text("\n".join(md), encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    problems = [make_problem(lv, i) for lv in sorted(LEVELS) for i in range(1, PER_LEVEL + 1)]
    (OUT / "problems.json").write_text(json.dumps({"problems": problems}, indent=1,
                                                  ensure_ascii=False), encoding="utf-8")
    write_markdown(problems)
    for p in problems:
        print(f"{p['id']}: {p['n_vars']:>2} vars, {p['n_clues']:>2} pistas, "
              f"backtracking simple {p['plain_bt_calls']:>6} llamadas")


if __name__ == "__main__":
    main()
