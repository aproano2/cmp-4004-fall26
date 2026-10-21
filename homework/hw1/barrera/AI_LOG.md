Herramienta: Claude versión sonnet 4.6

## 1. Brazo con herramienta y su depuración (`code/duel.py`, `code/llm.py`)

**Qué pedimos:** Que el modelo pudiera llamar a mi A* con una llamada JSON, y
después que revisara por qué la corrida fallaba.
**Qué obtuvimos:** El protocolo completo: el modelo emite el JSON, el código corre
A* sobre los argumentos que el modelo escribió (no sobre la instancia real) y le
devuelve el resultado. Al correrlo, la IA leyó los transcripts y encontró tres
problemas: Ollama devolvía HTTP 500 y el script se detenía (agregó reintentos);
cada llamada tardaba unos 2,4 s por usar `localhost` en Windows (lo cambió a
`127.0.0.1`, bajó a unos 0,2 s); y el prompt pedía la llamada y la respuesta
final en el mismo mensaje, por lo que el modelo inventaba el resultado (separó
los dos pasos). Con el prompt anterior el brazo dio 13/80 y 0/80; con el final,
26/80.
**Qué hicimos con eso:** Se corrió code/duel.py tres veces en la laptop con Ollama y 
qwen2.5:3b. La primera se cortó con un error HTTP 500 y se le pasó la salida a la IA.
Después de cada corrección se volvió a correr el script y code/plots.py, y se borró la caché
de transcripts antes de la corrida limpia. 
**¿Lo entendimos?** Sí. La herramienta resuelve lo que el modelo escribe, no el problema real,
si copia mal una celda, A* devuelve el óptimo de otro problema. Por eso acertó 25/40 puzzles, 
que son 9 celdas, y solo 1/40 grids, que tienen 25 o más. Además entendí que no basta con copiar
bien, el modelo también tiene que llamar a la herramienta y repetir el resultado tal cual, y en 
la corrida fallaron los tres pasos. Lo que no tenía claro antes es que el híbrido no hereda la
garantía de A*, porque esa garantía vale solo para el problema que A* recibe.

## 2. Validador de respuestas del modelo (`code/validator.py`)

**Qué pedimos:** Pedimos un validador que pudiera comprobar las respuestas del modelo sin tener que preguntarle al mismo modelo si su respuesta era correcta.
**Qué obtuvimos:** Código que recorre el camino movimiento por movimiento, recalcula
el costo y lo compara con A*, con las tres categorías de falla del deber más
`no_answer` para respuestas ilegibles.
**Qué hicimos con eso:** Se revisó results/duel_runs.csv para ver cómo 
clasificó las respuestas del modelo. 
**¿Lo entendimos?** Sí. El validador nunca le pregunta al modelo si acertó, recorre el 
camino paso a paso y, si se sale del tablero o no termina en la meta, es ilegal. Si es
legal, recalcula el costo sumando el terreno de cada celda y lo compara con el de A*; 
si es mayor, es subóptimo; si es igual pero el modelo reportó otro número, es "costo mal". 
Entendimos que el orden importa, porque un camino ilegal no tiene costo que comparar. 
Las 80 respuestas del LLM solo fueron ilegales, y por eso las otras dos categorías 
quedaron en 0. Antes pensaba que bastaba con revisar si el costo que decía el modelo era el correcto.

## 3. A* y el análisis de heurísticas (`code/search.py`, `code/benchmark.py`)

**Qué pedimos:** A* instrumentado y los análisis de dominancia, h × 3 y b*.
**Qué obtuvimos:** A* que reabre estados (necesario para h × 3) y rompe empates de f
hacia la h menor. La IA señaló dos cosas que yo no había preguntado, la
dominancia solo está garantizada para nodos con f < C*, así que el conteo depende
del desempate; y en el 8-puzzle `3 × Manhattan` no fue más rápido a profundidad
16, y comprobó que no era por re-expansiones.
**Qué hicimos con eso:** Se leyó los resultados de dominancia y de h × 3 en el reporte y en los
CSV.
**¿Lo entendimos?** Sí. A* es óptimo solo si la heurística nunca sobreestima el costo real. 
Manhattan domina a fichas mal ubicadas porque da un valor mayor o igual sin pasarse, y por eso
expande menos nodos (92 contra 383 a profundidad 16). Al multiplicar h por 3 se rompe la admisibilidad,
en el grid fue el doble de rápido pero 18/40 respuestas dejaron de ser óptimas, y en el 8-puzzle ni 
siquiera fue más rápido. También entendí que el test de meta va al expandir el nodo y no al generarlo, 
y que BFS solo es óptimo cuando todos los pasos cuestan lo mismo. Lo que no sabía es que la dominancia 
depende del desempate cuando hay nodos con el mismo valor que el costo óptimo.

## 4. Generación de los CSV de resultados (`results/*.csv`)

**Qué pedimos:** Que las mediciones del deber quedaran guardadas en CSV, con los
datos crudos por corrida y los resúmenes con mediana e IQR.
**Qué obtuvimos:** La IA escribió el código que genera los nueve CSV y decidió qué
columnas lleva cada uno:

- `code/benchmark.py` genera los seis de la Parte 1: `classical_runs.csv` (una
  fila por instancia y algoritmo: costo, longitud, expansiones, frontera máxima,
  tiempo y estado), `classical_summary.csv` (mediana, cuartiles e IQR por nivel,
  con los timeouts contados aparte), `optimality_check.csv` (UCS contra A* contra
  BFS), `dominance.csv` (expansiones con cada heurística), `weighted_astar.csv`
  (h contra 3h) y `ebf.csv` (factor de ramificación efectivo).
- `code/duel.py` genera los tres de la Parte 2: `duel_runs.csv` (una fila por
  instancia y sistema, con la categoría que asigna el validador, latencia y
  tokens), `duel_summary.csv` (conteos por categoría, tasa de óptimos, latencia
  mediana y p95) y `repro.csv` (las cinco llamadas idénticas).

Los seis CSV de la Parte 1 salieron de una corrida que hizo la IA en su entorno.
Los tres de la Parte 2 salieron de la corrida que hizo en la laptop con
Ollama.
**Qué hicimos con eso:** Los seis CSV de la Parte 1 los usé tal como los generó la IA,
sin volver a correr benchmark.py. Los tres de la Parte 2 los generamos al correr duel.py
en la laptop.
**¿Lo entendimos?** Sí. classical_runs.csv tiene el dato crudo, una fila por instancia y algoritmo,
y classical_summary.csv lo resume con mediana e IQR sobre 10 instancias, porque una sola corrida
no es un resultado. Entendimos que se usa la mediana y no el promedio porque un caso extremo arrastra
el promedio, y que los timeouts se cuentan aparte porque una corrida cortada no tiene su número real
de expansiones. También que las expansiones salen iguales en cualquier máquina y el tiempo no.

## 5. Implementaciones base y resto del código

**Qué pedimos:** BFS, DFS, UCS, IDS y A* para los dos dominios, partiendo del
código de los studios de las semanas 3 y 4, más las figuras y los tests.
**Qué obtuvimos:** La IA tomó de los studios la interfaz `Problem`, el ciclo de
búsqueda con tres fronteras y la estructura de A*, y lo reescribió para agregar
las mediciones, el timeout e IDS con pila explícita. Escribió desde cero el
benchmark de maner esqueletica donde las partes más importantes nosotros tuvimos 
que escribir y otras que son por defecto ya las escribía(solamente ibamos llenando
de la manera que nosotros lo cosiderabamos), el cliente del modelo y las figuras.
**Qué hicimos con eso:** Corrimos los tests y el duelo en la laptop; revisamoslos resultados contra los CSV.
Además, nos ayudaba a mantenernos en hilo con los codigos que nosotros implementabamos para entender y
que salga la tarea de la mejor forma.
**¿Lo entendimos?** Si. Algunas partes de los codigos nos complicaba, pero nos daba pista de que usar
y como implementarla para evitar errores ya sea de sintaxis o en la hora de compilar. No nos perdíamos del hilo y eso fue vital para entender todo el trabajo. En las figuras, ya teniamos los datos hechos, por lo que le pedimos que
nos ayudara graficando porque no teniamos una herramienta adecuada para graficar las imágenes.