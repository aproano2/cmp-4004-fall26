# Primera comparación: `sorted()` vs LLM

## Tabla de comparación

| Aspecto               | `sorted()`                                                   | LLM                                                                   |
| --------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------- |
| **Correctitud**       | 20/20 (100%)                                                 | 3/20 (15%)                                                            |
| **Garantía**          | Si recibe una lista válida, la ordena correctamente.         | Puede ordenar correctamente, pero no siempre da una respuesta válida. |
| **Costo**             | Muy bajo y no necesita usar un modelo.                       | Necesita hacer una llamada al modelo y utiliza más recursos.          |
| **Latencia**          | Mediana: 0.00 s / P95: 0.00 s                                | Mediana: 0.02 s / P95: 122.05 s                                       |
| **Reproducibilidad**  | Es determinista: con la misma entrada da el mismo resultado. | Dio respuestas diferentes en varias ejecuciones.                      |
| **Escalabilidad**     | 100% en todos los tamaños probados.                          | 60% con n=5 y 0% desde n=10.                                          |
| **Interpretabilidad** | Es fácil comprobar si la lista quedó ordenada correctamente. | Hay que revisar la respuesta para saber si está correcta.             |
| **Modo de fallo**     | No se observaron fallos.                                     | 10 `invalid`, 2 `malformed` y 5 `wrong-but-confident`.                |

---

## 1. Correctitud

El `sorted()` obtuvo **20 de 20 respuestas correctas**, es decir, un **100%**.

En cambio, el LLM solamente obtuvo **3 de 20**, que corresponde al **15%**. Esto significa que falló en 17 de las 20 pruebas.

Para una tarea sencilla como ordenar números, `sorted()` fue mucho más confiable que el LLM.

---

## 2. Garantía

Con `sorted()` sabemos que, si le damos una lista válida, la función la va a ordenar correctamente.

Con el LLM esto no siempre pasa. El modelo puede dar una respuesta correcta, pero también puede equivocarse o dar una respuesta que no tenga el formato esperado.

Por eso fue necesario utilizar un **verificador** para revisar si las respuestas del LLM realmente eran correctas.

---

## 3. Costo

`sorted()` es una función de Python y tiene un costo muy bajo. Además, no necesita hacer ninguna llamada a un modelo.

El LLM necesita procesar cada ejercicio y eso utiliza más recursos y tiempo.

En este experimento no calculamos cuánto dinero costó cada llamada al modelo, por lo que no podemos dar un valor exacto.

---

## 4. Latencia

Los resultados fueron:

| Sistema    | Mediana |      P95 |
| ---------- | ------: | -------: |
| `sorted()` |  0.00 s |   0.00 s |
| LLM        |  0.02 s | 122.05 s |

`sorted()` fue prácticamente inmediato en todas las pruebas.

El LLM tuvo una mediana de **0.02 segundos**, pero su P95 fue de **122.05 segundos**. Esto significa que algunas respuestas fueron mucho más lentas que otras.

Por eso, el tiempo de respuesta del LLM fue menos predecible.

---

## 5. Reproducibilidad

Se hicieron 3 ejecuciones para cada temperatura.

### Temperatura = 0.0

Se obtuvieron estas respuestas:

```text
run 0: 'Organize papers, Align documents, Secure folders'

run 1: 'Organize papers, Hold together documents, Keep cables tidy'

run 2: 'Organize papers, Hold together documents, Keep cables tidy'
```

Hubo **2 respuestas diferentes en 3 ejecuciones**.

### Temperatura = 1.0

Se obtuvieron:

```text
run 0: 'Organize papers,tie papers together,keep papers folded'

run 1: 'organizing papers holding folders together fastening files'

run 2: 'Organizing paperwork holding papers together organizing folders securi'
```

En este caso, las **3 respuestas fueron diferentes**.

Esto muestra que el LLM puede responder de manera diferente aunque se le haga la misma pregunta.

En cambio, `sorted()` siempre da el mismo resultado cuando recibe la misma lista.

**Nota:** El ejercicio pedía hacer 5 ejecuciones, pero en esta prueba se hicieron solamente 3. Por eso se reportan los resultados de las 3 ejecuciones realizadas.

---

## 6. Escalabilidad

Los resultados según el tamaño de la lista fueron:

| Sistema    | n = 5 | n = 10 | n = 20 | n = 40 |
| ---------- | ----: | -----: | -----: | -----: |
| `sorted()` |  100% |   100% |   100% |   100% |
| LLM        |   60% |     0% |     0% |     0% |

`sorted()` tuvo un **100% de respuestas correctas** en todos los tamaños.

El LLM tuvo un **60% con listas de 5 elementos**, pero bajó a **0% desde 10 elementos**.

Esto muestra que el LLM tuvo problemas cuando aumentó el tamaño de la lista.

---

## 7. Interpretabilidad

Con `sorted()` es fácil comprobar el resultado. Solo tenemos que revisar que:

* Los números estén ordenados.
* Estén todos los elementos originales.
* No falte ningún elemento.
* No aparezcan elementos nuevos.

En el caso del LLM, la respuesta es texto y puede parecer correcta aunque realmente no lo sea. Por eso necesitamos un **parser y un verificador** para comprobarla.

---

## 8. Modos de fallo

En las 20 pruebas del LLM se encontraron:

| Tipo de fallo         |  Casos |
| --------------------- | -----: |
| `invalid`             |     10 |
| `malformed`           |      2 |
| `wrong-but-confident` |      5 |
| **Total**             | **17** |

`sorted()` no presentó fallos en las pruebas realizadas.

Los errores del LLM fueron principalmente:

* **`invalid` (10 casos):** la respuesta no cumplía con lo que se necesitaba.
* **`malformed` (2 casos):** la respuesta tenía un formato incorrecto.
* **`wrong-but-confident` (5 casos):** la respuesta parecía correcta, pero en realidad estaba equivocada.

Esto último es importante porque una respuesta que parece segura no necesariamente es correcta.

---

# Dónde podemos haber sido injustos

Aunque `sorted()` obtuvo mejores resultados, también hay algunas cosas que pudieron favorecerlo.

### 1. ¿Los dos sistemas recibieron exactamente la misma información?

Los dos tenían que resolver la misma tarea: ordenar una lista.

Pero `sorted()` recibe directamente la lista, mientras que el LLM tiene que entender una pregunta escrita y después generar una respuesta.

Por eso, el LLM tiene algunos pasos adicionales.

### 2. ¿El prompt pudo afectar al resultado?

Sí. El LLM depende mucho de las instrucciones que recibe.

Un prompt diferente podría haber hecho que el modelo obtuviera mejores resultados. Por eso, estos resultados corresponden solamente al modelo y al prompt utilizados en este experimento.

### 3. ¿Las pruebas fueron suficientes?

Se utilizaron listas de tamaños **5, 10, 20 y 40**.

Es posible que utilizando otros tamaños o diferentes números los resultados fueran diferentes.

Por eso, no podemos decir que el LLM siempre va a tener un 15% de correctitud. Solo podemos decir que obtuvo ese resultado en las pruebas realizadas.

### 4. ¿Se tomó en cuenta el tiempo de hacer el prompt?

No. El tiempo medido fue solamente el tiempo de ejecución de los sistemas.

No se tomó en cuenta el tiempo que una persona necesitó para escribir el prompt, hacer el código o crear el verificador.

### 5. ¿Un modelo diferente podría hacerlo mejor?

Sí, es posible. Un modelo más grande o diferente podría obtener mejores resultados.

Pero para saberlo tendríamos que hacer el mismo experimento con ese modelo.

Por eso, los resultados no representan a todos los LLM, sino solamente al modelo utilizado en esta prueba.

---

# Conclusión

En este experimento, `sorted()` fue mucho mejor que el LLM para ordenar listas.

`sorted()` obtuvo **20/20 (100%)**, mientras que el LLM obtuvo solamente **3/20 (15%)**.

También se pudo observar que `sorted()` fue mucho más rápido y mantuvo el **100% de correctitud** incluso cuando aumentó el tamaño de las listas.

El LLM, en cambio, pasó de **60% con n=5 a 0% desde n=10**.

Además, el LLM presentó diferentes tipos de errores y en algunas pruebas dio respuestas diferentes aunque se utilizara la misma pregunta.

Por lo tanto, para esta tarea, `sorted()` fue más **confiable, rápido y fácil de verificar**.

Sin embargo, estos resultados solo corresponden al modelo, configuración, prompt y pruebas utilizadas. No significa que todos los LLM tengan el mismo resultado.
