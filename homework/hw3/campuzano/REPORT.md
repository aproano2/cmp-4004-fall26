# HW3 — Optimización: metaheurísticas, comparación justa y brazo LLM

**Autores:** Giuliana Auqui y Felipe Campuzano · **Código:** `code/` · **Datos crudos:** `results/*.csv` · **Figuras:** `fig/` · **Uso de IA:** `AI_LOG.md`

## 1. Qué se implementó

**Oficiales** (`swarm.py`, semana 11, sin modificar): `Budget`, PSO y ABC (continuo), ACO (TSP). **Propios**, desde cero con numpy (`code/algorithms.py`): GA, SA, PSO-Clerc, ACO-MMAS, ABC para permutaciones y los baselines.

| Clase | Algoritmos |
|---|---|
| Continuo (Rastrigin, Rosenbrock; D = 2, 10, 30) | PSO y ABC oficiales; GA (BLX-0.5, torneo, elitismo) y SA (enfriamiento ligado al presupuesto) propios; PSO-Clerc propio (inercia constante, el que se sintoniza en §4–5) |
| Combinatorio (TSP 20, 30, 50 ciudades, una instancia fija por tamaño) | ACO oficial (y su ablación **β = 0**, sin visibilidad); GA (OX + inversión), SA (2-opt), ACO-MMAS y ABC (swap/inserción) propios |
| Baselines obligatorios | Random search (RS); continuo: hill climbing con reinicios; TSP: vecino más cercano + 2-opt (con ILS al agotar arranques) |

**Protocolo.** Se usa el `Budget` **oficial** (subclase mínima que solo añade `batch`, que llama a su propio `__call__`): cuenta cada evaluación de una solución completa y lanza excepción al llegar al tope; un `assert` verifica que *todas* las corridas usaron exactamente el tope. Topes: 5 000 / 25 000 / 75 000 evaluaciones para D = 2 / 10 / 30 y 1 000·n para TSP (20 000 / 30 000 / 50 000). **20 seeds** por configuración (el mínimo pedido era 10). Se reportan media ± std y mediana [Q1–Q3]; contrastes Mann-Whitney unilaterales frente a RS. Las 1 320 corridas están en `results/main_final.csv` y `results/main_convergence.csv`. Hiperparámetros por defecto fijados *a priori* con valores de la literatura, sin modificarlos tras ver resultados.

## 2. Duel Scorecard

Mediana del mejor valor final en 20 seeds (menor es mejor). Tablas completas (media ± std, IQR, p-valores): `results/summary_tables.md`.

| Problema | Presupuesto | Ganador | Mejor metaheurística | Baseline específico | RS | ¿Meta. vence al baseline específico? |
|---|---|---|---|---|---|---|
| Rastrigin D2 | 5 000 | ABC = PSO oficiales (0) | 0 | HC 3·10⁻¹¹ | 0.86 | sí (p < 10⁻⁸) |
| Rastrigin D10 | 25 000 | ABC oficial (3·10⁻¹⁴) | ABC | HC 29.4 | 63.4 | sí |
| Rastrigin D30 | 75 000 | ABC oficial (2·10⁻⁸) | ABC | HC 155 | 331 | sí |
| Rosenbrock D2 | 5 000 | PSO oficial (3·10⁻¹⁰) | PSO | HC 7·10⁻⁵ | 5·10⁻³ | sí |
| Rosenbrock D10 | 25 000 | **HC (0.116)** | ABC 0.895 | HC 0.116 | 147 | **no** |
| Rosenbrock D30 | 75 000 | **HC (11.0)** | PSO-Clerc 19.0 | HC 11.0 | 2 731 | **no** |
| TSP 20 | 20 000 | ACO ≈ MMAS ≈ NN+2-opt (3.668) | ACO | 3.668 | 6.29 | **no** (empate) |
| TSP 30 | 30 000 | MMAS ≈ NN+2-opt (4.736) | MMAS 4.736 (ACO oficial 4.76) | 4.736 | 10.9 | **no** (empate) |
| TSP 50 | 50 000 | **NN+2-opt (6.047)** | MMAS 6.058 (ACO oficial 6.19) | 6.047 | 19.8 | **no** |

**Resultados que hay que decir en voz alta**

1. **El baseline específico del problema iguala o gana a toda metaheurística en 5 de 9 instancias** (Rosenbrock D10 y D30 con claridad, y los tres TSP). Una metaheurística solo se justifica con claridad en Rastrigin y Rosenbrock D2.
2. **Random search no es competitivo en casi ningún lado** (último en las 9 instancias por mediana). Pero hay una excepción cercana: en **Rosenbrock D2** (5 000 evals) RS no es distinguible de ABC oficial (p = 0.11) y SA solo lo supera marginalmente (p = 0.043). En 2 dimensiones con presupuesto generoso, RS es un rival serio. Además, **el ACO oficial sin visibilidad (β = 0) es casi RS** (18.5 vs 19.8 en TSP 50).
3. **NN+2-opt es determinista** hasta agotar sus n arranques: las 20 "seeds" dan el mismo valor (std = 0).
4. **PSO oficial (inercia 0.9→0.4) supera a mi PSO-Clerc en Rastrigin** (5.5 vs 7.5 en D10; 44.8 vs 70.1 en D30) **pero pierde en Rosenbrock D10 y D30** (3.2 vs 1.5; 22.7 vs 19.0).

## 3. Convergencia (x = evaluaciones, bandas = IQR en 20 seeds)

`fig/conv_rastrigin.png`, `fig/conv_rosenbrock.png`, `fig/conv_tsp.png` (más `fig/final_boxplots.png` con las distribuciones finales). Lecturas principales:

- **Rastrigin:** ABC oficial avanza como los demás hasta ~5·10³ evaluaciones y entonces cae varios órdenes de magnitud en una ventana corta ("escalón"). GA mejora de forma más suave pero se queda en 1–4.
- **TSP:** NN+2-opt y ACO (oficial y MMAS) arrancan en niveles que los demás tardan 10³–10⁴ evaluaciones en alcanzar, porque usan las distancias desde el inicio. GA, SA y ABC los alcanzan en n = 20 y 30, no en n = 50.
- **ACO oficial con β = 0** termina en 18.5 en TSP 50, 3× peor que con β = 2 (6.19) y a ~1.3 de RS (19.8): sin distancias, la feromona sola casi no aporta en este presupuesto.

## 4. Estudio de hiperparámetros (PSO-Clerc propio en Rastrigin D10, 25 000 evals)

Grid 4 × 4 sobre tamaño de enjambre n y inercia w (c₁ = c₂ = 1.496; se usa mi PSO-Clerc porque el oficial trae un calendario de inercia), 5 seeds por celda (seeds 100–104). Heatmap: `fig/heatmap_pso.png`; datos: `results/hyperparam_grid_pso.csv`. Error final medio:

| n \ w | 0.3 | 0.5 | 0.7 | 0.9 |
|---|---|---|---|---|
| 10 | 14.4 | 18.5 | 15.1 | 13.1 |
| 20 | 18.2 | 12.5 | 9.9 | 21.3 |
| 40 | 15.7 | 8.8 | 8.2 | 18.1 |
| 80 | 11.9 | 8.0 | 9.2 | 22.0 |

- **Importó w:** promediando sobre n, el error va de 15.1 (w = 0.3) a 10.6 (0.7) y sube a 18.6 (0.9): una cresta estrecha, mal resuelta por un grid grueso. Valores bajos estancan al enjambre en un mínimo local; 0.9 no llega a converger en el presupuesto.
- **Importó poco n:** promedios por fila 15.3 / 15.5 / 12.7 / 12.8 para n = 10 / 20 / 40 / 80; solo n ≤ 20 se queda corto.
- **Ruido:** la std por celda va de 1.1 a 8.7; (40, 0.7) da 8.2 en el grid pero (40, 0.73) dio 4.2 con las mismas seeds. No hay que sobreinterpretar una celda.
- Ni la mejor configuración hallada en §5 (n = 40, w = 0.8, error ≈ 3–4.5) se acerca a ABC (0): **el mal desempeño de PSO en Rastrigin no se explica solo por parámetros por defecto**. De hecho, el PSO oficial sin afinar (5.4 en D10) rinde parecido al PSO-Clerc afinado por el LLM (4.5 en test).

## 5. Brazo LLM — opción B (LLM como sintonizador de hiperparámetros)

**Por qué B.** A exige muchas llamadas al modelo y un evaluador robusto ante código que se cuelga; no hay clave de API, y B permite definir limpiamente el presupuesto igual.

**Cómo se hizo (limitación importante).** No había acceso por API, así que el "LLM" es *Claude dentro de esta misma sesión*, que actuó como sintonizador en 4 rondas × 4 configuraciones = 16 configuraciones: en cada ronda recibió el historial (error final y curva de convergencia por configuración) y propuso las 4 siguientes con una justificación. Prompts y respuestas están en `.llm_cache/`. Tras integrar el `Budget` oficial se reevaluaron las 16 propuestas cacheadas (`llm_round.py K --replay`) y se reprodujeron las mismas cifras; el tuning se hizo con el Budget propio previo. El espacio (n ∈ [5, 100], w ∈ [0.1, 1.0]) y las seeds de entrenamiento (100–104) son idénticos para los tres métodos.

**Definición de presupuesto igual (y su defensa).** La unidad es **una configuración evaluada = 5 corridas × 25 000 evaluaciones = 125 000 evaluaciones de la función objetivo**. Los tres métodos tienen 16 configuraciones = 2.0 M de evaluaciones. Una llamada al LLM no equivale a una evaluación, así que tokens y tiempo del modelo se contabilizan *aparte*. Defensa: el coste dominante es el cómputo de las corridas; la desventaja es que ignora que el LLM cuesta más por configuración.

**Resultados** (`fig/tuning_llm_random_grid.png`, `results/tuning_*.csv`):

| Método | Mejor error medio (entrenamiento, 5 seeds) | Config. elegida → error en TEST (20 seeds no vistas, 200–219) |
|---|---|---|
| Default PSO-Clerc (n = 40, w = 0.7298) | — | 6.02 |
| Grid 4 × 4 | 7.96 | (80, 0.5) → 10.00 |
| Random (30 repeticiones de 16 configs) | mediana 4.39 | media de medias 6.06 |
| **LLM (1 trayectoria)** | **3.18** | (40, 0.80) → **4.52** |

- En entrenamiento el LLM supera a la mediana de random y a grid, pero **en seeds no vistas la ventaja se encoge**: 4.52 frente a 6.02 del default (p = 0.095, no significativo), y **un 33 % de las repeticiones de random elige una configuración mejor en test que la del LLM**. El paso de 3.18 a 4.52 es la *maldición del ganador* (se elige el mejor de 16 medias ruidosas).
- **El LLM tiene una sola trayectoria**: no se estima su varianza. La conclusión honesta es "no hay evidencia de que supere a random search".
- Grid pierde porque su rejilla no contiene la cresta estrecha w ≈ 0.8. El LLM usó las curvas pero también **conocimiento previo** de PSO, que random no tiene.

**Costes.** Evaluación de las 16 configuraciones: 2.0 s de reloj (4 rondas de 0.4–0.6 s). El historial y las propuestas guardados suman ~19 KB (≈ 5 000 tokens visibles); contando razonamiento no guardado estimo 10 000–15 000 tokens en total (**estimación, no medición**). Reloj del modelo no medido. Tasa de compilación/fallos de código: **no aplica** (la opción B no genera código; 0 candidatos descartados).

**Interpretabilidad.** El vector (n, w) ya es legible, así que la ventaja del LLM sobre un tuner numérico es modesta; aporta una narrativa. Explicación *post hoc* (mía, no verificada) de por qué w ≈ 0.8 funcionó: con c₁ = c₂ = 1.496 la estabilidad de segundo orden de PSO exige c₁ + c₂ < 24(1−w²)/(7−5w). En w = 0.73 el límite es ≈ 3.34 (> 2.99): enjambre estable, colapsa pronto (~4.2). En w = 0.80 y 0.83 es ≈ 2.88 y 2.62 (< 2.99): queda algo inestable, conserva varianza y explora más (3.2 y 3.4). En w = 0.88 (≈ 2.1) no converge en el presupuesto (12.5). Los mejores w quedan justo pasada la frontera de estabilidad, pero con 5 seeds por punto es una hipótesis, no una prueba.

## 6. Declaración No Free Lunch

| Estructura del problema | Quién encajó | Por qué (propiedades del problema) |
|---|---|---|
| **Rastrigin: separable y multimodal** | **ABC oficial** (error ≈ 0 en D = 2, 10, 30) | ABC modifica **una sola coordenada** por candidato y acepta de forma voraz: en una función separable cada coordenada se optimiza casi independientemente, así que la dimensión deja de ser un problema. **Control:** con Rastrigin rotada (misma multimodalidad, ya no separable; `results/extra_rotated_rastrigin_final.csv`), ABC pasa de ≈ 0 a una media de 29.5 en D = 10 (198.5 en D = 30) y **GA lidera** (9.3 y 57.5), con los PSO segundos (14–16 y 64–71). La ventaja de ABC era la separabilidad, no la multimodalidad. |
| **Rosenbrock: valle estrecho, no separable, unimodal en la práctica** | **Hill climbing con regla 1/5** | Un valle curvo se sigue bien con adaptación del tamaño de paso; GA y SA, con pasos de distribución fija o enfriados a ciegas, rinden peor (≈ 7 vs 0.12 en D10; ABC oficial 0.9). |
| **TSP: discreto, con estructura métrica (vecindad geométrica)** | **NN + 2-opt y ACO (MMAS / oficial)** | Ambos usan la matriz de distancias para construir la solución (vecino más cercano / visibilidad 1/d). GA, ABC y SA deben redescubrir esa estructura con evaluaciones y quedan por detrás en n = 50. |

## 7. Dónde podemos haber sido injustos

- **Definición de presupuesto.** Cada candidato de 2-opt cuenta como una evaluación completa; con evaluación delta, NN+2-opt haría órdenes de magnitud más trabajo por evaluación, así que mi regla *perjudica* a ese baseline, que aun así empata con los mejores. El reloj no entra en la comparación y en el brazo LLM los tokens no se restan del presupuesto (§5).
- **Quién fue afinado más.** Solo se estudió PSO-Clerc (grid + sintonizador). Los demás usaron defaults (los de `swarm.py` para los oficiales; elegidos a priori para los míos), sin tocarlos tras ver resultados. El tuning no se usó para rehacer la comparación principal. El PSO oficial ajusta su inercia al presupuesto (`iters_hint`), como mi SA con su enfriamiento: ambos conocen el tope de evaluaciones.
- **Propios vs oficiales.** Mi ACO-MMAS (límites de feromona, depósito del mejor) es más fuerte que el ACO oficial (Ant System); lo hace ver mejor que "el" ACO. El ACO oficial tarda ~10× más en reloj (Python puro) y eso no entra en la comparación.
- **Baselines.** El hill climbing lleva regla 1/5 para el paso, más fuerte que uno simple, lo que lo favorece (y explica su victoria en Rosenbrock). NN+2-opt con ILS es determinista (std = 0): las 20 seeds no aportan varianza.
- **Una sola instancia de TSP por tamaño y una sola rotación** en el control.
- **Contaminación menor:** antes del tuning vi un resultado de PSO-Clerc por defecto con una seed (12.9), y el LLM conoce la configuración clásica de PSO. El LLM tiene una sola trayectoria y solo 5 seeds de entrenamiento.

## 8. ¿Ganaron su lugar las metáforas biológicas?

En su mayoría **no**: los resultados se explican por la estructura de la información, no por hormigas ni abejas. ACO venció a ABC en TSP (6.19 oficial / 6.06 MMAS frente a 6.59 en n = 50), pero la ablación muestra la causa: **el ACO oficial sin visibilidad (β = 0) llega a 18.5, casi igual que random search (19.8) y muy por debajo de ABC**. Lo que daba la ventaja a ACO no era la feromona (la "memoria" colectiva) sino el término 1/d, que inyecta la geometría del problema, es decir, la misma idea que el vecino más cercano; y por eso ACO y NN+2-opt quedan empatados. A su vez, mi ABC para TSP no es "social": sin combinación entre fuentes se reduce a 20 escaladores con abandono, y rinde como SA/GA. En Rastrigin, ABC oficial ganó porque su operador mueve una coordenada a la vez (separabilidad), no por el forrajeo; la rotación lo demuestra. Hay una conexión parcial con la memoria: la feromona agrega información de muchas soluciones en una distribución sobre aristas, mientras que ABC guarda solo soluciones completas; con β > 0 esa memoria ayuda a refinar. Con estos datos, lo que hizo ganar a cada algoritmo fueron operadores adaptados a una propiedad del problema (separabilidad, métrica, valle), no la historia de sus nombres.

## 9. Límites

20 seeds dan potencia para diferencias grandes, no pequeñas (ACO vs NN+2-opt en TSP 50); p-valores sin corrección por comparaciones múltiples; el brazo LLM es una trayectoria con Claude en el bucle y los tokens son estimados.
