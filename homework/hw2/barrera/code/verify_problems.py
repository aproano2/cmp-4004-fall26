"""Verificación independiente de la verdad (ground truth) del banco.

No usa el solver CSP, ni spec.py, ni el modelo JSON del brazo A: enumera TODAS
las asignaciones posibles (una permutación de casas por grupo) y evalúa cada
pista con su propio significado, escrito aquí de nuevo. Un problema es válido
si exactamente una asignación cumple todas las pistas y es la respuesta guardada.

También comprueba que el modelo a mano (campo "spec", brazo A) tenga la misma
única solución, para que el brazo A sea un techo legítimo.
"""
import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def clue_ok(c, pos):
    k, x, y = c["kind"], c["x"], c.get("y")
    if k == "at":
        return pos[x] == y
    if k == "not_at":
        return pos[x] != y
    if k == "same":
        return pos[x] == pos[y]
    if k == "differ":
        return pos[x] != pos[y]
    if k == "left_of":
        return pos[x] < pos[y]
    if k == "right_next":
        return pos[y] == pos[x] + 1
    if k == "next_to":
        return abs(pos[x] - pos[y]) == 1
    raise ValueError(k)


def brute_force(problem):
    n = problem["n_houses"]
    groups = list(problem["groups"].values())
    found = []
    for perms in itertools.product(itertools.permutations(range(1, n + 1)),
                                   repeat=len(groups)):
        pos = {}
        for items, perm in zip(groups, perms):
            pos.update(zip(items, perm))
        if all(clue_ok(c, pos) for c in problem["clues"]):
            found.append(pos)
    return found


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from csp_solver import solve
    from spec import build_csp
    problems = json.loads((ROOT / "problems" / "problems.json").read_text())["problems"]
    bad = 0
    for p in problems:
        sols = brute_force(p)
        unique = len(sols) == 1 and sols[0] == p["gold"]
        arm_a = solve(build_csp(p["spec"]), max_solutions=2)["solutions"]
        a_ok = len(arm_a) == 1 and arm_a[0] == p["gold"]
        bad += not (unique and a_ok)
        print(f"{p['id']}: {len(sols)} solución(es) por fuerza bruta, "
              f"{'coincide' if unique else 'NO coincide'} con la respuesta guardada; "
              f"modelo a mano {'OK' if a_ok else 'FALLA'}")
    print("TODOS LOS PROBLEMAS SON VÁLIDOS" if not bad else f"{bad} PROBLEMAS CON ERRORES")
    return bad


if __name__ == "__main__":
    sys.exit(main())
