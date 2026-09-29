# AI Use Log

## Week 0 — the sorting verifier

**Tool:* Gemini

---

**What I asked:** ¿Qué es la función `sorted()` en Python? y ¿cuál es la diferencia entre usar `sorted()` y LLM para ordenar información?

**What I got:** Me explicó que `sorted()` usa un código determinista $O(n \log n)$ y me dio una tabla comparando las dos, para ver como `sorted()` sigue reglas lógicas mientras que el LLM intenta adivinar el siguiente texto usando probabilidades.

**What I did with it:** La use para entender del por que un algoritmo tradicional siempre es mejor que un LLM al momento de ordenar datos o listas.

**Did I understand it?** Si, me ayudo a entender la diferencia entre `sorted()` que es un código exacto o cuantitativo y el LLM es mas cualitativo, además que puede equivocarse o inventar cosas.

---

**What I asked:** ¿Qué significa la métrica p95 en latencia al comparar `sorted()` frente a un LLM?

**What I got:** Me explicó que p95 es el tiempo en el que se completan el 95% de las tareas, y me mostró que `sorted()` tarda menos de 1s mientras que el LLM tarda más tiempo.

**What I did with it:** Use esto para llenar la sección de rendimiento y costos.

**Did I understand it?** Si, me ayudo a entender que si se usa algoritmos en vez de un LLM para este tipo de tareas, es mucho más rapido en obtener la respuesta.

---

**What I asked:** ¿Qué significan Reproducibility e Interpretability al evaluar `sorted()` vs LLM?

**What I got:** Me explicó que Reproducibility es si el sistema responde igual siempre, en `sorted()` si es asi, pero el LLM varía.
Interpretability es si se puede ver el paso a paso del código y en el LLM no se puede.

**What I did with it:** Use para llenar lo que pedia en la tabla.

**Did I understand it?** Si, ya entendi que en estos casos que no se puede tener errores o respuestas diferentes, es mejor usar el algoritmo clásico.

---

**What I asked:** Dime el significado del desglose `failure modes: LLM invalid=8, malformed=4, wrong-but-confident=6`

**What I got:** La explicación fue:
 - `invalid`: Cuando el modelo olvida números o se los inventa.
 - `malformed`: Cuando responde con un texto que no se puede entender como lista.
 - `wrong-but-confident`: Cuando entrega los números mal ordenados pero muy seguro de sí.

**What I did with it:** Use para poder entender mejor cada uno y poder llenar correctamente en el `first_comparison.md`.

**Did I understand it?** Si, ya entendi que medir estos tipos de error puede ayudar a saber si el modelo es confiable y cuales fueron sus fallos.

---

**What I asked:** ¿Qué modelo de LLM es `qwen2.5:3b` ejecutado en Ollama, junto con sus pros y contras?

**What I got:** Me explicó que es un modelo pequeño (3 mil millones de parámetros), es rápido de correr en la laptop, pero que sufre mucho con la lógica compleja y en las listas largas.

**What I did with it:** Use para poder justificar en por qué el modelo colapsó cuando la lista creció desde $n=5$ hasta $n=40$.

**Did I understand it?** Si, ya entendi que al ser un modelo pequeño le cuesta poder ordenar números en listas largas y por eso hay fallos.