"""Taxonomía de errores del brazo B, análisis del refinamiento (B') y comparación
de detectabilidad B vs C. Lee los CSV y results/intentos_b.jsonl; escribe
taxonomy.md y results/analisis.md (tablas listas para el REPORT).

    python code/taxonomia.py                 # datos reales
    python code/taxonomia.py --sufijo _ejemplos

Para cada fallo de B (primer intento) guarda la salida cruda del modelo. En los
fallos "problema_errado" (silenciosos) agrega, usando el gold y el modelo_mano
SOLO para el análisis, qué restricciones del modelo a mano incumple la solución
del LLM: eso muestra qué premisa se perdió o se tradujo mal.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from csp_motor import ModeloCSP  # noqa: E402
from problemas import cargar, ejemplos  # noqa: E402
from resultados import CARPETA, ERRORES_C, RAIZ, TAXONOMIA, leer  # noqa: E402

NOMBRES = {
    "sintaxis": "Sintaxis rota (no parsea)",
    "sobre_restringido": "Sintaxis válida, sobre-restringido (sin solución)",
    "sub_restringido": "Sintaxis válida, sub-restringido (varias soluciones, devolvió una equivocada)",
    "problema_errado": "Modelo válido del problema equivocado (premisas perdidas o inventadas)",
    "aridad_alcance": "Errores de alcance / aridad (variable inexistente, argumentos o tipos mal)",
    "timeout": "Timeout del solver",
    "no_termina": "El LLM no terminó en 300 s (no hubo modelo)",
}


DESCRIPCION = {
    "sintaxis": "la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.",
    "sobre_restringido": "el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.",
    "sub_restringido": "al modelo le falta (o tiene demasiado débil) alguna pista: el solver encuentra al menos dos soluciones.",
    "problema_errado": "el modelo tiene solución única, pero es la de otro problema: alguna pista se tradujo mal y el solver no puede notarlo.",
    "aridad_alcance": "una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.",
    "timeout": "el solver agotó su presupuesto de llamadas.",
    "no_termina": "el LLM no terminó de responder en 300 s.",
}
# Anotaciones a mano de los casos que discutimos en el REPORT (§3).
NOTAS = {
    ("facil-07", 0): "las 5 pistas están bien traducidas, pero el JSON termina en `}}` en vez de `}]}`: falta cerrar la lista de restricciones.",
    ("facil-07", 1): "junta a los 3 viajeros y los 3 colores de auto en un solo `alldiff` con dominio {1, 2, 3}: seis valores distintos en tres posiciones es imposible.",
    ("facil-03", 2): "traduce los enlaces del mapa (\"Ford–Gorge\") como `offset` (\"a la derecha de\") sobre colores, y además pone todas las regiones en un `alldiff`.",
    ("dificil-01", 1): "el `alldiff` de colores quedó con 4 de los 5 colores (falta `Red`) y no tradujo la pista del silbato; por eso `Whistle` queda libre.",
    ("facil-01", 2): "inventa una quinta pista (`offset Red Yellow`) en un problema de 4 pistas; el refinamiento de B′ termina convirtiendo este error en uno silencioso (ver REPORT §3, ejemplo 5).",
}


def _numeros(x):
    """Convierte "3" -> 3 dentro de un modelo (para el análisis de tipos estrictos)."""
    if isinstance(x, dict):
        return {k: _numeros(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_numeros(v) for v in x]
    if isinstance(x, str) and x.strip().lstrip("-").isdigit():
        return int(x)
    return x


def rescatables(fallos, por_clave, problemas) -> dict:
    """Cuántos fallos de B serían correctos con un parser más tolerante:
    cerrar llaves que faltan al final y convertir números escritos como texto.
    Es un análisis de honestidad: no cambia la clasificación."""
    from brazo_b import evaluar_salida
    from problemas import calificar
    from respuesta_c import extraer_json
    cuenta = {"cerrar_llaves": 0, "numeros_texto": 0, "ambos": 0}
    for f in fallos:
        it = por_clave[(f["problema_id"], int(f["semilla"]))][0]
        p = problemas.get(f["problema_id"])
        texto = it["salida"].strip()
        for nombre, arreglo in (("cerrar_llaves", lambda t: t + "}"), ("numeros_texto", None), ("ambos", None)):
            candidatos = [texto, texto + "}", texto + "}}"] if nombre != "numeros_texto" else [texto]
            ok = False
            for c in candidatos:
                try:
                    modelo = extraer_json(c)
                except Exception:  # noqa: BLE001
                    continue
                if nombre != "cerrar_llaves":
                    modelo = _numeros(modelo)
                ev = evaluar_salida(json.dumps(modelo), p)
                if not ev["categoria"] and calificar(p, ev["solucion"])[0] == "correcto":
                    ok = True
                break
            cuenta[nombre] += ok
    return cuenta


def _pct(a, b):
    return f"{100 * a / b:.0f} %" if b else "-"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sufijo", default="", help="'' o _ejemplos")
    args = ap.parse_args()
    sx = args.sufijo
    problemas = {p["id"]: p for p in (ejemplos() if sx == "_ejemplos" else cargar())}
    filas_b = leer(f"brazo_b{sx}.csv")
    intentos = [json.loads(l) for l in open(CARPETA / f"intentos_b{sx}.jsonl", encoding="utf-8")]
    por_clave = defaultdict(list)
    for it in intentos:
        por_clave[(it["problema_id"], it["semilla"])].append(it)

    B = [f for f in filas_b if f["brazo"] == "B"]
    Bp = [f for f in filas_b if f["brazo"] == "Bp"]
    fallos = [f for f in B if f["resultado"] != "correcto"]
    conteo = Counter(f["categoria_error"] for f in fallos)

    out = ["# Taxonomía de errores del brazo B", "",
           f"Modelo: `{B[0]['modelo'] if B else '?'}`. Intentos de B: {len(B)}; fallos: {len(fallos)}. "
           "Cada fallo de B (primer intento, sin refinamiento) está clasificado abajo con la salida del modelo.", "",
           "| Categoría | Fallos | % de fallos | ¿Detectable sin ground truth? | ¿Lo detectamos en nuestros datos? |",
           "|---|---|---|---|---|"]
    for cat, nombre in NOMBRES.items():
        n = conteo.get(cat, 0)
        teoria = {"si": "Sí", "no": "No"}[TAXONOMIA[cat]]
        if cat == "sub_restringido":
            teoria = "A veces (sí, si el solver cuenta soluciones)"
        if cat == "aridad_alcance":
            teoria = "A veces (sí, cuando rompe el modelo)"
        visto = "-" if n == 0 else ("sí, en los %d" % n if TAXONOMIA[cat] == "si" else "no: solo con el gold")
        out.append(f"| {nombre} | {n} | {_pct(n, len(fallos))} | {teoria} | {visto} |")
    det = sum(1 for f in fallos if f["detectable"] == "si")
    rescate = rescatables(fallos, por_clave, problemas)
    out += [f"Con un parser más tolerante (análisis de honestidad; no cambia la clasificación), de estos "
            f"{len(fallos)} fallos serían correctos: {rescate['cerrar_llaves']} cerrando la llave final que "
            f"falta, {rescate['numeros_texto']} convirtiendo números escritos como texto y {rescate['ambos']} "
            "con ambos arreglos.", "", f"**Fallos de B detectables sin ground truth: {det}/{len(fallos)} ({_pct(det, len(fallos))}).**", ""]

    out.append("## Cada fallo, con la salida del modelo\n")
    for f in sorted(fallos, key=lambda x: (x["categoria_error"], x["problema_id"], x["semilla"])):
        it = por_clave[(f["problema_id"], int(f["semilla"]))][0]
        p = problemas.get(f["problema_id"])
        out.append(f"### {f['problema_id']} · semilla {f['semilla']} · `{f['categoria_error']}`\n")
        if it["mensaje_solver"]:
            out.append(f"- Lo que dijo el solver: {it['mensaje_solver']}")
        if f["categoria_error"] == "problema_errado" and p:
            try:
                sol = json.loads(f["respuesta"]) if f["respuesta"] else {}
                viol = ModeloCSP(p["modelo_mano"]).violaciones({k: v for k, v in sol.items()})
                viol = [v for v in viol if not v.startswith("falta")]
                out.append(f"- Restricciones del modelo a mano que incumple (análisis con gold): {viol[:6]}")
            except Exception as e:  # noqa: BLE001
                out.append(f"- (no se pudo comparar con el modelo a mano: {e})")
        if it["detalle"]:
            out.append(f"- Diferencias con el gold: {'; '.join(it['detalle'][:6])}")
        nota = NOTAS.get((f["problema_id"], int(f["semilla"])))
        out.append(f"- Qué salió mal: {nota or DESCRIPCION[f['categoria_error']]}")
        out += ["", "```json", it["salida"].strip()[:3000], "```", ""]

    (RAIZ / f"taxonomy{sx}.md").write_text("\n".join(out), encoding="utf-8")

    # ---- refinamiento y comparación B vs C (para el REPORT) -----------------
    ana = ["# Análisis para el REPORT", "", "## Refinamiento (B')", ""]
    hist = Counter()
    nunca = 0
    primera_cat_fijados, primera_cat_sobreviven = Counter(), Counter()
    for f in Bp:
        its = por_clave[(f["problema_id"], int(f["semilla"]))]
        primera = its[0]["categoria"]
        if f["resultado"] == "correcto":
            hist[int(f["iteraciones"])] += 1
            if int(f["iteraciones"]) > 1:
                primera_cat_fijados[primera] += 1
        else:
            nunca += 1
            if f["categoria_error"] and TAXONOMIA.get(f["categoria_error"]) == "si" and int(f["iteraciones"]) > 1:
                primera_cat_sobreviven[primera] += 1
    okB = sum(f["resultado"] == "correcto" for f in B)
    okBp = sum(f["resultado"] == "correcto" for f in Bp)
    ana += [f"- B: {okB}/{len(B)} ({_pct(okB, len(B))}) · B': {okBp}/{len(Bp)} ({_pct(okBp, len(Bp))}) · "
            f"delta = {okBp - okB} instancias", "",
            "| Iteraciones hasta acertar | Instancias |", "|---|---|"]
    for k in sorted(hist):
        ana.append(f"| {k} | {hist[k]} |")
    ana += [f"| nunca convergió | {nunca} |", "",
            f"- Primer error de los que el refinamiento arregló: {dict(primera_cat_fijados)}",
            f"- Primer error de los que sobrevivieron 3 rondas con un error visible: {dict(primera_cat_sobreviven)}",
            "", "## Detectabilidad: B vs C", ""]
    try:
        C = leer("brazo_c.csv" if not sx else f"brazo_c{sx}.csv")
    except FileNotFoundError:
        C = []
    malC = [f for f in C if f["resultado"] != "correcto"]
    detC = sum(1 for f in malC if f["detectable"] == "si")
    ana += ["| Brazo | Fallos | Detectables sin gold | Silenciosos |", "|---|---|---|---|",
            f"| B | {len(fallos)} | {det} | {len(fallos) - det} |",
            f"| C | {len(malC)} | {detC} | {len(malC) - detC} |", ""]
    if malC:
        ana.append(f"- Errores de C por tipo: {dict(Counter(f['categoria_error'] for f in malC))} "
                   f"(detectable según {ERRORES_C})")
    (CARPETA / f"analisis{sx}.md").write_text("\n".join(ana), encoding="utf-8")
    print("\n".join(ana))
    print(f"\nEscrito taxonomy{sx}.md y results/analisis{sx}.md")


if __name__ == "__main__":
    main()
