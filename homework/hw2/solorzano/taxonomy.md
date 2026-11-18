# Taxonomía completa de los 16 casos marcados como fallos de B

Modelo: `qwen2.5:3b`. Resultado publicado por el evaluador original: 4/20. **Advertencia:** q02 y q10 tienen respuestas numéricamente correctas, pero fueron marcadas incorrectas por comparar `str` con `int`. En una evaluación semántica normalizada B = 6/20. Los CSV originales se conservan sin modificación.

| Categoría primaria | N | Detectable sin gold |
|---|---:|---|
| Sobre-restricción / UNSAT | 7 | Sí |
| JSON malformado | 1 | Sí |
| Sub-restricción, premisa omitida o alcance | 6 | A veces: los seis modelos admiten al menos dos soluciones. Una comprobación de unicidad detectaría la ambigüedad sin `gold`, pero no se hizo durante la corrida. |
| Desajuste de tipos evaluador | 2 | No como fallo del solver |

**Detectabilidad:** distinguimos entre una alerta que produjo nuestro programa y un error que se podría detectar sin `gold` con otra comprobación. En esta corrida hubo 8/16 alertas automáticas: siete `unsat` y un modelo malformado. Los otros seis modelos con errores de restricciones no dieron alerta, pero cada uno admite al menos dos soluciones. Buscar una segunda solución señalaría la ambigüedad sin decir qué premisa se omitió. Los dos desajustes de tipos tampoco produjeron una señal del solver.

## q02 — Desajuste de tipos (números como cadenas)

**Resultado original:** incorrect. **Señal:** `none`. **Detección automática sin gold:** No en esta corrida. Una búsqueda de segunda solución sí habría señalado la ambigüedad, sin identificar la premisa incorrecta.

**Revisión:** El modelo devuelve 1–4 como cadenas. La asignación coincide con gold tras normalizar los tipos; el evaluador estricto la marca incorrecta.

**Salida literal de Ollama (brazo B):**

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

## q03 — Sobre-restricción / UNSAT

**Resultado original:** no_answer. **Señal:** `unsat`. **Detección automática sin gold:** Sí.

**Revisión:** Room3 queda limitado a cream/mint y el modelo prohíbe ambos; no hay valor posible.

**Salida literal de Ollama (brazo B):**

```json
{
  "variables": {
    "Room1": ["cream"],
    "Room2": ["mint", "sky"],
    "Room3": ["cream", "mint"],
    "Room4": ["cream", "mint", "sky"],
    "Room5": ["cream", "mint", "sky"]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Room1", "Room2"]},
    {"type": "neq", "a": "Room1", "b": "sky"},
    {"type": "neq", "a": "Room2", "b": "Room1"},
    {"type": "neq", "a": "Room3", "b": "cream"},
    {"type": "neq", "a": "Room3", "b": "mint"},
    {"type": "neq", "a": "Room4", "b": "mint"},
    {"type": "neq", "a": "Room5", "b": "sky"},
    {"type": "neq", "a": "Room5", "b": "Room4"},
    {"type": "neq", "a": "Room4", "b": "Room3"}
  ]
}
```

## q04 — Premisa omitida y dominio incorrecto

**Resultado original:** incorrect. **Señal:** `none`. **Detección automática sin gold:** No.

**Revisión:** Omite que Ivo terminó último (posición 6) y permite Lia=6 pese a que la asignación correcta exige otra posición.

**Salida literal de Ollama (brazo B):**

```json
{
  "variables": {
    "Hana": ["1", "2", "3", "4", "5"],
    "Ivo": ["1", "2", "3", "4", "5", "6"],
    "Jun": ["1"],
    "Kai": ["1", "2", "3", "4", "5", "6"],
    "Lia": ["2", "3", "4", "5", "6"],
    "Moe": ["1", "2", "3", "4", "5", "6"]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Hana", "Ivo", "Jun", "Kai", "Lia", "Moe"]},
    {"type": "neq", "a": "Hana", "b": "4"},
    {"type": "neq", "a": "Hana", "b": "5"},
    {"type": "neq", "a": "Lia", "b": "3"},
    {"type": "neq", "a": "Lia", "b": "4"},
    {"type": "neq", "a": "Lia", "b": "5"},
    {"type": "neq", "a": "Moe", "b": "4"}
  ]
}
```

## q05 — Sobre-restricción / UNSAT

**Resultado original:** no_answer. **Señal:** `unsat`. **Detección automática sin gold:** Sí.

**Revisión:** Impone all-different a seis participantes con dominios limitados a 1–3; contradice la posibilidad de posiciones repetidas.

**Salida literal de Ollama (brazo B):**

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

## q06 — Sub-restricción: alcance/aritad de alldiff

**Resultado original:** incorrect. **Señal:** `none`. **Detección automática sin gold:** No.

**Revisión:** Incluye pistas de celdas, pero omite todas las restricciones alldiff de filas, columnas y cajas 2×2.

**Salida literal de Ollama (brazo B):**

```json
{
  "variables": {
    "R1C1": ["1"],
    "R1C2": ["1", "2", "3", "4"],
    "R1C3": ["1", "2", "3", "4"],
    "R1C4": ["1", "2", "3", "4"],
    "R2C1": ["1", "2", "3", "4"],
    "R2C2": ["4"],
    "R2C3": ["1", "2", "3", "4"],
    "R2C4": ["2"],
    "R3C1": ["1", "2", "3", "4"],
    "R3C2": ["1", "2", "3", "4"],
    "R3C3": ["4"],
    "R3C4": ["3"],
    "R4C1": ["4"],
    "R4C2": ["1", "2", "3", "4"],
    "R4C3": ["1", "2", "3", "4"],
    "R4C4": ["1", "2", "3", "4"]
  },
  "constraints": [
    {"type": "eq", "a": "R1C1", "b": "1"},
    {"type": "eq", "a": "R2C2", "b": "4"},
    {"type": "eq", "a": "R2C4", "b": "2"},
    {"type": "eq", "a": "R3C3", "b": "4"},
    {"type": "eq", "a": "R3C4", "b": "3"},
    {"type": "eq", "a": "R4C1", "b": "4"}
  ]
}
```

## q07 — Sobre-restricción / UNSAT

**Resultado original:** no_answer. **Señal:** `unsat`. **Detección automática sin gold:** Sí.

**Revisión:** La combinación de múltiples restricciones alldiff incorrectas hace el modelo insatisfacible.

**Salida literal de Ollama (brazo B):**

```json
{
  "variables": {
    "Arden": ["1"],
    "Brook": ["2"],
    "Cliff": ["3"],
    "Dale": ["1","2","3","4"],
    "Elm": ["1","2","3","4"],
    "Fern": ["1","2","3","4"],
    "Glen": ["1","2","3","4"],
    "Heath": ["1","2","3","4"]
  },
  "constraints": [
    {"type":"alldiff","vars":["Arden","Brook","Cliff","Dale"]},
    {"type":"alldiff","vars":["Arden","Brook","Cliff","Elm"]},
    {"type":"alldiff","vars":["Arden","Brook","Cliff","Fern"]},
    {"type":"alldiff","vars":["Arden","Brook","Cliff","Glen"]},
    {"type":"alldiff","vars":["Arden","Brook","Dale"]},
    {"type":"alldiff","vars":["Arden","Cliff","Dale"]},
    {"type":"alldiff","vars":["Arden","Elm","Dale"]},
    {"type":"alldiff","vars":["Arden","Fern","Dale"]},
    {"type":"alldiff","vars":["Arden","Glen","Dale"]},
    {"type":"alldiff","vars":["Brook","Cliff","Dale"]},
    {"type":"alldiff","vars":["Brook","Elm","Dale"]},
    {"type":"alldiff","vars":["Brook","Fern","Dale"]},
    {"type":"alldiff","vars":["Brook","Glen","Dale"]},
    {"type":"alldiff","vars":["Cliff","Dale"]},
    {"type":"alldiff","vars":["Elm","Fern","Dale"]},
    {"type":"alldiff","vars":["Elm","Glen","Dale"]},
    {"type":"alldiff","vars":["Fern","Glen","Dale"]},
    {"type":"alldiff","vars":["Heath","Elm","Dale"]},
    {"type":"alldiff","vars":["Heath","Fern","Dale"]},
    {"type":"alldiff","vars":["Heath","Glen","Dale"]}
  ]
}
```

## q08 — Premisas omitidas / sub-restricción

**Resultado original:** incorrect. **Señal:** `none`. **Detección automática sin gold:** No.

**Revisión:** Solo conserva all-different y Coin=4; omite exclusiones de Bell, Aspen y Drum.

**Salida literal de Ollama (brazo B):**

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

## q10 — Desajuste de tipos (números como cadenas)

**Resultado original:** incorrect. **Señal:** `none`. **Detección automática sin gold:** No.

**Revisión:** La asignación satisface el enunciado y coincide con gold al convertir cadenas numéricas; la comparación estricta falla.

**Salida literal de Ollama (brazo B):**

```json
{
  "variables": {
    "Alder": ["1", "2", "3", "4", "5"],
    "Birch": ["1", "2", "3", "4", "5"],
    "Cedar": ["1", "2", "3", "4", "5"],
    "Dune": ["1", "2", "3", "4", "5"],
    "Elm": ["1", "2", "3", "4", "5"]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Alder", "Birch", "Cedar", "Dune", "Elm"]},
    {"type": "neq", "a": "Cedar", "b": "1"},
    {"type": "neq", "a": "Cedar", "b": "2"},
    {"type": "neq", "a": "Cedar", "b": "4"},
    {"type": "neq", "a": "Birch", "b": "1"},
    {"type": "neq", "a": "Birch", "b": "4"},
    {"type": "neq", "a": "Alder", "b": "4"},
    {"type": "eq", "a": "Elm", "b": "5"}
  ]
}
```

## q11 — Sobre-restricción / UNSAT

**Resultado original:** no_answer. **Señal:** `unsat`. **Detección automática sin gold:** Sí.

**Revisión:** Obliga a seis variables a ser todas diferentes aunque solo hay tres valores disponibles; contradice las repeticiones permitidas.

**Salida literal de Ollama (brazo B):**

```json
{
  "variables": {
    "A": ["1", "2", "3"],
    "B": ["1", "2", "3"],
    "C": ["1", "2", "3"],
    "D": ["1", "2", "3"],
    "E": ["1", "2", "3"],
    "F": ["1", "2", "3"]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["A", "B", "C", "D", "E", "F"]},
    {"type": "eq", "a": "A", "b": "1"},
    {"type": "eq", "a": "B", "b": "2"}
  ]
}
```

## q12 — Sobre-restricción / UNSAT

**Resultado original:** no_answer. **Señal:** `unsat`. **Detección automática sin gold:** Sí.

**Revisión:** Añade restricciones incompatibles: Dia≠1 y Dia=1; también alldiff imposible para seis variables sobre tres valores.

**Salida literal de Ollama (brazo B):**

```json
{
  "variables": {
    "Ava": [1],
    "Ben": [2, 3],
    "Cai": [2, 3],
    "Dia": [1, 2, 3],
    "Eli": [1, 2, 3],
    "Fox": [1, 2, 3]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Ava", "Ben", "Cai", "Dia", "Eli", "Fox"]},
    {"type": "eq", "a": "Ava", "b": 1},
    {"type": "neq", "a": "Ava", "b": 2},
    {"type": "neq", "a": "Dia", "b": 1},
    {"type": "neq", "a": "Dia", "b": 2},
    {"type": "neq", "a": "Eli", "b": 1},
    {"type": "neq", "a": "Eli", "b": 2},
    {"type": "neq", "a": "Fox", "b": 2},
    {"type": "neq", "a": "Fox", "b": 3},
    {"type": "eq", "a": "Dia", "b": 1},
    {"type": "neq", "a": "Ben", "b": 3},
    {"type": "neq", "a": "Eli", "b": 1},
    {"type": "neq", "a": "Fox", "b": 1}
  ]
}
```

## q13 — Sobre-restricción / UNSAT

**Resultado original:** no_answer. **Señal:** `unsat`. **Detección automática sin gold:** Sí.

**Revisión:** AfternoonE es simultáneamente igual a 1, 2, 3 y 4, lo que imposibilita cualquier solución.

**Salida literal de Ollama (brazo B):**

```json
{
  "variables": {
    "MorningA": ["1"],
    "MorningB": ["2"],
    "MorningC": ["3"],
    "MorningD": ["4"],
    "AfternoonE": ["1", "2", "3", "4"],
    "AfternoonF": ["1", "2", "3", "4"],
    "AfternoonG": ["1", "2", "3", "4"]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["MorningA", "MorningB", "MorningC", "MorningD"]},
    {"type": "eq", "a": "AfternoonE", "b": "1"},
    {"type": "eq", "a": "AfternoonE", "b": "2"},
    {"type": "eq", "a": "AfternoonE", "b": "3"},
    {"type": "eq", "a": "AfternoonE", "b": "4"},
    {"type": "neq", "a": "AfternoonE", "b": "MorningA"},
    {"type": "neq", "a": "AfternoonE", "b": "MorningB"},
    {"type": "neq", "a": "AfternoonE", "b": "MorningC"},
    {"type": "neq", "a": "AfternoonE", "b": "MorningD"},
    {"type": "alldiff", "vars": ["AfternoonF", "MorningB", "MorningC", "MorningD"]},
    {"type": "neq", "a": "AfternoonF", "b": "MorningB"},
    {"type": "neq", "a": "AfternoonF", "b": "MorningC"},
    {"type": "neq", "a": "AfternoonF", "b": "MorningD"},
    {"type": "alldiff", "vars": ["AfternoonG", "MorningA", "MorningC", "MorningD"]}
  ]
}
```

## q14 — Error de alcance de alldiff → UNSAT

**Resultado original:** no_answer. **Señal:** `unsat`. **Detección automática sin gold:** Sí.

**Revisión:** Aplica all-different a las nueve casillas de sudoku 3×3; solo existen tres valores y se requieren restricciones por fila/columna.

**Salida literal de Ollama (brazo B):**

```json
{"variables":{"R1C1":[1],"R1C2":[2],"R1C3":[3],"R2C1":[2],"R2C2":[3],"R2C3":[1],"R3C1":[3],"R3C2":[1],"R3C3":[2]}, "constraints":[{"type":"alldiff","vars":["R1C1","R2C1","R3C1","R1C2","R2C2","R3C2","R1C3","R2C3","R3C3"]},{"type":"alldiff","vars":["R1C1","R2C1","R3C1","R1C2","R2C2","R3C2","R1C3","R2C3","R3C3"]}]}
```

## q17 — Premisas omitidas / campo no reconocido

**Resultado original:** incorrect. **Señal:** `none`. **Detección automática sin gold:** No.

**Revisión:** Solo codifica Aster=4; mueve las pistas Birch=1 y Cedar=5 a un campo given que no es una restricción del solver.

**Salida literal de Ollama (brazo B):**

```json
{"variables":{"Aster":["1","2","3","4","5"],"Birch":["1","2","3","4","5"],"Cedar":["1","2","3","4","5"],"Dahlia":["1","2","3","4","5"],"Elm":["1","2","3","4","5"]},"constraints":[{"type":"alldiff","vars":["Aster","Birch","Cedar","Dahlia","Elm"]},{"type":"eq","a":"Aster","b":"4"}],"given":{"Birch":"1","Cedar":"5"}}
```

## q18 — Premisas omitidas / sub-restricción

**Resultado original:** incorrect. **Señal:** `none`. **Detección automática sin gold:** No.

**Revisión:** Codifica solo Ava=5 y all-different; omite las pistas de Bela, Cora, Dina y Eli.

**Salida literal de Ollama (brazo B):**

```json
{"variables":{"Ava":[1,2,3,4,5,6],"Bela":[1,2,3,4,5,6],"Cora":[1,2,3,4,5,6],"Dina":[1,2,3,4,5,6],"Eli":[1,2,3,4,5,6],"Fina":[1,2,3,4,5,6]},"constraints":[{"type":"alldiff","vars":["Ava","Bela","Cora","Dina","Eli","Fina"]},{"type":"eq","a":"Ava","b":5}]}
```

## q19 — Sintaxis JSON malformada

**Resultado original:** no_answer. **Señal:** `malformed_model`. **Detección automática sin gold:** Sí.

**Revisión:** El parser rechaza el JSON inicial; tres correcciones repiten errores de sintaxis.

**Salida literal de Ollama (brazo B):**

```json
{"variables":{"Amber":[3],"Bronze":[7],"Coral":[1],"Diamond":[5],"Emerald":[2],"Flint":[4,6],"Garnet":[1,2,3,4,5,6,7]"},"constraints":[{"type":"alldiff","vars":["Amber","Bronze","Coral","Diamond","Emerald"]},{"type":"eq","a":"Amber","b":3},{"type":"eq","a":"Bronze","b":7},{"type":"eq","a":"Coral","b":1},{"type":"eq","a":"Diamond","b":5},{"type":"eq","a":"Emerald","b":2},{"type":"neq","a":"Flint","b":4}]}
```

## q20 — Modelo de otro alcance: variable omitida

**Resultado original:** incorrect. **Señal:** `none`. **Detección automática sin gold:** No.

**Revisión:** No incluye Hydra, solo siete de ocho satélites, y omite el detalle de Gemini.

**Salida literal de Ollama (brazo B):**

```json
{"variables":{"Aquila":["1","2","3","4","5","6","7","8"],"Boreal":["1","2","3","4","5","6","7","8"],"Cygnus":["1","2","3","4","5","6","7","8"],"Draco":["1","2","3","4","5","6","7","8"],"Equuleus":["1","2","3","4","5","6","7","8"],"Fornax":["1","2","3","4","5","6","7","8"],"Gemini":["1","2","3","4","5","6","7","8"]},"constraints":[{"type":"alldiff","vars":["Aquila","Boreal","Cygnus","Draco","Equuleus","Fornax","Gemini"]},{"type":"eq","a":"Aquila","b":"8"},{"type":"eq","a":"Boreal","b":"3"},{"type":"eq","a":"Cygnus","b":"6"},{"type":"eq","a":"Draco","b":"1"},{"type":"eq","a":"Equuleus","b":"7"},{"type":"eq","a":"Fornax","b":"2"}]}
```

## Brazo C: detectabilidad

En las 13 respuestas incorrectas de C, las ejecuciones registran `signal=none`. No hubo rechazo de parser ni diagnóstico de solver; se requeriría comprobar las premisas o contrastar con una referencia. **0/13 fallos anunciados automáticamente**, con el detector aplicado en este experimento.
