# HW2 — SAT translation duel (coloreado de grafos con 3 colores)

**Modelo bajo prueba:** `qwen2.5:3b` vía Ollama. La versión del modelo, el hardware y el sistema operativo utilizados están documentados en `REPORT.md`, §1.

**Estado:** experimento ejecutado. Resultados y métricas en `results/`, seis figuras en `fig/` y conclusiones en `REPORT.md`. Los comandos siguientes permiten repetir el experimento; no son pasos pendientes para esta entrega.

## Requisitos
Python 3.10+, `pip install -r requirements.txt` (solo matplotlib), Ollama en ejecución con el modelo descargado.

## Flujo
```bash
python code/run_tests.py                 # 1) tests offline (dataset, solver vs fuerza bruta, pipeline con LLM simulado)
ollama pull qwen2.5:3b && ollama serve   # 2) (en Windows suele estar ya corriendo)
python code/run_experiment.py            # 3) 3 corridas, T=0.7, seeds 0-2  (≈ 20×3×(1+≤3+1) llamadas)
python code/run_experiment.py --temperature 0 --runs 1 --outdir results_greedy   # (opcional) corrida voraz
python code/run_experiment.py --feedback rich --outdir results_rich              # (opcional) ablación: B' con núcleo UNSAT
python code/analyze.py --price-in <USD/Mtok> --price-out <USD/Mtok> \
       --price-source "Groq|Together, modelo equivalente, fecha"                  # 4) CSV, figuras, taxonomy.md
```
Si usas la ablación, pasa `--resdir results_rich --figdir fig_rich --taxonomy-md taxonomy_rich.md` a `analyze.py`.
Los precios **no están codificados**. En esta entrega el coste se reporta en tokens y segundos por respuesta correcta, sin conversión monetaria.

## Estructura
| ruta | contenido |
|---|---|
| `problems/dataset.json` | 20 problemas (6 easy / 7 medium / 7 hard), prompt en español, grafo y ground truth |
| `code/encoding.py` | codificación CNF de referencia (brazo A), decodificación, validadores, bandas de dificultad |
| `code/sat_solver.py` | DPLL propio, validación de CNF, núcleo UNSAT |
| `code/llm.py` | cliente Ollama + caché (conserva la latencia original; no cachea errores de red) |
| `code/prompts.py`, `code/arms.py` | prompts, brazos A/B/B′/C, bucle de refinamiento con traza por intento |
| `code/taxonomy.py` | clasificación de fallos: anunciados vs. silenciosos + diff de cláusulas |
| `code/run_experiment.py`, `code/analyze.py` | ejecución y análisis |
| `results/` | `metrics.csv`, `records.jsonl` (salidas literales), `taxonomy.json`, `bprime_traces.json`, `scorecard.*`, `cost.csv`, … |
| `fig/` | 6 figuras (accuracy vs dificultad, tiempos, convergencia, detectabilidad, heatmap, taxonomía) |
| `taxonomy.md` | generado automáticamente por `analyze.py` |

## Protocolo (decisiones de diseño)
- **Dificultad** = número de cláusulas del CNF de referencia (4n+3m para k=3), con bandas fijadas antes de ejecutar: easy ≤ 40, medium 41–70, hard ≥ 71 (verificado en `test_reference.py`).
- **Correcto** = la asignación devuelta cubre todos los vértices, usa colores válidos y no viola ninguna arista (no se compara con la solución guardada: hay muchas válidas).
- **A**: codificador parametrizado escrito una vez a mano + DPLL. Es el techo.
- **B**: un intento. **B′**: hasta 3 intentos; el primero es *la misma llamada* que B (misma semilla → misma respuesta cacheada), de modo que la comparación B vs B′ es pareada.
- **Feedback de B′** (nunca el ground truth): error de parseo/esquema, `UNSAT`, `TIMEOUT`, o fallo de decodificación (vértice con 0 o ≥2 colores en el modelo del solver). `--feedback rich` añade un núcleo UNSAT (ablación).
- **Fallo anunciado** = lo detecta el propio pipeline sin conocer la respuesta (parse, esquema, UNSAT, timeout, decodificación; en C: JSON ilegible o vértices/colores inválidos). **Fallo silencioso** = respuesta bien formada que viola una arista (B: solver dice SAT).
- **Varianza**: `--runs` repeticiones con semillas distintas; IC de Wilson al 95 % y prueba exacta de McNemar para B vs B′.
- El ground truth / CNF de referencia se usa **solo en el análisis** (`taxonomy.py`), nunca en prompts.

Notas: SAT no tiene cuantificadores; el análogo de los errores de *scope/aridad* son los errores de índice/aridad (literal fuera de rango, `num_vars` incorrecto).
