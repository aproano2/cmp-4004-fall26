# Taxonomía de fallas del brazo B

Cada falla del brazo B (primer intento del modelo, sin corrección) en las
cinco corridas (rep 0 a temperatura 0 y reps 1–4 a temperatura 0.7),
clasificada automáticamente por `code/taxonomy.py` y con la salida del modelo
tal cual. Al final están las fallas que sobrevivieron al bucle B′.

**Detectable sin la verdad** = el propio sistema lo nota: el JSON no carga, el
solver lo rechaza o prueba que no hay solución, se agota el tiempo, el modelo
admite más de una solución (el enunciado promete una sola) o falta un nombre
del enunciado. Las causas (inventada / invertida / perdida / alldiff) sí usan
el modelo a mano y solo sirven para el análisis.

| Categoría | Fallas (todas las corridas) | Detectables sin verdad |
|---|---|---|
| Sintaxis mala (no parsea) | 12 | 12 |
| Alcance / aridad | 16 | 16 |
| Sobre-restringido (sin solución) | 79 | 79 |
| Sub-restringido (varias soluciones, devolvió otra) | 71 | 71 |
| Modelo válido del problema equivocado | 11 | 0 |
| Timeout del solver | 0 | 0 |
| **Total** | **189** | **178** |

Además, 9 respuestas de B fueron correctas **por suerte**: el modelo admitía varias soluciones y el solver devolvió justo la buena.

### Patrones de causa en las fallas de B

Una falla puede tener varias causas a la vez, así que la suma pasa del total.

| Patrón | Fallas con ese patrón |
|---|---|
| offset con la dirección invertida (A = B + 1 en vez de B = A + 1) | 103 de 189 |
| eq inventado entre dos variables o con un número (p. ej. 'next to' → eq) | 91 de 189 |
| perdió al menos una pista (alguna solución del modelo la viola) | 83 de 189 |
| omitió el alldiff de un grupo ('cada casa es distinta') | 14 de 189 |
| no declaró una variable para algún nombre del enunciado | 14 de 189 |
| alldiff con alcance equivocado (mezcla grupos o deja miembros fuera) | 9 de 189 |

## Sintaxis mala (no parsea) (12)

### 1. L1-08 · rep 0 (T=0.0) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `schema`)
- **Mensaje del parser/solver:** constraint #2 (offset) is missing field 'k'

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4], "Omar": [1, 2, 3, 4], "Kai": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "lt", "a": "Carla", "b": "Omar"},
  {"type": "offset", "a": "Carla", "b": "Raul"},
  {"type": "lt", "a": "Omar", "b": "Kai"}
 ]}
```
</details>

### 2. L4-07 · rep 0 (T=0.0) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `schema`)
- **Mensaje del parser/solver:** constraint #12 (offset) is missing field 'k'

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Felix": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Felix", "Iris", "Elena", "Vera", "Mateo"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "white", "blue"]},
    {"type": "alldiff", "vars": ["fish", "turtle", "bird", "horse", "cat"]},
    {"type": "eq", "a": "turtle", "b": "orange", "k": 1},
    {"type": "offset", "a": "Felix", "b": "Iris", "k": 1},
    {"type": "neq", "a": "Vera", "b": 1},
    {"type": "eq", "a": "Felix", "b": "Iris"},
    {"type": "eq", "a": "Iris", "b": "bird"},
    {"type": "neq", "a": "Iris", "b": 1},
    {"type": "offset", "a": "Iris", "b": "turtle", "k": 1},
    {"type": "eq", "a": "red", "b": "blue", "k": 1},
    {"type": "offset", "a": "Iris", "b": "bird"},
    {"type": "neq", "a": "Iris", "b": 1},
    {"type": "offset", "a": "cat", "b": "turtle", "k": -1},
    {"type": "eq", "a": "blue", "b": "yellow", "k": 1}
  ]
}
```
</details>

### 3. L1-05 · rep 1 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `parse`)
- **Mensaje del parser/solver:** unbalanced braces: the JSON object is never closed

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Paula": [1, 2, 3, 4],
    "Mateo": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Nora": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Mateo", "Sara", "Nora"]},
    {"type": "offset", "a": "Mateo", "b": "Sara", "k": 1},
    {"type": "alldiff", "vars": ["Sara", "Nora"]],
    {"type": "neq", "a": "Nora", "b": 4},
    {"type": "next_to", "a": "Sara", "b": "Nora"}
  ]
}
```
</details>

### 4. L4-01 · rep 1 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `parse`)
- **Mensaje del parser/solver:** unbalanced braces: the JSON object is never closed

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Nora": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Elena", "Vera", "Gina", "Paula"]},
    {"type": "alldiff", "vars": ["purple", "black", "orange", "yellow", "blue"]},
    {"type": "alldiff", "vars": ["horse", "rabbit", "bird", "hamster", "fish"]},
    {"type": "eq", "a": "Nora", "b": "orange"},
    {"type": "offset", "a": "Vera", "b": "hamster", "k": 1},
    {"type": "lt", "a": "Vera", "b": "blue"},
    {"type": "offset", "a": "Vera", "b": "blue", "k": -1},
    {"type": "lt", "a": "Gina", "b": "black"},
    {"type": "offset", "a": "Gina", "b": "black", "k": -1},
    {"type": "offset", "a": "Gina", "b": "Paula", "k": 1},
    {"type": "offset", "a": "Paula", "b": "black", "k": 1},
    {"type": "lt", "a": "Gina", "b": "orange"},
    {"type": "offset", "a": "Gina", "b": "orange", "k": -1},
    {"type": "lt", "a": "Nora", "b": "black"},
    {"type": "lt", "a": "Nora", "b": "orange"},
    {"type": "lt", "a": "Nora", "b": "purple"},
    {"type": "lt", "a": "Nora", "b": "yellow"},
    {"type": "lt", "a": "Nora", "b": "blue"},
    {"type": "lt", "a": "Elena", "b": "black"},
    {"type": "lt", "a": "Elena", "b": "orange"},
    {"type": "lt", "a": "Elena", "b": "purple"},
    {"type": "lt", "a": "Elena", "b": "yellow"},
    {"type": "lt", "a": "Elena", "b": "blue"},
    {"type": "eq", "a": "Vera", "b": "hamster"},
    {"type": "lt", "a": "Vera", "b": "orange"},
    {"type": "lt", "a": "Vera", "b": "purple"},
    {"type": "lt", "a": "Vera", "b": "yellow"},
    {"type": "lt", "a": "Vera", "b": "blue"},
    {"type": "lt", "a": "Elena", "b": "purple"},
    {"type": "lt", "a": "Elena", "b": "yellow"},
    {"type": "lt", "a": "Elena", "b": "blue"},
    {"type": "neq", "a": "Vera", "b": 1},
    {"type": "neq", "a": "Vera", "b": 2},
    {"type": "neq", "a": "Vera", "b": 3},
    {"type": "neq", "a": "Vera", "b": 4},
    {"type": "neq", "a": "Vera", "b": 5},
    {"type": "lt", "a": "Vera", "b": "Gina"},
    {"type": "lt", "a": "Vera", "b": "Gina"},
    {"type": "lt", "a": "Vera", "b": "Paula"},
    {"type": "lt", "a": "Vera", "b": "orange"},
    {"type": "lt", "a": "Vera", "b": "purple"},
    {"type": "lt", "a": "Vera", "b": "yellow"},
    {"type": "lt", "a": "Vera", "b": "blue"},
    {"type": "lt", "a": "Elena", "b": "orange"},
    {"type": "lt", "a": "Elena", "b": "purple"},
    {"type": "lt", "a": "Elena", "b": "yellow"},
    {"type": "lt", "a": "Elena", "b": "blue"},
    {"type": "lt", "a": "Gina", "b": "orange"},
    {"type": "lt", "a": "Gina", "b": "purple"},
    {"type": "lt", "a": "Gina", "b": "yellow"},
    {"type": "lt", "a": "Gina", "b": "blue"},
    {"type": "lt", "a": "Gina", "b": "Nora"},
    {"type": "lt", "a": "Gina", "b": "Vera"},
    {"type": "lt", "a": "Gina", "b": "Paula"},
    {"type": "lt", "a": "Gina", "b": "orange"},
    {"type": "lt", "a": "Gina", "b":
```
</details>

### 5. L4-05 · rep 1 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `schema`)
- **Mensaje del parser/solver:** constraint #11 (offset) is missing field 'k'

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Hugo": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Hugo", "Tomas", "Dev", "Elena", "Jon"]},
    {"type": "alldiff", "vars": ["red", "white", "orange", "purple", "blue"]},
    {"type": "alldiff", "vars": ["horse", "turtle", "dog", "fish"]},
    {"type": "eq", "a": "Elena", "b": "white"},
    {"type": "offset", "a": "Tomas", "b": "blue", "k": 1},
    {"type": "eq", "a": "Tomas", "b": "blue"},
    {"type": "neq", "a": "Elena", "b": 1},
    {"type": "eq", "a": "Dev", "b": "red"},
    {"type": "offset", "a": "orange", "b": "blue", "k": 1},
    {"type": "eq", "a": "Hugo", "b": "purple"},
    {"type": "offset", "a": "Hugo", "b": "purple"},
    {"type": "next_to", "a": "horse", "b": "fish"},
    {"type": "neq", "a": "purple", "b": 1},
    {"type": "eq", "a": "Jon", "b": "red"},
    {"type": "offset", "a": "red", "b": "red"},
    {"type": "neq", "a": "purple", "b": 1}
  ]
}
'''
```
</details>

### 6. L4-08 · rep 1 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `schema`)
- **Mensaje del parser/solver:** constraint #11 (offset) is missing field 'k'

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5], "Iris": [1, 2, 3, 4, 5], "Kai": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "turtle": [1, 2, 3, 4, 5], "dog": [1, 2, 3, 4, 5], "cat": [1, 2, 3, 4, 5], "rabbit": [1, 2, 3, 4, 5], "hamster": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Raul", "Dev", "Iris", "Kai", "Tomas"]},
  {"type": "alldiff", "vars": ["red", "black", "yellow", "orange", "white"]},
  {"type": "alldiff", "vars": ["turtle", "dog", "cat", "rabbit", "hamster"]},
  {"type": "eq", "a": "Dev", "b": "hamster"},
  {"type": "eq", "a": "Tomas", "b": "hamster"},
  {"type": "eq", "a": "Dev", "b": "Dev"},
  {"type": "eq", "a": "Tomas", "b": "Tomas"},
  {"type": "neq", "a": "Iris", "b": 4},
  {"type": "next_to", "a": "Iris", "b": "cat"},
  {"type": "next_to", "a": "Iris", "b": "Kai"},
  {"type": "offset", "a": "Tomas", "b": "Iris"},
  {"type": "alldiff", "vars": ["red", "black"]},
  {"type": "lt", "a": "Iris", "b": 4},
  {"type": "next_to", "a": "orange", "b": "dog"},
  {"type": "eq", "a": "dog", "b": "yellow"},
  {"type": "eq", "a": "Raul", "b": "red"},
  {"type": "alldiff", "vars": ["Raul", "Iris"]},
  {"type": "next_to", "a": "Iris", "b": "Kai"}
 ]}
 
Note: The JSON representation includes all variables and constraints for the given puzzle, but it does not solve the puzzle.
```
</details>

### 7. L1-05 · rep 3 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `parse`)
- **Mensaje del parser/solver:** unbalanced braces: the JSON object is never closed

<details><summary>Salida del modelo</summary>

```
{"variables": {"Paula": [1, 2, 3, 4], "Mateo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Nora": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Paula", "Mateo", "Sara", "Nora"]},
  {"type": "offset", "a": "Mateo", "b": "Sara", "k": 1},
  {"type": "alldiff", "vars": ["Sara", "Nora"]],
  {"type": "neq", "a": "Nora", "b": 4}
 ]}
```
</details>

### 8. L1-08 · rep 3 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `schema`)
- **Mensaje del parser/solver:** constraint #2 (offset) is missing field 'k'

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4], "Omar": [1, 2, 3, 4], "Kai": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "lt", "a": "Carla", "b": "Omar"},
  {"type": "offset", "a": "Carla", "b": "Raul"},
  {"type": "lt", "a": "Omar", "b": "Kai"}
 ]}
```
</details>

### 9. L3-07 · rep 3 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `schema`)
- **Mensaje del parser/solver:** constraint #7 (offset) is missing field 'k'

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Lucia": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "Nora": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Lucia", "Mateo", "Nora", "Paula", "Raul"]},
    {"type": "alldiff", "vars": ["yellow", "orange", "purple", "red", "green"]},
    {"type": "eq", "a": "red", "b": 5},
    {"type": "next_to", "a": "Nora", "b": "red"},
    {"type": "next_to", "a": "Nora", "b": "Lucia"},
    {"type": "next_to", "a": "green", "b": "Paula"},
    {"type": "offset", "a": "Mateo", "b": "green"},
    {"type": "offset", "a": "Mateo", "b": "orange"},
    {"type": "next_to", "a": "Nora", "b": "yellow"}
  ]
}
```
</details>

### 10. L4-07 · rep 3 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `schema`)
- **Mensaje del parser/solver:** constraint #12 (offset) is missing field 'k'

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Felix": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Felix", "Iris", "Elena", "Vera", "Mateo"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "white", "blue"]},
    {"type": "alldiff", "vars": ["fish", "turtle", "bird", "horse", "cat"]},
    {"type": "eq", "a": "turtle", "b": "orange", "k": 1},
    {"type": "offset", "a": "Felix", "b": "Iris", "k": 1},
    {"type": "neq", "a": "Vera", "b": 1},
    {"type": "eq", "a": "Felix", "b": "Iris"},
    {"type": "eq", "a": "Iris", "b": "bird"},
    {"type": "neq", "a": "Iris", "b": 5},
    {"type": "next_to", "a": "Iris", "b": "horse"},
    {"type": "eq", "a": "red", "b": "yellow", "k": 1},
    {"type": "offset", "a": "Iris", "b": "bird"},
    {"type": "neq", "a": "Iris", "b": 5},
    {"type": "offset", "a": "Iris", "b": "turtle"}
  ]
}
```
</details>

### 11. L4-03 · rep 4 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `parse`)
- **Mensaje del parser/solver:** invalid JSON: Expecting ',' delimiter: line 16 column 3 (char 941)

<details><summary>Salida del modelo</summary>

```
{"variables": {"Hugo": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Elena": [1, 2, 3, 4, 5],
                "Ben": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5],
                "yellow": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5],
                "green": [1, 2, 3, 4, 5], "turtle": [1, 2, 3, 4, 5], "fish": [1, 2, 3, 4, 5],
                "dog": [1, 2, 3, 4, 5], "bird": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Hugo", "Vera", "Elena", "Ben", "Dev"]},
  {"type": "alldiff", "vars": ["white", "yellow", "red", "blue", "green"]},
  {"type": "alldiff", "vars": ["turtle", "fish", "dog", "bird"]},
  {"type": "eq", "a": "Ben", "b": "yellow"},
  {"type": "eq", "a": "Dev", "b": "fish"},
  {"type": "lt", "a": "turtle", "b": "dog"},
  {"type": "offset", "a": "turtle", "b": "white", "k": 1},
  {"type": "eq", "a": "Dev", "b": 5},
  {"type": "lt", "a": "Elena", "b": "bird"}
  {"type": "next_to", "a": "Vera", "b": "red"}
  {"type": "next_to", "a": "Hugo", "b": "Dev"}
 ]}
```
</details>

### 12. L4-08 · rep 4 (T=0.7) · Sintaxis mala (no parsea)

- **Detectable sin verdad:** sí (señal: `schema`)
- **Mensaje del parser/solver:** constraint #7 (offset) is missing field 'k'

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5], "Iris": [1, 2, 3, 4, 5],
                "Kai": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5],
                "red": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5],
                "orange": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5],
                "turtle": [1, 2, 3, 4, 5], "dog": [1, 2, 3, 4, 5], "cat": [1, 2, 3, 4, 5],
                "hamster": [1, 2, 3, 4, 5], "rabbit": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Raul", "Dev", "Iris", "Kai", "Tomas"]},
  {"type": "alldiff", "vars": ["red", "black", "yellow", "orange", "white"]},
  {"type": "alldiff", "vars": ["turtle", "dog", "cat", "rabbit", "hamster"]},
  {"type": "eq", "a": "Raul", "b": "red"},
  {"type": "offset", "a": "dog", "b": "orange", "k": 1},
  {"type": "eq", "a": "hamster", "b": "dog"},
  {"type": "offset", "a": "cat", "b": "hamster"},
  {"type": "neq", "a": "Iris", "b": 4},
  {"type": "offset", "a": "turtle", "b": "dog", "k": -1},
  {"type": "alldiff", "vars": ["Iris", "Tomas"]},
  {"type": "next_to", "a": "Iris", "b": "Tomas"},
  {"type": "eq", "a": "white", "b": "black"},
  {"type": "eq", "a": "Dev", "b": "hamster"},
  {"type": "alldiff", "vars": ["Raul", "Iris"]},
  {"type": "next_to", "a": "Raul", "b": "Iris"}
 ]}
```
</details>

## Alcance / aridad (16)

### 13. L3-07 · rep 0 (T=0.0) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `scope`)
- **Mensaje del parser/solver:** constraint #7 (lt): b='Paula' is neither a declared variable nor a number
- **Nombres del enunciado sin variable:** `Raul`; `Paula`
- **Restricciones inventadas (la verdad las viola):** `eq(Nora, red)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Lucia": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "Nora": [1, 2, 3, 4, 5],
                "yellow": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5],
                "green": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Lucia", "Mateo", "Nora"]},
  {"type": "alldiff", "vars": ["yellow", "orange", "red", "green", "purple"]},
  {"type": "eq", "a": "Nora", "b": "red"},
  {"type": "eq", "a": "red", "b": 5},
  {"type": "lt", "a": "yellow", "b": "Nora"},
  {"type": "next_to", "a": "Nora", "b": "Lucia"},
  {"type": "lt", "a": "green", "b": "Paula"},
  {"type": "next_to", "a": "green", "b": "Mateo"},
  {"type": "next_to", "a": "Mateo", "b": "orange"}
 ]}
```
</details>

### 14. L3-08 · rep 0 (T=0.0) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Problemas de alcance en alldiff:** `un alldiff deja fuera a miembros del grupo 'person'`; `un alldiff deja fuera a miembros del grupo 'colour'`
- **Restricciones inventadas (la verdad las viola):** `offset(Iris, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Iris": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Felix": [1, 2, 3, 4, 5],
    "Nora": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Iris", "Paula", "Felix"]},
    {"type": "alldiff", "vars": ["Ana", "blue", "green"]},
    {"type": "offset", "a": "Paula", "b": "Felix", "k": 1},
    {"type": "next_to", "a": "Ana", "b": "green"},
    {"type": "offset", "a": "Iris", "b": "white", "k": 1},
    {"type": "eq", "a": "Iris", "b": "white"},
    {"type": "neq", "a": "Nora", "b": 2},
    {"type": "next_to", "a": "blue", "b": "white"}
  ]
}
```
</details>

### 15. L4-06 · rep 0 (T=0.0) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Nombres del enunciado sin variable:** `blue`
- **Problemas de alcance en alldiff:** `alldiff mezcla grupos ['colour', 'pet']: alldiff(red, orange, yellow, green, bird, hamster, rabbit, turtle, horse)`
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, green)`; `eq(Kai, yellow)`; `eq(green, rabbit)`; `eq(red, bird)`; `offset(Hugo, horse, k=-1)`; `neq(horse, 5)`
- **Restricciones invertidas:** `offset(Hugo, hamster, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Hugo", "Kai", "Elena", "Carla"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "green", "bird", "hamster", "rabbit", "turtle", "horse"]},
    {"type": "eq", "a": "Hugo", "b": "green"},
    {"type": "offset", "a": "Hugo", "b": "hamster", "k": 1},
    {"type": "neq", "a": "Raul", "b": "turtle"},
    {"type": "offset", "a": "Kai", "b": "yellow", "k": 1},
    {"type": "offset", "a": "Elena", "b": "Raul", "k": 1},
    {"type": "eq", "a": "Kai", "b": "yellow"},
    {"type": "eq", "a": "green", "b": "rabbit"},
    {"type": "neq", "a": "Carla", "b": 1},
    {"type": "eq", "a": "red", "b": "bird"},
    {"type": "offset", "a": "Hugo", "b": "horse", "k": -1},
    {"type": "neq", "a": "horse", "b": 5}
  ]
}
'''
```
</details>

### 16. L2-08 · rep 1 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `scope`)
- **Mensaje del parser/solver:** constraint #5 (next_to): b='Dev' is neither a declared variable nor a number
- **Nombres del enunciado sin variable:** `Dev`
- **Restricciones inventadas (la verdad las viola):** `offset(Sara, red, k=1)`; `offset(Mateo, black, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Elena": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Mateo": [1, 2, 3, 4],
                "red": [1, 2, 3, 4], "orange": [1, 2, 3, 4], "black": [1, 2, 3, 4], "yellow": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Elena", "Sara", "Mateo"]},
  {"type": "alldiff", "vars": ["red", "orange", "black", "yellow"]},
  {"type": "eq", "a": "Elena", "b": "yellow"},
  {"type": "offset", "a": "Sara", "b": "red", "k": 1},
  {"type": "next_to", "a": "Elena", "b": "Dev"},
  {"type": "eq", "a": "Dev", "b": 4},
  {"type": "offset", "a": "Mateo", "b": "black", "k": 1}
 ]}
```
</details>

### 17. L3-07 · rep 1 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `scope`)
- **Mensaje del parser/solver:** constraint #4 (eq): a=5 is not a declared variable
- **Nombres del enunciado sin variable:** `Raul`; `Paula`
- **Restricciones inventadas (la verdad las viola):** `eq(Nora, red)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Lucia": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "Nora": [1, 2, 3, 4, 5],
                "yellow": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5],
                "green": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Lucia", "Mateo", "Nora"]},
  {"type": "alldiff", "vars": ["yellow", "orange", "red", "green", "purple"]},
  {"type": "eq", "a": "Nora", "b": "red"},
  {"type": "eq", "a": 5, "b": "red"},
  {"type": "lt", "a": "Nora", "b": 6},
  {"type": "next_to", "a": "Nora", "b": "Lucia"},
  {"type": "lt", "a": "green", "b": 6},
  {"type": "next_to", "a": "green", "b": "Mateo"},
  {"type": "next_to", "a": "Mateo", "b": "orange"}
 ]}
```
</details>

### 18. L4-03 · rep 1 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `scope`)
- **Mensaje del parser/solver:** constraint #2 (alldiff): vars='blue' is not a declared variable
- **Nombres del enunciado sin variable:** `blue`; `green`
- **Restricciones inventadas (la verdad las viola):** `eq(Vera, red)`; `eq(turtle, blue)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Hugo": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Elena": [1, 2, 3, 4, 5], "Ben": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5],
                "white": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5],
                "dog": [1, 2, 3, 4, 5], "turtle": [1, 2, 3, 4, 5], "fish": [1, 2, 3, 4, 5], "cat": [1, 2, 3, 4, 5], "bird": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Hugo", "Vera", "Elena", "Ben", "Dev"]},
  {"type": "alldiff", "vars": ["white", "yellow", "red", "blue", "green"]},
  {"type": "alldiff", "vars": ["dog", "turtle", "fish", "cat", "bird"]},
  {"type": "eq", "a": "Vera", "b": "red"},
  {"type": "eq", "a": "Ben", "b": "yellow"},
  {"type": "lt", "a": "Hugo", "b": "Dev"},
  {"type": "eq", "a": "turtle", "b": "blue"},
  {"type": "lt", "a": "turtle", "b": "dog"},
  {"type": "lt", "a": "white", "b": "turtle"},
  {"type": "eq", "a": "fish", "b": "white"},
  {"type": "eq", "a": "Dev", "b": "fish"},
  {"type": "lt", "a": "Elena", "b": "bird"}
 ]}
```
</details>

### 19. L4-06 · rep 1 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Nombres del enunciado sin variable:** `blue`
- **Problemas de alcance en alldiff:** `alldiff mezcla grupos ['colour', 'pet']: alldiff(red, orange, yellow, green, bird)`; `un alldiff deja fuera a miembros del grupo 'pet'`
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, green)`; `offset(Kai, Kai, k=1)`; `offset(Hugo, Hugo, k=1)`; `offset(Kai, Kai, k=1)`; `offset(Carla, Carla, k=1)`
- **Restricciones invertidas:** `offset(Raul, Elena, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "hamster_owner": [1, 2, 3, 4, 5],
    "rabbit_owner": [1, 2, 3, 4, 5],
    "turtle_owner": [1, 2, 3, 4, 5],
    "bird_owner": [1, 2, 3, 4, 5],
    "horse_owner": [1, 2, 3, 4, 5],
    "turtle_owner": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Hugo", "Kai", "Elena", "Carla"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "green", "bird"]},
    {"type": "alldiff", "vars": ["hamster", "rabbit", "turtle", "horse"]},
    {"type": "eq", "a": "Hugo", "b": "green"},
    {"type": "offset", "a": "hamster_owner", "b": "rabbit_owner", "k": 1},
    {"type": "neq", "a": "Raul", "b": "turtle_owner"},
    {"type": "offset", "a": "Kai", "b": "yellow", "k": 1},
    {"type": "eq", "a": "green", "b": "rabbit_owner"},
    {"type": "offset", "a": "Carla", "b": "rabbit_owner", "k": 1},
    {"type": "eq", "a": "red", "b": "bird_owner"},
    {"type": "offset", "a": "Hugo", "b": "horse_owner", "k": 1},
    {"type": "neq", "a": "Hugo", "b": "yellow"},
    {"type": "offset", "a": "Kai", "b": "Kai", "k": 1},
    {"type": "eq", "a": "Hugo", "b": "Hugo"},
    {"type": "offset", "a": "Raul", "b": "Elena", "k": 1},
    {"type": "offset", "a": "Hugo", "b": "Hugo", "k": 1},
    {"type": "offset", "a": "Kai", "b": "Kai", "k": 1},
    {"type": "offset", "a": "Carla", "b": "Carla", "k": 1}
  ]
}
```
</details>

### 20. L4-05 · rep 2 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `scope`)
- **Mensaje del parser/solver:** constraint #9 (next_to): a='Horse' is not a declared variable
- **Nombres del enunciado sin variable:** `cat`
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, red)`; `neq(Elena, 1)`; `next_to(Jon, Tomas)`
- **Restricciones invertidas:** `offset(Dev, purple, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Hugo": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Hugo", "Tomas", "Dev", "Elena", "Jon"]},
    {"type": "alldiff", "vars": ["red", "white", "orange", "purple", "blue"]},
    {"type": "alldiff", "vars": ["horse", "turtle", "dog", "fish"]},
    {"type": "eq", "a": "Hugo", "b": "red"},
    {"type": "offset", "a": "Dev", "b": "purple", "k": 1},
    {"type": "eq", "a": "Tomas", "b": "blue"},
    {"type": "neq", "a": "Elena", "b": 1},
    {"type": "offset", "a": "Hugo", "b": "Jon", "k": 1},
    {"type": "next_to", "a": "Horse", "b": "fish"},
    {"type": "neq", "a": "purple", "b": 5},
    {"type": "offset", "a": "blue", "b": "orange", "k": 1},
    {"type": "next_to", "a": "white", "b": "Elena"},
    {"type": "next_to", "a": "Horse", "b": "fish"},
    {"type": "next_to", "a": "purple", "b": "Hugo"},
    {"type": "next_to", "a": "Jon", "b": "Tomas"}
  ]
}
```
</details>

### 21. L4-06 · rep 2 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Nombres del enunciado sin variable:** `blue`
- **Problemas de alcance en alldiff:** `alldiff mezcla grupos ['colour', 'pet']: alldiff(red, orange, yellow, green, bird)`; `un alldiff deja fuera a miembros del grupo 'pet'`
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, green)`; `next_to(green, Kai)`; `eq(green, rabbit)`; `next_to(red, bird)`; `next_to(Hugo, horse)`
- **Restricciones invertidas:** `offset(hamster, rabbit, k=1)`; `offset(bird, Carla, k=1)`; `offset(Raul, Elena, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Hugo", "Kai", "Elena", "Carla"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "green", "bird"]},
    {"type": "alldiff", "vars": ["hamster", "horse", "rabbit", "turtle"]},
    {"type": "eq", "a": "Hugo", "b": "green"},
    {"type": "offset", "a": "hamster", "b": "rabbit", "k": 1},
    {"type": "neq", "a": "Raul", "b": "turtle"},
    {"type": "next_to", "a": "green", "b": "Kai"},
    {"type": "offset", "a": "bird", "b": "Carla", "k": 1},
    {"type": "offset", "a": "Raul", "b": "Elena", "k": 1},
    {"type": "next_to", "a": "yellow", "b": "Kai"},
    {"type": "eq", "a": "green", "b": "rabbit"},
    {"type": "next_to", "a": "red", "b": "bird"},
    {"type": "neq", "a": "Hugo", "b": "yellow"},
    {"type": "next_to", "a": "Hugo", "b": "horse"}
  ]
}
'''
```
</details>

### 22. L2-08 · rep 3 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Problemas de alcance en alldiff:** `un alldiff deja fuera a miembros del grupo 'person'`
- **Restricciones inventadas (la verdad las viola):** `offset(Sara, red, k=1)`; `offset(Dev, black, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Mateo": [1, 2, 3, 4],
    "Dev": [1, 2, 3, 4],
    "red": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Sara", "Mateo"]},
    {"type": "alldiff", "vars": ["Elena", "Dev"]},
    {"type": "alldiff", "vars": ["red", "orange", "black", "yellow"]},
    {"type": "eq", "a": "Elena", "b": "yellow"},
    {"type": "offset", "a": "Sara", "b": "red", "k": 1},
    {"type": "neq", "a": "Mateo", "b": 1},
    {"type": "offset", "a": "Dev", "b": "black", "k": 1},
    {"type": "eq", "a": "Dev", "b": 4},
    {"type": "next_to", "a": "Elena", "b": "Dev"}
  ]
}
```
</details>

### 23. L3-02 · rep 3 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Problemas de alcance en alldiff:** `un alldiff deja fuera a miembros del grupo 'person'`
- **Restricciones inventadas (la verdad las viola):** `eq(Mateo, orange)`; `next_to(red, Ana)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Gina": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Gina", "Ana", "Mateo"]},
    {"type": "alldiff", "vars": ["purple", "black", "red", "orange", "blue"]},
    {"type": "eq", "a": "Mateo", "b": "orange"},
    {"type": "next_to", "a": "Mateo", "b": "orange"},
    {"type": "next_to", "a": "red", "b": "Ana"},
    {"type": "next_to", "a": "Gina", "b": "Ana"},
    {"type": "next_to", "a": "black", "b": "red"},
    {"type": "next_to", "a": "black", "b": "Tomas"},
    {"type": "next_to", "a": "blue", "b": "purple"}
  ]
}
```
</details>

### 24. L3-08 · rep 3 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ana": 1, "green": 2, "blue": 1, "white": 3, "Iris": 3, "orange": 4, "Paula": 5, "Felix": 4, "red": 2, "Nora": 1}`
- **Respuesta correcta:** `{"Iris": 2, "Paula": 4, "Ana": 5, "Felix": 3, "Nora": 1, "blue": 3, "red": 1, "white": 2, "green": 4, "orange": 5}`
- **Problemas de alcance en alldiff:** `alldiff mezcla grupos ['colour', 'person']: alldiff(Ana, green, white, orange)`; `un alldiff deja fuera a miembros del grupo 'person'`; `un alldiff deja fuera a miembros del grupo 'colour'`
- **Pistas perdidas:** `offset(blue, white, k=1)`; `lt(red, Ana)`; `neq(blue, 2)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Iris": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Felix": [1, 2, 3, 4, 5],
    "Nora": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Iris", "Paula", "Felix"]},
    {"type": "alldiff", "vars": ["Ana", "green", "white", "orange"]},
    {"type": "offset", "a": "Paula", "b": "Felix", "k": 1},
    {"type": "next_to", "a": "Ana", "b": "green"},
    {"type": "offset", "a": "green", "b": "blue", "k": 1},
    {"type": "neq", "a": "red", "b": "Ana"},
    {"type": "lt", "a": "Iris", "b": "Paula"},
    {"type": "eq", "a": "Iris", "b": "white"}
  ]
}
```
</details>

### 25. L4-06 · rep 3 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Nombres del enunciado sin variable:** `blue`
- **Problemas de alcance en alldiff:** `alldiff mezcla grupos ['colour', 'pet']: alldiff(red, orange, yellow, green, bird, hamster, horse, rabbit, turtle)`
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, green)`; `eq(Elena, Raul)`; `eq(green, rabbit)`; `offset(red, bird, k=1)`; `eq(Hugo, horse)`
- **Restricciones invertidas:** `offset(hamster, rabbit, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Hugo", "Kai", "Elena", "Carla"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "green", "bird", "hamster", "horse", "rabbit", "turtle"]},
    {"type": "eq", "a": "Hugo", "b": "green"},
    {"type": "offset", "a": "hamster", "b": "rabbit", "k": 1},
    {"type": "neq", "a": "Raul", "b": 5},
    {"type": "offset", "a": "Kai", "b": "yellow", "k": 1},
    {"type": "eq", "a": "Elena", "b": "Raul"},
    {"type": "offset", "a": "Carla", "b": "bird", "k": 1},
    {"type": "eq", "a": "green", "b": "rabbit"},
    {"type": "neq", "a": "Carla", "b": 2},
    {"type": "offset", "a": "red", "b": "bird", "k": 1},
    {"type": "eq", "a": "Hugo", "b": "horse"},
    {"type": "neq", "a": "horse", "b": 4},
    {"type": "neq", "a": "Hugo", "b": 4}
  ]
}
'''
```
</details>

### 26. L2-08 · rep 4 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `scope`)
- **Mensaje del parser/solver:** constraint #7 (neq): a='Dev' is not a declared variable
- **Nombres del enunciado sin variable:** `Dev`
- **Restricciones inventadas (la verdad las viola):** `offset(Sara, red, k=1)`; `offset(Mateo, black, k=1)`; `eq(Elena, Sara)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Elena": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Mateo": [1, 2, 3, 4],
                "red": [1, 2, 3, 4], "orange": [1, 2, 3, 4], "black": [1, 2, 3, 4],
                "yellow": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Elena", "Sara", "Mateo"]},
  {"type": "alldiff", "vars": ["red", "orange", "black", "yellow"]},
  {"type": "eq", "a": "Elena", "b": "yellow"},
  {"type": "offset", "a": "Sara", "b": "red", "k": 1},
  {"type": "offset", "a": "Mateo", "b": "black", "k": 1},
  {"type": "eq", "a": "Elena", "b": "Sara"},
  {"type": "neq", "a": "Dev", "b": 4},
  {"type": "neq", "a": "Dev", "b": 3},
  {"type": "neq", "a": "Dev", "b": 2},
  {"type": "eq", "a": "Dev", "b": 4}
 ]}
```
</details>

### 27. L3-07 · rep 4 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `scope`)
- **Mensaje del parser/solver:** constraint #7 (next_to): b='Paula' is neither a declared variable nor a number
- **Nombres del enunciado sin variable:** `Raul`; `Paula`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Lucia": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "Nora": [1, 2, 3, 4, 5],
                "yellow": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5],
                "green": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Lucia", "Mateo", "Nora"]},
  {"type": "alldiff", "vars": ["yellow", "orange", "red", "green", "purple"]},
  {"type": "eq", "a": "red", "b": 5},
  {"type": "next_to", "a": "red", "b": "Nora"},
  {"type": "next_to", "a": "Nora", "b": "Lucia"},
  {"type": "lt", "a": "yellow", "b": "Nora"},
  {"type": "next_to", "a": "green", "b": "Paula"},
  {"type": "next_to", "a": "green", "b": "Mateo"},
  {"type": "next_to", "a": "orange", "b": "Mateo"}
 ]}
```
</details>

### 28. L3-08 · rep 4 (T=0.7) · Alcance / aridad

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Problemas de alcance en alldiff:** `un alldiff deja fuera a miembros del grupo 'person'`; `un alldiff deja fuera a miembros del grupo 'colour'`
- **Restricciones inventadas (la verdad las viola):** `offset(Ana, white, k=1)`; `eq(white, blue)`; `eq(Ana, green)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Iris": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Felix": [1, 2, 3, 4, 5],
    "Nora": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Iris", "Paula", "Felix"]},
    {"type": "alldiff", "vars": ["Ana", "blue", "green"]},
    {"type": "offset", "a": "Ana", "b": "white", "k": 1},
    {"type": "eq", "a": "white", "b": "blue"},
    {"type": "neq", "a": "red", "b": "Ana"},
    {"type": "next_to", "a": "Iris", "b": "Felix"},
    {"type": "eq", "a": "Iris", "b": "white"},
    {"type": "next_to", "a": "Paula", "b": "Felix"},
    {"type": "eq", "a": "Ana", "b": "green"},
    {"type": "neq", "a": "Ana", "b": 2}
  ]
}
```
</details>

## Sobre-restringido (sin solución) (79)

### 29. L1-05 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Sara, Nora)`
- **Restricciones invertidas:** `offset(Mateo, Sara, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Paula": [1, 2, 3, 4], "Mateo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Nora": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Paula", "Mateo", "Sara", "Nora"]},
  {"type": "eq", "a": "Sara", "b": "Nora"},
  {"type": "neq", "a": "Nora", "b": 4},
  {"type": "offset", "a": "Mateo", "b": "Sara", "k": 1}
 ]}
```
</details>

### 30. L1-06 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, Hugo, k=1)`
- **Restricciones invertidas:** `offset(Lucia, Hugo, k=1)`; `offset(Omar, Ben, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Lucia": [1, 2, 3, 4], "Ben": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Omar": [1, 2, 3, 4]},
 "constraints": [
  {"type": "offset", "a": "Lucia", "b": "Hugo", "k": 1},
  {"type": "offset", "a": "Omar", "b": "Hugo", "k": 1},
  {"type": "offset", "a": "Omar", "b": "Ben", "k": 1},
  {"type": "alldiff", "vars": ["Lucia", "Hugo", "Omar", "Ben"]}
 ]}
```
</details>

### 31. L2-01 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Tomas, Lucia)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Tomas": [1, 2, 3, 4],
    "Ana": [1, 2, 3, 4],
    "Lucia": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Tomas", "Ana", "Lucia", "Ben"]},
    {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
    {"type": "eq", "a": "Ana", "b": "blue"},
    {"type": "offset", "a": "Tomas", "b": "orange", "k": 1},
    {"type": "eq", "a": "Tomas", "b": "Lucia"},
    {"type": "neq", "a": "Lucia", "b": "white"},
    {"type": "next_to", "a": "Ana", "b": "Lucia"}
  ]
}
```
</details>

### 32. L2-02 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Kai, white)`
- **Restricciones invertidas:** `offset(Kai, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Ana": [1, 2, 3, 4],
    "Raul": [1, 2, 3, 4],
    "Kai": [1, 2, 3, 4],
    "Dev": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Ana", "Raul", "Kai", "Dev"]},
    {"type": "alldiff", "vars": ["white", "green", "purple", "red"]},
    {"type": "eq", "a": "Kai", "b": "white"},
    {"type": "eq", "a": "white", "b": 3},
    {"type": "lt", "a": "Dev", "b": 3},
    {"type": "next_to", "a": "green", "b": "red"},
    {"type": "next_to", "a": "Ana", "b": "white"},
    {"type": "offset", "a": "Kai", "b": "white", "k": 1}
  ]
}
```
</details>

### 33. L2-03 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Hugo, white, k=1)`; `lt(Hugo, 4)`; `eq(Jon, 4)`
- **Restricciones invertidas:** `lt(Jon, 1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Dev": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4],
    "Jon": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Dev", "Sara", "Hugo", "Jon"]},
    {"type": "alldiff", "vars": ["white", "black", "yellow", "red"]},
    {"type": "eq", "a": "Sara", "b": "black"},
    {"type": "offset", "a": "Hugo", "b": "white", "k": 1},
    {"type": "neq", "a": "Hugo", "b": 3},
    {"type": "lt", "a": "Hugo", "b": 4},
    {"type": "lt", "a": "Jon", "b": 1},
    {"type": "eq", "a": "Jon", "b": 4},
    {"type": "next_to", "a": "Sara", "b": "Hugo"}
  ]
}
```
</details>

### 34. L2-04 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(white, Gina)`
- **Restricciones invertidas:** `offset(Raul, Gina, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4],
    "Ana": [1, 2, 3, 4],
    "Gina": [1, 2, 3, 4],
    "Lucia": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Ana", "Gina", "Lucia"]},
    {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
    {"type": "eq", "a": "white", "b": "Gina"},
    {"type": "offset", "a": "Raul", "b": "Gina", "k": 1},
    {"type": "next_to", "a": "Raul", "b": "blue"},
    {"type": "next_to", "a": "Raul", "b": "orange"},
    {"type": "next_to", "a": "black", "b": "orange"},
    {"type": "eq", "a": "Lucia", "b": "orange"}
  ]
}
```
</details>

### 35. L2-06 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(purple, red)`
- **Restricciones invertidas:** `offset(Carla, Ben, k=1)`; `offset(black, red, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4],
    "Mateo": [1, 2, 3, 4],
    "Carla": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Mateo", "Carla", "Ben"]},
    {"type": "alldiff", "vars": ["black", "purple", "white", "red"]},
    {"type": "offset", "a": "Carla", "b": "Ben", "k": 1},
    {"type": "eq", "a": "purple", "b": "red"},
    {"type": "offset", "a": "black", "b": "red", "k": 1},
    {"type": "next_to", "a": "Sara", "b": "Ben"},
    {"type": "next_to", "a": "Sara", "b": "black"}
  ]
}
```
</details>

### 36. L2-10 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(purple, yellow)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Elena": [1, 2, 3, 4], "Paula": [1, 2, 3, 4], "Omar": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4],
                "purple": [1, 2, 3, 4], "yellow": [1, 2, 3, 4], "green": [1, 2, 3, 4], "blue": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Elena", "Paula", "Omar", "Hugo"]},
  {"type": "alldiff", "vars": ["purple", "yellow", "green", "blue"]},
  {"type": "eq", "a": "Elena", "b": "green"},
  {"type": "offset", "a": "Elena", "b": "Omar", "k": 1},
  {"type": "eq", "a": "purple", "b": "yellow"},
  {"type": "next_to", "a": "Elena", "b": "Omar"},
  {"type": "neq", "a": "green", "b": 1},
  {"type": "lt", "a": "purple", "b": "Hugo"},
  {"type": "next_to", "a": "Hugo", "b": "blue"}
 ]}
```
</details>

### 37. L3-01 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, yellow, k=1)`; `eq(green, white)`
- **Restricciones invertidas:** `offset(Hugo, Lucia, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Jon": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Jon", "Omar", "Elena", "Lucia", "Hugo"]},
    {"type": "alldiff", "vars": ["white", "green", "black", "orange", "yellow"]},
    {"type": "eq", "a": "Elena", "b": "white"},
    {"type": "offset", "a": "Omar", "b": "yellow", "k": 1},
    {"type": "eq", "a": "Omar", "b": "yellow"},
    {"type": "offset", "a": "Hugo", "b": "Lucia", "k": 1},
    {"type": "eq", "a": "green", "b": "white"},
    {"type": "neq", "a": "Hugo", "b": 1}
  ]
}
```
</details>

### 38. L3-02 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Mateo, orange)`; `eq(red, Ana)`; `eq(Gina, Ana)`; `eq(blue, purple)`
- **Restricciones invertidas:** `lt(Ana, 1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Gina": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Gina", "Mateo", "Ana", "Ben", "Tomas"]},
    {"type": "alldiff", "vars": ["purple", "black", "red", "orange", "blue"]},
    {"type": "eq", "a": "Mateo", "b": "orange"},
    {"type": "next_to", "a": "Mateo", "b": "orange"},
    {"type": "eq", "a": "red", "b": "Ana"},
    {"type": "lt", "a": "Ana", "b": 1},
    {"type": "eq", "a": "Gina", "b": "Ana"},
    {"type": "next_to", "a": "red", "b": "black"},
    {"type": "eq", "a": "blue", "b": "purple"},
    {"type": "next_to", "a": "black", "b": "Tomas"}
  ]
}
```
</details>

### 39. L3-03 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, Ben)`; `offset(Omar, Iris, k=1)`; `eq(green, Sara)`
- **Restricciones invertidas:** `offset(white, Omar, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Omar", "Hugo", "Iris", "Ben"]},
    {"type": "alldiff", "vars": ["red", "green", "orange", "purple", "white"]},
    {"type": "eq", "a": "Hugo", "b": "Ben"},
    {"type": "offset", "a": "Ben", "b": "purple", "k": 1},
    {"type": "offset", "a": "white", "b": "Omar", "k": 1},
    {"type": "offset", "a": "Omar", "b": "Iris", "k": 1},
    {"type": "eq", "a": "green", "b": "Sara"},
    {"type": "next_to", "a": "Ben", "b": "green"},
    {"type": "neq", "a": "orange", "b": 5}
  ]
}
```
</details>

### 40. L3-05 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Paula, blue)`; `next_to(Paula, Kai)`; `next_to(black, red)`; `next_to(Kai, Ben)`
- **Restricciones invertidas:** `offset(Mateo, black, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Ben": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Ben", "Mateo", "Kai", "Paula", "Gina"]},
    {"type": "alldiff", "vars": ["blue", "purple", "black", "red", "green"]},
    {"type": "eq", "a": "Paula", "b": "blue"},
    {"type": "next_to", "a": "Paula", "b": "Kai"},
    {"type": "next_to", "a": "black", "b": "green"},
    {"type": "offset", "a": "Mateo", "b": "black", "k": 1},
    {"type": "next_to", "a": "Ben", "b": "blue"},
    {"type": "neq", "a": "Paula", "b": 2},
    {"type": "next_to", "a": "black", "b": "red"},
    {"type": "next_to", "a": "Kai", "b": "Ben"}
  ]
}
```
</details>

### 41. L3-10 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Sara, black)`; `neq(Raul, 2)`; `eq(Lucia, black)`; `offset(Tomas, green, k=1)`
- **Restricciones invertidas:** `offset(Raul, yellow, k=1)`; `offset(Lucia, Ben, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Lucia", "Tomas", "Raul", "Ben"]},
    {"type": "alldiff", "vars": ["green", "yellow", "orange", "black", "white"]},
    {"type": "eq", "a": "Sara", "b": "black"},
    {"type": "offset", "a": "Raul", "b": "yellow", "k": 1},
    {"type": "neq", "a": "Raul", "b": 2},
    {"type": "eq", "a": "Raul", "b": "orange"},
    {"type": "offset", "a": "Lucia", "b": "Ben", "k": 1},
    {"type": "alldiff", "vars": ["orange", "Lucia"]},
    {"type": "eq", "a": "Lucia", "b": "black"},
    {"type": "offset", "a": "Tomas", "b": "green", "k": 1}
  ]
}
```
</details>

### 42. L4-01 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Vera, hamster, k=1)`; `eq(Vera, blue)`; `neq(Gina, 1)`; `neq(Gina, 1)`
- **Restricciones invertidas:** `offset(Gina, black, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Nora": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Elena", "Vera", "Gina", "Paula"]},
    {"type": "alldiff", "vars": ["purple", "black", "orange", "yellow", "blue"]},
    {"type": "alldiff", "vars": ["horse", "rabbit", "bird", "hamster", "fish"]},
    {"type": "eq", "a": "Nora", "b": "orange"},
    {"type": "offset", "a": "Vera", "b": "hamster", "k": 1},
    {"type": "neq", "a": "Vera", "b": 1},
    {"type": "eq", "a": "Vera", "b": "blue"},
    {"type": "offset", "a": "Elena", "b": "bird", "k": 1},
    {"type": "neq", "a": "Nora", "b": 1},
    {"type": "offset", "a": "Paula", "b": "rabbit", "k": 1},
    {"type": "neq", "a": "Gina", "b": 1},
    {"type": "offset", "a": "Gina", "b": "black", "k": 1},
    {"type": "neq", "a": "Gina", "b": 1},
    {"type": "neq", "a": "Paula", "b": 1}
  ]
}
```
</details>

### 43. L4-04 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(yellow, hamster)`; `eq(Lucia, turtle)`; `eq(Lucia, yellow)`; `eq(Ben, Lucia)`; `eq(purple, Ben)`
- **Restricciones invertidas:** `offset(red, turtle, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Paula": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Lucia", "Vera", "Raul", "Ben"]},
    {"type": "alldiff", "vars": ["orange", "red", "yellow", "purple", "black"]},
    {"type": "alldiff", "vars": ["bird", "dog", "hamster", "turtle", "fish"]},
    {"type": "eq", "a": "yellow", "b": "hamster"},
    {"type": "offset", "a": "red", "b": "turtle", "k": 1},
    {"type": "eq", "a": "Lucia", "b": "turtle"},
    {"type": "eq", "a": "Lucia", "b": "yellow"},
    {"type": "neq", "a": "Raul", "b": 5},
    {"type": "eq", "a": "Ben", "b": "Lucia"},
    {"type": "neq", "a": "Raul", "b": 4},
    {"type": "eq", "a": "purple", "b": "Ben"},
    {"type": "lt", "a": "fish", "b": 5}
  ]
}
```
</details>

### 44. L4-05 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Nombres del enunciado sin variable:** `cat`
- **Restricciones inventadas (la verdad las viola):** `eq(purple, horse)`; `neq(Elena, 1)`; `eq(orange, blue)`; `eq(purple, Hugo)`; `eq(white, Elena)`; `eq(red, Jon)`
- **Restricciones invertidas:** `offset(Elena, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Hugo": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Hugo", "Tomas", "Dev", "Elena", "Jon"]},
    {"type": "alldiff", "vars": ["red", "white", "orange", "purple", "blue"]},
    {"type": "alldiff", "vars": ["horse", "turtle", "dog", "fish"]},
    {"type": "eq", "a": "purple", "b": "horse"},
    {"type": "offset", "a": "Elena", "b": "white", "k": 1},
    {"type": "eq", "a": "Tomas", "b": "blue"},
    {"type": "neq", "a": "Elena", "b": 1},
    {"type": "offset", "a": "Dev", "b": "red", "k": 1},
    {"type": "eq", "a": "orange", "b": "blue"},
    {"type": "eq", "a": "purple", "b": "Hugo"},
    {"type": "next_to", "a": "horse", "b": "fish"},
    {"type": "neq", "a": "purple", "b": "fish"},
    {"type": "next_to", "a": "white", "b": "dog"},
    {"type": "eq", "a": "white", "b": "Elena"},
    {"type": "eq", "a": "red", "b": "Jon"}
  ]
}
```
</details>

### 45. L4-08 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(dog, yellow, k=1)`; `eq(Iris, cat)`; `eq(Kai, turtle)`; `eq(Iris, 1)`; `next_to(Raul, Iris)`; `eq(white, black)`; `next_to(Iris, Kai)`
- **Restricciones invertidas:** `offset(dog, turtle, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Dev", "Iris", "Kai", "Tomas"]},
    {"type": "alldiff", "vars": ["red", "black", "yellow", "orange", "white"]},
    {"type": "alldiff", "vars": ["turtle", "dog", "cat", "rabbit", "hamster"]},
    {"type": "eq", "a": "Dev", "b": "hamster"},
    {"type": "eq", "a": "Raul", "b": "red"},
    {"type": "offset", "a": "dog", "b": "yellow", "k": 1},
    {"type": "eq", "a": "Iris", "b": "cat"},
    {"type": "offset", "a": "dog", "b": "turtle", "k": 1},
    {"type": "eq", "a": "Kai", "b": "turtle"},
    {"type": "alldiff", "vars": ["Iris", "Tomas"]},
    {"type": "next_to", "a": "Iris", "b": "Tomas"},
    {"type": "eq", "a": "Iris", "b": "1"},
    {"type": "neq", "a": "Iris", "b": "4"},
    {"type": "next_to", "a": "Raul", "b": "Iris"},
    {"type": "next_to", "a": "Tomas", "b": "Iris"},
    {"type": "eq", "a": "white", "b": "black"},
    {"type": "next_to", "a": "Iris", "b": "Kai"}
  ]
}
```
</details>

### 46. L4-10 · rep 0 (T=0.0) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Elena, turtle)`; `offset(Iris, fish, k=1)`; `next_to(horse, yellow)`; `next_to(turtle, yellow)`
- **Restricciones invertidas:** `offset(orange, purple, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Iris", "Raul", "Jon", "Ana"]},
    {"type": "alldiff", "vars": ["orange", "purple", "yellow", "blue", "black"]},
    {"type": "alldiff", "vars": ["bird", "turtle", "rabbit", "fish", "horse"]},
    {"type": "eq", "a": "Elena", "b": "turtle"},
    {"type": "offset", "a": "Iris", "b": "fish", "k": 1},
    {"type": "next_to", "a": "black", "b": "turtle"},
    {"type": "next_to", "a": "horse", "b": "yellow"},
    {"type": "eq", "a": "rabbit", "b": "purple"},
    {"type": "next_to", "a": "Iris", "b": "Elena"},
    {"type": "neq", "a": "Raul", "b": 3},
    {"type": "next_to", "a": "turtle", "b": "yellow"},
    {"type": "next_to", "a": "Raul", "b": "purple"},
    {"type": "offset", "a": "orange", "b": "purple", "k": 1},
    {"type": "next_to", "a": "orange", "b": "Ana"}
  ]
}
```
</details>

### 47. L1-06 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, Hugo, k=1)`
- **Restricciones invertidas:** `offset(Lucia, Hugo, k=1)`; `offset(Omar, Ben, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Lucia": [1, 2, 3, 4], "Ben": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Omar": [1, 2, 3, 4]},
  "constraints": [
    {"type": "alldiff", "vars": ["Lucia", "Hugo", "Ben", "Omar"]},
    {"type": "offset", "a": "Lucia", "b": "Hugo", "k": 1},
    {"type": "offset", "a": "Omar", "b": "Hugo", "k": 1},
    {"type": "offset", "a": "Omar", "b": "Ben", "k": 1}
  ]
}
'''
```
</details>

### 48. L2-01 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Tomas, Lucia)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Tomas": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4], "Ben": [1, 2, 3, 4],
                "blue": [1, 2, 3, 4], "black": [1, 2, 3, 4], "white": [1, 2, 3, 4], "orange": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Tomas", "Ana", "Lucia", "Ben"]},
  {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
  {"type": "eq", "a": "Ana", "b": "blue"},
  {"type": "offset", "a": "Tomas", "b": "orange", "k": 1},
  {"type": "eq", "a": "Tomas", "b": "Lucia"},
  {"type": "neq", "a": "Lucia", "b": "white"},
  {"type": "next_to", "a": "Ana", "b": "Lucia"}
 ]}
```
</details>

### 49. L2-02 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Kai, white)`
- **Restricciones invertidas:** `offset(Kai, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Ana": [1, 2, 3, 4], "Raul": [1, 2, 3, 4], "Kai": [1, 2, 3, 4], "Dev": [1, 2, 3, 4],
                "white": [1, 2, 3, 4], "green": [1, 2, 3, 4], "purple": [1, 2, 3, 4], "red": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Ana", "Raul", "Kai", "Dev"]},
  {"type": "alldiff", "vars": ["white", "green", "purple", "red"]},
  {"type": "eq", "a": "Kai", "b": "white"},
  {"type": "eq", "a": "white", "b": 3},
  {"type": "lt", "a": "Dev", "b": 3},
  {"type": "next_to", "a": "green", "b": "red"},
  {"type": "next_to", "a": "Ana", "b": "white"},
  {"type": "offset", "a": "Kai", "b": "white", "k": 1}
 ]}
```
</details>

### 50. L2-03 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Hugo, white, k=1)`; `lt(Hugo, 4)`; `eq(Jon, 1)`; `offset(Dev, red, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Dev": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Jon": [1, 2, 3, 4],
                "white": [1, 2, 3, 4], "black": [1, 2, 3, 4], "yellow": [1, 2, 3, 4], "red": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Dev", "Sara", "Hugo", "Jon"]},
  {"type": "alldiff", "vars": ["white", "black", "yellow", "red"]},
  {"type": "eq", "a": "Sara", "b": "black"},
  {"type": "offset", "a": "Hugo", "b": "white", "k": 1},
  {"type": "neq", "a": "Hugo", "b": 3},
  {"type": "lt", "a": "Hugo", "b": 4},
  {"type": "lt", "a": "Sara", "b": 4},
  {"type": "eq", "a": "Jon", "b": 1},
  {"type": "offset", "a": "Dev", "b": "red", "k": 1}
 ]}
  
Note: The constraint for Hugo's position relative to the white house was not specified in the original puzzle. I've assumed it is meant to be immediate next to it for simplicity, as this aligns with the example provided. Adjustments may be needed based on the specific intent of the puzzle.
```
</details>

### 51. L2-04 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(white, Gina)`; `eq(Raul, blue)`; `eq(black, orange)`
- **Restricciones invertidas:** `offset(Raul, Gina, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Gina": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4],
                "blue": [1, 2, 3, 4], "black": [1, 2, 3, 4], "white": [1, 2, 3, 4], "orange": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Raul", "Ana", "Gina", "Lucia"]},
  {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
  {"type": "eq", "a": "white", "b": "Gina"},
  {"type": "offset", "a": "Raul", "b": "Gina", "k": 1},
  {"type": "eq", "a": "Raul", "b": "blue"},
  {"type": "eq", "a": "black", "b": "orange"},
  {"type": "eq", "a": "Lucia", "b": "orange"}
 ]}
```
</details>

### 52. L2-06 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(purple, red)`
- **Restricciones invertidas:** `offset(Carla, Ben, k=1)`; `offset(black, red, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Sara": [1, 2, 3, 4], "Mateo": [1, 2, 3, 4], "Carla": [1, 2, 3, 4], "Ben": [1, 2, 3, 4],
                "black": [1, 2, 3, 4], "purple": [1, 2, 3, 4], "white": [1, 2, 3, 4], "red": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Sara", "Mateo", "Carla", "Ben"]},
  {"type": "alldiff", "vars": ["black", "purple", "white", "red"]},
  {"type": "offset", "a": "Carla", "b": "Ben", "k": 1},
  {"type": "eq", "a": "purple", "b": "red"},
  {"type": "offset", "a": "black", "b": "red", "k": 1},
  {"type": "next_to", "a": "Sara", "b": "Ben"},
  {"type": "next_to", "a": "Sara", "b": "black"}
 ]}
```
</details>

### 53. L3-01 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, yellow, k=1)`; `eq(green, white)`
- **Restricciones invertidas:** `offset(Omar, Hugo, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Jon": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Jon", "Omar", "Elena", "Lucia", "Hugo"]},
    {"type": "alldiff", "vars": ["white", "green", "black", "orange", "yellow"]},
    {"type": "eq", "a": "Elena", "b": "white"},
    {"type": "offset", "a": "Omar", "b": "yellow", "k": 1},
    {"type": "eq", "a": "green", "b": "white"},
    {"type": "eq", "a": "Omar", "b": "yellow"},
    {"type": "neq", "a": "orange", "b": "yellow"},
    {"type": "next_to", "a": "Hugo", "b": "Lucia"},
    {"type": "offset", "a": "Omar", "b": "Hugo", "k": 1}
  ]
}
```
</details>

### 54. L3-03 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, Ben)`; `offset(Omar, Iris, k=1)`; `eq(Sara, green)`
- **Restricciones invertidas:** `offset(white, Omar, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Sara": [1, 2, 3, 4, 5], "Omar": [1, 2, 3, 4, 5], "Hugo": [1, 2, 3, 4, 5], "Iris": [1, 2, 3, 4, 5], "Ben": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Sara", "Omar", "Hugo", "Iris", "Ben"]},
  {"type": "alldiff", "vars": ["red", "green", "orange", "purple", "white"]},
  {"type": "eq", "a": "Hugo", "b": "Ben"},
  {"type": "offset", "a": "Ben", "b": "purple", "k": 1},
  {"type": "offset", "a": "white", "b": "Omar", "k": 1},
  {"type": "offset", "a": "Omar", "b": "Iris", "k": 1},
  {"type": "eq", "a": "Sara", "b": "green"},
  {"type": "next_to", "a": "Ben", "b": "green"},
  {"type": "neq", "a": "orange", "b": 5}
 ]}
  
Note: The last constraint "orange": "neq": 5 is corrected to "orange": "neq": 5 to ensure that the orange house is not house 5.
```
</details>

### 55. L3-10 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Sara, black)`; `neq(Raul, 2)`; `eq(Raul, 3)`; `eq(Lucia, black)`; `offset(Tomas, green, k=1)`
- **Restricciones invertidas:** `offset(Raul, yellow, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Lucia", "Tomas", "Raul", "Ben"]},
    {"type": "alldiff", "vars": ["green", "yellow", "orange", "black", "white"]},
    {"type": "eq", "a": "Sara", "b": "black"},
    {"type": "offset", "a": "Raul", "b": "yellow", "k": 1},
    {"type": "neq", "a": "Raul", "b": 2},
    {"type": "eq", "a": "Raul", "b": 3},
    {"type": "offset", "a": "Ben", "b": "Lucia", "k": 1},
    {"type": "alldiff", "vars": ["orange", "Lucia"]},
    {"type": "eq", "a": "Lucia", "b": "black"},
    {"type": "offset", "a": "Tomas", "b": "green", "k": 1}
  ]
}
```
</details>

### 56. L4-02 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `next_to(green, yellow)`; `next_to(rabbit, dog)`
- **Restricciones invertidas:** `offset(black, Carla, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Nora": [1, 2, 3, 4, 5], "Omar": [1, 2, 3, 4, 5], "Carla": [1, 2, 3, 4, 5], "Ana": [1, 2, 3, 4, 5], "Hugo": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "cat": [1, 2, 3, 4, 5], "rabbit": [1, 2, 3, 4, 5], "fish": [1, 2, 3, 4, 5], "dog": [1, 2, 3, 4, 5], "horse": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Nora", "Omar", "Carla", "Ana", "Hugo"]},
  {"type": "alldiff", "vars": ["red", "purple", "black", "green", "yellow"]},
  {"type": "alldiff", "vars": ["cat", "rabbit", "fish", "dog", "horse"]},
  {"type": "eq", "a": "Carla", "b": "red"},
  {"type": "eq", "a": "Carla", "b": "cat"},
  {"type": "offset", "a": "black", "b": "Carla", "k": 1},
  {"type": "alldiff", "vars": ["purple", "cat"]},
  {"type": "next_to", "a": "purple", "b": "cat"},
  {"type": "neq", "a": "Carla", "b": 1},
  {"type": "alldiff", "vars": ["green", "yellow"]},
  {"type": "next_to", "a": "green", "b": "yellow"},
  {"type": "next_to", "a": "rabbit", "b": "dog"},
  {"type": "alldiff", "vars": ["Ana", "fish"]},
  {"type": "next_to", "a": "Ana", "b": "fish"},
  {"type": "alldiff", "vars": ["red", "rabbit"]},
  {"type": "next_to", "a": "red", "b": "rabbit"},
  {"type": "alldiff", "vars": ["Omar", "Hugo"]},
  {"type": "next_to", "a": "Hugo", "b": "Omar"}
 ]
}
```
</details>

### 57. L4-04 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(yellow, hamster)`; `eq(Lucia, Vera)`; `eq(Lucia, yellow)`; `next_to(fish, black)`
- **Restricciones invertidas:** `offset(red, turtle, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Paula": [1, 2, 3, 4, 5], "Lucia": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Raul": [1, 2, 3, 4, 5], "Ben": [1, 2, 3, 4, 5],
               "orange": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5],
               "bird": [1, 2, 3, 4, 5], "dog": [1, 2, 3, 4, 5], "hamster": [1, 2, 3, 4, 5], "turtle": [1, 2, 3, 4, 5], "fish": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Paula", "Lucia", "Vera", "Raul", "Ben"]},
  {"type": "alldiff", "vars": ["orange", "red", "yellow", "purple", "black"]},
  {"type": "alldiff", "vars": ["bird", "dog", "hamster", "turtle", "fish"]},
  {"type": "eq", "a": "yellow", "b": "hamster"},
  {"type": "offset", "a": "red", "b": "turtle", "k": 1},
  {"type": "eq", "a": "Lucia", "b": "Vera"},
  {"type": "next_to", "a": "Lucia", "b": "turtle"},
  {"type": "eq", "a": "Lucia", "b": "yellow"},
  {"type": "neq", "a": "Ben", "b": "purple"},
  {"type": "next_to", "a": "Ben", "b": "Lucia"},
  {"type": "neq", "a": "Raul", "b": "black"},
  {"type": "next_to", "a": "fish", "b": "black"},
  {"type": "next_to", "a": "purple", "b": "Ben"}
 ]}
```
</details>

### 58. L4-07 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(turtle, orange)`; `offset(Felix, orange, k=1)`; `eq(Felix, Mateo)`; `neq(Vera, 1)`; `eq(Felix, Iris)`; `eq(red, yellow)`; `eq(Iris, bird)`; `eq(blue, yellow)`; `eq(Iris, turtle)`
- **Restricciones invertidas:** `lt(Elena, turtle)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Felix": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Felix", "Iris", "Elena", "Vera", "Mateo"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "white", "blue"]},
    {"type": "alldiff", "vars": ["fish", "turtle", "bird", "horse", "cat"]},
    {"type": "eq", "a": "turtle", "b": "orange", "c": "Felix"},
    {"type": "offset", "a": "Felix", "b": "orange", "k": 1},
    {"type": "eq", "a": "Felix", "b": "Mateo"},
    {"type": "neq", "a": "Vera", "b": 1},
    {"type": "eq", "a": "Felix", "b": "Iris"},
    {"type": "neq", "a": "Iris", "b": 1},
    {"type": "lt", "a": "Elena", "b": "turtle"},
    {"type": "eq", "a": "red", "b": "yellow", "k": 1},
    {"type": "eq", "a": "Iris", "b": "bird"},
    {"type": "neq", "a": "Iris", "b": 1},
    {"type": "lt", "a": "cat", "b": "turtle"},
    {"type": "eq", "a": "blue", "b": "yellow", "k": 1},
    {"type": "eq", "a": "Iris", "b": "turtle"},
    {"type": "neq", "a": "Iris", "b": 1}
  ]
}
'''
```
</details>

### 59. L4-09 · rep 1 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `next_to(Ana, fish)`; `neq(purple, 1)`; `lt(purple, 1)`; `offset(purple, hamster, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Omar": [1, 2, 3, 4, 5], "Ana": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5], "Jon": [1, 2, 3, 4, 5], "Carla": [1, 2, 3, 4, 5],
                "orange": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5],
                "fish": [1, 2, 3, 4, 5], "hamster": [1, 2, 3, 4, 5], "dog": [1, 2, 3, 4, 5], "horse": [1, 2, 3, 4, 5], "turtle": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Omar", "Ana", "Tomas", "Jon", "Carla"]},
  {"type": "alldiff", "vars": ["orange", "green", "blue", "purple", "red"]},
  {"type": "alldiff", "vars": ["fish", "hamster", "dog", "horse", "turtle"]},
  {"type": "neq", "a": "Jon", "b": "turtle"},
  {"type": "next_to", "a": "red", "b": "dog"},
  {"type": "neq", "a": "Tomas", "b": 1},
  {"type": "next_to", "a": "Omar", "b": "Ana"},
  {"type": "next_to", "a": "Omar", "b": "blue"},
  {"type": "next_to", "a": "Ana", "b": "fish"},
  {"type": "lt", "a": "Jon", "b": "Ana"},
  {"type": "lt", "a": "Ana", "b": "fish"},
  {"type": "next_to", "a": "Omar", "b": "dog"},
  {"type": "neq", "a": "purple", "b": 1},
  {"type": "lt", "a": "Ana", "b": "Omar"},
  {"type": "next_to", "a": "blue", "b": "hamster"},
  {"type": "lt", "a": "dog", "b": "Carla"},
  {"type": "lt", "a": "purple", "b": 1},
  {"type": "offset", "a": "purple", "b": "hamster", "k": 1}
 ]}
```
</details>

### 60. L1-06 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, Hugo, k=1)`
- **Restricciones invertidas:** `offset(Lucia, Hugo, k=1)`; `offset(Omar, Ben, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Lucia": [1, 2, 3, 4], "Ben": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Omar": [1, 2, 3, 4]},
 "constraints": [
  {"type": "offset", "a": "Lucia", "b": "Hugo", "k": 1},
  {"type": "offset", "a": "Omar", "b": "Hugo", "k": 1},
  {"type": "offset", "a": "Omar", "b": "Ben", "k": 1},
  {"type": "alldiff", "vars": ["Lucia", "Ben", "Hugo", "Omar"]}
 ]}
```
</details>

### 61. L2-01 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Tomas, Lucia)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Tomas": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4], "Ben": [1, 2, 3, 4],
                "blue": [1, 2, 3, 4], "black": [1, 2, 3, 4], "white": [1, 2, 3, 4], "orange": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Tomas", "Ana", "Lucia", "Ben"]},
  {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
  {"type": "eq", "a": "Ana", "b": "blue"},
  {"type": "offset", "a": "Tomas", "b": "orange", "k": 1},
  {"type": "eq", "a": "Tomas", "b": "Lucia"},
  {"type": "neq", "a": "Lucia", "b": 4},
  {"type": "next_to", "a": "Ana", "b": "Lucia"}
 ]}
```
</details>

### 62. L2-02 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Kai, white)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Ana": [1, 2, 3, 4],
    "Raul": [1, 2, 3, 4],
    "Kai": [1, 2, 3, 4],
    "Dev": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Ana", "Raul", "Kai", "Dev"]},
    {"type": "alldiff", "vars": ["white", "green", "purple", "red"]},
    {"type": "eq", "a": "Kai", "b": "white"},
    {"type": "eq", "a": "white", "b": 3},
    {"type": "lt", "a": "Dev", "b": 3},
    {"type": "next_to", "a": "green", "b": "red"},
    {"type": "next_to", "a": "Ana", "b": "white"},
    {"type": "offset", "a": "Kai", "b": "white", "k": -1}
  ]
}
```
</details>

### 63. L2-03 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Hugo, white, k=1)`
- **Restricciones invertidas:** `lt(Jon, 1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Dev": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4],
    "Jon": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Dev", "Sara", "Hugo", "Jon"]},
    {"type": "alldiff", "vars": ["white", "black", "yellow", "red"]},
    {"type": "eq", "a": "Sara", "b": "black"},
    {"type": "offset", "a": "Hugo", "b": "white", "k": 1},
    {"type": "neq", "a": "Hugo", "b": 3},
    {"type": "lt", "a": "Jon", "b": 1},
    {"type": "next_to", "a": "Sara", "b": "Hugo"}
  ]
}
```
</details>

### 64. L2-04 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Gina, white)`
- **Restricciones invertidas:** `offset(Raul, Gina, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4],
    "Ana": [1, 2, 3, 4],
    "Gina": [1, 2, 3, 4],
    "Lucia": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Ana", "Gina", "Lucia"]},
    {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
    {"type": "eq", "a": "Gina", "b": "white"},
    {"type": "offset", "a": "Raul", "b": "Gina", "k": 1},
    {"type": "next_to", "a": "Raul", "b": "blue"},
    {"type": "next_to", "a": "Raul", "b": "orange"},
    {"type": "next_to", "a": "black", "b": "orange"},
    {"type": "eq", "a": "Lucia", "b": "orange"},
    {"type": "next_to", "a": "Raul", "b": "orange"}
  ]
}
```
</details>

### 65. L2-06 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(purple, red)`
- **Restricciones invertidas:** `offset(Carla, Ben, k=1)`; `offset(black, red, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4],
    "Mateo": [1, 2, 3, 4],
    "Carla": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Mateo", "Carla", "Ben"]},
    {"type": "alldiff", "vars": ["black", "purple", "white", "red"]},
    {"type": "offset", "a": "Carla", "b": "Ben", "k": 1},
    {"type": "eq", "a": "purple", "b": "red"},
    {"type": "offset", "a": "black", "b": "red", "k": 1},
    {"type": "next_to", "a": "Sara", "b": "Ben"},
    {"type": "next_to", "a": "Sara", "b": "black"}
  ]
}
```
</details>

### 66. L2-08 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Sara, red, k=1)`; `offset(Mateo, red, k=-1)`
- **Restricciones invertidas:** `offset(black, yellow, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Mateo": [1, 2, 3, 4],
    "Dev": [1, 2, 3, 4],
    "red": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Sara", "Mateo", "Dev"]},
    {"type": "alldiff", "vars": ["red", "orange", "black", "yellow"]},
    {"type": "eq", "a": "Elena", "b": "yellow"},
    {"type": "offset", "a": "Sara", "b": "red", "k": 1},
    {"type": "offset", "a": "Mateo", "b": "red", "k": -1},
    {"type": "offset", "a": "black", "b": "yellow", "k": 1},
    {"type": "next_to", "a": "Elena", "b": "Dev"},
    {"type": "neq", "a": "Dev", "b": 1},
    {"type": "eq", "a": "Dev", "b": 4}
  ]
}
```
</details>

### 67. L2-10 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones invertidas:** `offset(purple, yellow, k=1)`; `offset(Hugo, blue, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4],
    "Paula": [1, 2, 3, 4],
    "Omar": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Paula", "Omar", "Hugo"]},
    {"type": "alldiff", "vars": ["purple", "yellow", "green", "blue"]},
    {"type": "eq", "a": "Elena", "b": "green"},
    {"type": "offset", "a": "Elena", "b": "Omar", "k": 1},
    {"type": "offset", "a": "purple", "b": "yellow", "k": 1},
    {"type": "neq", "a": "green", "b": 1},
    {"type": "lt", "a": "purple", "b": "Hugo"},
    {"type": "offset", "a": "Hugo", "b": "blue", "k": 1}
  ]
}
```
</details>

### 68. L3-01 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(green, white)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Jon": [1, 2, 3, 4, 5], "Omar": [1, 2, 3, 4, 5], "Elena": [1, 2, 3, 4, 5],
                "Lucia": [1, 2, 3, 4, 5], "Hugo": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5],
                "green": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5],
                "yellow": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Jon", "Omar", "Elena", "Lucia", "Hugo"]},
  {"type": "alldiff", "vars": ["white", "green", "black", "orange", "yellow"]},
  {"type": "eq", "a": "Elena", "b": "white"},
  {"type": "next_to", "a": "Omar", "b": "Hugo"},
  {"type": "eq", "a": "green", "b": "white"},
  {"type": "eq", "a": "Omar", "b": "yellow"},
  {"type": "next_to", "a": "orange", "b": "yellow"},
  {"type": "next_to", "a": "Hugo", "b": "Lucia"}
 ]}
  
This JSON object represents the given puzzle with the specified constraints.
```
</details>

### 69. L3-02 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Mateo, orange)`; `next_to(red, Ana)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Gina": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Gina", "Mateo", "Ana", "Ben", "Tomas"]},
    {"type": "alldiff", "vars": ["purple", "black", "red", "orange", "blue"]},
    {"type": "eq", "a": "Mateo", "b": "orange"},
    {"type": "next_to", "a": "Mateo", "b": "orange"},
    {"type": "next_to", "a": "red", "b": "Ana"},
    {"type": "neq", "a": "Gina", "b": "Ana"},
    {"type": "next_to", "a": "Gina", "b": "Ana"},
    {"type": "next_to", "a": "black", "b": "red"},
    {"type": "next_to", "a": "black", "b": "Tomas"},
    {"type": "next_to", "a": "blue", "b": "purple"}
  ]
}
```
</details>

### 70. L3-03 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, Ben)`; `offset(Omar, Iris, k=1)`; `eq(green, Sara)`
- **Restricciones invertidas:** `offset(white, Omar, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Omar", "Hugo", "Iris", "Ben"]},
    {"type": "alldiff", "vars": ["red", "green", "orange", "purple", "white"]},
    {"type": "eq", "a": "Hugo", "b": "Ben"},
    {"type": "offset", "a": "Ben", "b": "purple", "k": 1},
    {"type": "offset", "a": "white", "b": "Omar", "k": 1},
    {"type": "offset", "a": "Omar", "b": "Iris", "k": 1},
    {"type": "eq", "a": "green", "b": "Sara"},
    {"type": "next_to", "a": "Ben", "b": "green"},
    {"type": "neq", "a": "orange", "b": 5}
  ]
}
```
</details>

### 71. L3-05 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Paula, blue)`; `offset(Kai, black, k=1)`; `eq(Mateo, black)`; `next_to(red, black)`; `next_to(Kai, Ben)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Ben": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Ben", "Mateo", "Kai", "Paula", "Gina"]},
    {"type": "alldiff", "vars": ["blue", "purple", "black", "red", "green"]},
    {"type": "eq", "a": "Paula", "b": "blue"},
    {"type": "offset", "a": "Kai", "b": "black", "k": 1},
    {"type": "eq", "a": "Mateo", "b": "black"},
    {"type": "offset", "a": "Ben", "b": "blue", "k": 1},
    {"type": "neq", "a": "Paula", "b": 2},
    {"type": "next_to", "a": "red", "b": "black"},
    {"type": "next_to", "a": "Kai", "b": "Ben"}
  ]
}
```
</details>

### 72. L3-07 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Nora, red)`; `next_to(yellow, Nora)`; `next_to(green, Paula)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Lucia": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "Nora": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Lucia", "Mateo", "Nora", "Paula", "Raul"]},
    {"type": "alldiff", "vars": ["yellow", "orange", "red", "green", "purple"]},
    {"type": "eq", "a": "Nora", "b": "red"},
    {"type": "eq", "a": "red", "b": 5},
    {"type": "next_to", "a": "yellow", "b": "Nora"},
    {"type": "next_to", "a": "Nora", "b": "Lucia"},
    {"type": "next_to", "a": "green", "b": "Paula"},
    {"type": "next_to", "a": "green", "b": "Mateo"},
    {"type": "next_to", "a": "Mateo", "b": "orange"}
  ]
}
```
</details>

### 73. L3-08 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `lt(Felix, 3)`
- **Restricciones invertidas:** `offset(white, blue, k=1)`; `lt(Ana, 3)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Iris": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Felix": [1, 2, 3, 4, 5],
    "Nora": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Iris", "Paula", "Felix", "Ana", "Nora"]},
    {"type": "alldiff", "vars": ["blue", "red", "white", "green", "orange"]},
    {"type": "eq", "a": "Iris", "b": "white"},
    {"type": "offset", "a": "Paula", "b": "Felix", "k": 1},
    {"type": "next_to", "a": "Ana", "b": "green"},
    {"type": "offset", "a": "white", "b": "blue", "k": 1},
    {"type": "neq", "a": "Ana", "b": 1},
    {"type": "lt", "a": "Ana", "b": 3},
    {"type": "lt", "a": "Felix", "b": 3},
    {"type": "neq", "a": "blue", "b": 2}
  ]
}
```
</details>

### 74. L3-10 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Sara, black)`; `neq(Raul, 2)`; `eq(Raul, 3)`; `offset(Tomas, green, k=1)`; `eq(Lucia, black)`; `offset(Ben, black, k=1)`; `offset(Raul, orange, k=1)`
- **Restricciones invertidas:** `offset(Raul, yellow, k=1)`; `offset(Lucia, Ben, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Lucia", "Tomas", "Raul", "Ben"]},
    {"type": "alldiff", "vars": ["green", "yellow", "orange", "black", "white"]},
    {"type": "eq", "a": "Sara", "b": "black"},
    {"type": "offset", "a": "Raul", "b": "yellow", "k": 1},
    {"type": "neq", "a": "Raul", "b": 2},
    {"type": "eq", "a": "Raul", "b": 3},
    {"type": "alldiff", "vars": ["Tomas", "green"]},
    {"type": "offset", "a": "Tomas", "b": "green", "k": 1},
    {"type": "alldiff", "vars": ["Lucia", "Ben"]},
    {"type": "offset", "a": "Lucia", "b": "Ben", "k": 1},
    {"type": "eq", "a": "Lucia", "b": "black"},
    {"type": "offset", "a": "Ben", "b": "black", "k": 1},
    {"type": "eq", "a": "orange", "b": "Raul"},
    {"type": "offset", "a": "Raul", "b": "orange", "k": 1},
    {"type": "alldiff", "vars": ["Raul", "yellow"]}
  ]
}
```
</details>

### 75. L4-01 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(vera, hamster, k=1)`; `eq(vera, blue)`; `eq(Gina, black)`; `eq(Gina, Paula)`; `next_to(Paula, hamster)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Nora": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "vera": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Elena", "vera", "Gina", "Paula"]},
    {"type": "alldiff", "vars": ["purple", "black", "orange", "yellow", "blue"]},
    {"type": "alldiff", "vars": ["horse", "rabbit", "bird", "hamster", "fish"]},
    {"type": "eq", "a": "Nora", "b": "orange"},
    {"type": "offset", "a": "vera", "b": "hamster", "k": 1},
    {"type": "eq", "a": "horse", "b": "blue"},
    {"type": "offset", "a": "Elena", "b": "bird", "k": 1},
    {"type": "eq", "a": "vera", "b": "blue"},
    {"type": "eq", "a": "Gina", "b": "black"},
    {"type": "eq", "a": "Gina", "b": "Paula"},
    {"type": "eq", "a": "Nora", "b": 5},
    {"type": "next_to", "a": "Paula", "b": "hamster"}
  ]
}
```
</details>

### 76. L4-04 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(orange, yellow)`; `offset(red, fish, k=1)`; `eq(red, turtle)`; `eq(Lucia, yellow)`
- **Restricciones invertidas:** `offset(Lucia, Vera, k=1)`; `offset(Ben, Lucia, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Paula": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Lucia", "Vera", "Raul", "Ben"]},
    {"type": "alldiff", "vars": ["orange", "red", "yellow", "purple", "black"]},
    {"type": "alldiff", "vars": ["bird", "dog", "hamster", "turtle", "fish"]},
    {"type": "eq", "a": "orange", "b": "yellow"},
    {"type": "offset", "a": "red", "b": "fish", "k": 1},
    {"type": "eq", "a": "red", "b": "turtle"},
    {"type": "offset", "a": "Lucia", "b": "Vera", "k": 1},
    {"type": "neq", "a": "Lucia", "b": "turtle"},
    {"type": "eq", "a": "Lucia", "b": "yellow"},
    {"type": "neq", "a": "Ben", "b": "purple"},
    {"type": "offset", "a": "Ben", "b": "Lucia", "k": 1},
    {"type": "neq", "a": "Raul", "b": "black"},
    {"type": "lt", "a": "fish", "b": "black"},
    {"type": "lt", "a": "purple", "b": "Ben"}
  ]
}
```
</details>

### 77. L4-07 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(turtle, orange)`; `eq(Felix, Iris)`; `neq(Vera, 1)`; `eq(Felix, Iris)`; `eq(Iris, bird)`; `eq(red, yellow)`; `eq(Iris, bird)`; `eq(cat, turtle)`; `eq(blue, yellow)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Felix": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Felix", "Iris", "Elena", "Vera", "Mateo"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "white", "blue"]},
    {"type": "alldiff", "vars": ["fish", "turtle", "bird", "horse", "cat"]},
    {"type": "eq", "a": "turtle", "b": "orange", "k": 1},
    {"type": "eq", "a": "Felix", "b": "Iris"},
    {"type": "neq", "a": "Vera", "b": 1},
    {"type": "eq", "a": "Felix", "b": "Iris"},
    {"type": "eq", "a": "Iris", "b": "bird"},
    {"type": "eq", "a": "red", "b": "yellow"},
    {"type": "eq", "a": "Iris", "b": "bird"},
    {"type": "eq", "a": "cat", "b": "turtle"},
    {"type": "eq", "a": "blue", "b": "yellow"}
  ]
}
```
</details>

### 78. L4-08 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(dog, yellow, k=1)`; `eq(white, black)`
- **Restricciones invertidas:** `offset(turtle, Kai, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Dev", "Iris", "Kai", "Tomas"]},
    {"type": "alldiff", "vars": ["red", "black", "yellow", "orange", "white"]},
    {"type": "alldiff", "vars": ["turtle", "dog", "cat", "rabbit", "hamster"]},
    {"type": "eq", "a": "Dev", "b": "hamster"},
    {"type": "offset", "a": "dog", "b": "yellow", "k": 1},
    {"type": "neq", "a": "Iris", "b": 4},
    {"type": "offset", "a": "turtle", "b": "Kai", "k": 1},
    {"type": "alldiff", "vars": ["Raul", "Iris"]},
    {"type": "next_to", "a": "Tomas", "b": "Iris"},
    {"type": "eq", "a": "white", "b": "black"},
    {"type": "eq", "a": "Raul", "b": "red"}
  ]
}
```
</details>

### 79. L4-10 · rep 2 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Elena, turtle)`; `offset(Iris, fish, k=1)`; `next_to(horse, yellow)`; `next_to(turtle, yellow)`
- **Restricciones invertidas:** `offset(orange, purple, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Iris", "Raul", "Jon", "Ana"]},
    {"type": "alldiff", "vars": ["orange", "purple", "yellow", "blue", "black"]},
    {"type": "alldiff", "vars": ["bird", "turtle", "rabbit", "fish", "horse"]},
    {"type": "eq", "a": "Elena", "b": "turtle"},
    {"type": "offset", "a": "Iris", "b": "fish", "k": 1},
    {"type": "next_to", "a": "black", "b": "turtle"},
    {"type": "next_to", "a": "horse", "b": "yellow"},
    {"type": "eq", "a": "rabbit", "b": "purple"},
    {"type": "next_to", "a": "Iris", "b": "Elena"},
    {"type": "neq", "a": "Raul", "b": 3},
    {"type": "next_to", "a": "turtle", "b": "yellow"},
    {"type": "next_to", "a": "Raul", "b": "purple"},
    {"type": "offset", "a": "orange", "b": "purple", "k": 1},
    {"type": "next_to", "a": "orange", "b": "Ana"}
  ]
}
```
</details>

### 80. L1-06 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, Hugo, k=1)`
- **Restricciones invertidas:** `offset(Lucia, Hugo, k=1)`; `offset(Omar, Ben, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Lucia": [1, 2, 3, 4], "Ben": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Omar": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Lucia", "Hugo", "Ben", "Omar"]},
  {"type": "offset", "a": "Lucia", "b": "Hugo", "k": 1},
  {"type": "offset", "a": "Omar", "b": "Hugo", "k": 1},
  {"type": "offset", "a": "Omar", "b": "Ben", "k": 1}
 ]}
```
</details>

### 81. L2-01 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Tomas, Lucia)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Tomas": [1, 2, 3, 4],
    "Ana": [1, 2, 3, 4],
    "Lucia": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Tomas", "Ana", "Lucia", "Ben"]},
    {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
    {"type": "eq", "a": "Ana", "b": "blue"},
    {"type": "offset", "a": "Tomas", "b": "orange", "k": 1},
    {"type": "alldiff", "vars": ["Lucia", "Tomas"]},
    {"type": "eq", "a": "Tomas", "b": "Lucia"},
    {"type": "neq", "a": "Lucia", "b": 4},
    {"type": "next_to", "a": "Ana", "b": "Lucia"}
  ]
}
```
</details>

### 82. L2-04 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(white, Gina)`
- **Restricciones invertidas:** `offset(Raul, Gina, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4],
    "Ana": [1, 2, 3, 4],
    "Gina": [1, 2, 3, 4],
    "Lucia": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Ana", "Gina", "Lucia"]},
    {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
    {"type": "eq", "a": "white", "b": "Gina"},
    {"type": "offset", "a": "Raul", "b": "Gina", "k": 1},
    {"type": "next_to", "a": "Raul", "b": "blue"},
    {"type": "next_to", "a": "Raul", "b": "orange"},
    {"type": "next_to", "a": "black", "b": "orange"},
    {"type": "eq", "a": "Lucia", "b": "orange"}
  ]
}
```
</details>

### 83. L2-05 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `neq(Ana, 2)`; `offset(purple, yellow, k=1)`
- **Restricciones invertidas:** `offset(Omar, Carla, k=1)`; `offset(Ana, orange, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Omar": [1, 2, 3, 4],
    "Ana": [1, 2, 3, 4],
    "Carla": [1, 2, 3, 4],
    "Paula": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Omar", "Ana", "Carla", "Paula"]},
    {"type": "alldiff", "vars": ["yellow", "purple", "black", "orange"]},
    {"type": "eq", "a": "Omar", "b": 3},
    {"type": "neq", "a": "Paula", "b": 2},
    {"type": "neq", "a": "Ana", "b": 3},
    {"type": "offset", "a": "Ana", "b": "purple", "k": 1},
    {"type": "neq", "a": "Ana", "b": 2},
    {"type": "offset", "a": "purple", "b": "yellow", "k": 1},
    {"type": "neq", "a": "yellow", "b": 2},
    {"type": "neq", "a": "Omar", "b": 2},
    {"type": "offset", "a": "Omar", "b": "Carla", "k": 1},
    {"type": "neq", "a": "Ana", "b": 4},
    {"type": "offset", "a": "Ana", "b": "orange", "k": 1}
  ]
}
```
</details>

### 84. L2-06 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(purple, red)`
- **Restricciones invertidas:** `offset(Carla, Ben, k=1)`; `offset(black, red, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4],
    "Mateo": [1, 2, 3, 4],
    "Carla": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Mateo", "Carla", "Ben"]},
    {"type": "alldiff", "vars": ["black", "purple", "white", "red"]},
    {"type": "offset", "a": "Carla", "b": "Ben", "k": 1},
    {"type": "eq", "a": "purple", "b": "red"},
    {"type": "offset", "a": "black", "b": "red", "k": 1},
    {"type": "next_to", "a": "Sara", "b": "Ben"},
    {"type": "next_to", "a": "Sara", "b": "black"}
  ]
}
```
</details>

### 85. L3-01 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, yellow, k=1)`; `eq(green, white)`
- **Restricciones invertidas:** `offset(Omar, Hugo, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Jon": [1, 2, 3, 4, 5], "Omar": [1, 2, 3, 4, 5], "Elena": [1, 2, 3, 4, 5], "Lucia": [1, 2, 3, 4, 5], "Hugo": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Jon", "Omar", "Elena", "Lucia", "Hugo"]},
  {"type": "alldiff", "vars": ["white", "green", "black", "orange", "yellow"]},
  {"type": "eq", "a": "Elena", "b": "white"},
  {"type": "offset", "a": "Omar", "b": "yellow", "k": 1},
  {"type": "eq", "a": "green", "b": "white"},
  {"type": "eq", "a": "Omar", "b": "yellow"},
  {"type": "neq", "a": "orange", "b": "yellow"},
  {"type": "next_to", "a": "Hugo", "b": "Lucia"},
  {"type": "offset", "a": "Omar", "b": "Hugo", "k": 1}
 ]}
```
</details>

### 86. L3-03 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, Ben)`; `eq(green, Sara)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Omar", "Hugo", "Iris", "Ben"]},
    {"type": "alldiff", "vars": ["red", "green", "orange", "purple", "white"]},
    {"type": "eq", "a": "Hugo", "b": "Ben"},
    {"type": "lt", "a": "purple", "b": "Ben"},
    {"type": "lt", "a": "white", "b": "Omar"},
    {"type": "lt", "a": "Omar", "b": "Iris"},
    {"type": "eq", "a": "green", "b": "Sara"},
    {"type": "next_to", "a": "Ben", "b": "green"},
    {"type": "neq", "a": "orange", "b": 5}
  ]
}
```
</details>

### 87. L4-01 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Vera, hamster, k=1)`; `eq(Vera, blue)`; `eq(Nora, purple)`; `eq(Gina, black)`; `eq(Gina, orange)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Nora": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Elena", "Vera", "Gina", "Paula"]},
    {"type": "alldiff", "vars": ["purple", "black", "orange", "yellow", "blue"]},
    {"type": "alldiff", "vars": ["horse", "rabbit", "bird", "hamster", "fish"]},
    {"type": "eq", "a": "Nora", "b": "orange"},
    {"type": "offset", "a": "Vera", "b": "hamster", "k": 1},
    {"type": "eq", "a": "horse", "b": "blue"},
    {"type": "offset", "a": "Elena", "b": "bird", "k": 1},
    {"type": "eq", "a": "Vera", "b": "blue"},
    {"type": "eq", "a": "Nora", "b": "purple"},
    {"type": "offset", "a": "Paula", "b": "rabbit", "k": 1},
    {"type": "eq", "a": "Gina", "b": "black"},
    {"type": "eq", "a": "Gina", "b": "orange"}
  ]
}
```
</details>

### 88. L4-02 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(green, yellow, k=1)`; `offset(red, cat, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Nora": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Omar", "Carla", "Ana", "Hugo"]},
    {"type": "alldiff", "vars": ["red", "purple", "black", "green", "yellow"]},
    {"type": "alldiff", "vars": ["cat", "rabbit", "fish", "dog", "horse"]},
    {"type": "eq", "a": "Carla", "b": "red"},
    {"type": "eq", "a": "Carla", "b": "cat"},
    {"type": "offset", "a": "purple", "b": "cat", "k": 1},
    {"type": "neq", "a": "Carla", "b": 1},
    {"type": "offset", "a": "green", "b": "yellow", "k": 1},
    {"type": "lt", "a": "rabbit", "b": "dog"},
    {"type": "lt", "a": "Ana", "b": "fish"},
    {"type": "offset", "a": "red", "b": "cat", "k": 1},
    {"type": "lt", "a": "Omar", "b": "cat"},
    {"type": "lt", "a": "Hugo", "b": "Omar"}
  ]
}
```
</details>

### 89. L4-04 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(yellow, hamster)`; `offset(red, fish, k=1)`; `eq(red, turtle)`; `neq(Raul, 1)`
- **Restricciones invertidas:** `offset(Lucia, Vera, k=1)`; `offset(Lucia, yellow, k=1)`; `offset(Ben, Lucia, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Paula": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Lucia", "Vera", "Raul", "Ben"]},
    {"type": "alldiff", "vars": ["orange", "red", "yellow", "purple", "black"]},
    {"type": "alldiff", "vars": ["bird", "dog", "hamster", "turtle", "fish"]},
    {"type": "eq", "a": "yellow", "b": "hamster"},
    {"type": "offset", "a": "red", "b": "fish", "k": 1},
    {"type": "eq", "a": "red", "b": "turtle"},
    {"type": "offset", "a": "Lucia", "b": "Vera", "k": 1},
    {"type": "next_to", "a": "Lucia", "b": "turtle"},
    {"type": "offset", "a": "Lucia", "b": "yellow", "k": 1},
    {"type": "neq", "a": "Ben", "b": 1},
    {"type": "offset", "a": "Ben", "b": "Lucia", "k": 1},
    {"type": "neq", "a": "Raul", "b": 5},
    {"type": "neq", "a": "Raul", "b": 4},
    {"type": "neq", "a": "Raul", "b": 3},
    {"type": "neq", "a": "Raul", "b": 2},
    {"type": "neq", "a": "Raul", "b": 1},
    {"type": "neq", "a": "purple", "b": 2},
    {"type": "neq", "a": "purple", "b": 3},
    {"type": "neq", "a": "purple", "b": 4},
    {"type": "neq", "a": "purple", "b": 5},
    {"type": "next_to", "a": "purple", "b": "Ben"}
  ]
}
```
</details>

### 90. L4-05 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Nombres del enunciado sin variable:** `cat`
- **Restricciones inventadas (la verdad las viola):** `eq(Elena, white)`; `offset(Tomas, blue, k=1)`; `neq(Elena, 1)`; `eq(Dev, red)`; `eq(purple, Hugo)`; `offset(red, Jon, k=1)`
- **Restricciones invertidas:** `offset(orange, blue, k=1)`; `offset(horse, fish, k=1)`; `offset(white, dog, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Hugo": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Hugo", "Tomas", "Dev", "Elena", "Jon"]},
    {"type": "alldiff", "vars": ["red", "white", "orange", "purple", "blue"]},
    {"type": "alldiff", "vars": ["horse", "turtle", "dog", "fish"]},
    {"type": "eq", "a": "Elena", "b": "white"},
    {"type": "offset", "a": "Tomas", "b": "blue", "k": 1},
    {"type": "eq", "a": "Tomas", "b": "blue"},
    {"type": "neq", "a": "Elena", "b": 1},
    {"type": "eq", "a": "Dev", "b": "red"},
    {"type": "offset", "a": "orange", "b": "blue", "k": 1},
    {"type": "eq", "a": "purple", "b": "Hugo"},
    {"type": "offset", "a": "horse", "b": "fish", "k": 1},
    {"type": "neq", "a": "purple", "b": 1},
    {"type": "offset", "a": "white", "b": "dog", "k": 1},
    {"type": "neq", "a": "purple", "b": 5},
    {"type": "offset", "a": "red", "b": "Jon", "k": 1}
  ]
}
```
</details>

### 91. L4-08 · rep 3 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Kai, dog, k=1)`; `eq(Iris, cat)`; `next_to(Raul, Iris)`; `eq(orange, dog)`; `eq(white, black)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Dev", "Iris", "Kai", "Tomas"]},
    {"type": "alldiff", "vars": ["red", "black", "yellow", "orange", "white"]},
    {"type": "alldiff", "vars": ["turtle", "dog", "cat", "rabbit", "hamster"]},
    {"type": "eq", "a": "Dev", "b": "hamster"},
    {"type": "eq", "a": "Raul", "b": "red"},
    {"type": "offset", "a": "Kai", "b": "dog", "k": 1},
    {"type": "eq", "a": "Tomas", "b": "turtle"},
    {"type": "next_to", "a": "Tomas", "b": "Kai"},
    {"type": "eq", "a": "Iris", "b": "cat"},
    {"type": "alldiff", "vars": ["Iris", "Kai"]},
    {"type": "neq", "a": "Iris", "b": 4},
    {"type": "next_to", "a": "Raul", "b": "Iris"},
    {"type": "eq", "a": "orange", "b": "dog"},
    {"type": "eq", "a": "yellow", "b": "dog"},
    {"type": "eq", "a": "white", "b": "black"},
    {"type": "neq", "a": "Iris", "b": 4}
  ]
}
```
</details>

### 92. L1-04 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones invertidas:** `offset(Nora, Dev, k=1)`; `offset(Sara, Raul, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Nora": [1, 2, 3, 4],
    "Dev": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Raul": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Dev", "Sara", "Raul"]},
    {"type": "offset", "a": "Nora", "b": "Dev", "k": 1},
    {"type": "offset", "a": "Raul", "b": "Nora", "k": -1},
    {"type": "offset", "a": "Sara", "b": "Raul", "k": 1}
  ]
}
```
</details>

### 93. L1-06 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, Hugo, k=1)`
- **Restricciones invertidas:** `offset(Lucia, Hugo, k=1)`; `offset(Omar, Ben, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Lucia": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4],
    "Omar": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Lucia", "Hugo", "Omar", "Ben"]},
    {"type": "offset", "a": "Lucia", "b": "Hugo", "k": 1},
    {"type": "offset", "a": "Omar", "b": "Hugo", "k": 1},
    {"type": "offset", "a": "Omar", "b": "Ben", "k": 1}
  ]
}
```
</details>

### 94. L1-10 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Vera, Carla)`
- **Restricciones invertidas:** `offset(Hugo, Carla, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Vera": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
  "constraints": [
    {"type": "alldiff", "vars": ["Vera", "Hugo", "Sara", "Carla"]},
    {"type": "offset", "a": "Hugo", "b": "Sara", "k": 1},
    {"type": "eq", "a": "Vera", "b": "Carla"},
    {"type": "offset", "a": "Hugo", "b": "Carla", "k": 1}
  ]
}
'''
```
</details>

### 95. L2-01 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Tomas, Lucia)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Tomas": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4], "Ben": [1, 2, 3, 4],
                "blue": [1, 2, 3, 4], "black": [1, 2, 3, 4], "white": [1, 2, 3, 4], "orange": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Tomas", "Ana", "Lucia", "Ben"]},
  {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
  {"type": "eq", "a": "Ana", "b": "blue"},
  {"type": "offset", "a": "Tomas", "b": "orange", "k": 1},
  {"type": "eq", "a": "Tomas", "b": "Lucia"},
  {"type": "neq", "a": "Lucia", "b": "white"},
  {"type": "next_to", "a": "Ana", "b": "Lucia"}
 ]}
```
</details>

### 96. L2-04 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(white, Gina)`
- **Restricciones invertidas:** `offset(Raul, Gina, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Gina": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4],
                "blue": [1, 2, 3, 4], "black": [1, 2, 3, 4], "white": [1, 2, 3, 4], "orange": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Raul", "Ana", "Gina", "Lucia"]},
  {"type": "alldiff", "vars": ["blue", "black", "white", "orange"]},
  {"type": "eq", "a": "white", "b": "Gina"},
  {"type": "offset", "a": "Raul", "b": "Gina", "k": 1},
  {"type": "next_to", "a": "Raul", "b": "blue"},
  {"type": "next_to", "a": "black", "b": "orange"},
  {"type": "eq", "a": "Lucia", "b": "orange"},
  {"type": "next_to", "a": "Raul", "b": "orange"}
 ]}
```
</details>

### 97. L2-06 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(purple, red)`
- **Restricciones invertidas:** `offset(Carla, Ben, k=1)`; `offset(black, red, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Sara": [1, 2, 3, 4], "Mateo": [1, 2, 3, 4], "Carla": [1, 2, 3, 4], "Ben": [1, 2, 3, 4],
                "black": [1, 2, 3, 4], "purple": [1, 2, 3, 4], "white": [1, 2, 3, 4], "red": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Sara", "Mateo", "Carla", "Ben"]},
  {"type": "alldiff", "vars": ["black", "purple", "white", "red"]},
  {"type": "offset", "a": "Carla", "b": "Ben", "k": 1},
  {"type": "eq", "a": "purple", "b": "red"},
  {"type": "offset", "a": "black", "b": "red", "k": 1},
  {"type": "next_to", "a": "Sara", "b": "Ben"},
  {"type": "next_to", "a": "Sara", "b": "black"}
 ]}
```
</details>

### 98. L2-10 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones invertidas:** `offset(Hugo, blue, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4],
    "Paula": [1, 2, 3, 4],
    "Omar": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Omar", "Paula", "Hugo"]},
    {"type": "alldiff", "vars": ["purple", "yellow", "green", "blue"]},
    {"type": "eq", "a": "Elena", "b": "green"},
    {"type": "offset", "a": "Hugo", "b": "blue", "k": 1},
    {"type": "next_to", "a": "purple", "b": "yellow"},
    {"type": "next_to", "a": "Elena", "b": "Omar"},
    {"type": "neq", "a": "green", "b": 1},
    {"type": "lt", "a": "purple", "b": "Hugo"}
  ]
}
```
</details>

### 99. L3-01 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, yellow, k=1)`; `eq(green, white)`
- **Restricciones invertidas:** `offset(Hugo, Lucia, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Jon": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Jon", "Omar", "Elena", "Lucia", "Hugo"]},
    {"type": "alldiff", "vars": ["white", "green", "black", "orange", "yellow"]},
    {"type": "eq", "a": "Elena", "b": "white"},
    {"type": "offset", "a": "Omar", "b": "yellow", "k": 1},
    {"type": "eq", "a": "green", "b": "white"},
    {"type": "eq", "a": "Omar", "b": "yellow"},
    {"type": "offset", "a": "Hugo", "b": "Lucia", "k": 1},
    {"type": "neq", "a": "Hugo", "b": 1}
  ]
}
```
</details>

### 100. L3-02 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Mateo, orange)`
- **Restricciones invertidas:** `lt(Ana, red)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Gina": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "Ana": [1, 2, 3, 4, 5],
                "Ben": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5],
                "purple": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5],
                "orange": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Gina", "Mateo", "Ana", "Ben", "Tomas"]},
  {"type": "alldiff", "vars": ["purple", "black", "red", "orange", "blue"]},
  {"type": "eq", "a": "Mateo", "b": "orange"},
  {"type": "next_to", "a": "Mateo", "b": "orange"},
  {"type": "lt", "a": "Ana", "b": "red"},
  {"type": "next_to", "a": "Gina", "b": "Ana"},
  {"type": "next_to", "a": "red", "b": "black"},
  {"type": "next_to", "a": "black", "b": "Tomas"},
  {"type": "next_to", "a": "blue", "b": "purple"}
 ]}
```
</details>

### 101. L3-03 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, Ben)`; `offset(Omar, Iris, k=1)`; `eq(Sara, green)`
- **Restricciones invertidas:** `offset(white, Omar, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Sara": [1, 2, 3, 4, 5], "Omar": [1, 2, 3, 4, 5], "Hugo": [1, 2, 3, 4, 5], "Iris": [1, 2, 3, 4, 5], "Ben": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Sara", "Omar", "Hugo", "Iris", "Ben"]},
  {"type": "alldiff", "vars": ["red", "green", "orange", "purple", "white"]},
  {"type": "eq", "a": "Hugo", "b": "Ben"},
  {"type": "offset", "a": "Ben", "b": "purple", "k": 1},
  {"type": "offset", "a": "white", "b": "Omar", "k": 1},
  {"type": "offset", "a": "Omar", "b": "Iris", "k": 1},
  {"type": "eq", "a": "Sara", "b": "green"},
  {"type": "next_to", "a": "Ben", "b": "green"},
  {"type": "neq", "a": "orange", "b": 5}
 ]}
  
Note: The constraint for Hugo and Ben being next to each other should be a `{"type": "next_to", "a": "Hugo", "b": "Ben", "k": 1}` instead of Hugo's house being immediately to the left of Ben's house as it might not be clear if they are swapped.
```
</details>

### 102. L3-05 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Paula, 2)`; `next_to(Kai, Paula)`; `next_to(red, black)`; `next_to(Kai, Ben)`
- **Restricciones invertidas:** `offset(Mateo, black, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Ben": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "Kai": [1, 2, 3, 4, 5], "Paula": [1, 2, 3, 4, 5], "Gina": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Ben", "Mateo", "Kai", "Paula", "Gina"]},
  {"type": "alldiff", "vars": ["blue", "purple", "black", "red", "green"]},
  {"type": "eq", "a": "Paula", "b": 2},
  {"type": "next_to", "a": "Kai", "b": "Paula"},
  {"type": "next_to", "a": "black", "b": "green"},
  {"type": "offset", "a": "Mateo", "b": "black", "k": 1},
  {"type": "next_to", "a": "Ben", "b": "blue"},
  {"type": "neq", "a": "Paula", "b": 2},
  {"type": "next_to", "a": "red", "b": "black"},
  {"type": "next_to", "a": "Kai", "b": "Ben"},
  {"type": "eq", "a": "Gina", "b": 4}
 ]}
```
</details>

### 103. L4-04 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Lucia, turtle)`; `eq(Lucia, yellow)`; `offset(Raul, fish, k=1)`; `eq(Ben, red)`; `next_to(Lucia, Raul)`; `eq(Lucia, Vera)`; `neq(Raul, 1)`; `eq(Ben, 1)`; `neq(Ben, 2)`; `lt(black, 5)`; `next_to(fish, black)`
- **Restricciones invertidas:** `lt(black, purple)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Paula": [1, 2, 3, 4, 5], "Lucia": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Raul": [1, 2, 3, 4, 5], "Ben": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "bird": [1, 2, 3, 4, 5], "dog": [1, 2, 3, 4, 5], "hamster": [1, 2, 3, 4, 5], "turtle": [1, 2, 3, 4, 5], "fish": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Paula", "Lucia", "Vera", "Raul", "Ben"]},
  {"type": "alldiff", "vars": ["orange", "red", "yellow", "purple", "black"]},
  {"type": "alldiff", "vars": ["bird", "dog", "hamster", "turtle", "fish"]},
  {"type": "eq", "a": "Lucia", "b": "turtle"},
  {"type": "eq", "a": "Lucia", "b": "yellow"},
  {"type": "offset", "a": "Raul", "b": "fish", "k": 1},
  {"type": "eq", "a": "Ben", "b": "red"},
  {"type": "neq", "a": "Ben", "b": 1},
  {"type": "next_to", "a": "Lucia", "b": "Raul"},
  {"type": "eq", "a": "Lucia", "b": "Vera"},
  {"type": "neq", "a": "Raul", "b": 5},
  {"type": "neq", "a": "Raul", "b": 1},
  {"type": "neq", "a": "Raul", "b": 4},
  {"type": "neq", "a": "Raul", "b": 3},
  {"type": "eq", "a": "Ben", "b": 1},
  {"type": "neq", "a": "Ben", "b": 5},
  {"type": "neq", "a": "Ben", "b": 2},
  {"type": "neq", "a": "Ben", "b": 3},
  {"type": "neq", "a": "Ben", "b": 4},
  {"type": "lt", "a": "black", "b": 5},
  {"type": "alldiff", "vars": ["purple", "Ben"]},
  {"type": "lt", "a": "purple", "b": 5},
  {"type": "lt", "a": "black", "b": "purple"},
  {"type": "neq", "a": "Raul", "b": "black"},
  {"type": "neq", "a": "Paula", "b": "purple"},
  {"type": "next_to", "a": "fish", "b": "black"},
  {"type": "lt", "a": "orange", "b": 5},
  {"type": "alldiff", "vars": ["bird", "orange"]}
 ]}
```
</details>

### 104. L4-05 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Nombres del enunciado sin variable:** `cat`
- **Restricciones inventadas (la verdad las viola):** `eq(purple, horse)`; `eq(orange, blue)`; `eq(purple, Hugo)`; `eq(red, Jon)`
- **Restricciones invertidas:** `offset(Elena, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Hugo": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5],
                "Elena": [1, 2, 3, 4, 5], "Jon": [1, 2, 3, 4, 5],
                "red": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5],
                "purple": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5], "horse": [1, 2, 3, 4, 5],
                "turtle": [1, 2, 3, 4, 5], "dog": [1, 2, 3, 4, 5], "fish": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Hugo", "Tomas", "Dev", "Elena", "Jon"]},
  {"type": "alldiff", "vars": ["red", "white", "orange", "purple", "blue"]},
  {"type": "alldiff", "vars": ["horse", "turtle", "dog", "fish"]},
  {"type": "eq", "a": "purple", "b": "horse"},
  {"type": "offset", "a": "Elena", "b": "white", "k": 1},
  {"type": "eq", "a": "Tomas", "b": "blue"},
  {"type": "neq", "a": "Elena", "b": "turtle"},
  {"type": "offset", "a": "Dev", "b": "red", "k": 1},
  {"type": "eq", "a": "orange", "b": "blue"},
  {"type": "eq", "a": "purple", "b": "Hugo"},
  {"type": "next_to", "a": "horse", "b": "fish"},
  {"type": "neq", "a": "fish", "b": "purple"},
  {"type": "next_to", "a": "white", "b": "dog"},
  {"type": "eq", "a": "red", "b": "Jon"}
 ]}
```
</details>

### 105. L4-06 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(Hugo, green)`; `eq(Hugo, green)`; `eq(Raul, Elena)`; `eq(red, bird)`; `eq(Hugo, horse)`
- **Restricciones invertidas:** `offset(hamster, rabbit, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Hugo", "Kai", "Elena", "Carla"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "blue", "green"]},
    {"type": "alldiff", "vars": ["hamster", "horse", "bird", "rabbit", "turtle"]},
    {"type": "eq", "a": "Hugo", "b": "green"},
    {"type": "offset", "a": "hamster", "b": "rabbit", "k": 1},
    {"type": "neq", "a": "Raul", "b": "turtle"},
    {"type": "offset", "a": "Kai", "b": "yellow", "k": 1},
    {"type": "eq", "a": "Hugo", "b": "green"},
    {"type": "eq", "a": "Raul", "b": "Elena"},
    {"type": "offset", "a": "Kai", "b": "yellow", "k": 1},
    {"type": "eq", "a": "red", "b": "bird"},
    {"type": "neq", "a": "Hugo", "b": "yellow"},
    {"type": "eq", "a": "Hugo", "b": "horse"}
  ]
}
'''
```
</details>

### 106. L4-07 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `eq(turtle, orange)`; `neq(Vera, 1)`; `eq(Felix, Iris)`; `eq(Felix, Elena)`; `eq(red, yellow)`; `eq(Iris, bird)`; `next_to(cat, turtle)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Felix": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Felix", "Iris", "Elena", "Vera", "Mateo"]},
    {"type": "alldiff", "vars": ["red", "orange", "yellow", "white", "blue"]},
    {"type": "alldiff", "vars": ["fish", "turtle", "bird", "horse", "cat"]},
    {"type": "eq", "a": "turtle", "b": "orange", "k": 1},
    {"type": "offset", "a": "Felix", "b": "Iris", "k": 1},
    {"type": "neq", "a": "Vera", "b": 1},
    {"type": "eq", "a": "Felix", "b": "Iris"},
    {"type": "eq", "a": "Felix", "b": "Elena"},
    {"type": "next_to", "a": "Iris", "b": "bird"},
    {"type": "eq", "a": "red", "b": "yellow", "k": 1},
    {"type": "eq", "a": "Iris", "b": "bird"},
    {"type": "next_to", "a": "cat", "b": "turtle"},
    {"type": "next_to", "a": "blue", "b": "yellow"}
  ]
}
'''
```
</details>

### 107. L4-10 · rep 4 (T=0.7) · Sobre-restringido (sin solución)

- **Detectable sin verdad:** sí (señal: `unsat`)
- **Mensaje del parser/solver:** no solution exists
- **Restricciones inventadas (la verdad las viola):** `offset(Iris, fish, k=1)`; `next_to(turtle, yellow)`
- **Restricciones invertidas:** `offset(orange, purple, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Elena": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Iris", "Raul", "Jon", "Ana"]},
    {"type": "alldiff", "vars": ["orange", "purple", "yellow", "blue", "black"]},
    {"type": "alldiff", "vars": ["bird", "turtle", "rabbit", "fish", "horse"]},
    {"type": "lt", "a": "Elena", "b": "turtle"},
    {"type": "offset", "a": "Iris", "b": "fish", "k": 1},
    {"type": "next_to", "a": "black", "b": "turtle"},
    {"type": "lt", "a": "horse", "b": "yellow"},
    {"type": "eq", "a": "rabbit", "b": "purple"},
    {"type": "lt", "a": "Iris", "b": "Elena"},
    {"type": "neq", "a": "Raul", "b": 3},
    {"type": "next_to", "a": "turtle", "b": "yellow"},
    {"type": "next_to", "a": "Raul", "b": "purple"},
    {"type": "offset", "a": "orange", "b": "purple", "k": 1},
    {"type": "lt", "a": "orange", "b": "Ana"}
  ]
}
'''
```
</details>

## Sub-restringido (varias soluciones, devolvió otra) (71)

### 108. L1-02 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Nora": 3, "Raul": 2, "Elena": 1, "Hugo": 1}`
- **Respuesta correcta:** `{"Raul": 1, "Nora": 3, "Hugo": 4, "Elena": 2}`
- **Restricciones invertidas:** `offset(Raul, Elena, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `offset(Elena, Raul, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Elena": [1, 2, 3, 4]},
 "constraints": [
  {"type": "eq", "a": "Nora", "b": 3},
  {"type": "offset", "a": "Raul", "b": "Elena", "k": 1}
 ]}
```
</details>

### 109. L1-04 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Nora": 1, "Raul": 2, "Sara": 1, "Dev": 2}`
- **Respuesta correcta:** `{"Nora": 3, "Dev": 4, "Sara": 1, "Raul": 2}`
- **Restricciones invertidas:** `offset(Raul, Nora, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `offset(Nora, Raul, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Nora": [1, 2, 3, 4], "Dev": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Raul": [1, 2, 3, 4]},
 "constraints": [
  {"type": "lt", "a": "Nora", "b": "Dev"},
  {"type": "offset", "a": "Raul", "b": "Nora", "k": 1},
  {"type": "lt", "a": "Sara", "b": "Raul"}
 ]}
```
</details>

### 110. L1-07 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Felix": 1, "Jon": 2, "Ben": 1, "Tomas": 1}`
- **Respuesta correcta:** `{"Ben": 4, "Felix": 1, "Jon": 3, "Tomas": 2}`
- **Restricciones invertidas:** `offset(Jon, Ben, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `lt(Tomas, Jon)`; `offset(Ben, Jon, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Ben": [1, 2, 3, 4], "Felix": [1, 2, 3, 4], "Jon": [1, 2, 3, 4], "Tomas": [1, 2, 3, 4]},
 "constraints": [
  {"type": "eq", "a": "Felix", "b": 1},
  {"type": "next_to", "a": "Tomas", "b": "Jon"},
  {"type": "offset", "a": "Jon", "b": "Ben", "k": 1}
 ]}
```
</details>

### 111. L1-09 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 1, "Ana": 2, "Felix": 3, "Paula": 4}`
- **Respuesta correcta:** `{"Felix": 2, "Ana": 3, "Paula": 1, "Carla": 4}`
- **Restricciones invertidas:** `offset(Felix, Ana, k=1)`
- **Pistas perdidas:** `lt(Felix, Ana)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Felix": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Paula": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Felix", "Ana", "Paula", "Carla"]},
  {"type": "offset", "a": "Felix", "b": "Ana", "k": 1},
  {"type": "neq", "a": "Carla", "b": 3},
  {"type": "next_to", "a": "Ana", "b": "Carla"},
  {"type": "next_to", "a": "Felix", "b": "Ana"}
 ]}
```
</details>

### 112. L1-10 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Hugo": 3, "Carla": 2, "Vera": 1, "Sara": 2}`
- **Respuesta correcta:** `{"Vera": 1, "Hugo": 3, "Sara": 2, "Carla": 4}`
- **Restricciones invertidas:** `offset(Hugo, Carla, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `offset(Carla, Hugo, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Vera": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "next_to", "a": "Hugo", "b": "Sara"},
  {"type": "lt", "a": "Vera", "b": "Carla"},
  {"type": "offset", "a": "Hugo", "b": "Carla", "k": 1}
 ]}
```
</details>

### 113. L2-07 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 2, "white": 2, "Nora": 1, "Gina": 3, "Lucia": 4, "green": 4, "black": 3, "blue": 1}`
- **Respuesta correcta:** `{"Gina": 3, "Carla": 2, "Nora": 4, "Lucia": 1, "green": 1, "white": 3, "black": 2, "blue": 4}`
- **Restricciones inventadas (la verdad las viola):** `eq(Carla, white)`
- **Restricciones invertidas:** `offset(green, black, k=1)`
- **Pistas perdidas:** `offset(white, Carla, k=1)`; `offset(black, green, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Gina": [1, 2, 3, 4], "Carla": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4],
                "green": [1, 2, 3, 4], "white": [1, 2, 3, 4], "black": [1, 2, 3, 4], "blue": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Gina", "Carla", "Nora", "Lucia"]},
  {"type": "alldiff", "vars": ["green", "white", "black", "blue"]},
  {"type": "eq", "a": "Carla", "b": "white"},
  {"type": "neq", "a": "Carla", "b": 1},
  {"type": "next_to", "a": "Nora", "b": "white"},
  {"type": "lt", "a": "Carla", "b": "Gina"},
  {"type": "offset", "a": "green", "b": "black", "k": 1}
 ]}
```
</details>

### 114. L2-08 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Dev": 4, "Elena": 3, "yellow": 3, "Sara": 2, "red": 1, "Mateo": 1, "orange": 2, "black": 4}`
- **Respuesta correcta:** `{"Elena": 3, "Sara": 1, "Mateo": 2, "Dev": 4, "red": 4, "orange": 1, "black": 2, "yellow": 3}`
- **Restricciones inventadas (la verdad las viola):** `offset(Sara, red, k=1)`
- **Pistas perdidas:** `lt(Sara, Mateo)`; `offset(red, Elena, k=1)`; `offset(yellow, black, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Mateo": [1, 2, 3, 4],
    "Dev": [1, 2, 3, 4],
    "red": [1, 2, 3, 4],
    "orange": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Sara", "Mateo", "Dev"]},
    {"type": "alldiff", "vars": ["red", "orange", "black", "yellow"]},
    {"type": "eq", "a": "Elena", "b": "yellow"},
    {"type": "offset", "a": "Sara", "b": "red", "k": 1},
    {"type": "next_to", "a": "Elena", "b": "Dev"},
    {"type": "neq", "a": "Dev", "b": 1},
    {"type": "eq", "a": "Dev", "b": 4}
  ]
}
```
</details>

### 115. L2-09 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ben": 1, "blue": 1, "white": 2, "green": 3, "black": 4, "Iris": 4, "Felix": 3, "Nora": 2}`
- **Respuesta correcta:** `{"Iris": 2, "Felix": 3, "Nora": 4, "Ben": 1, "black": 4, "blue": 1, "green": 3, "white": 2}`
- **Restricciones invertidas:** `offset(Iris, Felix, k=1)`
- **Pistas perdidas:** `offset(Felix, Iris, k=1)`; `lt(Felix, Nora)`; `offset(green, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Iris": [1, 2, 3, 4],
    "Felix": [1, 2, 3, 4],
    "Nora": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "white": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Iris", "Felix", "Nora", "Ben"]},
    {"type": "alldiff", "vars": ["black", "blue", "green", "white"]},
    {"type": "eq", "a": "Ben", "b": "blue"},
    {"type": "next_to", "a": "Ben", "b": "white"},
    {"type": "offset", "a": "Iris", "b": "Felix", "k": 1},
    {"type": "next_to", "a": "Felix", "b": "Nora"},
    {"type": "next_to", "a": "white", "b": "green"}
  ]
}
```
</details>

### 116. L3-04 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"orange": 1, "blue": 2, "Carla": 2, "Paula": 3, "white": 4, "Gina": 1, "Ana": 4, "Vera": 5, "green": 3, "red": 5}`
- **Respuesta correcta:** `{"Paula": 3, "Vera": 1, "Gina": 5, "Carla": 4, "Ana": 2, "blue": 4, "red": 2, "white": 5, "green": 1, "orange": 3}`
- **Restricciones inventadas (la verdad las viola):** `next_to(Paula, white)`
- **Pistas perdidas:** `lt(Ana, Paula)`; `lt(green, Ana)`; `lt(Paula, white)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Paula": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Vera", "Gina", "Carla", "Ana"]},
    {"type": "alldiff", "vars": ["blue", "red", "white", "green", "orange"]},
    {"type": "eq", "a": "Carla", "b": "blue"},
    {"type": "next_to", "a": "Gina", "b": "Carla"},
    {"type": "next_to", "a": "Paula", "b": "Carla"},
    {"type": "neq", "a": "orange", "b": 2},
    {"type": "next_to", "a": "Ana", "b": "green"},
    {"type": "next_to", "a": "Paula", "b": "white"}
  ]
}
```
</details>

### 117. L3-06 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Jon": 2, "orange": 2, "yellow": 4, "Raul": 3, "Dev": 5, "Vera": 1, "Kai": 4, "white": 3, "green": 5, "black": 1}`
- **Respuesta correcta:** `{"Raul": 5, "Dev": 3, "Jon": 2, "Vera": 1, "Kai": 4, "yellow": 4, "orange": 2, "black": 1, "white": 3, "green": 5}`
- **Pistas perdidas:** `lt(orange, white)`; `lt(white, yellow)`; `lt(yellow, green)`; `lt(yellow, Raul)`; `eq(Kai, yellow)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Dev", "Jon", "Vera", "Kai"]},
    {"type": "alldiff", "vars": ["yellow", "orange", "black", "white", "green"]},
    {"type": "eq", "a": "Jon", "b": "orange"},
    {"type": "next_to", "a": "Dev", "b": "yellow"},
    {"type": "next_to", "a": "yellow", "b": "white"},
    {"type": "neq", "a": "Jon", "b": 1},
    {"type": "next_to", "a": "yellow", "b": "green"},
    {"type": "next_to", "a": "yellow", "b": "Raul"}
  ]
}
```
</details>

### 118. L3-09 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Omar": 1, "orange": 1, "Tomas": 4, "green": 4, "Dev": 3, "Mateo": 2, "Kai": 5, "white": 2, "yellow": 3, "red": 5}`
- **Respuesta correcta:** `{"Omar": 5, "Tomas": 4, "Kai": 1, "Dev": 3, "Mateo": 2, "white": 3, "orange": 5, "yellow": 1, "red": 2, "green": 4}`
- **Pistas perdidas:** `lt(red, Dev)`; `lt(green, orange)`; `offset(Mateo, yellow, k=1)`; `offset(Tomas, Dev, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Omar": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Omar", "Tomas", "Kai", "Dev", "Mateo"]},
    {"type": "alldiff", "vars": ["white", "orange", "yellow", "red", "green"]},
    {"type": "eq", "a": "Tomas", "b": "green"},
    {"type": "eq", "a": "Omar", "b": "orange"},
    {"type": "offset", "a": "Dev", "b": "Mateo", "k": 1},
    {"type": "offset", "a": "Mateo", "b": "Dev", "k": -1},
    {"type": "lt", "a": "Dev", "b": "Tomas"}
  ]
}
```
</details>

### 119. L4-02 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 2, "cat": 2, "red": 2, "purple": 3, "Omar": 1, "Nora": 3, "Ana": 4, "Hugo": 5, "black": 1, "green": 4, "yellow": 5, "rabbit": 3, "dog": 4, "fish": 1, "horse": 5}`
- **Respuesta correcta:** `{"Nora": 5, "Omar": 2, "Carla": 3, "Ana": 4, "Hugo": 1, "red": 3, "purple": 4, "black": 2, "green": 1, "yellow": 5, "cat": 3, "rabbit": 2, "fish": 5, "dog": 4, "horse": 1}`
- **Restricciones inventadas (la verdad las viola):** `next_to(rabbit, dog)`
- **Pistas perdidas:** `offset(Carla, black, k=1)`; `lt(green, yellow)`; `lt(rabbit, dog)`; `lt(Ana, fish)`; `next_to(red, rabbit)`; `lt(Hugo, Omar)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Nora": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Omar", "Carla", "Ana", "Hugo"]},
    {"type": "alldiff", "vars": ["red", "purple", "black", "green", "yellow"]},
    {"type": "alldiff", "vars": ["cat", "rabbit", "fish", "dog", "horse"]},
    {"type": "eq", "a": "Carla", "b": "red"},
    {"type": "eq", "a": "Carla", "b": "cat"},
    {"type": "offset", "a": "purple", "b": "cat", "k": 1},
    {"type": "neq", "a": "Carla", "b": 1},
    {"type": "alldiff", "vars": ["green", "yellow"]},
    {"type": "next_to", "a": "rabbit", "b": "dog"},
    {"type": "neq", "a": "Ana", "b": 1},
    {"type": "alldiff", "vars": ["red", "rabbit"]},
    {"type": "next_to", "a": "Omar", "b": "cat"},
    {"type": "neq", "a": "Hugo", "b": 2}
  ]
}
```
</details>

### 120. L4-03 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"white": 2, "fish": 2, "Dev": 2, "Hugo": 1, "turtle": 3, "blue": 3, "dog": 4, "bird": 5, "cat": 1, "Elena": 3, "Vera": 4, "Ben": 5, "yellow": 5, "red": 4, "green": 1}`
- **Respuesta correcta:** `{"Hugo": 1, "Vera": 3, "Elena": 4, "Ben": 5, "Dev": 2, "white": 2, "yellow": 5, "red": 4, "blue": 3, "green": 1, "dog": 4, "turtle": 3, "fish": 2, "cat": 1, "bird": 5}`
- **Restricciones inventadas (la verdad las viola):** `eq(Vera, red)`
- **Pistas perdidas:** `next_to(Vera, red)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Hugo": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Hugo", "Vera", "Elena", "Ben", "Dev"]},
    {"type": "alldiff", "vars": ["white", "yellow", "red", "blue", "green"]},
    {"type": "alldiff", "vars": ["dog", "turtle", "fish", "cat", "bird"]},
    {"type": "eq", "a": "Vera", "b": "red"},
    {"type": "eq", "a": "Ben", "b": "yellow"},
    {"type": "lt", "a": "Hugo", "b": "Dev"},
    {"type": "eq", "a": "turtle", "b": "blue"},
    {"type": "lt", "a": "turtle", "b": "dog"},
    {"type": "lt", "a": "white", "b": "turtle"},
    {"type": "eq", "a": "fish", "b": "white"},
    {"type": "eq", "a": "Dev", "b": "fish"},
    {"type": "lt", "a": "Elena", "b": "bird"}
  ]
}
```
</details>

### 121. L4-09 · rep 0 (T=0.0) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"dog": 2, "Omar": 3, "Ana": 2, "Jon": 1, "blue": 2, "hamster": 3, "purple": 1, "red": 3, "fish": 4, "green": 5, "turtle": 5, "orange": 4, "horse": 1, "Tomas": 4, "Carla": 5}`
- **Respuesta correcta:** `{"Omar": 4, "Ana": 3, "Tomas": 2, "Jon": 1, "Carla": 5, "orange": 5, "green": 4, "blue": 3, "purple": 1, "red": 2, "fish": 5, "hamster": 4, "dog": 3, "horse": 1, "turtle": 2}`
- **Pistas perdidas:** `offset(fish, green, k=1)`; `offset(orange, hamster, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Omar": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Omar", "Ana", "Tomas", "Jon", "Carla"]},
    {"type": "alldiff", "vars": ["orange", "green", "blue", "purple", "red"]},
    {"type": "alldiff", "vars": ["fish", "hamster", "dog", "horse", "turtle"]},
    {"type": "neq", "a": "Jon", "b": "turtle"},
    {"type": "next_to", "a": "red", "b": "dog"},
    {"type": "neq", "a": "Tomas", "b": "purple"},
    {"type": "next_to", "a": "Omar", "b": "Ana"},
    {"type": "next_to", "a": "Omar", "b": "blue"},
    {"type": "next_to", "a": "Ana", "b": "Omar"},
    {"type": "next_to", "a": "Omar", "b": "blue"},
    {"type": "next_to", "a": "green", "b": "fish"},
    {"type": "lt", "a": "Jon", "b": "Ana"},
    {"type": "lt", "a": "Ana", "b": "fish"},
    {"type": "next_to", "a": "Omar", "b": "dog"},
    {"type": "lt", "a": "purple", "b": "hamster"},
    {"type": "lt", "a": "Ana", "b": "Omar"},
    {"type": "next_to", "a": "blue", "b": "hamster"},
    {"type": "lt", "a": "dog", "b": "Carla"}
  ]
}
```
</details>

### 122. L1-02 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Nora": 3, "Raul": 2, "Elena": 1, "Hugo": 1}`
- **Respuesta correcta:** `{"Raul": 1, "Nora": 3, "Hugo": 4, "Elena": 2}`
- **Restricciones invertidas:** `offset(Raul, Elena, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `offset(Elena, Raul, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Raul": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Elena": [1, 2, 3, 4]},
  "constraints": [
    {"type": "eq", "a": "Nora", "b": 3},
    {"type": "offset", "a": "Raul", "b": "Elena", "k": 1}
  ]
}
'''
```
</details>

### 123. L1-07 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Felix": 1, "Jon": 2, "Ben": 1, "Tomas": 1}`
- **Respuesta correcta:** `{"Ben": 4, "Felix": 1, "Jon": 3, "Tomas": 2}`
- **Restricciones invertidas:** `offset(Jon, Ben, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `lt(Tomas, Jon)`; `offset(Ben, Jon, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Ben": [1, 2, 3, 4], "Felix": [1, 2, 3, 4], "Jon": [1, 2, 3, 4], "Tomas": [1, 2, 3, 4]},
  "constraints": [
    {"type": "eq", "a": "Felix", "b": 1},
    {"type": "next_to", "a": "Tomas", "b": "Jon"},
    {"type": "offset", "a": "Jon", "b": "Ben", "k": 1}
  ]
}
'''

This JSON object represents the given puzzle as a constraint satisfaction problem (CSP) using the specified constraint types.
```
</details>

### 124. L1-09 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 1, "Ana": 2, "Felix": 3, "Paula": 4}`
- **Respuesta correcta:** `{"Felix": 2, "Ana": 3, "Paula": 1, "Carla": 4}`
- **Restricciones invertidas:** `offset(Felix, Ana, k=1)`
- **Pistas perdidas:** `lt(Felix, Ana)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Felix": [1, 2, 3, 4],
    "Ana": [1, 2, 3, 4],
    "Paula": [1, 2, 3, 4],
    "Carla": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Felix", "Ana", "Paula", "Carla"]},
    {"type": "offset", "a": "Felix", "b": "Ana", "k": 1},
    {"type": "neq", "a": "Carla", "b": 3},
    {"type": "next_to", "a": "Ana", "b": "Carla"},
    {"type": "next_to", "a": "Felix", "b": "Ana"}
  ]
}
```
</details>

### 125. L1-10 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Hugo": 2, "Carla": 1, "Vera": 2, "Sara": 1}`
- **Respuesta correcta:** `{"Vera": 1, "Hugo": 3, "Sara": 2, "Carla": 4}`
- **Restricciones inventadas (la verdad las viola):** `offset(Vera, Carla, k=1)`
- **Restricciones invertidas:** `offset(Hugo, Carla, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `lt(Vera, Carla)`; `offset(Carla, Hugo, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Vera": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
  "constraints": [
    {"type": "next_to", "a": "Hugo", "b": "Sara"},
    {"type": "offset", "a": "Vera", "b": "Carla", "k": 1},
    {"type": "offset", "a": "Hugo", "b": "Carla", "k": 1}
  ]
}
'''

This JSON object represents the constraint satisfaction problem for the given puzzle, with variables for each friend and the appropriate constraints to ensure that the clues are respected.
```
</details>

### 126. L2-09 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ben": 1, "blue": 1, "white": 2, "green": 3, "black": 4, "Iris": 4, "Felix": 3, "Nora": 2}`
- **Respuesta correcta:** `{"Iris": 2, "Felix": 3, "Nora": 4, "Ben": 1, "black": 4, "blue": 1, "green": 3, "white": 2}`
- **Restricciones invertidas:** `offset(Iris, Felix, k=1)`
- **Pistas perdidas:** `offset(Felix, Iris, k=1)`; `lt(Felix, Nora)`; `offset(green, white, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Iris": [1, 2, 3, 4], "Felix": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Ben": [1, 2, 3, 4],
                 "black": [1, 2, 3, 4], "blue": [1, 2, 3, 4], "green": [1, 2, 3, 4], "white": [1, 2, 3, 4]},
  "constraints": [
    {"type": "alldiff", "vars": ["Iris", "Felix", "Nora", "Ben"]},
    {"type": "alldiff", "vars": ["black", "blue", "green", "white"]},
    {"type": "eq", "a": "Ben", "b": "blue"},
    {"type": "next_to", "a": "Ben", "b": "white"},
    {"type": "offset", "a": "Iris", "b": "Felix", "k": 1},
    {"type": "next_to", "a": "Felix", "b": "Nora"},
    {"type": "next_to", "a": "white", "b": "green"}
  ]
}
'''
```
</details>

### 127. L2-10 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"green": 3, "Elena": 3, "Omar": 2, "purple": 1, "Hugo": 1, "blue": 2, "Paula": 4, "yellow": 4}`
- **Respuesta correcta:** `{"Elena": 4, "Paula": 1, "Omar": 3, "Hugo": 2, "purple": 1, "yellow": 2, "green": 4, "blue": 3}`
- **Restricciones inventadas (la verdad las viola):** `offset(Omar, purple, k=1)`; `eq(purple, Hugo)`
- **Pistas perdidas:** `next_to(purple, yellow)`; `lt(purple, Hugo)`; `offset(blue, Hugo, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4],
    "Paula": [1, 2, 3, 4],
    "Omar": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Paula", "Omar", "Hugo"]},
    {"type": "alldiff", "vars": ["purple", "yellow", "green", "blue"]},
    {"type": "eq", "a": "Elena", "b": "green"},
    {"type": "offset", "a": "Omar", "b": "purple", "k": 1},
    {"type": "offset", "a": "Elena", "b": "Omar", "k": 1},
    {"type": "neq", "a": "green", "b": 1},
    {"type": "eq", "a": "purple", "b": "Hugo"},
    {"type": "next_to", "a": "Hugo", "b": "blue"}
  ]
}
```
</details>

### 128. L3-02 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Mateo": 1, "red": 2, "Ana": 3, "orange": 1, "black": 3, "Tomas": 2, "Gina": 4, "Ben": 5, "purple": 4, "blue": 5}`
- **Respuesta correcta:** `{"Gina": 4, "Mateo": 2, "Ana": 5, "Ben": 1, "Tomas": 3, "purple": 5, "black": 2, "red": 3, "orange": 1, "blue": 4}`
- **Restricciones inventadas (la verdad las viola):** `eq(Mateo, orange)`; `next_to(Ana, red)`
- **Pistas perdidas:** `next_to(Mateo, orange)`; `lt(red, Ana)`; `offset(Ana, Gina, k=1)`; `offset(red, black, k=1)`; `offset(purple, blue, k=1)`; `offset(Tomas, black, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Gina": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "Ana": [1, 2, 3, 4, 5], "Ben": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5], "purple": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Gina", "Mateo", "Ana", "Ben", "Tomas"]},
  {"type": "alldiff", "vars": ["purple", "black", "red", "orange", "blue"]},
  {"type": "eq", "a": "Mateo", "b": "orange"},
  {"type": "next_to", "a": "Mateo", "b": "red"},
  {"type": "next_to", "a": "Ana", "b": "red"},
  {"type": "next_to", "a": "Gina", "b": "Ana"},
  {"type": "next_to", "a": "black", "b": "red"},
  {"type": "next_to", "a": "Tomas", "b": "black"},
  {"type": "next_to", "a": "blue", "b": "purple"}
 ]}
```
</details>

### 129. L3-04 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ana": 1, "green": 2, "Carla": 3, "blue": 3, "Paula": 2, "white": 1, "Gina": 4, "Vera": 5, "red": 4, "orange": 5}`
- **Respuesta correcta:** `{"Paula": 3, "Vera": 1, "Gina": 5, "Carla": 4, "Ana": 2, "blue": 4, "red": 2, "white": 5, "green": 1, "orange": 3}`
- **Restricciones inventadas (la verdad las viola):** `next_to(Paula, white)`; `lt(Ana, 2)`
- **Pistas perdidas:** `lt(green, Ana)`; `lt(Paula, white)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Paula": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Gina": [1, 2, 3, 4, 5], "Carla": [1, 2, 3, 4, 5], "Ana": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Paula", "Vera", "Gina", "Carla", "Ana"]},
  {"type": "alldiff", "vars": ["blue", "red", "white", "green", "orange"]},
  {"type": "eq", "a": "Carla", "b": "blue"},
  {"type": "next_to", "a": "Gina", "b": "Carla"},
  {"type": "next_to", "a": "Paula", "b": "Carla"},
  {"type": "neq", "a": "Carla", "b": 2},
  {"type": "next_to", "a": "Ana", "b": "green"},
  {"type": "next_to", "a": "Paula", "b": "white"},
  {"type": "lt", "a": "Ana", "b": 2}
 ]}
```
</details>

### 130. L3-05 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Paula": 1, "Ben": 2, "Kai": 3, "Mateo": 4, "black": 3, "blue": 1, "Gina": 5, "red": 2, "green": 4, "purple": 5}`
- **Respuesta correcta:** `{"Ben": 5, "Mateo": 2, "Kai": 3, "Paula": 1, "Gina": 4, "blue": 4, "purple": 5, "black": 3, "red": 1, "green": 2}`
- **Restricciones inventadas (la verdad las viola):** `next_to(red, black)`; `next_to(Kai, Ben)`
- **Restricciones invertidas:** `offset(Mateo, black, k=1)`
- **Pistas perdidas:** `offset(black, Mateo, k=1)`; `lt(red, black)`; `lt(Kai, Ben)`; `eq(Gina, 4)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Ben": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "Kai": [1, 2, 3, 4, 5],
                "Paula": [1, 2, 3, 4, 5], "Gina": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5],
                "purple": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Ben", "Mateo", "Kai", "Paula", "Gina"]},
  {"type": "alldiff", "vars": ["blue", "purple", "black", "red", "green"]},
  {"type": "lt", "a": "Paula", "b": "Kai"},
  {"type": "next_to", "a": "black", "b": "green"},
  {"type": "offset", "a": "Mateo", "b": "black", "k": 1},
  {"type": "next_to", "a": "Ben", "b": "blue"},
  {"type": "neq", "a": "Paula", "b": 2},
  {"type": "next_to", "a": "red", "b": "black"},
  {"type": "next_to", "a": "Kai", "b": "Ben"}
 ],
 "additional_constraints": [
  {"type": "eq", "a": "Gina", "b": 4}
 ]
}
```
</details>

### 131. L3-06 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Jon": 2, "orange": 2, "yellow": 4, "Kai": 4, "Raul": 3, "Dev": 5, "Vera": 1, "white": 3, "green": 5, "black": 1}`
- **Respuesta correcta:** `{"Raul": 5, "Dev": 3, "Jon": 2, "Vera": 1, "Kai": 4, "yellow": 4, "orange": 2, "black": 1, "white": 3, "green": 5}`
- **Pistas perdidas:** `lt(orange, white)`; `lt(white, yellow)`; `lt(yellow, green)`; `lt(yellow, Raul)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5], "Jon": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Kai": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Raul", "Dev", "Jon", "Vera", "Kai"]},
  {"type": "alldiff", "vars": ["yellow", "orange", "black", "white", "green"]},
  {"type": "eq", "a": "Jon", "b": "orange"},
  {"type": "next_to", "a": "Dev", "b": "yellow"},
  {"type": "next_to", "a": "yellow", "b": "white"},
  {"type": "neq", "a": "Jon", "b": 1},
  {"type": "next_to", "a": "yellow", "b": "green"},
  {"type": "next_to", "a": "yellow", "b": "Raul"},
  {"type": "eq", "a": "Kai", "b": "yellow"}
 ]}
```
</details>

### 132. L3-08 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"white": 5, "Iris": 5, "Felix": 4, "Paula": 3, "blue": 4, "Ana": 2, "Nora": 1, "red": 1, "green": 3, "orange": 2}`
- **Respuesta correcta:** `{"Iris": 2, "Paula": 4, "Ana": 5, "Felix": 3, "Nora": 1, "blue": 3, "red": 1, "white": 2, "green": 4, "orange": 5}`
- **Restricciones inventadas (la verdad las viola):** `next_to(red, Ana)`; `neq(white, 2)`
- **Restricciones invertidas:** `offset(white, blue, k=1)`; `offset(Iris, Felix, k=1)`
- **Pistas perdidas:** `offset(blue, white, k=1)`; `lt(red, Ana)`; `offset(Felix, Iris, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Iris": [1, 2, 3, 4, 5], "Paula": [1, 2, 3, 4, 5], "Ana": [1, 2, 3, 4, 5], "Felix": [1, 2, 3, 4, 5], "Nora": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Iris", "Paula", "Felix", "Ana", "Nora"]},
  {"type": "alldiff", "vars": ["blue", "red", "white", "green", "orange"]},
  {"type": "eq", "a": "Iris", "b": "white"},
  {"type": "next_to", "a": "Paula", "b": "Felix"},
  {"type": "next_to", "a": "Ana", "b": "green"},
  {"type": "offset", "a": "white", "b": "blue", "k": 1},
  {"type": "next_to", "a": "red", "b": "Ana"},
  {"type": "offset", "a": "Iris", "b": "Felix", "k": 1},
  {"type": "neq", "a": "white", "b": 2}
 ]}
```
</details>

### 133. L3-09 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Dev": 2, "yellow": 1, "Tomas": 3, "green": 3, "Omar": 4, "orange": 4, "Kai": 1, "Mateo": 5, "white": 2, "red": 5}`
- **Respuesta correcta:** `{"Omar": 5, "Tomas": 4, "Kai": 1, "Dev": 3, "Mateo": 2, "white": 3, "orange": 5, "yellow": 1, "red": 2, "green": 4}`
- **Restricciones inventadas (la verdad las viola):** `offset(Dev, yellow, k=1)`
- **Pistas perdidas:** `lt(red, Dev)`; `lt(green, orange)`; `offset(Mateo, yellow, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Omar": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5], "Kai": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Omar", "Tomas", "Kai", "Dev", "Mateo"]},
  {"type": "alldiff", "vars": ["white", "orange", "yellow", "red", "green"]},
  {"type": "eq", "a": "Tomas", "b": "green"},
  {"type": "eq", "a": "Omar", "b": "orange"},
  {"type": "offset", "a": "Dev", "b": "yellow", "k": 1},
  {"type": "next_to", "a": "Dev", "b": "Tomas"},
  {"type": "lt", "a": "Dev", "b": 5}
 ]}
```
</details>

### 134. L4-10 · rep 1 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Raul": 2, "purple": 1, "orange": 2, "rabbit": 1, "yellow": 5, "turtle": 4, "black": 3, "blue": 4, "Elena": 3, "fish": 2, "horse": 3, "Iris": 1, "bird": 5, "Ana": 4, "Jon": 5}`
- **Respuesta correcta:** `{"Elena": 2, "Iris": 1, "Raul": 5, "Jon": 3, "Ana": 4, "orange": 3, "purple": 4, "yellow": 5, "blue": 1, "black": 2, "bird": 5, "turtle": 3, "rabbit": 4, "fish": 1, "horse": 2}`
- **Restricciones inventadas (la verdad las viola):** `next_to(turtle, yellow)`
- **Restricciones invertidas:** `offset(orange, purple, k=1)`
- **Pistas perdidas:** `offset(purple, orange, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Elena": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Iris", "Raul", "Jon", "Ana"]},
    {"type": "alldiff", "vars": ["orange", "purple", "yellow", "blue", "black"]},
    {"type": "alldiff", "vars": ["bird", "turtle", "rabbit", "fish", "horse"]},
    {"type": "lt", "a": "Elena", "b": "turtle"},
    {"type": "offset", "a": "Elena", "b": "fish", "k": 1},
    {"type": "next_to", "a": "black", "b": "turtle"},
    {"type": "lt", "a": "horse", "b": "yellow"},
    {"type": "eq", "a": "rabbit", "b": "purple"},
    {"type": "lt", "a": "Iris", "b": "Elena"},
    {"type": "neq", "a": "Raul", "b": 3},
    {"type": "next_to", "a": "turtle", "b": "yellow"},
    {"type": "next_to", "a": "Raul", "b": "purple"},
    {"type": "offset", "a": "orange", "b": "purple", "k": 1},
    {"type": "lt", "a": "orange", "b": "Ana"}
  ]
}
'''
```
</details>

### 135. L1-05 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Nora": 1, "Sara": 2, "Mateo": 3, "Paula": 4}`
- **Respuesta correcta:** `{"Paula": 4, "Mateo": 1, "Sara": 2, "Nora": 3}`
- **Restricciones invertidas:** `offset(Mateo, Sara, k=1)`
- **Pistas perdidas:** `offset(Sara, Mateo, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Paula": [1, 2, 3, 4], "Mateo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Nora": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Paula", "Mateo", "Sara", "Nora"]},
  {"type": "offset", "a": "Mateo", "b": "Sara", "k": 1},
  {"type": "neq", "a": "Nora", "b": 4},
  {"type": "next_to", "a": "Sara", "b": "Nora"}
 ]}
```
</details>

### 136. L1-07 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Felix": 1, "Jon": 2, "Ben": 1, "Tomas": 1}`
- **Respuesta correcta:** `{"Ben": 4, "Felix": 1, "Jon": 3, "Tomas": 2}`
- **Restricciones invertidas:** `offset(Jon, Ben, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `lt(Tomas, Jon)`; `offset(Ben, Jon, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Ben": [1, 2, 3, 4], "Felix": [1, 2, 3, 4], "Jon": [1, 2, 3, 4], "Tomas": [1, 2, 3, 4]},
 "constraints": [
  {"type": "eq", "a": "Felix", "b": 1},
  {"type": "next_to", "a": "Tomas", "b": "Jon"},
  {"type": "offset", "a": "Jon", "b": "Ben", "k": 1}
 ]}
```
</details>

### 137. L1-08 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Raul": 1, "Omar": 3, "Kai": 4, "Carla": 2}`
- **Respuesta correcta:** `{"Raul": 2, "Omar": 3, "Kai": 4, "Carla": 1}`
- **Restricciones inventadas (la verdad las viola):** `offset(Carla, Omar, k=-1)`
- **Pistas perdidas:** `offset(Raul, Carla, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4], "Omar": [1, 2, 3, 4], "Kai": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "lt", "a": "Carla", "b": "Omar"},
  {"type": "offset", "a": "Carla", "b": "Omar", "k": -1},
  {"type": "lt", "a": "Omar", "b": "Kai"},
  {"type": "alldiff", "vars": ["Raul", "Omar", "Kai", "Carla"]}
 ]}
```
</details>

### 138. L1-09 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 1, "Ana": 2, "Felix": 3, "Paula": 4}`
- **Respuesta correcta:** `{"Felix": 2, "Ana": 3, "Paula": 1, "Carla": 4}`
- **Restricciones invertidas:** `offset(Felix, Ana, k=1)`
- **Pistas perdidas:** `lt(Felix, Ana)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Felix": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Paula": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Felix", "Ana", "Paula", "Carla"]},
  {"type": "offset", "a": "Felix", "b": "Ana", "k": 1},
  {"type": "neq", "a": "Carla", "b": 3},
  {"type": "next_to", "a": "Ana", "b": "Carla"},
  {"type": "next_to", "a": "Felix", "b": "Ana"}
 ]}
```
</details>

### 139. L1-10 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Hugo": 2, "Carla": 1, "Vera": 2, "Sara": 1}`
- **Respuesta correcta:** `{"Vera": 1, "Hugo": 3, "Sara": 2, "Carla": 4}`
- **Restricciones inventadas (la verdad las viola):** `next_to(Vera, Carla)`
- **Restricciones invertidas:** `offset(Hugo, Carla, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `lt(Vera, Carla)`; `offset(Carla, Hugo, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Vera": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "next_to", "a": "Hugo", "b": "Sara"},
  {"type": "next_to", "a": "Vera", "b": "Carla"},
  {"type": "offset", "a": "Hugo", "b": "Carla", "k": 1}
 ]}
```
</details>

### 140. L2-07 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 2, "white": 2, "Nora": 1, "Gina": 3, "Lucia": 4, "green": 4, "black": 3, "blue": 1}`
- **Respuesta correcta:** `{"Gina": 3, "Carla": 2, "Nora": 4, "Lucia": 1, "green": 1, "white": 3, "black": 2, "blue": 4}`
- **Restricciones inventadas (la verdad las viola):** `eq(Carla, white)`
- **Restricciones invertidas:** `offset(green, black, k=1)`
- **Pistas perdidas:** `offset(white, Carla, k=1)`; `offset(black, green, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Gina": [1, 2, 3, 4], "Carla": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4],
                "green": [1, 2, 3, 4], "white": [1, 2, 3, 4], "black": [1, 2, 3, 4], "blue": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Gina", "Carla", "Nora", "Lucia"]},
  {"type": "alldiff", "vars": ["green", "white", "black", "blue"]},
  {"type": "eq", "a": "Carla", "b": "white"},
  {"type": "neq", "a": "Carla", "b": 1},
  {"type": "next_to", "a": "Nora", "b": "white"},
  {"type": "lt", "a": "Carla", "b": "Gina"},
  {"type": "offset", "a": "green", "b": "black", "k": 1}
 ]}
```
</details>

### 141. L2-09 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ben": 4, "blue": 4, "white": 3, "green": 2, "black": 1, "Iris": 1, "Felix": 2, "Nora": 3}`
- **Respuesta correcta:** `{"Iris": 2, "Felix": 3, "Nora": 4, "Ben": 1, "black": 4, "blue": 1, "green": 3, "white": 2}`
- **Restricciones invertidas:** `offset(white, green, k=1)`
- **Pistas perdidas:** `offset(Felix, Iris, k=1)`; `lt(Felix, Nora)`; `offset(green, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Iris": [1, 2, 3, 4],
    "Felix": [1, 2, 3, 4],
    "Nora": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "white": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Iris", "Felix", "Nora", "Ben"]},
    {"type": "alldiff", "vars": ["black", "blue", "green", "white"]},
    {"type": "eq", "a": "Ben", "b": "blue"},
    {"type": "next_to", "a": "Iris", "b": "Felix"},
    {"type": "next_to", "a": "Felix", "b": "Nora"},
    {"type": "offset", "a": "white", "b": "green", "k": 1},
    {"type": "next_to", "a": "Ben", "b": "white"}
  ]
}
```
</details>

### 142. L3-04 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ana": 1, "green": 2, "Paula": 2, "Carla": 3, "blue": 3, "white": 1, "Gina": 4, "Vera": 5, "red": 4, "orange": 5}`
- **Respuesta correcta:** `{"Paula": 3, "Vera": 1, "Gina": 5, "Carla": 4, "Ana": 2, "blue": 4, "red": 2, "white": 5, "green": 1, "orange": 3}`
- **Restricciones inventadas (la verdad las viola):** `neq(Ana, 2)`; `next_to(Paula, white)`
- **Pistas perdidas:** `lt(Ana, Paula)`; `neq(orange, 2)`; `lt(green, Ana)`; `lt(Paula, white)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Paula": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Vera", "Gina", "Carla", "Ana"]},
    {"type": "alldiff", "vars": ["blue", "red", "white", "green", "orange"]},
    {"type": "eq", "a": "Carla", "b": "blue"},
    {"type": "next_to", "a": "Gina", "b": "Carla"},
    {"type": "next_to", "a": "Paula", "b": "Carla"},
    {"type": "neq", "a": "Ana", "b": 2},
    {"type": "next_to", "a": "Ana", "b": "green"},
    {"type": "next_to", "a": "Paula", "b": "white"}
  ]
}
```
</details>

### 143. L3-06 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Jon": 2, "orange": 2, "yellow": 4, "Raul": 3, "Dev": 5, "Vera": 1, "Kai": 4, "white": 3, "green": 5, "black": 1}`
- **Respuesta correcta:** `{"Raul": 5, "Dev": 3, "Jon": 2, "Vera": 1, "Kai": 4, "yellow": 4, "orange": 2, "black": 1, "white": 3, "green": 5}`
- **Pistas perdidas:** `lt(orange, white)`; `lt(white, yellow)`; `lt(yellow, green)`; `lt(yellow, Raul)`; `eq(Kai, yellow)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Dev", "Jon", "Vera", "Kai"]},
    {"type": "alldiff", "vars": ["yellow", "orange", "black", "white", "green"]},
    {"type": "eq", "a": "Jon", "b": "orange"},
    {"type": "next_to", "a": "Dev", "b": "yellow"},
    {"type": "next_to", "a": "white", "b": "yellow"},
    {"type": "neq", "a": "Jon", "b": 1},
    {"type": "next_to", "a": "yellow", "b": "green"},
    {"type": "next_to", "a": "yellow", "b": "Raul"}
  ]
}
```
</details>

### 144. L3-09 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"yellow": 1, "Dev": 2, "Mateo": 1, "Tomas": 3, "green": 3, "Omar": 4, "orange": 4, "Kai": 5, "white": 2, "red": 5}`
- **Respuesta correcta:** `{"Omar": 5, "Tomas": 4, "Kai": 1, "Dev": 3, "Mateo": 2, "white": 3, "orange": 5, "yellow": 1, "red": 2, "green": 4}`
- **Restricciones inventadas (la verdad las viola):** `offset(Dev, yellow, k=1)`; `eq(Mateo, yellow)`
- **Pistas perdidas:** `lt(red, Dev)`; `lt(green, orange)`; `offset(Mateo, yellow, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Omar": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Omar", "Tomas", "Kai", "Dev", "Mateo"]},
    {"type": "alldiff", "vars": ["white", "orange", "yellow", "red", "green"]},
    {"type": "eq", "a": "Tomas", "b": "green"},
    {"type": "eq", "a": "Omar", "b": "orange"},
    {"type": "offset", "a": "Dev", "b": "yellow", "k": 1},
    {"type": "eq", "a": "Mateo", "b": "yellow"},
    {"type": "next_to", "a": "Dev", "b": "Tomas"}
  ]
}
```
</details>

### 145. L4-02 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 2, "cat": 2, "red": 2, "purple": 3, "Omar": 3, "Hugo": 4, "Ana": 5, "Nora": 1, "black": 1, "green": 4, "yellow": 5, "rabbit": 3, "dog": 4, "fish": 1, "horse": 5}`
- **Respuesta correcta:** `{"Nora": 5, "Omar": 2, "Carla": 3, "Ana": 4, "Hugo": 1, "red": 3, "purple": 4, "black": 2, "green": 1, "yellow": 5, "cat": 3, "rabbit": 2, "fish": 5, "dog": 4, "horse": 1}`
- **Restricciones inventadas (la verdad las viola):** `next_to(rabbit, dog)`
- **Pistas perdidas:** `offset(Carla, black, k=1)`; `lt(Omar, cat)`; `lt(green, yellow)`; `lt(rabbit, dog)`; `lt(Ana, fish)`; `next_to(red, rabbit)`; `lt(Hugo, Omar)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Nora": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Omar", "Carla", "Ana", "Hugo"]},
    {"type": "alldiff", "vars": ["red", "purple", "black", "green", "yellow"]},
    {"type": "alldiff", "vars": ["cat", "rabbit", "fish", "dog", "horse"]},
    {"type": "eq", "a": "Carla", "b": "red"},
    {"type": "eq", "a": "Carla", "b": "cat"},
    {"type": "offset", "a": "purple", "b": "cat", "k": 1},
    {"type": "neq", "a": "Carla", "b": 1},
    {"type": "alldiff", "vars": ["green", "yellow"]},
    {"type": "next_to", "a": "rabbit", "b": "dog"},
    {"type": "neq", "a": "Ana", "b": 1},
    {"type": "alldiff", "vars": ["red", "rabbit"]},
    {"type": "next_to", "a": "Omar", "b": "cat"},
    {"type": "next_to", "a": "Hugo", "b": "Omar"}
  ]
}
```
</details>

### 146. L4-03 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"white": 2, "fish": 2, "Dev": 2, "Hugo": 1, "turtle": 3, "blue": 3, "dog": 4, "bird": 5, "cat": 1, "Elena": 3, "Vera": 4, "Ben": 5, "yellow": 5, "red": 4, "green": 1}`
- **Respuesta correcta:** `{"Hugo": 1, "Vera": 3, "Elena": 4, "Ben": 5, "Dev": 2, "white": 2, "yellow": 5, "red": 4, "blue": 3, "green": 1, "dog": 4, "turtle": 3, "fish": 2, "cat": 1, "bird": 5}`
- **Restricciones inventadas (la verdad las viola):** `eq(Vera, red)`
- **Pistas perdidas:** `next_to(Vera, red)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Hugo": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Hugo", "Vera", "Elena", "Ben", "Dev"]},
    {"type": "alldiff", "vars": ["white", "yellow", "red", "blue", "green"]},
    {"type": "alldiff", "vars": ["dog", "turtle", "fish", "cat", "bird"]},
    {"type": "eq", "a": "Vera", "b": "red"},
    {"type": "eq", "a": "Ben", "b": "yellow"},
    {"type": "lt", "a": "Hugo", "b": "Dev"},
    {"type": "eq", "a": "turtle", "b": "blue"},
    {"type": "lt", "a": "turtle", "b": "dog"},
    {"type": "lt", "a": "white", "b": "turtle"},
    {"type": "eq", "a": "fish", "b": "white"},
    {"type": "eq", "a": "Dev", "b": "fish"},
    {"type": "lt", "a": "Elena", "b": "bird"}
  ]
}
```
</details>

### 147. L4-09 · rep 2 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ana": 2, "Omar": 3, "dog": 2, "Carla": 1, "blue": 4, "hamster": 3, "purple": 2, "fish": 1, "turtle": 4, "Jon": 5, "Tomas": 4, "horse": 5, "orange": 3, "red": 1, "green": 5}`
- **Respuesta correcta:** `{"Omar": 4, "Ana": 3, "Tomas": 2, "Jon": 1, "Carla": 5, "orange": 5, "green": 4, "blue": 3, "purple": 1, "red": 2, "fish": 5, "hamster": 4, "dog": 3, "horse": 1, "turtle": 2}`
- **Restricciones inventadas (la verdad las viola):** `next_to(Ana, fish)`; `next_to(purple, hamster)`; `next_to(dog, Carla)`; `next_to(turtle, orange)`
- **Pistas perdidas:** `offset(fish, green, k=1)`; `lt(Jon, Ana)`; `lt(Ana, fish)`; `lt(purple, hamster)`; `lt(Ana, Omar)`; `lt(dog, Carla)`; `offset(orange, hamster, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Omar": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Omar", "Ana", "Tomas", "Jon", "Carla"]},
    {"type": "alldiff", "vars": ["orange", "green", "blue", "purple", "red"]},
    {"type": "alldiff", "vars": ["fish", "hamster", "dog", "horse", "turtle"]},
    {"type": "neq", "a": "Jon", "b": "turtle"},
    {"type": "next_to", "a": "red", "b": "dog"},
    {"type": "neq", "a": "Tomas", "b": "purple"},
    {"type": "next_to", "a": "Omar", "b": "Ana"},
    {"type": "next_to", "a": "Omar", "b": "blue"},
    {"type": "next_to", "a": "Omar", "b": "Ana"},
    {"type": "neq", "a": "Ana", "b": 1},
    {"type": "next_to", "a": "Ana", "b": "fish"},
    {"type": "next_to", "a": "Omar", "b": "dog"},
    {"type": "next_to", "a": "purple", "b": "hamster"},
    {"type": "next_to", "a": "Ana", "b": "Omar"},
    {"type": "next_to", "a": "blue", "b": "hamster"},
    {"type": "next_to", "a": "dog", "b": "Carla"},
    {"type": "next_to", "a": "turtle", "b": "orange"}
  ]
}
```
</details>

### 148. L1-02 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Nora": 3, "Raul": 2, "Elena": 1, "Hugo": 1}`
- **Respuesta correcta:** `{"Raul": 1, "Nora": 3, "Hugo": 4, "Elena": 2}`
- **Restricciones invertidas:** `offset(Raul, Elena, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `offset(Elena, Raul, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Elena": [1, 2, 3, 4]},
 "constraints": [
  {"type": "eq", "a": "Nora", "b": 3},
  {"type": "offset", "a": "Raul", "b": "Elena", "k": 1}
 ]}
```
</details>

### 149. L1-03 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Sara": 3, "Lucia": 2, "Hugo": 1, "Paula": 4}`
- **Respuesta correcta:** `{"Paula": 1, "Sara": 3, "Lucia": 2, "Hugo": 4}`
- **Restricciones inventadas (la verdad las viola):** `offset(Lucia, Hugo, k=1)`
- **Pistas perdidas:** `lt(Lucia, Hugo)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Paula": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Lucia": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Sara", "Lucia", "Hugo"]},
    {"type": "offset", "a": "Sara", "b": "Lucia", "k": 1},
    {"type": "neq", "a": "Sara", "b": 2},
    {"type": "next_to", "a": "Sara", "b": "Lucia"},
    {"type": "offset", "a": "Lucia", "b": "Hugo", "k": 1}
  ]
}
```
</details>

### 150. L1-07 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Felix": 1, "Jon": 2, "Ben": 1, "Tomas": 1}`
- **Respuesta correcta:** `{"Ben": 4, "Felix": 1, "Jon": 3, "Tomas": 2}`
- **Restricciones invertidas:** `offset(Jon, Ben, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `lt(Tomas, Jon)`; `offset(Ben, Jon, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Ben": [1, 2, 3, 4], "Felix": [1, 2, 3, 4], "Jon": [1, 2, 3, 4], "Tomas": [1, 2, 3, 4]},
 "constraints": [
  {"type": "eq", "a": "Felix", "b": 1},
  {"type": "next_to", "a": "Tomas", "b": "Jon"},
  {"type": "offset", "a": "Jon", "b": "Ben", "k": 1}
 ]}
```
</details>

### 151. L1-09 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 1, "Ana": 2, "Felix": 3, "Paula": 4}`
- **Respuesta correcta:** `{"Felix": 2, "Ana": 3, "Paula": 1, "Carla": 4}`
- **Restricciones invertidas:** `offset(Felix, Ana, k=1)`
- **Pistas perdidas:** `lt(Felix, Ana)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Felix": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Paula": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Felix", "Ana", "Paula", "Carla"]},
  {"type": "offset", "a": "Felix", "b": "Ana", "k": 1},
  {"type": "neq", "a": "Carla", "b": 3},
  {"type": "next_to", "a": "Ana", "b": "Carla"},
  {"type": "next_to", "a": "Felix", "b": "Ana"}
 ]}
```
</details>

### 152. L1-10 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Hugo": 3, "Carla": 2, "Vera": 1, "Sara": 2}`
- **Respuesta correcta:** `{"Vera": 1, "Hugo": 3, "Sara": 2, "Carla": 4}`
- **Restricciones invertidas:** `offset(Hugo, Carla, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `offset(Carla, Hugo, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Vera": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
 "constraints": [
  {"type": "next_to", "a": "Hugo", "b": "Sara"},
  {"type": "lt", "a": "Vera", "b": "Carla"},
  {"type": "offset", "a": "Hugo", "b": "Carla", "k": 1}
 ]}
```
</details>

### 153. L2-02 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"white": 3, "Kai": 3, "Ana": 2, "Dev": 1, "Raul": 4, "green": 1, "red": 2, "purple": 4}`
- **Respuesta correcta:** `{"Ana": 4, "Raul": 3, "Kai": 2, "Dev": 1, "white": 3, "green": 2, "purple": 4, "red": 1}`
- **Restricciones inventadas (la verdad las viola):** `eq(Kai, white)`
- **Pistas perdidas:** `offset(white, Kai, k=1)`; `lt(Dev, green)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Ana": [1, 2, 3, 4],
    "Raul": [1, 2, 3, 4],
    "Kai": [1, 2, 3, 4],
    "Dev": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "purple": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Ana", "Raul", "Kai", "Dev"]},
    {"type": "alldiff", "vars": ["white", "green", "purple", "red"]},
    {"type": "eq", "a": "Kai", "b": "white"},
    {"type": "eq", "a": "white", "b": 3},
    {"type": "lt", "a": "Dev", "b": 3},
    {"type": "next_to", "a": "green", "b": "red"},
    {"type": "next_to", "a": "Ana", "b": "white"}
  ]
}
```
</details>

### 154. L2-03 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Jon": 2, "Sara": 4, "Hugo": 3, "white": 2, "black": 4, "Dev": 1, "yellow": 1, "red": 3}`
- **Respuesta correcta:** `{"Dev": 1, "Sara": 3, "Hugo": 4, "Jon": 2, "white": 4, "black": 3, "yellow": 2, "red": 1}`
- **Restricciones inventadas (la verdad las viola):** `offset(Hugo, white, k=1)`
- **Pistas perdidas:** `lt(yellow, Hugo)`; `eq(Dev, red)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Dev": [1, 2, 3, 4],
    "Sara": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4],
    "Jon": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "yellow": [1, 2, 3, 4],
    "red": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Dev", "Sara", "Hugo", "Jon"]},
    {"type": "alldiff", "vars": ["white", "black", "yellow", "red"]},
    {"type": "eq", "a": "Sara", "b": "black"},
    {"type": "offset", "a": "Hugo", "b": "white", "k": 1},
    {"type": "neq", "a": "Jon", "b": 1},
    {"type": "next_to", "a": "Sara", "b": "Hugo"}
  ]
}
```
</details>

### 155. L2-07 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 2, "white": 2, "Nora": 1, "Gina": 3, "Lucia": 4, "green": 3, "black": 4, "blue": 1}`
- **Respuesta correcta:** `{"Gina": 3, "Carla": 2, "Nora": 4, "Lucia": 1, "green": 1, "white": 3, "black": 2, "blue": 4}`
- **Restricciones inventadas (la verdad las viola):** `eq(Carla, white)`
- **Pistas perdidas:** `offset(white, Carla, k=1)`; `offset(black, green, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Gina": [1, 2, 3, 4], "Carla": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4],
                "green": [1, 2, 3, 4], "white": [1, 2, 3, 4], "black": [1, 2, 3, 4], "blue": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Gina", "Carla", "Nora", "Lucia"]},
  {"type": "alldiff", "vars": ["green", "white", "black", "blue"]},
  {"type": "eq", "a": "Carla", "b": "white"},
  {"type": "neq", "a": "Carla", "b": 1},
  {"type": "next_to", "a": "Nora", "b": "white"},
  {"type": "lt", "a": "Carla", "b": "Gina"},
  {"type": "next_to", "a": "green", "b": "black"}
 ]}
```
</details>

### 156. L2-09 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ben": 1, "blue": 1, "white": 2, "green": 3, "black": 4, "Iris": 4, "Felix": 3, "Nora": 2}`
- **Respuesta correcta:** `{"Iris": 2, "Felix": 3, "Nora": 4, "Ben": 1, "black": 4, "blue": 1, "green": 3, "white": 2}`
- **Restricciones invertidas:** `offset(Iris, Felix, k=1)`
- **Pistas perdidas:** `offset(Felix, Iris, k=1)`; `lt(Felix, Nora)`; `offset(green, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Iris": [1, 2, 3, 4],
    "Felix": [1, 2, 3, 4],
    "Nora": [1, 2, 3, 4],
    "Ben": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "white": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Iris", "Felix", "Nora", "Ben"]},
    {"type": "alldiff", "vars": ["black", "blue", "green", "white"]},
    {"type": "eq", "a": "Ben", "b": "blue"},
    {"type": "next_to", "a": "Ben", "b": "white"},
    {"type": "offset", "a": "Iris", "b": "Felix", "k": 1},
    {"type": "next_to", "a": "Felix", "b": "Nora"},
    {"type": "next_to", "a": "white", "b": "green"},
    {"type": "next_to", "a": "Ben", "b": "white"}
  ]
}
```
</details>

### 157. L3-04 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ana": 1, "green": 2, "Paula": 2, "Carla": 3, "blue": 3, "white": 1, "Gina": 4, "Vera": 5, "red": 4, "orange": 5}`
- **Respuesta correcta:** `{"Paula": 3, "Vera": 1, "Gina": 5, "Carla": 4, "Ana": 2, "blue": 4, "red": 2, "white": 5, "green": 1, "orange": 3}`
- **Restricciones inventadas (la verdad las viola):** `next_to(Paula, white)`; `neq(Ana, 2)`
- **Pistas perdidas:** `lt(Ana, Paula)`; `neq(orange, 2)`; `lt(green, Ana)`; `lt(Paula, white)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Paula": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Vera", "Gina", "Carla", "Ana"]},
    {"type": "alldiff", "vars": ["blue", "red", "white", "green", "orange"]},
    {"type": "eq", "a": "Carla", "b": "blue"},
    {"type": "next_to", "a": "Gina", "b": "Carla"},
    {"type": "next_to", "a": "Carla", "b": "Paula"},
    {"type": "next_to", "a": "Paula", "b": "white"},
    {"type": "neq", "a": "Ana", "b": 2},
    {"type": "next_to", "a": "Ana", "b": "green"}
  ]
}
```
</details>

### 158. L3-05 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Paula": 3, "black": 3, "Mateo": 4, "red": 2, "green": 4, "blue": 1, "Ben": 2, "Kai": 1, "Gina": 5, "purple": 5}`
- **Respuesta correcta:** `{"Ben": 5, "Mateo": 2, "Kai": 3, "Paula": 1, "Gina": 4, "blue": 4, "purple": 5, "black": 3, "red": 1, "green": 2}`
- **Restricciones inventadas (la verdad las viola):** `eq(Paula, black)`; `next_to(red, black)`; `next_to(Kai, Ben)`
- **Restricciones invertidas:** `offset(Mateo, black, k=1)`
- **Pistas perdidas:** `lt(Paula, Kai)`; `offset(black, Mateo, k=1)`; `lt(red, black)`; `lt(Kai, Ben)`; `eq(Gina, 4)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Ben": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Paula": [1, 2, 3, 4, 5],
    "Gina": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Ben", "Mateo", "Kai", "Paula", "Gina"]},
    {"type": "alldiff", "vars": ["blue", "purple", "black", "red", "green"]},
    {"type": "eq", "a": "Paula", "b": "black"},
    {"type": "next_to", "a": "black", "b": "green"},
    {"type": "offset", "a": "Mateo", "b": "black", "k": 1},
    {"type": "next_to", "a": "Ben", "b": "blue"},
    {"type": "neq", "a": "Paula", "b": 2},
    {"type": "next_to", "a": "red", "b": "black"},
    {"type": "next_to", "a": "Kai", "b": "Ben"}
  ]
}
```
</details>

### 159. L3-06 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Jon": 2, "orange": 2, "yellow": 4, "Raul": 3, "Dev": 5, "Vera": 1, "Kai": 4, "white": 3, "green": 5, "black": 1}`
- **Respuesta correcta:** `{"Raul": 5, "Dev": 3, "Jon": 2, "Vera": 1, "Kai": 4, "yellow": 4, "orange": 2, "black": 1, "white": 3, "green": 5}`
- **Pistas perdidas:** `lt(orange, white)`; `lt(white, yellow)`; `lt(yellow, green)`; `lt(yellow, Raul)`; `eq(Kai, yellow)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Dev", "Jon", "Vera", "Kai"]},
    {"type": "alldiff", "vars": ["yellow", "orange", "black", "white", "green"]},
    {"type": "eq", "a": "Jon", "b": "orange"},
    {"type": "next_to", "a": "Dev", "b": "yellow"},
    {"type": "next_to", "a": "yellow", "b": "white"},
    {"type": "neq", "a": "Jon", "b": 1},
    {"type": "next_to", "a": "yellow", "b": "green"},
    {"type": "next_to", "a": "yellow", "b": "Raul"}
  ]
}
```
</details>

### 160. L3-09 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Omar": 1, "orange": 1, "Tomas": 4, "Dev": 3, "red": 2, "green": 4, "Mateo": 2, "Kai": 5, "white": 3, "yellow": 5}`
- **Respuesta correcta:** `{"Omar": 5, "Tomas": 4, "Kai": 1, "Dev": 3, "Mateo": 2, "white": 3, "orange": 5, "yellow": 1, "red": 2, "green": 4}`
- **Pistas perdidas:** `lt(green, orange)`; `offset(Mateo, yellow, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Omar": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Kai": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "Mateo": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Omar", "Tomas", "Kai", "Dev", "Mateo"]},
    {"type": "alldiff", "vars": ["white", "orange", "yellow", "red", "green"]},
    {"type": "eq", "a": "Tomas", "b": "green"},
    {"type": "eq", "a": "Omar", "b": "orange"},
    {"type": "offset", "a": "Dev", "b": "Mateo", "k": 1},
    {"type": "offset", "a": "Tomas", "b": "Dev", "k": 1},
    {"type": "lt", "a": "red", "b": "Dev"}
  ]
}
```
</details>

### 161. L4-03 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"white": 2, "fish": 2, "Dev": 2, "Hugo": 1, "turtle": 3, "blue": 3, "dog": 4, "bird": 5, "cat": 1, "Elena": 3, "Vera": 4, "Ben": 5, "yellow": 5, "red": 4, "green": 1}`
- **Respuesta correcta:** `{"Hugo": 1, "Vera": 3, "Elena": 4, "Ben": 5, "Dev": 2, "white": 2, "yellow": 5, "red": 4, "blue": 3, "green": 1, "dog": 4, "turtle": 3, "fish": 2, "cat": 1, "bird": 5}`
- **Restricciones inventadas (la verdad las viola):** `eq(Vera, red)`
- **Pistas perdidas:** `next_to(Vera, red)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Hugo": [1, 2, 3, 4, 5],
    "Vera": [1, 2, 3, 4, 5],
    "Elena": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "Dev": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Hugo", "Vera", "Elena", "Ben", "Dev"]},
    {"type": "alldiff", "vars": ["white", "yellow", "red", "blue", "green"]},
    {"type": "alldiff", "vars": ["dog", "turtle", "fish", "cat", "bird"]},
    {"type": "eq", "a": "Vera", "b": "red"},
    {"type": "eq", "a": "Ben", "b": "yellow"},
    {"type": "lt", "a": "Hugo", "b": "Dev"},
    {"type": "eq", "a": "turtle", "b": "blue"},
    {"type": "lt", "a": "turtle", "b": "dog"},
    {"type": "lt", "a": "white", "b": "turtle"},
    {"type": "eq", "a": "fish", "b": "white"},
    {"type": "eq", "a": "Dev", "b": "fish"},
    {"type": "lt", "a": "Elena", "b": "bird"}
  ]
}
```
</details>

### 162. L4-09 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"dog": 2, "Omar": 3, "Carla": 1, "blue": 2, "hamster": 3, "purple": 4, "Ana": 4, "fish": 5, "Tomas": 2, "Jon": 5, "turtle": 4, "horse": 1, "red": 1, "orange": 3, "green": 5}`
- **Respuesta correcta:** `{"Omar": 4, "Ana": 3, "Tomas": 2, "Jon": 1, "Carla": 5, "orange": 5, "green": 4, "blue": 3, "purple": 1, "red": 2, "fish": 5, "hamster": 4, "dog": 3, "horse": 1, "turtle": 2}`
- **Restricciones inventadas (la verdad las viola):** `next_to(Ana, fish)`; `next_to(Ana, fish)`; `next_to(purple, hamster)`; `next_to(dog, Carla)`
- **Restricciones invertidas:** `offset(Jon, turtle, k=1)`
- **Pistas perdidas:** `offset(fish, green, k=1)`; `lt(Jon, Ana)`; `lt(Ana, fish)`; `lt(purple, hamster)`; `lt(Ana, Omar)`; `lt(dog, Carla)`; `offset(orange, hamster, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Omar": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "hamster": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Omar", "Ana", "Tomas", "Jon", "Carla"]},
    {"type": "alldiff", "vars": ["orange", "green", "blue", "purple", "red"]},
    {"type": "alldiff", "vars": ["fish", "hamster", "dog", "horse", "turtle"]},
    {"type": "neq", "a": "Jon", "b": "turtle"},
    {"type": "next_to", "a": "red", "b": "dog"},
    {"type": "neq", "a": "Tomas", "b": "purple"},
    {"type": "next_to", "a": "Omar", "b": "Ana"},
    {"type": "next_to", "a": "Omar", "b": "blue"},
    {"type": "next_to", "a": "Omar", "b": "blue"},
    {"type": "next_to", "a": "Omar", "b": "blue"},
    {"type": "next_to", "a": "Omar", "b": "blue"},
    {"type": "offset", "a": "Jon", "b": "turtle", "k": 1},
    {"type": "next_to", "a": "Ana", "b": "fish"},
    {"type": "next_to", "a": "Ana", "b": "fish"},
    {"type": "next_to", "a": "Omar", "b": "dog"},
    {"type": "next_to", "a": "purple", "b": "hamster"},
    {"type": "next_to", "a": "Ana", "b": "Omar"},
    {"type": "next_to", "a": "blue", "b": "hamster"},
    {"type": "next_to", "a": "dog", "b": "Carla"}
  ]
}
```
</details>

### 163. L4-10 · rep 3 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Raul": 2, "purple": 1, "orange": 2, "rabbit": 1, "Ana": 1, "Elena": 4, "turtle": 4, "fish": 5, "yellow": 3, "black": 5, "horse": 2, "blue": 4, "bird": 3, "Iris": 3, "Jon": 5}`
- **Respuesta correcta:** `{"Elena": 2, "Iris": 1, "Raul": 5, "Jon": 3, "Ana": 4, "orange": 3, "purple": 4, "yellow": 5, "blue": 1, "black": 2, "bird": 5, "turtle": 3, "rabbit": 4, "fish": 1, "horse": 2}`
- **Restricciones inventadas (la verdad las viola):** `eq(Elena, turtle)`; `next_to(horse, yellow)`; `next_to(turtle, yellow)`
- **Restricciones invertidas:** `offset(fish, Elena, k=1)`; `offset(orange, purple, k=1)`
- **Pistas perdidas:** `lt(Elena, turtle)`; `offset(Elena, fish, k=1)`; `lt(Iris, Elena)`; `lt(turtle, yellow)`; `offset(purple, orange, k=1)`; `lt(orange, Ana)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Elena": [1, 2, 3, 4, 5],
    "Iris": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Jon": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "blue": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "bird": [1, 2, 3, 4, 5],
    "turtle": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Elena", "Iris", "Raul", "Jon", "Ana"]},
    {"type": "alldiff", "vars": ["orange", "purple", "yellow", "blue", "black"]},
    {"type": "alldiff", "vars": ["bird", "turtle", "rabbit", "fish", "horse"]},
    {"type": "eq", "a": "Elena", "b": "turtle"},
    {"type": "offset", "a": "fish", "b": "Elena", "k": 1},
    {"type": "next_to", "a": "black", "b": "turtle"},
    {"type": "next_to", "a": "horse", "b": "yellow"},
    {"type": "eq", "a": "rabbit", "b": "purple"},
    {"type": "next_to", "a": "Iris", "b": "Elena"},
    {"type": "neq", "a": "Raul", "b": 3},
    {"type": "next_to", "a": "turtle", "b": "yellow"},
    {"type": "next_to", "a": "Raul", "b": "purple"},
    {"type": "offset", "a": "orange", "b": "purple", "k": 1},
    {"type": "next_to", "a": "orange", "b": "Ana"}
  ]
}
```
</details>

### 164. L1-01 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Gina": 3, "Carla": 2, "Mateo": 2, "Ben": 1}`
- **Respuesta correcta:** `{"Ben": 1, "Gina": 3, "Carla": 4, "Mateo": 2}`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `lt(Gina, Carla)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Ben": [1, 2, 3, 4],
    "Gina": [1, 2, 3, 4],
    "Carla": [1, 2, 3, 4],
    "Mateo": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "eq", "a": "Gina", "b": 3},
    {"type": "next_to", "a": "Gina", "b": "Carla"},
    {"type": "neq", "a": "Mateo", "b": 1}
  ]
}
```
</details>

### 165. L1-05 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Nora": 1, "Paula": 2, "Mateo": 4, "Sara": 3}`
- **Respuesta correcta:** `{"Paula": 4, "Mateo": 1, "Sara": 2, "Nora": 3}`
- **Restricciones invertidas:** `offset(Mateo, Sara, k=1)`
- **Pistas perdidas:** `next_to(Sara, Nora)`; `offset(Sara, Mateo, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Paula": [1, 2, 3, 4], "Mateo": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Nora": [1, 2, 3, 4]},
  "constraints": [
    {"type": "alldiff", "vars": ["Paula", "Mateo", "Sara", "Nora"]},
    {"type": "offset", "a": "Mateo", "b": "Sara", "k": 1},
    {"type": "alldiff", "vars": ["Sara", "Nora"]},
    {"type": "neq", "a": "Nora", "b": 4}
  ]
}
'''
```
</details>

### 166. L1-07 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Felix": 1, "Jon": 2, "Ben": 1, "Tomas": 1}`
- **Respuesta correcta:** `{"Ben": 4, "Felix": 1, "Jon": 3, "Tomas": 2}`
- **Restricciones invertidas:** `offset(Jon, Ben, k=1)`
- **Pistas perdidas:** `alldiff del grupo 'person' (premisa 'cada casa es distinta')`; `lt(Tomas, Jon)`; `offset(Ben, Jon, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Ben": [1, 2, 3, 4],
    "Felix": [1, 2, 3, 4],
    "Jon": [1, 2, 3, 4],
    "Tomas": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "eq", "a": "Felix", "b": 1},
    {"type": "next_to", "a": "Tomas", "b": "Jon"},
    {"type": "offset", "a": "Jon", "b": "Ben", "k": 1}
  ]
}
```
</details>

### 167. L1-09 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 1, "Ana": 2, "Felix": 3, "Paula": 4}`
- **Respuesta correcta:** `{"Felix": 2, "Ana": 3, "Paula": 1, "Carla": 4}`
- **Restricciones invertidas:** `offset(Felix, Ana, k=1)`
- **Pistas perdidas:** `lt(Felix, Ana)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Felix": [1, 2, 3, 4],
    "Ana": [1, 2, 3, 4],
    "Paula": [1, 2, 3, 4],
    "Carla": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Felix", "Ana", "Paula", "Carla"]},
    {"type": "offset", "a": "Felix", "b": "Ana", "k": 1},
    {"type": "neq", "a": "Carla", "b": 3},
    {"type": "next_to", "a": "Ana", "b": "Carla"},
    {"type": "next_to", "a": "Felix", "b": "Ana"}
  ]
}
```
</details>

### 168. L2-02 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"white": 4, "Ana": 3, "Kai": 4, "Dev": 1, "green": 1, "Raul": 2, "red": 2, "purple": 3}`
- **Respuesta correcta:** `{"Ana": 4, "Raul": 3, "Kai": 2, "Dev": 1, "white": 3, "green": 2, "purple": 4, "red": 1}`
- **Restricciones inventadas (la verdad las viola):** `eq(Kai, white)`; `offset(white, 3, k=1)`; `eq(Dev, green)`
- **Pistas perdidas:** `offset(white, Kai, k=1)`; `eq(white, 3)`; `lt(Dev, green)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Ana": [1, 2, 3, 4], "Raul": [1, 2, 3, 4], "Kai": [1, 2, 3, 4], "Dev": [1, 2, 3, 4],
                "white": [1, 2, 3, 4], "green": [1, 2, 3, 4], "purple": [1, 2, 3, 4], "red": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Ana", "Raul", "Kai", "Dev"]},
  {"type": "alldiff", "vars": ["white", "green", "purple", "red"]},
  {"type": "eq", "a": "Kai", "b": "white"},
  {"type": "offset", "a": "white", "b": 3, "k": 1},
  {"type": "eq", "a": "Dev", "b": "green"},
  {"type": "next_to", "a": "green", "b": "red"},
  {"type": "next_to", "a": "Ana", "b": "white"},
  {"type": "next_to", "a": "white", "b": "Ana"}
 ]}
  
Note: The constraint for the green and red houses being next to each other is incorrectly represented as `{"type": "next_to", "a": "green", "b": "red", "k": 1}` in the example JSON. It should be represented as two separate constraints: `{"type": "next_to", "a": "green", "b": "red"}` and `{"type": "next_to", "a": "red", "b": "green"}` to ensure both conditions are met. However, for simplicity and to fit the given format, I've combined them as `{"type": "next_to", "a": "green", "b": "red"}`.
```
</details>

### 169. L2-03 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"white": 1, "Hugo": 2, "Sara": 3, "black": 3, "Jon": 4, "Dev": 1, "yellow": 2, "red": 4}`
- **Respuesta correcta:** `{"Dev": 1, "Sara": 3, "Hugo": 4, "Jon": 2, "white": 4, "black": 3, "yellow": 2, "red": 1}`
- **Restricciones inventadas (la verdad las viola):** `offset(Hugo, white, k=1)`
- **Restricciones invertidas:** `lt(white, 3)`
- **Pistas perdidas:** `lt(yellow, Hugo)`; `eq(Dev, red)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Dev": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Jon": [1, 2, 3, 4],
                "white": [1, 2, 3, 4], "black": [1, 2, 3, 4], "yellow": [1, 2, 3, 4], "red": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Dev", "Sara", "Hugo", "Jon"]},
  {"type": "alldiff", "vars": ["white", "black", "yellow", "red"]},
  {"type": "eq", "a": "Sara", "b": "black"},
  {"type": "offset", "a": "Hugo", "b": "white", "k": 1},
  {"type": "neq", "a": "yellow", "b": 3},
  {"type": "lt", "a": "white", "b": 3},
  {"type": "neq", "a": "Jon", "b": 1},
  {"type": "next_to", "a": "Hugo", "b": "Sara"}
 ]}
  
Note: The constraint `"type": "next_to", "a": "Hugo", "b": "Sara"` was incorrectly provided in the example. The correct constraint should indicate that Sara and Hugo's houses are next to each other, so we use `"type": "next_to", "a": "Hugo", "b": "Sara"`.
```
</details>

### 170. L2-07 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Carla": 2, "white": 2, "Nora": 1, "Gina": 3, "Lucia": 4, "green": 4, "black": 3, "blue": 1}`
- **Respuesta correcta:** `{"Gina": 3, "Carla": 2, "Nora": 4, "Lucia": 1, "green": 1, "white": 3, "black": 2, "blue": 4}`
- **Restricciones inventadas (la verdad las viola):** `eq(Carla, white)`
- **Restricciones invertidas:** `offset(green, black, k=1)`
- **Pistas perdidas:** `offset(white, Carla, k=1)`; `offset(black, green, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Gina": [1, 2, 3, 4],
    "Carla": [1, 2, 3, 4],
    "Nora": [1, 2, 3, 4],
    "Lucia": [1, 2, 3, 4],
    "green": [1, 2, 3, 4],
    "white": [1, 2, 3, 4],
    "black": [1, 2, 3, 4],
    "blue": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Gina", "Carla", "Nora", "Lucia"]},
    {"type": "alldiff", "vars": ["green", "white", "black", "blue"]},
    {"type": "eq", "a": "Carla", "b": "white"},
    {"type": "neq", "a": "Carla", "b": 1},
    {"type": "next_to", "a": "Nora", "b": "white"},
    {"type": "lt", "a": "Carla", "b": "Gina"},
    {"type": "offset", "a": "green", "b": "black", "k": 1}
  ]
}
```
</details>

### 171. L2-09 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Ben": 4, "blue": 4, "white": 3, "green": 2, "black": 1, "Iris": 1, "Felix": 2, "Nora": 3}`
- **Respuesta correcta:** `{"Iris": 2, "Felix": 3, "Nora": 4, "Ben": 1, "black": 4, "blue": 1, "green": 3, "white": 2}`
- **Restricciones invertidas:** `offset(Ben, white, k=1)`
- **Pistas perdidas:** `offset(Felix, Iris, k=1)`; `lt(Felix, Nora)`; `offset(green, white, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Iris": [1, 2, 3, 4], "Felix": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Ben": [1, 2, 3, 4],
                "black": [1, 2, 3, 4], "blue": [1, 2, 3, 4], "green": [1, 2, 3, 4], "white": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Iris", "Felix", "Nora", "Ben"]},
  {"type": "alldiff", "vars": ["black", "blue", "green", "white"]},
  {"type": "eq", "a": "Ben", "b": "blue"},
  {"type": "next_to", "a": "Iris", "b": "Felix"},
  {"type": "next_to", "a": "Felix", "b": "Nora"},
  {"type": "next_to", "a": "white", "b": "green"},
  {"type": "offset", "a": "Ben", "b": "white", "k": 1}
 ]}
```
</details>

### 172. L3-04 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"orange": 1, "blue": 2, "Carla": 2, "Paula": 3, "white": 4, "Gina": 1, "Ana": 4, "Vera": 5, "green": 3, "red": 5}`
- **Respuesta correcta:** `{"Paula": 3, "Vera": 1, "Gina": 5, "Carla": 4, "Ana": 2, "blue": 4, "red": 2, "white": 5, "green": 1, "orange": 3}`
- **Restricciones inventadas (la verdad las viola):** `next_to(Paula, white)`
- **Pistas perdidas:** `lt(Ana, Paula)`; `lt(green, Ana)`; `lt(Paula, white)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Paula": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Gina": [1, 2, 3, 4, 5],
                "Carla": [1, 2, 3, 4, 5], "Ana": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5],
                "red": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Paula", "Vera", "Gina", "Carla", "Ana"]},
  {"type": "alldiff", "vars": ["blue", "red", "white", "green", "orange"]},
  {"type": "eq", "a": "Carla", "b": "blue"},
  {"type": "next_to", "a": "Gina", "b": "Carla"},
  {"type": "next_to", "a": "Paula", "b": "Carla"},
  {"type": "neq", "a": "orange", "b": 2},
  {"type": "next_to", "a": "green", "b": "Ana"},
  {"type": "next_to", "a": "Paula", "b": "white"}
 ]}
```
</details>

### 173. L3-06 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Jon": 2, "orange": 2, "yellow": 4, "Kai": 4, "Raul": 3, "Dev": 5, "Vera": 1, "white": 3, "green": 5, "black": 1}`
- **Respuesta correcta:** `{"Raul": 5, "Dev": 3, "Jon": 2, "Vera": 1, "Kai": 4, "yellow": 4, "orange": 2, "black": 1, "white": 3, "green": 5}`
- **Pistas perdidas:** `lt(orange, white)`; `lt(white, yellow)`; `lt(yellow, green)`; `lt(yellow, Raul)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5], "Jon": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Kai": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Raul", "Dev", "Jon", "Vera", "Kai"]},
  {"type": "alldiff", "vars": ["yellow", "orange", "black", "white", "green"]},
  {"type": "eq", "a": "Jon", "b": "orange"},
  {"type": "next_to", "a": "Dev", "b": "yellow"},
  {"type": "next_to", "a": "yellow", "b": "white"},
  {"type": "neq", "a": "Jon", "b": 1},
  {"type": "next_to", "a": "yellow", "b": "green"},
  {"type": "next_to", "a": "yellow", "b": "Raul"},
  {"type": "eq", "a": "Kai", "b": "yellow"}
 ]}
```
</details>

### 174. L3-09 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Omar": 1, "orange": 1, "Tomas": 4, "green": 4, "Dev": 3, "Mateo": 2, "Kai": 5, "white": 2, "yellow": 3, "red": 5}`
- **Respuesta correcta:** `{"Omar": 5, "Tomas": 4, "Kai": 1, "Dev": 3, "Mateo": 2, "white": 3, "orange": 5, "yellow": 1, "red": 2, "green": 4}`
- **Pistas perdidas:** `lt(red, Dev)`; `lt(green, orange)`; `offset(Mateo, yellow, k=1)`; `offset(Tomas, Dev, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Omar": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5], "Kai": [1, 2, 3, 4, 5], "Dev": [1, 2, 3, 4, 5], "Mateo": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Omar", "Tomas", "Kai", "Dev", "Mateo"]},
  {"type": "alldiff", "vars": ["white", "orange", "yellow", "red", "green"]},
  {"type": "eq", "a": "Tomas", "b": "green"},
  {"type": "eq", "a": "Omar", "b": "orange"},
  {"type": "offset", "a": "Dev", "b": "Mateo", "k": 1},
  {"type": "offset", "a": "Mateo", "b": "Dev", "k": -1},
  {"type": "lt", "a": "Dev", "b": "Tomas"}
 ]}
```
</details>

### 175. L3-10 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"yellow": 1, "Raul": 2, "orange": 2, "black": 3, "green": 4, "white": 5, "Tomas": 1, "Sara": 4, "Lucia": 5, "Ben": 3}`
- **Respuesta correcta:** `{"Sara": 5, "Lucia": 3, "Tomas": 1, "Raul": 2, "Ben": 4, "green": 5, "yellow": 3, "orange": 2, "black": 4, "white": 1}`
- **Restricciones invertidas:** `offset(Raul, yellow, k=1)`
- **Pistas perdidas:** `lt(black, Sara)`; `offset(yellow, Raul, k=1)`; `offset(Ben, Lucia, k=1)`; `lt(Tomas, green)`; `lt(orange, Lucia)`; `offset(black, Lucia, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Sara": [1, 2, 3, 4, 5], "Lucia": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5],
                "Raul": [1, 2, 3, 4, 5], "Ben": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5],
                "yellow": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "white": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Sara", "Lucia", "Tomas", "Raul", "Ben"]},
  {"type": "alldiff", "vars": ["green", "yellow", "orange", "black", "white"]},
  {"type": "eq", "a": "Raul", "b": "orange"},
  {"type": "offset", "a": "Raul", "b": "yellow", "k": 1},
  {"type": "neq", "a": "yellow", "b": 2},
  {"type": "alldiff", "vars": ["Sara", "black"]},
  {"type": "alldiff", "vars": ["Ben", "Lucia"]},
  {"type": "alldiff", "vars": ["Tomas", "green"]},
  {"type": "alldiff", "vars": ["black", "Lucia"]},
  {"type": "alldiff", "vars": ["Sara", "Raul"]},
  {"type": "alldiff", "vars": ["Lucia", "Ben"]},
  {"type": "alldiff", "vars": ["Tomas", "black"]},
  {"type": "alldiff", "vars": ["Raul", "Tomas"]},
  {"type": "alldiff", "vars": ["Raul", "Sara"]},
  {"type": "alldiff", "vars": ["Tomas", "Sara"]},
  {"type": "alldiff", "vars": ["Ben", "Sara"]},
  {"type": "alldiff", "vars": ["Ben", "Lucia"]},
  {"type": "alldiff", "vars": ["Ben", "Raul"]},
  {"type": "alldiff", "vars": ["Ben", "Tomas"]},
  {"type": "alldiff", "vars": ["Ben", "Sara"]},
  {"type": "alldiff", "vars": ["Ben", "Raul"]},
  {"type": "alldiff", "vars": ["Ben", "Tomas"]},
  {"type": "alldiff", "vars": ["Ben", "Lucia"]},
  {"type": "alldiff", "vars": ["Ben", "Sara"]},
  {"type": "alldiff", "vars": ["Ben", "Raul"]},
  {"type": "alldiff", "vars": ["Ben", "Tomas"]},
  {"type": "alldiff", "vars": ["Ben", "Sara"]},
  {"type": "alldiff", "vars": ["Ben", "Raul"]},
  {"type": "alldiff", "vars": ["Ben", "Tomas"]},
  {"type": "alldiff", "vars": ["Ben", "Lucia"]}
 ]}
```
</details>

### 176. L4-01 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Vera": 2, "blue": 2, "horse": 2, "hamster": 1, "bird": 3, "Elena": 4, "rabbit": 4, "fish": 5, "Gina": 5, "purple": 4, "black": 5, "Nora": 1, "orange": 1, "Paula": 3, "yellow": 3}`
- **Respuesta correcta:** `{"Nora": 5, "Elena": 4, "Vera": 3, "Gina": 1, "Paula": 2, "purple": 3, "black": 2, "orange": 5, "yellow": 1, "blue": 4, "horse": 4, "rabbit": 1, "bird": 3, "hamster": 5, "fish": 2}`
- **Restricciones inventadas (la verdad las viola):** `offset(Vera, hamster, k=1)`; `eq(Vera, blue)`; `offset(Gina, purple, k=1)`; `eq(Gina, black)`; `eq(Gina, black)`
- **Pistas perdidas:** `lt(Vera, hamster)`; `offset(blue, Vera, k=1)`; `lt(rabbit, purple)`; `offset(Paula, rabbit, k=1)`; `offset(black, Gina, k=1)`; `offset(Paula, Gina, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Nora": [1, 2, 3, 4, 5], "Elena": [1, 2, 3, 4, 5], "Vera": [1, 2, 3, 4, 5], "Gina": [1, 2, 3, 4, 5], "Paula": [1, 2, 3, 4, 5],
               "purple": [1, 2, 3, 4, 5], "black": [1, 2, 3, 4, 5], "orange": [1, 2, 3, 4, 5], "yellow": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5],
               "horse": [1, 2, 3, 4, 5], "rabbit": [1, 2, 3, 4, 5], "bird": [1, 2, 3, 4, 5], "hamster": [1, 2, 3, 4, 5], "fish": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Nora", "Elena", "Vera", "Gina", "Paula"]},
  {"type": "alldiff", "vars": ["purple", "black", "orange", "yellow", "blue"]},
  {"type": "alldiff", "vars": ["horse", "rabbit", "bird", "hamster", "fish"]},
  {"type": "eq", "a": "Nora", "b": "orange"},
  {"type": "offset", "a": "Vera", "b": "hamster", "k": 1},
  {"type": "eq", "a": "horse", "b": "blue"},
  {"type": "offset", "a": "Elena", "b": "bird", "k": 1},
  {"type": "eq", "a": "Vera", "b": "blue"},
  {"type": "eq", "a": "Nora", "b": "orange"},
  {"type": "offset", "a": "Gina", "b": "purple", "k": 1},
  {"type": "eq", "a": "Gina", "b": "black"},
  {"type": "eq", "a": "Gina", "b": "black"}
 ]}
```
</details>

### 177. L4-02 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"Hugo": 1, "Carla": 2, "cat": 2, "red": 2, "black": 3, "Omar": 3, "purple": 1, "Ana": 4, "Nora": 5, "rabbit": 3, "fish": 5, "dog": 4, "horse": 1, "green": 4, "yellow": 5}`
- **Respuesta correcta:** `{"Nora": 5, "Omar": 2, "Carla": 3, "Ana": 4, "Hugo": 1, "red": 3, "purple": 4, "black": 2, "green": 1, "yellow": 5, "cat": 3, "rabbit": 2, "fish": 5, "dog": 4, "horse": 1}`
- **Restricciones inventadas (la verdad las viola):** `next_to(green, yellow)`; `next_to(rabbit, dog)`
- **Restricciones invertidas:** `offset(black, Carla, k=1)`
- **Pistas perdidas:** `offset(Carla, black, k=1)`; `lt(Omar, cat)`; `lt(green, yellow)`; `lt(rabbit, dog)`; `lt(Ana, fish)`; `lt(Hugo, Omar)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {
    "Nora": [1, 2, 3, 4, 5],
    "Omar": [1, 2, 3, 4, 5],
    "Carla": [1, 2, 3, 4, 5],
    "Ana": [1, 2, 3, 4, 5],
    "Hugo": [1, 2, 3, 4, 5],
    "red": [1, 2, 3, 4, 5],
    "purple": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "cat": [1, 2, 3, 4, 5],
    "rabbit": [1, 2, 3, 4, 5],
    "fish": [1, 2, 3, 4, 5],
    "dog": [1, 2, 3, 4, 5],
    "horse": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Omar", "Carla", "Ana", "Hugo"]},
    {"type": "alldiff", "vars": ["red", "purple", "black", "green", "yellow"]},
    {"type": "alldiff", "vars": ["cat", "rabbit", "fish", "dog", "horse"]},
    {"type": "eq", "a": "Carla", "b": "red"},
    {"type": "eq", "a": "Carla", "b": "cat"},
    {"type": "offset", "a": "black", "b": "Carla", "k": 1},
    {"type": "alldiff", "vars": ["purple", "cat", "black"]},
    {"type": "next_to", "a": "purple", "b": "cat"},
    {"type": "alldiff", "vars": ["Omar", "cat"]},
    {"type": "next_to", "a": "Omar", "b": "cat"},
    {"type": "neq", "a": "Hugo", "b": 2},
    {"type": "next_to", "a": "green", "b": "yellow"},
    {"type": "next_to", "a": "rabbit", "b": "dog"},
    {"type": "alldiff", "vars": ["Ana", "fish"]},
    {"type": "next_to", "a": "Ana", "b": "fish"},
    {"type": "next_to", "a": "red", "b": "rabbit"},
    {"type": "alldiff", "vars": ["Hugo", "Omar"]}
  ]
}
'''
```
</details>

### 178. L4-09 · rep 4 (T=0.7) · Sub-restringido (varias soluciones, devolvió otra)

- **Detectable sin verdad:** sí (señal: `non_unique`)
- **Soluciones del modelo:** ≥2; devolvió `{"dog": 3, "Omar": 4, "carla": 2, "Ana": 3, "Jon": 1, "Tomas": 5, "blue": 3, "hamster": 2, "purple": 1, "fish": 4, "turtle": 5, "horse": 1, "red": 2, "orange": 4, "green": 5}`
- **Respuesta correcta:** `{"Omar": 4, "Ana": 3, "Tomas": 2, "Jon": 1, "Carla": 5, "orange": 5, "green": 4, "blue": 3, "purple": 1, "red": 2, "fish": 5, "hamster": 4, "dog": 3, "horse": 1, "turtle": 2}`
- **Restricciones inventadas (la verdad las viola):** `next_to(Ana, carla)`; `offset(Ana, carla, k=1)`; `next_to(Ana, fish)`; `next_to(Jon, carla)`; `next_to(Ana, fish)`; `next_to(purple, hamster)`; `next_to(dog, carla)`
- **Pistas perdidas:** `offset(fish, green, k=1)`; `lt(Ana, fish)`; `lt(dog, Carla)`; `offset(orange, hamster, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Omar": [1, 2, 3, 4, 5], "Ana": [1, 2, 3, 4, 5], "Tomas": [1, 2, 3, 4, 5],
                "Jon": [1, 2, 3, 4, 5], "carla": [1, 2, 3, 4, 5],
                "orange": [1, 2, 3, 4, 5], "green": [1, 2, 3, 4, 5], "blue": [1, 2, 3, 4, 5],
                "purple": [1, 2, 3, 4, 5], "red": [1, 2, 3, 4, 5], "fish": [1, 2, 3, 4, 5],
                "hamster": [1, 2, 3, 4, 5], "dog": [1, 2, 3, 4, 5], "horse": [1, 2, 3, 4, 5], "turtle": [1, 2, 3, 4, 5]},
 "constraints": [
  {"type": "alldiff", "vars": ["Omar", "Ana", "Tomas", "Jon", "carla"]},
  {"type": "alldiff", "vars": ["orange", "green", "blue", "purple", "red"]},
  {"type": "alldiff", "vars": ["fish", "hamster", "dog", "horse", "turtle"]},
  {"type": "neq", "a": "Jon", "b": "turtle"},
  {"type": "next_to", "a": "red", "b": "dog"},
  {"type": "neq", "a": "Tomas", "b": "purple"},
  {"type": "next_to", "a": "Omar", "b": "Ana"},
  {"type": "next_to", "a": "Omar", "b": "blue"},
  {"type": "next_to", "a": "Ana", "b": "carla"},
  {"type": "offset", "a": "Ana", "b": "carla", "k": 1},
  {"type": "next_to", "a": "Ana", "b": "fish"},
  {"type": "next_to", "a": "Jon", "b": "carla"},
  {"type": "next_to", "a": "Ana", "b": "fish"},
  {"type": "next_to", "a": "Omar", "b": "dog"},
  {"type": "next_to", "a": "purple", "b": "hamster"},
  {"type": "next_to", "a": "Ana", "b": "Omar"},
  {"type": "next_to", "a": "blue", "b": "hamster"},
  {"type": "next_to", "a": "dog", "b": "carla"}
 ]}
```
</details>

## Modelo válido del problema equivocado (11)

### 179. L1-04 · rep 1 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Nora": 2, "Dev": 1, "Raul": 3, "Sara": 4}`
- **Respuesta correcta:** `{"Nora": 3, "Dev": 4, "Sara": 1, "Raul": 2}`
- **Restricciones invertidas:** `offset(Nora, Dev, k=1)`; `offset(Raul, Nora, k=1)`; `offset(Sara, Raul, k=1)`
- **Pistas perdidas:** `lt(Nora, Dev)`; `offset(Nora, Raul, k=1)`; `lt(Sara, Raul)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Nora": [1, 2, 3, 4], "Dev": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Raul": [1, 2, 3, 4]},
  "constraints": [
    {"type": "alldiff", "vars": ["Nora", "Dev", "Sara", "Raul"]},
    {"type": "offset", "a": "Nora", "b": "Dev", "k": 1},
    {"type": "offset", "a": "Raul", "b": "Nora", "k": 1},
    {"type": "alldiff", "vars": ["Nora", "Sara"]},
    {"type": "offset", "a": "Sara", "b": "Raul", "k": 1}
  ]
}
'''
```
</details>

### 180. L1-08 · rep 1 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Raul": 4, "Carla": 3, "Omar": 2, "Kai": 1}`
- **Respuesta correcta:** `{"Raul": 2, "Omar": 3, "Kai": 4, "Carla": 1}`
- **Restricciones inventadas (la verdad las viola):** `offset(Carla, Omar, k=1)`
- **Restricciones invertidas:** `offset(Omar, Kai, k=1)`
- **Pistas perdidas:** `lt(Carla, Omar)`; `lt(Omar, Kai)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Raul": [1, 2, 3, 4], "Omar": [1, 2, 3, 4], "Kai": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Omar", "Kai", "Carla"]},
    {"type": "offset", "a": "Carla", "b": "Omar", "k": 1},
    {"type": "offset", "a": "Raul", "b": "Carla", "k": 1},
    {"type": "offset", "a": "Omar", "b": "Kai", "k": 1}
  ]
}
'''
```
</details>

### 181. L2-07 · rep 1 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Carla": 3, "white": 3, "green": 2, "Gina": 4, "Nora": 2, "Lucia": 1, "black": 1, "blue": 4}`
- **Respuesta correcta:** `{"Gina": 3, "Carla": 2, "Nora": 4, "Lucia": 1, "green": 1, "white": 3, "black": 2, "blue": 4}`
- **Restricciones inventadas (la verdad las viola):** `eq(Carla, white)`
- **Restricciones invertidas:** `offset(green, black, k=1)`
- **Pistas perdidas:** `offset(white, Carla, k=1)`; `offset(black, green, k=1)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Gina": [1, 2, 3, 4], "Carla": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Lucia": [1, 2, 3, 4],
                 "green": [1, 2, 3, 4], "white": [1, 2, 3, 4], "black": [1, 2, 3, 4], "blue": [1, 2, 3, 4]},
  "constraints": [
    {"type": "alldiff", "vars": ["Gina", "Carla", "Nora", "Lucia"]},
    {"type": "alldiff", "vars": ["green", "white", "black", "blue"]},
    {"type": "eq", "a": "Carla", "b": "white"},
    {"type": "offset", "a": "Carla", "b": "green", "k": 1},
    {"type": "neq", "a": "Carla", "b": 1},
    {"type": "next_to", "a": "Nora", "b": "white"},
    {"type": "lt", "a": "Carla", "b": "Gina"},
    {"type": "offset", "a": "green", "b": "black", "k": 1}
  ]
}
'''
```
</details>

### 182. L1-02 · rep 2 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Nora": 3, "Raul": 2, "Elena": 1, "Hugo": 4}`
- **Respuesta correcta:** `{"Raul": 1, "Nora": 3, "Hugo": 4, "Elena": 2}`
- **Restricciones invertidas:** `offset(Raul, Elena, k=1)`
- **Pistas perdidas:** `offset(Elena, Raul, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Raul": [1, 2, 3, 4], "Nora": [1, 2, 3, 4], "Hugo": [1, 2, 3, 4], "Elena": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Raul", "Nora", "Hugo", "Elena"]},
  {"type": "eq", "a": "Nora", "b": 3},
  {"type": "offset", "a": "Raul", "b": "Elena", "k": 1}
 ]}
```
</details>

### 183. L1-04 · rep 2 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Nora": 2, "Dev": 1, "Raul": 3, "Sara": 4}`
- **Respuesta correcta:** `{"Nora": 3, "Dev": 4, "Sara": 1, "Raul": 2}`
- **Restricciones invertidas:** `offset(Nora, Dev, k=1)`; `offset(Raul, Nora, k=1)`; `offset(Sara, Raul, k=1)`
- **Pistas perdidas:** `lt(Nora, Dev)`; `offset(Nora, Raul, k=1)`; `lt(Sara, Raul)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Nora": [1, 2, 3, 4], "Dev": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Raul": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Nora", "Dev", "Sara", "Raul"]},
  {"type": "offset", "a": "Nora", "b": "Dev", "k": 1},
  {"type": "offset", "a": "Raul", "b": "Nora", "k": 1},
  {"type": "offset", "a": "Sara", "b": "Raul", "k": 1}
 ]}
```
</details>

### 184. L2-05 · rep 2 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Omar": 3, "Carla": 4, "Paula": 1, "Ana": 2, "orange": 3, "purple": 4, "yellow": 1, "black": 2}`
- **Respuesta correcta:** `{"Omar": 3, "Ana": 2, "Carla": 4, "Paula": 1, "yellow": 4, "purple": 1, "black": 2, "orange": 3}`
- **Restricciones invertidas:** `lt(yellow, purple)`
- **Pistas perdidas:** `lt(purple, yellow)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Omar": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Carla": [1, 2, 3, 4], "Paula": [1, 2, 3, 4],
                "yellow": [1, 2, 3, 4], "purple": [1, 2, 3, 4], "black": [1, 2, 3, 4], "orange": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Omar", "Ana", "Carla", "Paula"]},
  {"type": "alldiff", "vars": ["yellow", "purple", "black", "orange"]},
  {"type": "neq", "a": "Paula", "b": 2},
  {"type": "neq", "a": "Ana", "b": "purple"},
  {"type": "eq", "a": "Omar", "b": 3},
  {"type": "lt", "a": "yellow", "b": "purple"},
  {"type": "neq", "a": "yellow", "b": 2},
  {"type": "lt", "a": "Omar", "b": "Carla"},
  {"type": "neq", "a": "orange", "b": 4},
  {"type": "lt", "a": "Ana", "b": "orange"}
 ]}
```
</details>

### 185. L1-04 · rep 3 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Nora": 2, "Raul": 3, "Dev": 4, "Sara": 1}`
- **Respuesta correcta:** `{"Nora": 3, "Dev": 4, "Sara": 1, "Raul": 2}`
- **Restricciones invertidas:** `offset(Raul, Nora, k=1)`
- **Pistas perdidas:** `offset(Nora, Raul, k=1)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Nora": [1, 2, 3, 4], "Dev": [1, 2, 3, 4], "Sara": [1, 2, 3, 4], "Raul": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Nora", "Dev", "Sara", "Raul"]},
  {"type": "lt", "a": "Nora", "b": "Dev"},
  {"type": "offset", "a": "Raul", "b": "Nora", "k": 1},
  {"type": "lt", "a": "Sara", "b": "Raul"}
 ]}
```
</details>

### 186. L3-10 · rep 3 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Sara": 2, "black": 2, "Lucia": 3, "white": 3, "Ben": 4, "Raul": 5, "Tomas": 1, "green": 1, "yellow": 4, "orange": 5}`
- **Respuesta correcta:** `{"Sara": 5, "Lucia": 3, "Tomas": 1, "Raul": 2, "Ben": 4, "green": 5, "yellow": 3, "orange": 2, "black": 4, "white": 1}`
- **Restricciones inventadas (la verdad las viola):** `eq(Sara, black)`; `neq(Raul, 2)`; `eq(Tomas, green)`; `eq(Lucia, white)`; `next_to(Sara, 1)`
- **Restricciones invertidas:** `offset(Raul, yellow, k=1)`; `offset(Lucia, black, k=1)`
- **Pistas perdidas:** `lt(black, Sara)`; `offset(yellow, Raul, k=1)`; `lt(Tomas, green)`; `lt(orange, Lucia)`; `offset(black, Lucia, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Sara": [1, 2, 3, 4, 5],
    "Lucia": [1, 2, 3, 4, 5],
    "Tomas": [1, 2, 3, 4, 5],
    "Raul": [1, 2, 3, 4, 5],
    "Ben": [1, 2, 3, 4, 5],
    "green": [1, 2, 3, 4, 5],
    "yellow": [1, 2, 3, 4, 5],
    "orange": [1, 2, 3, 4, 5],
    "black": [1, 2, 3, 4, 5],
    "white": [1, 2, 3, 4, 5]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Sara", "Lucia", "Tomas", "Raul", "Ben"]},
    {"type": "alldiff", "vars": ["green", "yellow", "orange", "black", "white"]},
    {"type": "eq", "a": "Sara", "b": "black"},
    {"type": "offset", "a": "Raul", "b": "yellow", "k": 1},
    {"type": "neq", "a": "Raul", "b": 2},
    {"type": "eq", "a": "Raul", "b": "orange"},
    {"type": "next_to", "a": "Lucia", "b": "Ben"},
    {"type": "eq", "a": "Tomas", "b": "green"},
    {"type": "offset", "a": "Lucia", "b": "black", "k": 1},
    {"type": "eq", "a": "Lucia", "b": "white"},
    {"type": "next_to", "a": "Sara", "b": 1}
  ]
}
```
</details>

### 187. L1-02 · rep 4 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Nora": 3, "Raul": 2, "Elena": 1, "Hugo": 4}`
- **Respuesta correcta:** `{"Raul": 1, "Nora": 3, "Hugo": 4, "Elena": 2}`
- **Restricciones invertidas:** `offset(Raul, Elena, k=1)`
- **Pistas perdidas:** `offset(Elena, Raul, k=1)`

<details><summary>Salida del modelo</summary>

```
{
  "variables": {
    "Raul": [1, 2, 3, 4],
    "Nora": [1, 2, 3, 4],
    "Hugo": [1, 2, 3, 4],
    "Elena": [1, 2, 3, 4]
  },
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Nora", "Hugo", "Elena"]},
    {"type": "eq", "a": "Nora", "b": 3},
    {"type": "offset", "a": "Raul", "b": "Elena", "k": 1}
  ]
}
```
</details>

### 188. L1-08 · rep 4 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Raul": 4, "Carla": 3, "Omar": 2, "Kai": 1}`
- **Respuesta correcta:** `{"Raul": 2, "Omar": 3, "Kai": 4, "Carla": 1}`
- **Restricciones inventadas (la verdad las viola):** `offset(Carla, Omar, k=1)`
- **Restricciones invertidas:** `offset(Omar, Kai, k=1)`
- **Pistas perdidas:** `lt(Carla, Omar)`; `lt(Omar, Kai)`

<details><summary>Salida del modelo</summary>

```
'''json
{
  "variables": {"Raul": [1, 2, 3, 4], "Omar": [1, 2, 3, 4], "Kai": [1, 2, 3, 4], "Carla": [1, 2, 3, 4]},
  "constraints": [
    {"type": "alldiff", "vars": ["Raul", "Omar", "Kai", "Carla"]},
    {"type": "offset", "a": "Carla", "b": "Omar", "k": 1},
    {"type": "offset", "a": "Raul", "b": "Carla", "k": 1},
    {"type": "offset", "a": "Omar", "b": "Kai", "k": 1}
  ]
}
'''
```
</details>

### 189. L2-05 · rep 4 (T=0.7) · Modelo válido del problema equivocado

- **Detectable sin verdad:** no
- **Soluciones del modelo:** 1; devolvió `{"Omar": 3, "Carla": 4, "Paula": 1, "Ana": 2, "purple": 1, "yellow": 3, "orange": 4, "black": 2}`
- **Respuesta correcta:** `{"Omar": 3, "Ana": 2, "Carla": 4, "Paula": 1, "yellow": 4, "purple": 1, "black": 2, "orange": 3}`
- **Restricciones inventadas (la verdad las viola):** `lt(yellow, 4)`
- **Pistas perdidas:** `neq(orange, 4)`

<details><summary>Salida del modelo</summary>

```
{"variables": {"Omar": [1, 2, 3, 4], "Ana": [1, 2, 3, 4], "Carla": [1, 2, 3, 4], "Paula": [1, 2, 3, 4],
                "yellow": [1, 2, 3, 4], "purple": [1, 2, 3, 4], "black": [1, 2, 3, 4], "orange": [1, 2, 3, 4]},
 "constraints": [
  {"type": "alldiff", "vars": ["Omar", "Ana", "Carla", "Paula"]},
  {"type": "alldiff", "vars": ["yellow", "purple", "black", "orange"]},
  {"type": "eq", "a": "Omar", "b": 3},
  {"type": "neq", "a": "Paula", "b": 2},
  {"type": "neq", "a": "Ana", "b": 3},
  {"type": "offset", "a": "Ana", "b": "purple", "k": 1},
  {"type": "lt", "a": "yellow", "b": 4},
  {"type": "neq", "a": "yellow", "b": 2},
  {"type": "lt", "a": "Omar", "b": "Carla"},
  {"type": "neq", "a": "Ana", "b": 4},
  {"type": "lt", "a": "Ana", "b": "orange"}
 ]}
```
</details>

## Fallas que sobrevivieron al refinamiento (B′, 189)

| Problema | Rep | Categoría | Detectable | Rondas |
|---|---|---|---|---|
| L1-02 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-04 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-05 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L1-06 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L1-07 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-08 | 0 | Modelo válido del problema equivocado | no | 1 |
| L1-09 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-10 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-01 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 2 |
| L2-02 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-03 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-04 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-06 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L2-07 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-08 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-09 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-10 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L3-01 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L3-02 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L3-03 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L3-04 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-05 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L3-06 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-07 | 0 | Alcance / aridad | sí | 3 |
| L3-08 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L3-09 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-10 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L4-01 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L4-02 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-03 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-04 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L4-05 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L4-06 | 0 | Alcance / aridad | sí | 3 |
| L4-07 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L4-08 | 0 | Alcance / aridad | sí | 3 |
| L4-09 | 0 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-10 | 0 | Sobre-restringido (sin solución) | sí | 3 |
| L1-02 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-04 | 1 | Modelo válido del problema equivocado | no | 0 |
| L1-05 | 1 | Sintaxis mala (no parsea) | sí | 3 |
| L1-06 | 1 | Modelo válido del problema equivocado | no | 1 |
| L1-07 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-08 | 1 | Modelo válido del problema equivocado | no | 0 |
| L1-09 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-10 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-01 | 1 | Alcance / aridad | sí | 3 |
| L2-02 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-03 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 2 |
| L2-04 | 1 | Modelo válido del problema equivocado | no | 3 |
| L2-06 | 1 | Sobre-restringido (sin solución) | sí | 3 |
| L2-07 | 1 | Modelo válido del problema equivocado | no | 0 |
| L2-08 | 1 | Alcance / aridad | sí | 3 |
| L2-09 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-10 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-01 | 1 | Sobre-restringido (sin solución) | sí | 3 |
| L3-02 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-03 | 1 | Sobre-restringido (sin solución) | sí | 3 |
| L3-04 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-05 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-06 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-07 | 1 | Modelo válido del problema equivocado | sí | 3 |
| L3-08 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-09 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-10 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 2 |
| L4-01 | 1 | Sintaxis mala (no parsea) | sí | 3 |
| L4-02 | 1 | Sobre-restringido (sin solución) | sí | 3 |
| L4-03 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 3 |
| L4-04 | 1 | Sobre-restringido (sin solución) | sí | 3 |
| L4-05 | 1 | Alcance / aridad | sí | 3 |
| L4-06 | 1 | Alcance / aridad | sí | 3 |
| L4-07 | 1 | Sobre-restringido (sin solución) | sí | 3 |
| L4-08 | 1 | Sobre-restringido (sin solución) | sí | 3 |
| L4-09 | 1 | Sobre-restringido (sin solución) | sí | 3 |
| L4-10 | 1 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-02 | 2 | Modelo válido del problema equivocado | no | 0 |
| L1-04 | 2 | Modelo válido del problema equivocado | no | 0 |
| L1-05 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-06 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 2 |
| L1-07 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-08 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-09 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-10 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-01 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L2-02 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-03 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 2 |
| L2-04 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-05 | 2 | Modelo válido del problema equivocado | no | 0 |
| L2-06 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-07 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-08 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L2-09 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-10 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L3-01 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L3-02 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L3-03 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L3-04 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-05 | 2 | Sintaxis mala (no parsea) | sí | 3 |
| L3-06 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-07 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L3-08 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L3-09 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-10 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L4-01 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L4-02 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-03 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-04 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L4-05 | 2 | Alcance / aridad | sí | 3 |
| L4-06 | 2 | Alcance / aridad | sí | 3 |
| L4-07 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L4-08 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L4-09 | 2 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-10 | 2 | Sobre-restringido (sin solución) | sí | 3 |
| L1-02 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-03 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-04 | 3 | Modelo válido del problema equivocado | no | 0 |
| L1-05 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L1-06 | 3 | Modelo válido del problema equivocado | no | 1 |
| L1-07 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-08 | 3 | Modelo válido del problema equivocado | no | 1 |
| L1-09 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-10 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-01 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-02 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-03 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-04 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L2-05 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L2-06 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L2-07 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-08 | 3 | Alcance / aridad | sí | 1 |
| L2-09 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-01 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L3-02 | 3 | Alcance / aridad | sí | 3 |
| L3-03 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L3-04 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-05 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-06 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-07 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L3-08 | 3 | Alcance / aridad | sí | 0 |
| L3-09 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-10 | 3 | Modelo válido del problema equivocado | no | 0 |
| L4-01 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L4-02 | 3 | Sintaxis mala (no parsea) | sí | 3 |
| L4-03 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-04 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L4-05 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L4-06 | 3 | Alcance / aridad | sí | 3 |
| L4-07 | 3 | Sobre-restringido (sin solución) | sí | 3 |
| L4-08 | 3 | Alcance / aridad | sí | 3 |
| L4-09 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-10 | 3 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-01 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-02 | 4 | Modelo válido del problema equivocado | no | 0 |
| L1-04 | 4 | Alcance / aridad | sí | 3 |
| L1-05 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-06 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L1-07 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-08 | 4 | Modelo válido del problema equivocado | no | 0 |
| L1-09 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L1-10 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-01 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L2-02 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-03 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-04 | 4 | Sobre-restringido (sin solución) | sí | 3 |
| L2-05 | 4 | Modelo válido del problema equivocado | no | 0 |
| L2-06 | 4 | Sobre-restringido (sin solución) | sí | 3 |
| L2-07 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-08 | 4 | Alcance / aridad | sí | 3 |
| L2-09 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L2-10 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L3-01 | 4 | Sobre-restringido (sin solución) | sí | 3 |
| L3-02 | 4 | Sobre-restringido (sin solución) | sí | 3 |
| L3-03 | 4 | Sobre-restringido (sin solución) | sí | 3 |
| L3-04 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-05 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L3-06 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-07 | 4 | Alcance / aridad | sí | 2 |
| L3-08 | 4 | Alcance / aridad | sí | 3 |
| L3-09 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L3-10 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-01 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-02 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-03 | 4 | Modelo válido del problema equivocado | sí | 1 |
| L4-04 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 1 |
| L4-05 | 4 | Modelo válido del problema equivocado | sí | 1 |
| L4-06 | 4 | Sobre-restringido (sin solución) | sí | 3 |
| L4-07 | 4 | Sobre-restringido (sin solución) | sí | 3 |
| L4-08 | 4 | Sobre-restringido (sin solución) | sí | 3 |
| L4-09 | 4 | Sub-restringido (varias soluciones, devolvió otra) | sí | 0 |
| L4-10 | 4 | Sobre-restringido (sin solución) | sí | 3 |
