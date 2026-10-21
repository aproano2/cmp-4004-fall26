# BFS con costos no uniformes

BFS devolvió un camino más caro que el óptimo (UCS) en 33 de 40 grillas. En el 8-puzzle, donde todo paso cuesta 1, el sobrecosto de BFS fue 0 en 40 de 40 instancias: BFS es óptimo solo cuando los costos son uniformes.

| nivel | grillas | BFS subóptimo | sobrecosto mediano (cuando lo hay) |
|---|---|---|---|
| 5×5 | 10 | 5 | 2 |
| 8×8 | 10 | 10 | 7.5 |
| 12×12 | 10 | 8 | 11.5 |
| 16×16 | 10 | 10 | 15 |

## La instancia que mostramos: `grid-12-09`

BFS usa 11 pasos y cuesta 32; UCS usa 11 pasos y cuesta 11 (+21, 191 % más caro). BFS minimiza el número de pasos y no mira el terreno; UCS minimiza el costo acumulado. Costos al entrar: `.`=1, `,`=3, `~`=8.

**BFS** — `DDDDDDRRRRR`

```
. , , . . . , . . , , .
. , ~ , , , . . . . . ,
. ~ . S . . . ~ . , . .
. . , * . . . . . . . .
. . . * . , . . , . . .
. , . * ~ , . . . ~ , ~
~ . ~ * . , , , . . . ~
. ~ . * . . , ~ . . . ~
. . . * * * * * G , . ,
, . , . . . ~ . , . . .
. ~ . . . ~ , . . . , .
. , . . . . . . , ~ ~ .
```

**UCS (óptimo)** — `DRRRDDRRDDD`

```
. , , . . . , . . , , .
. , ~ , , , . . . . . ,
. ~ . S . . . ~ . , . .
. . , * * * * . . . . .
. . . . . , * . , . . .
. , . ~ ~ , * * * ~ , ~
~ . ~ ~ . , , , * . . ~
. ~ . ~ . . , ~ * . . ~
. . . . . . . . G , . ,
, . , . . . ~ . , . . .
. ~ . . . ~ , . . . , .
. , . . . . . . , ~ ~ .
```
