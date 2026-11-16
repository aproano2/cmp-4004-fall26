# Registro de uso de IA — Duelo 2

Herramienta: Claude versión sonnet 4.6


## 1. Banco de problemas y verdad (`code/generate_problems.py`, `code/verify_problems.py`)

**Qué pedimos:** 20 o más problemas propios con su respuesta comprobada y al menos 3 niveles de dificultad.
**Qué obtuvimos:** Un generador con semillas fijas que arma acertijos de casas en
fila. Agrega pistas verdaderas hasta que la solución es única, quita las que sobran y
redacta el texto con plantillas. También un verificador por fuerza bruta que no usa el
solver ni el parser. Se subió de 24 a 40 problemas (10 por nivel) porque la scorecard
del curso pide al menos diez instancias por tamaño.
**Qué hicimos con eso:** Elegimos CSP como formalismo y aceptamos subir el banco a 40
problemas para cumplir el mínimo de diez instancias por nivel. Leímos los enunciados en
`problems/PROBLEMS.md` para confirmar que se entienden y que coinciden con la respuesta
guardada.
**¿Lo entendimos?** Claro, cada problema sale de una solución escondida, el generador agrega pistas que son verdad para esa solución hasta que el solver encuentra una sola respuesta, y después quita las pistas que sobran. Entendimos por qué se verifica aparte por fuerza bruta, si solo usáramos el mismo solver para crear y para verificar, un error en el solver no se notaría. La fuerza bruta prueba todas las combinaciones y no depende de ese código.

## 2. Solver y formato JSON (`code/csp_solver.py`, `code/spec.py`)

**Qué pedimos:** Usar el solver de la semana 6 para los modelos que escribe el LLM.
**Qué obtuvimos:** El `backtrack_search` de la semana 6 generalizado. El original solo
sabe all-different, y aquí hacen falta <, "vecino de" y "desplazamiento". Se le agregó un
conteo de soluciones (pedir 2) para detectar modelos sub-restringidos sin conocer la
respuesta. El parser/validador distingue tres errores (sintaxis, esquema, alcance) cuyos
mensajes son lo único que vuelve al modelo en B′.
**Qué hicimos con eso:** Corrimos los 19 tests(`python -m pytest code/tests -q`) y pasaron. Usamos este mismo solver en los brazos A, B y B′.
**¿Lo entendimos?** Por supuesto, es el backtracking de la semana 6 con MRV y forward checking, pero aceptando restricciones como “a la izquierda de” o “vecino de”, no solo “distintos”. Lo más importante que entendimos que si le pedimos al solver 2 soluciones y encuentra 2, el modelo del LLM está incompleto, porque el acertijo promete una sola. Eso se detecta sin conocer la respuesta correcta. También entendimos los tres tipos de error que son sintaxis (el JSON no carga), esquema (no tiene la forma de un CSP) y alcance (usa una variable que no declaró).

## 3. Los cuatro brazos y el bucle de refinamiento (`code/arms.py`, `code/llm.py`, `code/run_all.py`)

**Qué pedimos:** Los brazos A, B, B′ y C con las mediciones que pide el deber.
**Qué obtuvimos:** Los prompts, el bucle B′ (máximo 3 rondas, sin pasarle nunca la
respuesta correcta; un test lo comprueba) y el cliente de Ollama con caché. Después de una
corrida de prueba con un problema, la IA vio dos problemas y escribió correcciones:
- La primera llamada tardaba 70 s solo en cargar el modelo (calentamiento).
- En el brazo C el modelo copiaba los colores del ejemplo en un problema sin colores.
Al revisar la carpeta antes de entregar comprobamos que esas correcciones no quedaron
guardadas y que la corrida final usó la versión original del código (los prompts de
`.llm_cache/` lo confirman). La latencia no se infló, porque el modelo seguía cargado por
la prueba (primera llamada: 1,7 s). El defecto del prompt de C quedó declarado en el reporte
(§7), y el código entregado es exactamente el que se corrió.
**Qué hicimos con eso:** Elegimos `qwen2.5:3b` en Ollama.
Corrimos primero una prueba con un problema (L1-01) y después la corrida completa con las 200 instancias en 85 minutos.
**¿Lo entendimos?** Entendimos que A es nuestro modelo a mano; B es el LLM que escribe el CSP y el solver que lo resuelve; B′ es B más hasta 3 rondas de corrección; C es el LLM respondiendo directo. Entendimos por qué en B′ solo se le devuelve el mensaje del solver y nunca la respuesta correcta; si se la diéramos, el modelo podría copiarla y no estaríamos midiendo si el error del solver le sirve para aprender. También entendimos por qué B′ no mejoró porque cuando el solver decía “no hay solución”, el modelo borraba restricciones en vez de corregir la que estaba mal.

## 4. Taxonomía y monitores (`code/taxonomy.py`, `code/analyze.py`)

**Qué pedimos:** Clasificar cada falla del brazo B en las categorías del deber.
**Qué obtuvimos:** Una clasificación automática de las 189 fallas. Compara el modelo del
LLM con el modelo a mano para encontrar restricciones inventadas, invertidas y perdidas.
Al revisar los resultados reales, la IA encontró un error en su propio clasificador: marcaba
`alldiff(red, rabbit)` como error de alcance aunque es una forma válida de decir "el conejo
no vive en la casa roja". Se corrigió para marcarlo solo si la respuesta correcta lo viola.
Esto movió 9 fallas de "alcance" a otras categorías.
**Qué hicimos con eso:** Corrimos `python code/analyze.py`. Con eso revisamos las fallas reales y encontramos el error de su clasificador. Después volvimos a generar `taxonomy.md` y los CSV con la versión corregida.
**¿Lo entendimos?** Claro, cada falla de B se clasifica según lo que se ve; no parsea, no tiene solución, tiene varias soluciones o tiene una sola pero equivocada. La idea central es que casi todas las fallas de B se anuncian solas, mientras que las de C no. Por eso, C da una respuesta completa y segura aunque esté mal. Entendimos la falla “espejo” del ejemplo L1-04, el modelo invirtió todas las relaciones, describió el acertijo al revés con una sola solución, y por eso ningún monitor la detecta. También entendimos el error del clasificador; alldiff(red, rabbit) parecía un error, pero en realidad es una forma válida de decir que el conejo no vive en la casa roja. 


## 5. Corrección y colocación de graficas (`REPORT.md`)
**Qué pedimos:** Ayudanos revisando la estructura del REPORT.md y corrige las faltas de ortografía y 
coherencia de todo. Además, coloca las imagenes con el corespondiente link para que se observe en el 
reporte y sea de apoyo para la comprensión del lector y no se pierda.
**Qué obtuvimos:** Obtuvimos un reporte sin faltas de ortografía y bien ordenado.
**Qué hicimos con eso:** Nos sirvió para que sea una entrega academica y con coherencia de las ideas con
el fin de evitar errores fatales que impidan la comprensión de nuestro trabajo.
**¿Lo entendimos?** Más de entender, fue un apoyo para la escritura donde es una falla que aveces
cometemos en la hora de escribir.