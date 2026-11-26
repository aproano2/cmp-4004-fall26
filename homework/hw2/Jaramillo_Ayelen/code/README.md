# Duelo 2 — The Formalizer (CSP): cómo correrlo

```
python -m pytest code/tests -q          # 19 tests
python code/verify_problems.py          # la verdad del banco, por fuerza bruta (~30 s)
python code/run_all.py                  # los 4 brazos con Ollama (qwen2.5:3b)
python code/analyze.py                  # CSV de resumen, taxonomy.md y fig/*.png
```

## Archivos

| Archivo | Qué es |
|---|---|
| `problems/problems.json` | los 40 problemas: texto, pistas, modelo a mano (brazo A) y respuesta única |
| `problems/PROBLEMS.md` | los mismos 40 problemas para leer, con su respuesta |
| `problems/verification.txt` | salida de `verify_problems.py` |
| `code/csp_solver.py` | solver de la semana 6 generalizado (MRV + forward checking + conteo de soluciones) |
| `code/spec.py` | formato JSON del CSP, parser y validador (errores de sintaxis / esquema / alcance) |
| `code/generate_problems.py` | genera el banco con semillas fijas |
| `code/verify_problems.py` | verificación independiente por fuerza bruta |
| `code/llm.py` | cliente de Ollama con caché |
| `code/arms.py` | brazos A, B, B′ y C, prompts y bucle de refinamiento |
| `code/taxonomy.py` | clasificación de cada falla del brazo B |
| `code/run_all.py`, `code/analyze.py`, `code/plots.py` | corrida, análisis y figuras |


