# Homework 2 — The Formalizer

**CMP-4004 · Inteligencia Artificial · USFQ**
**Equipo:** Diego Changotasig (Integrante 1: dataset, ground truth y brazo A) · [Integrante 2: brazos B y B′] ·
[Integrante 3: brazo C, evaluación y análisis]
**Formalismo:** Constraint Satisfaction Problems (CSP)
**Modelo previsto para B, B′ y C:** Ollama local `qwen2.5:3b` (3,1 mil millones de parámetros,
Q4_K_M), temperatura 0 y semilla 0. Confirmar la misma versión y configuración en el equipo de C.
**Estado:** borrador con resultados de B y B′; C y análisis conjunto pendientes · límite: 2 500 palabras.

## 0. Objetivo y protocolo experimental

El objetivo es comparar dos formas de resolver problemas escritos en lenguaje natural: que el LLM responda
directamente, o que traduzca el problema a un modelo CSP para que lo resuelva un solver. Se comparan cuatro
brazos sobre **los mismos 20 problemas**:

| Brazo | Procedimiento |
|---|---|
| **A — Manual + solver** | Modelo CSP escrito y revisado a mano → solver. |
| **B — LLM → CSP → solver** | El LLM escribe el modelo desde el enunciado → solver. Un intento. |
| **B′ — B + refinamiento** | Si el solver falla, el LLM recibe **solo el mensaje de error del solver** y reintenta, hasta 3 veces. |
| **C — LLM directo** | El LLM responde sin solver. |

**Protocolo común.** A, B y B′ usan el mismo solver (`code/csp_spec.py`); C no usa solver.
Todos usan el mismo formato de resultados y regla de calificación (`code/results_schema.py`). Por cada instancia se registra:

- resultado: correcto / incorrecto / sin respuesta;
- tiempo total, tiempo del LLM y tiempo del solver;
- tokens;
- costo.

Si el solver encuentra varias soluciones, el brazo devuelve la primera y se califica. Si no hay solución, se
agota el tiempo o el modelo es inválido, cuenta como sin respuesta. Los LLM reciben `statement` y
`answer_format` de `problems/public/problems.json`; nunca la dificultad ni el ground truth.
Se muestra `answer_format` a B y C, con variables y dominios: esto simplifica la traducción y debe
considerarse en §7. Protocolo inicial: temperatura 0, semilla 0, una ejecución por instancia; la
variación entre instancias no mide varianza entre generaciones. Si hay tiempo, ejecutar semillas
adicionales con temperatura mayor y reportarlas por separado. El prompt de B está en `code/arm_b.py`;
C debe guardar su propio prompt y usar el mismo modelo, configuración y presupuesto de salida (4096 tokens).
Ollama puede ejecutarse en equipos distintos; registrar hardware y versión para interpretar tiempos.

Para B′ se parte de la salida inicial de B y solo se reintenta tras error de JSON/especificación o
`unsat`, hasta tres refinamientos. `multiple` devuelve la primera solución, igual que A, sin reintento;
es una alerta, no una prueba por sí sola de que la traducción es incorrecta. Timeout se registra sin
reintento. Los modelos válidos pero incorrectos pueden pasar sin señal del solver.

## 1. Dataset, formalización y ground truth (Integrante 1)

El dataset tiene **20 problemas de Ingeniería Industrial**: **7 fáciles (F01–F07), 7 intermedios (M08–M14) y
6 difíciles (D15–D20)**. Cubren producción, logística, inventarios, mantenimiento, asignación de recursos y
turnos. Los enunciados, los modelos CSP y el solucionador se generaron con asistencia de IA (Claude) y los
revisé manualmente uno por uno (detalle en `AI_LOG.md`).

Cada problema es un CSP con variables discretas, dominios finitos y restricciones explícitas: `alldiff`,
precedencias, igualdades y desigualdades, adyacencia, capacidades ponderadas, conteos e implicaciones. La
dificultad crece en tres ejes a la vez: número de variables, número y tipo de restricciones, y longitud de la
cadena de deducción.

| Dificultad | Variables | Restricciones atómicas | Espacio de búsqueda | Mediana de nodos (backtracking) |
|---|---:|---:|---:|---:|
| Fácil | 3–4 | 4–10 | 27–256 | 5 |
| Intermedia | 5–6 | 7–12 | 243–46 656 | 7 |
| Difícil | 7–9 | 9–23 | 6 561–2 097 152 | 42 |

Los nodos explorados no crecen siempre con el espacio de búsqueda. D15 tiene 2 097 152 combinaciones, pero el
backtracking demuestra la unicidad en 10 nodos porque sus restricciones podan mucho. Las métricas por problema
están en `problems/difficulty_metrics.csv`.

El solucionador (`code/csp_spec.py`) usa backtracking con selección **MRV** (desempate por grado),
**consistencia de nodo** y un **forward checking limitado** a las restricciones a las que les falta una sola
variable. **No** aplica AC-3. El modelo es un JSON de expresiones que se validan antes de ejecutarse, lo que
permite correr modelos escritos por el LLM.

**Verificación.** `code/verify_ground_truth.py` comprueba que cada solución guardada cumple todas las
restricciones y que es **única** según dos métodos independientes, backtracking completo y fuerza bruta.
También comprueba que cada regla del enunciado esté codificada y que los archivos públicos no incluyan datos
privados. Resultado: **20/20** (`results/ground_truth_check.csv`).

**Revisión manual.** La verificación automática solo prueba la corrección respecto de las restricciones
*codificadas*. Por eso revisé a mano los 20 problemas: comparé cada regla con su expresión y seguí cada
deducción. Registré `manual_review: "OK"` y mis notas en `ground_truth.json`. Por ejemplo:

- En **M10** comprobé que las cargas respetan las capacidades (V1 8/10, V2 6/8, V3 6/6 t).
- En **D16** comprobé que se cumplen a la vez las capacidades (8/8, 8/8, 6/6 h), los pedidos agrupados y la
  condición lógica.

La revisión no encontró errores, así que ningún modelo ni ninguna solución cambió.

## 2. Duel Scorecard

| Métrica | A: manual + solver | B: LLM + solver | B′: refinamiento | C: LLM directo |
|---|---|---|---|---|
| Correctas / 20 | **20/20** | **0/20** | **0/20** | [PENDIENTE] |
| Incorrectas / sin respuesta | 0 / 0 | 5 / 15 | 5 / 15 | [PENDIENTE] |
| Tiempo por instancia, mediana (Q1–Q3) | 0,47 ms (0,25–0,67) | 32,42 s (22,90–50,04) | 162,58 s (68,02–239,27) | [PENDIENTE] |
| Tiempo del solver, mediana (Q1–Q3) | 0,08 ms (0,06–0,20) | 0,35 ms (0,16–0,59) | 0,35 ms (0,25–0,63) | — |
| Tiempo del LLM, mediana | — | 32,42 s | 162,58 s | [PENDIENTE] |
| Tokens totales por instancia, mediana (Q1–Q3) | 0 | 912,5 (765,5–1183,75) | 6556,5 (3452,75–8663,25) | [PENDIENTE] |
| Fallos detectables sin ground truth | — (sin fallos) | 15 errores; 4 alertas de multiplicidad (§4) | 15 errores; 4 alertas de multiplicidad | [PENDIENTE] |
| Costo por respuesta correcta | 0 USD (+ tiempo humano, §6) | No definido (0 correctas) | No definido (0 correctas) | [PENDIENTE] |

Los tiempos de A son la mediana de 5 ejecuciones por problema (`results/arm_a.csv`; `python code/arm_a.py`).
**A obtiene 20/20 por construcción**, porque su modelo es el mismo que produce el ground truth. Ese número solo
tiene valor gracias a la revisión manual de la §1. Si B supera a A en algún problema, primero hay que sospechar
del modelo manual (ver `hw2.md`).

B/B′: `results/arm_b_complete.jsonl`, `results/arm_b.csv` y `results/arm_b_refined.csv`.
Cuartiles calculados por interpolación inclusiva. La medida del solver incluye validación y
parseo; en A el tiempo de solver solo mide búsqueda, de modo que no son estrictamente iguales.
El tiempo de B/B′ suma los tiempos originales por intento, no incluye carga inicial ni escritura
de resultados, y al reutilizar caché conserva la latencia original. Parte de la ejecución original
se interrumpió; se conservaron las respuestas válidas y se reintentaron fallos de infraestructura
con 600 s de timeout (originalmente 300 s). No se cuentan los intentos fallidos de infraestructura
en la latencia de la ejecución final; el archivo interrumpido se conserva para transparencia.

**Interpretación:** [PENDIENTE — Integrante 3.]

## 3. Precisión vs. dificultad

[PENDIENTE — Integrante 3.] B y B′: 0/7 fácil, 0/7 intermedio, 0/6 difícil. Completar A y C
y graficar la precisión de cada brazo por nivel sobre los mismos 20 problemas.

- `fig/accuracy_vs_difficulty.png`: precisión de los cuatro brazos por nivel (figura obligatoria).
- `fig/latency_by_arm.png`: tiempo total por brazo, separando el tiempo del LLM y el del solver.
- `fig/errors_by_category.png`: fallos de B por categoría de la taxonomía.

No se incluirá ninguna figura sin datos medidos.

## 4. Taxonomía de errores

Se clasifican **todos** los fallos de B. El detalle de cada uno, con
la salida del modelo, va en `taxonomy.md`. La columna de detección se llena con *nuestros* datos, no solo con
la expectativa de `hw2.md`.

| Categoría (fallo de B) | Señal en nuestro sistema | ¿Detectable sin ground truth? | Casos |
|---|---|---|---:|
| Sintaxis o especificación inválida | `SpecError` / JSON que no se puede leer | Sí | 10 |
| Modelo declarado insatisfacible | `solver_status = unsat` | Sí | 5 |
| Múltiples soluciones y respuesta incorrecta | `solver_status = multiple` | Señal observable; no prueba por sí sola un fallo | 4 |
| Modelo único del problema equivocado | `unique`, pero respuesta incorrecta | No por señal del solver | 1 |
| Error de aridad o alcance | Puede aparecer en otras categorías | A veces; solapado, no sumar | Ver `taxonomy.md` |
| Timeout del solver | `solver_status = timeout` | Sí | 0 |

**Ejemplos literales de B, primer intento** (salidas completas en JSONL):

1. F01 (`unsat`): `"expr": "OP1 + OP2 + OP3 == 3"` suma cadenas de máquinas y las compara con un número.
2. F04 (`unique` incorrecto): `"expr": "not (PINTURA == INSPECCION + 1)"` invierte la precedencia prohibida.
3. F06 (`spec_error`): `"expr": "ELENA != LOTE2"` usa un valor como si fuera una variable.
4. M13 (`unsat`): `"expr": "MOTOR != 1"`, `"expr": "MOTOR != 2"` y `"expr": "MOTOR != 3"` eliminan todo el dominio.
5. D16 (`unsat`): `"expr": "P2 + P5 == 1"` es imposible cuando ambos valores son como mínimo 1.

En F01 y M11, el evaluador de expresiones puede convertir errores de tipo en restricciones falsas;
la señal `unsat` no demuestra por sí sola una sobre-restricción semántica. F04 muestra una
respuesta incorrecta sin alerta de sintaxis ni multiplicidad. Los cuatro `multiple` son alertas
observables, no diagnósticos automáticos de incorrección.

**Comparación con C:** [PENDIENTE: de las respuestas incorrectas de C, ¿cuántas eran detectables sin ground
truth? Contrastar con B y explicar la consecuencia de ingeniería: una arquitectura cuyos fallos se anuncian
solos se puede desplegar; una cuyos fallos son silenciosos, no.]

## 5. Análisis del refinamiento (B′)

B′ recibe solo el error del solver, nunca el ground truth.

| Iteraciones hasta acertar | Casos |
|---|---:|
| Correcto en el primer intento (igual que B) | 0 |
| Corregido tras 1 refinamiento | 0 |
| Corregido tras 2 refinamientos | 0 |
| Corregido tras 3 refinamientos | 0 |
| No alcanzó respuesta correcta | 20/20 (100 %) |

**Discusión:** 15 casos recibieron tres refinamientos y terminaron con `spec_error`; cinco no
fueron refinados (cuatro `multiple`, un `unique`) por el protocolo. Por tanto no se puede afirmar
que los 20 hayan agotado tres rondas. Ninguno se corrigió en una ronda, así que no hay grupo de
éxitos rápidos con el cual comparar cualitativamente. En F01, por ejemplo, tras `unsat` las
respuestas de reparación añadieron prosa y Markdown, rechazados por el parser; el CSP interno
seguía conteniendo la suma inválida. La mejora de precisión B′ − B fue **0 puntos porcentuales**.

## 6. Costo por respuesta correcta

[PENDIENTE — Integrante 3.]

**Costo por respuesta correcta = costo total del brazo / número de respuestas correctas.**

En esta ejecución el denominador es cero en B y B′, por lo que el costo y el tiempo por
respuesta correcta **no están definidos**. No son 0 USD. B consumió 12 114 tokens de entrada,
18 067 de salida y 1751,32 s medidos; B′ consumió 75 634 de entrada, 43 766 de salida y
4031,75 s. Las cifras B′ incluyen el primer intento compartido con B: son costos hipotéticos
de cada brazo por separado, no deben sumarse como si se hubieran ejecutado independientemente.
La tarifa equivalente del proveedor, su fuente y fecha quedan pendientes; los CSV dejan el
costo vacío hasta proporcionarla.

Se cuenta el costo de todos los intentos, incluidos los fallidos y las iteraciones de B′. El costo se calcula
como tokens × precio. Si el modelo es local, se usa el precio por token equivalente de un proveedor alojado
(Groq o Together AI), como pide la tarea, indicando la tarifa y la fecha. Además se reportan los segundos por
respuesta correcta.

Para **A**, el costo de cómputo es 0 USD y unos milisegundos, pero escribir y revisar los 20 modelos a mano
tuvo un costo humano fijo de **2 Horas**.

## 7. Dónde pudimos ser injustos

- **A tiene ventaja estructural.** Su modelo ya está hecho y revisado, mientras que B tiene que inferirlo, así
  que la comparación mide también el costo de formular el problema. Además, A saca 100 % por construcción
  (§2) y no se le carga el tiempo humano (§6).
- **El dataset lo generó un LLM.** Claude escribió los enunciados y los modelos, y una sola persona del equipo
  los revisó a mano. Si B o C usan un modelo de la misma familia, la redacción podría favorecerlo.
- **Los problemas están ajustados para tener una sola solución.** Se agregaron reglas hasta que el solver
  encontrara una única solución. Esto puede producir reglas algo artificiales y favorece a los brazos con
  solver frente a enunciados reales, que suelen ser ambiguos.
- **El formato de expresiones es nuestro.** El LLM de B debe aprender un formato que no conoce de su
  entrenamiento. Parte de los errores de sintaxis pueden deberse al formato y no a la capacidad de formalizar.
- **`answer_format`.** Si se da al LLM, recibe las variables y los dominios, y a B solo le queda traducir las
  restricciones. [PENDIENTE: decisión tomada.]
- [PENDIENTE — equipo: sesgos observados al ejecutar B, B′ y C, como el presupuesto de tokens, la temperatura y
  la cantidad de repeticiones.]

## 8. Recomendación de despliegue y monitoreo

[PENDIENTE — equipo, con los números de §2–§6.] ¿Qué brazo pondríamos en producción en una planta real y con
qué monitoreo? Se debe defender con nuestras cifras de precisión, de fallos detectables sin ground truth, de
latencia y de costo por respuesta correcta. Monitoreo mínimo a considerar:

- alertas cuando el solver devuelve `unsat`, `multiple`, `timeout` o un error de sintaxis;
- revisión humana de esos casos;
- muestreo periódico de respuestas `unique` para detectar modelos del problema equivocado, que no dan señal.

## 9. Reproducibilidad y entregables

```bash
python code/export_problem_files.py   # regenera problems/public/, formulations.md, difficulty_metrics.csv
python code/verify_ground_truth.py    # 20/20 → results/ground_truth_check.csv
python code/arm_a.py                  # brazo A, 20/20 → results/arm_a.csv
python code/arm_b.py --timeout 600 --out results/arm_b_new.jsonl  # no sobrescribe resultados
python code/evaluate_b.py results/arm_b_new.jsonl --out-dir results/new_evaluation
```

| Entregable | Estado |
|---|---|
| `problems/` (20 problemas, ground truth revisado, `README.md`) | Listo |
| `code/csp_spec.py`, `export_problem_files.py`, `verify_ground_truth.py` | Listo |
| `code/results_schema.py` (formato común y calificación), `code/arm_a.py` | Listo |
| `results/ground_truth_check.csv`, `results/arm_a.csv` | Listo |
| `code/arm_b.py`, `code/evaluate_b.py`, `.llm_cache/`, `results/arm_b*.csv` | Ejecución y análisis de B/B′ completos; confirmar inclusión de la caché en la entrega |
| `code/arm_c.py`, `code/evaluation.py`, `results/arm_c.csv`, `fig/*.png` (≥ 3), `taxonomy.md` | [PENDIENTE — Integrante 3] |
| `AI_LOG.md` | Integrante 1 listo (faltan sus campos «¿Lo entendí?»); integrantes 2 y 3 pendientes |
