# Duel 1 — Búsqueda clásica contra un LLM

**Equipo:** Daniel Salazar, Andretty Ochoa y Jalil Chano · CMP-4004 · USFQ

> Todas las cifras salen de `results/`, generadas por `code/`; ninguna se escribió a mano.
>
> **Aportes.** Andretty Ochoa: heurísticas, análisis 2 y 3 y la corrida oficial de la Parte 1. Jalil Chano: diseño del validador (recorrido, categorías y lectura tolerante), del brazo LLM y de la medición de reproducibilidad. Daniel Salazar: motor y benchmark, análisis 1 y 4, brazo con herramienta e integración. El uso de IA de cada uno está en `AI_LOG.md`.

## 1. Qué medimos y cómo

Comparamos tres sistemas sobre las mismas 80 instancias: los algoritmos clásicos (BFS, DFS, UCS, IDS y A*), un LLM local (`qwen2.5:3b` en Ollama, temperatura 0, semilla 0) y ese mismo LLM con nuestro A* como herramienta.

- **8-puzzle:** banco del curso (week 3), 10 instancias por profundidad óptima 4, 8, 12 y 16.
- **Grilla con terrenos:** banco del curso (week 4), 10 grillas de 5×5, 8×8, 12×12 y 16×16. El costo se cobra al entrar a la celda: `.` = 1, `,` = 3 y `~` = 8. Los dos bancos usan la semilla 20260807.
- **Motor:** el `search()` del curso, más frontera máxima, tiempo y un **timeout duro de 30 s por corrida** (reportado como timeout, nunca como "sin solución"). `test_group.py` comprueba que expande igual que el original.
- **Validación del LLM:** un validador propio. El modelo nunca juzga sus propias respuestas.

Reportamos medianas y rango intercuartil (IQR). La Parte 1 se midió en la laptop de Andretty (Intel) y los brazos LLM en la de Daniel (GPU RTX 5070 Ti).

## 2. The Duel Scorecard

| Eje | Clásico (A*-Manhattan) | LLM (`qwen2.5:3b`) | LLM + A* como herramienta | Evidencia |
|---|---|---|---|---|
| 1 Corrección | **80/80** óptimas | **0/80** | **17/80** | `results/scorecard.csv` |
| 2 Garantía | Costo mínimo **si** *h* es admisible (Manhattan: 0 sobreestimaciones en los 181 440 estados del 8-puzzle); nada sobre el tiempo. Con *h*×3 la garantía se pierde (20/80 subóptimas) | Ninguna: 0/80 aquí no dice nada sobre la instancia 81 | Óptimo **solo si** el modelo copia bien la instancia y la respuesta. Lo comprueba nuestro validador, no el sistema | §3.1, §4.3 |
| 3 Costo (mediana) | 23,5 expansiones | 204 tokens | 682 tokens + una búsqueda A* (23,5 expansiones de mediana) | `results/scorecard.csv` |
| 4 Latencia (mediana / p95) | 0,0004 s / 0,002 s | 8,4 s / 302 s | 9,0 s / 302 s | `results/*_respuestas.csv` |
| 5 Reproducibilidad (5 llamadas idénticas) | 1 resultado distinto | `grid-8-00`: 1 (5 bucles); `grid-5-00`: **3 distintos** con temperatura 0 | `grid-5-00`: 1 (la misma respuesta ilegal 5 veces) | `results/*reproducibilidad*.csv` |
| 6 Escalado | 100 % en los 4 tamaños | 0 % en todos; en la grilla, los bucles pasan de 2/10 a 10/10 | 8-puzzle: 10–50 %; grilla: 10–20 % y **0 %** en 16×16 | `fig/escalado_optimalidad.png` |
| 7 Interpretabilidad | Camino + costo, verificables | Texto sin justificación verificable; solo el camino se puede revisar | Camino de A*, verificable si se copió bien | — |
| 8 Modo de falla | Solo IDS hace timeout (6/40, todas en grilla 16×16); A* nunca | Ilegal y seguro de sí (45), no termina (32), mal formado (3) | No llama a la herramienta (21), copia mal la instancia (22) o la envía en un formato que no se puede leer (18) | `fig/fallas_llm.png` |

## 3. Parte 1: comparación clásica

### 3.0 Mediciones (nivel más difícil)

**8-puzzle, profundidad 16** (10 instancias; mediana [q1–q3] de las corridas resueltas)

| Algoritmo | Resueltas / timeouts | Costo | Longitud | Expansiones | Frontera máx. | Tiempo (ms) |
|---|---|---|---|---|---|---|
| BFS | 10 / 0 | 16 [16–16] | 16 [16–16] | 9 442 [8 486–10 056] | 5 652 [5 230–5 864] | 47,9 [42,0–51,9] |
| DFS | 10 / 0 | 24 835 [9 258–42 584] | 24 835 [9 258–42 584] | 25 284 [9 356–43 813] | 20 019 [7 467–34 049] | 121,8 [46,5–205,6] |
| UCS | 10 / 0 | 16 [16–16] | 16 [16–16] | 9 442 [8 486–10 056] | 5 652 [5 230–5 864] | 62,2 [58,0–73,6] |
| IDS | 10 / 0 | 16 [16–16] | 16 [16–16] | 25 064 [21 411–26 129] | 17 [17–17] | 147,2 [134,6–167,3] |
| A*-misplaced | 10 / 0 | 16 [16–16] | 16 [16–16] | 551 [519–627] | 365 [330–399] | 5,6 [4,5–5,9] |
| A*-manhattan | 10 / 0 | 16 [16–16] | 16 [16–16] | 128 [103–164] | 86 [72–111] | 2,0 [1,8–3,2] |
| A*-manhattan_x3 | 10 / 0 | 18 [16–20] | 18 [16–20] | 172 [100–231] | 112 [71–142] | 3,5 [2,0–4,2] |

**Grilla 16×16** (10 instancias; mediana [q1–q3] de las corridas resueltas)

| Algoritmo | Resueltas / timeouts | Costo | Longitud | Expansiones | Frontera máx. | Tiempo (ms) |
|---|---|---|---|---|---|---|
| BFS | 10 / 0 | 32 [28–44] | 16 [14–18] | 208 [196–220] | 38 [34–42] | 1,1 [1,0–1,3] |
| DFS | 10 / 0 | 321 [307–370] | 138 [119–160] | 138 [119–160] | 148 [130–168] | 0,7 [0,6–0,9] |
| UCS | 10 / 0 | 20 [18–24] | 17 [14–19] | 177 [156–204] | 86 [81–89] | 1,9 [1,1–2,5] |
| IDS | 4 / 6 | 28 [27–30] | 12 [12–14] | 225 347 [140 044–467 590] | 14 [13–14] | 2 556,0 [1 589,7–5 865,2] |
| A*-manhattan | 10 / 0 | 20 [18–24] | 17 [14–19] | 65 [46–73] | 70 [59–89] | 0,7 [0,6–0,8] |
| A*-manhattan_x3 | 10 / 0 | 22 [20–25] | 16 [14–18] | 18 [16–19] | 36 [30–40] | 0,2 [0,1–0,3] |

Los cuatro niveles están en `results/resumen_parte1.csv`.

### 3.1 Optimalidad: UCS = A*, y BFS cuando los costos no son uniformes

UCS y A* con heurística admisible (misplaced y Manhattan) devolvieron **el mismo costo en las 80 instancias** (`results/optimalidad.csv`). BFS también fue óptimo en las 40 instancias del 8-puzzle, pero solo porque ahí todo paso cuesta 1. En la grilla, con costos no uniformes, BFS devolvió un camino más caro que el óptimo en **33 de 40 instancias**, y el sobrecosto mediano crece con el tamaño: 2 en 5×5 y 15 en 16×16.

![Expansiones por nivel](fig/expansiones_vs_nivel.png)

**Conclusión de la figura:** en el 8-puzzle, BFS, UCS e IDS crecen en línea recta en escala logarítmica, es decir, de forma exponencial. A*-Manhattan expande unas 100 veces menos. En la grilla, IDS se dispara: en 16×16 hizo timeout en 6 de 10.

Elegimos el ejemplo de forma automática: la grilla con mayor sobrecosto relativo. En `grid-12-09`, BFS y UCS usan 11 pasos cada uno, pero el camino de BFS cuesta **32** porque cruza agua (`~`), y el de UCS cuesta **11**. Los dos caminos están dibujados en `results/bfs_suboptimo.md`. BFS minimiza pasos, no costo: su optimalidad depende de que los costos sean uniformes.

### 3.2 Dominancia de Manhattan sobre misplaced

Comparamos A*-misplaced y A*-manhattan en las 40 instancias del 8-puzzle. Manhattan expandió igual o menos nodos en **las 40**. Es lo esperado: las dos son admisibles, pero Manhattan mide cuántos movimientos le faltan a cada ficha, no solo si está fuera de lugar.

En la figura, cada punto es una instancia (misplaced en x, Manhattan en y): todos quedan sobre o bajo la diagonal y = x. En `8puzzle-16-00`, misplaced expandió 685 nodos y Manhattan 169. La garantía no depende del banco: en los **181 440 estados** del 8-puzzle, ninguna de las dos heurísticas sobreestima ni es inconsistente, y Manhattan domina a misplaced estado por estado (`results/admisibilidad_exhaustiva.csv`).

![Dominancia](fig/dominancia.png)

**Conclusión de la figura:** Manhattan nunca expandió más nodos que misplaced en las 40 instancias y su ventaja fue más evidente en los niveles difíciles.

### 3.3 Romper la admisibilidad: h × 3

También multiplicamos Manhattan por 3 para estudiar qué ocurre al usar una heurística deliberadamente no admisible. Comparamos A*-manhattan_x3 contra A*-manhattan en 80 instancias. Medimos el speedup como expansiones de Manhattan divididas para expansiones de x3, y de forma equivalente para segundos. Para la calidad usamos `costo_x3 / costo_óptimo`: 1 significa que se conservó la solución óptima y valores mayores que 1 indican pérdida de calidad.

| Dominio | Nivel | Speedup expansiones (mediana) | Speedup segundos (mediana) | Razón de costo (mediana) | Subóptimas |
|---|---:|---:|---:|---:|---:|
| 8-puzzle | 4 | 1,000 | 1,079 | 1,000 | 0/10 |
| 8-puzzle | 8 | 1,036 | 1,242 | 1,000 | 0/10 |
| 8-puzzle | 12 | 1,252 | 0,856 | 1,000 | 1/10 |
| 8-puzzle | 16 | 0,695 | 0,489 | 1,125 | 6/10 |
| grilla | 5 | 1,650 | 1,208 | 1,000 | 2/10 |
| grilla | 8 | 2,458 | 2,209 | 1,059 | 5/10 |
| grilla | 12 | 2,500 | 1,390 | 1,000 | 2/10 |
| grilla | 16 | 3,670 | 3,301 | 1,000 | 4/10 |

El efecto depende claramente del dominio. En la grilla, x3 redujo considerablemente las expansiones, llegando a un speedup mediano de 3,67× en nivel 16. En el 8-puzzle difícil ocurrió lo contrario: en nivel 16 el speedup mediano fue 0,695×, por lo que x3 expandió más nodos, y además perdió optimalidad con frecuencia. En total, 20 de las 80 instancias fueron subóptimas. El peor caso fue `8puzzle-16-07`: Manhattan encontró costo 16 con 99 expansiones, mientras x3 produjo costo 24 con 261 expansiones, una pérdida de costo del 50 %.

![Inflado x3](fig/inflado_x3.png)

**Conclusión de la figura:** inflar Manhattan puede acelerar considerablemente la búsqueda, especialmente en la grilla, pero no garantiza menos trabajo ni optimalidad; el intercambio entre velocidad y calidad depende del dominio y de la instancia.

### 3.4 Factor de ramificación efectivo b*

Resolvimos N + 1 = 1 + b* + … + (b*)^d por bisección, con N = nodos expandidos y d = longitud de la solución (`results/branching_resumen.csv`, `fig/branching.png`).

| 8-puzzle, profundidad | UCS | A*-misplaced | A*-manhattan |
|---|---:|---:|---:|
| 8 | 1,78 | 1,17 | 1,08 |
| 12 | 1,70 | 1,31 | 1,17 |
| 16 | 1,67 | 1,37 | 1,22 |

Manhattan tiene el b* más cercano a 1 en todos los niveles, de forma consistente con la dominancia de la sección 3.2. En la grilla, A*-manhattan queda entre 1,15 y 1,20 y UCS entre 1,25 y 1,36. Nuestros valores son menores que la tabla típica de las slides (~2,8 para UCS a d = 12) porque nuestro motor es búsqueda de grafo: no vuelve a expandir estados repetidos. No forzamos el número de la tabla.

![b*](fig/branching.png)

**Conclusión de la figura:** con mejor heurística, b* se acerca a 1, y la diferencia entre heurísticas se mantiene en todos los niveles.

## 4. Parte 2: el duelo

### 4.1 Brazo LLM: fallas por categoría y escalado

El validador es nuestro (`code/validador.py`, 9 pruebas). Camina el camino paso a paso, recalcula el costo y lo compara con el óptimo de nuestro A*. Nunca le preguntamos al modelo si su respuesta es correcta. Corrimos las 80 instancias con temperatura 0, semilla 0, sin reintentar ni corregir respuestas.

| | 8-puzzle 4 / 8 / 12 / 16 | Grilla 5 / 8 / 12 / 16 |
|---|---|---|
| ilegal | 9 / 9 / 5 / 9 | 8 / 4 / 1 / 0 |
| subóptima / costo mal reportado | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| mal formada | 0 / 0 / 0 / 0 | 0 / 1 / 2 / 0 |
| no termina | 1 / 1 / 5 / 1 | 2 / 5 / 7 / 10 |
| **correcta** | **0 / 0 / 0 / 0** | **0 / 0 / 0 / 0** |

El modelo nunca llegó a ser subóptimo ni a reportar mal el costo, porque ni siquiera produjo caminos legales. En el 8-puzzle, 31 de sus 32 caminos ilegales sacan el blanco del tablero. En la grilla aparece el "cliff" del scorecard en otra forma: las respuestas que no terminan pasan de 2/10 en 5×5 a 10/10 en 16×16. Dos respuestas solo se pudieron leer con la lectura tolerante.

"No termina" no es un error de nuestra infraestructura. Repetimos en streaming las 15 llamadas cortadas con HTTP 500 (`results/diagnostico_500.csv`). En 7, Ollama devolvió *"token repeat limit reached"*: el modelo repetía `. . . .` sin parar. En 5 seguía generando a los 120 s, y solo 3 terminaron esta vez (el modelo no es determinista, ver 4.2). Cruzamos cada llamada sin texto con el log de Ollama (`results/auditoria_*.csv`). Solo 4 se cortaron sin haber generado ningún token; esas fueron fallas de infraestructura y se repitieron.

![Escalado](fig/escalado_optimalidad.png)

**Conclusión de la figura** (`fig/escalado_optimalidad.png`): A* se mantiene en 100 % en todos los tamaños y el LLM solo se queda en 0 %. Con 10 instancias por punto, la curva del LLM no puede ser peor.

### 4.2 Reproducibilidad

Hicimos 5 llamadas idénticas sin caché (con caché, las llamadas 2 a 5 serían copias de la primera). En `grid-8-00`, la instancia fijada de antemano, el modelo entró en bucle las 5 veces. Como eso no deja caminos que comparar, repetimos la medición en `grid-5-00`, la primera grilla con respuesta. Ahí, **con temperatura 0 y la misma semilla, salieron 3 resultados distintos en 5 llamadas**, y ninguno coincide con la corrida principal. Con temperatura 0,7 y semillas 1 a 5 salieron 5 distintos de 5. A* dio el mismo camino las 5 veces, y el brazo con herramienta, la misma respuesta (ilegal) las 5 veces.

### 4.3 Brazo con herramienta

El modelo puede pedir nuestro A* con una línea de JSON. La herramienta resuelve la instancia **tal como el modelo la escribió** y devuelve el camino y el costo. Llegó a **17/80** correctas, frente a 0/80 del LLM solo:

| ¿Qué pasó con la llamada? | n | correctas |
|---|---|---|
| copió la instancia exacta | 19 | **16** |
| copió la instancia con errores | 22 | 1 |
| la envió en un formato que no se puede leer | 18 | 0 |
| no llamó a la herramienta (no terminó) | 21 | 0 |

Con el problema bien copiado, el resultado es casi siempre óptimo (16/19). El cuello de botella pasó a ser **transcribir la instancia**, y empeora con el tamaño: en 16×16 nunca lo logró. Es el patrón del curso: el LLM como *front-end* y el solver como dueño de la garantía.

![Fallas](fig/fallas_llm.png)

**Conclusión de la figura** (`fig/fallas_llm.png`): con la herramienta aparecen respuestas correctas en los tamaños pequeños. Las fallas ya no vienen de buscar, sino de copiar la instancia o de no terminar.

## 5. Where we may have been unfair

- **Heurísticas ajustadas contra prompt sin ajustar.** Usamos heurísticas conocidas y probadas (Manhattan), mientras que el modelo recibió un solo prompt por dominio, escrito una vez y nunca ajustado. Un prompt con ejemplos resueltos o con "piensa paso a paso" podría rendir distinto. No lo medimos.
- **Un modelo pequeño.** `qwen2.5:3b` es el modelo que recomienda el curso, pero un modelo grande podría comportarse muy distinto. Nuestra evidencia no dice nada sobre él.
- **Distribución de instancias.** Los bancos del curso son pequeños (grillas de hasta 16×16, profundidad 16 como máximo) y no tienen paredes. Favorecen a los algoritmos clásicos, que resuelven todo en milisegundos. Además, el validador revisa paredes que este banco nunca pone a prueba.
- **Tiempo de desarrollo.** No contamos las horas que nos tomó programar el motor, las heurísticas y el validador.
- **Máquinas distintas.** La Parte 1 se midió en una laptop Intel y los brazos LLM en una laptop con GPU. Las latencias de un sistema y otro no son comparables entre sí en términos absolutos.
- **Las respuestas que no terminan cuentan como falla.** Sin un tope de tokens, un bucle del modelo cuesta 300 s y se clasifica como `no_termina`. Con un tope, esas instancias seguirían fallando, pero mucho más rápido: la latencia del LLM que reportamos depende de esa decisión.

- **h × 3 no es un rival con las mismas garantías.** Inflar la heurística rompe la admisibilidad a propósito. Comparar solo expansiones sería injusto, por eso reportamos también la pérdida de calidad.

## 6. Lo que nuestra evidencia no permite afirmar

- **El modelo no "no sabe buscar".** Medimos un modelo de 3B, con un prompt por dominio y temperatura 0. 0/80 no dice nada de modelos más grandes, de otros prompts ni de grillas de 20×20.
- **No hay una tasa precisa.** Con 10 instancias por punto, 17/80 de la herramienta tiene un margen amplio. Una o dos respuestas más o menos por nivel son ruido.
- **La reproducibilidad no es general.** 3 resultados distintos en `grid-5-00` muestran que la temperatura 0 no garantiza la misma respuesta en nuestra máquina. No sabemos si en otra GPU pasaría igual.
- **La latencia del LLM depende de nosotros.** Su p95 de 302 s es nuestro límite de espera, y en algunos tramos la GPU bajó de velocidad.

- **La dominancia y el efecto de h × 3 son de este banco.** Observamos la dominancia en estas 40 instancias, no en cualquier problema. Y h × 3 no siempre ayuda: aceleró en la grilla, pero en el 8-puzzle de profundidad 16 expandió más y perdió optimalidad.
