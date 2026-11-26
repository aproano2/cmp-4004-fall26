
**rastrigin_D10** (presupuesto 25000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| ABC (oficial) | 1.73e-11 ± 6.98e-11 | 2.84e-14 [1.42e-14–1.92e-13] | 3.2e-08 |
| GA (propio) | 0.94 ± 0.775 | 1.05 [0.27–1.29] | 3.4e-08 |
| PSO (oficial) | 5.37 ± 2.69 | 5.47 [2.98–6.96] | 3.3e-08 |
| PSO-Clerc (propio) | 7.91 ± 3.45 | 7.46 [4.97–9.95] | 3.4e-08 |
| SA (propio) | 11.4 ± 6.1 | 8.7 [6.72–14.7] | 3.4e-08 |
| Hill climb + reinicios | 28.5 ± 9.26 | 29.4 [21.1–35.1] | 3.4e-08 |
| Random search | 63 ± 7.79 | 63.4 [58.7–67.6] | — |

**rastrigin_D2** (presupuesto 5000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| ABC (oficial) | 0 ± 0 | 0 [0–0] | 4.0e-09 |
| PSO (oficial) | 0 ± 0 | 0 [0–0] | 4.0e-09 |
| PSO-Clerc (propio) | 9.12e-11 ± 2.21e-10 | 5.9e-12 [1.18e-12–3.02e-11] | 3.4e-08 |
| Hill climb + reinicios | 0.448 ± 0.508 | 3.05e-11 [3.75e-13–0.995] | 3.3e-03 |
| SA (propio) | 0.2 ± 0.382 | 1.26e-06 [4.39e-07–0.101] | 1.3e-05 |
| GA (propio) | 0.0039 ± 0.00452 | 0.00273 [0.000749–0.00514] | 3.4e-08 |
| Random search | 0.904 ± 0.53 | 0.861 [0.609–1.19] | — |

**rastrigin_D30** (presupuesto 75000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| ABC (oficial) | 0.00186 ± 0.00831 | 1.58e-08 [1.53e-09–3.4e-07] | 3.4e-08 |
| GA (propio) | 4.24 ± 1.63 | 4.34 [3.44–5.46] | 3.4e-08 |
| PSO (oficial) | 48.6 ± 14.5 | 44.8 [39.3–54.5] | 3.4e-08 |
| PSO-Clerc (propio) | 69.3 ± 17.8 | 70.1 [62.7–81.6] | 3.4e-08 |
| SA (propio) | 78 ± 17.3 | 77.1 [64.4–87.1] | 3.4e-08 |
| Hill climb + reinicios | 156 ± 19.6 | 155 [145–166] | 3.4e-08 |
| Random search | 329 ± 12.7 | 331 [321–339] | — |

**rosenbrock_D10** (presupuesto 25000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| Hill climb + reinicios | 0.711 ± 1.46 | 0.116 [0.101–0.138] | 3.4e-08 |
| ABC (oficial) | 1.33 ± 1.13 | 0.895 [0.494–1.69] | 3.4e-08 |
| PSO-Clerc (propio) | 2.56 ± 2.39 | 1.54 [1.33–2.2] | 3.4e-08 |
| PSO (oficial) | 3.56 ± 1.54 | 3.2 [3.09–3.61] | 3.4e-08 |
| GA (propio) | 6.4 ± 1 | 6.73 [6.17–6.99] | 3.4e-08 |
| SA (propio) | 7.28 ± 1.27 | 7.14 [6.74–7.82] | 3.4e-08 |
| Random search | 153 ± 40.5 | 147 [124–187] | — |

**rosenbrock_D2** (presupuesto 5000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| PSO (oficial) | 1.27e-08 ± 3.64e-08 | 2.78e-10 [2.74e-11–1.59e-09] | 3.4e-08 |
| PSO-Clerc (propio) | 3.44e-07 ± 1.12e-06 | 2.42e-08 [1e-08–1.66e-07] | 3.4e-08 |
| GA (propio) | 0.000283 ± 0.000463 | 6.85e-05 [3.83e-05–0.000181] | 2.3e-07 |
| Hill climb + reinicios | 0.000375 ± 0.00093 | 7.2e-05 [3.32e-05–0.00013] | 2.0e-07 |
| SA (propio) | 0.00473 ± 0.00552 | 0.0023 [0.000193–0.00797] | 4.3e-02 |
| ABC (oficial) | 0.00781 ± 0.011 | 0.00288 [0.000756–0.0112] | 1.1e-01 |
| Random search | 0.00854 ± 0.0097 | 0.00519 [0.00189–0.0123] | — |

**rosenbrock_D30** (presupuesto 75000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| Hill climb + reinicios | 11 ± 3.09 | 11 [10.4–11.6] | 3.4e-08 |
| PSO-Clerc (propio) | 19.1 ± 0.865 | 19 [18.6–19.2] | 3.4e-08 |
| ABC (oficial) | 20.2 ± 4.1 | 20.6 [19.1–22] | 3.4e-08 |
| PSO (oficial) | 27.6 ± 19.7 | 22.7 [22.3–23.3] | 3.4e-08 |
| GA (propio) | 31.5 ± 16.6 | 27.2 [26.5–27.4] | 3.4e-08 |
| SA (propio) | 33.3 ± 16.9 | 28.3 [26.6–29.4] | 3.4e-08 |
| Random search | 2744 ± 367 | 2731 [2666–2989] | — |

**tsp_20** (presupuesto 20000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| ACO (oficial) | 3.67 ± 0 | 3.67 [3.67–3.67] | 4.0e-09 |
| ACO-MMAS (propio) | 3.67 ± 0.00298 | 3.67 [3.67–3.67] | 9.8e-09 |
| NN + 2-opt (ILS) | 3.67 ± 0 | 3.67 [3.67–3.67] | 4.0e-09 |
| ABC perm. (propio) | 3.68 ± 0.0108 | 3.67 [3.67–3.68] | 2.5e-08 |
| GA (propio) | 3.7 ± 0.0562 | 3.68 [3.67–3.7] | 3.1e-08 |
| SA (propio) | 3.68 ± 0.0111 | 3.68 [3.68–3.7] | 3.1e-08 |
| ACO oficial β=0 | 5.89 ± 0.192 | 5.93 [5.78–6.01] | 1.0e-05 |
| Random search | 6.24 ± 0.214 | 6.29 [6.15–6.39] | — |

**tsp_30** (presupuesto 30000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| ACO-MMAS (propio) | 4.74 ± 0.00833 | 4.74 [4.74–4.74] | 1.9e-08 |
| NN + 2-opt (ILS) | 4.74 ± 0 | 4.74 [4.74–4.74] | 4.0e-09 |
| SA (propio) | 4.79 ± 0.0968 | 4.76 [4.75–4.78] | 3.2e-08 |
| ACO (oficial) | 4.76 ± 0.00447 | 4.76 [4.75–4.76] | 2.7e-08 |
| GA (propio) | 4.82 ± 0.108 | 4.77 [4.76–4.87] | 3.4e-08 |
| ABC perm. (propio) | 4.81 ± 0.063 | 4.77 [4.77–4.87] | 3.4e-08 |
| ACO oficial β=0 | 10.2 ± 0.269 | 10.2 [10–10.5] | 1.7e-07 |
| Random search | 10.9 ± 0.222 | 10.9 [10.7–11.1] | — |

**tsp_50** (presupuesto 50000 evals, 20 seeds)

| Algoritmo | media ± std | mediana [Q1–Q3] | p vs RS |
|---|---|---|---|
| NN + 2-opt (ILS) | 6.05 ± 0 | 6.05 [6.05–6.05] | 4.0e-09 |
| ACO-MMAS (propio) | 6.07 ± 0.0456 | 6.06 [6.02–6.1] | 3.2e-08 |
| SA (propio) | 6.19 ± 0.0855 | 6.17 [6.12–6.22] | 3.4e-08 |
| ACO (oficial) | 6.19 ± 0.0557 | 6.19 [6.14–6.22] | 3.4e-08 |
| GA (propio) | 6.33 ± 0.152 | 6.29 [6.22–6.42] | 3.4e-08 |
| ABC perm. (propio) | 6.56 ± 0.186 | 6.59 [6.44–6.68] | 3.4e-08 |
| ACO oficial β=0 | 18.5 ± 0.537 | 18.5 [18.2–18.9] | 1.0e-06 |
| Random search | 19.6 ± 0.461 | 19.8 [19.4–19.9] | — |
