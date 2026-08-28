| Axis | sorted() | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 2/20 (10%) |
| Guarantee | Garantiza ordenar la lista de forma no decreciente en O(nlogn) para cualquier lista válida de entrada | No ofrece garantías; el rendimiento es estadístico y falló en las listas más largas |
| Cost | El costo temporal es O(nlogn) | Inferencia opaca de red neuronal (~120s en total) sin cota de complejidad demostrable. |
| Latency | 0.00s / 0.00s | 0.00s / 120.01s |
| Reproducibility | 1 respuesta única en 5 ejecuciones (100% determinista). | 3 respuestas distintas en 5 ejecuciones al variar la semilla estadística. |
| Scaling | 100% -> 100% -> 100% -> 100% | 40% -> 0% -> 0% -> 0% |
| Interpretability | Sí, el algoritmo clásico es trazable y matemáticamente verificable. | No, los pesos internos de la red son cajas negras que no explican la decisión |
| Failure mode | none observed | invalid=10, malformed=3, wrong-but-confident=5 |

### Where we may have been unfair

**TODO — this section is worth real credit. Address at least three:**

- Did both systems get the same information?

No exactamente. Al LLM le entregué una representación en formato de texto (string) de la lista, lo que lo obligó a procesar cognitivamente los caracteres, espacios y corchetes antes de siquiera analizar los números. En cambio, la función clásica `sorted()` recibió directamente una estructura de datos nativa de Python en memoria, lo que representa una ventaja técnica significativa a favor del algoritmo clásico.

- Did you tune one side's parameters but use a default prompt for the other?

Sí, dediqué un esfuerzo de ingeniería considerable diseñando instrucciones de formato específicas ("fenced code block") y probando iteraciones del prompt para que el LLM devolviera datos procesables. Por el contrario, a `sorted()` simplemente lo ejecuté con su comportamiento por defecto. Esto representa un sesgo, ya que intenté "ayudar" al modelo a ser evaluable, algo que el algoritmo clásico no necesitó.

- Would a larger model change the result — and can you know without running it?

Es casi seguro que un modelo de frontera superaría la caída abrupta de rendimiento (el "acantilado") que observé en las listas de tamaño 40 con el modelo local `qwen2.5:3b`. Sin embargo, sin ejecutarlo no puedo garantizar el resultado. A diferencia del enfoque clásico, ningún LLM cuenta con una prueba formal condicional que asegure el éxito en todas las instancias posibles .

### [Wk0] El LLM duplica e inventa elementos al intentar ordenar una lista
**Setup:** qwen2.5:3b, temp 0.0, "Reply with ONLY the sorted list..."

**Classical:** sorted() — correcto, O(n log n)

**LLM:** Inició ordenando algunos números, pero luego concatenó la lista original desordenada al final, duplicando los elementos (entregó 19 números en lugar de 10).
  Lista original: [479, 55, 711, 200, 750, 426, 950, 824, 707, 7]
  Respuesta LLM: [7, 200, 426, 479, 55, 707, 711, 750, 824, 950, 479, 55, 711, 750, 426, 950, 824, 707, 7]

**Category:** invalid

**Why it matters:** Si este sistema estuviera en producción en una base de datos o sistema de inventario, estaría duplicando registros de forma silenciosa. Un error de código tradicional haría que el programa colapsara (lo cual es fácil de detectar), pero el LLM devuelve datos corruptos con total seguridad, lo que envenenaría cualquier sistema posterior que consuma esta información asumiendo que es correcta.