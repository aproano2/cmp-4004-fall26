Week 0 - First Comparison

Table 
| Axis | sorted() | LLM |
|---|---|---|
| Correctness | 20/20 (100%) | 2/20 (10%) |
| Guarantee | Siempre devuelve los elementos ordenados del input, para cualquier input válido. No falla | Si el output pasa el verifier entonces está correctamente ordenado, no hay garantía previa de que eso siempre funcione|
| Cost | Practicamente sin costo, no hace llamadas externas y se desarrolla en el CPU interno | Al hacer 20 llamadas, con 14.85s por cada intento, que serían 297 s en total, dividido para los 2 aciertos es 148.5s por resultado válido, lo que es un costo elevado comparado a sorted |
| Latency | 0.00s / 0.00s | 0.00s / 122.07s | 
| Reproducibility| 5/5 , deterministico porque para el mismo input da siempre el mismo output| 2 de 5 distintas a temperatura 0.0 |  
| Scaling | 100% → 100% → 100% → 100% | 40% → 0% → 0% → 0% |
| Interpretability | Si se puede verificar que O(n) da un output en orden creciente del input inicial  | Se debe comparar con un sorted O(n) |
| Failure mode | none observed | invalid=10, malformed=3, wrong-but-confident=5 |

*Aqui sale que fuera 0 en el LLM pero es porque habia un problema al correr el notebook mas de una vez se almaceno en el caché y no me dio un resultado real y tuve que poner uan funcion para poder calcular el costo real

### Where we may have been unfair. 

- Is your instance distribution accidentally favourable to one side? 
R: No fue accidentalmente favorable a un lado u otro, porque tuvieron el mismo input en cada instancia. Se debe reconocer que la asimetría existente se debe a que sorted() es un algoritmo que se ha ido perfeccionando a lo largo de muchos años, a diferencia  del LLM, que tuvo que resolver la tarea sin ajustes especificos. 
- Did you count the time you spent writing the prompt? The heuristic?
No, no fue contado en la tabla, pero es importante considerar el tiempo de trabaajo en el prompt y el parser, que es algo que sorted no necesitaba, porque la función no necesita algo extra para ejecutar esa tarea. Esto haría que el costo del LLM aumente.
- Would a larger model change the result — and can you know without running it?
Un modelo más grande probablemente pueda dar un resultado más favorable, debería ser un modelo con más parametros que nuestro modelo actual. Esto podría hacer que la tasa de éxito mejore pero debe ser probado, no se pueden hacer afirmaciones sin la respectiva prueba experimental. El reusltado que obtuvimos no debe generalizarse para todos los LLMs.



- Did the LLM's solve rate fall as the list got longer? That is the cliff, and it is the characteristic finding of this course. 
R: Si cayó la tasa de éxito, empezó con 40% en el n menor (n=5), y bajó a 0% para el resto de muestras, que fueron n = 10, 20 40. El modelo tuvo éxito de manera parcial solo en la muestra menor

- Which failure mode dominated? invalid (dropped or invented numbers) is a different problem from wrong-but-confident (right numbers, wrong order), and they suggest different fixes.
R: El fallo dominante fue invalid con 10 de 18, donde el modelo inventaba o perdía numeros del input, en este caso en especifico, al tener una lista de numeros mayor fallaba al perder o alterar información. El segundo fallo mayor, con 5 de 18 fue wrong-but-confident, donde se entiende la tarea y falla la ejecucuión.

- What did each solved instance cost? Compare seconds per instance. Then note that sorted() is O(n log n) with a proof, and the LLM has no such claim.
R: En sorted() es practicamente nulo, 0s. En el LLM fue 14.85s por respuesta, multiplicado por 20 llamadas, fue 297, y dividido para los aciertos que tuvo (2), da 148.5s. sorted() tiene la garantía de O(n log n) y el LLM carece de esto y tiene un costo elevado por las llamadas externas que debe hacer al modelo. 
