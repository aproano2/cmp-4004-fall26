# HW2 — Dataset de 20 problemas CSP de Ingeniería Industrial (Integrante 1)

Dataset compartido por los cuatro brazos (A, B, B′, C). **Los cuatro brazos se evalúan sobre estos mismos 20 problemas.**

## Estructura y qué puede ver cada brazo

```
problems/
├── public/                     ← lo ÚNICO que puede ver un LLM (brazos B, B′, C)
│   ├── problems.json           id, título, área, dificultad, enunciado, formato de respuesta
│   └── problems.md             los mismos enunciados, para leer
├── ground_truth/               ← PRIVADO: nunca en un prompt
│   ├── ground_truth.json       FUENTE DE VERDAD: modelo CSP + solución + deducción
│   └── formulations.md         variables, dominios, restricciones, solución y cómo verificarla
├── difficulty_metrics.csv      métricas de dificultad por problema (sin respuestas)
└── README.md
code/
├── csp_spec.py                 formato del modelo + evaluador seguro + solver (MRV + forward checking)
├── export_problem_files.py     regenera public/, formulations.md y las métricas desde ground_truth.json
├── verify_ground_truth.py      verifica validez y unicidad → results/ground_truth_check.csv
├── results_schema.py           columnas comunes de results/arm_*.csv + regla de calificación (para TODOS los brazos)
└── arm_a.py                    brazo A: modelo manual → solver → results/arm_a.csv
results/
├── ground_truth_check.csv
└── arm_a.csv                   20/20 correctas
```

## Formato común de resultados (para los Integrantes 2 y 3)

`code/results_schema.py` define las columnas de `results/arm_*.csv` y la función `grade()`. Si B, B′ y C usan
`make_row()` + `write_results()`, el Integrante 3 puede concatenar los cuatro CSV sin transformarlos. Columnas:
`problem_id, difficulty, arm, outcome (correct/incorrect/no_answer), answer (JSON), solver_status, attempts,
wall_s, llm_s, solver_s, tokens_in, tokens_out, cost_usd, model, error_category, error_message, timestamp`.
Política acordada en `grade()`: si el solver da `multiple`, el brazo devuelve la primera solución y se califica;
`unsat`/`timeout`/`spec_error` cuentan como `no_answer`.

En el prompt envíen solo el campo `statement` (y `answer_format`, si el equipo lo decide). No envíen `difficulty`
ni `title`, para que el modelo no sepa el nivel del problema.

**Regla de oro (enunciado de la tarea):** el bucle de refinamiento B′ solo puede recibir el **mensaje de error del solver**,
nunca la solución. Ningún script de los brazos B/B′/C debe abrir `problems/ground_truth/`. Solo el evaluador
(Integrante 3) compara contra `ground_truth.json`.

## Los 20 problemas

| Nivel | IDs | Variables | Restricciones atómicas | Espacio de búsqueda |
|---|---|---|---|---|
| Fácil (7) | F01–F07 | 3–4 | 4–10 | 27 – 256 |
| Intermedio (7) | M08–M14 | 5–6 | 7–12 | 243 – 46 656 |
| Difícil (6) | D15–D20 | 7–9 | 9–23 | 6 561 – 2 097 152 |

Áreas: producción (F01, F04, M08, M14, D15, D16, D19), logística (F02, M10, D20), inventarios (F05, M13),
asignación de recursos (F06, M09), turnos (F07, M12, D17) y mantenimiento (F03, M11, D18).

La dificultad crece en tres ejes a la vez: número de variables, número de restricciones y **tipo** de restricción.
Los fáciles usan sobre todo restricciones unarias, de exclusión y todos-distintos. Los intermedios agregan conteos,
capacidad ponderada y precedencias. Los difíciles combinan capacidad ponderada, condicionales (`implies`),
no-solapamiento disyuntivo (D15) y cadenas de deducción largas, donde una decisión temprana solo se descarta varios
pasos después (por ejemplo, el caso P1 = L1 en D16 o L4 = 2 en D19). Las métricas exactas están en `difficulty_metrics.csv`,
y la columna `solver_nodes` sirve como medida empírica de dificultad para la gráfica de precisión vs. dificultad.

## Formato del modelo formal (lo que escribe A a mano y lo que debe producir el LLM en B)

El solver de la semana 6 (`studios/week-06/csp.py`) solo admite restricciones binarias de todos-distintos, y
`logic_lm.build_csp` solo `alldiff`/`neq`/`eq`. Eso no alcanza para capacidad, precedencia o condicionales, así que
usamos el mismo JSON pero con restricciones como **expresiones**:

```json
{"variables": {"C1": [1, 2, 3], "C2": [1, 2, 3], "C3": [1, 2, 3]},
 "constraints": [{"id": "R1", "expr": "alldiff(C1, C2, C3)"},
                 {"id": "R2", "expr": "C1 in [1, 3]"},
                 {"id": "R4", "expr": "abs(C3 - C1) == 1"}]}
```

Permitido en `expr`: nombres de variables, enteros y strings, `+ - * // %`, `== != < <= > >= in not in`,
`and or not`, listas, y las funciones `abs, min, max, alldiff(...), count(valor, ...), implies(a, b)`.
Capacidad ponderada: `(P1 == 'L1')*4 + (P2 == 'L1')*3 <= 8`. Cualquier otra cosa (atributos, imports, nombres
desconocidos) se rechaza con `SpecError` **antes** de evaluar, así que se puede ejecutar código escrito por el LLM.
Ese `SpecError` cae en la categoría "malformed syntax" de la taxonomía, y es el mensaje de error que puede recibir B′.

```python
from csp_spec import solve, SpecError
r = solve(spec)             # {'status': 'unique'|'multiple'|'unsat'|'timeout', 'solutions': [...], 'nodes', 'seconds'}
```

`status` se corresponde con la taxonomía: `unsat` → sobre-restringido; `multiple` → sub-restringido (detectable sin
ground truth); `timeout` → timeout. Ojo: `solve(spec)` se detiene por defecto al encontrar 2 soluciones, lo que basta
para distinguir única de múltiple; pasen `max_solutions=None` para enumerarlas todas.

## Decisión pendiente para el equipo: `answer_format`

`public/problems.json` incluye `answer_format`, con las claves de la respuesta (por ejemplo `OP1, OP2, OP3`) y sus
valores permitidos. Así la calificación es automática: B/B′ deben usar esos nombres de variables y C debe responder
un JSON con esas claves. **Si se muestra, el LLM ya recibe las variables y los dominios**, y en el brazo B solo le
queda traducir las restricciones. Decidan si se muestra y apliquen lo mismo en B y en C. Documéntenlo en la sección
*"Where we may have been unfair"*.

## Estado de verificación

- `python code/verify_ground_truth.py` comprueba, para los 20 problemas, que la solución guardada cumple todas las
  restricciones y que es la **única**. Lo hace con dos métodos: backtracking completo y fuerza bruta sobre todo el
  espacio. También comprueba que cada regla del enunciado tiene su restricción y que `public/` no tiene campos
  privados. Último resultado: **20/20** (`results/ground_truth_check.csv`).
- **Límite de esa verificación:** el solver confirma que el *modelo* tiene solución única, no que el modelo traduzca
  bien el enunciado. Esa parte es la **revisión manual**: en `formulations.md` cada problema trae la tabla regla →
  expresión, la sustitución de la solución en cada restricción y una deducción paso a paso.
  **Revisión manual completada:** los 20 problemas están marcados `OK` por Diego Changotasig, con notas por
  problema en `ground_truth.json` (y copiadas en `formulations.md`). Ningún modelo ni solución cambió tras la
  revisión.
- Si editan un problema: modifiquen `ground_truth.json` → `python code/export_problem_files.py` →
  `python code/verify_ground_truth.py`. No editen a mano los archivos de `public/` ni `formulations.md`.
