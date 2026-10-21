**Tasa de optimalidad, 8-puzzle (profundidad óptima)** (óptimo y costo correcto; IC 95 % de Wilson)

| Sistema | 4 | 8 | 12 | 16 |
|---|---:|---:|---:|---:|
| A* clásico | 10/10 (72%–100%) | 10/10 (72%–100%) | 10/10 (72%–100%) | 10/10 (72%–100%) |
| LLM solo | 0/10 (0%–28%) | 0/10 (0%–28%) | 0/10 (0%–28%) | 0/10 (0%–28%) |
| LLM + herramienta A* | 6/10 (31%–83%) | 6/10 (31%–83%) | 6/10 (31%–83%) | 6/10 (31%–83%) |
| LLM + herramienta (v1, solo texto) | 0/10 (0%–28%) | 0/10 (0%–28%) | 0/10 (0%–28%) | 0/10 (0%–28%) |

**Tasa de optimalidad, Weighted grid (tamaño n×n)** (óptimo y costo correcto; IC 95 % de Wilson)

| Sistema | 5 | 8 | 12 | 16 |
|---|---:|---:|---:|---:|
| A* clásico | 10/10 (72%–100%) | 10/10 (72%–100%) | 10/10 (72%–100%) | 10/10 (72%–100%) |
| LLM solo | 0/10 (0%–28%) | 0/10 (0%–28%) | 0/10 (0%–28%) | 0/10 (0%–28%) |
| LLM + herramienta A* | 2/10 (6%–51%) | 2/10 (6%–51%) | 0/10 (0%–28%) | 0/10 (0%–28%) |
| LLM + herramienta (v1, solo texto) | 0/10 (0%–28%) | 0/10 (0%–28%) | 0/10 (0%–28%) | 0/10 (0%–28%) |

**Resultados por categoría (todas las instancias)**

| Sistema | Dominio | n | Óptimo y costo correcto | 1. Ilegal | 2. Legal subóptimo | 3. Óptimo, costo incorrecto | Sin respuesta legible | Timeout |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| A* clásico | 8puzzle | 40 | 40 | 0 | 0 | 0 | 0 | 0 |
| A* clásico | grid | 40 | 40 | 0 | 0 | 0 | 0 | 0 |
| LLM solo | 8puzzle | 40 | 0 | 29 | 0 | 0 | 11 | 0 |
| LLM solo | grid | 40 | 0 | 17 | 0 | 0 | 23 | 0 |
| LLM + herramienta A* | 8puzzle | 40 | 24 | 7 | 0 | 0 | 9 | 0 |
| LLM + herramienta A* | grid | 40 | 4 | 20 | 0 | 0 | 16 | 0 |
| LLM + herramienta (v1, solo texto) | 8puzzle | 40 | 0 | 40 | 0 | 0 | 0 | 0 |
| LLM + herramienta (v1, solo texto) | grid | 40 | 0 | 39 | 0 | 0 | 1 | 0 |

**Brazo con herramienta**

| Versión | Dominio | n | Llamó a A* | Argumentos rechazados | Respondió sin la herramienta | Óptimo y costo correcto |
|---|---|---:|---:|---:|---:|---:|
| LLM + herramienta (v1, solo texto) | 8puzzle | 40 | 0 | 0 | 40 | 0 |
| LLM + herramienta (v1, solo texto) | grid | 40 | 1 | 1 | 39 | 0 |
| LLM + herramienta A* | 8puzzle | 40 | 39 | 10 | 1 | 24 |
| LLM + herramienta A* | grid | 40 | 30 | 21 | 10 | 4 |

**Dónde falla el brazo con herramienta (v2)**

| Dominio | n | óptimo y costo correcto | A* respondió bien, pero el modelo copió mal la respuesta | A* rechazó los argumentos que escribió el modelo | no llamó a la herramienta | se trabó repitiendo texto (Ollama cortó la respuesta) | error del servidor / timeout |
|---|---:|---:|---:|---:|---:|---:|---:|
| 8puzzle | 40 | 24 | 5 | 10 | 0 | 1 | 0 |
| grid | 40 | 4 | 5 | 21 | 8 | 2 | 0 |

**Reproducibilidad** (`repro.csv`): instancia 8puzzle-8-01, temperatura 0.7, 5 llamadas idénticas salvo la semilla → **5 resultados distintos** (4 caminos distintos, más 1 sin respuesta).

| Llamada | Semilla | Resultado | Costo reportado | Costo real | Óptimo |
|---:|---:|---|---:|---:|---:|
| 1 | 1 | 1 camino ilegal | 3 | – | 8 |
| 2 | 2 | 1 camino ilegal | 3 | – | 8 |
| 3 | 3 | 1 camino ilegal | 12 | – | 8 |
| 4 | 4 | sin respuesta legible | – | – | 8 |
| 5 | 5 | 1 camino ilegal | 3 | – | 8 |

**Reproducibilidad** (`repro_t0.csv`): instancia 8puzzle-8-01, temperatura 0.0, 5 llamadas idénticas salvo la semilla → **1 resultado distinto** (1 camino distinto).

| Llamada | Semilla | Resultado | Costo reportado | Costo real | Óptimo |
|---:|---:|---|---:|---:|---:|
| 1 | 1 | 1 camino ilegal | 10 | – | 8 |
| 2 | 2 | 1 camino ilegal | 10 | – | 8 |
| 3 | 3 | 1 camino ilegal | 10 | – | 8 |
| 4 | 4 | 1 camino ilegal | 10 | – | 8 |
| 5 | 5 | 1 camino ilegal | 10 | – | 8 |

