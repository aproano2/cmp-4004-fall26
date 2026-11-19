# Experimento de tamaño: qwen2.5:3b contra qwen2.5:7b

| Modelo | Brazo | Correctas | Fácil / Medio / Difícil | Fallos | Detectables sin gold | Silenciosos |
|---|---|---|---|---|---|---|
| 3B | B | 3/63 | 3 / 0 / 0 (de 21 c/u) | 60 | 60 | 0 |
| 3B | B′ | 6/63 | 5 / 1 / 0 (de 21 c/u) | 57 | 54 | 3 |
| 3B | C | 3/63 | 3 / 0 / 0 (de 21 c/u) | 60 | 14 | 46 |
| 7B | B | 22/63 | 13 / 6 / 3 (de 21 c/u) | 41 | 41 | 0 |
| 7B | B′ | 26/63 | 15 / 8 / 3 (de 21 c/u) | 37 | 37 | 0 |
| 7B | C | 3/63 | 3 / 0 / 0 (de 21 c/u) | 60 | 6 | 54 |

- Fallos de B con 3B: {'sobre_restringido': 11, 'sintaxis': 34, 'aridad_alcance': 9, 'sub_restringido': 3, 'no_termina': 3}
- Fallos de B′ con 3B: {'problema_errado': 3, 'sintaxis': 18, 'aridad_alcance': 14, 'sobre_restringido': 15, 'sub_restringido': 4, 'no_termina': 3}
- Fallos de B con 7B: {'sobre_restringido': 21, 'aridad_alcance': 13, 'sub_restringido': 3, 'sintaxis': 1, 'no_termina': 3}
- Fallos de B′ con 7B: {'aridad_alcance': 12, 'sobre_restringido': 20, 'sub_restringido': 2, 'no_termina': 3}
