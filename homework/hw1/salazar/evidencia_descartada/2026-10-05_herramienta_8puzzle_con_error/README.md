# Corrida descartada: la herramienta devolvía un error en el 8-puzzle (5 de octubre)

En el 8-puzzle del curso, cada acción del problema es la **casilla** a la que se mueve el blanco (un número), no una letra U/D/L/R. Nuestra herramienta unía esas acciones como texto, y en el 8-puzzle respondía al modelo con un error ("expected str instance, int found") en vez del camino. En la grilla las acciones ya son letras, así que esa parte funcionaba bien.

Lo detectamos al leer las primeras transcripciones del brazo con herramienta, detuvimos la corrida y corregimos `camino_en_letras()` en `code/herramienta.py`. Agregamos una prueba en `test_group.py`: para cada instancia, la herramienta debe devolver un camino que nuestro validador clasifique como `correct`.

Aquí quedan las respuestas del modelo que recibieron el resultado erróneo (`llm_cache/`) y el registro de esas llamadas. No se usan en el reporte. Las llamadas de la ronda 0, en las que el modelo pide la herramienta, no dependen de la respuesta de la herramienta y siguen siendo válidas en la caché oficial.
