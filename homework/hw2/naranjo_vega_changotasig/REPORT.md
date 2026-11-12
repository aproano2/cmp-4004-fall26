# Homework 2 — The Formalizer

**CMP-4004 · Inteligencia Artificial · USFQ**
**Equipo:** Diego Changotasig (Integrante 1: dataset, ground truth y brazo A) · [Integrante 2: brazos B y B′] ·
[Integrante 3: brazo C, evaluación y análisis]
**Formalismo:** Constraint Satisfaction Problems (CSP)
**Modelo LLM usado en B, B′ y C:** **[PENDIENTE: nombre exacto, tamaño (n.º de parámetros), proveedor o local,
temperatura]**. Este dato condiciona todos los resultados y debe ir aquí.
**Estado:** borrador. Secciones de los integrantes 2 y 3 pendientes · límite: 2 500 palabras.

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

**Protocolo común.** Todos los brazos usan el mismo solver (`code/csp_spec.py`), el mismo formato de resultados
y la misma regla de calificación (`code/results_schema.py`). Por cada instancia se registra:

- resultado: correcto / incorrecto / sin respuesta;
- tiempo total, tiempo del LLM y tiempo del solver;
- tokens;
- costo.

Si el solver encuentra varias soluciones, el brazo devuelve la primera y se califica. Si no hay solución, se
agota el tiempo o el modelo es inválido, cuenta como sin respuesta. Los LLM reciben solo `statement` de
`problems/public/problems.json`; nunca la dificultad ni el ground truth.
**[PENDIENTE — equipo: (a) si se muestra `answer_format` (variables y dominios) al LLM, igual en B y C;
(b) temperatura y número de repeticiones por instancia para medir la varianza; (c) los prompts exactos,
en `code/`.]**

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
| Correctas / 20 | **20/20** | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| Incorrectas / sin respuesta | 0 / 0 | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| Tiempo total por instancia, mediana (IQR) | 0,47 ms (0,25–0,67) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| Tiempo del solver, mediana (IQR) | 0,08 ms (0,06–0,20) | [PENDIENTE] | [PENDIENTE] | — |
| Tiempo del LLM | — | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| Tokens por instancia, mediana (IQR) | 0 | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| Fallos detectables sin ground truth | — (sin fallos) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| Costo por respuesta correcta | 0 USD (+ tiempo humano, §6) | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |

Los tiempos de A son la mediana de 5 ejecuciones por problema (`results/arm_a.csv`; `python code/arm_a.py`).
**A obtiene 20/20 por construcción**, porque su modelo es el mismo que produce el ground truth. Ese número solo
tiene valor gracias a la revisión manual de la §1. Si B supera a A en algún problema, primero hay que sospechar
del modelo manual (ver `hw2.md`).

**Interpretación:** [PENDIENTE — Integrante 3.]

## 3. Precisión vs. dificultad

[PENDIENTE — Integrante 3.] Precisión de cada brazo por nivel, sobre los mismos 20 problemas.

- `fig/accuracy_vs_difficulty.png`: precisión de los cuatro brazos por nivel (figura obligatoria).
- `fig/latency_by_arm.png`: tiempo total por brazo, separando el tiempo del LLM y el del solver.
- `fig/errors_by_category.png`: fallos de B por categoría de la taxonomía.

No se incluirá ninguna figura sin datos medidos.

## 4. Taxonomía de errores

[PENDIENTE — Integrante 3, con datos de B.] Se clasifican **todos** los fallos de B. El detalle de cada uno, con
la salida del modelo, va en `taxonomy.md`. La columna de detección se llena con *nuestros* datos, no solo con
la expectativa de `hw2.md`.

| Categoría (fallo de B) | Señal en nuestro sistema | ¿Detectable sin ground truth? | Casos |
|---|---|---|---:|
| Sintaxis inválida | `SpecError` / JSON que no se puede leer | Sí — el solver lo rechaza | [ ] |
| Sintaxis válida, sobre-restringido | `solver_status = unsat` | Sí — el solver lo reporta | [ ] |
| Sintaxis válida, sub-restringido | `solver_status = multiple` | A veces: se detecta si se pide más de una solución, como hace nuestro solver | [ ] |
| Modelo válido del *problema equivocado* (premisas inventadas u omitidas) | `unique`, pero con respuesta incorrecta | No | [ ] |
| Error de aridad o alcance (`count` o `alldiff` sobre las variables equivocadas) | variable o valor fuera del dominio, o como en el problema equivocado | A veces | [ ] |
| Timeout | `solver_status = timeout` | Sí | [ ] |

**Cinco salidas literales del modelo:** [PENDIENTE: al menos 5, con problema, brazo, intento, categoría y qué
salió mal. Copiarlas tal cual de `.llm_cache/`, sin parafrasear.]

**Comparación con C:** [PENDIENTE: de las respuestas incorrectas de C, ¿cuántas eran detectables sin ground
truth? Contrastar con B y explicar la consecuencia de ingeniería: una arquitectura cuyos fallos se anuncian
solos se puede desplegar; una cuyos fallos son silenciosos, no.]

## 5. Análisis del refinamiento (B′)

[PENDIENTE — Integrantes 2 y 3.] B′ recibe solo el error del solver, nunca el ground truth.

| Iteraciones hasta acertar | Casos |
|---|---:|
| Correcto en el primer intento (igual que B) | [ ] |
| Corregido tras 1 refinamiento | [ ] |
| Corregido tras 2 refinamientos | [ ] |
| Corregido tras 3 refinamientos | [ ] |
| Nunca converge (sigue fallando tras 3) | [ ] (fracción: [ ]) |

**Discusión:** [PENDIENTE: ¿los fallos que sobreviven 3 rondas son cualitativamente distintos de los que se
corrigen en 1? Hipótesis a contrastar: los errores con señal del solver (sintaxis, `unsat`, `multiple`) se
reparan; los modelos del problema equivocado devuelven `unique`, así que B′ ni siquiera intenta repararlos.]

## 6. Costo por respuesta correcta

[PENDIENTE — Integrante 3.]

**Costo por respuesta correcta = costo total del brazo / número de respuestas correctas.**

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
```

| Entregable | Estado |
|---|---|
| `problems/` (20 problemas, ground truth revisado, `README.md`) | Listo |
| `code/csp_spec.py`, `export_problem_files.py`, `verify_ground_truth.py` | Listo |
| `code/results_schema.py` (formato común y calificación), `code/arm_a.py` | Listo |
| `results/ground_truth_check.csv`, `results/arm_a.csv` | Listo |
| `code/arm_b.py`, `code/refinement.py`, `.llm_cache/`, `results/arm_b*.csv` | [PENDIENTE — Integrante 2] |
| `code/arm_c.py`, `code/evaluation.py`, `results/arm_c.csv`, `fig/*.png` (≥ 3), `taxonomy.md` | [PENDIENTE — Integrante 3] |
| `AI_LOG.md` | Integrante 1 listo (faltan sus campos «¿Lo entendí?»); integrantes 2 y 3 pendientes |
