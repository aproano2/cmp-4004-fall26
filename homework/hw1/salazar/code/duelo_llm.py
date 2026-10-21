"""Parte 2 — brazo LLM puro. Diseño: Jalil Chano;
integrado al motor y a los bancos del grupo.

Le damos al modelo LAS MISMAS 80 instancias de la Parte 1 como texto y validamos
cada respuesta con ``validador.py`` (nunca con el modelo). Modelo: qwen2.5:3b vía
Ollama, temperatura 0 y semilla 0 en la corrida principal, sin reintentos ni
correcciones a mano. Todas las respuestas quedan en ``.llm_cache/`` (se versiona).

Salidas:
    results/llm_respuestas.csv        una fila por instancia (COLUMNAS)
    results/llm_fallas_por_nivel.csv  las tres fallas contadas por separado
    results/llm_reproducibilidad_<id>.csv  5 llamadas idénticas a una instancia
    results/llm_calls.jsonl           cada llamada, con la marca cached
    fig/escalado_optimalidad.png      % correct vs nivel: clásico, LLM y herramienta
    fig/fallas_llm.png                categorías por nivel (barras apiladas)

Uso:
    python code/duelo_llm.py --dominio grid --por-nivel 2   # prueba corta
    python code/duelo_llm.py                                # corrida completa
    python code/duelo_llm.py --repro grid-8-00
    python code/duelo_llm.py --figuras
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime

from rutas import CACHE, FIG, RESULTS, preparar_rutas

preparar_rutas()
import dominios  # noqa: E402
import duel  # noqa: E402  curso/week04: prompt exacto del plan para la grilla
import validador  # noqa: E402
from aicourse import LLM  # noqa: E402
from aicourse.cache import cache_key  # noqa: E402
from estadistica import agrupar, escribir_csv, leer_csv  # noqa: E402

MODELO = "qwen2.5:3b"
TIMEOUT_LLM_S = 300      # el harness trae 120 s; una grilla de 16×16 a veces no alcanza
CATS = ["correct", "wrong_cost", "suboptimal", "illegal", "malformed", "no_termina", "llm_error"]
COLUMNAS = ["instance", "domain", "level", "system", "model", "temperature", "seed",
            "cached", "seconds", "tokens_in", "tokens_out", "category", "reason", "path",
            "reported_cost", "checker_cost", "optimal_cost", "suboptimal",
            "wrong_cost", "tolerant"]


# ---- prompts -----------------------------------------------------------------------

def prompt_grid(grid) -> str:
    """EXACTAMENTE ``duel.prompt_for`` del curso. No se cambia."""
    return duel.prompt_for(grid)


def prompt_puzzle(estado) -> str:
    """Prompt del 8-puzzle, escrito una vez y antes de ver resultados.

    Sigue la estructura y el formato de salida del prompt del curso para la
    grilla (inglés, letras sin separadores), para que los dos dominios reciban
    instrucciones equivalentes."""
    def tablero(t):
        return "\n".join(" ".join(str(x) if x else "_" for x in t[i:i + 3])
                         for i in range(0, 9, 3))
    return (
        "Solve this 8-puzzle with the minimum number of moves.\n"
        "The blank is '_'. Each move slides the blank one cell: "
        "U (up), D (down), L (left) or R (right); the tile there takes the blank's place.\n"
        "The blank cannot leave the 3x3 board. Every move costs 1.\n"
        "Start:\n" + tablero(estado) + "\n"
        "Goal:\n" + tablero((1, 2, 3, 4, 5, 6, 7, 8, 0)) + "\n\n"
        "Reply with the path as a sequence of moves (U/D/L/R) and its total cost.\n"
        "Format your final answer as two lines:\n"
        "PATH: <letters, no separators>\n"
        "COST: <integer>\n"
    )


def prompt_de(dominio, instancia) -> str:
    return prompt_grid(instancia) if dominio == "grid" else prompt_puzzle(instancia)


def nuevo_llm():
    return LLM(backend="ollama", model=MODELO, cache_dir=str(CACHE), timeout=TIMEOUT_LLM_S)


PAUSA_TRAS_ERROR_S = 10  # ver DECISION_NOTES: evita que el corte de una respuesta
                         # en bucle afecte a la llamada siguiente


def llamar(llm, prompt, **kw):
    """llm.complete con hora de inicio y fin (para cruzar con el log de Ollama).

    Si la llamada termina en error, esperamos PAUSA_TRAS_ERROR_S antes de seguir:
    Ollama tarda unos segundos en cancelar una generación cortada, y una llamada
    que llega en ese momento recibe un 500 que no es suyo."""
    inicio = datetime.now().isoformat(timespec="seconds")
    r = llm.complete(prompt, **kw)
    r.meta = dict(r.meta or {}, t_inicio=inicio,
                  t_fin=datetime.now().isoformat(timespec="seconds"))
    if r.error:
        time.sleep(PAUSA_TRAS_ERROR_S)
    return r


def latencia(llm, prompt, r):
    """Segundos que tardó la inferencia ORIGINAL. Si la respuesta salió de la caché,
    r.elapsed es 0, pero la caché guardó el tiempo real de cuando se generó."""
    if not r.cached:
        return r.elapsed
    registro = llm.cache.get(cache_key(llm.backend, r.model, prompt, r.temperature, r.seed))
    return (registro or {}).get("elapsed", 0.0)


def _log(registro):
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / "llm_calls.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")


def veredicto_error(error):
    """Clasifica una llamada que no devolvió texto.

    no_termina: el modelo entró en un bucle y no terminó su respuesta. Ollama
        corta la generación y responde HTTP 500, o pasamos los TIMEOUT_LLM_S
        segundos. Es una falla del MODELO (eje 8 del scorecard: "times out"):
        se reporta y NO se reintenta. Con temperatura 0 se repite igual.
    llm_error:  falla de infraestructura (Ollama apagado, conexión rechazada).
        No es una respuesta del modelo; esas llamadas se vuelven a correr."""
    if "HTTP Error 500" in error or "timed out" in error.lower():
        return validador.Veredicto("no_termina", error, None, None, None, None)
    return validador.Veredicto("llm_error", error, None, None, None, None)


def fila_de(id_inst, dominio, nivel, instancia, r, segundos, system="llm"):
    """Valida una respuesta del modelo y arma la fila del CSV."""
    if r.error:
        v = veredicto_error(r.error)
    else:
        v = validador.validar_texto(dominio, instancia, r.text)
    return {"instance": id_inst, "domain": dominio, "level": nivel, "system": system,
            "model": r.model, "temperature": r.temperature, "seed": r.seed,
            "cached": r.cached, "seconds": round(segundos, 3),
            "tokens_in": (r.meta or {}).get("prompt_eval_count"),
            "tokens_out": (r.meta or {}).get("eval_count"),
            "category": v.category, "reason": v.reason, "path": v.path,
            "reported_cost": v.reported_cost, "checker_cost": v.checker_cost,
            "optimal_cost": v.optimal_cost, "suboptimal": v.suboptimal,
            "wrong_cost": v.wrong_cost, "tolerant": v.tolerant}


# ---- corrida principal ------------------------------------------------------------------

def correr_brazo_llm(doms=dominios.DOMINIOS, por_nivel=None, salida=None, solo=None):
    """Una llamada por instancia (temperatura 0, semilla 0), validada, sin reintentos.

    ``solo``: lista de ids para volver a correr ÚNICAMENTE las llamadas que la
    auditoría marcó como falla de infraestructura; sus filas se reemplazan en el
    CSV y el resto queda igual."""
    llm = nuevo_llm()
    filas = []
    for dominio in doms:
        for id_inst, nivel, inst in dominios.instancias(dominio, por_nivel=por_nivel):
            if solo is not None and id_inst not in solo:
                continue
            prompt = prompt_de(dominio, inst)
            r = llamar(llm, prompt)
            _log({"system": "llm", "instance": id_inst, "model": r.model,
                  "temperature": r.temperature, "seed": r.seed, "cached": r.cached,
                  "elapsed": r.elapsed, "error": r.error, "meta": r.meta,
                  "prompt": prompt, "text": r.text})
            fila = fila_de(id_inst, dominio, nivel, inst, r, latencia(llm, prompt, r))
            filas.append(fila)
            tiempo = "cache" if r.cached else f"{r.elapsed:.1f}s"
            print(f"  {id_inst:<14} {fila['category']:<11} {tiempo}", file=sys.stderr)
    ruta = salida or RESULTS / "llm_respuestas.csv"
    if solo is not None and ruta.exists():
        nuevas = {f["instance"]: f for f in filas}
        filas = [nuevas.get(f["instance"], f) for f in leer_csv(ruta)]
    escribir_csv(ruta, filas, COLUMNAS)
    return filas


# ---- reproducibilidad -------------------------------------------------------------------

def reproducibilidad(id_inst="grid-8-00", n=5):
    """A) n llamadas IDÉNTICAS (temperatura 0, semilla 0) SIN caché: con la caché
    encendida las llamadas 2..n serían copias de la 1 y la medición sería falsa.
    B) complemento: temperatura 0.7 con semillas 1..n (como en week 5).
    Cada transcripción se guarda en .llm_cache/repro/."""
    dominio, nivel, inst = dominios.buscar(id_inst)
    llm = nuevo_llm()
    carpeta = CACHE / "repro"
    carpeta.mkdir(parents=True, exist_ok=True)
    prompt = prompt_de(dominio, inst)
    filas = []
    for modo, temp, semillas in (("identicas_t0_s0", 0.0, [0] * n),
                                 ("t0.7_semillas_1a5", 0.7, list(range(1, n + 1)))):
        grupo = []
        for k, semilla in enumerate(semillas, 1):
            r = llamar(llm, prompt, temperature=temp, seed=semilla, use_cache=False)
            nombre = (f"{id_inst}_llamada_{k}.json" if modo.startswith("identicas")
                      else f"{id_inst}_t07_semilla_{semilla}.json")
            (carpeta / nombre).write_text(json.dumps(
                {"prompt": prompt, "modo": modo, "temperature": temp, "seed": semilla,
                 "text": r.text, "error": r.error, "meta": r.meta, "elapsed": r.elapsed,
                 "cached": r.cached}, ensure_ascii=False, indent=2), encoding="utf-8")
            v = (veredicto_error(r.error) if r.error
                 else validador.validar_texto(dominio, inst, r.text))
            grupo.append({"instance": id_inst, "modo": modo, "llamada": k,
                          "temperature": temp, "seed": semilla, "cached": r.cached,
                          "sha_texto": hashlib.sha256(r.text.encode()).hexdigest()[:12],
                          "path": v.path, "reported_cost": v.reported_cost,
                          "category": v.category, "seconds": round(r.elapsed, 3)})
            print(f"  {modo} #{k}: {v.category} {v.path} {v.reported_cost}", file=sys.stderr)
        textos = len({g["sha_texto"] for g in grupo})
        respuestas = len({(g["path"], g["reported_cost"]) for g in grupo})
        for g in grupo:
            g["textos_distintos"] = textos
            g["respuestas_distintas"] = respuestas
        filas += grupo
        print(f"{modo}: {textos} textos distintos, {respuestas} respuestas (PATH, COST) "
              f"distintas de {n}", file=sys.stderr)
    escribir_csv(RESULTS / f"llm_reproducibilidad_{id_inst}.csv", filas)
    return filas


def reintentar_repro(id_inst, semilla):
    """Vuelve a hacer UNA llamada del complemento (temperatura 0.7) que la
    auditoría marcó como falla de infraestructura, y reemplaza su fila."""
    dominio, _, inst = dominios.buscar(id_inst)
    llm = nuevo_llm()
    prompt = prompt_de(dominio, inst)
    r = llamar(llm, prompt, temperature=0.7, seed=semilla, use_cache=False)
    (CACHE / "repro" / f"{id_inst}_t07_semilla_{semilla}.json").write_text(json.dumps(
        {"prompt": prompt, "modo": "t0.7_semillas_1a5", "temperature": 0.7, "seed": semilla,
         "text": r.text, "error": r.error, "meta": r.meta, "elapsed": r.elapsed,
         "cached": r.cached, "reintento_por_infraestructura": True},
        ensure_ascii=False, indent=2), encoding="utf-8")
    v = veredicto_error(r.error) if r.error else validador.validar_texto(dominio, inst, r.text)
    ruta = RESULTS / f"llm_reproducibilidad_{id_inst}.csv"
    filas = leer_csv(ruta)
    for f in filas:
        if f["modo"] == "t0.7_semillas_1a5" and f["seed"] == semilla:
            f.update(cached=r.cached, sha_texto=hashlib.sha256(r.text.encode()).hexdigest()[:12],
                     path=v.path, reported_cost=v.reported_cost, category=v.category,
                     seconds=round(r.elapsed, 3))
    grupo = [f for f in filas if f["modo"] == "t0.7_semillas_1a5"]
    textos = len({f["sha_texto"] for f in grupo})
    resp = len({(f["path"], f["reported_cost"]) for f in grupo})
    for f in grupo:
        f.update(textos_distintos=textos, respuestas_distintas=resp)
    escribir_csv(ruta, filas)
    print(f"reintento semilla {semilla}: {v.category}", file=sys.stderr)


# ---- tabla y figuras ---------------------------------------------------------------------

def _si(x):
    return x is True or str(x) == "True"


def tabla_fallas():
    """Las tres fallas del enunciado contadas por separado, por dominio y nivel."""
    filas = leer_csv(RESULTS / "llm_respuestas.csv")
    out = []
    for (dom, nivel), g in sorted(agrupar(filas, "domain", "level").items()):
        out.append({"domain": dom, "level": nivel, "n": len(g),
                    "illegal": sum(f["category"] == "illegal" for f in g),
                    "suboptimal": sum(_si(f["suboptimal"]) for f in g),
                    "wrong_cost": sum(_si(f["wrong_cost"]) for f in g),
                    "malformed": sum(f["category"] == "malformed" for f in g),
                    "no_termina": sum(f["category"] == "no_termina" for f in g),
                    "llm_error": sum(f["category"] == "llm_error" for f in g),
                    "correct": sum(f["category"] == "correct" for f in g),
                    "tolerant": sum(_si(f["tolerant"]) for f in g)})
    escribir_csv(RESULTS / "llm_fallas_por_nivel.csv", out)
    return out


def _tasa_clasica():
    """% de instancias donde A*-manhattan devolvió el costo óptimo (= UCS)."""
    filas = leer_csv(RESULTS / "parte1_mediciones.csv")
    ucs = {f["instance"]: f["cost"] for f in filas if f["config"] == "UCS"}
    out = {}
    for (dom, nivel), g in agrupar([f for f in filas if f["config"] == "A*-manhattan"],
                                   "domain", "level").items():
        ok = sum(f["status"] == "solved" and f["cost"] == ucs.get(f["instance"]) for f in g)
        out[(dom, nivel)] = (100 * ok / len(g), len(g))
    return out


def _tasa(ruta):
    if not ruta.exists():
        return None
    filas = [f for f in leer_csv(ruta) if f["category"] != "pending"]
    if not filas:
        return None
    return {k: (100 * sum(f["category"] == "correct" for f in g) / len(g), len(g))
            for k, g in agrupar(filas, "domain", "level").items()}


def figuras():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIG.mkdir(exist_ok=True)
    sistemas = [("A* clásico (Manhattan)", _tasa_clasica(), "o-"),
                ("LLM qwen2.5:3b", _tasa(RESULTS / "llm_respuestas.csv"), "s-"),
                ("LLM + A* como herramienta", _tasa(RESULTS / "herramienta_respuestas.csv"), "^-")]
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for eje, dom in zip(ejes, dominios.DOMINIOS):
        for nombre, tasas, estilo in sistemas:
            if not tasas:
                continue
            niveles = [n for n in dominios.NIVELES[dom] if (dom, n) in tasas]
            ys = [tasas[(dom, n)][0] for n in niveles]
            eje.plot(niveles, ys, estilo, label=nombre)
            for x, y in zip(niveles, ys):
                eje.annotate(f"n={tasas[(dom, x)][1]}", (x, y), textcoords="offset points",
                             xytext=(0, 6), ha="center", fontsize=7)
        eje.set_xticks(dominios.NIVELES[dom])
        eje.set_xlabel("profundidad óptima" if dom == "8puzzle" else "lado de la grilla")
        eje.set_title("8-puzzle" if dom == "8puzzle" else "Grilla con terrenos")
        eje.set_ylim(-5, 110)
        eje.grid(alpha=0.3)
        eje.legend(fontsize=8)
    ejes[0].set_ylabel("% de respuestas óptimas y bien reportadas")
    fig.suptitle("Escalado: tasa de respuestas correctas por tamaño")
    fig.tight_layout()
    fig.savefig(FIG / "escalado_optimalidad.png", dpi=150)
    plt.close(fig)

    colores = {"correct": "#2e7d32", "wrong_cost": "#f9a825", "suboptimal": "#ef6c00",
               "illegal": "#c62828", "malformed": "#6a1b9a", "no_termina": "#757575",
               "llm_error": "#000000"}
    sistemas = [("Brazo LLM", RESULTS / "llm_respuestas.csv"),
                ("LLM + A* como herramienta", RESULTS / "herramienta_respuestas.csv")]
    sistemas = [(n, r) for n, r in sistemas if r.exists()]
    fig, ejes = plt.subplots(len(sistemas), 2, figsize=(11, 3.8 * len(sistemas)),
                             sharey=True, squeeze=False)
    for fila_ejes, (nombre, ruta) in zip(ejes, sistemas):
        filas = leer_csv(ruta)
        for eje, dom in zip(fila_ejes, dominios.DOMINIOS):
            niveles = dominios.NIVELES[dom]
            base = [0] * len(niveles)
            for cat in CATS:
                vals = [sum(f["category"] == cat for f in filas
                            if f["domain"] == dom and f["level"] == n) for n in niveles]
                eje.bar([str(n) for n in niveles], vals, bottom=base, label=cat,
                        color=colores[cat])
                base = [a + b for a, b in zip(base, vals)]
            eje.set_xlabel("profundidad óptima" if dom == "8puzzle" else "lado de la grilla")
            eje.set_title(f"{nombre} — {'8-puzzle' if dom == '8puzzle' else 'grilla'}")
        fila_ejes[0].set_ylabel("respuestas (n = 10 por nivel)")
    manejadores = [plt.Rectangle((0, 0), 1, 1, color=colores[c]) for c in CATS]
    fig.legend(manejadores, CATS, loc="lower center", ncol=len(CATS), fontsize=8)
    fig.suptitle("Categoría de cada respuesta según nuestro validador")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(FIG / "fallas_llm.png", dpi=150)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Brazo LLM puro")
    ap.add_argument("--dominio", choices=dominios.DOMINIOS, action="append")
    ap.add_argument("--por-nivel", type=int)
    ap.add_argument("--repro", nargs="?", const="grid-8-00", metavar="ID")
    ap.add_argument("--figuras", action="store_true")
    ap.add_argument("--reintentar-repro", metavar="ID:SEMILLA")
    ap.add_argument("--solo", help="ids separados por coma (reintento de fallas de infraestructura)")
    a = ap.parse_args(argv)
    if a.reintentar_repro:
        id_, sem = a.reintentar_repro.split(":")
        reintentar_repro(id_, int(sem))
    elif a.figuras:
        tabla_fallas()
        figuras()
    elif a.repro:
        reproducibilidad(a.repro)
    else:
        correr_brazo_llm(a.dominio or dominios.DOMINIOS, a.por_nivel,
                         solo=set(a.solo.split(",")) if a.solo else None)


if __name__ == "__main__":
    main()
