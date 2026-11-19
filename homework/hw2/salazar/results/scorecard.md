# Duel Scorecard

| Eje | A · a mano | B · híbrido | B′ · refinamiento | C · directo |
|---|---|---|---|---|
| 1 Correctness | 63/63 (100 %) | 3/63 (5 %) | 6/63 (10 %) | 3/63 (5 %) |
| 2 Guarantee | Correcta y única si el modelo a mano es fiel (el solver es completo). | Correcta y única si la traducción es fiel; ninguna sobre la traducción. | Igual que B; solo corrige lo que el solver ve. | Ninguna; no hay certificado. |
| 3 Cost | 0 tokens | 40027 tokens/correcta | 101881 tokens/correcta | 10471 tokens/correcta |
| 4 Latency | mediana 0.00 s · p95 0.00 s | mediana 12.32 s · p95 77.79 s | mediana 46.54 s · p95 300.00 s | mediana 7.49 s · p95 13.42 s |
| 5 Reproducibility | 1.00 respuestas distintas por problema; 21/21 estables | 1.95 respuestas distintas por problema; 3/21 estables | 1.86 respuestas distintas por problema; 6/21 estables | 2.62 respuestas distintas por problema; 3/21 estables |
| 6 Scaling | facil 100 % → medio 100 % → dificil 100 % | facil 14 % → medio 0 % → dificil 0 % | facil 24 % → medio 5 % → dificil 0 % | facil 14 % → medio 0 % → dificil 0 % |
| 7 Interpretability | Total: modelo JSON revisable. | Alta: el modelo JSON es un certificado; se ve qué pista falló. | Alta, más la traza de mensajes del solver. | Baja: solo una asignación final. |
| 8 Failure mode | sin fallos | sintaxis 34, sobre_restringido 11, aridad_alcance 9, sub_restringido 3 · **detectables sin gold: 60/60** | sintaxis 18, sobre_restringido 15, aridad_alcance 14, sub_restringido 4 · **detectables sin gold: 54/57** | incorrecta 46, incompleta 14 · **detectables sin gold: 14/60** |
