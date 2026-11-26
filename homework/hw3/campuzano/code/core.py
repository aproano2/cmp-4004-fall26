"""Núcleo: Budget (oficial, semana 11), problemas y arnés de ejecución.

Regla de oro: 1 evaluación = 1 llamada a la función objetivo sobre UNA solución completa.
Todo algoritmo recibe un `Budget` y corre hasta agotar exactamente `cap` evaluaciones.
El Budget es el de swarm.py (semana 11), importado tal cual.
"""
import time
import numpy as np


from swarm import Budget as _OfficialBudget, BudgetExhausted  # Budget OFICIAL de la semana 11 (sin modificar)


class Budget(_OfficialBudget):
    """Budget oficial de swarm.py. Solo se añaden alias (cap, n) y `batch`, que evalúa fila por fila
    llamando a la propia __call__ oficial: el conteo y la traza los hace SIEMPRE el código de la semana 11."""

    @property
    def cap(self):
        return self.max_evals

    @property
    def n(self):
        return self.used

    def batch(self, X):
        return np.array([self(x) for x in X])


# ---------------------------------------------------------------- problemas continuos
class Continuous:
    def __init__(self, name, dim):
        self.name, self.dim = name, dim
        self.lo, self.hi = (-5.12, 5.12) if name in ("rastrigin", "rotrastrigin") else (-2.048, 2.048)
        if name == "rotrastrigin":  # control de separabilidad: Rastrigin con rotación ortogonal fija (semilla 7)
            self.Q = np.linalg.qr(np.random.default_rng(7).normal(size=(dim, dim)))[0]
        self.kind = "continuous"
        self.key = f"{name}_D{dim}"
        # presupuesto: 2500*D para D=2 -> 5 000 ; D=10 -> 25 000 ; D=30 -> 75 000
        self.cap = {2: 5000, 10: 25000, 30: 75000}[dim]

    def __call__(self, x):
        x = np.asarray(x)
        if self.name == "rotrastrigin":
            x = x @ self.Q.T
        if self.name in ("rastrigin", "rotrastrigin"):
            return 10 * x.shape[-1] + np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x), axis=-1)
        return np.sum(100 * (x[..., 1:] - x[..., :-1] ** 2) ** 2 + (1 - x[..., :-1]) ** 2, axis=-1)

    def vec(self, X):
        return self(X)


# ---------------------------------------------------------------- TSP
class TSP:
    def __init__(self, n):
        self.n, self.kind, self.key = n, "tsp", f"tsp_{n}"
        rng = np.random.default_rng(1000 + n)  # instancia FIJA por tamaño
        self.pts = rng.random((n, 2))
        self.D = np.sqrt(((self.pts[:, None] - self.pts[None]) ** 2).sum(-1))
        self.cap = 1000 * n  # 20k, 30k, 50k

    def __call__(self, t):
        t = np.asarray(t)
        return self.D[t, np.roll(t, -1)].sum()

    def vec(self, P):
        P = np.asarray(P)
        return self.D[P, np.roll(P, -1, axis=1)].sum(axis=1)


def make_problem(key):
    a, b = key.rsplit("_", 1)
    return TSP(int(b)) if a == "tsp" else Continuous(a, int(b[1:]))


def run_one(problem_key, algo_name, seed, params=None, algos=None):
    """Ejecuta un algoritmo con presupuesto exacto. Devuelve (traza, mejor, segundos)."""
    from algorithms import ALGOS
    prob = make_problem(problem_key)
    bud = Budget(prob, prob.cap)
    import algorithms; algorithms.bind_instance(prob)
    rng = np.random.default_rng(seed)
    t0 = time.perf_counter()
    try:
        ALGOS[algo_name](bud, prob, rng, **(params or {}))
    except BudgetExhausted:
        pass
    dt = time.perf_counter() - t0
    assert bud.used == bud.max_evals, (algo_name, problem_key, bud.used, bud.max_evals)
    tr = np.array(bud.trace)
    assert len(tr) == bud.max_evals
    return tr, float(bud.best), dt
