"""Solver CSP del duelo 2.

Es el `backtrack_search` de la semana 6 (studios/week-06/csp.py) generalizado:
el original solo sabe all-different (su `forward_check` borra el mismo valor del
vecino), y aquí necesitamos restricciones binarias arbitrarias (<, vecino de,
desplazamiento). La estructura es la misma: MRV + grado para elegir variable,
forward checking para podar, y un límite de llamadas que produce TIMEOUT.

Diferencias con la semana 6:
  * cada restricción binaria es un predicado p(x, y) sobre (var_a, var_b);
  * forward checking filtra el dominio del vecino con ese predicado;
  * `solve(..., max_solutions=2)` sigue buscando después de la primera solución.
    Eso permite comprobar UNICIDAD sin conocer la respuesta correcta: si el
    modelo del LLM admite dos soluciones, está sub-restringido.
"""
import time

DEFAULT_LIMIT = 200_000      # llamadas a recurse() antes de declarar TIMEOUT


class CSP:
    """CSP binario. `binary[v]` = lista de (vecino, pred) con pred(val_v, val_vecino)."""

    def __init__(self, variables, domains):
        self.variables = list(variables)
        self.domains = {v: list(domains[v]) for v in self.variables}
        self.binary = {v: [] for v in self.variables}

    def add_unary(self, var, pred):
        self.domains[var] = [x for x in self.domains[var] if pred(x)]

    def add_binary(self, a, b, pred):
        """Restricción pred(valor_a, valor_b). Se guarda en ambos sentidos."""
        if a == b:                       # X op X: se evalúa como unaria
            self.add_unary(a, lambda x, p=pred: p(x, x))
            return
        self.binary[a].append((b, pred))
        self.binary[b].append((a, lambda y, x, p=pred: p(x, y)))

    def add_alldiff(self, vs):
        for i, a in enumerate(vs):
            for b in vs[i + 1:]:
                self.add_binary(a, b, lambda x, y: x != y)

    def degree(self, var):
        return len({n for n, _ in self.binary[var]})

    def consistent(self, var, value, assignment):
        return all(pred(value, assignment[n])
                   for n, pred in self.binary[var] if n in assignment)


def solve(csp, max_solutions=1, limit=DEFAULT_LIMIT, use_fc=True, use_mrv=True):
    """Backtracking con forward checking y MRV (como la semana 6).

    Devuelve un dict:
      status     'ok' (búsqueda completa) | 'timeout'
      solutions  lista con hasta `max_solutions` soluciones
      calls      llamadas a recurse()
      time_s     tiempo de CPU del solver (separado del tiempo del LLM)
    Con status 'ok', solutions == [] es una PRUEBA de que no hay solución.
    """
    t0 = time.perf_counter()
    counter = {"calls": 0}
    domains = {v: list(csp.domains[v]) for v in csp.variables}
    assignment = {}
    solutions = []

    def select_unassigned():
        unassigned = [v for v in csp.variables if v not in assignment]
        if not use_mrv:
            return unassigned[0]
        return min(unassigned, key=lambda v: (len(domains[v]), -csp.degree(v)))

    def forward_check(var, value):
        removed = []
        for n, pred in csp.binary[var]:
            if n in assignment:
                continue
            keep = [y for y in domains[n] if pred(value, y)]
            if len(keep) != len(domains[n]):
                removed.append((n, domains[n]))
                domains[n] = keep
                if not keep:
                    return removed, True
        return removed, False

    def undo(removed):
        for n, old in reversed(removed):
            domains[n] = old

    def recurse():
        counter["calls"] += 1
        if counter["calls"] > limit:
            raise TimeoutError
        if len(assignment) == len(csp.variables):
            solutions.append(dict(assignment))
            return len(solutions) >= max_solutions
        var = select_unassigned()
        for value in list(domains[var]):
            if csp.consistent(var, value, assignment):
                assignment[var] = value
                removed, wiped = forward_check(var, value) if use_fc else ([], False)
                if not wiped and recurse():
                    return True
                undo(removed)
                del assignment[var]
        return False

    status = "ok"
    if any(not d for d in domains.values()):
        pass                                  # dominio vacío: sin solución
    else:
        try:
            recurse()
        except TimeoutError:
            status = "timeout"
    return {"status": status, "solutions": solutions, "calls": counter["calls"],
            "time_s": time.perf_counter() - t0}
