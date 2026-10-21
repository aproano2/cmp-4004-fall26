"""Construye y ejecuta el notebook de presentación del Duel 1.

El notebook NO vuelve a llamar a Ollama ni repite el benchmark: lee los
resultados guardados en results/ y fig/, y corre las pruebas para mostrar que
el código que los generó funciona.

Uso (desde la carpeta del grupo):  python code/construir_notebook.py
Salidas: duel1_salazarD_ochoaA_chanoJ.ipynb (ejecutado) y su .html
"""
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient
from nbconvert import HTMLExporter

RAIZ = Path(__file__).resolve().parents[1]
NOMBRE = "duel1_salazarD_ochoaA_chanoJ"
celdas = []


def md(texto):
    celdas.append(nbf.v4.new_markdown_cell(texto.strip()))


def code(texto):
    celdas.append(nbf.v4.new_code_cell(texto.strip()))


md("""
# Duel 1 · Búsqueda clásica contra un LLM
**Equipo: Daniel Salazar, Andretty Ochoa y Jalil Chano · CMP-4004 · USFQ · 5 de octubre de 2026**

**Pregunta:** ¿cómo se comparan BFS, DFS, UCS, IDS y A* entre sí, contra un modelo de lenguaje y contra ese mismo modelo cuando puede usar nuestro A* como herramienta?

Usamos las mismas 80 instancias en todo el trabajo: 40 del 8-puzzle y 40 grillas con terrenos, del banco del curso. Este notebook **no vuelve a llamar al modelo**. Lee los resultados guardados en `results/` y corre las pruebas del código que los generó. El reporte completo está en `REPORT.md`.
""")

code("""
import csv, json, subprocess, sys
from pathlib import Path
from IPython.display import Image, Markdown, display

RAIZ = Path.cwd()
sys.path.insert(0, str(RAIZ / "code"))
R = RAIZ / "results"

def leer(nombre):
    with open(R / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def tabla(filas, columnas, titulos=None):
    titulos = titulos or columnas
    lineas = ["| " + " | ".join(titulos) + " |", "|" + "---|" * len(columnas)]
    lineas += ["| " + " | ".join(str(f[c]) for c in columnas) + " |" for f in filas]
    display(Markdown("\\n".join(lineas)))
""")

md("""
## 1. Verificación: las pruebas pasan

Las pruebas son el contrato entre las partes del equipo:
- `test_group.py`: el motor expande igual que el `search()` del curso, el timeout se reporta como timeout, b* y la herramienta.
- `test_heuristicas.py`: admisibilidad, dominancia y h×3.
- `test_validador.py`: las categorías de falla, con paredes y lectura tolerante.
""")

code("""
for prueba in ["test_group.py", "test_heuristicas.py", "test_validador.py"]:
    r = subprocess.run([sys.executable, f"code/tests/{prueba}"], capture_output=True,
                       text=True, encoding="utf-8", env={**__import__('os').environ, "PYTHONIOENCODING": "utf-8"})
    print(f"{prueba:<22} ->", r.stdout.strip().splitlines()[-1])
""")

md("""
## 2. Parte 1: comparación clásica

**Protocolo:** 4 niveles por dominio, 10 instancias por nivel y un timeout duro de 30 s por corrida. Reportamos medianas y rango intercuartil; un timeout cuenta como timeout, no como "sin solución". Abajo va el nivel más difícil de cada dominio; los cuatro niveles están en `results/resumen_parte1.csv`.
""")

code("""
res = leer("resumen_parte1.csv")
filas = [f for f in res if f["level"] == "16"]
for f in filas:
    for c in ("expansions_med", "max_frontier_med", "cost_med"):
        f[c] = f"{float(f[c]):,.0f}".replace(",", " ") if f[c] not in ("", "None") else "—"
    f["seconds_med"] = f"{float(f['seconds_med'])*1000:.1f}" if f["seconds_med"] not in ("", "None") else "—"
tabla(filas, ["domain", "config", "solved", "timeouts", "cost_med", "expansions_med", "max_frontier_med", "seconds_med"],
      ["dominio", "algoritmo", "resueltas", "timeouts", "costo", "expansiones", "frontera máx.", "tiempo (ms)"])
display(Image(filename="fig/expansiones_vs_nivel.png"))
""")

md("""
En el 8-puzzle, BFS, UCS e IDS crecen en línea recta en escala logarítmica, es decir, de forma **exponencial**. A* con Manhattan expande unas 100 veces menos. En la grilla, IDS se dispara: en 16×16 hizo timeout en 6 de 10 corridas.

### 2.1 UCS = A* y por qué BFS falla con costos no uniformes
""")

code("""
opt = leer("optimalidad.csv")
iguales = sum(f["astar_admisible_igual_ucs"] == "True" for f in opt)
bfs_grilla = [f for f in opt if f["domain"] == "grid" and float(f["bfs_sobrecosto"]) > 0]
print(f"A* admisible devuelve el mismo costo que UCS en {iguales}/80 instancias")
print(f"BFS es subóptimo en {len(bfs_grilla)}/40 grillas y en 0/40 puzzles (costo uniforme)")
texto = (R / "bfs_suboptimo.md").read_text(encoding="utf-8")
display(Markdown(texto[texto.index("## La instancia"):]))
""")

md("""
BFS minimiza **pasos**, no costo: en `grid-12-09` sus 11 pasos cruzan agua (`~` = 8). Su garantía de optimalidad tiene una condición, que los costos sean uniformes, y aquí no se cumple.

### 2.2 Dominancia de Manhattan sobre misplaced
""")

code("""
dom = leer("dominancia.csv")
print(f"Manhattan expandió igual o menos que misplaced en {sum(f['ok']=='True' for f in dom)}/40 instancias")
display(Image(filename="fig/dominancia.png", width=520))
""")

md("""
### 2.3 Romper la admisibilidad: h × 3

Se reportan **los dos números**: cuánto se acelera la búsqueda y cuánto empeora la solución.
""")

code("""
x3 = leer("inflado_x3.csv")
sub = [f for f in x3 if float(f["ratio_costo"]) > 1]
peor = max(x3, key=lambda f: float(f["ratio_costo"]))
print(f"Soluciones subóptimas con h×3: {len(sub)}/80")
print(f"Peor caso: {peor['instance']}: costo {peor['cost_x3']} vs óptimo {peor['cost_opt']}, "
      f"{peor['exp_x3']} expansiones vs {peor['exp_manhattan']}")
display(Image(filename="fig/inflado_x3.png"))
""")

md("""
En la grilla, h×3 acelera hasta 3,7× con pérdidas de calidad moderadas. En el 8-puzzle de profundidad 16 expande **más** y pierde optimalidad en 6 de 10 instancias. Inflar la heurística cambia la garantía por velocidad, y esa velocidad no siempre llega.

### 2.4 Factor de ramificación efectivo b*
""")

code("""
b = leer("branching_resumen.csv")
tabla([dict(f, b_star_median=f"{float(f['b_star_median']):.2f}") for f in b if f["domain"] == "8puzzle" and f["level"] != "4"],
      ["level", "config", "b_star_median"], ["profundidad", "configuración", "b* (mediana)"])
display(Image(filename="fig/branching.png"))
""")

md("""
## 3. Parte 2: el duelo

### 3.1 Cómo juzgamos al LLM

**Nunca le preguntamos al modelo si su respuesta es correcta.** Nuestro validador camina el camino paso a paso, recalcula el costo y lo compara con el óptimo de nuestro A*. Este es un ejemplo real de la corrida oficial:
""")

code("""
import validador, dominios, duelo_llm
llm = {f["instance"]: f for f in leer("llm_respuestas.csv")}
llamadas = [json.loads(l) for l in open(R / "llm_calls.jsonl", encoding="utf-8")]
ejemplo = next(l for l in llamadas if l["instance"] == "grid-5-00" and l.get("system") == "llm")
print("PROMPT (exacto del curso):\\n" + ejemplo["prompt"])
print("RESPUESTA DEL MODELO:\\n" + ejemplo["text"].strip()[-300:])
_, _, grid = dominios.buscar("grid-5-00")
print("\\nVEREDICTO:", validador.validar_texto("grid", grid, ejemplo["text"]))
""")

md("""
### 3.2 Brazo LLM: 0 de 80
""")

code("""
fallas = leer("llm_fallas_por_nivel.csv")
tabla(fallas, ["domain", "level", "illegal", "suboptimal", "wrong_cost", "malformed", "no_termina", "correct"],
      ["dominio", "nivel", "ilegal", "subóptima", "costo mal", "mal formada", "no termina", "correcta"])
display(Image(filename="fig/escalado_optimalidad.png"))
""")

md("""
El modelo no llegó a ser subóptimo ni a reportar mal un costo, porque **no produjo ni un camino legal**. En la grilla, las respuestas que no terminan pasan de 2/10 a 10/10 al crecer el tamaño.

**¿"No termina" es un error nuestro?** No. Repetimos en streaming las llamadas que Ollama cortó con HTTP 500, y Ollama dio el motivo:
""")

code("""
diag = leer("diagnostico_500.csv")
tabla(diag, ["system", "instance", "motivo", "tokens_streaming"], ["brazo", "instancia", "motivo", "tokens"])
ej = next(f for f in diag if "repeat" in f["motivo"])
print("Final del texto que el modelo estaba generando:", repr(ej["final_del_texto"]))
""")

md("""
El modelo repite el mismo token sin parar, y Ollama lo detiene con *"token repeat limit reached"*. Solo 4 llamadas se cortaron sin generar ningún token; esas fueron fallas del servidor y se repitieron. Todo está en `results/auditoria_*.csv` y en `DECISION_NOTES.md`.

### 3.3 Reproducibilidad: 5 llamadas idénticas, sin caché
""")

code("""
for archivo in ["reproducibilidad_clasica.csv", "llm_reproducibilidad_grid-8-00.csv",
                "llm_reproducibilidad_grid-5-00.csv", "herramienta_reproducibilidad_grid-5-00.csv"]:
    filas = leer(archivo)
    if "modo" in filas[0]:
        filas = [f for f in filas if f["modo"] == "identicas_t0_s0"]
    caminos = [(f.get("path") or "—", f.get("reported_cost") or f.get("cost") or "—") for f in filas]
    print(f"{archivo:<45} {filas[0]['respuestas_distintas']} distinta(s): {caminos}")
""")

md("""
A* siempre da lo mismo. El LLM, **con temperatura 0 y la misma semilla**, dio 3 resultados distintos en `grid-5-00`. "Temperatura 0" no garantiza reproducibilidad en nuestra máquina.

### 3.4 LLM + A* como herramienta: 17 de 80
""")

code("""
h = leer("herramienta_respuestas.csv")
grupos = {"copió la instancia exacta": [f for f in h if f["tool_args_match"] == "True"],
          "copió la instancia con errores": [f for f in h if f["tool_args_match"] == "False"],
          "formato que no se puede leer": [f for f in h if f["tool_called"] == "True" and f["tool_args_match"] == ""],
          "no llamó a la herramienta": [f for f in h if f["tool_called"] == "False"]}
tabla([{"caso": k, "n": len(v), "correctas": sum(f["category"] == "correct" for f in v)} for k, v in grupos.items()],
      ["caso", "n", "correctas"])
display(Image(filename="fig/fallas_llm.png"))
""")

md("""
Con el problema bien copiado, el resultado es casi siempre óptimo (16/19). El cuello de botella dejó de ser **buscar** y pasó a ser **transcribir la instancia**, y eso empeora con el tamaño.

## 4. Scorecard
""")

code("""
texto = (RAIZ / "REPORT.md").read_text(encoding="utf-8")
display(Markdown(texto[texto.index("| Eje |"):texto.index("## 3. Parte 1")]))
""")

md("""
## 5. Dónde pudimos ser injustos y qué no podemos afirmar

- Usamos heurísticas conocidas frente a un prompt escrito una sola vez y nunca ajustado.
- Es un modelo de 3B: 0/80 no dice nada de modelos grandes ni de grillas de 20×20.
- El banco es pequeño y no tiene paredes, lo que favorece a los algoritmos clásicos.
- La latencia del LLM incluye nuestro límite de 300 s y tramos en que la GPU bajó de velocidad.
- Con 10 instancias por punto, una o dos respuestas más o menos por nivel son ruido.

## 6. Conclusiones y análisis final

1. **Las garantías se cumplen, pero con sus condiciones.** A* con heurística admisible fue óptimo en 80/80 instancias, y BFS solo con costos uniformes: falló en 33/40 grillas. Al inflar la heurística se pierde la garantía, tal como dice la teoría.
2. **Una mejor heurística reduce el trabajo de forma medible.** Manhattan dominó a misplaced en 40/40 instancias y llevó b* de 1,67 (UCS) a 1,22 a profundidad 16.
3. **Un LLM pequeño no sirve como motor de búsqueda.** El modelo resolvió 0 de 80 instancias: o propone caminos ilegales o entra en bucles que no terminan, y empeora con el tamaño.
4. **Como intermediario del solver sí aporta.** Con nuestro A* como herramienta llegó a 17/80, y a 16 de 19 cuando copió bien el problema. La garantía la pone el solver; el modelo solo debe traducir bien.
5. **Lo que medimos también incluye cómo medimos.** Encontramos y documentamos varios problemas propios: corridas concurrentes, un error en nuestra herramienta y una regla de auditoría incompleta. Las corridas descartadas están en `evidencia_descartada/`, porque se califica el experimento, no el veredicto.
""")

nb = nbf.v4.new_notebook()
nb.cells = celdas
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
NotebookClient(nb, timeout=600, kernel_name="python3",
               resources={"metadata": {"path": str(RAIZ)}}).execute()
nbf.write(nb, RAIZ / f"{NOMBRE}.ipynb")
html, _ = HTMLExporter(embed_images=True).from_notebook_node(nb)
(RAIZ / f"{NOMBRE}.html").write_text(html, encoding="utf-8")
print("listo:", RAIZ / f"{NOMBRE}.ipynb")
