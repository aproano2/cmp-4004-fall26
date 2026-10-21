# Duel 1 — Salazar, Ochoa y Chano

Comparación de BFS, DFS, UCS, IDS y A* entre sí, contra un LLM (`qwen2.5:3b` en Ollama) y contra ese mismo LLM con nuestro A* como herramienta. Usamos las mismas 80 instancias en todos los casos: 8-puzzle y grilla con terrenos, 4 niveles × 10 instancias.

- Consigna: [`referencias/hw1/hw-1-search.md`](referencias/hw1/hw-1-search.md)
- **Presentación:** [`duel1_salazarD_ochoaA_chanoJ.ipynb`](duel1_salazarD_ochoaA_chanoJ.ipynb) (ejecutado; versión de lectura en `.html`)
- Reporte: [`REPORT.md`](REPORT.md) · Decisiones: [`DECISION_NOTES.md`](DECISION_NOTES.md) · IA: [`AI_LOG.md`](AI_LOG.md)

## Estado y resultados principales

Las tres partes están completas y todas las pruebas pasan: 9 de la base, 7 de heurísticas (incluida la comprobación en los 181 440 estados del 8-puzzle) y 9 del validador.

| Sistema | Correctas (de 80) | Evidencia |
|---|---|---|
| A*-Manhattan (clásico) | 80 | `results/parte1_mediciones.csv` |
| LLM `qwen2.5:3b` | 0 | `results/llm_respuestas.csv` |
| LLM + nuestro A* como herramienta | 17 | `results/herramienta_respuestas.csv` |

Quién hizo qué: Andretty Ochoa las heurísticas y los análisis 2 y 3 (PR #4); Jalil Chano el diseño del validador, del brazo LLM y de la reproducibilidad; Daniel Salazar la base, los análisis 1 y 4, el brazo con herramienta, la integración y el reporte. El uso de IA está en `AI_LOG.md`.

Las corridas que descartamos están en `evidencia_descartada/`, cada una con un README que explica por qué: dos procesos a la vez contra Ollama, y un error de nuestra herramienta en el 8-puzzle que ya corregimos.

## Ejecución

Desde la raíz del repositorio, en PowerShell y con Python 3.10 o posterior:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r homework\hw1\duel1_salazarD_ochoaA_chanoJ\requirements.txt
cd homework\hw1\duel1_salazarD_ochoaA_chanoJ
$env:PYTHONIOENCODING="utf-8"
python code\tests\test_group.py          # base
python code\tests\test_heuristicas.py    # Andretty
python code\tests\test_validador.py      # Jalil
python code\benchmark.py                 # Parte 1 completa (timeout 30 s por corrida)
python code\analisis_heuristicas.py      # análisis 2 y 3 + figuras
python code\analisis_optimalidad.py      # análisis 1 y 4
ollama pull qwen2.5:3b
python code\duelo_llm.py                 # brazo LLM, reproducibilidad, escalado
python code\herramienta.py               # brazo con herramienta
python code\duelo_llm.py --repro grid-8-00   # reproducibilidad (también grid-5-00)
python code\duelo_llm.py --figuras       # figuras y conteo de fallas
python code\auditoria_ollama.py --por-hora   # auditoría de llamadas sin texto
python code\scorecard.py                 # números del scorecard
python code\construir_notebook.py        # notebook de presentación (lee results/, no llama al LLM)
```

## Estructura

```
REPORT.md  AI_LOG.md  DECISION_NOTES.md  SOURCE_MANIFEST.json  duel1_salazarD_ochoaA_chanoJ.ipynb (.html)
code/
  motor.py              BFS/DFS/UCS/IDS/A* con expansiones, frontera máxima, tiempo y timeout
  dominios.py           bancos del curso e ids de instancia
  benchmark.py          Parte 1 → results/parte1_mediciones.csv
  estadistica.py        CSV, mediana e IQR, huellas (sin pandas)
  heuristicas.py        (Andretty)  analisis_heuristicas.py (Andretty)
  validador.py          (Jalil)     duelo_llm.py          (Jalil)
  analisis_optimalidad.py (Daniel)  herramienta.py        (Daniel)
  auditoria_ollama.py, diagnostico_500.py, restaurar_primer_intento.py   auditoría de llamadas sin texto
  admisibilidad_exhaustiva.py   garantía de las heurísticas en los 181 440 estados
  scorecard.py, construir_notebook.py   números del scorecard y notebook
  tests/                pruebas de la base y de aceptación de cada parte
  curso/week03, week04  archivos del profe, intactos
  aicourse/             harness del curso, copiado sin cambios de nuestra Week 05
results/  fig/  .llm_cache/
evidencia_descartada/   corridas que no usamos, cada una con su README
referencias/            consigna, resources, studios 3 y 4, notebooks y slides del curso
```
