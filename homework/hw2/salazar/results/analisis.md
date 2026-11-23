# Análisis para el REPORT

## Refinamiento (B')

- B: 3/63 (5 %) · B': 6/63 (10 %) · delta = 3 instancias

| Iteraciones hasta acertar | Instancias |
|---|---|
| 1 | 2 |
| 2 | 2 |
| 3 | 1 |
| 4 | 1 |
| nunca convergió | 57 |

- Primer error de los que el refinamiento arregló: {'': 1, 'sintaxis': 3}
- Primer error de los que sobrevivieron 3 rondas con un error visible: {'sintaxis': 29, 'aridad_alcance': 9, 'sobre_restringido': 10, 'sub_restringido': 3}

## Detectabilidad: B vs C

| Brazo | Fallos | Detectables sin gold | Silenciosos |
|---|---|---|---|
| B | 60 | 60 | 0 |
| C | 60 | 14 | 46 |

- Errores de C por tipo: {'incorrecta': 46, 'incompleta': 14} (detectable según {'sin_formato': 'si', 'incompleta': 'si', 'incorrecta': 'no', 'no_termina': 'si'})