# AI Use Log

## Part 1 — Classical Search

**Herramienta:** ChatGPT

**Uso:** Se utilizó ChatGPT como apoyo para desarrollar y revisar la Parte 1. Ayudó con la estructura del benchmark para BFS, DFS, UCS, IDS y A*, la generación de instancias del 8-puzzle y gridworld, el cálculo de medianas, effective branching factor, y la generación de figuras. 

**Qué hicimos con la ayuda:** Se revisó y ejecutó el código localmente, verificamos los resultados contra los CSV generados y corregimos problemas encontrados durante el proceso. Las conclusiones del reporte se basan en los resultados experimentales obtenidos en nuestro repositorio.

**Comprensión:** Entendemos el funcionamiento general del código utilizado, las métricas reportadas y las conclusiones derivadas de los experimentos.


## Parte 2 — The Duel

### Generación del código Python

**Herramienta:** Claude

**Lo que pedí:**
Le pedí ayuda para generar el código Python necesario para implementar la parte experimental del duelo, incluyendo la ejecución del LLM, la validación de las respuestas, el sistema con herramienta A*, el registro de resultados y las pruebas de reproducibilidad.

**Lo que obtuve:**
Claude generó una base de código para ejecutar los experimentos y guardar los resultados en archivos CSV. También ayudó con la estructura de algunas funciones necesarias para procesar las respuestas del modelo y clasificarlas.

**Lo que hice con ello:**
No utilicé el código sin revisarlo. Lo integré con el código de búsqueda y las estructuras que ya tenía del proyecto, revisé las funciones y ejecuté las pruebas proporcionadas. También hice cambios cuando el comportamiento no coincidía con lo que necesitaba el experimento.

Después ejecuté los experimentos localmente con Ollama y `qwen2.5:3b`, revisé los archivos CSV generados y comprobé que el número de instancias y la distribución por nivel fueran correctos.

**¿Lo entendí?:**
Sí. Entiendo qué hace cada parte principal del código que utilicé para el experimento y puedo explicar cómo se generan las respuestas, cómo se validan y cómo se registran los resultados. También entiendo que el código experimental no determina por sí mismo si una respuesta del modelo es correcta: esa decisión la toma el validator comparando la respuesta con las reglas del problema y con la solución óptima.

---

### Validator y clasificación de errores

**Herramienta:** ChatGPT

**Lo que pedí:**
Pedí ayuda para entender cómo debía validar las respuestas del LLM sin preguntarle al propio modelo si su respuesta era correcta.

**Lo que obtuve:**
Recibí una explicación sobre cómo separar una solución ilegal, una solución legal pero subóptima y una solución óptima con un costo reportado incorrecto.

**Lo que hice con ello:**
Implementé y revisé el proceso de validación para que comprobara independientemente la legalidad del camino, que llegara al estado objetivo, que el costo reportado fuera correcto y que el costo fuera igual al costo óptimo obtenido con A*.

También revisé los resultados finales para asegurarme de que las categorías fueran consistentes con estas condiciones.

**¿Lo entendí?:**
Sí. Entiendo que una solución correcta/legal no necesariamente es óptima. Una solución puede llegar al objetivo respetando todas las reglas, pero utilizar más movimientos de los necesarios. Para ser `optimal_correct`, debe ser legal, llegar al objetivo, tener el costo reportado correcto y además tener el costo óptimo.

---

### Sistema LLM + A*

**Herramienta:** ChatGPT

**Lo que pedí:**
Pedí ayuda para implementar y depurar la interacción entre el modelo y mi implementación de A* como herramienta.

**Lo que obtuve:**
Recibí sugerencias sobre cómo estructurar la llamada de la herramienta y cómo hacer que el modelo devolviera los argumentos en formato JSON.

**Lo que hice con ello:**
Ejecuté primero una prueba y observé que el modelo estaba intentando resolver el puzzle directamente en lugar de llamar a la herramienta. Revisé el comportamiento y modifiqué las instrucciones del sistema para obligar al modelo a realizar primero la llamada a `astar_solve`.

Después ejecuté nuevamente una prueba específica para comprobar que el modelo generara correctamente la llamada y luego corrí el experimento completo.

También comparé los argumentos enviados a la herramienta con el problema real para poder determinar si los errores venían de A* o de la interacción con el modelo.

**¿Lo entendí?:**
Sí. Entiendo que A* puede encontrar la solución óptima cuando recibe correctamente el estado del problema, pero el LLM todavía puede equivocarse al construir los argumentos de la herramienta. Por eso el sistema aumentado no tiene una garantía de éxito completa: la búsqueda es confiable, pero la interfaz entre el modelo y la herramienta puede fallar.

---

### Experimento de reproducibilidad

**Herramienta:** ChatGPT

**Lo que pedí:**
Pedí ayuda para realizar la prueba de reproducibilidad requerida por el enunciado.

**Lo que obtuve:**
Recibí orientación sobre cómo realizar cinco llamadas idénticas sobre una misma instancia y cómo contar las respuestas diferentes.

**Lo que hice con ello:**
Ejecuté las cinco llamadas para cada sistema y revisé el archivo de resultados generado.

El resultado fue de 5 respuestas distintas en 5 llamadas para LLM-only y también 5 respuestas distintas en 5 llamadas para LLM+A*.

**¿Lo entendí?:**
Sí. Entiendo que esto mide qué tan consistente es el modelo cuando recibe exactamente la misma entrada. En este caso, con temperatura 1.0, ninguno de los dos sistemas fue completamente reproducible.

---

### Análisis y gráfica de scaling

**Herramienta:** ChatGPT

**Lo que pedí:**
Pedí ayuda para calcular la tasa de optimalidad por nivel y generar la gráfica de scaling a partir de los resultados obtenidos.

**Lo que obtuve:**
Recibí ayuda para procesar el CSV y generar la gráfica comparando los dos sistemas.

**Lo que hice con ello:**
Verifiqué los resultados y utilicé los valores obtenidos de mis propias ejecuciones:

* LLM-only: 0% en L4, L8, L12 y L16.
* LLM+A*: 70% en L4, 60% en L8, 50% en L12 y 80% en L16.

Después generé la gráfica y comprobé que coincidiera con estos valores antes de incluirla en el informe.

**¿Lo entendí?:**
Sí. Entiendo que la gráfica representa la proporción de soluciones que fueron correctas y óptimas en cada nivel. También entiendo que las variaciones entre niveles no necesariamente significan que el modelo empeore o mejore con el tamaño, porque solamente utilicé 10 instancias por nivel.

---

### Interpretación de resultados

**Herramienta:** ChatGPT

**Lo que pedí:**
Pedí ayuda para interpretar los resultados obtenidos y organizar la explicación para el informe.

**Lo que obtuve:**
Recibí ayuda para comparar los dos sistemas y para identificar qué información era importante destacar, como las categorías de error, la reproducibilidad y la latencia.

**Lo que hice con ello:**
Revisé los resultados de los CSV y comprobé los valores antes de utilizarlos en el informe.

El resultado principal fue que LLM-only obtuvo 0/40 soluciones óptimas, mientras que LLM+A* obtuvo 26/40, es decir, 65%.

También comparé la latencia promedio: 128.89 segundos para LLM-only frente a 15.08 segundos para LLM+A*. Finalmente, revisé que los 26 casos con argumentos correctos para la herramienta coincidieran con los 26 casos clasificados como `optimal_correct`.

**¿Lo entendí?:**
Sí. Entiendo que el resultado no significa simplemente que "A* es mejor que el LLM", sino que separar la búsqueda algorítmica del razonamiento del modelo permitió obtener mejores resultados. El LLM por sí solo tuvo dificultades para realizar la búsqueda, mientras que A* pudo encargarse de esa parte de manera determinista cuando recibió correctamente el problema.

También entiendo que los 14 errores del sistema aumentado estuvieron relacionados con argumentos incorrectos enviados por el modelo, y no con que A* encontrara una solución subóptima.
