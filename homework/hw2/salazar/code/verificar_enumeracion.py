"""Comprobación independiente del solver para los problemas de problems/VERIFICACION_MANUAL.md.

Enumera TODAS las asignaciones posibles (sin backtracking ni propagación), se queda con
las que cumplen las restricciones del modelo a mano y solo al final las compara con el gold.

  facil-01: producto de 3 posiciones para 6 variables  -> 3^6 = 729 asignaciones
  facil-02: permutaciones de 6 franjas                  -> 6!  = 720
  facil-05: permutaciones de 8 franjas                  -> 8!  = 40 320

    python code/verificar_enumeracion.py
"""
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csp_motor import ModeloCSP  # noqa: E402
from problemas import CARPETA_PROBLEMAS  # noqa: E402


def enumerar(pid, modo):
    p = json.loads((CARPETA_PROBLEMAS / f"{pid}.json").read_text(encoding="utf-8"))
    csp = ModeloCSP(p["modelo_mano"])
    variables = list(p["modelo_mano"]["variables"])
    dominio = p["modelo_mano"]["variables"][variables[0]]
    if modo == "producto":
        candidatos = itertools.product(dominio, repeat=len(variables))
    else:
        candidatos = itertools.permutations(dominio, len(variables))
    evaluadas, soluciones = 0, []
    for valores in candidatos:
        evaluadas += 1
        asignacion = dict(zip(variables, valores))
        if not csp.violaciones(asignacion):
            soluciones.append(asignacion)
    igual = len(soluciones) == 1 and all(soluciones[0][k] == v for k, v in p["gold"].items())
    return evaluadas, len(soluciones), igual


if __name__ == "__main__":
    total = 0
    print(f"{'problema':<10}{'evaluadas':>12}{'soluciones':>12}  igual al gold")
    for pid, modo in (("facil-01", "producto"), ("facil-02", "permutaciones"), ("facil-05", "permutaciones")):
        n, s, ok = enumerar(pid, modo)
        total += n
        print(f"{pid:<10}{n:>12}{s:>12}  {'sí' if ok else 'NO'}")
    print(f"{'total':<10}{total:>12}")
