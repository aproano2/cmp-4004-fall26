"""Motor CSP del grupo para el HW2 (The Formalizer).

Partimos del solver del studio de la semana 6 (`studios/week-06/csp.py` y
`logic_lm.py`): backtracking con forward checking y MRV. Ese solver solo entiende
`alldiff`, `eq` y `neq` contra un valor, lo que limita los problemas a
asignaciones pequeñas. Para que la dificultad suba de verdad (acertijos tipo
Einstein con "a la izquierda de", "junto a", horarios con "antes de") ampliamos
el vocabulario y escribimos el motor de nuevo con la misma idea.

Formato de un modelo (lo usan el brazo A, escrito a mano, y el brazo B, escrito
por el LLM; las claves van en inglés para seguir el formato del studio):

    {"variables": {"Ana": [1, 2, 3], "Rojo": [1, 2, 3], ...},
     "constraints": [
        {"type": "alldiff", "vars": ["Ana", "Bob", "Cara"]},
        {"type": "eq",  "a": "Ana", "b": "Rojo"},     # misma posición (b es variable)
        {"type": "eq",  "a": "Ana", "b": 1},          # Ana vale 1 (b es un valor)
        {"type": "neq", "a": "Ana", "b": "Bob"},      # distintas (variable o valor)
        {"type": "lt",  "a": "Ana", "b": "Bob"},      # Ana < Bob   (solo números)
        {"type": "gt",  "a": "Ana", "b": "Bob"},      # Ana > Bob   (solo números)
        {"type": "adj", "a": "Ana", "b": "Bob"},      # |Ana - Bob| == 1
        {"type": "offset", "a": "Ana", "b": "Bob", "k": 1}   # Ana - Bob == k
     ]}

Regla para `b`: si es un texto igual al nombre de una variable, la restricción es
binaria; en cualquier otro caso `b` es un valor y la restricción es unaria.

Qué devuelve `resolver(modelo)`: un `ResultadoSolver` con `estado` en
    "unica"        exactamente una solución (la que esperamos de un buen modelo)
    "multiple"     al menos dos soluciones -> modelo sub-restringido
    "sin_solucion" el solver probó que no hay solución -> sobre-restringido
    "timeout"      se acabó el límite de llamadas o de segundos
y los errores de construcción salen como `ErrorModelo` con `categoria` (el mensaje
va en inglés porque es lo que el brazo B' le devuelve al modelo)
    "sintaxis"        estructura rota (falta 'variables', tipo desconocido, ...)
    "aridad_alcance"  la restricción apunta a una variable que no existe, le
                      faltan argumentos o compara con < sobre valores no numéricos

Contar hasta 2 soluciones es lo que vuelve medible la fila "sub-restringido" de la
taxonomía de la consigna: el solver avisa sin conocer la respuesta correcta.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

TIPOS = ("alldiff", "eq", "neq", "lt", "gt", "adj", "offset")
BINARIOS_NUMERICOS = ("lt", "gt", "adj", "offset")


class ErrorModelo(Exception):
    """El modelo no se puede construir. `categoria` dice por qué."""

    def __init__(self, categoria: str, mensaje: str):
        super().__init__(mensaje)
        self.categoria = categoria
        self.mensaje = mensaje


@dataclass
class ResultadoSolver:
    estado: str                         # unica | multiple | sin_solucion | timeout
    solucion: dict | None = None        # la primera solución encontrada
    n_soluciones: int = 0               # cuántas encontró (se detiene en max_soluciones)
    llamadas: int = 0                   # llamadas recursivas del backtracking
    tiempo_s: float = 0.0               # solo el tiempo del solver
    soluciones: list = field(default_factory=list)


def _es_numero(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _predicado(tipo: str, k=None):
    """Devuelve f(x, y) -> bool para una restricción binaria entre variables."""
    if tipo == "eq":
        return lambda x, y: x == y
    if tipo == "neq":
        return lambda x, y: x != y
    if tipo == "lt":
        return lambda x, y: x < y
    if tipo == "gt":
        return lambda x, y: x > y
    if tipo == "adj":
        return lambda x, y: abs(x - y) == 1
    if tipo == "offset":
        return lambda x, y: x - y == k
    raise ErrorModelo("sintaxis", f"unknown constraint type {tipo!r}")


class ModeloCSP:
    """Un modelo ya validado: dominios (con las unarias aplicadas) y una lista
    de restricciones binarias (a, b, predicado, texto)."""

    def __init__(self, modelo: dict):
        if not isinstance(modelo, dict):
            raise ErrorModelo("sintaxis", "the model is not a JSON object")
        if "variables" not in modelo:
            raise ErrorModelo("sintaxis", "missing key 'variables'")
        variables = modelo["variables"]
        if not isinstance(variables, dict) or not variables:
            raise ErrorModelo("sintaxis", "'variables' must be a non-empty object")
        self.dominios: dict[str, list] = {}
        for nombre, dom in variables.items():
            if not isinstance(dom, list) or not dom:
                raise ErrorModelo("sintaxis", f"variable {nombre!r} has no list of values")
            if any(isinstance(v, (list, dict)) for v in dom):
                raise ErrorModelo("sintaxis", f"the domain of {nombre!r} has nested values")
            vistos = []
            for v in dom:
                if v not in vistos:
                    vistos.append(v)
            self.dominios[nombre] = vistos
        self.variables = list(self.dominios)
        restricciones = modelo.get("constraints", [])
        if not isinstance(restricciones, list):
            raise ErrorModelo("sintaxis", "'constraints' must be a list")
        self.binarias: list[tuple] = []
        self.vecinos: dict[str, set] = {v: set() for v in self.variables}
        for i, r in enumerate(restricciones):
            self._agregar(i, r)

    # -- construcción -----------------------------------------------------
    def _var(self, x, i, tipo):
        if not isinstance(x, str) or x not in self.dominios:
            raise ErrorModelo("aridad_alcance",
                              f"constraint #{i} ({tipo}) uses the unknown variable {x!r}")
        return x

    def _numerica(self, v, i, tipo):
        if not all(_es_numero(x) for x in self.dominios[v]):
            raise ErrorModelo("aridad_alcance",
                              f"constraint #{i} ({tipo}) compares numbers but {v!r} has non-numeric values")

    def _agregar(self, i, r):
        if not isinstance(r, dict) or "type" not in r:
            raise ErrorModelo("sintaxis", f"constraint #{i} is not an object with 'type'")
        tipo = r["type"]
        if tipo not in TIPOS:
            raise ErrorModelo("sintaxis", f"constraint #{i}: unknown type {tipo!r}")
        if tipo == "alldiff":
            vs = r.get("vars")
            if not isinstance(vs, list) or len(vs) < 2:
                raise ErrorModelo("aridad_alcance",
                                  f"constraint #{i} (alldiff) needs a list 'vars' with 2 or more variables")
            vs = [self._var(v, i, tipo) for v in vs]
            for j, a in enumerate(vs):
                for b in vs[j + 1:]:
                    if a == b:
                        raise ErrorModelo("aridad_alcance",
                                          f"constraint #{i} (alldiff) repeats the variable {a!r}")
                    self._binaria(a, b, _predicado("neq"), f"{a} != {b}")
            return
        if "a" not in r or "b" not in r:
            raise ErrorModelo("aridad_alcance", f"constraint #{i} ({tipo}) needs 'a' and 'b'")
        a = self._var(r["a"], i, tipo)
        b = r["b"]
        k = None
        if tipo == "offset":
            k = r.get("k")
            if not _es_numero(k):
                raise ErrorModelo("aridad_alcance", f"constraint #{i} (offset) needs a number 'k'")
        b_es_variable = isinstance(b, str) and b in self.dominios
        if isinstance(b, str) and not b_es_variable and b not in self.dominios[a]:
            # un texto que no es variable ni valor posible de `a`: casi siempre un
            # nombre de variable mal escrito o inventado (error de alcance)
            raise ErrorModelo("aridad_alcance",
                              f"constraint #{i} ({tipo}) uses {b!r}, which is neither a variable nor a possible value of {a!r} (possible values: {self.dominios[a]})")
        if isinstance(b, (list, dict)):
            raise ErrorModelo("aridad_alcance", f"constraint #{i} ({tipo}) has several values in 'b'")
        if tipo in BINARIOS_NUMERICOS:
            self._numerica(a, i, tipo)
            if b_es_variable:
                self._numerica(b, i, tipo)
            elif not _es_numero(b):
                raise ErrorModelo("aridad_alcance",
                                  f"constraint #{i} ({tipo}) compares {a!r} with {b!r}, which is neither a variable nor a number")
        f = _predicado(tipo, k)
        if b_es_variable:
            if a == b:
                raise ErrorModelo("aridad_alcance", f"constraint #{i} ({tipo}) relates {a!r} to itself")
            texto = f"{a} {tipo} {b}" + (f" k={k}" if tipo == "offset" else "")
            self._binaria(a, b, f, texto)
        else:
            # unaria: filtra el dominio ahora (un dominio vacío se detecta al resolver)
            self.dominios[a] = [x for x in self.dominios[a] if f(x, b)]

    def _binaria(self, a, b, f, texto):
        self.binarias.append((a, b, f, texto))
        self.vecinos[a].add(b)
        self.vecinos[b].add(a)

    # -- consultas --------------------------------------------------------
    def violaciones(self, asignacion: dict) -> list[str]:
        """Lista de restricciones que una asignación completa incumple."""
        malas = []
        for v in self.variables:
            if v not in asignacion:
                malas.append(f"falta {v}")
            elif asignacion[v] not in self.dominios[v]:
                malas.append(f"{v}={asignacion[v]!r} fuera de su dominio")
        for a, b, f, texto in self.binarias:
            if a in asignacion and b in asignacion and not f(asignacion[a], asignacion[b]):
                malas.append(texto)
        return malas


def construir(modelo: dict) -> ModeloCSP:
    return ModeloCSP(modelo)


def resolver(modelo, max_soluciones: int = 2, limite_llamadas: int = 200_000,
             limite_segundos: float = 10.0) -> ResultadoSolver:
    """Backtracking con forward checking y MRV (la receta de la semana 6).

    `modelo` puede ser el dict JSON o un ModeloCSP ya construido. Puede lanzar
    ErrorModelo si el dict no se puede construir.
    """
    csp = modelo if isinstance(modelo, ModeloCSP) else ModeloCSP(modelo)
    t0 = time.perf_counter()
    dominios = {v: list(d) for v, d in csp.dominios.items()}
    por_var: dict[str, list] = {v: [] for v in csp.variables}
    for a, b, f, _ in csp.binarias:
        por_var[a].append((b, f, True))     # f(valor_a, valor_b)
        por_var[b].append((a, f, False))    # f(valor_a, valor_b) con b como el que se asigna
    asignacion: dict = {}
    soluciones: list[dict] = []
    llamadas = 0

    class _Corte(Exception):
        pass

    def compatible(var, val, otro, f, var_es_a, val_otro):
        return f(val, val_otro) if var_es_a else f(val_otro, val)

    def recursion():
        nonlocal llamadas
        llamadas += 1
        if llamadas > limite_llamadas or time.perf_counter() - t0 > limite_segundos:
            raise _Corte
        if len(asignacion) == len(csp.variables):
            soluciones.append(dict(asignacion))
            return len(soluciones) >= max_soluciones
        pendientes = [v for v in csp.variables if v not in asignacion]
        var = min(pendientes, key=lambda v: (len(dominios[v]), -len(csp.vecinos[v])))
        for val in list(dominios[var]):
            if not all(compatible(var, val, o, f, es_a, asignacion[o])
                       for o, f, es_a in por_var[var] if o in asignacion):
                continue
            asignacion[var] = val
            quitados = []
            vacio = False
            for o, f, es_a in por_var[var]:
                if o in asignacion:
                    continue
                for x in list(dominios[o]):
                    ok = f(val, x) if es_a else f(x, val)
                    if not ok:
                        dominios[o].remove(x)
                        quitados.append((o, x))
                if not dominios[o]:
                    vacio = True
                    break
            if not vacio and recursion():
                return True
            for o, x in quitados:
                dominios[o].append(x)
            del asignacion[var]
        return False

    try:
        if any(not d for d in dominios.values()):
            estado = "sin_solucion"
        else:
            recursion()
            estado = {0: "sin_solucion", 1: "unica"}.get(len(soluciones), "multiple")
    except _Corte:
        estado = "timeout" if not soluciones else ("multiple" if len(soluciones) > 1 else "timeout")
    return ResultadoSolver(
        estado=estado,
        solucion=soluciones[0] if soluciones else None,
        n_soluciones=len(soluciones),
        llamadas=llamadas,
        tiempo_s=time.perf_counter() - t0,
        soluciones=soluciones,
    )


def metricas(modelo: dict) -> dict:
    """Métricas de dificultad de un modelo (las usamos para los niveles)."""
    csp = ModeloCSP(modelo)
    tam = 1
    for d in modelo["variables"].values():
        tam *= max(1, len(d))
    return {
        "n_vars": len(csp.variables),
        "n_restricciones": len(modelo.get("constraints", [])),
        "n_binarias": len(csp.binarias),
        "espacio": tam,
    }
