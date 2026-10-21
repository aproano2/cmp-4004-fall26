"""Parte 1, análisis 2 y 3 + figuras de la Parte 1. Autoría: Andretty Ochoa.

Lee SOLO ``results/parte1_mediciones.csv`` (no vuelve a correr búsquedas, salvo
que se indique). Con ``estadistica.py``: medianas e IQR, nunca solo promedios.

Salidas (contrato del grupo):
    results/dominancia.csv        instance, exp_misplaced, exp_manhattan, ok
    results/inflado_x3.csv        domain, level, instance, cost_opt, cost_x3,
                                  ratio_costo, exp_manhattan, exp_x3, speedup
    results/resumen_parte1.csv    domain, level, config, n, solved, timeouts,
                                  med/q1/q3 de expansions, max_frontier, seconds, cost
    fig/expansiones_vs_nivel.png  log-y, una curva por config, barras = IQR
    fig/dominancia.png            dispersión exp_misplaced vs exp_manhattan + diagonal
    fig/inflado_x3.png            speedup y pérdida de calidad por nivel

Uso:  python code/analisis_heuristicas.py
"""
from rutas import FIG, RESULTS, preparar_rutas
from estadistica import escribir_csv, leer_csv, mediana_iqr, agrupar
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

preparar_rutas()


def resumen_parte1():
    """Tabla por (dominio, nivel, config): n, resueltas, timeouts y mediana [q1, q3]
    de expansions, max_frontier, seconds y cost. Los timeouts NO entran en las
    medianas de costo: se cuentan aparte (el enunciado lo exige)."""

    filas = leer_csv(RESULTS / "parte1_mediciones.csv")
    grupos = agrupar(filas, "domain", "level", "config")

    resumen = []

    for (domain, level, config), grupo in grupos.items():
        resueltas = [f for f in grupo if f["status"] == "solved"]

        fila_resumen = {
            "domain": domain,
            "level": level,
            "config": config,
            "n": len(grupo),
            "solved": len(resueltas),
            "timeouts": sum(1 for f in grupo if f["status"] == "timeout"),
        }

        # Solo corridas resueltas: un timeout corta el conteo en un punto
        # arbitrario y bajaría la mediana. Los timeouts se cuentan aparte.
        for campo in ("expansions", "max_frontier", "seconds"):
            mediana, q1, q3, _ = mediana_iqr(
                [f[campo] for f in resueltas]
            )

            fila_resumen[f"{campo}_med"] = mediana
            fila_resumen[f"{campo}_q1"] = q1
            fila_resumen[f"{campo}_q3"] = q3

        mediana, q1, q3, _ = mediana_iqr(
            [f["cost"] for f in resueltas]
        )

        fila_resumen["cost_med"] = mediana
        fila_resumen["cost_q1"] = q1
        fila_resumen["cost_q3"] = q3

        resumen.append(fila_resumen)

    escribir_csv(RESULTS / "resumen_parte1.csv", resumen)

    return resumen


def dominancia():
    """Análisis 2: en las 40 instancias del 8-puzzle, exp(A*-manhattan) <=
    exp(A*-misplaced). Si alguna falla, NO la escondas: es un bug en una
    heurística (o un empate de f resuelto distinto); encuéntralo y documéntalo."""

    filas = leer_csv(RESULTS / "parte1_mediciones.csv")

    puzzle = [
        f for f in filas
        if f["domain"] == "8puzzle"
        and f["config"] in ("A*-misplaced", "A*-manhattan")
    ]

    por_instancia = agrupar(puzzle, "instance")
    resultado = []

    for (instance,), grupo in por_instancia.items():
        configs = {f["config"]: f for f in grupo}

        misplaced = configs["A*-misplaced"]
        manhattan = configs["A*-manhattan"]

        exp_misplaced = misplaced["expansions"]
        exp_manhattan = manhattan["expansions"]

        resultado.append({
            "instance": instance,
            "exp_misplaced": exp_misplaced,
            "exp_manhattan": exp_manhattan,
            "ok": exp_manhattan <= exp_misplaced,
        })

    escribir_csv(RESULTS / "dominancia.csv", resultado)

    return resultado


def inflado_x3():
    """Análisis 3: A*-manhattan_x3 vs A*-manhattan en ambos dominios.
    Reporta LOS DOS números por nivel: speedup = exp_manhattan / exp_x3 (y en
    segundos) y pérdida de calidad = cost_x3 / cost_opt (y cuántas instancias
    salieron subóptimas). Señala la peor instancia."""

    filas = leer_csv(RESULTS / "parte1_mediciones.csv")

    seleccionadas = [
        f for f in filas
        if f["config"] in ("A*-manhattan", "A*-manhattan_x3")
    ]

    por_instancia = agrupar(seleccionadas, "domain", "level", "instance")
    resultado = []

    for (domain, level, instance), grupo in por_instancia.items():
        configs = {f["config"]: f for f in grupo}

        manhattan = configs["A*-manhattan"]
        x3 = configs["A*-manhattan_x3"]

        cost_opt = manhattan["cost"]
        cost_x3 = x3["cost"]

        exp_manhattan = manhattan["expansions"]
        exp_x3 = x3["expansions"]
        
        seconds_manhattan = manhattan["seconds"]
        seconds_x3 = x3["seconds"]

        resultado.append({
            "domain": domain,
            "level": level,
            "instance": instance,
            "cost_opt": cost_opt,
            "cost_x3": cost_x3,
            "ratio_costo": cost_x3 / cost_opt,
            "exp_manhattan": exp_manhattan,
            "exp_x3": exp_x3,
            "speedup": exp_manhattan / exp_x3,
            "seconds_manhattan": seconds_manhattan,
            "seconds_x3": seconds_x3,
            "speedup_seconds": (
                seconds_manhattan / seconds_x3
                if seconds_x3 > 0
                else None
            ),
        })

    escribir_csv(RESULTS / "inflado_x3.csv", resultado)

    return resultado


COLORES = {"BFS": "#1f77b4", "DFS": "#9467bd", "UCS": "#e377c2", "IDS": "#8c564b",
           "A*-misplaced": "#2ca02c", "A*-manhattan": "#d62728",
           "A*-manhattan_x3": "#ff7f0e"}


def figuras():
    """Genera las tres figuras requeridas para el análisis de la Parte 1."""

    # ============================================================
    # FIGURA 1: expansiones vs nivel
    # ============================================================

    resumen = leer_csv(RESULTS / "resumen_parte1.csv")

    dominios = ["8puzzle", "grid"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, domain in zip(axes, dominios):
        filas_domain = [
            f for f in resumen
            if f["domain"] == domain
        ]

        configs = sorted(set(f["config"] for f in filas_domain))

        for config in configs:
            datos = sorted(
                [f for f in filas_domain if f["config"] == config],
                key=lambda f: f["level"]
            )

            niveles = [f["level"] for f in datos]
            medianas = [f["expansions_med"] for f in datos]

            error_inferior = [
                f["expansions_med"] - f["expansions_q1"]
                for f in datos
            ]

            error_superior = [
                f["expansions_q3"] - f["expansions_med"]
                for f in datos
            ]

            ax.errorbar(
                niveles,
                medianas,
                yerr=[error_inferior, error_superior],
                marker="o",
                capsize=4,
                label=config,
                color=COLORES.get(config)   # mismo color por config en ambos paneles
            )

            for f in datos:
                ax.annotate(
                    f"n={f['solved']}",      # la mediana usa solo corridas resueltas
                    (f["level"], f["expansions_med"]),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    fontsize=7
                )

        ax.set_yscale("log")
        ax.set_xlabel("Nivel")
        ax.set_ylabel("Expansiones (escala logarítmica)")
        ax.set_title(f"Dominio: {domain}")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7)

    fig.suptitle("Expansiones por nivel y configuración")
    fig.tight_layout()

    fig.savefig(
        FIG / "expansiones_vs_nivel.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.close(fig)

    # ============================================================
    # FIGURA 2: dominancia Manhattan vs misplaced
    # ============================================================

    datos_dominancia = leer_csv(RESULTS / "dominancia.csv")

    x = [f["exp_misplaced"] for f in datos_dominancia]
    y = [f["exp_manhattan"] for f in datos_dominancia]

    fig, ax = plt.subplots(figsize=(7, 6))

    ax.scatter(x, y)

    limite = max(x + y)

    ax.plot(
        [0, limite],
        [0, limite],
        linestyle="--",
        label="y = x"
    )

    ax.set_xlabel("Expansiones A*-misplaced")
    ax.set_ylabel("Expansiones A*-manhattan")
    ax.set_title("Dominancia de Manhattan sobre misplaced")
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()

    fig.savefig(
        FIG / "dominancia.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.close(fig)

    # ============================================================
    # FIGURA 3: Manhattan x3
    # ============================================================

    datos_x3 = leer_csv(RESULTS / "inflado_x3.csv")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for domain in dominios:
        datos_domain = [
            f for f in datos_x3
            if f["domain"] == domain
        ]

        por_nivel = agrupar(datos_domain, "level")

        niveles = []
        speedups = []
        ratios = []
        cantidades = []

        for (level,), grupo in sorted(por_nivel.items()):
            speedup_med, _, _, n = mediana_iqr(
                [f["speedup"] for f in grupo]
            )

            ratio_med, _, _, _ = mediana_iqr(
                [f["ratio_costo"] for f in grupo]
            )

            niveles.append(level)
            speedups.append(speedup_med)
            ratios.append(ratio_med)
            cantidades.append(n)

        axes[0].plot(
            niveles,
            speedups,
            marker="o",
            label=domain
        )

        axes[1].plot(
            niveles,
            ratios,
            marker="o",
            label=domain
        )

        for level, valor, n in zip(niveles, speedups, cantidades):
            axes[0].annotate(
                f"n={n}",
                (level, valor),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                fontsize=8
            )

        for level, valor, n in zip(niveles, ratios, cantidades):
            axes[1].annotate(
                f"n={n}",
                (level, valor),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                fontsize=8
            )

    axes[0].axhline(
        1,
        linestyle="--"
    )

    axes[0].set_xlabel("Nivel")
    axes[0].set_ylabel("Speedup de expansiones")
    axes[0].set_title("Reducción de expansiones con Manhattan x3")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].axhline(
        1,
        linestyle="--"
    )

    axes[1].set_xlabel("Nivel")
    axes[1].set_ylabel("Costo x3 / costo óptimo")
    axes[1].set_title("Pérdida de calidad con Manhattan x3")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    fig.suptitle("Efecto de inflar la heurística Manhattan por 3")
    fig.tight_layout()

    fig.savefig(
        FIG / "inflado_x3.png",
        dpi=200,
        bbox_inches="tight"
    )

    plt.close(fig)


if __name__ == "__main__":
    resumen_parte1()
    dominancia()
    inflado_x3()
    figuras()
