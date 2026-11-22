# HW2 — Formulaciones CSP y ground truth (PRIVADO)

> **No enviar a ningún LLM.** Contiene modelos y soluciones. Generado por `code/export_problem_files.py` desde `ground_truth.json`.

Formato de las restricciones: expresiones del DSL de `code/csp_spec.py` (`alldiff`, `count(valor, ...)`, `implies(a, b)`, `abs`, comparaciones, `and/or/not`). En las expresiones de capacidad, `(X == 'L1')*4` vale 4 si X = L1 y 0 en caso contrario.

## F01 — Asignación de órdenes a máquinas

**Área:** Producción · **Dificultad:** Fácil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Un taller metalmecánico debe procesar hoy tres órdenes de producción: OP1 (un eje de acero), OP2 (una brida de aluminio con ranuras) y OP3 (una carcasa de polímero). Dispone de tres máquinas: un centro CNC, un torno y una fresadora. Cada orden se procesa completa en una sola máquina.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `OP1` | {CNC, TORNO, FRESADORA} | máquina asignada a la orden OP1 |
| `OP2` | {CNC, TORNO, FRESADORA} | máquina asignada a la orden OP2 |
| `OP3` | {CNC, TORNO, FRESADORA} | máquina asignada a la orden OP3 |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1 | Cada máquina procesa exactamente una orden y cada orden va a exactamente una máquina. | `alldiff(OP1, OP2, OP3)` |
| R2 | El torno no puede hacer ranuras, por lo que la OP2 no puede asignarse al torno. | `OP2 != 'TORNO'` |
| R3 | El torno está calibrado solo para metales, por lo que la OP3 no puede asignarse al torno. | `OP3 != 'TORNO'` |
| R4 | La sujeción de la fresadora no es compatible con la carcasa de polímero, por lo que la OP3 no puede asignarse a la fresadora. | `OP3 != 'FRESADORA'` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `OP1` | **TORNO** |
| `OP2` | **FRESADORA** |
| `OP3` | **CNC** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1 | `alldiff('TORNO', 'FRESADORA', 'CNC')` | ✓ |
| R2 | `'FRESADORA' != 'TORNO'` | ✓ |
| R3 | `'CNC' != 'TORNO'` | ✓ |
| R4 | `'CNC' != 'FRESADORA'` | ✓ |

**2. Unicidad — deducción manual:**

Por R2 y R3, ni OP2 ni OP3 pueden ir al torno, así que el torno queda para OP1. Por R4, OP3 tampoco va a la fresadora, así que OP3 = CNC. Por R1, OP2 = FRESADORA.

**Notas de la revisión manual (Diego Changotasig):** Revisé que cada orden se asigne a una máquina distinta y que las restricciones del torno y la fresadora coincidan con las incompatibilidades indicadas en el enunciado.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

3 variables, dominios de tamaño 3 (espacio de búsqueda de 27 asignaciones), 4 reglas en lenguaje natural que se traducen en 4 restricciones atómicas, aridad máxima 3. Tipos de restricción: todos-distintos, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 4 nodos para enumerarlas todas.

---

## F02 — Asignación de muelles de carga

**Área:** Logística · **Dificultad:** Fácil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Un centro de distribución recibe a la misma hora tres camiones: C1 (refrigerado), C2 (carga a granel) y C3 (paquetería). Hay tres muelles numerados 1, 2 y 3, ubicados uno junto al otro en ese orden, de modo que los muelles 1 y 2 son vecinos, y los muelles 2 y 3 también.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `C1` | {1, 2, 3} | muelle del camión C1 |
| `C2` | {1, 2, 3} | muelle del camión C2 |
| `C3` | {1, 2, 3} | muelle del camión C3 |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1 | Cada muelle atiende exactamente a un camión. | `alldiff(C1, C2, C3)` |
| R2 | Solo los muelles 1 y 3 tienen conexión eléctrica para equipos de frío, y el camión refrigerado C1 la necesita. | `C1 in [1, 3]` |
| R3 | El camión de granel C2 necesita la rampa niveladora, que no existe en el muelle 3. | `C2 != 3` |
| R4 | C3 debe quedar en un muelle vecino al de C1, porque ambos comparten el mismo montacargas. | `abs(C3 - C1) == 1` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `C1` | **3** |
| `C2` | **1** |
| `C3` | **2** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1 | `alldiff(3, 1, 2)` | ✓ |
| R2 | `3 in [1, 3]` | ✓ |
| R3 | `1 != 3` | ✓ |
| R4 | `abs(2 - 3) == 1` | ✓ |

**2. Unicidad — deducción manual:**

Por R2, C1 ∈ {1, 3}. Si C1 = 1, por R4 C3 = 2 y entonces C2 = 3, lo que viola R3. Por tanto C1 = 3, C3 = 2 (R4) y C2 = 1 (R1), que cumple R3.

**Notas de la revisión manual (Diego Changotasig):** Comprobé que la condición de muelles vecinos signifique una diferencia de una posición, y que las limitaciones de conexión eléctrica y de rampa estén bien representadas.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

3 variables, dominios de tamaño 3 (espacio de búsqueda de 27 asignaciones), 4 reglas en lenguaje natural que se traducen en 4 restricciones atómicas, aridad máxima 3. Tipos de restricción: distancia/adyacencia, todos-distintos, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 5 nodos para enumerarlas todas.

---

## F03 — Calendario de mantenimiento preventivo

**Área:** Mantenimiento · **Dificultad:** Fácil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

La jefatura de mantenimiento de una planta de alimentos debe programar el mantenimiento preventivo de cuatro equipos: el compresor, la caldera, la banda transportadora y la prensa. Hay cuatro días disponibles, numerados del 1 (lunes) al 4 (jueves), y la cuadrilla atiende exactamente un equipo por día.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `COMPRESOR` | {1, 2, 3, 4} | día de mantenimiento del compresor |
| `CALDERA` | {1, 2, 3, 4} | día de mantenimiento de la caldera |
| `BANDA` | {1, 2, 3, 4} | día de mantenimiento de la banda transportadora |
| `PRENSA` | {1, 2, 3, 4} | día de mantenimiento de la prensa |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1 | Cada equipo recibe mantenimiento en un día distinto (uno por día). | `alldiff(COMPRESOR, CALDERA, BANDA, PRENSA)` |
| R2 | La prensa es neumática, por lo que el compresor debe revisarse en un día anterior al de la prensa. | `COMPRESOR < PRENSA` |
| R3 | La caldera no puede detenerse el día 1 por un pedido urgente. | `CALDERA != 1` |
| R4 | La banda debe revisarse exactamente el día siguiente al de la caldera, porque usa el mismo electricista. | `BANDA == CALDERA + 1` |
| R5 | La prensa no puede revisarse el día 4, porque ese día se usa para una auditoría. | `PRENSA != 4` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `COMPRESOR` | **1** |
| `CALDERA` | **3** |
| `BANDA` | **4** |
| `PRENSA` | **2** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1 | `alldiff(1, 3, 4, 2)` | ✓ |
| R2 | `1 < 2` | ✓ |
| R3 | `3 != 1` | ✓ |
| R4 | `4 == 3 + 1` | ✓ |
| R5 | `2 != 4` | ✓ |

**2. Unicidad — deducción manual:**

Por R3, CALDERA ∈ {2, 3, 4}, y por R4 BANDA = CALDERA + 1 ≤ 4, así que CALDERA ∈ {2, 3}. Si CALDERA = 2 y BANDA = 3, quedan los días {1, 4} para COMPRESOR < PRENSA, lo que da PRENSA = 4 y viola R5. Entonces CALDERA = 3, BANDA = 4, y en {1, 2} se cumple COMPRESOR = 1 < PRENSA = 2.

**Notas de la revisión manual (Diego Changotasig):** Revisé que 'antes de la prensa' sea una desigualdad estricta y que la banda se programe exactamente al día siguiente de la caldera. También comprobé los días que están prohibidos.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

4 variables, dominios de tamaño 4 (espacio de búsqueda de 256 asignaciones), 5 reglas en lenguaje natural que se traducen en 5 restricciones atómicas, aridad máxima 4. Tipos de restricción: igualdad (agrupación), precedencia/orden, todos-distintos, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 7 nodos para enumerarlas todas.

---

## F04 — Secuencia de operaciones en una estación

**Área:** Producción · **Dificultad:** Fácil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

En una estación de fabricación de soportes metálicos se realizan cuatro operaciones, una después de otra, ocupando las posiciones 1, 2, 3 y 4 de la secuencia (1 es la primera): corte, soldadura, pintura e inspección.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `CORTE` | {1, 2, 3, 4} | posición del corte en la secuencia |
| `SOLDADURA` | {1, 2, 3, 4} | posición de la soldadura |
| `PINTURA` | {1, 2, 3, 4} | posición de la pintura |
| `INSPECCION` | {1, 2, 3, 4} | posición de la inspección |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1 | Cada operación ocupa una posición distinta. | `alldiff(CORTE, SOLDADURA, PINTURA, INSPECCION)` |
| R2 | El corte debe realizarse antes que la soldadura. | `CORTE < SOLDADURA` |
| R3 | La soldadura debe realizarse antes que la pintura. | `SOLDADURA < PINTURA` |
| R4 | La inspección debe hacerse después de la soldadura. | `INSPECCION > SOLDADURA` |
| R5 | La inspección no puede ir inmediatamente después de la pintura, porque la pintura aún estaría húmeda. | `INSPECCION != PINTURA + 1` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `CORTE` | **1** |
| `SOLDADURA` | **2** |
| `PINTURA` | **4** |
| `INSPECCION` | **3** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1 | `alldiff(1, 2, 4, 3)` | ✓ |
| R2 | `1 < 2` | ✓ |
| R3 | `2 < 4` | ✓ |
| R4 | `3 > 2` | ✓ |
| R5 | `3 != 4 + 1` | ✓ |

**2. Unicidad — deducción manual:**

Por R2 y R3, CORTE < SOLDADURA < PINTURA, y por R4 INSPECCION > SOLDADURA. Entonces SOLDADURA tiene después al menos dos operaciones, así que SOLDADURA ≤ 2; como CORTE < SOLDADURA, CORTE = 1 y SOLDADURA = 2. PINTURA e INSPECCION ocupan {3, 4}. Si PINTURA = 3, INSPECCION = 4 = PINTURA + 1, lo que viola R5. Por tanto PINTURA = 4 e INSPECCION = 3.

**Notas de la revisión manual (Diego Changotasig):** Comparé el orden de las operaciones con las cinco reglas. El enunciado permite inspeccionar después de soldar y antes de pintar; no exige que la inspección sea la última operación, por eso el modelo no agrega esa condición.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

4 variables, dominios de tamaño 4 (espacio de búsqueda de 256 asignaciones), 5 reglas en lenguaje natural que se traducen en 5 restricciones atómicas, aridad máxima 4. Tipos de restricción: exclusión (≠), precedencia/orden, todos-distintos. El solver de referencia (MRV + forward checking) exploró 7 nodos para enumerarlas todas.

---

## F05 — Ubicación de productos en zonas del almacén

**Área:** Inventarios · **Dificultad:** Fácil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Un almacén tiene tres zonas: A (con ventilación forzada), B (estándar) y C (refrigerada). Hay que ubicar cuatro productos: ácido, alimento, solvente y papel. Cada producto se guarda completo en una sola zona.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `ACIDO` | {A, B, C} | zona del ácido |
| `ALIMENTO` | {A, B, C} | zona del alimento |
| `SOLVENTE` | {A, B, C} | zona del solvente |
| `PAPEL` | {A, B, C} | zona del papel |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Cada zona puede contener como máximo dos de estos productos. | `count('A', ACIDO, ALIMENTO, SOLVENTE, PAPEL) <= 2` |
| R1b | Cada zona puede contener como máximo dos de estos productos. | `count('B', ACIDO, ALIMENTO, SOLVENTE, PAPEL) <= 2` |
| R1c | Cada zona puede contener como máximo dos de estos productos. | `count('C', ACIDO, ALIMENTO, SOLVENTE, PAPEL) <= 2` |
| R2 | El alimento debe guardarse en la zona refrigerada. | `ALIMENTO == 'C'` |
| R3a | Ni el ácido ni el solvente pueden compartir zona con el alimento. | `ACIDO != ALIMENTO` |
| R3b | Ni el ácido ni el solvente pueden compartir zona con el alimento. | `SOLVENTE != ALIMENTO` |
| R4 | El ácido y el solvente reaccionan entre sí y no pueden compartir zona. | `ACIDO != SOLVENTE` |
| R5 | El solvente es volátil y debe guardarse en la zona con ventilación forzada. | `SOLVENTE == 'A'` |
| R6a | El papel no puede ir en la zona refrigerada (absorbe humedad) ni compartir zona con el solvente (es inflamable). | `PAPEL != 'C'` |
| R6b | El papel no puede ir en la zona refrigerada (absorbe humedad) ni compartir zona con el solvente (es inflamable). | `PAPEL != SOLVENTE` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `ACIDO` | **B** |
| `ALIMENTO` | **C** |
| `SOLVENTE` | **A** |
| `PAPEL` | **B** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `count('A', 'B', 'C', 'A', 'B') <= 2` | ✓ |
| R1b | `count('B', 'B', 'C', 'A', 'B') <= 2` | ✓ |
| R1c | `count('C', 'B', 'C', 'A', 'B') <= 2` | ✓ |
| R2 | `'C' == 'C'` | ✓ |
| R3a | `'B' != 'C'` | ✓ |
| R3b | `'A' != 'C'` | ✓ |
| R4 | `'B' != 'A'` | ✓ |
| R5 | `'A' == 'A'` | ✓ |
| R6a | `'B' != 'C'` | ✓ |
| R6b | `'B' != 'A'` | ✓ |

**2. Unicidad — deducción manual:**

Por R2, ALIMENTO = C. Por R5, SOLVENTE = A. Por R3 y R4, ÁCIDO ≠ C y ÁCIDO ≠ A, así que ÁCIDO = B. Por R6, PAPEL ≠ C y PAPEL ≠ A, así que PAPEL = B. Cada zona queda con a lo sumo 2 productos (R1).

**Notas de la revisión manual (Diego Changotasig):** Comprobé que se incluyan por separado las incompatibilidades del ácido y del solvente con el alimento, las condiciones de almacenamiento y el límite de dos productos por zona.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

4 variables, dominios de tamaño 3 (espacio de búsqueda de 81 asignaciones), 6 reglas en lenguaje natural que se traducen en 10 restricciones atómicas, aridad máxima 4. Tipos de restricción: conteo/cobertura, exclusión (≠), unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 5 nodos para enumerarlas todas.

---

## F06 — Asignación de inspectores de calidad

**Área:** Asignación de recursos · **Dificultad:** Fácil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Tres inspectores de calidad, Rosa, Pablo y Elena, deben revisar cuatro lotes recibidos hoy. LOTE1 y LOTE3 son de componentes eléctricos, LOTE2 es de insumos alimenticios y LOTE4 es metalmecánico. Rosa está certificada en eléctricos y metalmecánica; Pablo en alimentos y metalmecánica; Elena en eléctricos y alimentos. Cada lote es revisado por un solo inspector.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `LOTE1` | {ROSA, PABLO, ELENA} | inspector del LOTE1 |
| `LOTE2` | {ROSA, PABLO, ELENA} | inspector del LOTE2 |
| `LOTE3` | {ROSA, PABLO, ELENA} | inspector del LOTE3 |
| `LOTE4` | {ROSA, PABLO, ELENA} | inspector del LOTE4 |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Cada lote solo puede ser revisado por un inspector certificado en su tipo de producto. | `LOTE1 in ['ROSA', 'ELENA']` |
| R1b | Cada lote solo puede ser revisado por un inspector certificado en su tipo de producto. | `LOTE2 in ['PABLO', 'ELENA']` |
| R1c | Cada lote solo puede ser revisado por un inspector certificado en su tipo de producto. | `LOTE3 in ['ROSA', 'ELENA']` |
| R1d | Cada lote solo puede ser revisado por un inspector certificado en su tipo de producto. | `LOTE4 in ['ROSA', 'PABLO']` |
| R2 | Los dos lotes eléctricos deben ser revisados por inspectores distintos. | `LOTE1 != LOTE3` |
| R3 | Elena no puede revisar el LOTE2 por conflicto de interés con el proveedor. | `LOTE2 != 'ELENA'` |
| R4 | El LOTE1 y el LOTE4 vienen del mismo proveedor y deben ser revisados por el mismo inspector. | `LOTE1 == LOTE4` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `LOTE1` | **ROSA** |
| `LOTE2` | **PABLO** |
| `LOTE3` | **ELENA** |
| `LOTE4` | **ROSA** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `'ROSA' in ['ROSA', 'ELENA']` | ✓ |
| R1b | `'PABLO' in ['PABLO', 'ELENA']` | ✓ |
| R1c | `'ELENA' in ['ROSA', 'ELENA']` | ✓ |
| R1d | `'ROSA' in ['ROSA', 'PABLO']` | ✓ |
| R2 | `'ROSA' != 'ELENA'` | ✓ |
| R3 | `'PABLO' != 'ELENA'` | ✓ |
| R4 | `'ROSA' == 'ROSA'` | ✓ |

**2. Unicidad — deducción manual:**

Por R1 y R3, LOTE2 ∈ {PABLO, ELENA} y LOTE2 ≠ ELENA, así que LOTE2 = PABLO. Por R4 LOTE1 = LOTE4; LOTE1 ∈ {ROSA, ELENA} y LOTE4 ∈ {ROSA, PABLO}, por lo que ambos son ROSA. Por R2, LOTE3 ≠ ROSA, y como LOTE3 ∈ {ROSA, ELENA}, LOTE3 = ELENA.

**Notas de la revisión manual (Diego Changotasig):** Revisé las certificaciones de los tres inspectores y la excepción de Elena con LOTE2. Las reglas para separar los lotes eléctricos y juntar LOTE1 con LOTE4 coinciden con el enunciado.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

4 variables, dominios de tamaño 3 (espacio de búsqueda de 81 asignaciones), 4 reglas en lenguaje natural que se traducen en 7 restricciones atómicas, aridad máxima 2. Tipos de restricción: exclusión (≠), igualdad (agrupación), unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 5 nodos para enumerarlas todas.

---

## F07 — Asignación de operarios a turnos

**Área:** Turnos de trabajo · **Dificultad:** Fácil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una planta de envasado opera en tres turnos: mañana, tarde y noche. Cuatro operarios, Ana, Bruno, Carla y Diego, deben asignarse cada uno a exactamente un turno para la próxima semana.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `ANA` | {MANANA, TARDE, NOCHE} | turno de Ana |
| `BRUNO` | {MANANA, TARDE, NOCHE} | turno de Bruno |
| `CARLA` | {MANANA, TARDE, NOCHE} | turno de Carla |
| `DIEGO` | {MANANA, TARDE, NOCHE} | turno de Diego |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Cada turno debe tener al menos un operario. | `count('MANANA', ANA, BRUNO, CARLA, DIEGO) >= 1` |
| R1b | Cada turno debe tener al menos un operario. | `count('TARDE', ANA, BRUNO, CARLA, DIEGO) >= 1` |
| R1c | Cada turno debe tener al menos un operario. | `count('NOCHE', ANA, BRUNO, CARLA, DIEGO) >= 1` |
| R2 | Ana y Bruno no pueden estar en el mismo turno. | `ANA != BRUNO` |
| R3 | Carla no trabaja de noche. | `CARLA != 'NOCHE'` |
| R4 | Diego está en entrenamiento y debe estar en el mismo turno que Carla. | `DIEGO == CARLA` |
| R5 | Bruno no puede trabajar en el turno de la mañana. | `BRUNO != 'MANANA'` |
| R6 | Ana no puede trabajar de noche. | `ANA != 'NOCHE'` |
| R7 | Diego no puede trabajar en el turno de la tarde. | `DIEGO != 'TARDE'` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `ANA` | **TARDE** |
| `BRUNO` | **NOCHE** |
| `CARLA` | **MANANA** |
| `DIEGO` | **MANANA** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `count('MANANA', 'TARDE', 'NOCHE', 'MANANA', 'MANANA') >= 1` | ✓ |
| R1b | `count('TARDE', 'TARDE', 'NOCHE', 'MANANA', 'MANANA') >= 1` | ✓ |
| R1c | `count('NOCHE', 'TARDE', 'NOCHE', 'MANANA', 'MANANA') >= 1` | ✓ |
| R2 | `'TARDE' != 'NOCHE'` | ✓ |
| R3 | `'MANANA' != 'NOCHE'` | ✓ |
| R4 | `'MANANA' == 'MANANA'` | ✓ |
| R5 | `'NOCHE' != 'MANANA'` | ✓ |
| R6 | `'TARDE' != 'NOCHE'` | ✓ |
| R7 | `'MANANA' != 'TARDE'` | ✓ |

**2. Unicidad — deducción manual:**

Por R4 DIEGO = CARLA. CARLA ≠ NOCHE (R3) y DIEGO ≠ TARDE (R7), así que ambos están en MAÑANA. Por R1, la TARDE y la NOCHE deben cubrirlas ANA y BRUNO, que además deben estar en turnos distintos (R2). ANA ≠ NOCHE (R6), así que ANA = TARDE y BRUNO = NOCHE (esto cumple R5).

**Notas de la revisión manual (Diego Changotasig):** Comprobé que los tres turnos deban quedar cubiertos, que Diego trabaje con Carla y que se respeten las restricciones de disponibilidad de cada operario.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

4 variables, dominios de tamaño 3 (espacio de búsqueda de 81 asignaciones), 7 reglas en lenguaje natural que se traducen en 9 restricciones atómicas, aridad máxima 4. Tipos de restricción: conteo/cobertura, exclusión (≠), igualdad (agrupación), unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 8 nodos para enumerarlas todas.

---

## M08 — Secuenciación de pedidos en una inyectora

**Área:** Producción · **Dificultad:** Intermedio · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una inyectora de plásticos debe procesar cinco pedidos, P1 a P5, uno tras otro. Cada pedido ocupa una posición de la secuencia del día, de la 1 (primera) a la 5 (última).

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `P1` | {1, 2, 3, 4, 5} | posición del pedido P1 en la secuencia |
| `P2` | {1, 2, 3, 4, 5} | posición del pedido P2 en la secuencia |
| `P3` | {1, 2, 3, 4, 5} | posición del pedido P3 en la secuencia |
| `P4` | {1, 2, 3, 4, 5} | posición del pedido P4 en la secuencia |
| `P5` | {1, 2, 3, 4, 5} | posición del pedido P5 en la secuencia |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1 | Cada pedido ocupa una posición distinta. | `alldiff(P1, P2, P3, P4, P5)` |
| R2 | P2 es urgente y debe ir en una de las dos primeras posiciones. | `P2 <= 2` |
| R3 | P3 reutiliza el molde que se ajusta durante P1, así que P1 debe ir antes que P3. | `P1 < P3` |
| R4 | P4 y P5 usan el mismo colorante y deben ir en posiciones consecutivas (en cualquier orden). | `abs(P4 - P5) == 1` |
| R5 | P3 debe ir antes que P5. | `P3 < P5` |
| R6 | La materia prima de P1 llega tarde, por lo que P1 no puede ir en la posición 1. | `P1 != 1` |
| R7 | P5 requiere una limpieza posterior larga, por lo que no puede ser el último pedido del día. | `P5 != 5` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `P1` | **2** |
| `P2` | **1** |
| `P3` | **3** |
| `P4` | **5** |
| `P5` | **4** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1 | `alldiff(2, 1, 3, 5, 4)` | ✓ |
| R2 | `1 <= 2` | ✓ |
| R3 | `2 < 3` | ✓ |
| R4 | `abs(5 - 4) == 1` | ✓ |
| R5 | `3 < 4` | ✓ |
| R6 | `2 != 1` | ✓ |
| R7 | `4 != 5` | ✓ |

**2. Unicidad — deducción manual:**

Por R6, P1 ≥ 2. Por R3 y R5, P1 < P3 < P5, así que P5 ≥ 4; como P5 ≠ 5 (R7), P5 = 4 y entonces P3 = 3 y P1 = 2. Por R4, P4 es vecino de P5 = 4 y el 3 está ocupado, así que P4 = 5. Queda P2 = 1, que cumple R2.

**Notas de la revisión manual (Diego Changotasig):** Revisé que 'antes' se represente con <, 'dos primeras posiciones' con <= 2 y 'consecutivos' con una diferencia absoluta de 1. También comprobé las dos posiciones prohibidas.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

5 variables, dominios de tamaño 5 (espacio de búsqueda de 3,125 asignaciones), 7 reglas en lenguaje natural que se traducen en 7 restricciones atómicas, aridad máxima 5. Tipos de restricción: distancia/adyacencia, precedencia/orden, todos-distintos, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 15 nodos para enumerarlas todas.

---

## M09 — Asignación de operarios a estaciones de trabajo

**Área:** Asignación de recursos · **Dificultad:** Intermedio · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una línea de ensamble de electrodomésticos tiene tres estaciones: ENSAMBLE, EMPAQUE y CONTROL (control de calidad). Seis operarios, Ana, Beto, Caro, Dani, Edu y Fer, deben asignarse cada uno a exactamente una estación. Solo Ana, Beto y Dani tienen la certificación de control de calidad.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `ANA` | {ENSAMBLE, EMPAQUE, CONTROL} | estación de Ana |
| `BETO` | {ENSAMBLE, EMPAQUE, CONTROL} | estación de Beto |
| `CARO` | {ENSAMBLE, EMPAQUE, CONTROL} | estación de Caro |
| `DANI` | {ENSAMBLE, EMPAQUE, CONTROL} | estación de Dani |
| `EDU` | {ENSAMBLE, EMPAQUE, CONTROL} | estación de Edu |
| `FER` | {ENSAMBLE, EMPAQUE, CONTROL} | estación de Fer |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Cada estación debe tener exactamente dos operarios. | `count('ENSAMBLE', ANA, BETO, CARO, DANI, EDU, FER) == 2` |
| R1b | Cada estación debe tener exactamente dos operarios. | `count('EMPAQUE', ANA, BETO, CARO, DANI, EDU, FER) == 2` |
| R1c | Cada estación debe tener exactamente dos operarios. | `count('CONTROL', ANA, BETO, CARO, DANI, EDU, FER) == 2` |
| R2a | En CONTROL solo pueden trabajar operarios certificados. | `CARO != 'CONTROL'` |
| R2b | En CONTROL solo pueden trabajar operarios certificados. | `EDU != 'CONTROL'` |
| R2c | En CONTROL solo pueden trabajar operarios certificados. | `FER != 'CONTROL'` |
| R3 | Ana y Beto son supervisores de relevo y no pueden estar en la misma estación. | `ANA != BETO` |
| R4 | Edu y Fer son nuevos y no pueden estar en la misma estación. | `EDU != FER` |
| R5 | Caro es la tutora de Edu y debe estar en la misma estación que él. | `CARO == EDU` |
| R6 | Dani tiene una restricción médica y no puede trabajar en EMPAQUE. | `DANI != 'EMPAQUE'` |
| R7 | Ana y Fer no pueden estar en la misma estación. | `ANA != FER` |
| R8 | Beto no tiene el curso de la máquina de ensamble, así que no puede trabajar en ENSAMBLE. | `BETO != 'ENSAMBLE'` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `ANA` | **CONTROL** |
| `BETO` | **EMPAQUE** |
| `CARO` | **ENSAMBLE** |
| `DANI` | **CONTROL** |
| `EDU` | **ENSAMBLE** |
| `FER` | **EMPAQUE** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `count('ENSAMBLE', 'CONTROL', 'EMPAQUE', 'ENSAMBLE', 'CONTROL', 'ENSAMBLE', 'EMPAQUE') == 2` | ✓ |
| R1b | `count('EMPAQUE', 'CONTROL', 'EMPAQUE', 'ENSAMBLE', 'CONTROL', 'ENSAMBLE', 'EMPAQUE') == 2` | ✓ |
| R1c | `count('CONTROL', 'CONTROL', 'EMPAQUE', 'ENSAMBLE', 'CONTROL', 'ENSAMBLE', 'EMPAQUE') == 2` | ✓ |
| R2a | `'ENSAMBLE' != 'CONTROL'` | ✓ |
| R2b | `'ENSAMBLE' != 'CONTROL'` | ✓ |
| R2c | `'EMPAQUE' != 'CONTROL'` | ✓ |
| R3 | `'CONTROL' != 'EMPAQUE'` | ✓ |
| R4 | `'ENSAMBLE' != 'EMPAQUE'` | ✓ |
| R5 | `'ENSAMBLE' == 'ENSAMBLE'` | ✓ |
| R6 | `'CONTROL' != 'EMPAQUE'` | ✓ |
| R7 | `'CONTROL' != 'EMPAQUE'` | ✓ |
| R8 | `'EMPAQUE' != 'ENSAMBLE'` | ✓ |

**2. Unicidad — deducción manual:**

CONTROL necesita dos certificados (R1, R2) entre {ANA, BETO, DANI}, y ANA ≠ BETO (R3), así que CONTROL = DANI + uno de ANA/BETO. Por R5 CARO = EDU, y ambos llenan una estación no-control. FER ≠ EDU (R4), así que FER va a la otra estación no-control junto con el supervisor que no está en CONTROL. Por R7 ANA ≠ FER, de modo que ANA = CONTROL y BETO va con FER. Por R8 BETO ≠ ENSAMBLE, así que BETO y FER están en EMPAQUE y CARO y EDU en ENSAMBLE.

**Notas de la revisión manual (Diego Changotasig):** Comparé las certificaciones para CONTROL, el límite exacto de dos personas por estación y las reglas sobre compañeros que deben trabajar juntos o separados. No encontré reglas omitidas en el modelo.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

6 variables, dominios de tamaño 3 (espacio de búsqueda de 729 asignaciones), 8 reglas en lenguaje natural que se traducen en 12 restricciones atómicas, aridad máxima 6. Tipos de restricción: conteo/cobertura, exclusión (≠), igualdad (agrupación), unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 13 nodos para enumerarlas todas.

---

## M10 — Asignación de clientes a vehículos de reparto

**Área:** Logística · **Dificultad:** Intermedio · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una distribuidora debe atender mañana a cinco clientes con tres vehículos. Capacidades: V1 = 10 toneladas, V2 = 8 toneladas y V3 = 6 toneladas. Demandas: C1 = 6 t, C2 = 3 t, C3 = 5 t, C4 = 2 t y C5 = 4 t. Cada cliente es atendido completo por un solo vehículo. Solo V1 tiene equipo de refrigeración.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `C1` | {V1, V2, V3} | vehículo que atiende al cliente C1 |
| `C2` | {V1, V2, V3} | vehículo que atiende al cliente C2 |
| `C3` | {V1, V2, V3} | vehículo que atiende al cliente C3 |
| `C4` | {V1, V2, V3} | vehículo que atiende al cliente C4 |
| `C5` | {V1, V2, V3} | vehículo que atiende al cliente C5 |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | La carga total asignada a cada vehículo no puede superar su capacidad. | `(C1 == 'V1')*6 + (C2 == 'V1')*3 + (C3 == 'V1')*5 + (C4 == 'V1')*2 + (C5 == 'V1')*4 <= 10` |
| R1b | La carga total asignada a cada vehículo no puede superar su capacidad. | `(C1 == 'V2')*6 + (C2 == 'V2')*3 + (C3 == 'V2')*5 + (C4 == 'V2')*2 + (C5 == 'V2')*4 <= 8` |
| R1c | La carga total asignada a cada vehículo no puede superar su capacidad. | `(C1 == 'V3')*6 + (C2 == 'V3')*3 + (C3 == 'V3')*5 + (C4 == 'V3')*2 + (C5 == 'V3')*4 <= 6` |
| R2 | El pedido de C2 es perecible y requiere refrigeración. | `C2 == 'V1'` |
| R3 | C4 está en el centro histórico, donde solo puede circular V3. | `C4 == 'V3'` |
| R4 | C1 y C3 están en direcciones opuestas de la ciudad y no pueden ir en el mismo vehículo. | `C1 != C3` |
| R5 | C2 y C3 son sucursales de la misma cadena y deben ser atendidas por el mismo vehículo. | `C3 == C2` |
| R6a | Los tres vehículos deben salir con al menos un cliente. | `count('V1', C1, C2, C3, C4, C5) >= 1` |
| R6b | Los tres vehículos deben salir con al menos un cliente. | `count('V2', C1, C2, C3, C4, C5) >= 1` |
| R6c | Los tres vehículos deben salir con al menos un cliente. | `count('V3', C1, C2, C3, C4, C5) >= 1` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `C1` | **V2** |
| `C2` | **V1** |
| `C3` | **V1** |
| `C4` | **V3** |
| `C5` | **V3** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `('V2' == 'V1') * 6 + ('V1' == 'V1') * 3 + ('V1' == 'V1') * 5 + ('V3' == 'V1') * 2 + ('V3' == 'V1') * 4 <= 10` | ✓ |
| R1b | `('V2' == 'V2') * 6 + ('V1' == 'V2') * 3 + ('V1' == 'V2') * 5 + ('V3' == 'V2') * 2 + ('V3' == 'V2') * 4 <= 8` | ✓ |
| R1c | `('V2' == 'V3') * 6 + ('V1' == 'V3') * 3 + ('V1' == 'V3') * 5 + ('V3' == 'V3') * 2 + ('V3' == 'V3') * 4 <= 6` | ✓ |
| R2 | `'V1' == 'V1'` | ✓ |
| R3 | `'V3' == 'V3'` | ✓ |
| R4 | `'V2' != 'V1'` | ✓ |
| R5 | `'V1' == 'V1'` | ✓ |
| R6a | `count('V1', 'V2', 'V1', 'V1', 'V3', 'V3') >= 1` | ✓ |
| R6b | `count('V2', 'V2', 'V1', 'V1', 'V3', 'V3') >= 1` | ✓ |
| R6c | `count('V3', 'V2', 'V1', 'V1', 'V3', 'V3') >= 1` | ✓ |

**2. Unicidad — deducción manual:**

Por R2 y R5, C2 = C3 = V1. Por R3, C4 = V3. Por R4, C1 ≠ V1. Si C1 = V3, la carga sería 2 + 6 = 8 > 6, así que C1 = V2. C5 (4 t): en V1 serían 3 + 5 + 4 = 12 > 10, en V2 serían 6 + 4 = 10 > 8, y en V3 son 2 + 4 = 6 ≤ 6, así que C5 = V3. Los tres vehículos salen con clientes (R6).

**Notas de la revisión manual (Diego Changotasig):** Comprobé que las demandas de los cinco clientes y las capacidades de V1, V2 y V3 coincidan con el contexto. También revisé la refrigeración, las restricciones de compartir vehículo y que cada vehículo atienda al menos un cliente.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

5 variables, dominios de tamaño 3 (espacio de búsqueda de 243 asignaciones), 6 reglas en lenguaje natural que se traducen en 10 restricciones atómicas, aridad máxima 5. Tipos de restricción: capacidad ponderada, conteo/cobertura, exclusión (≠), igualdad (agrupación), unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 6 nodos para enumerarlas todas.

---

## M11 — Programa de mantenimiento con capacidad limitada

**Área:** Mantenimiento · **Dificultad:** Intermedio · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una planta textil debe dar mantenimiento a cinco equipos durante una parada de tres días (días 1, 2 y 3): el generador, el tablero eléctrico, el compresor, el secador de aire y el horno de termofijado. Cada equipo se atiende completo en un solo día.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `GENERADOR` | {1, 2, 3} | día del generador |
| `TABLERO` | {1, 2, 3} | día del tablero eléctrico |
| `COMPRESOR` | {1, 2, 3} | día del compresor |
| `SECADOR` | {1, 2, 3} | día del secador de aire |
| `HORNO` | {1, 2, 3} | día del horno |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | La cuadrilla puede atender como máximo dos equipos por día. | `count(1, GENERADOR, TABLERO, COMPRESOR, SECADOR, HORNO) <= 2` |
| R1b | La cuadrilla puede atender como máximo dos equipos por día. | `count(2, GENERADOR, TABLERO, COMPRESOR, SECADOR, HORNO) <= 2` |
| R1c | La cuadrilla puede atender como máximo dos equipos por día. | `count(3, GENERADOR, TABLERO, COMPRESOR, SECADOR, HORNO) <= 2` |
| R2 | El generador debe atenderse en un día anterior al del tablero, porque es la energía de respaldo durante esa intervención. | `GENERADOR < TABLERO` |
| R3 | El compresor y el secador forman el mismo sistema neumático y se atienden el mismo día. | `COMPRESOR == SECADOR` |
| R4 | El horno no puede atenderse el día 1 porque todavía estará caliente. | `HORNO != 1` |
| R5 | El tablero no puede atenderse el día 3, porque ese día llega el inspector eléctrico externo para certificarlo ya reparado. | `TABLERO != 3` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `GENERADOR` | **1** |
| `TABLERO` | **2** |
| `COMPRESOR` | **3** |
| `SECADOR` | **3** |
| `HORNO` | **2** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `count(1, 1, 2, 3, 3, 2) <= 2` | ✓ |
| R1b | `count(2, 1, 2, 3, 3, 2) <= 2` | ✓ |
| R1c | `count(3, 1, 2, 3, 3, 2) <= 2` | ✓ |
| R2 | `1 < 2` | ✓ |
| R3 | `3 == 3` | ✓ |
| R4 | `2 != 1` | ✓ |
| R5 | `2 != 3` | ✓ |

**2. Unicidad — deducción manual:**

Por R2 GENERADOR < TABLERO, así que TABLERO ≥ 2, y por R5 TABLERO ≠ 3, así que TABLERO = 2 y GENERADOR = 1. Por R4, HORNO ∈ {2, 3}. COMPRESOR = SECADOR (R3) necesitan un día con dos cupos libres (R1). Si HORNO = 3, los tres días quedan con un solo cupo libre y no hay solución. Entonces HORNO = 2 (día 2 lleno con TABLERO y HORNO), y COMPRESOR = SECADOR = 3.

**Notas de la revisión manual (Diego Changotasig):** Revisé el máximo de dos mantenimientos por día, el orden generador-tablero y que compresor y secador se atiendan juntos. También verifiqué las prohibiciones del horno y del tablero.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

5 variables, dominios de tamaño 3 (espacio de búsqueda de 243 asignaciones), 5 reglas en lenguaje natural que se traducen en 7 restricciones atómicas, aridad máxima 5. Tipos de restricción: conteo/cobertura, igualdad (agrupación), precedencia/orden, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 7 nodos para enumerarlas todas.

---

## M12 — Días libres del personal de bodega

**Área:** Turnos de trabajo · **Dificultad:** Intermedio · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una bodega trabaja de lunes a viernes (días 1 = lunes a 5 = viernes). Cada uno de sus cinco trabajadores, Luis, María, Jorge, Sofía y Pedro, tiene exactamente un día libre a la semana. Jorge y Sofía son los únicos operadores de montacargas.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `LUIS` | {1, 2, 3, 4, 5} | día libre de Luis |
| `MARIA` | {1, 2, 3, 4, 5} | día libre de Maria |
| `JORGE` | {1, 2, 3, 4, 5} | día libre de Jorge |
| `SOFIA` | {1, 2, 3, 4, 5} | día libre de Sofia |
| `PEDRO` | {1, 2, 3, 4, 5} | día libre de Pedro |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1 | Para mantener la cobertura, no puede haber dos trabajadores libres el mismo día. | `alldiff(LUIS, MARIA, JORGE, SOFIA, PEDRO)` |
| R2 | Los días libres de los dos operadores de montacargas no pueden ser consecutivos ni iguales (debe haber al menos un día entre ellos). | `abs(JORGE - SOFIA) >= 2` |
| R3 | María estudia y su día libre debe ser lunes o viernes. | `MARIA in [1, 5]` |
| R4 | Pedro es el encargado de recepción y no puede librar ni lunes ni viernes, que son días de mayor recepción. | `PEDRO not in [1, 5]` |
| R5 | Luis debe librar un día anterior al de Pedro. | `LUIS < PEDRO` |
| R6 | Sofía libra después que Jorge. | `SOFIA > JORGE` |
| R7 | María libra el día inmediatamente posterior al de Sofía. | `MARIA == SOFIA + 1` |
| R8 | Luis no puede librar el lunes, porque ese día hace el inventario semanal. | `LUIS != 1` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `LUIS` | **2** |
| `MARIA` | **5** |
| `JORGE` | **1** |
| `SOFIA` | **4** |
| `PEDRO` | **3** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1 | `alldiff(2, 5, 1, 4, 3)` | ✓ |
| R2 | `abs(1 - 4) >= 2` | ✓ |
| R3 | `5 in [1, 5]` | ✓ |
| R4 | `3 not in [1, 5]` | ✓ |
| R5 | `2 < 3` | ✓ |
| R6 | `4 > 1` | ✓ |
| R7 | `5 == 4 + 1` | ✓ |
| R8 | `2 != 1` | ✓ |

**2. Unicidad — deducción manual:**

Por R3 y R7, MARIA ∈ {1, 5} y MARIA = SOFIA + 1, así que MARIA = 5 y SOFIA = 4. Por R6 y R2, JORGE < 4 y |JORGE − 4| ≥ 2, así que JORGE ≤ 2. Por R4, PEDRO ∈ {2, 3, 4} y el 4 está ocupado. Quedan los días {1, 2, 3} para LUIS, JORGE y PEDRO. LUIS ≠ 1 (R8) y LUIS < PEDRO (R5) obligan a LUIS = 2, PEDRO = 3, y entonces JORGE = 1.

**Notas de la revisión manual (Diego Changotasig):** Comprobé que los días libres sean distintos, que los de Jorge y Sofía tengan al menos un día de separación y que María libre exactamente al día siguiente de Sofía. Las demás disponibilidades también coinciden.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

5 variables, dominios de tamaño 5 (espacio de búsqueda de 3,125 asignaciones), 8 reglas en lenguaje natural que se traducen en 8 restricciones atómicas, aridad máxima 5. Tipos de restricción: distancia/adyacencia, igualdad (agrupación), precedencia/orden, todos-distintos, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 7 nodos para enumerarlas todas.

---

## M13 — Ubicación de productos en una estantería

**Área:** Inventarios · **Dificultad:** Intermedio · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

En una bodega de repuestos hay una estantería de tres niveles: nivel 1 (piso), nivel 2 (altura de la cintura) y nivel 3 (alto). Deben ubicarse seis productos: motor, tornillos, cable, pintura, filtros y guantes. El motor y la pintura pesan más de 20 kg, y los tornillos y los guantes son los de mayor rotación.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `MOTOR` | {1, 2, 3} | nivel del producto motor |
| `TORNILLOS` | {1, 2, 3} | nivel del producto tornillos |
| `CABLE` | {1, 2, 3} | nivel del producto cable |
| `PINTURA` | {1, 2, 3} | nivel del producto pintura |
| `FILTROS` | {1, 2, 3} | nivel del producto filtros |
| `GUANTES` | {1, 2, 3} | nivel del producto guantes |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Cada nivel tiene espacio para exactamente dos productos. | `count(1, MOTOR, TORNILLOS, CABLE, PINTURA, FILTROS, GUANTES) == 2` |
| R1b | Cada nivel tiene espacio para exactamente dos productos. | `count(2, MOTOR, TORNILLOS, CABLE, PINTURA, FILTROS, GUANTES) == 2` |
| R1c | Cada nivel tiene espacio para exactamente dos productos. | `count(3, MOTOR, TORNILLOS, CABLE, PINTURA, FILTROS, GUANTES) == 2` |
| R2a | Los productos de más de 20 kg no pueden ir en el nivel 3. | `MOTOR != 3` |
| R2b | Los productos de más de 20 kg no pueden ir en el nivel 3. | `PINTURA != 3` |
| R3a | Los dos productos de mayor rotación no pueden ir en el nivel 3. | `TORNILLOS != 3` |
| R3b | Los dos productos de mayor rotación no pueden ir en el nivel 3. | `GUANTES != 3` |
| R4 | La pintura es líquida y no puede estar en un nivel superior al del cable, para no gotear sobre él. | `PINTURA <= CABLE` |
| R5 | El motor y la pintura no pueden compartir nivel (no caben juntos). | `MOTOR != PINTURA` |
| R6 | Los tornillos y los guantes no pueden compartir nivel, para separar los dos puntos de mayor tránsito. | `TORNILLOS != GUANTES` |
| R7 | La pintura no puede compartir nivel con los guantes, para evitar que se manchen. | `PINTURA != GUANTES` |
| R8 | Los tornillos no van en el nivel 1, para evitar que el operario se agache con tanta frecuencia. | `TORNILLOS != 1` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `MOTOR` | **1** |
| `TORNILLOS` | **2** |
| `CABLE` | **3** |
| `PINTURA` | **2** |
| `FILTROS` | **3** |
| `GUANTES` | **1** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `count(1, 1, 2, 3, 2, 3, 1) == 2` | ✓ |
| R1b | `count(2, 1, 2, 3, 2, 3, 1) == 2` | ✓ |
| R1c | `count(3, 1, 2, 3, 2, 3, 1) == 2` | ✓ |
| R2a | `1 != 3` | ✓ |
| R2b | `2 != 3` | ✓ |
| R3a | `2 != 3` | ✓ |
| R3b | `1 != 3` | ✓ |
| R4 | `2 <= 3` | ✓ |
| R5 | `1 != 2` | ✓ |
| R6 | `2 != 1` | ✓ |
| R7 | `2 != 1` | ✓ |
| R8 | `2 != 1` | ✓ |

**2. Unicidad — deducción manual:**

Por R3 y R6, TORNILLOS y GUANTES ∈ {1, 2} y son distintos; TORNILLOS ≠ 1 (R8), así que TORNILLOS = 2 y GUANTES = 1. Por R2 y R5, MOTOR y PINTURA ∈ {1, 2} y son distintos; PINTURA ≠ GUANTES (R7), así que PINTURA = 2 y MOTOR = 1. Los niveles 1 y 2 quedan llenos (R1), así que CABLE = FILTROS = 3. R4 se cumple (2 ≤ 3).

**Notas de la revisión manual (Diego Changotasig):** Revisé la capacidad exacta de dos productos por nivel, las restricciones por peso y rotación y las incompatibilidades entre productos. La condición de pintura respecto al cable está bien expresada como <=.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

6 variables, dominios de tamaño 3 (espacio de búsqueda de 729 asignaciones), 8 reglas en lenguaje natural que se traducen en 12 restricciones atómicas, aridad máxima 6. Tipos de restricción: conteo/cobertura, exclusión (≠), precedencia/orden, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 7 nodos para enumerarlas todas.

---

## M14 — Distribución en planta de departamentos

**Área:** Producción · **Dificultad:** Intermedio · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Se va a redistribuir una nave industrial con seis espacios en línea recta, numerados del 1 al 6; dos espacios son vecinos si sus números difieren en 1. Deben ubicarse seis departamentos: recepción, corte, soldadura, ensamble, pintura y despacho, uno por espacio.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `RECEPCION` | {1, 2, 3, 4, 5, 6} | espacio del departamento de recepcion |
| `CORTE` | {1, 2, 3, 4, 5, 6} | espacio del departamento de corte |
| `SOLDADURA` | {1, 2, 3, 4, 5, 6} | espacio del departamento de soldadura |
| `ENSAMBLE` | {1, 2, 3, 4, 5, 6} | espacio del departamento de ensamble |
| `PINTURA` | {1, 2, 3, 4, 5, 6} | espacio del departamento de pintura |
| `DESPACHO` | {1, 2, 3, 4, 5, 6} | espacio del departamento de despacho |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1 | Cada departamento ocupa un espacio distinto. | `alldiff(RECEPCION, CORTE, SOLDADURA, ENSAMBLE, PINTURA, DESPACHO)` |
| R2 | Recepción y despacho deben estar en los dos extremos de la nave (espacios 1 y 6, en cualquier orden). | `abs(RECEPCION - DESPACHO) == 5` |
| R3 | Corte debe estar junto a recepción, porque recibe la materia prima. | `abs(CORTE - RECEPCION) == 1` |
| R4 | Soldadura debe estar junto a corte. | `abs(SOLDADURA - CORTE) == 1` |
| R5a | Pintura no puede estar junto a corte ni junto a soldadura, por el riesgo de chispas. | `abs(PINTURA - CORTE) >= 2` |
| R5b | Pintura no puede estar junto a corte ni junto a soldadura, por el riesgo de chispas. | `abs(PINTURA - SOLDADURA) >= 2` |
| R6 | Ensamble debe estar junto a pintura. | `abs(ENSAMBLE - PINTURA) == 1` |
| R7 | La toma de corriente trifásica que necesita corte solo existe en los espacios 1, 2 y 3. | `CORTE in [1, 2, 3]` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `RECEPCION` | **1** |
| `CORTE` | **2** |
| `SOLDADURA` | **3** |
| `ENSAMBLE` | **4** |
| `PINTURA` | **5** |
| `DESPACHO` | **6** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1 | `alldiff(1, 2, 3, 4, 5, 6)` | ✓ |
| R2 | `abs(1 - 6) == 5` | ✓ |
| R3 | `abs(2 - 1) == 1` | ✓ |
| R4 | `abs(3 - 2) == 1` | ✓ |
| R5a | `abs(5 - 2) >= 2` | ✓ |
| R5b | `abs(5 - 3) >= 2` | ✓ |
| R6 | `abs(4 - 5) == 1` | ✓ |
| R7 | `2 in [1, 2, 3]` | ✓ |

**2. Unicidad — deducción manual:**

Por R2, RECEPCION y DESPACHO ocupan los extremos. Si RECEPCION = 6, por R3 CORTE = 5, lo que viola R7. Entonces RECEPCION = 1, DESPACHO = 6 y CORTE = 2. Por R4, SOLDADURA = 3. PINTURA y ENSAMBLE quedan en {4, 5}; por R5, PINTURA ≠ 4 (vecino de SOLDADURA), así que PINTURA = 5 y ENSAMBLE = 4, que cumple R6.

**Notas de la revisión manual (Diego Changotasig):** Comprobé que recepción y despacho ocupen extremos opuestos y que 'junto a' se represente con diferencia absoluta de 1. También revisé las separaciones de pintura y los espacios permitidos para corte.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

6 variables, dominios de tamaño 6 (espacio de búsqueda de 46,656 asignaciones), 7 reglas en lenguaje natural que se traducen en 8 restricciones atómicas, aridad máxima 6. Tipos de restricción: distancia/adyacencia, todos-distintos, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 10 nodos para enumerarlas todas.

---

## D15 — Programación de un taller de fabricación (job shop)

**Área:** Producción · **Dificultad:** Difícil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Un taller debe fabricar hoy tres pedidos, A, B y C, durante una jornada de 8 horas (las horas se cuentan desde 0, inicio de la jornada, hasta 8, fin de la jornada). Cada operación empieza en una hora entera y se ejecuta sin interrupción. Las operaciones son:
- A1: corte de A, 2 h; A2: doblado de A, 1 h.
- B1: corte de B, 1 h; B2: doblado de B, 2 h.
- C1: corte de C, 2 h; C2: doblado de C, 2 h; C3: pintura de C, 1 h.
Hay una sola cortadora, una sola dobladora y una sola cabina de pintura. La pregunta es la hora de inicio de cada operación.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `A1` | {0, 1, 2, 3, 4, 5, 6, 7} | hora de inicio de la operación A1 |
| `A2` | {0, 1, 2, 3, 4, 5, 6, 7} | hora de inicio de la operación A2 |
| `B1` | {0, 1, 2, 3, 4, 5, 6, 7} | hora de inicio de la operación B1 |
| `B2` | {0, 1, 2, 3, 4, 5, 6, 7} | hora de inicio de la operación B2 |
| `C1` | {0, 1, 2, 3, 4, 5, 6, 7} | hora de inicio de la operación C1 |
| `C2` | {0, 1, 2, 3, 4, 5, 6, 7} | hora de inicio de la operación C2 |
| `C3` | {0, 1, 2, 3, 4, 5, 6, 7} | hora de inicio de la operación C3 |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Dentro de cada pedido, una operación solo puede empezar cuando terminó la anterior (A1 antes que A2; B1 antes que B2; C1 antes que C2 y C2 antes que C3). | `A1 + 2 <= A2` |
| R1b | Dentro de cada pedido, una operación solo puede empezar cuando terminó la anterior (A1 antes que A2; B1 antes que B2; C1 antes que C2 y C2 antes que C3). | `B1 + 1 <= B2` |
| R1c | Dentro de cada pedido, una operación solo puede empezar cuando terminó la anterior (A1 antes que A2; B1 antes que B2; C1 antes que C2 y C2 antes que C3). | `C1 + 2 <= C2` |
| R1d | Dentro de cada pedido, una operación solo puede empezar cuando terminó la anterior (A1 antes que A2; B1 antes que B2; C1 antes que C2 y C2 antes que C3). | `C2 + 2 <= C3` |
| R2a | La cortadora solo puede hacer una operación a la vez (A1, B1 y C1 no pueden solaparse). | `A1 + 2 <= B1 or B1 + 1 <= A1` |
| R2b | La cortadora solo puede hacer una operación a la vez (A1, B1 y C1 no pueden solaparse). | `A1 + 2 <= C1 or C1 + 2 <= A1` |
| R2c | La cortadora solo puede hacer una operación a la vez (A1, B1 y C1 no pueden solaparse). | `B1 + 1 <= C1 or C1 + 2 <= B1` |
| R3a | La dobladora solo puede hacer una operación a la vez (A2, B2 y C2 no pueden solaparse). | `A2 + 1 <= B2 or B2 + 2 <= A2` |
| R3b | La dobladora solo puede hacer una operación a la vez (A2, B2 y C2 no pueden solaparse). | `A2 + 1 <= C2 or C2 + 2 <= A2` |
| R3c | La dobladora solo puede hacer una operación a la vez (A2, B2 y C2 no pueden solaparse). | `B2 + 2 <= C2 or C2 + 2 <= B2` |
| R4a | Todas las operaciones deben terminar a más tardar en la hora 8 (fin de la jornada). | `A2 + 1 <= 8` |
| R4b | Todas las operaciones deben terminar a más tardar en la hora 8 (fin de la jornada). | `B2 + 2 <= 8` |
| R4c | Todas las operaciones deben terminar a más tardar en la hora 8 (fin de la jornada). | `C3 + 1 <= 8` |
| R5 | El doblado de B requiere cambiar el dado de la dobladora, por lo que B2 solo puede empezar después de que termine A2. | `A2 + 1 <= B2` |
| R6 | La pintura de C debe empezar exactamente cuando termina su doblado (C2), para que la pieza no se oxide. | `C3 == C2 + 2` |
| R7 | La cabina de pintura está ocupada por otro cliente hasta la hora 7, así que C3 no puede empezar antes de la hora 7. | `C3 >= 7` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `A1` | **0** |
| `A2` | **2** |
| `B1` | **2** |
| `B2` | **3** |
| `C1` | **3** |
| `C2` | **5** |
| `C3` | **7** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `0 + 2 <= 2` | ✓ |
| R1b | `2 + 1 <= 3` | ✓ |
| R1c | `3 + 2 <= 5` | ✓ |
| R1d | `5 + 2 <= 7` | ✓ |
| R2a | `0 + 2 <= 2 or 2 + 1 <= 0` | ✓ |
| R2b | `0 + 2 <= 3 or 3 + 2 <= 0` | ✓ |
| R2c | `2 + 1 <= 3 or 3 + 2 <= 2` | ✓ |
| R3a | `2 + 1 <= 3 or 3 + 2 <= 2` | ✓ |
| R3b | `2 + 1 <= 5 or 5 + 2 <= 2` | ✓ |
| R3c | `3 + 2 <= 5 or 5 + 2 <= 3` | ✓ |
| R4a | `2 + 1 <= 8` | ✓ |
| R4b | `3 + 2 <= 8` | ✓ |
| R4c | `7 + 1 <= 8` | ✓ |
| R5 | `2 + 1 <= 3` | ✓ |
| R6 | `7 == 5 + 2` | ✓ |
| R7 | `7 >= 7` | ✓ |

**2. Unicidad — deducción manual:**

Por R7 y R4 (C3 ≥ 7 y C3 + 1 ≤ 8), C3 = 7, y por R6 C2 = 5, y la dobladora está ocupada en [5, 7). B2 (2 h, fin ≤ 8) no puede solaparse con C2, así que B2 ≤ 3. Por R5, A2 ≤ B2 − 1 ≤ 2, y por R1 A2 ≥ A1 + 2 ≥ 2, de modo que A2 = 2, A1 = 0 y B2 = 3. Por R1, B1 ≤ 2, y la cortadora está ocupada en [0, 2) por A1, así que B1 = 2. C1 debe terminar antes de C2 = 5 (C1 ≤ 3) y no puede solaparse con [0, 3), así que C1 = 3.

**Notas de la revisión manual (Diego Changotasig):** Revisé las duraciones de cada operación, las precedencias y que las máquinas no atiendan dos tareas a la vez. La hora límite es 8, y la pintura C3 debe empezar justo al terminar C2 y no antes de la hora 7.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

7 variables, dominios de tamaño 8 (espacio de búsqueda de 2,097,152 asignaciones), 7 reglas en lenguaje natural que se traducen en 16 restricciones atómicas, aridad máxima 2. Tipos de restricción: disyuntiva (no solapamiento), igualdad (agrupación), precedencia/orden, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 10 nodos para enumerarlas todas.

---

## D16 — Asignación de pedidos a líneas de producción con capacidad

**Área:** Producción · **Dificultad:** Difícil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una planta de envases tiene tres líneas de producción: L1 y L2, con 8 horas disponibles cada una, y L3, con 6 horas disponibles. Debe asignar ocho pedidos, cada uno completo a una sola línea. Duración de cada pedido: P1 = 4 h, P2 = 3 h, P3 = 2 h, P4 = 5 h, P5 = 3 h, P6 = 2 h, P7 = 1 h y P8 = 2 h. P3 y P6 son envases para alimentos; P7 usa un recubrimiento con lubricante industrial.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `P1` | {L1, L2, L3} | línea asignada al pedido P1 |
| `P2` | {L1, L2, L3} | línea asignada al pedido P2 |
| `P3` | {L1, L2, L3} | línea asignada al pedido P3 |
| `P4` | {L1, L2, L3} | línea asignada al pedido P4 |
| `P5` | {L1, L2, L3} | línea asignada al pedido P5 |
| `P6` | {L1, L2, L3} | línea asignada al pedido P6 |
| `P7` | {L1, L2, L3} | línea asignada al pedido P7 |
| `P8` | {L1, L2, L3} | línea asignada al pedido P8 |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | La suma de las duraciones de los pedidos asignados a una línea no puede superar las horas disponibles de esa línea. | `(P1=='L1')*4 + (P2=='L1')*3 + (P3=='L1')*2 + (P4=='L1')*5 + (P5=='L1')*3 + (P6=='L1')*2 + (P7=='L1')*1 + (P8=='L1')*2 <= 8` |
| R1b | La suma de las duraciones de los pedidos asignados a una línea no puede superar las horas disponibles de esa línea. | `(P1=='L2')*4 + (P2=='L2')*3 + (P3=='L2')*2 + (P4=='L2')*5 + (P5=='L2')*3 + (P6=='L2')*2 + (P7=='L2')*1 + (P8=='L2')*2 <= 8` |
| R1c | La suma de las duraciones de los pedidos asignados a una línea no puede superar las horas disponibles de esa línea. | `(P1=='L3')*4 + (P2=='L3')*3 + (P3=='L3')*2 + (P4=='L3')*5 + (P5=='L3')*3 + (P6=='L3')*2 + (P7=='L3')*1 + (P8=='L3')*2 <= 6` |
| R2a | L3 es una línea pequeña y no puede procesar pedidos de más de 3 horas. | `P1 != 'L3'` |
| R2b | L3 es una línea pequeña y no puede procesar pedidos de más de 3 horas. | `P4 != 'L3'` |
| R3 | P2 y P5 son del mismo cliente y deben producirse en la misma línea. | `P2 == P5` |
| R4a | Los envases para alimentos no pueden producirse en la misma línea que P7. | `P3 != P7` |
| R4b | Los envases para alimentos no pueden producirse en la misma línea que P7. | `P6 != P7` |
| R5 | Si P1 se asigna a L1, entonces P8 debe asignarse a L3. | `implies(P1 == 'L1', P8 == 'L3')` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `P1` | **L2** |
| `P2` | **L3** |
| `P3` | **L2** |
| `P4` | **L1** |
| `P5` | **L3** |
| `P6` | **L2** |
| `P7` | **L1** |
| `P8` | **L1** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `('L2' == 'L1') * 4 + ('L3' == 'L1') * 3 + ('L2' == 'L1') * 2 + ('L1' == 'L1') * 5 + ('L3' == 'L1') * 3 + ('L2' == 'L1') * 2 + ('L1' == 'L1') * 1 + ('L1' == 'L1') * 2 <= 8` | ✓ |
| R1b | `('L2' == 'L2') * 4 + ('L3' == 'L2') * 3 + ('L2' == 'L2') * 2 + ('L1' == 'L2') * 5 + ('L3' == 'L2') * 3 + ('L2' == 'L2') * 2 + ('L1' == 'L2') * 1 + ('L1' == 'L2') * 2 <= 8` | ✓ |
| R1c | `('L2' == 'L3') * 4 + ('L3' == 'L3') * 3 + ('L2' == 'L3') * 2 + ('L1' == 'L3') * 5 + ('L3' == 'L3') * 3 + ('L2' == 'L3') * 2 + ('L1' == 'L3') * 1 + ('L1' == 'L3') * 2 <= 6` | ✓ |
| R2a | `'L2' != 'L3'` | ✓ |
| R2b | `'L1' != 'L3'` | ✓ |
| R3 | `'L3' == 'L3'` | ✓ |
| R4a | `'L2' != 'L1'` | ✓ |
| R4b | `'L2' != 'L1'` | ✓ |
| R5 | `implies('L2' == 'L1', 'L1' == 'L3')` | ✓ |

**2. Unicidad — deducción manual:**

Las capacidades suman 22 h, igual que la demanda, así que todas las líneas quedan llenas. P1 y P4 no van en L3 (R2), y juntos suman 9 h > 8, así que uno va en L1 y el otro en L2. Si P1 = L1, por R5 P8 = L3, y el bloque P2 + P5 (6 h, R3) no cabe en ninguna línea (10, 11 y 8 h): contradicción. Por tanto P1 = L2 y P4 = L1. El bloque P2 + P5 solo cabe en L3, que queda llena. Quedan P3, P6, P7 y P8 (7 h) para L1 (3 h libres) y L2 (4 h libres). Con R4, la única forma de sumar 3 h en L1 sin juntar P7 con P3 o P6 es {P7, P8}, así que L2 = {P1, P3, P6}.

**Notas de la revisión manual (Diego Changotasig):** Comprobé las ocho duraciones y las capacidades 8, 8 y 6 horas. También revisé la asignación conjunta de P2 y P5, las incompatibilidades con P7 y la dirección de la condición: si P1 va a L1, P8 debe ir a L3.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

8 variables, dominios de tamaño 3 (espacio de búsqueda de 6,561 asignaciones), 5 reglas en lenguaje natural que se traducen en 9 restricciones atómicas, aridad máxima 8. Tipos de restricción: capacidad ponderada, condicional, exclusión (≠), igualdad (agrupación), unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 166 nodos para enumerarlas todas.

---

## D17 — Programación de turnos con habilidades y cobertura

**Área:** Turnos de trabajo · **Dificultad:** Difícil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una planta química opera en tres turnos: mañana, tarde y noche. Ocho técnicos deben asignarse cada uno a exactamente un turno: Andrés, Beatriz, Carlos, Diana, Esteban, Fabiola, Gabriel y Helena. Andrés y Beatriz son supervisores; Carlos, Fabiola y Helena son los únicos electricistas.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `ANDRES` | {MANANA, TARDE, NOCHE} | turno de Andres |
| `BEATRIZ` | {MANANA, TARDE, NOCHE} | turno de Beatriz |
| `CARLOS` | {MANANA, TARDE, NOCHE} | turno de Carlos |
| `DIANA` | {MANANA, TARDE, NOCHE} | turno de Diana |
| `ESTEBAN` | {MANANA, TARDE, NOCHE} | turno de Esteban |
| `FABIOLA` | {MANANA, TARDE, NOCHE} | turno de Fabiola |
| `GABRIEL` | {MANANA, TARDE, NOCHE} | turno de Gabriel |
| `HELENA` | {MANANA, TARDE, NOCHE} | turno de Helena |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | La mañana y la tarde deben tener exactamente tres técnicos cada una, y la noche exactamente dos. | `count('MANANA', ANDRES, BEATRIZ, CARLOS, DIANA, ESTEBAN, FABIOLA, GABRIEL, HELENA) == 3` |
| R1b | La mañana y la tarde deben tener exactamente tres técnicos cada una, y la noche exactamente dos. | `count('TARDE', ANDRES, BEATRIZ, CARLOS, DIANA, ESTEBAN, FABIOLA, GABRIEL, HELENA) == 3` |
| R1c | La mañana y la tarde deben tener exactamente tres técnicos cada una, y la noche exactamente dos. | `count('NOCHE', ANDRES, BEATRIZ, CARLOS, DIANA, ESTEBAN, FABIOLA, GABRIEL, HELENA) == 2` |
| R2 | Cada turno debe tener exactamente un electricista. | `alldiff(CARLOS, FABIOLA, HELENA)` |
| R3 | Los dos supervisores no pueden estar en el mismo turno. | `ANDRES != BEATRIZ` |
| R4 | El turno de noche debe tener al menos un supervisor. | `count('NOCHE', ANDRES, BEATRIZ) >= 1` |
| R5 | Diana y Esteban comparten transporte y deben estar en el mismo turno. | `DIANA == ESTEBAN` |
| R6 | Gabriel tiene clases por la mañana y no puede trabajar en ese turno. | `GABRIEL != 'MANANA'` |
| R7 | Si Helena trabaja de noche, entonces Andrés también debe trabajar de noche. | `implies(HELENA == 'NOCHE', ANDRES == 'NOCHE')` |
| R8 | Fabiola no puede trabajar de noche. | `FABIOLA != 'NOCHE'` |
| R9 | Beatriz no puede trabajar en la tarde. | `BEATRIZ != 'TARDE'` |
| R10 | Fabiola está capacitando a Diana, así que ambas deben estar en el mismo turno. | `FABIOLA == DIANA` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `ANDRES` | **TARDE** |
| `BEATRIZ` | **NOCHE** |
| `CARLOS` | **NOCHE** |
| `DIANA` | **MANANA** |
| `ESTEBAN` | **MANANA** |
| `FABIOLA` | **MANANA** |
| `GABRIEL` | **TARDE** |
| `HELENA` | **TARDE** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `count('MANANA', 'TARDE', 'NOCHE', 'NOCHE', 'MANANA', 'MANANA', 'MANANA', 'TARDE', 'TARDE') == 3` | ✓ |
| R1b | `count('TARDE', 'TARDE', 'NOCHE', 'NOCHE', 'MANANA', 'MANANA', 'MANANA', 'TARDE', 'TARDE') == 3` | ✓ |
| R1c | `count('NOCHE', 'TARDE', 'NOCHE', 'NOCHE', 'MANANA', 'MANANA', 'MANANA', 'TARDE', 'TARDE') == 2` | ✓ |
| R2 | `alldiff('NOCHE', 'MANANA', 'TARDE')` | ✓ |
| R3 | `'TARDE' != 'NOCHE'` | ✓ |
| R4 | `count('NOCHE', 'TARDE', 'NOCHE') >= 1` | ✓ |
| R5 | `'MANANA' == 'MANANA'` | ✓ |
| R6 | `'TARDE' != 'MANANA'` | ✓ |
| R7 | `implies('TARDE' == 'NOCHE', 'TARDE' == 'NOCHE')` | ✓ |
| R8 | `'MANANA' != 'NOCHE'` | ✓ |
| R9 | `'NOCHE' != 'TARDE'` | ✓ |
| R10 | `'MANANA' == 'MANANA'` | ✓ |

**2. Unicidad — deducción manual:**

Por R5 y R10, FABIOLA = DIANA = ESTEBAN, que forman un turno completo de 3 y no de noche (R8). Si fuera la TARDE, GABRIEL (≠ MAÑANA) iría a la NOCHE, que además necesitaría un electricista (R2) y un supervisor (R4): serían 3 personas > 2. Entonces el trío está en la MAÑANA. Si HELENA = NOCHE, por R7 ANDRES = NOCHE y BEATRIZ (≠ ANDRES, ≠ TARDE) iría a la MAÑANA, que ya está llena. Entonces CARLOS = NOCHE y HELENA = TARDE. La NOCHE necesita un supervisor; BEATRIZ no puede ir a la TARDE ni a la MAÑANA (llena), así que BEATRIZ = NOCHE. ANDRES y GABRIEL completan la TARDE.

**Notas de la revisión manual (Diego Changotasig):** Revisé la cobertura exacta de 3, 3 y 2 técnicos, un electricista por turno y la presencia de un supervisor nocturno. También comprobé las igualdades, disponibilidades y la condición que se activa si Helena trabaja de noche.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

8 variables, dominios de tamaño 3 (espacio de búsqueda de 6,561 asignaciones), 10 reglas en lenguaje natural que se traducen en 12 restricciones atómicas, aridad máxima 8. Tipos de restricción: condicional, conteo/cobertura, exclusión (≠), igualdad (agrupación), todos-distintos, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 34 nodos para enumerarlas todas.

---

## D18 — Plan semanal de mantenimiento de equipos

**Área:** Mantenimiento · **Dificultad:** Difícil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Un taller de manufactura debe programar el mantenimiento de siete equipos en una semana laboral de cinco días (día 1 = lunes, ..., día 5 = viernes): dos tornos de la línea A (TORNO1 y TORNO2), dos fresadoras de la línea B (FRESA1 y FRESA2), una prensa, un compresor y un puente grúa. Cada equipo se atiende completo en un solo día.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `TORNO1` | {1, 2, 3, 4, 5} | día de mantenimiento de TORNO1 |
| `TORNO2` | {1, 2, 3, 4, 5} | día de mantenimiento de TORNO2 |
| `FRESA1` | {1, 2, 3, 4, 5} | día de mantenimiento de FRESA1 |
| `FRESA2` | {1, 2, 3, 4, 5} | día de mantenimiento de FRESA2 |
| `PRENSA` | {1, 2, 3, 4, 5} | día de mantenimiento de PRENSA |
| `COMPRESOR` | {1, 2, 3, 4, 5} | día de mantenimiento de COMPRESOR |
| `GRUA` | {1, 2, 3, 4, 5} | día de mantenimiento de GRUA |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Se pueden atender como máximo dos equipos por día. | `count(1, TORNO1, TORNO2, FRESA1, FRESA2, PRENSA, COMPRESOR, GRUA) <= 2` |
| R1b | Se pueden atender como máximo dos equipos por día. | `count(2, TORNO1, TORNO2, FRESA1, FRESA2, PRENSA, COMPRESOR, GRUA) <= 2` |
| R1c | Se pueden atender como máximo dos equipos por día. | `count(3, TORNO1, TORNO2, FRESA1, FRESA2, PRENSA, COMPRESOR, GRUA) <= 2` |
| R1d | Se pueden atender como máximo dos equipos por día. | `count(4, TORNO1, TORNO2, FRESA1, FRESA2, PRENSA, COMPRESOR, GRUA) <= 2` |
| R1e | Se pueden atender como máximo dos equipos por día. | `count(5, TORNO1, TORNO2, FRESA1, FRESA2, PRENSA, COMPRESOR, GRUA) <= 2` |
| R2a | El lunes (día 1) y el miércoles (día 3) hay capacitación del personal, así que esos días se atiende como máximo un equipo. | `count(1, TORNO1, TORNO2, FRESA1, FRESA2, PRENSA, COMPRESOR, GRUA) <= 1` |
| R2b | El lunes (día 1) y el miércoles (día 3) hay capacitación del personal, así que esos días se atiende como máximo un equipo. | `count(3, TORNO1, TORNO2, FRESA1, FRESA2, PRENSA, COMPRESOR, GRUA) <= 1` |
| R3a | Para no detener una línea completa, dos equipos de la misma línea no pueden atenderse el mismo día. | `TORNO1 != TORNO2` |
| R3b | Para no detener una línea completa, dos equipos de la misma línea no pueden atenderse el mismo día. | `FRESA1 != FRESA2` |
| R4 | La prensa se desmonta con el puente grúa recién revisado, así que la prensa se atiende exactamente el día siguiente al de la grúa. | `PRENSA == GRUA + 1` |
| R5a | La prensa fabrica los bujes de repuesto de los tornos, así que ambos tornos se atienden en días posteriores al de la prensa. | `TORNO1 > PRENSA` |
| R5b | La prensa fabrica los bujes de repuesto de los tornos, así que ambos tornos se atienden en días posteriores al de la prensa. | `TORNO2 > PRENSA` |
| R6 | Los dos tornos usan el mismo kit de repuestos y se atienden en días consecutivos, primero TORNO1 y luego TORNO2. | `TORNO2 == TORNO1 + 1` |
| R7a | Los tornos deben estar operativos el viernes, así que ninguno puede atenderse el día 5. | `TORNO1 != 5` |
| R7b | Los tornos deben estar operativos el viernes, así que ninguno puede atenderse el día 5. | `TORNO2 != 5` |
| R8a | Tornos y fresadoras los atiende el mismo mecánico, así que ninguna fresadora puede atenderse el mismo día que un torno. | `FRESA1 != TORNO1` |
| R8b | Tornos y fresadoras los atiende el mismo mecánico, así que ninguna fresadora puede atenderse el mismo día que un torno. | `FRESA1 != TORNO2` |
| R8c | Tornos y fresadoras los atiende el mismo mecánico, así que ninguna fresadora puede atenderse el mismo día que un torno. | `FRESA2 != TORNO1` |
| R8d | Tornos y fresadoras los atiende el mismo mecánico, así que ninguna fresadora puede atenderse el mismo día que un torno. | `FRESA2 != TORNO2` |
| R9a | Las fresadoras se prueban con aire comprimido, así que ninguna puede atenderse el mismo día que el compresor. | `FRESA1 != COMPRESOR` |
| R9b | Las fresadoras se prueban con aire comprimido, así que ninguna puede atenderse el mismo día que el compresor. | `FRESA2 != COMPRESOR` |
| R10 | El compresor y la prensa usan al mismo electricista, así que no pueden atenderse el mismo día. | `COMPRESOR != PRENSA` |
| R11 | FRESA1 es la de mayor uso y debe atenderse antes que FRESA2. | `FRESA1 < FRESA2` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `TORNO1` | **3** |
| `TORNO2` | **4** |
| `FRESA1` | **2** |
| `FRESA2` | **5** |
| `PRENSA` | **2** |
| `COMPRESOR` | **4** |
| `GRUA` | **1** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `count(1, 3, 4, 2, 5, 2, 4, 1) <= 2` | ✓ |
| R1b | `count(2, 3, 4, 2, 5, 2, 4, 1) <= 2` | ✓ |
| R1c | `count(3, 3, 4, 2, 5, 2, 4, 1) <= 2` | ✓ |
| R1d | `count(4, 3, 4, 2, 5, 2, 4, 1) <= 2` | ✓ |
| R1e | `count(5, 3, 4, 2, 5, 2, 4, 1) <= 2` | ✓ |
| R2a | `count(1, 3, 4, 2, 5, 2, 4, 1) <= 1` | ✓ |
| R2b | `count(3, 3, 4, 2, 5, 2, 4, 1) <= 1` | ✓ |
| R3a | `3 != 4` | ✓ |
| R3b | `2 != 5` | ✓ |
| R4 | `2 == 1 + 1` | ✓ |
| R5a | `3 > 2` | ✓ |
| R5b | `4 > 2` | ✓ |
| R6 | `4 == 3 + 1` | ✓ |
| R7a | `3 != 5` | ✓ |
| R7b | `4 != 5` | ✓ |
| R8a | `2 != 3` | ✓ |
| R8b | `2 != 4` | ✓ |
| R8c | `5 != 3` | ✓ |
| R8d | `5 != 4` | ✓ |
| R9a | `2 != 4` | ✓ |
| R9b | `5 != 4` | ✓ |
| R10 | `4 != 2` | ✓ |
| R11 | `2 < 5` | ✓ |

**2. Unicidad — deducción manual:**

Por R6 y R7, TORNO2 = TORNO1 + 1 ≤ 4, así que TORNO1 ≤ 3. Por R5, PRENSA < TORNO1, así que PRENSA ≤ 2, y por R4 PRENSA = GRUA + 1 ≥ 2. Entonces PRENSA = 2, GRUA = 1, TORNO1 = 3 y TORNO2 = 4. Los días 1 y 3 ya tienen su único cupo (R2). Las fresadoras no pueden ir en los días 3 y 4 (R8) ni en el día 1 (lleno), así que van en {2, 5}, y por R11 FRESA1 = 2 y FRESA2 = 5. El COMPRESOR no puede ir en los días 2 ni 5 (R9, R10) ni en los días 1 ni 3 (llenos), así que COMPRESOR = 4.

**Notas de la revisión manual (Diego Changotasig):** Comprobé el máximo de dos equipos diarios, la excepción de un equipo en los días 1 y 3, las precedencias y las restricciones de personal compartido. También revisé que los tornos sean consecutivos y no se programen el día 5.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

7 variables, dominios de tamaño 5 (espacio de búsqueda de 78,125 asignaciones), 11 reglas en lenguaje natural que se traducen en 23 restricciones atómicas, aridad máxima 7. Tipos de restricción: conteo/cobertura, exclusión (≠), igualdad (agrupación), precedencia/orden, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 11 nodos para enumerarlas todas.

---

## D19 — Plan maestro de producción por semanas

**Área:** Producción · **Dificultad:** Difícil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Una fábrica de muebles debe programar nueve lotes (L1 a L9) en las próximas tres semanas (semanas 1, 2 y 3). Cada lote se produce completo en una sola semana. Horas requeridas: L1 = 10, L2 = 8, L3 = 12, L4 = 6, L5 = 10, L6 = 8, L7 = 14, L8 = 6 y L9 = 6. La planta dispone de 30 horas por semana. L1 fabrica los componentes que luego se ensamblan en L5. L2 y L6 pertenecen a la misma familia de productos (mismo acabado).

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `L1` | {1, 2, 3} | semana en que se produce el lote L1 |
| `L2` | {1, 2, 3} | semana en que se produce el lote L2 |
| `L3` | {1, 2, 3} | semana en que se produce el lote L3 |
| `L4` | {1, 2, 3} | semana en que se produce el lote L4 |
| `L5` | {1, 2, 3} | semana en que se produce el lote L5 |
| `L6` | {1, 2, 3} | semana en que se produce el lote L6 |
| `L7` | {1, 2, 3} | semana en que se produce el lote L7 |
| `L8` | {1, 2, 3} | semana en que se produce el lote L8 |
| `L9` | {1, 2, 3} | semana en que se produce el lote L9 |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Las horas totales de los lotes de una misma semana no pueden superar 30. | `(L1==1)*10 + (L2==1)*8 + (L3==1)*12 + (L4==1)*6 + (L5==1)*10 + (L6==1)*8 + (L7==1)*14 + (L8==1)*6 + (L9==1)*6 <= 30` |
| R1b | Las horas totales de los lotes de una misma semana no pueden superar 30. | `(L1==2)*10 + (L2==2)*8 + (L3==2)*12 + (L4==2)*6 + (L5==2)*10 + (L6==2)*8 + (L7==2)*14 + (L8==2)*6 + (L9==2)*6 <= 30` |
| R1c | Las horas totales de los lotes de una misma semana no pueden superar 30. | `(L1==3)*10 + (L2==3)*8 + (L3==3)*12 + (L4==3)*6 + (L5==3)*10 + (L6==3)*8 + (L7==3)*14 + (L8==3)*6 + (L9==3)*6 <= 30` |
| R2 | L3 debe entregarse al final de la semana 1. | `L3 == 1` |
| R3 | L7 debe entregarse a más tardar al final de la semana 2. | `L7 <= 2` |
| R4 | Los componentes de L1 deben producirse en una semana anterior a la del ensamble L5. | `L1 < L5` |
| R5 | L2 y L6 deben producirse en la misma semana para aprovechar la preparación del acabado. | `L2 == L6` |
| R6a | Por los cambios de formato, en cada semana se pueden producir como máximo cuatro lotes. | `count(1, L1, L2, L3, L4, L5, L6, L7, L8, L9) <= 4` |
| R6b | Por los cambios de formato, en cada semana se pueden producir como máximo cuatro lotes. | `count(2, L1, L2, L3, L4, L5, L6, L7, L8, L9) <= 4` |
| R6c | Por los cambios de formato, en cada semana se pueden producir como máximo cuatro lotes. | `count(3, L1, L2, L3, L4, L5, L6, L7, L8, L9) <= 4` |
| R7 | L8 usa los moldes que se fabrican en L4, así que L4 debe producirse en una semana anterior a la de L8. | `L4 < L8` |
| R8 | L9 es la versión de exportación de L4 y debe producirse en la misma semana que L4. | `L9 == L4` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `L1` | **2** |
| `L2` | **3** |
| `L3` | **1** |
| `L4` | **1** |
| `L5` | **3** |
| `L6` | **3** |
| `L7` | **2** |
| `L8` | **2** |
| `L9` | **1** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `(2 == 1) * 10 + (3 == 1) * 8 + (1 == 1) * 12 + (1 == 1) * 6 + (3 == 1) * 10 + (3 == 1) * 8 + (2 == 1) * 14 + (2 == 1) * 6 + (1 == 1) * 6 <= 30` | ✓ |
| R1b | `(2 == 2) * 10 + (3 == 2) * 8 + (1 == 2) * 12 + (1 == 2) * 6 + (3 == 2) * 10 + (3 == 2) * 8 + (2 == 2) * 14 + (2 == 2) * 6 + (1 == 2) * 6 <= 30` | ✓ |
| R1c | `(2 == 3) * 10 + (3 == 3) * 8 + (1 == 3) * 12 + (1 == 3) * 6 + (3 == 3) * 10 + (3 == 3) * 8 + (2 == 3) * 14 + (2 == 3) * 6 + (1 == 3) * 6 <= 30` | ✓ |
| R2 | `1 == 1` | ✓ |
| R3 | `2 <= 2` | ✓ |
| R4 | `2 < 3` | ✓ |
| R5 | `3 == 3` | ✓ |
| R6a | `count(1, 2, 3, 1, 1, 3, 3, 2, 2, 1) <= 4` | ✓ |
| R6b | `count(2, 2, 3, 1, 1, 3, 3, 2, 2, 1) <= 4` | ✓ |
| R6c | `count(3, 2, 3, 1, 1, 3, 3, 2, 2, 1) <= 4` | ✓ |
| R7 | `1 < 2` | ✓ |
| R8 | `1 == 1` | ✓ |

**2. Unicidad — deducción manual:**

Por R2, L3 = 1. Por R7 y R8, L4 = L9 < L8, así que L4 = L9 ∈ {1, 2}. Si L4 = L9 = 2, L8 = 3, y el par L2 = L6 (16 h) junto con L1 < L5 no cabe en ninguna asignación de capacidad (se prueban L7 = 1 y L7 = 2, y ambas fallan). Entonces L4 = L9 = 1, y la semana 1 queda con 24 h, donde ya no cabe L7 (14 h). Así L7 = 2. L1 no cabe en la semana 1, y por R4 L1 < L5, así que L1 = 2 y L5 = 3. El par L2 = L6 (16 h) no cabe en la semana 2 (24 + 16), así que va en la semana 3 (10 + 16 = 26). L8 (6 h) no cabe en la semana 3 (32), así que L8 = 2 (30 h). Ninguna semana pasa de 4 lotes (R6).

**Notas de la revisión manual (Diego Changotasig):** Revisé las horas de los nueve lotes, el límite de 30 horas y cuatro lotes por semana. También comprobé que 'a más tardar la semana 2' sea <= 2 y que las reglas de precedencia y producción conjunta estén completas.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

9 variables, dominios de tamaño 3 (espacio de búsqueda de 19,683 asignaciones), 8 reglas en lenguaje natural que se traducen en 12 restricciones atómicas, aridad máxima 9. Tipos de restricción: capacidad ponderada, conteo/cobertura, igualdad (agrupación), precedencia/orden, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 50 nodos para enumerarlas todas.

---

## D20 — Programación de ventanas en un centro de cross-docking

**Área:** Logística · **Dificultad:** Difícil · **Estado de revisión manual:** OK (Diego Changotasig)

### Contexto industrial

Un centro de cross-docking tiene dos muelles y cuatro ventanas horarias consecutivas (1, 2, 3 y 4). Ocho camiones, T1 a T8, deben recibir cada uno una ventana. T1 y T2 son refrigerados. T3 trae componentes que luego recoge T6. T4 y T5 se transfieren carga directamente de uno a otro.

### Variables y dominios

| Variable | Dominio | Significado |
|---|---|---|
| `T1` | {1, 2, 3, 4} | ventana horaria del camión T1 |
| `T2` | {1, 2, 3, 4} | ventana horaria del camión T2 |
| `T3` | {1, 2, 3, 4} | ventana horaria del camión T3 |
| `T4` | {1, 2, 3, 4} | ventana horaria del camión T4 |
| `T5` | {1, 2, 3, 4} | ventana horaria del camión T5 |
| `T6` | {1, 2, 3, 4} | ventana horaria del camión T6 |
| `T7` | {1, 2, 3, 4} | ventana horaria del camión T7 |
| `T8` | {1, 2, 3, 4} | ventana horaria del camión T8 |

### Restricciones

| ID | Regla del enunciado | Expresión |
|---|---|---|
| R1a | Como hay dos muelles, en cada ventana pueden atenderse como máximo dos camiones. | `count(1, T1, T2, T3, T4, T5, T6, T7, T8) <= 2` |
| R1b | Como hay dos muelles, en cada ventana pueden atenderse como máximo dos camiones. | `count(2, T1, T2, T3, T4, T5, T6, T7, T8) <= 2` |
| R1c | Como hay dos muelles, en cada ventana pueden atenderse como máximo dos camiones. | `count(3, T1, T2, T3, T4, T5, T6, T7, T8) <= 2` |
| R1d | Como hay dos muelles, en cada ventana pueden atenderse como máximo dos camiones. | `count(4, T1, T2, T3, T4, T5, T6, T7, T8) <= 2` |
| R2a | Los camiones refrigerados deben atenderse en las ventanas 1 o 2. | `T1 <= 2` |
| R2b | Los camiones refrigerados deben atenderse en las ventanas 1 o 2. | `T2 <= 2` |
| R3 | T6 recoge lo que trae T3, así que T6 debe atenderse en una ventana posterior a la de T3. | `T3 < T6` |
| R4 | T4 y T5 deben atenderse en la misma ventana para hacer la transferencia directa. | `T4 == T5` |
| R5 | T7 llega desde otra ciudad y solo puede atenderse en las ventanas 3 o 4. | `T7 >= 3` |
| R6 | Si T8 se atiende en la ventana 1, entonces T2 debe atenderse en la ventana 2. | `implies(T8 == 1, T2 == 2)` |
| R7 | Los dos refrigerados no pueden atenderse en la misma ventana, porque solo hay una toma de frío. | `T1 != T2` |
| R8 | T6 debe atenderse exactamente en la ventana siguiente a la de T3, para que la mercadería no espere en el andén. | `T6 == T3 + 1` |
| R9 | T8 debe atenderse en una ventana anterior a la de T7. | `T8 < T7` |

### Solución propuesta (ground truth)

| Variable | Valor |
|---|---|
| `T1` | **1** |
| `T2` | **2** |
| `T3` | **2** |
| `T4` | **4** |
| `T5` | **4** |
| `T6` | **3** |
| `T7` | **3** |
| `T8` | **1** |

### Cómo verificarla

**1. Validez — sustituir la solución en cada restricción** (todas deben ser verdaderas):

| ID | Con los valores sustituidos | ¿Se cumple? |
|---|---|---|
| R1a | `count(1, 1, 2, 2, 4, 4, 3, 3, 1) <= 2` | ✓ |
| R1b | `count(2, 1, 2, 2, 4, 4, 3, 3, 1) <= 2` | ✓ |
| R1c | `count(3, 1, 2, 2, 4, 4, 3, 3, 1) <= 2` | ✓ |
| R1d | `count(4, 1, 2, 2, 4, 4, 3, 3, 1) <= 2` | ✓ |
| R2a | `1 <= 2` | ✓ |
| R2b | `2 <= 2` | ✓ |
| R3 | `2 < 3` | ✓ |
| R4 | `4 == 4` | ✓ |
| R5 | `3 >= 3` | ✓ |
| R6 | `implies(1 == 1, 2 == 2)` | ✓ |
| R7 | `1 != 2` | ✓ |
| R8 | `3 == 2 + 1` | ✓ |
| R9 | `1 < 3` | ✓ |

**2. Unicidad — deducción manual:**

Hay 8 camiones y 4 ventanas de 2 cupos, así que cada ventana queda llena. Por R2 y R7, T1 y T2 ocupan un cupo de la ventana 1 y otro de la 2. El par T4 = T5 (R4) necesita una ventana completa, así que va en la 3 o la 4. Si T4 = T5 = 3, entonces T7 = 4 (R5), y T3, T6 y T8 ocupan un cupo en las ventanas 1, 2 y 4. T6 = T3 + 1 (R8) obliga a T3 = 1 y T6 = 2, con lo que T8 = 4, que no es < T7 (R9): contradicción. Entonces T4 = T5 = 4 y T7 = 3. Si T3 = 1 y T6 = 2, T8 = 3, que no es < 3: contradicción. Así T3 = 2, T6 = 3 y T8 = 1. Por R6, T2 = 2 y T1 = 1.

**Notas de la revisión manual (Diego Changotasig):** Comprobé los dos cupos por ventana, las ventanas permitidas para los refrigerados y para T7, y las relaciones entre los camiones. La condición sobre T8 y T2 está expresada como implicación, y T6 va exactamente una ventana después de T3.

**3. Unicidad — búsqueda exhaustiva:** `python code/verify_ground_truth.py` enumera todas las soluciones con dos métodos independientes (backtracking y fuerza bruta) y registra el resultado en `results/ground_truth_check.csv`.

### Justificación de la dificultad

8 variables, dominios de tamaño 4 (espacio de búsqueda de 65,536 asignaciones), 9 reglas en lenguaje natural que se traducen en 13 restricciones atómicas, aridad máxima 8. Tipos de restricción: condicional, conteo/cobertura, exclusión (≠), igualdad (agrupación), precedencia/orden, unaria (restricción de dominio). El solver de referencia (MRV + forward checking) exploró 67 nodos para enumerarlas todas.

---
