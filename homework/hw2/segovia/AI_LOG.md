# AI Log - HW2 

## Parte 1

### Entendimiento del deber

**Tool:** Claude 

**What I asked:** Revisión del deber 2 y revisar la tabla de reparto del equipo que una de mis compañeras nos facilitó. Pregunté qué necesitaba para hacer mi parte y resolví unas dudas sobre el formalismo.

**What I got:** Una explicación: crear 7 problemas en tres niveles, verificar sus respuestas, definir la métrica de dificultad y preparar el brazo A y el validador. También me confirmó que hay que escoger un solo formalismo y que el equipo usará CSP.

**What I did with it:** Confirmé que trabajamos con CSP y revisé los archivos de la semana 6 para empezar a trabajar en el código.

**Did I understand it?** Sí. Mi parte es la base del experimento: el brazo A es el techo y a la vez la respuesta correcta (ground truth) contra la que se califican los brazos B, B′ y C.

### Revisión de los problemas y métrica de dificultad

**Tool:** Claude 

**What I asked:** Con los 7 problemas que planteé los corrigio, los desaorrolló para que se encuentre en tres niveles de dificultad que se pudieran escribir con `alldiff`, `neq` y `eq`, con su respuesta correcta.

**What I got:** Los enunciados q01–q07 (2 fáciles, 3 medios, 2 difíciles), cada uno con su respuesta y una derivación paso a paso. La métrica de dificultad es el número de variables (fácil ≤ 4, medio 5–6, difícil ≥ 7) y como métrica secundaria el número de restricciones. También una lista de "trampas" en cada problema, un `alldiff` por mesa en lugar de uno global.

**What I did with it:** Revisé que no cambiara nada sustancial de los problemas, que pusiera nombres porque yo los planteé como persona1, persona2 y así. Comprobar que si existian los 3 niveles de dificultad y revisar las métricas.

**Did I understand it?** Sí. Usamos el número de variables porque el solver resuelve todos en 4–11 llamadas, así que lo difícil es traducir el texto. Las trampas sirven para la taxonomía: algunos errores el solver los detecta solo  y otros pasan sin aviso.


### Revisión, guía y corrección de código

### Modelos del brazo A (`arm_a_p1.py`)

**Tool:** Claude 

**What I asked:** Que me guie en como hacer los modelos del brazo A en el mismo estilo del `arm_a.py` de la semana 6 y que el runner registrara los datos necesarios. Una vez plantee mi codigo le pedí que lo compruebe, que me corrija errores y me sugiera mejoras a implementar.

**What I got:** Correcciones y bloques de código escritos correctamente de los modelos por problema. Armar los helpers `V`, `alldiff`, `is_`, `not_` y `differs`. Guia para el runner para que guarde por instancia el resultado (correct / incorrect / no_answer), el tiempo total, el tiempo del solver y los tokens.

**What I did with it:** Implementé las correciones y ejecuté el archivo.

**Did I understand it?** Sí. Cada frase del enunciado se convierte en una restricción: "todos diferentes" es `alldiff`, "X es Y" es `eq`, "X no es Y" es `neq` contra un valor y "X es diferente de Z" es `neq` entre dos variables.

### Validador (`validate_problems.py`)

**Tool:** Claude 

**What I asked:** Que me guie en como modificar `_verify_puzzles.py` para este caso. Después que revise el codigo que yo planteé y me corrija y lo mejore de ser posible

**What I got:** La guia para hacer el archivo donde se revisa que las variables aparezcan en el enunciado, enumera todas las soluciones con un método independiente del solver, exige que haya una sola y que sea igual a la respuesta, vuelve a resolver con `backtrack_search` y revisa que el nivel corresponda a la métrica. Correción posterior de mi codigo para que cumpla con todos esos parametros correctamente. 

**What I did with it:** Segui la guia de como armar el archivo y luego implementé las sugerencias para que salga todo lo soliciytado para el deber 2 correctamente y que todo el equipo pueda usarlo y entender. También se probaron errores a propósito un `alldiff` global en q05 da 0 soluciones y quitar las cajas en q06 da 2 soluciones.

**Did I understand it?** Sí. La solución tiene que ser única para poder calificar sin ambigüedad. Si un modelo del LLM tiene varias soluciones, el solver devuelve una sin avisar. Por eso el error "sub-restringido" solo se detecta sin la respuesta correcta si se busca una segunda solución.

## Parte 2

### Entender la Parte 2

**Tool:** ChatGPT

**What I asked:** Le pedí que me explicara de qué se trataba el deber, qué me tocaba hacer exactamente en mi parte y qué archivos de la semana 6 podía reutilizar.

**What I got:** Me resumió cómo funcionan los brazos A, B, B' y C, y aclaró lo que debía entregar: siete problemas nuevos con sus modelos A, la conexión con Ollama para B y C, y los CSV con tiempos y tokens usando `csp.py`, `logic_lm.py` y `aicourse`.

**What I did with it:** Organicé mis archivos según lo que me correspondía en el grupo, separando el JSON de los problemas del script que llama a Ollama y guarda los resultados.

**Did I understand it?** Si, me quedó claro que en B el modelo traduce el texto a CSP para que lo resuelva el solver, en C responde directo sin solver, y B' sirve para intentar corregir los fallos a partir de los errores.

### Programa de B/C y problema con `--ids`

**Tool:** ChatGPT

**What I asked:** Le pasé el código que ya tenía de `run_bc.py` para que me ayudara a corregir los errores que me estaban saliendo y a resolver el fallo al ejecutar `--ids q01`.

**What I got:** Revisó mi script, me señaló dónde estaba fallando y me explicó cómo agregar el filtro de `--ids` y por qué `q01` podía dar respuestas distintas si el modelo generado quedaba con varias soluciones.

**What I did with it:** Corregí esos puntos directamente sobre mi código en `run_bc.py`, probé que `--ids q01` ya corriera bien de forma individual y luego ejecuté mis siete problemas guardando los resultados y la caché.

**Did I understand it?** Si, entendí que `--ids` solo filtra qué casos correr y que, si el modelo generado por B omite pistas, el solver puede acertar por casualidad aunque la traducción esté incompleta.

### Problemas q08–q14 y revisión del JSON

**Tool:** ChatGPT

**What I asked:** Le pasé mis avances de los siete problemas en el formato JSON de la parte 1 para que me ayudara a corregir lo que no funcionaba bien y a revisar si las respuestas eran únicas.

**What I got:** Revisó la estructura de los enunciados q08–q14, corrigió los errores en los modelos de `arm_a_p2.py` y verificó que cada caso tuviera una única solución sin ambigüedades, manteniendo la distribución en dos fáciles, tres medios y dos difíciles.

**What I did with it:** Solo tomé las partes necesarias para corregir los errores en `problems_p2.json` y `arm_a_p2.py`. Probé todo con `validate_problems.py` y confirmé que los siete problemas tenían una única solución igual al `gold` (7/7 en A). Luego ejecuté B y C con Ollama (ambos lograron 1/7) y guardé los CSV finales (`difficulty_p2.csv`, `arm_a_p2_results.csv` y `bc_p2.csv`).

**Did I understand it?** Si, entiendo cómo funcionan `alldiff`, `eq` y `neq`, y por qué cada problema necesita una única solución para comparar los brazos de forma justa. Aunque el validador revisa el modelo, también verifiqué a mano que los enunciados coincidieran con sus derivaciones.

## Parte 3

### Implementación de B′ y revisión de resultados

**Tool:** ChatGPT

**What I asked:** Pedí apoyo para adaptar el refinamiento B′ al solver CSP del equipo y revisar la integración de resultados.

**What I got:** Orientación sobre el ciclo de hasta tres correcciones a partir de errores del solver, compatibilidad de archivos y comparación de los cuatro brazos.

**What I did with it:** Revisé el código, ejecuté B′ con Ollama y consolidé los resultados de los 20 problemas.

**Did I understand it?** Sí, entendí que el refinamiento no puede consultar las respuestas correctas, únicamente se activa cuando el solver informa un error.

### Gráficas, costos y análisis

**Tool:** ChatGPT

**What I asked:** Solicité ayuda para revisar las tablas, las gráficas y el cálculo de costo por respuesta correcta a partir de los CSV del experimento.

**What I got:** Una revisión de los resultados, la diferencia entre evaluación estricta y normalización de tipos y una fórmula de costo basada en tiempo de inferencia.

**What I did with it:** Contrasté la información con las ejecuciones locales y usé los resultados obtenidos para preparar el análisis y las figuras.

**Did I understand it?** Sí. B′ no mejoró la exactitud de B y el costo presentado es una estimación, no un cobro de Ollama.


### Errores

**Tool:** ChatGPT

**What I asked:** Pedí ayuda para solucionar errores que aparecieron al ejecutar los archivos del proyecto en VS Code, principalmente relacionados con las importaciones de Python y la ejecución de los programas.

**What I got:** Explicaciones sobre los errores y los comandos correctos para ejecutar los archivos desde la terminal.

**What I did with it:** Apliqué las correcciones necesarias y ejecuté las pruebas localmente hasta obtener los resultados.

**Did I understand it?** Sí. Comprendí cómo ejecutar correctamente los módulos de Python y cómo identificar errores de ejecución sin modificar innecesariamente el código.
