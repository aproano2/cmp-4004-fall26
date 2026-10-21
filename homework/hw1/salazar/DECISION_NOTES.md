# Notas de decisiones — Salazar, Ochoa y Chano

Cada integrante agrega aquí las decisiones de su parte, con el porqué. Las de la base son estas.

## Instancias

Usamos los bancos del curso sin cambios: el 8-puzzle de week 3 (profundidades óptimas 4, 8, 12 y 16, verificadas por el profe con BFS exhaustivo) y las grillas de week 4 (5, 8, 12 y 16). Ambos tienen 10 instancias por nivel y semilla 20260807. No generamos instancias propias, para que nadie pueda pensar que elegimos un banco favorable a un lado. Es una limitación: los niveles los fijó el profe, no nosotros.

Las grillas del curso no tienen paredes. El validador igual las revisa, porque el enunciado lo pide, pero ningún camino puede fallar por una pared en este banco. Lo declaramos en la sección de honestidad.

## Motor instrumentado

El `search()` del curso no mide la frontera máxima ni el tiempo, y no tiene timeout. Por eso `code/motor.py` repite su bucle con esas métricas, sin modificar el original: el test de meta va al expandir, `expansions` cuenta lo mismo y el desempate es estable. `test_group.py` comprueba que nuestras expansiones y costos son idénticos a los del `search()` del curso en BFS, DFS y UCS.

A* es la misma búsqueda de grafo con prioridad `g + h` y conjunto de explorados. Con una heurística admisible pero no consistente, esa versión podría perder optimalidad. Misplaced y Manhattan son consistentes en el 8-puzzle, y Manhattan × MIN_COST lo es en la grilla, así que no afecta a las heurísticas admisibles. Con h × 3 la pérdida es justamente lo que medimos.

IDS es el de nuestra hw3: usa el conjunto del camino actual contra ciclos y `max_depth` de 60. Su "frontera máxima" es la profundidad máxima de la pila de recursión, porque IDS no tiene cola. Lo decimos así en el reporte para no comparar peras con manzanas.

## Timeout

Usamos 30 s por corrida (algoritmo × instancia). El reloj se revisa cada 256 expansiones, así que una corrida puede pasarse unos milisegundos. Un timeout se guarda como `status=timeout` con las expansiones hasta el corte, y no entra en las medianas de costo. En la prueba rápida, IDS se queda sin tiempo en la grilla de 16×16: busca la menor profundidad y, con costos no uniformes, el número de caminos simples crece demasiado.

## LLM

Usamos `qwen2.5:3b`, el modelo por defecto de `resources/setup.md`, con temperatura 0 y semilla 0 en la corrida principal. La caché del harness incluye la semilla en la clave. Las 5 llamadas de reproducibilidad se hacen sin caché, porque si no serían copias de la primera (como pasó en week 2).

## Análisis 1 y 4

Para el análisis 1 comparamos el costo de UCS con el de cada A* admisible (misplaced y Manhattan), instancia por instancia. A*-manhattan_x3 queda fuera porque no es admisible a propósito. Para mostrar a BFS elegimos, de forma automática, la grilla donde su sobrecosto relativo es mayor, y dibujamos los dos caminos. Así no escogemos a mano un ejemplo favorable.

Para b* usamos la definición de las slides de week 4: N son los nodos que A* **expandió** y d es la longitud de la solución. Lo resolvemos por bisección, igual que `effective_bf` del notebook. Incluimos a UCS como referencia sin heurística. En nuestra corrida de prueba, b* de UCS a profundidad 12 sale cerca de 1,7, menor que el ~2,8 típico de la tabla de las slides. La razón es que nuestro motor es búsqueda de grafo con conjunto de explorados, no búsqueda de árbol: no vuelve a expandir estados repetidos. Lo decimos en el reporte en vez de forzar el número de la tabla.

## Brazo con herramienta

El modelo recibe exactamente el mismo texto que el brazo puro, más la descripción de una herramienta `astar` que se llama con una línea de JSON. Ejecutamos nuestro A* sobre la grilla **que el modelo escribió** en la llamada, no sobre la instancia original. Si el modelo la copia mal, la herramienta resuelve otro problema; eso lo medimos con `tool_args_match`. Aceptamos la grilla como lista de filas o como texto con saltos de línea, porque es la misma información. Una grilla aplanada en una sola línea es ambigua y se devuelve como error a la herramienta. El modelo puede llamar a la herramienta hasta 2 veces.

En las pruebas con 4 grillas ya aparecieron los modos de falla que esperábamos. El modelo aplanó la grilla, la herramienta respondió con error y el modelo inventó un camino. También copió mal una grilla de 12×12. Y en una de 16×16 el modelo no terminó de responder en 300 s. Estos casos se cuentan; no se corrigen.

Subimos el timeout del cliente de 120 s a 300 s y registramos los errores del modelo como `llm_error`. El harness no limita la longitud de la respuesta y lo dejamos sin cambios, por eso no fijamos `num_predict`.

## Librerías

No usamos pandas. En la laptop de Daniel, el Control inteligente de aplicaciones de Windows bloquea sus DLL. Todo se hace con `csv` y `numpy`.

## Heurísticas y análisis 2 y 3

Para el 8-puzzle implementamos dos heurísticas admisibles. `h_misplaced` cuenta las fichas que no están en su posición objetivo, excluyendo el espacio vacío. `h_manhattan_puzzle` suma para cada ficha su distancia Manhattan hasta la posición objetivo, también excluyendo el vacío. No contamos el espacio vacío porque moverlo no representa una ficha adicional que necesariamente deba colocarse; incluirlo podría hacer que la estimación deje de ser una cota inferior del costo restante.

Para las grillas usamos distancia Manhattan multiplicada por `MIN_COST`. La distancia Manhattan estima el número mínimo de movimientos necesarios y `MIN_COST` representa el menor costo posible por movimiento. Así obtenemos una cota inferior del costo real y conservamos la admisibilidad.

En el análisis de dominancia comparamos A*-misplaced y A*-manhattan instancia por instancia en las 40 instancias del 8-puzzle. Manhattan tuvo un número de expansiones menor o igual que misplaced en las 40, sin excepciones. Esto es consistente con que Manhattan contiene más información: una ficha fuera de lugar aporta solamente 1 a misplaced, mientras Manhattan considera cuántos movimientos mínimos faltan para colocarla.

También evaluamos `A*-manhattan_x3`, que multiplica Manhattan por 3. Esta modificación se hizo deliberadamente para romper la admisibilidad y observar el intercambio entre eficiencia y calidad de solución. En las 80 instancias de ambos dominios, 20 produjeron una solución subóptima. El peor caso fue `8puzzle-16-07`: A*-manhattan obtuvo costo 16 con 99 expansiones, mientras x3 obtuvo costo 24 con 261 expansiones. Por tanto, inflar la heurística no garantiza una mejora: puede reducir expansiones en muchos casos, pero también puede producir soluciones de mayor costo e incluso expandir más nodos en ciertas instancias.

## Validador y brazo LLM

El validador recorre el camino paso a paso, clasifica en un orden fijo de categorías y lleva banderas separadas para las tres fallas. Tiene lectura estricta y tolerante, y una UCS de respaldo para grillas con paredes. Usa la interfaz del grupo (`validar(dominio, instancia, camino, costo)`), nuestros bancos y los costos del curso (`~` = 8). El óptimo sale de nuestro A* con Manhattan. Tiene las 7 pruebas de aceptación y 2 más sobre la lectura tolerante y las fallas combinadas.

La lectura estricta acepta exactamente lo que pide el prompt del curso: `PATH: <letras sin separadores>` y `COST: <entero>`. La columna `tolerant` registra cuándo hizo falta la lectura flexible. Si falta `PATH` o `COST`, la respuesta es `malformed`.

Para el 8-puzzle escribimos un prompt en inglés, con la misma estructura y el mismo formato de salida que el prompt del curso para la grilla, para que los dos dominios reciban instrucciones equivalentes. Lo escribimos antes de ver cualquier respuesta del modelo. El texto está en `prompt_puzzle()`.

Cuando una respuesta sale de la caché, `r.elapsed` vale 0. Para la latencia usamos el tiempo que la caché guardó cuando se generó la respuesta. Las 26 grillas del brazo con herramienta que se respondieron en la corrida interrumpida del 2 de octubre conservan su registro en `results/llm_calls_herramienta_corrida_parcial_2026-10-02.jsonl`.

## Medianas de la Parte 1

Las medianas de expansiones, frontera y tiempo se calculan solo sobre corridas resueltas. Un timeout detiene los contadores en un punto arbitrario y bajaba la mediana de IDS en 16×16. Los timeouts se cuentan en su propia columna (6, todos de IDS en grilla de 16×16).

## Respuestas que no terminan (`no_termina`)

A veces el modelo entra en un bucle y genera texto sin parar. En el log de Ollama vimos una respuesta que pasó de 2 500 tokens antes de cortarse. En ese caso Ollama corta la generación y devuelve un error HTTP 500, o la llamada pasa de los 300 s. Decidimos no ponerle un tope de tokens al modelo, porque eso cambiaría la configuración del harness del curso. Lo tratamos como lo que es: una **falla del modelo**, que el scorecard nombra en el eje 8 ("times out"). Se clasifica como `no_termina`, se cuenta por nivel y no se reintenta. Con temperatura 0, al repetir la llamada se repite el bucle, así que el resultado es reproducible. Solo un error de infraestructura (Ollama apagado o conexión rechazada) se registra como `llm_error` y se vuelve a correr. Estas respuestas no se guardan en la caché, porque el harness no guarda errores; quedan registradas en `results/llm_calls.jsonl`.

## Auditoría de las llamadas sin texto

En la corrida oficial, 34 de las 80 llamadas del brazo LLM terminaron sin texto. No las clasificamos a ciegas. `code/auditoria_ollama.py` cruza cada una con el log del servidor de Ollama, que registra cuántos tokens llevaba generados el modelo cuando se cortó la llamada. La regla se fijó antes de mirar los conteos:

- **Bucle del modelo** (`no_termina`): 2 000 tokens o más (más de 10 veces la respuesta normal más larga, de 188 tokens) y un corte que no fue instantáneo.
- **Infraestructura:** todo lo demás. Por ejemplo, un error que llegó en 1–2 s con 0 tokens, porque Ollama todavía estaba cancelando la respuesta en bucle de la llamada anterior. O una llamada que se cortó con pocos tokens mientras la GPU bajó de 135 a 14 tokens/s.

Resultado: 27 bucles confirmados (entre 2 300 y 40 000 tokens) y 7 fallas de infraestructura. Solo esas 7 instancias se volvieron a correr, con `--solo`. La evidencia queda en `results/auditoria_llm.csv` y `results/ollama_cortes_llm.txt`. Para evitar los cortes heredados, desde el brazo con herramienta esperamos 10 s después de cada error y registramos la hora de inicio y fin de cada llamada.

En algunos tramos de la noche la GPU de la laptop bajó de velocidad, probablemente por el ahorro de energía con la pantalla apagada. Eso infla las latencias de esas llamadas. Lo declaramos en la sección de honestidad.

## Reproducibilidad: dos instancias

En las asignaciones fijamos `grid-8-00` antes de correr nada, y la mantenemos como medición oficial. Con temperatura 0, el modelo entra en bucle las 5 veces, así que obtenemos "1 resultado distinto de 5", pero sin ningún camino que comparar. Como medición adicional, la repetimos en `grid-5-00`: la primera grilla del banco en la que el modelo sí devolvió una respuesta en la corrida principal. La regla es fija y la instancia no se eligió por su resultado. Reportamos las dos por separado.

## Corrección de la regla de auditoría (5 de octubre)

La primera regla, "bucle si hay 2 000 tokens o más", resultó incompleta. Repetimos en streaming las 15 llamadas cortadas con HTTP 500 que tenían tokens generados (`code/diagnostico_500.py`, `results/diagnostico_500.csv`). En 7 casos, Ollama respondió *"prediction aborted, token repeat limit reached"*: detiene al modelo cuando repite el mismo token, aunque lleve solo 100 tokens. En 5 casos el modelo seguía generando cuando cortamos a los 120 s. En 3 terminó normalmente esta vez, porque el modelo no es determinista.

La regla corregida es: **bucle del modelo** si la llamada se pasa de los 300 s o si Ollama corta con tokens ya generados; **infraestructura** solo si el corte llega con 0 tokens, es decir, cuando Ollama seguía cancelando la respuesta anterior. Con esta regla, la corrida principal tiene 30 bucles y 4 fallas de infraestructura. Las llamadas con hora registrada (reintentos, reproducibilidad y herramienta) son todas bucles.

Con la regla anterior habíamos repetido 3 llamadas del brazo LLM y 6 del brazo con herramienta que en realidad eran bucles. Repetir una falla del modelo le da una segunda oportunidad que los otros sistemas no tienen. Por eso `code/restaurar_primer_intento.py` deja como oficial el **primer intento**, reconstruido desde `results/llm_calls.jsonl`. Solo cambió una categoría: `grid-16-05` en la herramienta, que en el reintento dio una respuesta ilegal y queda como `no_termina`.

## Error de la herramienta en el 8-puzzle

En el 8-puzzle del curso, cada acción es la casilla a la que se mueve el blanco, no una letra. Nuestra herramienta respondía con un error en vez del camino. Lo detectamos al leer las primeras transcripciones, detuvimos la corrida, corregimos (`camino_en_letras`) y agregamos una prueba que exige que cada respuesta de la herramienta sea `correct` para el validador. Las llamadas afectadas están archivadas en `evidencia_descartada/2026-10-05_herramienta_8puzzle_con_error/`.

