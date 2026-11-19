# Taxonomía de errores — brazos B y B′

**Ejecución completa:** 20 fallos de B. Cada caso figura abajo con un fragmento literal y la
salida completa en `results/arm_b_complete.jsonl` (registro con `arm` = `B`, campo
`attempt_log[0].text`). El historial de B′ y la caché guardan todos los intentos. Las
categorías principales son excluyentes según la primera señal; las causas pueden solaparse.

El estado del solver es una **señal**, no necesariamente una explicación causal: un modelo
`unsat` puede contener varios errores, `multiple` no prueba por sí solo que haya una premisa
omitida, y un modelo `unique` no demuestra que represente correctamente el enunciado. La
detectabilidad se refiere a la información disponible sin consultar la solución de referencia.

## F01 (ejemplo detallado)

- **B: sin respuesta; solver `unsat`.** Detectable sin ground truth: sí, el solver anuncia
  que el modelo generado no tiene solución. En la salida literal aparece la restricción
  `"expr": "OP1 + OP2 + OP3 == 3"`, aunque los dominios declarados para las tres variables
  contienen cadenas como `"CNC"`, `"TORNO"` y `"FRESADORA"`. También compara esas mismas
  variables con enteros (`"expr": "OP2 != 2"`), en lugar de traducir las restricciones
  sobre nombres de máquinas. El modelo no representa adecuadamente las reglas del enunciado;
  en particular, la suma de las cadenas nunca es igual al entero 3. El solver comunica
  `unsat`, no una explicación semántica de la mezcla de tipos.
- **B′: tres refinamientos, sin respuesta; último estado `spec_error`.** El primer intento es
  idéntico al de B. En los tres refinamientos la respuesta incluye texto explicativo y un
  bloque Markdown en vez de un objeto JSON puro, por lo que el parser rechaza la respuesta.
  Detectable sin ground truth: sí. El último mensaje del parser es
  `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`. La respuesta aún incluye la
  misma suma indebida dentro del bloque JSON: eliminar Markdown por sí solo no arreglaría
  el modelo.

## Clasificación por instancia

Los errores de conexión del archivo interrumpido no se incluyen en la ejecución completa.

- **F02 — incorrecto, `multiple`:** la primera asignación usa el mismo muelle para C2 y C3.
  El modelo omitió la exclusión entre todos los camiones; en la salida figura solo
  `"expr": "C1 != C3"` para esa distinción. Además, `"expr": "C1 != 1"` contradice
  la regla que permite los muelles 1 y 3 a C1. La multiplicidad es detectable sin ground
  truth, pero identificar estas omisiones requiere contrastar el modelo con el enunciado.
- **F03 — incorrecto, `multiple`:** el modelo solo incluye algunas desigualdades entre
  equipos; por ejemplo, `"expr": "COMPRESOR != CALDERA"`. También omite que el compresor vaya antes de
  la prensa y agrega `"expr": "abs(COMPRESOR - PRENSA) > 1"`. La multiplicidad es observable.
- **F04 — incorrecto, `unique`:** la salida incluye
  `"expr": "not (PINTURA == INSPECCION + 1)"`, que excluye que pintura siga
  inmediatamente a inspección. La regla prohíbe el orden inverso: inspección inmediatamente
  después de pintura. El solver devuelve una solución única, pero esta señal no identifica
  el modelo equivocado; se necesita contrastar con el enunciado.
- **F05 — sin respuesta, `spec_error`:** JSON inválido (`Expecting ',' delimiter`), detectable
  por el parser. También aparece `"expr": "ALIMENTO == C"`, con `C` sin comillas; si se
  reparara el JSON, el validador lo interpretaría como una variable desconocida.
- **F06 — sin respuesta, `spec_error`:** `"expr": "ELENA != LOTE2"` usa el nombre de
  una persona como variable, cuando es un valor del dominio. Detectable sin ground truth.
- **F07 — sin respuesta, `spec_error`:** el modelo usa `"expr": "sum(ANA, BRUNO, CARLA, DIEGO) >= 4"`,
  pero `sum` no pertenece a las funciones admitidas. Detectable sin ground truth.
- **M08 — incorrecto, `multiple`:** la salida no impide que todos los pares de pedidos
  compartan posición: por ejemplo, `"expr": "P4 < P5 or P5 < P4"` solo distingue P4
  de P5. El primer resultado asigna la posición 1 tanto a P2 como a P4. La multiplicidad
  es observable, pero el diagnóstico requiere comparar con las reglas del problema.
- **M09 — sin respuesta, sintaxis inválida:** `Unterminated string` y fin por `length`; el
  modelo repite reglas como `{"id": "R198", "expr": "ANA != 1"}` y se corta en medio de
  JSON. El parser detecta el fallo sin ground truth.
- **M10 — sin respuesta, sintaxis/especificación inválida:**
  `"expr": "all(C1, C2, C3, C4, C5) != []"` invoca `all`, que no está permitido.
  El validador lo detecta sin ground truth; además se comparan dominios de texto con números.
- **M11 — sin respuesta, `unsat`:** la salida contiene tanto
  `"expr": "COMPRESOR == SECADOR"` como
  `"expr": "alldiff([GENERADOR, TABLERO, COMPRESOR, SECADOR, HORNO])"`. El formato de
  este solver exige argumentos separados para `alldiff`, no una lista; además, exigir
  todos distintos sería incompatible con la igualdad. El estado `unsat` es observable,
  pero no revela por sí solo estos problemas de aridad y de restricciones.
- **M12 — sin respuesta, JSON inválido:** el parser informa `Expecting ',' delimiter`;
  la salida termina con `{"id": "R21", "expr": "abs(MARIA - 1) > 1"}}}`. Detectable sin
  ground truth; además repite restricciones, por ejemplo `abs(JORGE - SOFIA) > 1`.
- **M13 — sin respuesta, `unsat`:** se excluyen los tres valores de MOTOR en
  `"expr": "MOTOR != 1"`, `"expr": "MOTOR != 3"` y `"expr": "MOTOR != 2"`.
  El solver anuncia la insatisfacibilidad sin ground truth.
- **M14 — sin respuesta, JSON inválido:** el parser informa `Expecting ',' delimiter`;
  el texto termina `{"id": "R19", "expr": "ENSAMBLE != DESPACHO"}}]`. Detectable sin
  ground truth. Un JSON reparado no implica que las restricciones sean correctas.
- **D15 — sin respuesta, JSON inválido:** el parser informa `Expecting ',' delimiter`;
  el texto termina `{"id": "R17", "expr": "C2 + 2 <= 8"}}}`. Detectable sin ground truth.
- **D16 — sin respuesta, `unsat`:** `"expr": "P2 + P5 == 1"` es imposible cuando cada
  dominio es `[1, 2, 3]`: la suma mínima es 2. El solver detecta insatisfacibilidad.
- **D17 — sin respuesta, JSON inválido:** `Invalid control character`, con fin `length`.
  La salida también contiene `"expr": "FABIOLA != FABIOLA"`, que sería contradictorio.
  El parser detecta el primer fallo sin ground truth.
- **D18 — sin respuesta, JSON inválido:** `Unterminated string`, con fin `length`; se repiten
  reglas como `"expr": "TORNO1 != TORNO2"` hasta el corte. Detectable sin ground truth.
- **D19 — sin respuesta, `unsat`:** `"expr": "L1 + L2 + L3 + L4 + L5 + L6 + L7 + L8 + L9 == 30"`
  excede la suma máxima de 27 de los nueve dominios `[1, 2, 3]`. También incluye
  `"expr": "L4 != L8"` y `"expr": "L8 == L4"`. El solver anuncia `unsat`.
- **D20 — incorrecto, `multiple`:** la primera solución asigna ventana 2 a cinco camiones,
  pese al máximo de dos. El modelo omite la capacidad y contiene
  `"expr": "T8 == 1 or T2 == 2"`, que no representa la implicación indicada. La
  multiplicidad es observable; el diagnóstico de reglas omitidas exige leer el enunciado.

## Conteo por primera señal de B

| Categoría principal | Casos | IDs |
|---|---:|---|
| JSON o especificación inválida | 10 | F05, F06, F07, M09, M10, M12, M14, D15, D17, D18 |
| `unsat` | 5 | F01, M11, M13, D16, D19 |
| `multiple` y respuesta incorrecta | 4 | F02, F03, M08, D20 |
| `unique` pero modelo equivocado | 1 | F04 |
| Timeout del solver | 0 | — |

De 20 fallos, 15 se anuncian como error/`unsat`; otros cuatro producen la alerta
`multiple`, aunque la multiplicidad por sí sola no demuestra un error. F04 es silencioso.
Los errores de alcance/uso de funciones también aparecen en otras categorías; no se suman
otra vez. El solver trata algunos errores de tipo durante la evaluación como restricción
falsa; por eso no todo `unsat` debe interpretarse como sobre-restricción semántica pura.

---

# Fallos del brazo C (LLM directo) y su detectabilidad

**Ejecución principal:** `qwen2.5:3b`, T=0, semilla 0 (`results/arm_c_raw.jsonl`, campo `text`).
C acierta 3/20 (F05, F07, M14) y falla 17, todos con una respuesta en formato válido: no hubo
ningún `no_answer`. Sin ground truth, la única verificación posible en C es comparar la respuesta
con el `answer_format` público (claves completas y valores permitidos). El análisis posterior,
que sí usa el ground truth, está en `results/c_failure_analysis.csv`: cuántas variables acertó y
cuántas restricciones del modelo manual viola cada respuesta.

| Señal sin ground truth | Casos | IDs |
|---|---:|---|
| Valor fuera del dominio permitido (`format_errors`) | 2 | D15, D18 |
| Ninguna: JSON válido, claves completas, valores permitidos | 15 | F01, F02, F03, F04, F06, M08, M09, M10, M11, M12, M13, D16, D17, D19, D20 |

**Detectables sin ground truth: 2/17 (12 %). Silenciosos: 15/17 (88 %).** En B fueron 15/20
anunciados por el parser o el solver, 4 con alerta `multiple` y 1 silencioso (F04).

## Ejemplos literales (salida completa de C)

1. **F01, eco del dominio:** `{"OP1": "CNC", "OP2": "TORNO", "OP3": "FRESADORA"}`. Copia en orden
   los valores de `allowed_values`. Viola R2 (OP2 no puede ir al torno) y R4 (OP3 no puede ir a la
   fresadora): 0/3 variables. Nada en la respuesta lo delata.
2. **F02, eco de posiciones:** `{"C1": 1, "C2": 2, "C3": 3}`. Asigna 1, 2, 3 en orden y viola la
   regla de adyacencia R4. Lo mismo pasa en F04 (`1, 2, 3, 4`) y en M14 (`1…6`). **M14 es
   "correcto" porque su solución coincide con el orden identidad**: es un acierto por coincidencia,
   no por razonamiento. Contarlo como acierto infla la precisión de C.
3. **M11, contradicción interna invisible:** `{"GENERADOR": 2, "TABLERO": 3, "COMPRESOR": 1,
   "SECADOR": 1, "HORNO": 2}`. Viola R5 y acierta 1/5 variables. Sin un modelo formal no hay nada
   contra qué comprobarlo.
4. **D18, el único tipo de error que se anuncia:** `{"TORNO1": 2, "TORNO2": 4, "FRESA1": 5,
   "FRESA2": 3, "PRENSA": 6, "COMPRESOR": 7, "GRUA": 8}`. Continúa la secuencia 6, 7, 8 fuera del
   dominio permitido, y por eso `format_errors` lo detecta. D15 (`"C2": 8`) es igual.
5. **D17, completamente equivocado y con aspecto plausible:** ocho turnos asignados con valores
   válidos, 0/8 variables correctas y 6 restricciones violadas. Un usuario no podría distinguirlo
   de una respuesta correcta.

## Patrón cualitativo

- **Eco del orden:** 4 de 20 respuestas reproducen el orden de los valores permitidos o la
  secuencia 1…n (F01, F02, F04, M14). El modelo no resuelve el problema; rellena el esqueleto.
- **Errores "cerca":** las respuestas incorrectas violan una mediana de 2 restricciones del modelo
  manual (entre 1 y 6), y en M09 acierta 5/6 variables. Son errores pequeños y plausibles, que
  justamente por eso resultan peligrosos al ser silenciosos.
- **Con más dificultad no aparecen más señales**, salvo los valores fuera de rango en D15 y D18.
