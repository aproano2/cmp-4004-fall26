# Homework 2 — The Formalizer

**Integrantes:** Daniela Urbina, Estefanía Solórzano, Sol Segovia  
**Formalismo:** CSP · **Solver:** implementación Python del curso · **Modelo:** Ollama `qwen2.5:3b` (local)

## Método y resultados

Se diseñaron 20 problemas originales en lenguaje natural con soluciones de referencia documentadas (6 fáciles, 8 medios y 6 difíciles). La dificultad se definió por el número de variables: fácil ≤4, medio 5–6 y difícil ≥7; el número de restricciones complementa la clasificación. Se verificaron los 20 modelos escritos a mano con el solver. Las ejecuciones de B, B′ y C se realizaron con el mismo modelo local. Se registraron resultados por instancia, tiempos de pared, tiempo del solver, duración de inferencia y tokens; los CSV y las respuestas originales se conservan en `results/` y `.llm_cache/`.

Los cuatro brazos fueron: A (modelo manual → solver); B (LLM → JSON CSP → solver); B′ (B más un máximo de tres correcciones cuando el solver reporta un error); C (respuesta directa del LLM). En B′, el LLM solo recibe el error del solver, **nunca** la solución de referencia.

| Métrica | A | B | B′ | C |
|---|---:|---:|---:|---:|
| Problemas | 20 | 20 | 20 | 20 |
| Correctos, criterio original | 20 | 4 | 4 | 7 |
| Incorrectos | 0 | 8 | 8 | 13 |
| Sin respuesta | 0 | 8 | 8 | 0 |
| Exactitud original | 100% | 20% | 20% | 35% |
| Tokens de entrada | 0 | 6.666 | 22.604 | 3.326 |
| Tokens de salida | 0 | 4.703 | 11.468 | 1.087 |
| Inferencia acumulada (s) | 0 | 209,103 | 745,123 | 49,410 |

![Exactitud por dificultad](fig/accuracy_vs_difficulty.png)

![Exactitud total](fig/arm_accuracy.png)

**Control de evaluación:** las asignaciones q02 y q10 son numéricamente correctas en B y B′, pero el evaluador estricto comparó cadenas (`"3"`) con enteros (`3`). Sin cambiar los registros originales, la normalización de tipos eleva B y B′ a **6/20 (30%)** cada uno; A y C permanecen iguales. Por ambos criterios, **B′ − B = 0 puntos porcentuales**.

### Variación entre semillas

Repetimos B y C sobre los mismos 20 problemas con semillas 1 y 2. Mantuvimos temperatura 0 y `PYTHONHASHSEED=0`. La corrida principal usa semilla 0.

| Semilla | B correctos | C correctos |
|---|---:|---:|
| 0 | 4/20 (20 %) | 7/20 (35 %) |
| 1 | 3/20 (15 %) | 7/20 (35 %) |
| 2 | 3/20 (15 %) | 7/20 (35 %) |

B cambió el resultado en 7 de los 20 problemas entre las tres corridas; sus salidas de modelo cambiaron en 15. Su exactitud quedó entre 15 % y 20 %, con una desviación estándar muestral de 2,9 puntos porcentuales. C mantuvo los mismos 7 aciertos en las tres semillas, aunque una salida cambió de texto. Esta prueba adicional solo mide B y C; no repetimos B'. Los seis CSV `results/variance_*.csv` guardan los resultados por problema. El scorecard y el cálculo de costo usan únicamente la corrida principal.

## Taxonomía de errores

El evaluador marcó 16 fallos de B: **7 `unsat`**, **1 modelo malformado**, **6 errores de restricciones o premisas** y **2 diferencias de tipos**. Los primeros 8 dieron una alerta sin consultar la respuesta correcta. Los otros seis no avisaron durante la corrida. Al revisar sus modelos vimos que todos admitían al menos dos soluciones: buscar una segunda habría detectado la ambigüedad sin `gold`, aunque no nos diría qué pista faltaba. En q02 y q10, la asignación era numéricamente correcta, pero el evaluador comparó cadenas con enteros. Después de normalizar esos tipos quedan **14 fallos genuinos**: 8 señalados automáticamente y 6 silenciosos en nuestro programa. C tuvo **13 respuestas incorrectas** y ninguna produjo una alerta equivalente del solver (**0/13**). La clasificación y las salidas completas de B están en `taxonomy.md`.

Cinco salidas completas del modelo en B:

**q02 - diferencia de tipos.** El modelo puso las posiciones como texto. La asignación coincide con `gold` si se convierten a números, pero falló la comparación estricta.

```json
{
  "variables": {
    "Fern": ["1", "2", "3", "4"],
    "Cactus": ["1", "2", "3", "4"],
    "Orchid": ["1", "2", "3", "4"],
    "Ivy": ["1", "2", "3", "4"]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Fern", "Cactus", "Orchid", "Ivy"]},
    {"type": "neq", "a": "Cactus", "b": "1"},
    {"type": "neq", "a": "Cactus", "b": "2"},
    {"type": "neq", "a": "Fern", "b": "2"},
    {"type": "eq", "a": "Ivy", "b": "4"}
  ]
}
```

**q05 - `unsat`.** Pidió seis valores diferentes para seis personas que solo podían usar posiciones de 1 a 3. El solver rechazó el modelo.

```json
{
  "variables": {
    "Ann": [1, 2],
    "Ben": [1, 2],
    "Cat": [1],
    "Dan": [2, 3],
    "Eve": [2, 3],
    "Fay": [2, 3]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Ann", "Ben", "Cat", "Dan", "Eve", "Fay"]}
  ]
}
```

**q08 - faltaron pistas.** Solo dejó la restricción `alldiff` y `Coin=4` en el dominio. Omitió exclusiones de Bell, Aspen y Drum; quedaron seis soluciones y el programa no avisó.

```json
{
  "variables": {
    "Aspen": ["1", "2", "3", "4"],
    "Bell": ["1", "2", "3", "4"],
    "Coin": ["4"],
    "Drum": ["1", "2", "3", "4"]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Aspen", "Bell", "Coin", "Drum"]}
  ]
}
```

**q17 - pistas en un campo que el solver ignora.** Birch y Cedar aparecen en `given`, pero ese campo no se convierte en restricciones. El modelo quedó con varias soluciones y no produjo alerta.

```json
{"variables":{"Aster":["1","2","3","4","5"],"Birch":["1","2","3","4","5"],"Cedar":["1","2","3","4","5"],"Dahlia":["1","2","3","4","5"],"Elm":["1","2","3","4","5"]},"constraints":[{"type":"alldiff","vars":["Aster","Birch","Cedar","Dahlia","Elm"]},{"type":"eq","a":"Aster","b":"4"}],"given":{"Birch":"1","Cedar":"5"}}
```

**q19 - JSON malformado.** Hay una comilla de más después del dominio de Garnet. El parser lo rechazó antes de llegar al solver.

```text
{"variables":{"Amber":[3],"Bronze":[7],"Coral":[1],"Diamond":[5],"Emerald":[2],"Flint":[4,6],"Garnet":[1,2,3,4,5,6,7]"},"constraints":[{"type":"alldiff","vars":["Amber","Bronze","Coral","Diamond","Emerald"]},{"type":"eq","a":"Amber","b":3},{"type":"eq","a":"Bronze","b":7},{"type":"eq","a":"Coral","b":1},{"type":"eq","a":"Diamond","b":5},{"type":"eq","a":"Emerald","b":2},{"type":"neq","a":"Flint","b":4}]}
```

El solver detecta una especificación imposible o malformada; **no verifica automáticamente que el CSP conserve el significado del texto original**. Ese es el riesgo de los fallos silenciosos.

## Refinamiento B′

Doce de 20 instancias no activaron correcciones (el solver aceptó la especificación inicial). Ocho activaron las tres correcciones permitidas: **24 intentos de corrección**, sin un solo caso reparado. La distribución de éxitos fue: 0 tras la primera corrección, 0 tras la segunda, 0 tras la tercera; **8/8 no convergieron**. Siete terminaron en UNSAT y q19 terminó en un modelo malformado. Como no hubo correcciones exitosas, no es posible comparar empíricamente errores reparados en una ronda con errores persistentes. Los modelos válidos pero semánticamente incorrectos no activaron B′.

![Intentos de refinamiento](fig/refinement_iterations.png)

## Costo por respuesta correcta

Para el modelo local, se usa como indicador auditable **segundos de inferencia por respuesta correcta**, separados del tiempo del solver: A 0 s de inferencia; B **52,28 s/acierto**; B′ **186,28 s/acierto**; C **7,06 s/acierto**, con la evaluación estricta. Las duraciones de B′ incluyen la inferencia inicial de B para representar el costo de ejecutar todo el brazo, aunque su salida inicial se reutilizó durante esta ejecución. Los tiempos de pared no son estrictamente comparables debido a la caché.

El archivo `results/cost_per_correct.csv` contiene una **estimación ilustrativa**, no un precio real: con USD 0,25/h de cómputo local, los costos por respuesta correcta serían B **USD 0,00363**, B′ **USD 0,01294** y C **USD 0,00049** (sin electricidad ni amortización cuantificadas). La fórmula es `(segundos de inferencia / 3600 × costo por hora) / aciertos`; no se asigna costo monetario al trabajo humano del brazo A.

## Limitaciones y recomendación

El modelo local es pequeño y estos resultados no deben generalizarse a modelos mayores. El banco fue diseñado y revisado por el equipo. La dificultad se aproxima por tamaño formal, no por complejidad lingüística independiente. Una única solución `gold` puede penalizar otras soluciones válidas si el problema no exige unicidad; el evaluador estricto también penalizó tipos equivalentes en q02 y q10. La caché afecta las métricas de pared y el refinamiento solo reacciona a errores visibles del solver.

**Recomendación:** no desplegar B′ en su forma actual: triplicó aproximadamente el tiempo de inferencia de B sin mejorar su exactitud. Para una aplicación que necesite garantías, preferir B con validaciones adicionales de JSON, tipos, cobertura de premisas, satisfacibilidad y unicidad cuando aplique, además de registros y revisión humana de errores. C fue más preciso en esta muestra, pero sus fallos no tuvieron una señal automática comparable. Los resultados respaldan monitorear especialmente los modelos formalmente válidos pero semánticamente equivocados.
