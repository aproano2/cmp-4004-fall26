# Week 0 — First Comparison
# Martin Cevallos

| Axis | sorted() | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 2/20 (10%) |
| Guarantee | Regresa los elementos de la entrada en orden | No hay garantía, ya que acerto 2/20 veces |
| Cost | Computación local | Usando qwen2.5:3b, que es un API gratuito |
| Latency | 0.00s / 0.00s | 0.00s / 120.01s |
| Reproducibility | Con la misma entrada devuelve la misma salida | Si esta en el cache, entonces exactamente lo mismo. Pero si la LLM genera de nuevo, los resultados pueden cambiar. |
| Scaling | 100% → 100% → 100% → 100% | 40% → 0% → 0% → 0% |
| Interpretability | Fácil de verificar revisando los elementos y el orden | Fácil de verificar revisando los elementos y el orden |
| Failure mode | none observed | invalid=7, malformed=5, wrong-but-confident=6 |

## Analysis

La implementación de 'sorted()' resolvió las 20 entradas correctamente, mientras que la LLM resolvió 2 de las 20 correctamente. A la hora de analizar la escalabilidad, 'sorted()' pude resolver al 100% cada entrada independientemente del tamaño. Mientras que la LLM tuvo un 40% de éxito con listas de 5 elementos, mientras que no pude resolver listas más grandes de 10, 20 y 40 elementos.

Al analizar las fallas de cada una, evidentemente 'sorted()' no presenta ya que completo con éxito cada prueba. No obstante, la LLM falló principalmente con "invalid" en 7 elementos, "wrong-but-confident" en 6 ocasiones y "malformed" en 5 ocasiones. Esto es importante analizar, ya que la forma de error podría ser de los valores de elementos la lista, pero no de orden o viceversa.

## Where we may have been unfair

Did both systems get the same information?
Ambos recibieron los mismos datos de números, no obstante, al usar 'sorted()', este recibió y trato las listas como números enteros. La LLM recibió la información como texto. Esto implica que la LLM tuvo que hacer más procesos, como generar texto y pasar por parsing y validation. Entonces los errores se pueden presentar no solamente a la hora de ordenar, pero errores de formato o traducción.

Is your instance distribution accidentally favourable to one side?
Esta comparación favorece al algoritmo 'sorted()' ya que esta específicamente diseñado para la tarea de ordenar. Mientras que la LLM en verdad esta diseñada para ser un modelo de lenguaje multipropósito.

Would a larger model change the result — and can you know without running it?
El modelo utilizad 'qwen2.5:3b' es relativamente pequeño, además de gratuito. Con un modelo más grande y poderoso se podría presentar un resultado distinto y un poco más favorable a dicho LLM. No obstante, sin realizar ese experimento realmente no se puede confirmar o negar que el resultado final cambiaría. Si tuviese que adivinar, pienso que el algoritmo 'sorted()' seguiría siendo más efectivo.