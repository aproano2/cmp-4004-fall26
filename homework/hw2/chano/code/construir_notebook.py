"""Construye y ejecuta el notebook de presentación del HW2.

El notebook NO vuelve a llamar a Ollama: lee los resultados guardados en
results/ y fig/, recalcula las tablas desde los CSV y corre las pruebas del
código que los generó.

    python code/construir_notebook.py
Salidas: hw2_salazarD_ochoaA_chanoJ.ipynb (ejecutado) y su .html
"""
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient
from nbconvert import HTMLExporter

RAIZ = Path(__file__).resolve().parents[1]
NOMBRE = "hw2_salazarD_ochoaA_chanoJ"
celdas = []


def md(texto):
    celdas.append(nbf.v4.new_markdown_cell(texto.strip()))


def code(texto):
    celdas.append(nbf.v4.new_code_cell(texto.strip()))


md("""
# HW2 · The Formalizer: ¿traducir a CSP o responder directo?
**Equipo: Daniel Salazar, Andretty Ochoa y Jalil Chano · CMP-4004 · USFQ · 18 de noviembre de 2026**

**Pregunta:** si un modelo de lenguaje pequeño (`qwen2.5:3b`, local; y `qwen2.5:7b` como experimento de tamaño) traduce un acertijo a un modelo CSP y un solver lo resuelve, ¿acierta más que si responde directo? Y sobre todo: **cuando falla, ¿nos damos cuenta?**

Cuatro brazos sobre los mismos 21 problemas propios (7 fáciles, 7 medios, 7 difíciles) y 3 semillas:
**A** modelo a mano → solver · **B** LLM → modelo → solver · **B′** B con hasta 3 rondas de mensajes del solver · **C** LLM responde directo.

Este notebook no vuelve a llamar al modelo: lee `results/` y `fig/`. El reporte completo está en `REPORT.md`.
""")

code("""
import csv, json, sys, subprocess
from collections import Counter
from pathlib import Path
from IPython.display import Image, Markdown, display
RAIZ = Path.cwd()
sys.path.insert(0, str(RAIZ / "code"))
from resultados import leer, TAXONOMIA
from scorecard import calcular, tabla
filas = leer()
print(Counter((f["brazo"]) for f in filas))
""")

md("## 1. El dataset y el brazo A (el techo)")
code("""
subprocess.run([sys.executable, "code/verificar_dataset.py"], check=False)
""")

md("## 2. Duel Scorecard")
code("""
display(Markdown(tabla(calcular(filas))))
""")

md("## 3. Precisión vs. dificultad")
code("""
display(Image(filename="fig/precision_vs_dificultad.png"))
""")

md("## 4. Taxonomía de errores del brazo B y la columna que importa: ¿se detecta sin la respuesta correcta?")
code("""
display(Image(filename="fig/taxonomia_b.png"))
for brazo in ("B", "C"):
    fallos = [f for f in filas if f["brazo"] == brazo and f["resultado"] != "correcto"]
    det = sum(f["detectable"] == "si" for f in fallos)
    print(f"{brazo}: {len(fallos)} fallos, {det} detectables sin gold, {len(fallos) - det} silenciosos")
""")

md("### Ejemplos verbatim de salidas del modelo (brazo B)")
code("""
intentos = [json.loads(l) for l in open("results/intentos_b.jsonl", encoding="utf-8")]
vistos = set()
for it in intentos:
    if it["iteracion"] == 1 and it["categoria"] and it["categoria"] not in vistos:
        vistos.add(it["categoria"])
        print(f"--- {it['problema_id']} semilla {it['semilla']} · {it['categoria']}")
        print("solver:", it["mensaje_solver"] or "(solución única)")
        print(it["salida"][:700], "\\n")
""")

md("## 5. Refinamiento: ¿sirve el mensaje del solver como señal de aprendizaje?")
code("""
display(Image(filename="fig/iteraciones_bp.png"))
display(Markdown(open("results/analisis.md", encoding="utf-8").read()))
""")

md("## 6. Costo por respuesta correcta")
code("""
display(Image(filename="fig/costo_por_correcta.png"))
display(Markdown(open("results/costos.md", encoding="utf-8").read()))
""")

md("## 7. Dónde se va el tiempo")
code("""
display(Image(filename="fig/tiempo_llm_vs_solver.png"))
""")

md("## 8. Experimento de tamaño: el mismo pipeline con qwen2.5:7b")
code("""
display(Image(filename="fig/modelos.png"))
display(Markdown(open("results/comparacion_modelos.md", encoding="utf-8").read()))
""")

md("## 9. Las pruebas del código pasan")
code("""
subprocess.run([sys.executable, "code/tests/test_base.py"], check=False)
subprocess.run([sys.executable, "code/tests/test_sin_fugas.py"], check=False)
subprocess.run([sys.executable, "code/verificar_enumeracion.py"], check=False)
""")

md("""
## 10. Conclusión
Con 3B, B y C aciertan lo mismo, pero **todos** los fallos de B se anuncian solos y 46 de 60 de C son silenciosos. Con 7B, B pasa a 22/63 mientras C sigue en 3/63, y B sigue sin fallos silenciosos. La recomendación (B con abstención) y el análisis de dónde pudimos ser injustos están en `REPORT.md`.
""")

nb = nbf.v4.new_notebook()
nb["cells"] = celdas
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(RAIZ)}}).execute()
ruta = RAIZ / f"{NOMBRE}.ipynb"
nbf.write(nb, ruta)
html, _ = HTMLExporter().from_notebook_node(nb)
(RAIZ / f"{NOMBRE}.html").write_text(html, encoding="utf-8")
print(f"Notebook ejecutado: {ruta}")
