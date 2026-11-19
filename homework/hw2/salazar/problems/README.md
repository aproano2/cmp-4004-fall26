# Dataset del HW2 · The Formalizer

Preparamos 21 problemas originales en inglés, con siete por nivel. Usamos tres familias en cada nivel. En **Einstein** asignamos posiciones a elementos de distintas categorías. En **horario** ordenamos actividades en franjas exclusivas. En **coloreo** asignamos tres colores a regiones conectadas por aristas.

Medimos la dificultad por el número de variables del CSP: fácil hasta 8, medio de 9 a 15 y difícil desde 16. Las llamadas al solver se incluyen como dato descriptivo, ya que también dependen de los dominios y de cómo se propagan las restricciones.

En `verificacion_manual` de cada JSON dejamos la deducción del `gold` a partir de las pistas. En Einstein fijamos posiciones y completamos cada categoría por orden y descarte. En horario ordenamos bloques consecutivos y ocupamos las franjas restantes. En coloreo partimos de dos colores fijados y buscamos regiones con dos vecinos de colores distintos. Luego ejecutamos `python code/verificar_dataset.py` para comprobar la solución única de cada modelo y su coincidencia con el `gold`. El brazo A resolvió correctamente las tres repeticiones de cada problema (63/63) con `python code/brazo_a.py`.

## Métricas del verificador

| ID | Nivel | Familia | Variables | Restricciones | Llamadas |
|---|---|---|---:|---:|---:|
| facil-01 | facil | einstein | 6 | 6 | 7 |
| facil-02 | facil | horario | 6 | 6 | 8 |
| facil-03 | facil | coloreo | 6 | 11 | 7 |
| facil-04 | facil | einstein | 8 | 10 | 9 |
| facil-05 | facil | horario | 8 | 9 | 9 |
| facil-06 | facil | coloreo | 8 | 18 | 9 |
| facil-07 | facil | einstein | 6 | 7 | 10 |
| medio-01 | medio | einstein | 12 | 15 | 13 |
| medio-02 | medio | horario | 12 | 13 | 20 |
| medio-03 | medio | coloreo | 12 | 27 | 13 |
| medio-04 | medio | einstein | 15 | 16 | 17 |
| medio-05 | medio | horario | 15 | 15 | 71 |
| medio-06 | medio | coloreo | 15 | 34 | 16 |
| medio-07 | medio | einstein | 12 | 14 | 13 |
| dificil-01 | dificil | einstein | 20 | 23 | 21 |
| dificil-02 | dificil | horario | 20 | 21 | 40 |
| dificil-03 | dificil | coloreo | 20 | 45 | 21 |
| dificil-04 | dificil | einstein | 25 | 27 | 27 |
| dificil-05 | dificil | horario | 25 | 25 | 6427 |
| dificil-06 | dificil | coloreo | 25 | 56 | 26 |
| dificil-07 | dificil | einstein | 25 | 28 | 26 |
