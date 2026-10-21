# Registro de asistencia de IA — Duel 1

Formato de `referencias/resources/ai-policy.md`. Cada integrante agrega sus propias entradas. El LLM que es objeto del experimento (`qwen2.5:3b`) no va aquí; va en el reporte.

## Base del Duel 1 — estructura, motor instrumentado y asignaciones

**Quién:** Daniel Salazar.
**Herramienta:** Claude Code (Anthropic), trabajando en la carpeta local del repositorio de Daniel, 2 de octubre de 2026.

**Qué le pedí:** revisar a fondo el repositorio del profe y las ramas del equipo, proponer una base para el Duel 1, armarla y escribir asignaciones detalladas para Andretty y Jalil.

**Qué recibí:**
- La estructura de carpetas que exige la consigna, con nuestras convenciones de hw3 y hw5 (archivos del curso intactos, `SOURCE_MANIFEST.json`, `referencias/` y `DECISION_NOTES.md`).
- `code/motor.py`: el bucle de `search()` del curso con frontera máxima, tiempo, timeout y A*, más el IDS de nuestra hw3.
- `code/dominios.py`, `code/benchmark.py`, `code/estadistica.py` y `code/rutas.py`.
- `code/tests/test_group.py` (7 pruebas), los esqueletos con `TODO` y las pruebas de aceptación de cada parte (`test_heuristicas.py` y `test_validador.py`). Con Claude Code comprobé, usando una implementación de referencia que no guardé en el repo, que esas pruebas se pueden pasar.
- Las asignaciones del equipo (publicadas como issues en GitHub), una checklist de la rúbrica, el borrador de `REPORT.md` y este registro.

**Qué hice con eso:** usé Claude Code como herramienta de apoyo; las decisiones fueron mías. Revisé la estructura propuesta y las asignaciones, y las ajusté en los issues de GitHub para que los tres tuviéramos partes equivalentes y plazos justos. Pedí que todo quedara escrito con la voz del equipo, subí la base a la rama `hw1-salazarD` y preparé la guía en PDF para Andretty y Jalil.

**¿Lo entendí?** Sí. El test de meta va al **expandir** y no al generar, porque con costos no uniformes el primer camino generado hacia la meta puede no ser el más barato; UCS y A* solo garantizan el óptimo si la meta sale de la frontera con el menor costo. En IDS no hay cola, así que su "frontera" es la profundidad de la pila de recursión. Un timeout significa que la búsqueda se detuvo antes de terminar; no prueba que no haya solución, por eso lo reportamos aparte.

## Análisis 1 y 4 y brazo con herramienta

**Quién:** Daniel Salazar.
**Herramienta:** Claude Code (Anthropic), 2 de octubre de 2026.

**Qué le pedí:** desarrollar conmigo mi parte: el análisis de optimalidad (UCS = A* y BFS con costos no uniformes), el factor de ramificación efectivo b* y el brazo con herramienta.

**Qué recibí:** `code/analisis_optimalidad.py` (tablas, el informe de BFS dibujado, b* por bisección y su figura), una prueba de b* en `test_group.py` y `code/herramienta.py` (la llamada JSON, la ejecución de nuestro A* con los argumentos del modelo y el registro de cada llamada). Probamos el análisis con una corrida de benchmark hecha con heurísticas de prueba que no guardamos en el repo, porque las heurísticas oficiales son de Andretty. El brazo con herramienta lo probamos en 4 grillas con una caché aparte, para no mezclar esas pruebas con la evidencia.

**Qué hice con eso:** revisé el código y lo corrí con los datos oficiales de la Parte 1 cuando integramos las heurísticas. Elegí la regla para escoger el ejemplo de BFS (el mayor sobrecosto relativo, de forma automática) y decidí reportar nuestro b* aunque no coincida con la tabla de las slides.

**¿Lo entendí?** Sí. BFS minimiza el número de pasos, no el costo; con costos no uniformes, como el agua (`~` = 8), puede devolver un camino igual de corto pero mucho más caro. b* es el factor de ramificación que tendría un árbol uniforme de profundidad d con N+1 nodos; lo despejamos por bisección. Nuestro b* de UCS sale menor que el de las slides porque nuestro motor es búsqueda de grafo y no vuelve a expandir estados repetidos. En la herramienta, el modelo pasa la instancia en JSON y nuestro A* la resuelve tal como el modelo la escribió.


## Heurísticas, análisis 2 y 3 y figuras

**Quién:** Andretty Ochoa.  
**Herramienta:** ChatGPT (OpenAI), 4 de octubre de 2026.

**Qué le pedí:** acompañarme paso a paso en mi parte del Duel 1, incluyendo la implementación y revisión de las heurísticas para 8-puzzle y grid, la comparación entre misplaced y Manhattan, el experimento con Manhattan ×3, el procesamiento de las mediciones y la generación de las figuras requeridas. También lo usé para interpretar los resultados y preparar mis aportes al reporte y a las notas de decisiones.

**Qué recibí:**
- Apoyo para implementar y revisar `h_misplaced`, `h_manhattan_puzzle`, `h_manhattan_grid` e `inflar` en `code/heuristicas.py`.
- Apoyo para completar `code/analisis_heuristicas.py`, generando `resumen_parte1.csv`, `dominancia.csv`, `inflado_x3.csv` y las tres figuras de la Parte 1.
- Explicaciones sobre admisibilidad, dominancia, heurísticas infladas, speedup y pérdida de optimalidad.
- Ayuda para interpretar las mediciones oficiales y redactar mis secciones de `REPORT.md` y `DECISION_NOTES.md`.

**Qué hice con eso:** revisé el código antes de incorporarlo, ejecuté personalmente las pruebas de heurísticas y del grupo, corrí primero el benchmark rápido y después el benchmark completo de 520 mediciones. Verifiqué los resultados de dominancia y del experimento ×3 y regeneré los CSV y las figuras con los datos oficiales antes de usarlos en el reporte.

**¿Lo entendí?** Sí. Puedo explicar por qué misplaced y Manhattan excluyen el espacio vacío, por qué Manhattan es admisible, por qué Manhattan domina informativamente a misplaced, por qué multiplicar la heurística por 3 rompe la garantía de admisibilidad y cómo interpretar los speedups y la pérdida de calidad observada.

## Integración final: PR de Andretty, validador y brazo LLM

**Quién:** Daniel Salazar.
**Herramienta:** Claude Code (Anthropic), 4 de octubre de 2026.

**Qué le pedí:** revisar la parte de Andretty (PR #4) y el borrador que nos pasó Jalil, integrar lo que sirviera y dejar el deber funcionando completo en local.

**Qué recibí:** la revisión de ambos aportes (pruebas, reproducción de los análisis de Andretty y los ajustes necesarios para integrar las partes). Después, el merge local del PR #4, la corrección de las medianas para excluir timeouts, `validador.py` y `duelo_llm.py` reescritos sobre la lógica del borrador de Jalil y adaptados a nuestra interfaz, el prompt del 8-puzzle en inglés, la latencia real de las respuestas en caché y las corridas con Ollama.

**Qué hice con eso:** coordiné la integración de las tres partes y revisé los resultados finales. Tomé las decisiones del protocolo cuando hubo problemas: no ponerle un tope de tokens al modelo para respetar el harness del curso, contar los bucles del modelo como falla (`no_termina`), repetir solo las fallas reales del servidor y conservar las corridas descartadas como evidencia. También revisé el REPORT y el notebook. Claude Code fue una herramienta de apoyo para programar y redactar; el criterio y las decisiones fueron del equipo.

**¿Lo entendí?** Sí. Un validador propio es necesario porque el modelo no puede juzgar su propia respuesta: sería circular. `suboptimal` significa que el camino es legal pero más caro que el óptimo; `wrong_cost` significa que el camino es óptimo pero el costo que reporta el modelo está mal sumado. La reproducibilidad se mide sin caché porque, con caché, las llamadas 2 a 5 serían copias de la primera y no se mediría nada. También puedo explicar por qué un HTTP 500 de Ollama era el modelo repitiendo el mismo token y no una falla nuestra.

## Validador, brazo LLM y reproducibilidad

**Quién:** Jalil Chano.
**Herramienta:** Claude (Anthropic), 4 de octubre de 2026.

**Qué le pedí:** siguiendo mi issue (#2) y las indicaciones de Daniel en las asignaciones del equipo, le pedí ayuda para escribir el validador (recorrido del camino, categorías de falla, lectura estricta y tolerante), sus pruebas, el script del brazo LLM con la medición de reproducibilidad y las figuras, y un borrador de mis secciones del reporte.

**Qué recibí:** borradores de `validador.py`, `test_validador.py` y `duelo_llm.py`, y un esquema de las secciones 4.1 y 4.2.

**Qué hice con eso:** los revisé y se los entregué al equipo. Mi diseño se integró al repositorio con la interfaz común del grupo (mismos bancos, mismo motor A* para el óptimo y las pruebas de aceptación), y así se corrió con Ollama.

**¿Lo entendí?** Sí, en general. El validador tiene que ser nuestro porque, si el mismo modelo revisa su respuesta, puede repetir el mismo error y darla por buena: sería circular. Por eso el validador camina el camino paso a paso, suma el costo de cada celda a la que entra y lo compara con el óptimo de nuestro A*. Una respuesta es `suboptimal` cuando el camino es legal pero cuesta más que el óptimo, es decir, el modelo eligió mal la ruta. Es `wrong_cost` cuando el camino es óptimo pero el costo que escribió no coincide con la suma real: el modelo sumó mal. Para la reproducibilidad usamos `use_cache=False` porque, con la caché encendida, las llamadas 2 a 5 salen guardadas de la primera y siempre darían lo mismo, sin medir nada. Al hacerlo sin caché vimos que, incluso con temperatura 0, el modelo dio 3 respuestas distintas en 5 llamadas. Al principio no entendía por qué mi borrador tenía que usar el mismo formato de instancias y el mismo A* que el resto del grupo. Lo entendí al ver que, si cada parte usa sus propios datos, los resultados de los tres sistemas no se pueden comparar.

