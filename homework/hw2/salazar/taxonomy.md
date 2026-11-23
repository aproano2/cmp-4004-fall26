# Taxonomía de errores del brazo B

Modelo: `qwen2.5:3b`. Intentos de B: 63; fallos: 60. Cada fallo de B (primer intento, sin refinamiento) está clasificado abajo con la salida del modelo.

| Categoría | Fallos | % de fallos | ¿Detectable sin ground truth? | ¿Lo detectamos en nuestros datos? |
|---|---|---|---|---|
| Sintaxis rota (no parsea) | 34 | 57 % | Sí | sí, en los 34 |
| Sintaxis válida, sobre-restringido (sin solución) | 11 | 18 % | Sí | sí, en los 11 |
| Sintaxis válida, sub-restringido (varias soluciones, devolvió una equivocada) | 3 | 5 % | A veces (sí, si el solver cuenta soluciones) | sí, en los 3 |
| Modelo válido del problema equivocado (premisas perdidas o inventadas) | 0 | 0 % | No | - |
| Errores de alcance / aridad (variable inexistente, argumentos o tipos mal) | 9 | 15 % | A veces (sí, cuando rompe el modelo) | sí, en los 9 |
| Timeout del solver | 0 | 0 % | Sí | - |
| El LLM no terminó en 300 s (no hubo modelo) | 3 | 5 % | Sí | sí, en los 3 |
Con un parser más tolerante (análisis de honestidad; no cambia la clasificación), de estos 60 fallos serían correctos: 0 cerrando la llave final que falta, 0 convirtiendo números escritos como texto y 0 con ambos arreglos.

**Fallos de B detectables sin ground truth: 60/60 (100 %).**

## Cada fallo, con la salida del modelo

### dificil-02 · semilla 1 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #0 (offset) uses 'Unload', which is neither a variable nor a possible value of 'Register' (possible values: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]).
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.

```json
{
  "variables": {
    "Align": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Caption": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Drill": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Dust": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Inspect": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Level": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Light": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Measure": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Mount": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Open": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Photograph": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Place": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Register": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Review": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Seal": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
    "Sign": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
  },
  "constraints": [
    {"clue": 1, "type": "offset", "a": "Register", "b": "Unload", "k": 1},
    {"clue": 2, "type": "offset", "a": "Measure", "b": "Register", "k": 1},
    {"clue": 3, "type": "offset", "a": "Mount", "b": "Drill", "k": 1},
    {"clue": 4, "type": "offset", "a": "Level", "b": "Mount", "k": 1},
    {"clue": 5, "type": "offset", "a": "Test", "b": "Wire", "k": 1},
    {"clue": 6, "type": "offset", "a": "Inspect", "b": "Unwrap", "k": 1},
    {"clue": 7, "type": "offset", "a": "Place", "b": "Inspect", "k": 1},
    {"clue": 8, "type": "offset", "a": "Align", "b": "Place", "k": 1},
    {"clue": 9, "type": "offset", "a": "Light", "b": "Caption", "k": 1},
    {"clue": 10, "type": "offset", "a": "Photograph", "b": "Light", "k": 1},
    {"clue": 11, "type": "offset", "a": "Dust", "b": "Unwrap", "k": 1},
    {"clue": 12, "type": "offset", "a": "Sign", "b": "Review", "k": 1},
    {"clue": 13, "type": "offset", "a": "Open", "b": "Sign", "k": 1},
    {"clue": 14, "type": "eq", "a": "Unwrap", "b": 9},
    {"clue": 15, "type": "lt", "a": "Measure", "b": "Drill"},
    {"clue": 16, "type": "lt", "a": "Level", "b": "Wire"},
    {"clue": 17, "type": "lt", "a": "Test", "b": "Unwrap"},
    {"clue": 18, "type": "offset", "a": "Caption", "b": "Align", "k": 1},
    {"clue": 19, "type": "lt", "a": "Photograph", "b": "Dust"},
    {"clue": 20, "type": "lt", "a": "Seal", "b": "Review"}
  ]
}
```

### dificil-06 · semilla 1 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #2 (offset) compares numbers but 'Tunnel' has non-numeric values.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.

```json
{
  "variables": {
    "Switch": ["red", "green", "blue"],
    "Signal": ["red", "green", "blue"],
    "Tunnel": ["red", "green", "blue"],
    "Siding": ["red", "green", "blue"],
    "Track": ["red", "green", "blue"],
    "Cabin": ["red", "green", "blue"],
    "Platform": ["red", "green", "blue"],
    "Tower": ["red", "green", "blue"],
    "Viaduct": ["red", "green", "blue"],
    "Furnace": ["red", "green", "blue"],
    "Gate": ["red", "green", "blue"],
    "Station": ["red", "green", "blue"],
    "Loop": ["red", "green", "blue"],
    "Workshop": ["red", "green", "blue"],
    "Relay": ["red", "green", "blue"],
    "Depot": ["red", "green", "blue"],
    "Crane": ["red", "green", "blue"],
    "Fence": ["red", "green", "blue"],
    "Point": ["red", "green", "blue"],
    "Bridge": ["red", "green", "blue"],
    "Trench": ["red", "green", "blue"],
    "Shed": ["red", "green", "blue"],
    "Ramp": ["red", "green", "blue"],
    "Gantry": ["red", "green", "blue"],
    "Lane": ["red", "green", "blue"]
  },
  "constraints": [
    {"clue": 1, "type": "eq", "a": "Switch", "b": "green"},
    {"clue": 2, "type": "eq", "a": "Signal", "b": "red"},
    {"clue": 3, "type": "offset", "a": "Tunnel", "b": "Switch", "k": 1},
    {"clue": 4, "type": "alldiff", "vars": ["Signal", "Tower", "Tunnel", "Workshop"]},
    {"clue": 5, "type": "alldiff", "vars": ["Siding", "Track", "Tunnel", "Viaduct"]},
    {"clue": 6, "type": "eq", "a": "Track", "b": "Tunnel"},
    {"clue": 7, "type": "alldiff", "vars": ["Cabin", "Signal", "Track"]},
    {"clue": 8, "type": "eq", "a": "Platform", "b": "Switch"},
    {"clue": 9, "type": "alldiff", "vars": ["Tower", "Track", "Viaduct"]},
    {"clue": 10, "type": "alldiff", "vars": ["Station", "Tower", "Workshop"]},
    {"clue": 11, "type": "alldiff", "vars": ["Loop", "Tower", "Viaduct"]},
    {"clue": 12, "type": "alldiff", "vars": ["Workshop", "Track", "Trench"]},
    {"clue": 13, "type": "alldiff", "vars": ["Depot", "Furnace", "Signal"]},
    {"clue": 14, "type": "alldiff", "vars": ["Crane", "Gate", "Platform"]},
    {"clue": 15, "type": "alldiff", "vars": ["Fence", "Point", "Relay", "Tower"]},
    {"clue": 16, "type": "alldiff", "vars": ["Bridge", "Trench", "Viaduct", "Workshop"]},
    {"clue": 17, "type": "alldiff", "vars": ["Shed", "Signal", "Viaduct", "Workshop"]},
    {"clue": 18, "type": "alldiff", "vars": ["Relay", "Track", "Trench"]},
    {"clue": 19, "type": "alldiff", "vars": ["Depot", "Furnace", "Gantry", "Signal"]},
    {"clue": 20, "type": "alldiff", "vars": ["Crane", "Fence", "Platform"]},
    {"clue": 21, "type": "alldiff", "vars": ["Lane", "Ramp", "Track", "Trench"]}
  ]
}
```

### facil-03 · semilla 2 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #3 (offset) compares numbers but 'Ford' has non-numeric values.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: traduce los enlaces del mapa ("Ford–Gorge") como `offset` ("a la derecha de") sobre colores, y además pone todas las regiones en un `alldiff`.

```json
{"variables": {"Rim": ["red", "green", "blue"], "Ford": ["red", "green", "blue"], "Gorge": ["red", "green", "blue"], "Dune": ["red", "green", "blue"], "Marsh": ["red", "green", "blue"], "Cliff": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Rim", "Ford", "Gorge", "Dune", "Marsh", "Cliff"]}, {"clue": 1, "type": "eq", "a": "Rim", "b": "red"}, {"clue": 2, "type": "eq", "a": "Ford", "b": "green"}, {"clue": 3, "type": "offset", "a": "Ford", "b": "Gorge", "k": 1}, {"clue": 3, "type": "offset", "a": "Ford", "b": "Marsh", "k": 1}, {"clue": 3, "type": "offset", "a": "Ford", "b": "Rim", "k": 1}, {"clue": 4, "type": "adj", "a": "Gorge", "b": "Rim"}, {"clue": 5, "type": "offset", "a": "Dune", "b": "Ford", "k": 1}, {"clue": 5, "type": "offset", "a": "Dune", "b": "Gorge", "k": 1}, {"clue": 5, "type": "offset", "a": "Dune", "b": "Marsh", "k": 1}, {"clue": 6, "type": "offset", "a": "Cliff", "b": "Dune", "k": 1}, {"clue": 6, "type": "offset", "a": "Cliff", "b": "Marsh", "k": 1}]}
```

### facil-06 · semilla 0 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #4 (adj) compares numbers but 'Plaza' has non-numeric values.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.

```json
{"variables": {"Plaza": ["red", "green", "blue"], "Gate": ["red", "green", "blue"], "Tent": ["red", "green", "blue"], "Stage": ["red", "green", "blue"], "Court": ["red", "green", "blue"], "Lawn": ["red", "green", "blue"], "Deck": ["red", "green", "blue"], "Ramp": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Plaza", "Gate", "Tent"]}, {"clue": 0, "type": "alldiff", "vars": ["Stage", "Court", "Lawn", "Ramp"]}, {"clue": 1, "type": "eq", "a": "Plaza", "b": "blue"}, {"clue": 2, "type": "eq", "a": "Gate", "b": "red"}, {"clue": 3, "type": "adj", "a": "Plaza", "b": "Tent"}, {"clue": 4, "type": "offset", "a": "Gate", "b": "Stage", "k": 1}, {"clue": 4, "type": "offset", "a": "Gate", "b": "Tent", "k": 1}, {"clue": 5, "type": "adj", "a": "Stage", "b": "Tent"}, {"clue": 6, "type": "adj", "a": "Court", "b": "Lawn"}, {"clue": 6, "type": "adj", "a": "Court", "b": "Stage"}, {"clue": 6, "type": "adj", "a": "Court", "b": "Tent"}, {"clue": 7, "type": "adj", "a": "Lawn", "b": "Plaza"}, {"clue": 7, "type": "adj", "a": "Lawn", "b": "Ramp"}, {"clue": 7, "type": "adj", "a": "Lawn", "b": "Stage"}, {"clue": 8, "type": "adj", "a": "Deck", "b": "Plaza"}, {"clue": 8, "type": "adj", "a": "Deck", "b": "Ramp"}, {"clue": 8, "type": "adj", "a": "Deck", "b": "Stage"}, {"clue": 8, "type": "adj", "a": "Deck", "b": "Tent"}, {"clue": 9, "type": "adj", "a": "Ramp", "b": "Tent"}]}
```

### facil-06 · semilla 2 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #5 (adj) compares numbers but 'Plaza' has non-numeric values.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.

```json
{"variables": {"Plaza": ["red", "green", "blue"], "Gate": ["red", "green", "blue"], "Tent": ["red", "green", "blue"], "Stage": ["red", "green", "blue"], "Court": ["red", "green", "blue"], "Lawn": ["red", "green", "blue"], "Deck": ["red", "green", "blue"], "Ramp": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Plaza", "Gate", "Tent"]}, {"clue": 0, "type": "alldiff", "vars": ["Stage", "Court", "Lawn"]}, {"clue": 0, "type": "alldiff", "vars": ["Stage", "Court", "Ramp"]}, {"clue": 1, "type": "eq", "a": "Plaza", "b": "blue"}, {"clue": 2, "type": "eq", "a": "Gate", "b": "red"}, {"clue": 3, "type": "adj", "a": "Plaza", "b": "Tent"}, {"clue": 4, "type": "adj", "a": "Gate", "b": "Plaza"}, {"clue": 4, "type": "adj", "a": "Gate", "b": "Stage"}, {"clue": 4, "type": "adj", "a": "Gate", "b": "Tent"}, {"clue": 5, "type": "adj", "a": "Stage", "b": "Tent"}, {"clue": 6, "type": "adj", "a": "Court", "b": "Lawn"}, {"clue": 6, "type": "adj", "a": "Court", "b": "Stage"}, {"clue": 6, "type": "adj", "a": "Court", "b": "Tent"}, {"clue": 7, "type": "adj", "a": "Lawn", "b": "Plaza"}, {"clue": 7, "type": "adj", "a": "Lawn", "b": "Ramp"}, {"clue": 7, "type": "adj", "a": "Lawn", "b": "Stage"}, {"clue": 8, "type": "adj", "a": "Deck", "b": "Plaza"}, {"clue": 8, "type": "adj", "a": "Deck", "b": "Ramp"}, {"clue": 8, "type": "adj", "a": "Deck", "b": "Stage"}, {"clue": 8, "type": "adj", "a": "Deck", "b": "Tent"}, {"clue": 9, "type": "adj", "a": "Ramp", "b": "Tent"}]}
```

### medio-03 · semilla 1 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #3 (alldiff) repeats the variable 'Oaks'.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.

```json
{
  "variables": {
    "Library": ["red", "green", "blue"],
    "Bridge": ["red", "green", "blue"],
    "Arena": ["red", "green", "blue"],
    "Lab": ["red", "green", "blue"],
    "Quad": ["red", "green", "blue"],
    "Gym": ["red", "green", "blue"],
    "Oaks": ["red", "green", "blue"],
    "Dorm": ["red", "green", "blue"],
    "Clinic": ["red", "green", "blue"],
    "Pond": ["red", "green", "blue"],
    "Hall": ["red", "green", "blue"],
    "Cafe": ["red", "green", "blue"]
  },
  "constraints": [
    {"clue": 0, "type": "alldiff", "vars": ["Library", "Bridge", "Arena", "Lab", "Quad", "Gym", "Oaks", "Dorm", "Clinic", "Pond", "Hall", "Cafe"]},
    {"clue": 1, "type": "eq", "a": "Library", "b": "green"},
    {"clue": 2, "type": "eq", "a": "Bridge", "b": "blue"},
    {"clue": 3, "type": "alldiff", "vars": ["Library", "Oaks", "Pond", "Lab", "Quad", "Gym", "Oaks", "Dorm", "Clinic", "Pond", "Hall", "Cafe"]},
    {"clue": 4, "type": "alldiff", "vars": ["Bridge", "Cafe", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab"]},
    {"clue": 5, "type": "alldiff", "vars": ["Arena", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab"]},
    {"clue": 6, "type": "eq", "a": "Lab", "b": "Quad"},
    {"clue": 7, "type": "alldiff", "vars": ["Gym", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab"]},
    {"clue": 8, "type": "alldiff", "vars": ["Dorm", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab"]},
    {"clue": 9, "type": "alldiff", "vars": ["Clinic", "Dorm", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab"]},
    {"clue": 10, "type": "alldiff", "vars": ["Hall", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab"]},
    {"clue": 11, "type": "alldiff", "vars": ["Cafe", "Dorm", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab", "Lab"]}
  ]
}
```

### medio-03 · semilla 2 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #3 (offset) compares numbers but 'Library' has non-numeric values.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.

```json
{"variables": {"Library": ["red", "green", "blue"], "Bridge": ["red", "green", "blue"], "Arena": ["red", "green", "blue"], "Lab": ["red", "green", "blue"], "Quad": ["red", "green", "blue"], "Gym": ["red", "green", "blue"], "Oaks": ["red", "green", "blue"], "Dorm": ["red", "green", "blue"], "Clinic": ["red", "green", "blue"], "Pond": ["red", "green", "blue"], "Hall": ["red", "green", "blue"], "Cafe": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Library", "Bridge", "Arena", "Lab", "Quad", "Gym", "Oaks", "Dorm", "Clinic", "Pond", "Hall", "Cafe"]}, {"clue": 1, "type": "eq", "a": "Library", "b": "green"}, {"clue": 2, "type": "eq", "a": "Bridge", "b": "blue"}, {"clue": 3, "type": "offset", "a": "Library", "b": "Oaks", "k": 1}, {"clue": 3, "type": "offset", "a": "Library", "b": "Pond", "k": 1}, {"clue": 4, "type": "offset", "a": "Bridge", "b": "Cafe", "k": 1}, {"clue": 4, "type": "offset", "a": "Bridge", "b": "Lab", "k": 1}, {"clue": 4, "type": "offset", "a": "Bridge", "b": "Oaks", "k": 1}, {"clue": 4, "type": "offset", "a": "Bridge", "b": "Quad", "k": 1}, {"clue": 5, "type": "offset", "a": "Arena", "b": "Bridge", "k": 1}, {"clue": 5, "type": "offset", "a": "Arena", "b": "Gym", "k": 1}, {"clue": 5, "type": "offset", "a": "Arena", "b": "Lab", "k": 1}, {"clue": 5, "type": "offset", "a": "Arena", "b": "Library", "k": 1}, {"clue": 6, "type": "eq", "a": "Lab", "b": "Quad"}, {"clue": 7, "type": "offset", "a": "Gym", "b": "Lab", "k": 1}, {"clue": 7, "type": "offset", "a": "Gym", "b": "Pond", "k": 1}, {"clue": 7, "type": "offset", "a": "Gym", "b": "Quad", "k": 1}, {"clue": 8, "type": "offset", "a": "Dorm", "b": "Lab", "k": 1}, {"clue": 8, "type": "offset", "a": "Dorm", "b": "Oaks", "k": 1}, {"clue": 8, "type": "offset", "a": "Dorm", "b": "Pond", "k": 1}, {"clue": 9, "type": "offset", "a": "Clinic", "b": "Dorm", "k": 1}, {"clue": 9, "type": "offset", "a": "Clinic", "b": "Quad", "k": 1}, {"clue": 10, "type": "offset", "a": "Hall", "b": "Lab", "k": 1}, {"clue": 10, "type": "offset", "a": "Hall", "b": "Oaks", "k": 1}, {"clue": 10, "type": "offset", "a": "Hall", "b": "Pond", "k": 1}, {"clue": 11, "type": "offset", "a": "Cafe", "b": "Dorm", "k": 1}, {"clue": 11, "type": "offset", "a": "Cafe", "b": "Pond", "k": 1}]}
```

### medio-06 · semilla 0 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #2 (offset) compares numbers but 'Pier' has non-numeric values.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.

```json
{"variables": {"Pier": ["red"], "Jetty": ["blue"], "Bay": ["red", "green", "blue"], "Ramp": ["red", "green", "blue"], "Basin": ["red", "green", "blue"], "Lock": ["red", "green", "blue"], "Quay": ["red", "green", "blue"], "Depot": ["red", "green", "blue"], "Crane": ["red", "green", "blue"], "Yard": ["red", "green", "blue"], "Float": ["red", "green", "blue"], "Slip": ["red", "green", "blue"], "Reef": ["red", "green", "blue"], "Mole": ["red", "green", "blue"], "Inlet": ["red", "green", "blue"]}, "constraints": [{"clue": 1, "type": "eq", "a": "Pier", "b": "red"}, {"clue": 2, "type": "eq", "a": "Jetty", "b": "blue"}, {"clue": 3, "type": "offset", "a": "Pier", "b": "Yard", "k": 1}, {"clue": 4, "type": "offset", "a": "Jetty", "b": "Pier", "k": 1}, {"clue": 4, "type": "offset", "a": "Jetty", "b": "Ramp", "k": 1}, {"clue": 5, "type": "alldiff", "vars": ["Bay", "Inlet", "Jetty", "Pier", "Quay"]}, {"clue": 6, "type": "eq", "a": "Ramp", "b": "Slip"}, {"clue": 7, "type": "alldiff", "vars": ["Basin", "Depot", "Jetty", "Lock", "Pier", "Reef"]}, {"clue": 8, "type": "alldiff", "vars": ["Lock", "Mole", "Ramp", "Yard"]}, {"clue": 9, "type": "eq", "a": "Quay", "b": "Ramp"}, {"clue": 10, "type": "alldiff", "vars": ["Depot", "Inlet", "Quay", "Slip"]}, {"clue": 11, "type": "alldiff", "vars": ["Crane", "Depot", "Lock", "Pier"]}, {"clue": 12, "type": "alldiff", "vars": ["Float", "Jetty", "Lock"]}, {"clue": 13, "type": "eq", "a": "Slip", "b": "Yard"}, {"clue": 14, "type": "eq", "a": "Reef", "b": "Slip"}, {"clue": 15, "type": "alldiff", "vars": ["Mole", "Pier", "Slip"]}]}
```

### medio-06 · semilla 1 · `aridad_alcance`

- Lo que dijo el solver: The solver rejected the model: constraint #2 (adj) compares numbers but 'Pier' has non-numeric values.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: una restricción apunta a una variable que no existe, le faltan argumentos o compara posiciones sobre valores que no son números.

```json
{
  "variables": {
    "Pier": ["red"],
    "Jetty": ["blue"],
    "Bay": ["green", "red", "blue"],
    "Ramp": ["green", "red", "blue"],
    "Basin": ["green", "red", "blue"],
    "Lock": ["green", "red", "blue"],
    "Quay": ["green", "red", "blue"],
    "Depot": ["green", "red", "blue"],
    "Crane": ["green", "red", "blue"],
    "Yard": ["green", "red", "blue"],
    "Float": ["green", "red", "blue"],
    "Slip": ["green", "red", "blue"],
    "Reef": ["green", "red", "blue"],
    "Mole": ["green", "red", "blue"],
    "Inlet": ["green", "red", "blue"]
  },
  "constraints": [
    {"clue": 1, "type": "eq", "a": "Pier", "b": "red"},
    {"clue": 2, "type": "eq", "a": "Jetty", "b": "blue"},
    {"clue": 3, "type": "adj", "a": "Pier", "b": "Yard"},
    {"clue": 4, "type": "offset", "a": "Jetty", "b": "Pier", "k": 1},
    {"clue": 4, "type": "offset", "a": "Jetty", "b": "Ramp", "k": 1},
    {"clue": 5, "type": "alldiff", "vars": ["Bay", "Inlet", "Jetty", "Pier", "Quay"]},
    {"clue": 6, "type": "eq", "a": "Ramp", "b": "Slip"},
    {"clue": 7, "type": "alldiff", "vars": ["Basin", "Jetty", "Lock", "Pier", "Reef"]},
    {"clue": 8, "type": "alldiff", "vars": ["Lock", "Mole", "Ramp", "Yard"]},
    {"clue": 9, "type": "eq", "a": "Quay", "b": "Ramp"},
    {"clue": 10, "type": "alldiff", "vars": ["Depot", "Inlet", "Quay", "Slip"]},
    {"clue": 11, "type": "alldiff", "vars": ["Crane", "Depot", "Float", "Lock", "Pier"]},
    {"clue": 12, "type": "alldiff", "vars": ["Float", "Jetty", "Lock"]},
    {"clue": 13, "type": "eq", "a": "Slip", "b": "Yard"},
    {"clue": 14, "type": "eq", "a": "Reef", "b": "Slip"},
    {"clue": 15, "type": "alldiff", "vars": ["Mole", "Pier", "Slip"]}
  ]
}
```

### dificil-05 · semilla 0 · `no_termina`

- Lo que dijo el solver: LLM: no_termina
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el LLM no terminó de responder en 300 s.

```json

```

### dificil-05 · semilla 1 · `no_termina`

- Lo que dijo el solver: LLM: no_termina
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el LLM no terminó de responder en 300 s.

```json

```

### dificil-05 · semilla 2 · `no_termina`

- Lo que dijo el solver: LLM: no_termina
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el LLM no terminó de responder en 300 s.

```json

```

### dificil-01 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1834.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Alma": [1, 2, 3, 4, 5], "Bear": [1, 2, 3, 4, 5], "Compass": [1, 2, 3, 4, 5], "Deer": [1, 2, 3, 4, 5], "Flask": [1, 2, 3, 4, 5], "Fox": [1, 2, 3, 4, 5], "Gold": [1, 2, 3, 4, 5], "Hare": [1, 2, 3, 4, 5], "Jade": [1, 2, 3, 4, 5], "Lilac": [1, 2, 3, 4, 5], "Luis": [1, 2, 3, 4, 5], "Nico": [1, 2, 3, 4, 5], "Owl": [1, 2, 3, 4, 5], "Red": [1, 2, 3, 4, 5], "Rope": [1, 2, 3, 4, 5], "Rosa": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5], "Torch": [1, 2, 3, 4, 5], "Whistle": [1, 2, 3, 4, 5], "White": [1, 2, 3, 4, 5]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Alma", "Bear", "Compass", "Deer", "Flask", "Fox", "Gold", "Hare", "Jade", "Lilac", "Luis", "Nico", "Owl", "Red", "Rope", "Rosa", "Tomas", "Torch", "Whistle", "White"]}, {"clue": 1, "type": "offset", "a": "Alma", "b": "Tomas", "k": 1}, {"clue": 2, "type": "eq", "a": "Luis", "b": 3}, {"clue": 3, "type": "gt", "a": "Rosa", "b": "Luis"}, {"clue": 4, "type": "lt", "a": "Tomas", "b": "Luis"}, {"clue": 5, "type": "lt", "a": "Rosa", "b": "Nico"}, {"clue": 6, "type": "eq", "a": "White", "b": "Alma"}, {"clue": 7, "type": "adj", "a": "Red", "b": "White"}, {"clue": 8, "type": "lt", "a": "Red", "b": "White"}, {"clue": 9, "type": "offset", "a": "Gold", "b": "Jade", "k": 1}, {"clue": 10, "type": "gt", "a": "Lilac", "b": "Gold"}, {"clue": 11, "type": "eq", "a": "Gold", "b": "Bear"}, {"clue": 12, "type": "offset", "a": "Hare", "b": "Bear", "k": -1}, {"clue": 13, "type": "lt", "a": "Owl", "b": "Fox"}, {"clue": 14, "type": "lt", "a": "Fox", "b": "Hare"}, {"clue": 15, "type": "eq", "a": "Flask", "b": "Fox"}, {"clue": 16, "type": "offset", "a": "Compass", "b": "Flask", "k": 1}, {"clue": 17, "type": "lt", "a": "Compass", "b": "Flask"}, {"clue": 18, "type": "offset", "a": "Rope", "b": "Torch", "k": 1}, {"clue": 19, "type": "gt", "a": "Rope", "b": "Flask"}}
```

### dificil-01 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1828.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Alma": [1, 2, 3, 4, 5], "Bear": [1, 2, 3, 4, 5], "Compass": [1, 2, 3, 4, 5], "Deer": [1, 2, 3, 4, 5], "Flask": [1, 2, 3, 4, 5], "Fox": [1, 2, 3, 4, 5], "Gold": [1, 2, 3, 4, 5], "Hare": [1, 2, 3, 4, 5], "Jade": [1, 2, 3, 4, 5], "Lilac": [1, 2, 3, 4, 5], "Luis": [1, 2, 3, 4, 5], "Nico": [1, 2, 3, 4, 5], "Owl": [1, 2, 3, 4, 5], "Red": [1, 2, 3, 4, 5], "Rope": [1, 2, 3, 4, 5], "Rosa": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5], "Torch": [1, 2, 3, 4, 5], "Whistle": [1, 2, 3, 4, 5], "White": [1, 2, 3, 4, 5]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Alma", "Luis", "Rosa", "Tomas"]}, {"clue": 0, "type": "alldiff", "vars": ["Gold", "Jade", "Lilac"]}, {"clue": 0, "type": "alldiff", "vars": ["Bear", "Hare", "Owl"]}, {"clue": 1, "type": "offset", "a": "Alma", "b": "Tomas", "k": 1}, {"clue": 2, "type": "eq", "a": "Luis", "b": 3}, {"clue": 3, "type": "neq", "a": "Rosa", "b": "Luis"}, {"clue": 4, "type": "neq", "a": "Tomas", "b": "Luis"}, {"clue": 5, "type": "neq", "a": "Rosa", "b": "Nico"}, {"clue": 6, "type": "eq", "a": "White", "b": "Alma"}, {"clue": 7, "type": "adj", "a": "Red", "b": "White"}, {"clue": 8, "type": "lt", "a": "Red", "b": "White"}, {"clue": 9, "type": "offset", "a": "Gold", "b": "Jade", "k": 1}, {"clue": 10, "type": "neq", "a": "Lilac", "b": "Gold"}, {"clue": 11, "type": "eq", "a": "Gold", "b": "Bear"}, {"clue": 12, "type": "offset", "a": "Hare", "b": "Bear", "k": -1}, {"clue": 13, "type": "lt", "a": "Owl", "b": "Hare"}, {"clue": 14, "type": "lt", "a": "Fox", "b": "Hare"}, {"clue": 15, "type": "eq", "a": "Flask", "b": "Fox"}, {"clue": 16, "type": "adj", "a": "Compass", "b": "Flask"}, {"clue": 17, "type": "lt", "a": "Compass", "b": "Flask"}, {"clue": 18, "type": "offset", "a": "Rope", "b": "Torch", "k": 1}, {"clue": 19, "type": "neq", "a": "Whistle", "b": "Rope"}}
```

### dificil-02 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 3230.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Align": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Caption": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Drill": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Dust": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Inspect": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Level": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Light": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Measure": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Mount": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Open": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Photograph": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Place": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Register": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Review": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Seal": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Sign": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Test": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Unload": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Unwrap": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Wire": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Align", "Caption", "Drill", "Dust", "Inspect", "Level", "Light", "Measure", "Mount", "Open", "Photograph", "Place", "Register", "Review", "Seal", "Sign", "Test", "Unload", "Unwrap", "Wire"]}, {"clue": 1, "type": "eq", "a": "Register", "b": "Unload + 1"}, {"clue": 2, "type": "eq", "a": "Measure", "b": "Register + 1"}, {"clue": 3, "type": "offset", "a": "Mount", "b": "Drill + 1", "k": 1}, {"clue": 4, "type": "offset", "a": "Level", "b": "Mount + 1", "k": 1}, {"clue": 5, "type": "offset", "a": "Test", "b": "Wire + 1", "k": 1}, {"clue": 6, "type": "offset", "a": "Inspect", "b": "Unwrap + 1", "k": 1}, {"clue": 7, "type": "offset", "a": "Place", "b": "Inspect + 1", "k": 1}, {"clue": 8, "type": "offset", "a": "Align", "b": "Place + 1", "k": 1}, {"clue": 9, "type": "offset", "a": "Light", "b": "Caption + 1", "k": 1}, {"clue": 10, "type": "offset", "a": "Photograph", "b": "Light + 1", "k": 1}, {"clue": 11, "type": "neq", "a": "Dust", "b": "Unload"}, {"clue": 12, "type": "offset", "a": "Sign", "b": "Review + 1", "k": 1}, {"clue": 13, "type": "offset", "a": "Open", "b": "Sign + 1", "k": 1}, {"clue": 14, "type": "eq", "a": "Unwrap", "b": 9}, {"clue": 15, "type": "lt", "a": "Measure", "b": "Drill"}, {"clue": 16, "type": "lt", "a": "Level", "b": "Wire"}, {"clue": 17, "t
```

### dificil-03 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Delta": ["red", "green", "blue"], "Pines": ["red", "green", "blue"], "Falls": ["red", "green", "blue"], "Hollow": ["red", "green", "blue"], "Cove": ["red", "green", "blue"], "Crest": ["red", "green", "blue"], "Meadow": ["red", "green", "blue"], "Pool": ["red", "green", "blue"], "Bank": ["red", "green", "blue"], "Moss": ["red", "green", "blue"], "Birch": ["red", "green", "blue"], "Heath": ["red", "green", "blue"], "Hill": ["red", "green", "blue"], "Fen": ["red", "green", "blue"], "Spur": ["red", "green", "blue"], "Shoal": ["red", "green", "blue"], "Grove": ["red", "green", "blue"], "Dale": ["red", "green", "blue"], "Pass": ["red", "green", "blue"], "Lagoon": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Delta", "Pines", "Falls", "Hollow", "Cove", "Crest", "Meadow", "Pool", "Bank", "Moss", "Birch", "Heath", "Hill", "Fen", "Spur", "Shoal", "Grove", "Dale", "Pass", "Lagoon"]}, {"clue": 1, "type": "eq", "a": "Delta", "b": "blue"}, {"clue": 2, "type": "eq", "a": "Pines", "b": "green"}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Falls", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Hollow", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pass", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pines", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pool", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Hollow", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Meadow", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Moss", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Pines", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Shoal", "k": 1}, {"clue": 5, "type": "offset", "a": "Hollow", "b": "Pass", "k": 1}, {"clue": 5, "type": "offset", "a": "Hollow", "b": "Shoal", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Crest", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Falls", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Heath", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Hill", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Hollow", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Heath", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Hill", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Pool", "k": 1}, {"clue": 8, "type": "eq", "a": "Meadow", "b": "Pines"}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Cove", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Dale", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Fen", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Pool", "k": 1}, {"clue": 10, "type": "offset", "a": "Moss", "b": "Pines", "k": 1}, {"clue": 10, "type": "offset", "a": "Moss", "b": "Spur", "k": 1}, {"clue": 11, "type": "offset", "a": "Birch", "b": "Crest", "k": 1}, {"clue": 11, "type": "offset", "a": "Birch", "b": "Hill", "k": 1}, {"clue": 11, "type": "offset", "a"
```

### dificil-03 · semilla 1 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Delta": ["red", "green", "blue"], "Pines": ["red", "green", "blue"], "Falls": ["red", "green", "blue"], "Hollow": ["red", "green", "blue"], "Cove": ["red", "green", "blue"], "Crest": ["red", "green", "blue"], "Meadow": ["red", "green", "blue"], "Pool": ["red", "green", "blue"], "Bank": ["red", "green", "blue"], "Moss": ["red", "green", "blue"], "Birch": ["red", "green", "blue"], "Heath": ["red", "green", "blue"], "Hill": ["red", "green", "blue"], "Fen": ["red", "green", "blue"], "Spur": ["red", "green", "blue"], "Shoal": ["red", "green", "blue"], "Grove": ["red", "green", "blue"], "Dale": ["red", "green", "blue"], "Pass": ["red", "green", "blue"], "Lagoon": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Delta", "Pines", "Falls", "Hollow", "Cove", "Crest", "Meadow", "Pool", "Bank", "Moss", "Birch", "Heath", "Hill", "Fen", "Spur", "Shoal", "Grove", "Dale", "Pass", "Lagoon"]}, {"clue": 1, "type": "eq", "a": "Delta", "b": "blue"}, {"clue": 2, "type": "eq", "a": "Pines", "b": "green"}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Falls", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Hollow", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pass", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pines", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pool", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Hollow", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Meadow", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Moss", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Pines", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Shoal", "k": 1}, {"clue": 5, "type": "offset", "a": "Hollow", "b": "Pass", "k": 1}, {"clue": 5, "type": "offset", "a": "Hollow", "b": "Shoal", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Crest", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Falls", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Heath", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Hill", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Hollow", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Heath", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Hill", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Pool", "k": 1}, {"clue": 8, "type": "eq", "a": "Meadow", "b": "Pines"}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Cove", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Dale", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Fen", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Pool", "k": 1}, {"clue": 10, "type": "offset", "a": "Moss", "b": "Pines", "k": 1}, {"clue": 10, "type": "offset", "a": "Moss", "b": "Spur", "k": 1}, {"clue": 11, "type": "offset", "a": "Birch", "b": "Crest", "k": 1}, {"clue": 11, "type": "offset", "a": "Birch", "b": "Hill", "k": 1}, {"clue": 11, "type": "offset", "a"
```

### dificil-03 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Delta": ["red", "green", "blue"], "Pines": ["red", "green", "blue"], "Falls": ["red", "green", "blue"], "Hollow": ["red", "green", "blue"], "Cove": ["red", "green", "blue"], "Crest": ["red", "green", "blue"], "Meadow": ["red", "green", "blue"], "Pool": ["red", "green", "blue"], "Bank": ["red", "green", "blue"], "Moss": ["red", "green", "blue"], "Birch": ["red", "green", "blue"], "Heath": ["red", "green", "blue"], "Hill": ["red", "green", "blue"], "Fen": ["red", "green", "blue"], "Spur": ["red", "green", "blue"], "Shoal": ["red", "green", "blue"], "Grove": ["red", "green", "blue"], "Dale": ["red", "green", "blue"], "Pass": ["red", "green", "blue"], "Lagoon": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Delta", "Pines", "Falls", "Hollow", "Cove", "Crest", "Meadow", "Pool", "Bank", "Moss", "Birch", "Heath", "Hill", "Fen", "Spur", "Shoal", "Grove", "Dale", "Pass", "Lagoon"]}, {"clue": 1, "type": "eq", "a": "Delta", "b": "blue"}, {"clue": 2, "type": "eq", "a": "Pines", "b": "green"}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Falls", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Hollow", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pass", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pines", "k": 1}, {"clue": 3, "type": "offset", "a": "Delta", "b": "Pool", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Hollow", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Meadow", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Moss", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Pines", "k": 1}, {"clue": 4, "type": "offset", "a": "Falls", "b": "Shoal", "k": 1}, {"clue": 5, "type": "offset", "a": "Hollow", "b": "Pass", "k": 1}, {"clue": 5, "type": "offset", "a": "Hollow", "b": "Shoal", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Crest", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Falls", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Heath", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Hill", "k": 1}, {"clue": 6, "type": "offset", "a": "Cove", "b": "Hollow", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Heath", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Hill", "k": 1}, {"clue": 7, "type": "offset", "a": "Crest", "b": "Pool", "k": 1}, {"clue": 8, "type": "eq", "a": "Meadow", "b": "Pines"}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Cove", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Dale", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Fen", "k": 1}, {"clue": 9, "type": "offset", "a": "Bank", "b": "Pool", "k": 1}, {"clue": 10, "type": "offset", "a": "Moss", "b": "Pines", "k": 1}, {"clue": 10, "type": "offset", "a": "Moss", "b": "Spur", "k": 1}, {"clue": 11, "type": "offset", "a": "Birch", "b": "Crest", "k": 1}, {"clue": 11, "type": "offset", "a": "Birch", "b": "Hill", "k": 1}, {"clue": 11, "type": "offset", "a"
```

### dificil-04 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 2280.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Animation": [1, 2, 3, 4, 5], "Arrow": [1, 2, 3, 4, 5], "Bia": [1, 2, 3, 4, 5], "Birch": [1, 2, 3, 4, 5], "Cedar": [1, 2, 3, 4, 5], "Circle": [1, 2, 3, 4, 5], "Comedy": [1, 2, 3, 4, 5], "Dani": [1, 2, 3, 4, 5], "Diamond": [1, 2, 3, 4, 5], "Documentary": [1, 2, 3, 4, 5], "Elio": [1, 2, 3, 4, 5], "Gelato": [1, 2, 3, 4, 5], "Luz": [1, 2, 3, 4, 5], "Maple": [1, 2, 3, 4, 5], "Mystery": [1, 2, 3, 4, 5], "Nachos": [1, 2, 3, 4, 5], "Paz": [1, 2, 3, 4, 5], "Pine": [1, 2, 3, 4, 5], "Popcorn": [1, 2, 3, 4, 5], "Pretzel": [1, 2, 3, 4, 5], "Square": [1, 2, 3, 4, 5], "Star": [1, 2, 3, 4, 5], "Toffee": [1, 2, 3, 4, 5], "Walnut": [1, 2, 3, 4, 5], "Western": [1, 2, 3, 4, 5]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Animation", "Arrow", "Bia", "Birch", "Cedar", "Circle", "Comedy", "Dani", "Diamond", "Documentary", "Elio", "Gelato", "Luz", "Maple", "Mystery", "Nachos", "Paz", "Pine", "Popcorn", "Pretzel", "Square", "Star", "Toffee", "Walnut", "Western"]}, {"clue": 1, "type": "eq", "a": "Luz", "b": 1}, {"clue": 2, "type": "adj", "a": "Elio", "b": "Luz"}, {"clue": 3, "type": "offset", "a": "Paz", "b": "Dani", "k": 1}, {"clue": 4, "type": "gt", "a": "Bia", "b": "Paz"}, {"clue": 5, "type": "eq", "a": "Elio", "b": "Western"}, {"clue": 6, "type": "adj", "a": "Comedy", "b": "Western"}, {"clue": 7, "type": "lt", "a": "Comedy", "b": "Western"}, {"clue": 8, "type": "adj", "a": "Animation", "b": "Mystery"}, {"clue": 9, "type": "gt", "a": "Documentary", "b": "Animation"}, {"clue": 10, "type": "eq", "a": "Nachos", "b": "Animation"}, {"clue": 11, "type": "offset", "a": "Toffee", "b": "Nachos", "k": 1}, {"clue": 12, "type": "lt", "a": "Popcorn", "b": "Pretzel"}, {"clue": 13, "type": "lt", "a": "Pretzel", "b": "Toffee"}, {"clue": 14, "type": "eq", "a": "Pretzel", "b": "Star"}, {"clue": 15, "type": "adj", "a": "Circle", "b": "Star"}, {"clue": 16, "type": "lt", "a": "Circle", "b": "Star"}, {"clue": 17, "type": "offset", "a": "Arrow", "b": "Square", "k": 1}, {"clue": 18, "type": "gt", "a": "Diamond", "b": "Arrow"}, {"clue": 19, "type": "eq", "a": "Walnut", "b": "Arrow"}, {"clue": 20, "type": "offset", "a": "Birch", "b": "Walnut", "k": 1}, {"clue": 21, "type": "lt", "a": "Cedar", "b": "Pine"}, {"clue": 22, "type": "lt", "a": "Pine", "b": "Birch"}}
```

### dificil-04 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1974.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Animation": [1, 2, 3, 4, 5], "Arrow": [1, 2, 3, 4, 5], "Bia": [1, 2, 3, 4, 5], "Birch": [1, 2, 3, 4, 5], "Cedar": [1, 2, 3, 4, 5], "Circle": [1, 2, 3, 4, 5], "Comedy": [1, 2, 3, 4, 5], "Dani": [1, 2, 3, 4, 5], "Diamond": [1, 2, 3, 4, 5], "Documentary": [1, 2, 3, 4, 5], "Elio": [1, 2, 3, 4, 5], "Gelato": [1, 2, 3, 4, 5], "Luz": [1, 2, 3, 4, 5], "Maple": [1, 2, 3, 4, 5], "Mystery": [1, 2, 3, 4, 5], "Nachos": [1, 2, 3, 4, 5], "Paz": [1, 2, 3, 4, 5], "Pine": [1, 2, 3, 4, 5], "Popcorn": [1, 2, 3, 4, 5], "Pretzel": [1, 2, 3, 4, 5], "Square": [1, 2, 3, 4, 5], "Star": [1, 2, 3, 4, 5], "Toffee": [1, 2, 3, 4, 5], "Walnut": [1, 2, 3, 4, 5], "Western": [1, 2, 3, 4, 5]}, "constraints": [{"clue": 1, "type": "eq", "a": "Luz", "b": 1}, {"clue": 2, "type": "adj", "a": "Luz", "b": "Elio"}, {"clue": 3, "type": "offset", "a": "Paz", "b": "Dani", "k": 1}, {"clue": 4, "type": "gt", "a": "Paz", "b": "Bia"}, {"clue": 5, "type": "eq", "a": "Elio", "b": "Western"}, {"clue": 6, "type": "adj", "a": "Comedy", "b": "Western"}, {"clue": 7, "type": "lt", "a": "Comedy", "b": "Western"}, {"clue": 8, "type": "adj", "a": "Animation", "b": "Mystery"}, {"clue": 9, "type": "gt", "a": "Animation", "b": "Mystery"}, {"clue": 10, "type": "eq", "a": "Nachos", "b": "Animation"}, {"clue": 11, "type": "neq", "a": "Nachos", "b": 2}, {"clue": 12, "type": "lt", "a": "Popcorn", "b": "Pretzel"}, {"clue": 13, "type": "lt", "a": "Pretzel", "b": "Toffee"}, {"clue": 14, "type": "eq", "a": "Star", "b": "Pretzel"}, {"clue": 15, "type": "adj", "a": "Circle", "b": "Star"}, {"clue": 16, "type": "lt", "a": "Circle", "b": "Star"}, {"clue": 17, "type": "offset", "a": "Arrow", "b": "Square", "k": 1}, {"clue": 18, "type": "gt", "a": "Arrow", "b": "Diamond"}, {"clue": 19, "type": "eq", "a": "Walnut", "b": "Arrow"}, {"clue": 20, "type": "offset", "a": "Walnut", "b": "Birch", "k": 1}, {"clue": 21, "type": "lt", "a": "Cedar", "b": "Pine"}, {"clue": 22, "type": "lt", "a": "Pine", "b": "Birch"}}}
```

### dificil-06 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Switch": ["red", "green", "blue"], "Signal": ["red", "green", "blue"], "Tunnel": ["red", "green", "blue"], "Siding": ["red", "green", "blue"], "Track": ["red", "green", "blue"], "Cabin": ["red", "green", "blue"], "Platform": ["red", "green", "blue"], "Tower": ["red", "green", "blue"], "Viaduct": ["red", "green", "blue"], "Furnace": ["red", "green", "blue"], "Gate": ["red", "green", "blue"], "Station": ["red", "green", "blue"], "Loop": ["red", "green", "blue"], "Workshop": ["red", "green", "blue"], "Relay": ["red", "green", "blue"], "Depot": ["red", "green", "blue"], "Crane": ["red", "green", "blue"], "Fence": ["red", "green", "blue"], "Point": ["red", "green", "blue"], "Bridge": ["red", "green", "blue"], "Trench": ["red", "green", "blue"], "Shed": ["red", "green", "blue"], "Ramp": ["red", "green", "blue"], "Gantry": ["red", "green", "blue"], "Lane": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Switch", "Signal", "Tunnel", "Siding", "Track", "Cabin", "Platform", "Tower", "Viaduct", "Furnace", "Gate", "Station", "Loop", "Workshop", "Relay", "Depot", "Crane", "Fence", "Point", "Bridge", "Trench", "Shed", "Ramp", "Gantry", "Lane"]}, {"clue": 1, "type": "eq", "a": "Switch", "b": "green"}, {"clue": 2, "type": "eq", "a": "Signal", "b": "red"}, {"clue": 3, "type": "adj", "a": "Switch", "b": "Tunnel"}, {"clue": 4, "type": "alldiff", "vars": ["Signal", "Tower", "Tunnel", "Workshop"]}, {"clue": 5, "type": "alldiff", "vars": ["Siding", "Track", "Tunnel", "Viaduct"]}, {"clue": 6, "type": "eq", "a": "Track", "b": "Tunnel"}, {"clue": 7, "type": "alldiff", "vars": ["Cabin", "Crane", "Signal", "Track"]}, {"clue": 8, "type": "alldiff", "vars": ["Platform", "Tunnel", "Viaduct"]}, {"clue": 9, "type": "alldiff", "vars": ["Tower", "Track", "Viaduct", "Workshop"]}, {"clue": 10, "type": "alldiff", "vars": ["Furnace", "Point", "Signal", "Tunnel"]}, {"clue": 11, "type": "alldiff", "vars": ["Gate", "Switch", "Trench"]}, {"clue": 12, "type": "eq", "a": "Station", "b": "Tower"}, {"clue": 13, "type": "alldiff", "vars": ["Loop", "Tower", "Viaduct"]}, {"clue": 14, "type": "alldiff", "vars": ["Relay", "Track", "Trench"]}, {"clue": 15, "type": "alldiff", "vars": ["Depot", "Furnace", "Signal", "Tunnel"]}, {"clue": 16, "type": "alldiff", "vars": ["Crane", "Fence", "Platform"]}, {"clue": 17, "type": "alldiff", "vars": ["Fence", "Point", "Fence", "Tower"]}, {"clue": 18, "type": "alldiff", "vars": ["Bridge", "Trench", "Viaduct", "Workshop"]}, {"clue": 19, "type": "alldiff", "vars": ["Shed", "Signal", "Viaduct", "Workshop"]}, {"clue": 20, "type": "alldiff", "vars": ["Ramp", "Relay", "Switch"]}, {"clue": 21, "type": "alldiff", "vars": ["Gantry", "Siding"]}]
```

### dificil-06 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Switch": ["red", "green", "blue"], "Signal": ["red", "green", "blue"], "Tunnel": ["red", "green", "blue"], "Siding": ["red", "green", "blue"], "Track": ["red", "green", "blue"], "Cabin": ["red", "green", "blue"], "Platform": ["red", "green", "blue"], "Tower": ["red", "green", "blue"], "Viaduct": ["red", "green", "blue"], "Furnace": ["red", "green", "blue"], "Gate": ["red", "green", "blue"], "Station": ["red", "green", "blue"], "Loop": ["red", "green", "blue"], "Workshop": ["red", "green", "blue"], "Relay": ["red", "green", "blue"], "Depot": ["red", "green", "blue"], "Crane": ["red", "green", "blue"], "Fence": ["red", "green", "blue"], "Point": ["red", "green", "blue"], "Bridge": ["red", "green", "blue"], "Trench": ["red", "green", "blue"], "Shed": ["red", "green", "blue"], "Ramp": ["red", "green", "blue"], "Gantry": ["red", "green", "blue"], "Lane": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Switch", "Signal", "Tunnel", "Siding", "Track", "Cabin", "Platform", "Tower", "Viaduct", "Furnace", "Gate", "Station", "Loop", "Workshop", "Relay", "Depot", "Crane", "Fence", "Point", "Bridge", "Trench", "Shed", "Ramp", "Gantry", "Lane"]}], {"clue": 1, "type": "eq", "a": "Switch", "b": "green"}, {"clue": 2, "type": "eq", "a": "Signal", "b": "red"}, {"clue": 3, "type": "offset", "a": "Tunnel", "b": "Switch", "k": 1}, {"clue": 4, "type": "alldiff", "vars": ["Signal", "Tower", "Tunnel", "Workshop"]}, {"clue": 5, "type": "alldiff", "vars": ["Siding", "Track", "Tunnel", "Viaduct"]}, {"clue": 6, "type": "eq", "a": "Track", "b": "Tunnel"}, {"clue": 7, "type": "alldiff", "vars": ["Cabin", "Crane", "Signal", "Track"]}, {"clue": 8, "type": "alldiff", "vars": ["Platform", "Tunnel", "Viaduct"]}, {"clue": 9, "type": "alldiff", "vars": ["Tower", "Track", "Viaduct", "Workshop"]}, {"clue": 10, "type": "alldiff", "vars": ["Furnace", "Point", "Signal", "Tunnel"]}, {"clue": 11, "type": "alldiff", "vars": ["Gate", "Switch", "Trench"]}, {"clue": 12, "type": "eq", "a": "Station", "b": "Tower"}, {"clue": 13, "type": "alldiff", "vars": ["Loop", "Tower", "Viaduct"]}, {"clue": 14, "type": "alldiff", "vars": ["Relay", "Track", "Trench"]}, {"clue": 15, "type": "alldiff", "vars": ["Depot", "Furnace", "Signal", "Gantry"]}, {"clue": 16, "type": "alldiff", "vars": ["Crane", "Fence", "Gate", "Platform"]}, {"clue": 17, "type": "alldiff", "vars": ["Fence", "Point", "Relay", "Tower"]}, {"clue": 18, "type": "alldiff", "vars": ["Bridge", "Trench", "Viaduct", "Workshop"]}, {"clue": 19, "type": "alldiff", "vars": ["Shed", "Signal", "Viaduct", "Workshop"]}, {"clue": 20, "type": "alldiff", "vars": ["Ramp", "Switch"]}, {"clue": 21, "type": "alldiff", "vars": ["Gantry", "Siding"]}]
```

### dificil-07 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 2413.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Azure": [1, 2, 3, 4, 5], "Baggage": [1, 2, 3, 4, 5], "Bruno": [1, 2, 3, 4, 5], "Camera": [1, 2, 3, 4, 5], "Clock": [1, 2, 3, 4, 5], "Crane": [1, 2, 3, 4, 5], "Cream": [1, 2, 3, 4, 5], "Dining": [1, 2, 3, 4, 5], "Eagle": [1, 2, 3, 4, 5], "Elsa": [1, 2, 3, 4, 5], "Falcon": [1, 2, 3, 4, 5], "Heron": [1, 2, 3, 4, 5], "Ivan": [1, 2, 3, 4, 5], "Lantern": [1, 2, 3, 4, 5], "Lina": [1, 2, 3, 4, 5], "Mail": [1, 2, 3, 4, 5], "Mara": [1, 2, 3, 4, 5], "Observation": [1, 2, 3, 4, 5], "Olive": [1, 2, 3, 4, 5], "Pink": [1, 2, 3, 4, 5], "Radio": [1, 2, 3, 4, 5], "Rust": [1, 2, 3, 4, 5], "Sleeper": [1, 2, 3, 4, 5], "Swan": [1, 2, 3, 4, 5], "Trunk": [1, 2, 3, 4, 5], "Bruno": [1, 2, 3, 4, 5], "Mara": [1, 2, 3, 4, 5]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Azure", "Baggage", "Bruno", "Camera", "Clock", "Crane", "Cream", "Dining", "Eagle", "Elsa", "Falcon", "Heron", "Ivan", "Lantern", "Lina", "Mail", "Mara", "Observation", "Olive", "Pink", "Radio", "Rust", "Sleeper", "Swan", "Trunk"]}, {"clue": 1, "type": "offset", "a": "Bruno", "b": "Mail", "k": 1}, {"clue": 2, "type": "eq", "a": "Elsa", "b": 3}, {"clue": 3, "type": "offset", "a": "Ivan", "b": "Elsa", "k": 1}, {"clue": 4, "type": "offset", "a": "Bruno", "b": "Elsa", "k": 1}, {"clue": 5, "type": "offset", "a": "Ivan", "b": "Lina", "k": 1}, {"clue": 6, "type": "eq", "a": "Bruno", "b": "Dining"}, {"clue": 7, "type": "eq", "a": "Mail", "b": "Dining"}, {"clue": 8, "type": "lt", "a": "Mail", "b": "Dining"}, {"clue": 9, "type": "offset", "a": "Baggage", "b": "Sleeper", "k": 1}, {"clue": 10, "type": "offset", "a": "Observation", "b": "Baggage", "k": 1}, {"clue": 11, "type": "eq", "a": "Baggage", "b": "Pink"}, {"clue": 12, "type": "offset", "a": "Azure", "b": "Pink", "k": 1}, {"clue": 13, "type": "lt", "a": "Cream", "b": "Rust"}, {"clue": 14, "type": "lt", "a": "Rust", "b": "Azure"}, {"clue": 15, "type": "eq", "a": "Clock", "b": "Rust"}, {"clue": 16, "type": "adj", "a": "Radio", "b": "Clock"}, {"clue": 17, "type": "lt", "a": "Radio", "b": "Clock"}, {"clue": 18, "type": "offset", "a": "Trunk", "b": "Lantern", "k": 1}, {"clue": 19, "type": "offset", "a": "Camera", "b": "Trunk", "k": 1}, {"clue": 20, "type": "eq", "a": "Trunk", "b": "Swan"}, {"clue": 21, "type": "offset", "a": "Crane", "b": "Swan", "k": 1}, {"clue": 22, "type": "lt", "a": "Eagle", "b": "Falcon"}, {"clue": 23, "type": "lt", "a": "Falcon", "b": "Crane"}}
```

### dificil-07 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 2362.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Azure": [1, 2, 3, 4, 5], "Baggage": [1, 2, 3, 4, 5], "Bruno": [1, 2, 3, 4, 5], "Camera": [1, 2, 3, 4, 5], "Clock": [1, 2, 3, 4, 5], "Crane": [1, 2, 3, 4, 5], "Cream": [1, 2, 3, 4, 5], "Dining": [1, 2, 3, 4, 5], "Eagle": [1, 2, 3, 4, 5], "Elsa": [1, 2, 3, 4, 5], "Falcon": [1, 2, 3, 4, 5], "Heron": [1, 2, 3, 4, 5], "Ivan": [1, 2, 3, 4, 5], "Lantern": [1, 2, 3, 4, 5], "Lina": [1, 2, 3, 4, 5], "Mail": [1, 2, 3, 4, 5], "Mara": [1, 2, 3, 4, 5], "Observation": [1, 2, 3, 4, 5], "Olive": [1, 2, 3, 4, 5], "Pink": [1, 2, 3, 4, 5], "Radio": [1, 2, 3, 4, 5], "Rust": [1, 2, 3, 4, 5], "Sleeper": [1, 2, 3, 4, 5], "Swan": [1, 2, 3, 4, 5], "Trunk": [1, 2, 3, 4, 5], "Bruno": [1, 2, 3, 4, 5], "Mara": [1, 2, 3, 4, 5]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Azure", "Baggage", "Bruno", "Camera", "Clock", "Crane", "Cream", "Dining", "Eagle", "Elsa", "Falcon", "Heron", "Ivan", "Lantern", "Lina", "Mail", "Mara", "Observation", "Olive", "Pink", "Radio", "Rust", "Sleeper", "Swan", "Trunk"]}, {"clue": 1, "type": "offset", "a": "Bruno", "b": "Mara", "k": 1}, {"clue": 2, "type": "eq", "a": "Elsa", "b": 3}, {"clue": 3, "type": "gt", "a": "Ivan", "b": "Elsa"}, {"clue": 4, "type": "lt", "a": "Bruno", "b": "Elsa"}, {"clue": 5, "type": "gt", "a": "Ivan", "b": "Lina"}, {"clue": 6, "type": "eq", "a": "Mara", "b": "Dining"}, {"clue": 7, "type": "eq", "a": "Mail", "b": "Dining"}, {"clue": 8, "type": "lt", "a": "Mail", "b": "Dining"}, {"clue": 9, "type": "offset", "a": "Baggage", "b": "Sleeper", "k": 1}, {"clue": 10, "type": "gt", "a": "Observation", "b": "Baggage"}, {"clue": 11, "type": "eq", "a": "Baggage", "b": "Pink"}, {"clue": 12, "type": "offset", "a": "Azure", "b": "Pink", "k": 1}, {"clue": 13, "type": "lt", "a": "Cream", "b": "Rust"}, {"clue": 14, "type": "lt", "a": "Rust", "b": "Azure"}, {"clue": 15, "type": "eq", "a": "Clock", "b": "Rust"}, {"clue": 16, "type": "offset", "a": "Radio", "b": "Clock", "k": 1}, {"clue": 17, "type": "lt", "a": "Radio", "b": "Clock"}, {"clue": 18, "type": "offset", "a": "Trunk", "b": "Lantern", "k": 1}, {"clue": 19, "type": "gt", "a": "Camera", "b": "Trunk"}, {"clue": 20, "type": "eq", "a": "Trunk", "b": "Swan"}, {"clue": 21, "type": "offset", "a": "Crane", "b": "Swan", "k": 1}, {"clue": 22, "type": "lt", "a": "Eagle", "b": "Crane"}, {"clue": 23, "type": "lt", "a": "Falcon", "b": "Crane"}}
```

### facil-02 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Interview": [1, 2, 3, 4, 5, 6], "Jingle": [1, 2, 3, 4, 5, 6], "News": [1, 2, 3, 4, 5, 6], "Quiz": [1, 2, 3, 4, 5, 6], "Traffic": [1, 2, 3, 4, 5, 6], "Weather": [1, 2, 3, 4, 5, 6]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Interview", "Jingle", "News", "Quiz", "Traffic", "Weather"]}, {"clue": 1, "type": "offset", "a": "Interview", "b": "Weather", "k": 1}, {"clue": 2, "type": "offset", "a": "Traffic", "b": "Jingle", "k": 1}, {"clue": 3, "type": "offset", "a": "News", "b": "Traffic", "k": 1}, {"clue": 4, "type": "neq", "a": "Jingle", "b": 3}, {"clue": 5, "type": "lt", "a": "Interview", "b": "Quiz"}]
```

### facil-02 · semilla 1 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Interview": [1, 2, 3, 4, 5, 6], "Jingle": [1, 2, 3, 4, 5, 6], "News": [1, 2, 3, 4, 5, 6], "Quiz": [1, 2, 3, 4, 5, 6], "Traffic": [1, 2, 3, 4, 5, 6], "Weather": [1, 2, 3, 4, 5, 6]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Interview", "Jingle", "News", "Quiz", "Traffic", "Weather"]}, {"clue": 1, "type": "offset", "a": "Interview", "b": "Weather", "k": 1}, {"clue": 2, "type": "offset", "a": "Traffic", "b": "Jingle", "k": 1}, {"clue": 3, "type": "offset", "a": "News", "b": "Traffic", "k": 1}, {"clue": 4, "type": "lt", "a": "Jingle", "b": 4}, {"clue": 5, "type": "lt", "a": "Interview", "b": "Quiz"}]
```

### facil-02 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Interview": [1, 2, 3, 4, 5, 6], "Jingle": [1, 2, 3, 4, 5, 6], "News": [1, 2, 3, 4, 5, 6], "Quiz": [1, 2, 3, 4, 5, 6], "Traffic": [1, 2, 3, 4, 5, 6], "Weather": [1, 2, 3, 4, 5, 6]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Interview", "Jingle", "News", "Quiz", "Traffic", "Weather"]}, {"clue": 1, "type": "offset", "a": "Interview", "b": "Weather", "k": 1}, {"clue": 2, "type": "offset", "a": "Traffic", "b": "Jingle", "k": 1}, {"clue": 3, "type": "offset", "a": "News", "b": "Traffic", "k": 1}, {"clue": 4, "type": "lt", "a": "Jingle", "b": 4}, {"clue": 5, "type": "lt", "a": "Interview", "b": "Quiz"}]
```

### facil-03 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 992.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Rim": ["red", "green", "blue"], "Ford": ["red", "green", "blue"], "Gorge": ["red", "green", "blue"], "Dune": ["red", "green", "blue"], "Marsh": ["red", "green", "blue"], "Cliff": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Rim", "Ford", "Gorge", "Dune", "Marsh", "Cliff"]}, {"clue": 1, "type": "eq", "a": "Rim", "b": "red"}, {"clue": 2, "type": "eq", "a": "Ford", "b": "green"}, {"clue": 3, "type": "offset", "a": "Ford", "b": "Gorge", "k": 1}, {"clue": 3, "type": "offset", "a": "Ford", "b": "Marsh", "k": 1}, {"clue": 3, "type": "offset", "a": "Ford", "b": "Rim", "k": 1}, {"clue": 4, "type": "adj", "a": "Gorge", "b": "Rim"}, {"clue": 5, "type": "offset", "a": "Dune", "b": "Ford", "k": 1}, {"clue": 5, "type": "offset", "a": "Dune", "b": "Gorge", "k": 1}, {"clue": 5, "type": "offset", "a": "Dune", "b": "Marsh", "k": 1}, {"clue": 6, "type": "adj", "a": "Cliff", "b": "Dune"}, {"clue": 6, "type": "adj", "a": "Cliff", "b": "Marsh"}}
```

### facil-03 · semilla 1 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Rim": ["red", "green", "blue"], "Ford": ["red", "green", "blue"], "Gorge": ["red", "green", "blue"], "Dune": ["red", "green", "blue"], "Marsh": ["red", "green", "blue"], "Cliff": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Rim", "Ford", "Gorge", "Dune", "Marsh", "Cliff"]}, {"clue": 1, "type": "eq", "a": "Rim", "b": "red"}, {"clue": 2, "type": "eq", "a": "Ford", "b": "green"}, {"clue": 3, "type": "alldiff", "vars": ["Ford", "Gorge", "Marsh", "Rim"], "offset": {"a": "Ford", "b": "Gorge", "k": 1}, {"clue": 4, "type": "eq", "a": "Gorge", "b": "red"}, {"clue": 5, "type": "alldiff", "vars": ["Dune", "Ford", "Gorge", "Marsh"], "offset": {"a": "Dune", "b": "Ford", "k": 1}, {"clue": 5, "type": "alldiff", "vars": ["Dune", "Ford", "Gorge", "Marsh"], "offset": {"a": "Dune", "b": "Gorge", "k": 1}, {"clue": 5, "type": "alldiff", "vars": ["Dune", "Ford", "Gorge", "Marsh"], "offset": {"a": "Dune", "b": "Marsh", "k": 1}, {"clue": 6, "type": "alldiff", "vars": ["Cliff", "Dune", "Marsh"], "offset": {"a": "Cliff", "b": "Dune", "k": 1}, {"clue": 6, "type": "alldiff", "vars": ["Cliff", "Dune", "Marsh"], "offset": {"a": "Cliff", "b": "Marsh", "k": 1}}
```

### facil-04 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Basil": [1, 2, 3, 4], "Dill": [1, 2, 3, 4], "Ines": [1, 2, 3, 4], "Marco": [1, 2, 3, 4], "Mint": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Pablo": [1, 2, 3, 4], "Sage": [1, 2, 3, 4]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Basil", "Dill", "Ines", "Marco", "Mint", "Nora", "Pablo", "Sage"]}, {"clue": 1, "type": "offset", "a": "Marco", "b": "Ines", "k": 1}, {"clue": 2, "type": "eq", "a": "Nora", "b": 3}, {"clue": 3, "type": "gt", "a": "Pablo", "b": "Nora"}, {"clue": 4, "type": "lt", "a": "Ines", "b": "Nora"}, {"clue": 5, "type": "eq", "a": "Marco", "b": "Basil"}, {"clue": 6, "type": "eq", "a": "Mint", "b": "Basil"}, {"clue": 7, "type": "lt", "a": "Mint", "b": "Basil"}, {"clue": 8, "type": "adj", "a": "Sage", "b": "Dill"}]
```

### facil-04 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Basil": [1, 2, 3, 4], "Dill": [1, 2, 3, 4], "Ines": [1, 2, 3, 4], "Marco": [1, 2, 3, 4], "Mint": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Pablo": [1, 2, 3, 4], "Sage": [1, 2, 3, 4]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Basil", "Dill", "Ines", "Marco", "Mint", "Nora", "Pablo", "Sage"]}, {"clue": 1, "type": "offset", "a": "Marco", "b": "Ines", "k": 1}, {"clue": 2, "type": "eq", "a": "Nora", "b": 3}, {"clue": 3, "type": "gt", "a": "Pablo", "b": "Nora"}, {"clue": 4, "type": "lt", "a": "Ines", "b": "Nora"}, {"clue": 5, "type": "eq", "a": "Marco", "b": "Basil"}, {"clue": 6, "type": "adj", "a": "Mint", "b": "Basil"}, {"clue": 7, "type": "lt", "a": "Mint", "b": "Basil"}, {"clue": 8, "type": "adj", "a": "Sage", "b": "Dill"}, {"clue": 0, "type": "alldiff", "vars": ["Basil", "Dill"]}, {"clue": 0, "type": "alldiff", "vars": ["Ines", "Marco"]}, {"clue": 0, "type": "alldiff", "vars": ["Nora", "Pablo"]}, {"clue": 0, "type": "alldiff", "vars": ["Sage", "Dill"]}]
```

### facil-05 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 906.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Center": [1, 2, 3, 4, 5, 6, 7, 8], "Dry": [1, 2, 3, 4, 5, 6, 7, 8], "Fire": [1, 2, 3, 4, 5, 6, 7, 8], "Glaze": [1, 2, 3, 4, 5, 6, 7, 8], "Pack": [1, 2, 3, 4, 5, 6, 7, 8], "Sketch": [1, 2, 3, 4, 5, 6, 7, 8], "Stamp": [1, 2, 3, 4, 5, 6, 7, 8], "Trim": [1, 2, 3, 4, 5, 6, 7, 8]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Center", "Dry", "Fire", "Glaze", "Pack", "Sketch", "Stamp", "Trim"]}, {"clue": 1, "type": "offset", "a": "Center", "b": "Sketch", "k": 1}, {"clue": 2, "type": "offset", "a": "Stamp", "b": "Trim", "k": 1}, {"clue": 3, "type": "offset", "a": "Fire", "b": "Glaze", "k": 1}, {"clue": 4, "type": "offset", "a": "Pack", "b": "Fire", "k": 1}, {"clue": 5, "type": "eq", "a": "Trim", "b": 3}, {"clue": 6, "type": "lt", "a": "Trim", "b": "Center"}, {"clue": 7, "type": "offset", "a": "Dry", "b": "Stamp", "k": 1}, {"clue": 8, "type": "lt", "a": "Dry", "b": "Glaze"}}
```

### facil-05 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 906.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Center": [1, 2, 3, 4, 5, 6, 7, 8], "Dry": [1, 2, 3, 4, 5, 6, 7, 8], "Fire": [1, 2, 3, 4, 5, 6, 7, 8], "Glaze": [1, 2, 3, 4, 5, 6, 7, 8], "Pack": [1, 2, 3, 4, 5, 6, 7, 8], "Sketch": [1, 2, 3, 4, 5, 6, 7, 8], "Stamp": [1, 2, 3, 4, 5, 6, 7, 8], "Trim": [1, 2, 3, 4, 5, 6, 7, 8]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Center", "Dry", "Fire", "Glaze", "Pack", "Sketch", "Stamp", "Trim"]}, {"clue": 1, "type": "offset", "a": "Center", "b": "Sketch", "k": 1}, {"clue": 2, "type": "offset", "a": "Stamp", "b": "Trim", "k": 1}, {"clue": 3, "type": "offset", "a": "Fire", "b": "Glaze", "k": 1}, {"clue": 4, "type": "offset", "a": "Pack", "b": "Fire", "k": 1}, {"clue": 5, "type": "eq", "a": "Trim", "b": 3}, {"clue": 6, "type": "lt", "a": "Center", "b": "Trim"}, {"clue": 7, "type": "offset", "a": "Dry", "b": "Stamp", "k": 1}, {"clue": 8, "type": "lt", "a": "Dry", "b": "Glaze"}}
```

### facil-06 · semilla 1 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Plaza": ["red", "green", "blue"], "Gate": ["red", "green", "blue"], "Tent": ["red", "green", "blue"], "Stage": ["red", "green", "blue"], "Court": ["red", "green", "blue"], "Lawn": ["red", "green", "blue"], "Deck": ["red", "green", "blue"], "Ramp": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Plaza", "Gate", "Tent"]}, {"clue": 0, "type": "alldiff", "vars": ["Stage", "Court", "Lawn"]}, {"clue": 0, "type": "alldiff", "vars": ["Stage", "Court", "Ramp"]}, {"clue": 0, "type": "alldiff", "vars": ["Deck", "Lawn", "Ramp"]}, {"clue": 1, "type": "eq", "a": "Plaza", "b": "blue"}, {"clue": 2, "type": "eq", "a": "Gate", "b": "red"}, {"clue": 3, "type": "eq", "a": "Plaza", "b": "Tent"}, {"clue": 4, "type": "alldiff", "vars": ["Gate", "Plaza", "Stage"]}, {"clue": 4, "type": "alldiff", "vars": ["Gate", "Plaza", "Tent"]}, {"clue": 5, "type": "eq", "a": "Stage", "b": "Tent"}, {"clue": 6, "type": "alldiff", "vars": ["Court", "Lawn", "Stage"]}, {"clue": 6, "type": "alldiff", "vars": ["Court", "Lawn", "Ramp"]}, {"clue": 7, "type": "alldiff", "vars": ["Lawn", "Plaza", "Ramp"]}, {"clue": 8, "type": "alldiff", "vars": ["Deck", "Lawn", "Ramp"]}, {"clue": 9, "type": "eq", "a": "Ramp", "b": "Tent"}]
```

### facil-07 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 511.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: las 5 pistas están bien traducidas, pero el JSON termina en `}}` en vez de `}]}`: falta cerrar la lista de restricciones.

```json
{"variables": {"Copper": [1, 2, 3], "Indigo": [1, 2, 3], "Lea": [1, 2, 3], "Omar": [1, 2, 3], "Rui": [1, 2, 3], "Silver": [1, 2, 3]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Copper", "Indigo", "Lea", "Omar", "Rui", "Silver"]}, {"clue": 1, "type": "adj", "a": "Omar", "b": "Rui"}, {"clue": 2, "type": "lt", "a": "Lea", "b": "Omar"}, {"clue": 3, "type": "lt", "a": "Omar", "b": "Rui"}, {"clue": 4, "type": "eq", "a": "Rui", "b": "Indigo"}, {"clue": 5, "type": "lt", "a": "Silver", "b": "Copper"}}
```

### facil-07 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 618.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Copper": [1, 2, 3], "Indigo": [1, 2, 3], "Lea": [1, 2, 3], "Omar": [1, 2, 3], "Rui": [1, 2, 3], "Silver": [1, 2, 3]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Copper", "Indigo", "Lea"]}, {"clue": 0, "type": "alldiff", "vars": ["Omar", "Rui"]}, {"clue": 0, "type": "alldiff", "vars": ["Lea", "Omar", "Rui"]}, {"clue": 1, "type": "offset", "a": "Omar", "b": "Rui", "k": 1}, {"clue": 2, "type": "lt", "a": "Lea", "b": "Omar"}, {"clue": 3, "type": "lt", "a": "Omar", "b": "Rui"}, {"clue": 4, "type": "eq", "a": "Indigo", "b": "Rui"}, {"clue": 5, "type": "lt", "a": "Silver", "b": "Copper"}}
```

### medio-01 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Ada": [1, 2, 3, 4], "Amber": [1, 2, 3, 4], "Coral": [1, 2, 3, 4], "Fossils": [1, 2, 3, 4], "Ivory": [1, 2, 3, 4], "Mina": [1, 2, 3, 4], "Noel": [1, 2, 3, 4], "Optics": [1, 2, 3, 4], "Robots": [1, 2, 3, 4], "Sound": [1, 2, 3, 4], "Teal": [1, 2, 3, 4], "Teo": [1, 2, 3, 4]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Ada", "Amber", "Coral"]}, {"clue": 0, "type": "alldiff", "vars": ["Fossils", "Ivory", "Sound"]}, {"clue": 0, "type": "alldiff", "vars": ["Ada", "Noel"]}, {"clue": 0, "type": "alldiff", "vars": ["Mina", "Teo"]}, {"clue": 1, "type": "offset", "a": "Ada", "b": "Noel", "k": 1}, {"clue": 2, "type": "eq", "a": "Mina", "b": 3}, {"clue": 3, "type": "offset", "a": "Teo", "b": "Mina", "k": 1}, {"clue": 4, "type": "neq", "a": "Noel", "b": 3}, {"clue": 5, "type": "eq", "a": "Ada", "b": "Coral"}, {"clue": 6, "type": "eq", "a": "Amber", "b": "Coral"}, {"clue": 7, "type": "lt", "a": "Amber", "b": "Coral"}, {"clue": 8, "type": "offset", "a": "Ivory", "b": "Teal", "k": 1}, {"clue": 9, "type": "eq", "a": "Ivory", "b": "Sound"}, {"clue": 10, "type": "adj", "a": "Sound", "b": "Robots"}, {"clue": 11, "type": "lt", "a": "Optics", "b": "Robots"}, {"clue": 12, "type": "lt", "a": "Fossils", "b": "Optics"}]
```

### medio-01 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1212.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Ada": [1, 2, 3, 4], "Amber": [1, 2, 3, 4], "Coral": [1, 2, 3, 4], "Fossils": [1, 2, 3, 4], "Ivory": [1, 2, 3, 4], "Mina": [1, 2, 3, 4], "Noel": [1, 2, 3, 4], "Optics": [1, 2, 3, 4], "Robots": [1, 2, 3, 4], "Sound": [1, 2, 3, 4], "Teal": [1, 2, 3, 4], "Teo": [1, 2, 3, 4]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Ada", "Amber", "Coral"]}, {"clue": 0, "type": "alldiff", "vars": ["Fossils", "Ivory", "Sound"]}, {"clue": 0, "type": "alldiff", "vars": ["Optics", "Noel", "Robots"]}, {"clue": 1, "type": "offset", "a": "Ada", "b": "Noel", "k": 1}, {"clue": 2, "type": "eq", "a": "Mina", "b": 3}, {"clue": 3, "type": "offset", "a": "Teo", "b": "Mina", "k": 1}, {"clue": 4, "type": "neq", "a": "Noel", "b": "Mina"}, {"clue": 5, "type": "eq", "a": "Ada", "b": "Coral"}, {"clue": 6, "type": "eq", "a": "Amber", "b": "Coral"}, {"clue": 7, "type": "lt", "a": "Amber", "b": "Coral"}, {"clue": 8, "type": "offset", "a": "Ivory", "b": "Teal", "k": 1}, {"clue": 9, "type": "eq", "a": "Ivory", "b": "Sound"}, {"clue": 10, "type": "offset", "a": "Robots", "b": "Sound", "k": 1}, {"clue": 11, "type": "lt", "a": "Optics", "b": "Robots"}, {"clue": 12, "type": "lt", "a": "Optics", "b": "Fossils"}}
```

### medio-02 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1603.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Closing": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Comets": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Eclipses": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Lobby": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 12], "Meteors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Moon": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Orbits": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Photos": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Questions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Survey": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Tickets": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Welcome": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Closing", "Comets", "Eclipses", "Lobby", "Meteors", "Moon", "Orbits", "Photos", "Questions", "Survey", "Tickets", "Welcome"]}, {"clue": 1, "type": "offset", "a": "Lobby", "b": "Tickets", "k": 1}, {"clue": 2, "type": "offset", "a": "Welcome", "b": "Lobby", "k": 1}, {"clue": 3, "type": "offset", "a": "Eclipses", "b": "Orbits", "k": 1}, {"clue": 4, "type": "offset", "a": "Meteors", "b": "Comets", "k": 1}, {"clue": 5, "type": "offset", "a": "Moon", "b": "Meteors", "k": 1}, {"clue": 6, "type": "offset", "a": "Survey", "b": "Photos", "k": 1}, {"clue": 7, "type": "offset", "a": "Closing", "b": "Survey", "k": 1}, {"clue": 8, "type": "eq", "a": "Comets", "b": 6}, {"clue": 9, "type": "lt", "a": "Welcome", "b": "Orbits"}, {"clue": 10, "type": "lt", "a": "Eclipses", "b": "Comets"}, {"clue": 11, "type": "offset", "a": "Questions", "b": "Moon", "k": 1}, {"clue": 12, "type": "lt", "a": "Questions", "b": "Photos"}}
```

### medio-02 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1603.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Closing": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Comets": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Eclipses": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Lobby": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 12], "Meteors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Moon": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Orbits": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Photos": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Questions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Survey": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Tickets": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], "Welcome": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Closing", "Comets", "Eclipses", "Lobby", "Meteors", "Moon", "Orbits", "Photos", "Questions", "Survey", "Tickets", "Welcome"]}, {"clue": 1, "type": "offset", "a": "Lobby", "b": "Tickets", "k": 1}, {"clue": 2, "type": "offset", "a": "Welcome", "b": "Lobby", "k": 1}, {"clue": 3, "type": "offset", "a": "Eclipses", "b": "Orbits", "k": 1}, {"clue": 4, "type": "offset", "a": "Meteors", "b": "Comets", "k": 1}, {"clue": 5, "type": "offset", "a": "Moon", "b": "Meteors", "k": 1}, {"clue": 6, "type": "offset", "a": "Survey", "b": "Photos", "k": 1}, {"clue": 7, "type": "offset", "a": "Survey", "b": "Closing", "k": 1}, {"clue": 8, "type": "eq", "a": "Comets", "b": 6}, {"clue": 9, "type": "lt", "a": "Welcome", "b": "Orbits"}, {"clue": 10, "type": "lt", "a": "Eclipses", "b": "Comets"}, {"clue": 11, "type": "offset", "a": "Questions", "b": "Moon", "k": 1}, {"clue": 12, "type": "lt", "a": "Questions", "b": "Photos"}}
```

### medio-03 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Library": ["red", "green", "blue"], "Bridge": ["red", "green", "blue"], "Arena": ["red", "green", "blue"], "Lab": ["red", "green", "blue"], "Quad": ["red", "green", "blue"], "Gym": ["red", "green", "blue"], "Oaks": ["red", "green", "blue"], "Dorm": ["red", "green", "blue"], "Clinic": ["red", "green", "blue"], "Pond": ["red", "green", "blue"], "Hall": ["red", "green", "blue"], "Cafe": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Library", "Bridge", "Arena", "Lab", "Quad", "Gym", "Oaks", "Dorm", "Clinic", "Pond", "Hall", "Cafe"]}, {"clue": 1, "type": "eq", "a": "Library", "b": "green"}, {"clue": 2, "type": "eq", "a": "Bridge", "b": "blue"}, {"clue": 3, "type": "alldiff", "vars": ["Library", "Oaks", "Pond"]}, {"clue": 4, "type": "alldiff", "vars": ["Bridge", "Cafe", "Lab", "Library", "Oaks", "Quad"]}, {"clue": 5, "type": "alldiff", "vars": ["Arena", "Lab", "Gym", "Library"]}, {"clue": 6, "type": "eq", "a": "Lab", "b": "Quad"}, {"clue": 7, "type": "alldiff", "vars": ["Gym", "Lab", "Pond", "Quad"]}, {"clue": 8, "type": "alldiff", "vars": ["Dorm", "Lab", "Oaks", "Pond"]}, {"clue": 9, "type": "alldiff", "vars": ["Clinic", "Dorm", "Quad"]}, {"clue": 10, "type": "alldiff", "vars": ["Hall", "Lab", "Oaks", "Pond"]}, {"clue": 11, "type": "alldiff", "vars": ["Cafe", "Dorm", "Pond"]}]
```

### medio-04 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1300.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Cork": [1, 2, 3, 4, 5], "Dawn": [1, 2, 3, 4, 5], "Desert": [1, 2, 3, 4, 5], "Eva": [1, 2, 3, 4, 5], "Forest": [1, 2, 3, 4, 5], "Glass": [1, 2, 3, 4, 5], "Hugo": [1, 2, 3, 4, 5], "Ivo": [1, 2, 3, 4, 5], "Lagoon": [1, 2, 3, 4, 5], "Linen": [1, 2, 3, 4, 5], "Nina": [1, 2, 3, 4, 5], "Oak": [1, 2, 3, 4, 5], "Steel": [1, 2, 3, 4, 5], "Storm": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Cork", "Dawn", "Desert", "Eva", "Forest", "Glass", "Hugo", "Ivo", "Lagoon", "Linen", "Nina", "Oak", "Steel", "Storm", "Vera"]}, {"clue": 1, "type": "eq", "a": "Vera", "b": 1}, {"clue": 2, "type": "adj", "a": "Vera", "b": "Hugo"}, {"clue": 3, "type": "offset", "a": "Ivo", "b": "Nina", "k": 1}, {"clue": 4, "type": "gt", "a": "Eva", "b": "Ivo"}, {"clue": 5, "type": "eq", "a": "Hugo", "b": 5}, {"clue": 6, "type": "eq", "a": "Dawn", "b": 5}, {"clue": 7, "type": "lt", "a": "Lagoon", "b": "Dawn"}, {"clue": 8, "type": "offset", "a": "Storm", "b": "Forest", "k": 1}, {"clue": 9, "type": "gt", "a": "Desert", "b": "Storm"}, {"clue": 10, "type": "eq", "a": "Steel", "b": 5}, {"clue": 11, "type": "offset", "a": "Oak", "b": "Steel", "k": 1}, {"clue": 12, "type": "lt", "a": "Linen", "b": "Glass"}, {"clue": 13, "type": "lt", "a": "Glass", "b": "Oak"}}
```

### medio-04 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1309.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Cork": [1, 2, 3, 4, 5], "Dawn": [1, 2, 3, 4, 5], "Desert": [1, 2, 3, 4, 5], "Eva": [1, 2, 3, 4, 5], "Forest": [1, 2, 3, 4, 5], "Glass": [1, 2, 3, 4, 5], "Hugo": [1, 2, 3, 4, 5], "Ivo": [1, 2, 3, 4, 5], "Lagoon": [1, 2, 3, 4, 5], "Linen": [1, 2, 3, 4, 5], "Nina": [1, 2, 3, 4, 5], "Oak": [1, 2, 3, 4, 5], "Steel": [1, 2, 3, 4, 5], "Storm": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Cork", "Dawn", "Desert", "Eva", "Forest", "Glass", "Hugo", "Ivo", "Lagoon", "Linen", "Nina", "Oak", "Steel", "Storm", "Vera"]}, {"clue": 1, "type": "eq", "a": "Vera", "b": 1}, {"clue": 2, "type": "adj", "a": "Vera", "b": "Hugo"}, {"clue": 3, "type": "offset", "a": "Ivo", "b": "Nina", "k": 1}, {"clue": 4, "type": "gt", "a": "Eva", "b": "Ivo"}, {"clue": 5, "type": "eq", "a": "Lagoon", "b": 1}, {"clue": 6, "type": "lt", "a": "Dawn", "b": "Lagoon"}, {"clue": 7, "type": "lt", "a": "Lagoon", "b": "Dawn"}, {"clue": 8, "type": "offset", "a": "Storm", "b": "Forest", "k": 1}, {"clue": 9, "type": "gt", "a": "Desert", "b": "Storm"}, {"clue": 10, "type": "eq", "a": "Steel", "b": 5}, {"clue": 11, "type": "offset", "a": "Steel", "b": "Oak", "k": 1}, {"clue": 12, "type": "lt", "a": "Linen", "b": "Glass"}, {"clue": 13, "type": "lt", "a": "Glass", "b": "Oak"}}
```

### medio-05 · semilla 1 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 20, column 61.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{
  "variables": {
    "Blend": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Boil": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Chill": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Chop": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Inventory": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Label": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Lock": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Log": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Peel": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Report": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Season": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Stack": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Strain": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Wash": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "Wipe": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
  },
  "constraints": [
    {"clue": 1, "type": "eq", "a": "Wash", "b": "Inventory" + 1},
    {"clue": 2, "type": "eq", "a": "Chop", "b": "Peel" + 1},
    {"clue": 3, "type": "offset", "a": "Blend", "b": "Chop", "k": 1},
    {"clue": 4, "type": "offset", "a": "Strain", "b": "Blend", "k": 1},
    {"clue": 5, "type": "eq", "a": "Season", "b": "Boil" + 1},
    {"clue": 6, "type": "eq", "a": "Chill", "b": "Label" + 1},
    {"clue": 7, "type": "offset", "a": "Stack", "b": "Chill", "k": 1},
    {"clue": 8, "type": "eq", "a": "Log", "b": "Wipe" + 1},
    {"clue": 9, "type": "eq", "a": "Lock", "b": "Log" + 1},
    {"clue": 10, "type": "eq", "a": "Report", "b": "Lock" + 1},
    {"clue": 11, "type": "neq", "a": "Log", "b": 11},
    {"clue": 12, "type": "neq", "a": "Peel", "b": "Inventory" + 1},
    {"clue": 13, "type": "neq", "a": "Boil", "b": "Strain" + 1},
    {"clue": 14, "type": "neq", "a": "Label", "b": "Season" + 1}
  ]
}
```

### medio-06 · semilla 2 · `sintaxis`

- Lo que dijo el solver: Your output could not be parsed: the JSON is incomplete: a closing brace '}' is missing at the end.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Pier": ["red", "green", "blue"], "Jetty": ["red", "green", "blue"], "Bay": ["red", "green", "blue"], "Ramp": ["red", "green", "blue"], "Basin": ["red", "green", "blue"], "Lock": ["red", "green", "blue"], "Quay": ["red", "green", "blue"], "Depot": ["red", "green", "blue"], "Crane": ["red", "green", "blue"], "Yard": ["red", "green", "blue"], "Float": ["red", "green", "blue"], "Slip": ["red", "green", "blue"], "Reef": ["red", "green", "blue"], "Mole": ["red", "green", "blue"], "Inlet": ["red", "green", "blue"]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Pier", "Jetty", "Bay", "Ramp", "Basin", "Lock", "Quay", "Depot", "Crane", "Yard", "Float", "Slip", "Reef", "Mole"]}, {"clue": 1, "type": "eq", "a": "Pier", "b": "red"}, {"clue": 2, "type": "eq", "a": "Jetty", "b": "blue"}, {"clue": 3, "type": "eq", "a": "Pier", "b": "Yard"}, {"clue": 4, "type": "offset", "a": "Jetty", "b": "Pier", "k": 1}, {"clue": 4, "type": "offset", "a": "Jetty", "b": "Ramp", "k": 1}, {"clue": 5, "type": "alldiff", "vars": ["Bay", "Inlet", "Jetty", "Pier", "Quay"]}, {"clue": 6, "type": "eq", "a": "Ramp", "b": "Slip"}, {"clue": 7, "type": "alldiff", "vars": ["Basin", "Depot", "Jetty", "Lock", "Pier", "Reef"]}, {"clue": 8, "type": "alldiff", "vars": ["Lock", "Mole", "Ramp", "Yard"]}, {"clue": 9, "type": "eq", "a": "Quay", "b": "Ramp"}, {"clue": 10, "type": "alldiff", "vars": ["Depot", "Inlet", "Quay", "Slip"]}, {"clue": 11, "type": "alldiff", "vars": ["Crane", "Depot", "Lock", "Pier"]}, {"clue": 12, "type": "alldiff", "vars": ["Float", "Jetty", "Lock"]}, {"clue": 13, "type": "eq", "a": "Slip", "b": "Yard"}, {"clue": 14, "type": "eq", "a": "Reef", "b": "Slip"}, {"clue": 15, "type": "alldiff", "vars": ["Mole", "Pier", "Slip"]}]
```

### medio-07 · semilla 0 · `sintaxis`

- Lo que dijo el solver: Your output is not valid JSON: Expecting ',' delimiter at line 1, column 1127.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: la salida no es un JSON válido (casi siempre una llave o corchete mal cerrado al final), así que no hay modelo que resolver.

```json
{"variables": {"Ari": [1, 2, 3, 4], "Beacon": [1, 2, 3, 4], "Bell": [1, 2, 3, 4], "Beto": [1, 2, 3, 4], "Celia": [1, 2, 3, 4], "Dora": [1, 2, 3, 4], "Flag": [1, 2, 3, 4], "Kite": [1, 2, 3, 4], "Otter": [1, 2, 3, 4], "Puffin": [1, 2, 3, 4], "Seal": [1, 2, 3, 4], "Turtle": [1, 2, 3, 4]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Ari", "Beacon", "Bell", "Beto", "Celia", "Dora", "Flag", "Kite", "Otter", "Puffin", "Seal", "Turtle"]}, {"clue": 1, "type": "eq", "a": "Dora", "b": 1}, {"clue": 2, "type": "adj", "a": "Ari", "b": "Dora"}, {"clue": 3, "type": "offset", "a": "Celia", "b": "Beto", "k": 1}, {"clue": 4, "type": "eq", "a": "Flag", "b": "Ari"}, {"clue": 5, "type": "adj", "a": "Flag", "b": "Kite"}, {"clue": 6, "type": "lt", "a": "Flag", "b": "Kite"}, {"clue": 7, "type": "alldiff", "vars": ["Bell", "Beacon"]}, {"clue": 7, "type": "alldiff", "vars": ["Bell", "Puffin"]}, {"clue": 8, "type": "eq", "a": "Bell", "b": "Beacon"}, {"clue": 9, "type": "offset", "a": "Seal", "b": "Puffin", "k": 1}, {"clue": 10, "type": "lt", "a": "Otter", "b": "Seal"}, {"clue": 11, "type": "lt", "a": "Otter", "b": "Turtle"}}
```

### dificil-02 · semilla 2 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{"variables": {"Align": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Caption": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Drill": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Dust": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Inspect": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Level": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Light": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Measure": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Mount": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Open": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Photograph": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Place": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Register": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Review": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Seal": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Sign": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Test": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Unload": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Unwrap": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], "Wire": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}, "constraints": [{"clue": 1, "type": "neq", "a": "Register", "b": "Unload"}, {"clue": 2, "type": "lt", "a": "Register", "b": "Measure"}, {"clue": 3, "type": "offset", "a": "Mount", "b": "Drill", "k": 1}, {"clue": 4, "type": "offset", "a": "Level", "b": "Wire", "k": 1}, {"clue": 5, "type": "offset", "a": "Test", "b": "Unwrap", "k": 1}, {"clue": 6, "type": "offset", "a": "Inspect", "b": "Unwrap", "k": 1}, {"clue": 7, "type": "offset", "a": "Place", "b": "Inspect", "k": 1}, {"clue": 8, "type": "offset", "a": "Align", "b": "Place", "k": 1}, {"clue": 9, "type": "offset", "a": "Light", "b": "Caption", "k": 1}, {"clue": 10, "type": "offset", "a": "Photograph", "b": "Light", "k": 1}, {"clue": 11, "type": "neq", "a": "Dust", "b": "Unwrap"}, {"clue": 12, "type": "offset", "a": "Sign", "b": "Review", "k": 1}, {"clue": 13, "type": "offset", "a": "Open", "b": "Sign", "k": 1}, {"clue": 14, "type": "eq", "a": "Unwrap", "b": 9}, {"clue": 15, "type": "lt", "a": "Measure", "b": "Drill"}, {"clue": 16, "type": "lt", "a": "Level", "b": "Wire"}, {"clue": 17, "type": "lt", "a": "Test", "b": "Unwrap"}, {"clue": 18, "type": "offset", "a": "Caption", "b": "Align", "k": 1}, {"clue": 19, "type": "lt", "a": "Photograph", "b": "Dust"}, {"clue": 20, "type": "lt", "a": "Seal", "b": "Review"}]}
```

### dificil-04 · semilla 1 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{
  "variables": {
    "Animation": [1, 2, 3, 4, 5],
    "Arrow": [1, 2, 3, 4, 5],
    "Bia": [1, 2, 3, 4, 5],
    "Birch": [1, 2, 3, 4, 5],
    "Cedar": [1, 2, 3, 4, 5],
    "Circle": [1, 2, 3, 4, 5],
    "Comedy": [1, 2, 3, 4, 5],
    "Dani": [1, 2, 3, 4, 5],
    "Diamond": [1, 2, 3, 4, 5],
    "Documentary": [1, 2, 3, 4, 5],
    "Elio": [1, 2, 3, 4, 5],
    "Gelato": [1, 2, 3, 4, 5],
    "Luz": [1, 2, 3, 4, 5],
    "Maple": [1, 2, 3, 4, 5],
    "Mystery": [1, 2, 3, 4, 5],
    "Nachos": [1, 2, 3, 4, 5],
    "Paz": [1, 2, 3, 4, 5],
    "Pine": [1, 2, 3, 4, 5],
    "Popcorn": [1, 2, 3, 4, 5],
    "Pretzel": [1, 2, 3, 4, 5],
    "Square": [1, 2, 3, 4, 5],
    "Star": [1, 2, 3, 4, 5],
    "Toffee": [1, 2, 3, 4, 5],
    "Walnut": [1, 2, 3, 4, 5],
    "Western": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"clue": 0, "type": "alldiff", "vars": ["Animation", "Arrow", "Bia", "Birch", "Cedar", "Circle", "Comedy", "Dani", "Diamond", "Documentary", "Elio", "Gelato", "Luz", "Maple", "Mystery", "Nachos", "Paz", "Pine", "Popcorn", "Pretzel", "Square", "Star", "Toffee", "Walnut", "Western"]},
    {"clue": 1, "type": "eq", "a": "Luz", "b": 1},
    {"clue": 2, "type": "adj", "a": "Luz", "b": "Elio"},
    {"clue": 3, "type": "offset", "a": "Paz", "b": "Dani", "k": 1},
    {"clue": 4, "type": "lt", "a": "Paz", "b": "Bia"},
    {"clue": 5, "type": "eq", "a": "Elio", "b": "Western"},
    {"clue": 6, "type": "lt", "a": "Comedy", "b": "Western"},
    {"clue": 7, "type": "lt", "a": "Comedy", "b": "Western"},
    {"clue": 8, "type": "offset", "a": "Animation", "b": "Mystery", "k": 1},
    {"clue": 9, "type": "lt", "a": "Documentary", "b": "Animation"},
    {"clue": 10, "type": "eq", "a": "Nachos", "b": "Animation"},
    {"clue": 11, "type": "offset", "a": "Nachos", "b": "Toffee", "k": -1},
    {"clue": 12, "type": "lt", "a": "Popcorn", "b": "Pretzel"},
    {"clue": 13, "type": "lt", "a": "Pretzel", "b": "Toffee"},
    {"clue": 14, "type": "eq", "a": "Pretzel", "b": "Star"},
    {"clue": 15, "type": "offset", "a": "Circle", "b": "Star", "k": -1},
    {"clue": 16, "type": "lt", "a": "Circle", "b": "Star"},
    {"clue": 17, "type": "offset", "a": "Arrow", "b": "Square", "k": 1},
    {"clue": 18, "type": "lt", "a": "Diamond", "b": "Arrow"},
    {"clue": 19, "type": "eq", "a": "Walnut", "b": "Arrow"},
    {"clue": 20, "type": "offset", "a": "Birch", "b": "Walnut", "k": -1},
    {"clue": 21, "type": "lt", "a": "Cedar", "b": "Pine"},
    {"clue": 22, "type": "lt", "a": "Pine", "b": "Birch"}
  ]
}
```

### dificil-07 · semilla 1 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{
  "variables": {
    "Azure": [1, 2, 3, 4, 5],
    "Baggage": [1, 2, 3, 4, 5],
    "Bruno": [1, 2, 3, 4, 5],
    "Camera": [1, 2, 3, 4, 5],
    "Clock": [1, 2, 3, 4, 5],
    "Crane": [1, 2, 3, 4, 5],
    "Cream": [1, 2, 3, 4, 5],
    "Dining": [1, 2, 3, 4, 5],
    "Eagle": [1, 2, 3, 4, 5],
    "Elsa": [1, 2, 3, 4, 5],
    "Falcon": [1, 2, 3, 4, 5],
    "Heron": [1, 2, 3, 4, 5],
    "Ivan": [1, 2, 3, 4, 5],
    "Lantern": [1, 2, 3, 4, 5],
    "Lina": [1, 2, 3, 4, 5],
    "Mail": [1, 2, 3, 4, 5],
    "Mara": [1, 2, 3, 4, 5],
    "Observation": [1, 2, 3, 4, 5],
    "Olive": [1, 2, 3, 4, 5],
    "Pink": [1, 2, 3, 4, 5],
    "Radio": [1, 2, 3, 4, 5],
    "Rust": [1, 2, 3, 4, 5],
    "Sleeper": [1, 2, 3, 4, 5],
    "Swan": [1, 2, 3, 4, 5],
    "Trunk": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"clue": 0, "type": "alldiff", "vars": ["Azure", "Baggage", "Bruno", "Camera", "Clock", "Crane", "Cream", "Dining", "Eagle", "Elsa", "Falcon", "Heron", "Ivan", "Lantern", "Lina", "Mail", "Mara", "Observation", "Olive", "Pink", "Radio", "Rust", "Sleeper", "Swan", "Trunk"]},
    {"clue": 1, "type": "offset", "a": "Bruno", "b": "Mail", "k": 1},
    {"clue": 2, "type": "eq", "a": "Elsa", "b": 3},
    {"clue": 3, "type": "offset", "a": "Ivan", "b": "Elsa", "k": 1},
    {"clue": 4, "type": "offset", "a": "Ivan", "b": "Lina", "k": 1},
    {"clue": 5, "type": "offset", "a": "Mail", "b": "Dining", "k": 1},
    {"clue": 6, "type": "eq", "a": "Mail", "b": "Baggage"},
    {"clue": 7, "type": "eq", "a": "Pink", "b": 1},
    {"clue": 8, "type": "lt", "a": "Mail", "b": "Baggage"},
    {"clue": 9, "type": "offset", "a": "Baggage", "b": "Sleeper", "k": 1},
    {"clue": 10, "type": "offset", "a": "Observation", "b": "Baggage", "k": 1},
    {"clue": 11, "type": "eq", "a": "Pink", "b": "Baggage"},
    {"clue": 12, "type": "offset", "a": "Azure", "b": "Pink", "k": 1},
    {"clue": 13, "type": "lt", "a": "Cream", "b": "Rust"},
    {"clue": 14, "type": "lt", "a": "Rust", "b": "Azure"},
    {"clue": 15, "type": "eq", "a": "Clock", "b": 5},
    {"clue": 16, "type": "offset", "a": "Radio", "b": "Clock", "k": 1},
    {"clue": 17, "type": "lt", "a": "Radio", "b": "Clock"},
    {"clue": 18, "type": "offset", "a": "Trunk", "b": "Lantern", "k": 1},
    {"clue": 19, "type": "offset", "a": "Camera", "b": "Trunk", "k": 1},
    {"clue": 20, "type": "eq", "a": "Trunk", "b": 5},
    {"clue": 21, "type": "offset", "a": "Crane", "b": "Swan", "k": 1},
    {"clue": 22, "type": "lt", "a": "Eagle", "b": "Swan"}
  ]
}
```

### facil-01 · semilla 2 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong. Removing any ONE of these constraints would make it solvable, so check them against the puzzle: {"clue": 1, "type": "eq", "a": "Mateo", "b": "Red"}; {"clue": 5, "type": "offset", "a": "Red", "b": "Yellow", "k": 1}.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: inventa una quinta pista (`offset Red Yellow`) en un problema de 4 pistas; el refinamiento de B′ termina convirtiendo este error en uno silencioso (ver REPORT §3, ejemplo 5).

```json
{"variables": {"Mateo": [1, 2, 3], "Sofía": [1, 2, 3], "Lucas": [1, 2, 3], "Red": [1, 2, 3], "Yellow": [1, 2, 3], "Blue": [1, 2, 3]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Mateo", "Sofía", "Lucas"]}, {"clue": 0, "type": "alldiff", "vars": ["Red", "Yellow", "Blue"]}, {"clue": 1, "type": "eq", "a": "Mateo", "b": "Red"}, {"clue": 2, "type": "offset", "a": "Sofía", "b": "Mateo", "k": 1}, {"clue": 3, "type": "eq", "a": "Lucas", "b": 3}, {"clue": 4, "type": "adj", "a": "Yellow", "b": "Blue"}, {"clue": 5, "type": "offset", "a": "Red", "b": "Yellow", "k": 1}]}
```

### facil-04 · semilla 1 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{"variables": {"Basil": [1, 2, 3, 4], "Dill": [1, 2, 3, 4], "Ines": [1, 2, 3, 4], "Marco": [1, 2, 3, 4], "Mint": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Pablo": [1, 2, 3, 4], "Sage": [1, 2, 3, 4]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Basil", "Dill", "Ines", "Marco", "Mint", "Nora", "Pablo", "Sage"]}, {"clue": 1, "type": "offset", "a": "Marco", "b": "Ines", "k": 1}, {"clue": 2, "type": "eq", "a": "Nora", "b": 3}, {"clue": 3, "type": "lt", "a": "Pablo", "b": "Nora"}, {"clue": 4, "type": "gt", "a": "Ines", "b": "Nora"}, {"clue": 5, "type": "eq", "a": "Marco", "b": "Basil"}, {"clue": 6, "type": "eq", "a": "Mint", "b": "Dill"}, {"clue": 7, "type": "lt", "a": "Mint", "b": "Basil"}, {"clue": 8, "type": "offset", "a": "Sage", "b": "Dill", "k": 1}]}
```

### facil-07 · semilla 1 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: junta a los 3 viajeros y los 3 colores de auto en un solo `alldiff` con dominio {1, 2, 3}: seis valores distintos en tres posiciones es imposible.

```json
{"variables": {"Copper": [1, 2, 3], "Indigo": [1, 2, 3], "Lea": [1, 2, 3], "Omar": [1, 2, 3], "Rui": [1, 2, 3], "Silver": [1, 2, 3]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Copper", "Indigo", "Lea", "Omar", "Rui", "Silver"]}, {"clue": 1, "type": "adj", "a": "Omar", "b": "Rui"}, {"clue": 2, "type": "lt", "a": "Lea", "b": "Omar"}, {"clue": 3, "type": "lt", "a": "Omar", "b": "Rui"}, {"clue": 4, "type": "eq", "a": "Indigo", "b": "Rui"}, {"clue": 5, "type": "lt", "a": "Silver", "b": "Copper"}]}
```

### medio-01 · semilla 1 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{
  "variables": {
    "Ada": [1, 2, 3, 4],
    "Amber": [1, 2, 3, 4],
    "Coral": [1, 2, 3, 4],
    "Fossils": [1, 2, 3, 4],
    "Ivory": [1, 2, 3, 4],
    "Mina": [1, 2, 3, 4],
    "Noel": [1, 2, 3, 4],
    "Optics": [1, 2, 3, 4],
    "Robots": [1, 2, 3, 4],
    "Sound": [1, 2, 3, 4],
    "Teal": [1, 2, 3, 4],
    "Teo": [1, 2, 3, 4]
  },
  "constraints": [
    {"clue": 0, "type": "alldiff", "vars": ["Ada", "Noel", "Mina", "Teo", "Teal", "Coral", "Fossils", "Ivory", "Optics", "Robots", "Sound", "Amber"]},
    {"clue": 1, "type": "offset", "a": "Ada", "b": "Noel", "k": 1},
    {"clue": 2, "type": "eq", "a": "Mina", "b": 3},
    {"clue": 3, "type": "offset", "a": "Teo", "b": "Mina", "k": 1},
    {"clue": 4, "type": "neq", "a": "Noel", "b": "Mina"},
    {"clue": 5, "type": "eq", "a": "Ada", "b": "Coral"},
    {"clue": 6, "type": "eq", "a": "Amber", "b": "Coral"},
    {"clue": 7, "type": "lt", "a": "Amber", "b": "Coral"},
    {"clue": 8, "type": "offset", "a": "Ivory", "b": "Teal", "k": 1},
    {"clue": 9, "type": "eq", "a": "Ivory", "b": "Sound"},
    {"clue": 10, "type": "offset", "a": "Robots", "b": "Sound", "k": 1},
    {"clue": 11, "type": "lt", "a": "Optics", "b": "Robots"},
    {"clue": 12, "type": "lt", "a": "Fossils", "b": "Optics"}
  ]
}
```

### medio-02 · semilla 1 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong. Removing any ONE of these constraints would make it solvable, so check them against the puzzle: {"clue": 6, "type": "offset", "a": "Survey", "b": "Photos", "k": 1}; {"clue": 7, "type": "offset", "a": "Survey", "b": "Closing", "k": 1}.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{
  "variables": {
    "Closing": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "Comets": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "Eclipses": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    "Lobby": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 11],
    "Meteors": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 11],
    "Moon": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 11],
    "Orbits": [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 10],
    "Photos": [1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 10, 9],
    "Questions": [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 9],
    "Survey": [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 10, 8],
    "Tickets": [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 7],
    "Welcome": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  },
  "constraints": [
    {"clue": 0, "type": "alldiff", "vars": ["Closing", "Comets", "Eclipses", "Lobby", "Meteors", "Moon", "Orbits", "Photos", "Questions", "Survey", "Tickets", "Welcome"]},
    {"clue": 1, "type": "offset", "a": "Lobby", "b": "Tickets", "k": 1},
    {"clue": 2, "type": "offset", "a": "Welcome", "b": "Lobby", "k": 1},
    {"clue": 3, "type": "offset", "a": "Eclipses", "b": "Orbits", "k": 1},
    {"clue": 4, "type": "offset", "a": "Meteors", "b": "Comets", "k": 1},
    {"clue": 5, "type": "offset", "a": "Moon", "b": "Meteors", "k": 1},
    {"clue": 6, "type": "offset", "a": "Survey", "b": "Photos", "k": 1},
    {"clue": 7, "type": "offset", "a": "Survey", "b": "Closing", "k": 1},
    {"clue": 8, "type": "eq", "a": "Comets", "b": 6},
    {"clue": 9, "type": "lt", "a": "Welcome", "b": "Orbits"},
    {"clue": 10, "type": "lt", "a": "Eclipses", "b": "Comets"},
    {"clue": 11, "type": "offset", "a": "Questions", "b": "Moon", "k": 1},
    {"clue": 12, "type": "lt", "a": "Questions", "b": "Photos"}
  ]
}
```

### medio-04 · semilla 1 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{
  "variables": {
    "Cork": [1, 2, 3, 4, 5],
    "Dawn": [1, 2, 3, 4, 5],
    "Desert": [1, 2, 3, 4, 5],
    "Eva": [1, 2, 3, 4, 5],
    "Forest": [1, 2, 3, 4, 5],
    "Glass": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Ivo": [1, 2, 3, 4, 5],
    "Lagoon": [1, 2, 3, 4, 5],
    "Linen": [1, 2, 3, 4, 5],
    "Nina": [1, 2, 3, 4, 5],
    "Oak": [1, 2, 3, 4, 5],
    "Steel": [1, 2, 3, 4, 5],
    "Storm": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"clue": 0, "type": "alldiff", "vars": ["Cork", "Dawn", "Desert", "Eva", "Forest", "Glass", "Hugo", "Ivo", "Lagoon", "Linen", "Nina", "Oak", "Steel", "Storm", "Vera"]},
    {"clue": 1, "type": "eq", "a": "Vera", "b": 1},
    {"clue": 2, "type": "offset", "a": "Hugo", "b": "Dawn", "k": 1},
    {"clue": 3, "type": "offset", "a": "Ivo", "b": "Nina", "k": 1},
    {"clue": 4, "type": "gt", "a": "Eva", "b": "Ivo"},
    {"clue": 5, "type": "eq", "a": "Hugo", "b": "Dawn"},
    {"clue": 6, "type": "lt", "a": "Dawn", "b": "Lagoon"},
    {"clue": 7, "type": "eq", "a": "Lagoon", "b": "Dawn"},
    {"clue": 8, "type": "offset", "a": "Storm", "b": "Forest", "k": 1},
    {"clue": 9, "type": "gt", "a": "Desert", "b": "Storm"},
    {"clue": 10, "type": "eq", "a": "Storm", "b": "Steel"},
    {"clue": 11, "type": "offset", "a": "Steel", "b": "Oak", "k": 1},
    {"clue": 12, "type": "lt", "a": "Glass", "b": "Oak"},
    {"clue": 13, "type": "lt", "a": "Linen", "b": "Glass"}
  ]
}
```

### medio-07 · semilla 1 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{
  "variables": {
    "Ari": [1, 2, 3, 4],
    "Beacon": [1, 2, 3, 4],
    "Bell": [1, 2, 3, 4],
    "Beto": [1, 2, 3, 4],
    "Celia": [1, 2, 3, 4],
    "Dora": [1, 2, 3, 4],
    "Flag": [1, 2, 3, 4],
    "Kite": [1, 2, 3, 4],
    "Otter": [1, 2, 3, 4],
    "Puffin": [1, 2, 3, 4],
    "Seal": [1, 2, 3, 4],
    "Turtle": [1, 2, 3, 4]
  },
  "constraints": [
    {"clue": 0, "type": "alldiff", "vars": ["Ari", "Beacon", "Bell", "Beto", "Celia", "Dora", "Flag", "Kite", "Otter", "Puffin", "Seal", "Turtle"]},
    {"clue": 1, "type": "eq", "a": "Dora", "b": 1},
    {"clue": 2, "type": "adj", "a": "Ari", "b": "Dora"},
    {"clue": 3, "type": "offset", "a": "Celia", "b": "Beto", "k": 1},
    {"clue": 4, "type": "eq", "a": "Flag", "b": "Ari"},
    {"clue": 5, "type": "eq", "a": "Kite", "b": "Flag"},
    {"clue": 6, "type": "lt", "a": "Kite", "b": "Flag"},
    {"clue": 7, "type": "offset", "a": "Bell", "b": "Beacon", "k": 1},
    {"clue": 8, "type": "eq", "a": "Bell", "b": "Puffin"},
    {"clue": 9, "type": "neq", "a": "Seal", "b": "Puffin"},
    {"clue": 10, "type": "lt", "a": "Seal", "b": "Otter"},
    {"clue": 11, "type": "lt", "a": "Otter", "b": "Seal"}
  ]
}
```

### medio-07 · semilla 2 · `sobre_restringido`

- Lo que dijo el solver: The solver proved the model has NO solution: some constraint is wrong or too strong.
- Diferencias con el gold: no hubo respuesta
- Qué salió mal: el modelo parsea, pero alguna restricción contradice a otra: el solver prueba que no hay ninguna asignación posible.

```json
{"variables": {"Ari": [1, 2, 3, 4], "Beacon": [1, 2, 3, 4], "Bell": [1, 2, 3, 4], "Beto": [1, 2, 3, 4], "Celia": [1, 2, 3, 4], "Dora": [1, 2, 3, 4], "Flag": [1, 2, 3, 4], "Kite": [1, 2, 3, 4], "Otter": [1, 2, 3, 4], "Puffin": [1, 2, 3, 4], "Seal": [1, 2, 3, 4], "Turtle": [1, 2, 3, 4]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Ari", "Beacon", "Bell", "Beto", "Celia", "Dora", "Flag", "Kite", "Otter", "Puffin", "Seal", "Turtle"]}, {"clue": 1, "type": "eq", "a": "Dora", "b": 1}, {"clue": 2, "type": "adj", "a": "Ari", "b": "Dora"}, {"clue": 3, "type": "offset", "a": "Celia", "b": "Beto", "k": 1}, {"clue": 4, "type": "eq", "a": "Flag", "b": "Ari"}, {"clue": 5, "type": "adj", "a": "Flag", "b": "Kite"}, {"clue": 6, "type": "lt", "a": "Kite", "b": "Flag"}, {"clue": 7, "type": "alldiff", "vars": ["Bell", "Puffin"]}, {"clue": 7, "type": "alldiff", "vars": ["Beacon", "Bell"]}, {"clue": 8, "type": "eq", "a": "Bell", "b": "Puffin"}, {"clue": 9, "type": "adj", "a": "Seal", "b": "Puffin"}, {"clue": 10, "type": "lt", "a": "Turtle", "b": "Seal"}, {"clue": 11, "type": "lt", "a": "Turtle", "b": "Seal"}]}
```

### dificil-01 · semilla 1 · `sub_restringido`

- Lo que dijo el solver: The model has MORE THAN ONE solution, so some clue is missing or too weak. Two solutions differ in: Whistle.
- Diferencias con el gold: Alma: dio 4, era 2; Bear: dio 3, era 4; Gold: dio 3, era 4; Hare: dio 4, era 3; Jade: dio 2, era 3; Nico: dio 1, era 5
- Qué salió mal: el `alldiff` de colores quedó con 4 de los 5 colores (falta `Red`) y no tradujo la pista del silbato; por eso `Whistle` queda libre.

```json
{
  "variables": {
    "Alma": [1, 2, 3, 4, 5],
    "Bear": [1, 2, 3, 4, 5],
    "Compass": [1, 2, 3, 4, 5],
    "Deer": [1, 2, 3, 4, 5],
    "Flask": [1, 2, 3, 4, 5],
    "Fox": [1, 2, 3, 4, 5],
    "Gold": [1, 2, 3, 4, 5],
    "Hare": [1, 2, 3, 4, 5],
    "Jade": [1, 2, 3, 4, 5],
    "Lilac": [1, 2, 3, 4, 5],
    "Luis": [1, 2, 3, 4, 5],
    "Nico": [1, 2, 3, 4, 5],
    "Owl": [1, 2, 3, 4, 5],
    "Red": [1, 2, 3, 4, 5],
    "Rope": [1, 2, 3, 4, 5],
    "Rosa": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Torch": [1, 2, 3, 4, 5],
    "Whistle": [1, 2, 3, 4, 5],
    "White": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"clue": 0, "type": "alldiff", "vars": ["Alma", "Luis", "Rosa", "Tomas", "Nico"]},
    {"clue": 0, "type": "alldiff", "vars": ["Bear", "Deer", "Fox", "Hare", "Owl"]},
    {"clue": 0, "type": "alldiff", "vars": ["Gold", "Jade", "Lilac", "White"]},
    {"clue": 1, "type": "offset", "a": "Alma", "b": "Luis", "k": 1},
    {"clue": 2, "type": "eq", "a": "Luis", "b": 3},
    {"clue": 3, "type": "neq", "a": "Rosa", "b": "Luis"},
    {"clue": 4, "type": "neq", "a": "Tomas", "b": "Luis"},
    {"clue": 5, "type": "neq", "a": "Rosa", "b": "Nico"},
    {"clue": 6, "type": "eq", "a": "Alma", "b": "White"},
    {"clue": 7, "type": "adj", "a": "Red", "b": "White"},
    {"clue": 8, "type": "lt", "a": "Red", "b": "White"},
    {"clue": 9, "type": "offset", "a": "Gold", "b": "Jade", "k": 1},
    {"clue": 10, "type": "neq", "a": "Lilac", "b": "Gold"},
    {"clue": 11, "type": "eq", "a": "Gold", "b": "Bear"},
    {"clue": 12, "type": "adj", "a": "Hare", "b": "Bear"},
    {"clue": 13, "type": "lt", "a": "Owl", "b": "Hare"},
    {"clue": 14, "type": "lt", "a": "Fox", "b": "Hare"},
    {"clue": 15, "type": "eq", "a": "Fox", "b": "Flask"},
    {"clue": 16, "type": "adj", "a": "Compass", "b": "Flask"},
    {"clue": 17, "type": "lt", "a": "Compass", "b": "Flask"},
    {"clue": 18, "type": "adj", "a": "Rope", "b": "Torch"},
    {"clue": 19, "type": "neq", "a": "Whistle", "b": "Rope"}
  ]
}
```

### medio-05 · semilla 0 · `sub_restringido`

- Lo que dijo el solver: The model has MORE THAN ONE solution, so some clue is missing or too weak. Two solutions differ in: Inventory, Lock, Log, Report, Wash, Wipe.
- Diferencias con el gold: Blend: dio 9, era 5; Boil: dio 11, era 7; Chill: dio 14, era 10; Chop: dio 8, era 4; Inventory: dio 5, era 1; Label: dio 13, era 9
- Qué salió mal: al modelo le falta (o tiene demasiado débil) alguna pista: el solver encuentra al menos dos soluciones.

```json
{"variables": {"Blend": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Boil": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Chill": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Chop": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Inventory": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Label": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Lock": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Log": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Peel": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Report": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Season": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Stack": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Strain": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Wash": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Wipe": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Blend", "Boil", "Chill", "Chop", "Inventory", "Label", "Lock", "Log", "Peel", "Report", "Season", "Stack", "Strain", "Wash", "Wipe"]}, {"clue": 1, "type": "offset", "a": "Wash", "b": "Inventory", "k": 1}, {"clue": 2, "type": "offset", "a": "Chop", "b": "Peel", "k": 1}, {"clue": 3, "type": "offset", "a": "Blend", "b": "Chop", "k": 1}, {"clue": 4, "type": "offset", "a": "Strain", "b": "Blend", "k": 1}, {"clue": 5, "type": "offset", "a": "Season", "b": "Boil", "k": 1}, {"clue": 6, "type": "offset", "a": "Chill", "b": "Label", "k": 1}, {"clue": 7, "type": "offset", "a": "Stack", "b": "Chill", "k": 1}, {"clue": 8, "type": "offset", "a": "Wipe", "b": "Log", "k": 1}, {"clue": 9, "type": "offset", "a": "Lock", "b": "Wipe", "k": 1}, {"clue": 10, "type": "offset", "a": "Report", "b": "Lock", "k": 1}, {"clue": 11, "type": "lt", "a": "Log", "b": 11}, {"clue": 12, "type": "lt", "a": "Wash", "b": "Peel"}, {"clue": 13, "type": "lt", "a": "Strain", "b": "Boil"}, {"clue": 14, "type": "lt", "a": "Season", "b": "Label"}, {"clue": 15, "type": "alldiff", "vars": ["Wash", "Peel"]}]}
```

### medio-05 · semilla 2 · `sub_restringido`

- Lo que dijo el solver: The model has MORE THAN ONE solution, so some clue is missing or too weak. Two solutions differ in: Chill, Label, Stack.
- Diferencias con el gold: Chill: dio 9, era 10; Label: dio 10, era 9
- Qué salió mal: al modelo le falta (o tiene demasiado débil) alguna pista: el solver encuentra al menos dos soluciones.

```json
{"variables": {"Blend": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Boil": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Chill": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Chop": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Inventory": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Label": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Lock": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Log": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Peel": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Report": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Season": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Stack": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Strain": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Wash": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], "Wipe": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}, "constraints": [{"clue": 0, "type": "alldiff", "vars": ["Blend", "Boil", "Chill", "Chop", "Inventory", "Label", "Lock", "Log", "Peel", "Report", "Season", "Stack", "Strain", "Wash", "Wipe"]}, {"clue": 1, "type": "lt", "a": "Wash", "b": "Peel"}, {"clue": 2, "type": "lt", "a": "Strain", "b": "Boil"}, {"clue": 3, "type": "lt", "a": "Season", "b": "Label"}, {"clue": 4, "type": "offset", "a": "Wash", "b": "Inventory", "k": 1}, {"clue": 5, "type": "offset", "a": "Chop", "b": "Peel", "k": 1}, {"clue": 6, "type": "offset", "a": "Blend", "b": "Chop", "k": 1}, {"clue": 7, "type": "offset", "a": "Strain", "b": "Blend", "k": 1}, {"clue": 8, "type": "offset", "a": "Label", "b": "Chill", "k": 1}, {"clue": 9, "type": "offset", "a": "Lock", "b": "Wipe", "k": 1}, {"clue": 10, "type": "offset", "a": "Report", "b": "Lock", "k": 1}, {"clue": 11, "type": "gt", "a": "Log", "b": 11}, {"clue": 12, "type": "neq", "a": "Wash", "b": "Peel"}, {"clue": 13, "type": "neq", "a": "Strain", "b": "Boil"}, {"clue": 14, "type": "neq", "a": "Season", "b": "Label"}, {"clue": 15, "type": "eq", "a": "Inventory", "b": 1}]}
```
