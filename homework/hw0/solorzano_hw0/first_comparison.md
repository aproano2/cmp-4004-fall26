# Comparación: sorted() vs LLM

### Sección 6: Resultados

| Axis | sorted() | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 2/20 (10%) |
| Guarantee | Si hay garantia porque ordena todas las listas usando O(n log n) | No hay garantia porque solo puede ordenar listas de maximo 5 números |
| Cost | No hubo costo, no gasto casi nada de energia | Costo alto, si gasto bastante energia |
| Latency | 0.00s / 0.00s | 0.00s / 122.08s |
| Reproducibility | Siempre es identico, da la misma respuesta | Es variable, puede dar respuestas distintas según la temperatura |
| Scaling | 100% → 100% → 100% → 100% | 40% → 0% → 0% → 0% |
| Interpretability | Alta: Se puede ver el código de como ordeno | No se puede saber que "penso" la red neuronal en como ordenar|
| Failure mode | none observed | invalid=8, malformed=4, wrong-but-confident=6 |

### Where we may have been unfair

**TODO — this section is worth real credit. Address at least three:**

- **Did both systems get the same information?**

   Si, los dos recibieron la misma información. Pero sorted() recibio como una lista nativa, en cambio el LLM lo recibio como un texto.

- **Did you tune one side's parameters but use a default prompt for the other?**

   Si, sorted() no requiere configuración pero al LLM se le dio un prompt pero sin ejemplos.

- **Is your instance distribution accidentally favourable to one side?**

- **Did you count the time you spent writing the prompt? The heuristic?**

   No, solo medi el tiempo que demoro la ejecución.

- **Would a larger model change the result — and can you know without running it?**

   Se podria mejorar el prompt poniendo algunos ejemplos, aunque no se podria saber si podría funcionar pero sin ejecutar.



### Reading your own table

Whatever numbers you got, answer these four in your submission:

1. **Did the LLM's solve rate fall as the list got longer?** 

   Si, el modelo alcanzo un 40% de exito con las listas pequeñas (n=5). Pero con las listas de tamaño n=10, n=20 y n=40 bajo a un 0%.

2. **Which failure mode dominated?**

   El fallo que predominó fue `invalid` con 8 casos, el modelo pudo perder o inventar números de la lista original. Los otros fallos fueron `malformed` con 4 casos, donde la respuesta en texto rompió la estructura requerida y `wrong-but-confident` con 6 casos, donde conservó los números pero los ordenó mal. 

3. **What did each solved instance cost?** 

   Por el lado de `sorted()` resolvió cada caso casi al instante (0.00s). En cambio, el LLM tomó hasta 122.08s en el percentil 95 (p95), consumiendo muchos más recursos.

4. **Where might you have been unfair?**

   Se ejecutó en un modelo local pequeño (`qwen2.5:3b`) con un prompt directo pero sin ejemplos previos. Pedirle a un modelo ligero de 3B que ordene secuencias largas de números sin herramientas externas era de esperar que tuviera fallos al ordenar los números en comparación con un algoritmo matematico escrito para esa tarea.