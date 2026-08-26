# Week 0 — Primera comparacion: ordenar enteros

**Backend:** ollama, `qwen2.5:3b`, temperatura = 0.0
**Instancias:** 20 en total, 5 por cada tamano 5 / 10 / 20 / 40 (semilla fija 20250806)
**Prompt usado:** estilo `format` — el equivalente de "Reply with only the number"
pero para ordenar: "Reply with ONLY the sorted list as comma-separated integers,
no explanation." Elegido en la §4 antes de correr el benchmark, no ajustado despues.

## Tabla resumen

| sistema    | n   | resueltos | tasa | mediana | p95     |
| ---------- | --- | --------- | ---- | ------- | ------- |
| `sorted()` | 20  | 20        | 100% | 0.00s   | 0.00s   |
| LLM        | 20  | 2         | 10%  | 0.00s   | 120.00s |

**Modos de falla (LLM):** invalid = 7, malformed = 5, wrong-but-confident = 6

## Scorecard

| Eje                                      | `sorted()`                                                                                                                     | LLM                                                                                                                                                                                                                                                                                                               |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Correctness (exactitud)                  | 20/20 (100%)                                                                                                                   | 2/20 (10%)                                                                                                                                                                                                                                                                                                        |
| **Guarantee (garantia)**                 | Devuelve una permutacion del input en orden no-decreciente para **todo** input, en O(n log n). Sin condicion, sin excepciones. | Produjo un ordenamiento correcto en 2/20 instancias. No se afirma nada sobre la instancia 21 — no hay una prueba detras, solo una tasa observada en esta muestra.                                                                                                                                                 |
| **Cost (costo)**                         | Practicamente gratis — microsegundos, sin configuracion.                                                                       | ~10 minutos de tiempo real para las 20 instancias en CPU (`qwen2.5:3b`, ollama), mas el tiempo que invert­i probando cuatro variantes de prompt antes de fijar una. Ese tiempo de diseno no esta incluido en los 10 minutos y no apareceria si solo reportara el tiempo de inferencia.                            |
| **Latency (latencia)**                   | 0.00s / 0.00s (mediana/p95)                                                                                                    | 0.00s / 120.00s. El p95 se dispara por las instancias de tamano 40, donde el modelo a veces genero miles de tokens en vez de solo la lista pedida.                                                                                                                                                                |
| **Reproducibility (reproducibilidad)**   | Deterministico por construccion — el mismo input siempre da el mismo output.                                                   | A temp = 0.0 (lo que use aqui), 1 de 3 corridas repetidas con el mismo prompt dio una respuesta — asi que es mayormente, pero no perfectamente, reproducible incluso a temp 0. A temp = 1.0 fue 3 de 3 distintas. Solo puedo afirmar la reproducibilidad que demostre, bajo las condiciones exactas que demostre. |
| **Scaling (escalamiento)**               | 100% → 100% → 100% → 100% (n = 5, 10, 20, 40)                                                                                  | 40% → 0% → 0% → 0% (n = 5, 10, 20, 40)                                                                                                                                                                                                                                                                            |
| **Interpretability (interpretabilidad)** | Puedo senalar una prueba de libro de texto de correccion y complejidad.                                                        | Ningun certificado de ningun tipo. No puedo inspeccionar _por que_ acerto 40% en n=5 — solo puedo reportar que lo hizo.                                                                                                                                                                                           |
| **Failure mode (modo de falla)**         | Ninguno observado.                                                                                                             | invalid = 7, malformed = 5, wrong-but-confident = 6 — ningun modo domina claramente, lo que significa que el modelo no esta fallando por una sola razon limpia.                                                                                                                                                   |

## Respondiendo las cuatro preguntas

**1. ¿Cayo la tasa de acierto del LLM conforme la lista se hizo mas larga?**
Si, y es un acantilado, no una pendiente: 40% en n=5, luego 0% en n=10, 20 y 40. Practicamente no hay una zona de "acierto parcial" en mis datos — el modelo, o acertaba bastante bien en el caso pequeno, o fallaba por completo en cuanto la lista pasaba de 5 elementos.

**2. ¿Que modo de falla domino?**
Ninguno domino claramente — invalid (7), wrong-but-confident (6) y malformed (5) estan bastante parejos. Eso ya es informacion en si misma: no es un solo bug que pudiera arreglar con un ajuste de prompt, son tres rutas de falla distintas (perder o inventar numeros, tener los numeros correctos pero en el orden equivocado, y no producir una lista parseable en absoluto) ocurriendo a tasas similares.

**3. ¿Que costo cada instancia resuelta?**
`sorted()` costo practicamente nada por instancia. La corrida del LLM costo cerca de 10 minutos de tiempo real para 20 instancias (unos 30s/instancia en promedio, aunque muy desparejo — algunas instancias fueron rapidas, y las de
tamano 40 se alargaron porque el modelo genero muchos mas tokens de los que la tarea necesitaba). `sorted()` ademas viene con una prueba de O(n log n); el "costo" del LLM no viene con ninguna garantia de ese tipo.

**4. ¿Donde pude haber sido injusto?**

- Corri la comparacion principal a temperatura = 0.0, que es el ajuste mas favorable y mas deterministico para el LLM. Un duelo a temp = 1.0 probablemente mostraria una tasa de acierto aun mas baja y menos reproducible.
- Un modelo mas grande (o alguna de las opciones de API de pago) probablemente resolveria mas instancias, sobre todo en n=40. No puedo saber cuanto sin correrlo de verdad — estoy reportando el resultado para este modelo especifico de 3B, no para "los LLM" en general.

## Para traer a la Sesion 1A

**Mi prediccion:** el algoritmo clasico va a ganar mas duelos este
semestre. Con base en este primer resultado, la brecha se ve grande, pero espero que se reduzca en tareas donde "correcto de forma verificable" importe menos que "plausible y rapido", asi que no espero un barrido de 14-0 en ningun sentido.
