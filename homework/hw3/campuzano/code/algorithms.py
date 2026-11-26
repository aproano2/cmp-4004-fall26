"""Algoritmos (todos escritos a mano, solo numpy) y baselines.

Convención: f(bud, prob, rng, **params). Corren hasta que Budget lanza BudgetExhausted.
Parámetros por defecto fijados a priori con valores de la literatura (NO afinados por problema).
"""
import numpy as np

# =============================================================== utilidades TSP
def rev(t, i, j):
    c = t.copy()
    c[i:j + 1] = c[i:j + 1][::-1]
    return c


def rand_pair(rng, n):
    i, j = rng.choice(n, 2, replace=False)
    return (i, j) if i < j else (j, i)


def ox(p1, p2, rng):
    n = len(p1)
    a, b = rand_pair(rng, n)
    child = -np.ones(n, dtype=int)
    child[a:b + 1] = p1[a:b + 1]
    used = np.zeros(n, bool)
    used[p1[a:b + 1]] = True
    rest = np.roll(p2, -(b + 1))
    rest = rest[~used[rest]]
    pos = np.r_[b + 1:n, 0:a]
    child[pos] = rest
    return child


def nn_tour(D, start):
    n = len(D)
    t = [start]
    vis = np.zeros(n, bool)
    vis[start] = True
    for _ in range(n - 1):
        d = D[t[-1]].copy()
        d[vis] = np.inf
        j = int(np.argmin(d))
        t.append(j)
        vis[j] = True
    return np.array(t)


# =============================================================== random search
def rs(bud, prob, rng, chunk=100):
    while True:
        if prob.kind == "continuous":
            bud.batch(rng.uniform(prob.lo, prob.hi, (chunk, prob.dim)))
        else:
            bud.batch(np.argsort(rng.random((chunk, prob.n)), axis=1))


# =============================================================== baselines específicos
def hc(bud, prob, rng):
    """Hill climbing con reinicios: (1+1) con regla 1/5 para el paso; reinicia cuando el paso colapsa."""
    D, lo, hi = prob.dim, prob.lo, prob.hi
    while True:
        x = rng.uniform(lo, hi, D)
        f = bud(x)
        s = 0.1 * (hi - lo)
        while s > 1e-7:
            y = np.clip(x + rng.normal(0, s, D), lo, hi)
            fy = bud(y)
            if fy < f:
                x, f = y, fy
                s *= 1.5
            else:
                s *= 1.5 ** (-0.25)


def two_opt(bud, t, f):
    n = len(t)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                c = rev(t, i, j)
                fc = bud(c)  # cada candidato cuenta como 1 evaluación (sin delta-eval)
                if fc < f - 1e-12:
                    t, f, improved = c, fc, True
    return t, f


def nn2opt(bud, prob, rng):
    """Vecino más cercano (desde cada ciudad) + 2-opt; al agotar arranques, ILS con double-bridge."""
    n = prob.n
    best_t, best_f, k = None, np.inf, 0
    while True:
        if k < n:
            t = nn_tour(prob.D, k)
        else:
            a, b, c = np.sort(rng.choice(np.arange(1, n), 3, replace=False))
            t = np.r_[best_t[:a], best_t[b:c], best_t[a:b], best_t[c:]]
        f = bud(t)
        t, f = two_opt(bud, t, f)
        if f < best_f:
            best_t, best_f = t, f
        k += 1


# =============================================================== GA
def ga_c(bud, prob, rng, n=50, pm=None, sigma=0.1, k=3, elite=2):
    D, lo, hi = prob.dim, prob.lo, prob.hi
    pm = pm if pm is not None else 1.0 / D
    P = rng.uniform(lo, hi, (n, D))
    F = bud.batch(P)
    m = n - elite
    while True:
        idx = np.argsort(F)[:elite]
        E, EF = P[idx], F[idx]

        def sel():
            c = rng.integers(0, n, (m, k))
            return c[np.arange(m), np.argmin(F[c], axis=1)]

        p1, p2 = P[sel()], P[sel()]
        a, b = np.minimum(p1, p2), np.maximum(p1, p2)
        d = b - a
        C = rng.uniform(a - 0.5 * d, b + 0.5 * d)  # BLX-0.5
        C = C + (rng.random((m, D)) < pm) * rng.normal(0, sigma * (hi - lo), (m, D))
        C = np.clip(C, lo, hi)
        FC = bud.batch(C)
        P, F = np.vstack([E, C]), np.concatenate([EF, FC])


def ga_t(bud, prob, rng, n=100, pm=0.3, k=3, elite=2):
    N = prob.n
    P = np.argsort(rng.random((n, N)), axis=1)
    F = bud.batch(P)
    while True:
        idx = np.argsort(F)[:elite]
        kids = [P[i].copy() for i in idx]
        while len(kids) < n:
            c1 = rng.integers(0, n, k)
            c2 = rng.integers(0, n, k)
            p1, p2 = P[c1[np.argmin(F[c1])]], P[c2[np.argmin(F[c2])]]
            ch = ox(p1, p2, rng) if rng.random() < 0.9 else p1.copy()
            if rng.random() < pm:
                i, j = rand_pair(rng, N)
                ch = rev(ch, i, j)
            kids.append(ch)
        K = np.array(kids)
        FK = np.concatenate([F[idx], bud.batch(K[elite:])])
        P, F = K, FK


def ga(bud, prob, rng, **kw):
    return (ga_c if prob.kind == "continuous" else ga_t)(bud, prob, rng, **kw)


# =============================================================== SA (enfriamiento ligado al presupuesto)
def sa_c(bud, prob, rng, T0f=0.1, Tratio=1e-5):
    D, lo, hi = prob.dim, prob.lo, prob.hi
    x = rng.uniform(lo, hi, D)
    f = bud(x)
    T0 = T0f * max(abs(f), 1.0)
    while True:
        T = T0 * Tratio ** (bud.n / bud.cap)
        s = max(0.1 * (hi - lo) * np.sqrt(T / T0), 1e-4)
        y = x.copy()
        j = rng.integers(D)
        y[j] = np.clip(y[j] + rng.normal(0, s), lo, hi)
        fy = bud(y)
        if fy < f or rng.random() < np.exp((f - fy) / T):
            x, f = y, fy


def sa_t(bud, prob, rng, T0f=0.03, Tratio=1e-3):
    n = prob.n
    t = rng.permutation(n)
    f = bud(t)
    T0 = T0f * f
    while True:
        T = T0 * Tratio ** (bud.n / bud.cap)
        i, j = rand_pair(rng, n)
        c = rev(t, i, j)
        fc = bud(c)
        if fc < f or rng.random() < np.exp((f - fc) / T):
            t, f = c, fc


def sa(bud, prob, rng, **kw):
    return (sa_c if prob.kind == "continuous" else sa_t)(bud, prob, rng, **kw)


# =============================================================== PSO (solo continuo)
def pso_clerc(bud, prob, rng, n=40, w=0.7298, c1=1.49618, c2=1.49618):
    D, lo, hi = prob.dim, prob.lo, prob.hi
    vmax = 0.2 * (hi - lo)
    X = rng.uniform(lo, hi, (n, D))
    V = rng.uniform(-vmax, vmax, (n, D))
    F = bud.batch(X)
    PB, PF = X.copy(), F.copy()
    g = int(np.argmin(PF))
    while True:
        r1, r2 = rng.random((2, n, D))
        V = np.clip(w * V + c1 * r1 * (PB - X) + c2 * r2 * (PB[g] - X), -vmax, vmax)
        X = np.clip(X + V, lo, hi)
        F = bud.batch(X)
        imp = F < PF
        PB[imp], PF[imp] = X[imp], F[imp]
        g = int(np.argmin(PF))


# =============================================================== ABC
def _fit(f):
    return 1.0 / (1.0 + f) if f >= 0 else 1.0 + abs(f)


def abc_c(bud, prob, rng, SN=20, limit=None):
    D, lo, hi = prob.dim, prob.lo, prob.hi
    limit = limit or SN * D
    X = rng.uniform(lo, hi, (SN, D))
    F = bud.batch(X)
    trial = np.zeros(SN, int)

    def visit(i):
        k = rng.integers(SN - 1)
        k += k >= i
        j = rng.integers(D)
        v = X[i].copy()
        v[j] = np.clip(X[i, j] + rng.uniform(-1, 1) * (X[i, j] - X[k, j]), lo, hi)
        fv = bud(v)
        if fv < F[i]:
            X[i], F[i], trial[i] = v, fv, 0
        else:
            trial[i] += 1

    while True:
        for i in range(SN):
            visit(i)
        fit = np.array([_fit(f) for f in F])
        p = fit / fit.sum()
        for i in rng.choice(SN, SN, p=p):
            visit(i)
        i = int(np.argmax(trial))
        if trial[i] > limit:
            X[i] = rng.uniform(lo, hi, D)
            F[i] = bud(X[i])
            trial[i] = 0


def abc_t(bud, prob, rng, SN=20, limit=None):
    n = prob.n
    limit = limit or 5 * n
    X = np.argsort(rng.random((SN, n)), axis=1)
    F = bud.batch(X)
    trial = np.zeros(SN, int)

    def neighbour(t):
        if rng.random() < 0.5:
            i, j = rand_pair(rng, n)
            return rev(t, i, j)
        i, j = rng.choice(n, 2, replace=False)  # inserción
        c = np.delete(t, i)
        return np.insert(c, j, t[i])

    def visit(i):
        v = neighbour(X[i])
        fv = bud(v)
        if fv < F[i]:
            X[i], F[i], trial[i] = v, fv, 0
        else:
            trial[i] += 1

    while True:
        for i in range(SN):
            visit(i)
        fit = 1.0 / F
        p = fit / fit.sum()
        for i in rng.choice(SN, SN, p=p):
            visit(i)
        i = int(np.argmax(trial))
        if trial[i] > limit:
            X[i] = rng.permutation(n)
            F[i] = bud(X[i])
            trial[i] = 0


def abc(bud, prob, rng, **kw):
    return (abc_c if prob.kind == "continuous" else abc_t)(bud, prob, rng, **kw)


# =============================================================== ACO (MAX-MIN Ant System)
def aco_mmas(bud, prob, rng, m=20, alpha=1.0, beta=3.0, rho=0.1):
    n, Dm = prob.n, prob.D
    eta = 1.0 / (Dm + np.eye(n))
    tau = np.ones((n, n))
    gb_f, gb_t = np.inf, None
    ar = np.arange(m)
    while True:
        base = (tau ** alpha) * (eta ** beta)
        tours = np.empty((m, n), dtype=int)
        cur = rng.integers(0, n, m)
        tours[:, 0] = cur
        vis = np.zeros((m, n), bool)
        vis[ar, cur] = True
        for s in range(1, n):
            W = base[cur] * (~vis)
            cs = np.cumsum(W, axis=1)
            r = rng.random(m) * cs[:, -1]
            nxt = np.minimum((cs < r[:, None]).sum(1), n - 1)
            tours[:, s] = nxt
            vis[ar, nxt] = True
            cur = nxt
        try:
            F = bud.batch(tours)
        finally:
            pass
        ib = int(np.argmin(F))
        if F[ib] < gb_f:
            gb_f, gb_t = F[ib], tours[ib].copy()
        tmax = 1.0 / (rho * gb_f)
        tmin = tmax / (2 * n)
        tau *= (1 - rho)
        t = tours[ib]
        a, b = t, np.roll(t, -1)
        tau[a, b] += 1.0 / F[ib]
        tau[b, a] += 1.0 / F[ib]
        np.clip(tau, tmin, tmax, out=tau)


# =============================================================== algoritmos OFICIALES (swarm.py, semana 11)
import swarm


def bind_instance(prob):
    """El ACO oficial lee NC/DIST como globales del módulo: se apuntan a la instancia TSP actual."""
    if prob.kind == "tsp":
        D = prob.D.copy()
        np.fill_diagonal(D, 1e-9)
        swarm.NC, swarm.DIST, swarm.PTS = prob.n, D, prob.pts


def pso_official(bud, prob, rng, **kw):
    swarm.pso(bud, prob.dim, bounds=(prob.lo, prob.hi), rng=rng, **kw)


def abc_official(bud, prob, rng, **kw):
    swarm.abc_optimize(bud, prob.dim, bounds=(prob.lo, prob.hi), rng=rng, **kw)


def aco_official(bud, prob, rng, **kw):
    swarm.aco(bud, rng=rng, **kw)


def aco_official_b0(bud, prob, rng, **kw):
    """Ablación: ACO oficial sin heurística de visibilidad (beta=0)."""
    swarm.aco(bud, rng=rng, beta=0.0, **kw)


ALGOS = {"RS": rs, "HC": hc, "NN2OPT": nn2opt, "GA": ga, "SA": sa,
         "PSO": pso_official, "PSO_clerc": pso_clerc, "ABC": abc_official,
         "ACO": aco_official, "ACO_b0": aco_official_b0, "ACO_MMAS": aco_mmas, "ABC_T": abc_t}
SETS = {"continuous": ["RS", "HC", "GA", "SA", "PSO", "PSO_clerc", "ABC"],
        "tsp": ["RS", "NN2OPT", "GA", "SA", "ACO", "ACO_b0", "ACO_MMAS", "ABC_T"]}
