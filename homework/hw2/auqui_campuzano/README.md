# Homework 2 — The Formalizer

**Equipo:** Giuliana Auqui y Felipe Campuzano  
**Formalismo:** CSP (graph coloring)  

## Ejecución (3 comandos)

Requisitos: Python 3.10+, `matplotlib`. Solver y harness usan solo la biblioteca estándar.

```bash
# 1) Credenciales de CUALQUIER endpoint compatible con OpenAI. Ejemplo Groq (modelo pequeño: produce fallos, que alimentan la taxonomía):
export OPENAI_API_KEY="..."
export OPENAI_BASE_URL="https://api.groq.com/openai/v1"
export MODEL_NAME="llama-3.1-8b-instant"      # nombre exacto
export MODEL_PROVIDER="Groq"; export MODEL_SIZE="8B"
export TEMPERATURE=0.7                         # >0 para que las repeticiones midan varianza

# 2) Experimento: 20 problemas x (A, B, B', C) x 3 repeticiones. Respuestas cacheadas en .llm_cache/
python code/run_experiment.py --repeats 3

# 3) Tablas, taxonomy.md, figuras y REPORT.md (sobrescribe el marcador)
python code/analyze.py
```

Antes de ejecutar el paso 3, complete `results/pricing.csv` con la tarifa publicada (USD por millón de tokens, entrada/salida) del modelo usado, o exporte `PRICE_IN_PER_M` y `PRICE_OUT_PER_M`; si no, el informe reporta tokens por respuesta correcta y no inventa costos. Si hubo errores de red, repita el paso 2 (lo ya cacheado no se vuelve a pagar). Para un modelo local, apunte `OPENAI_BASE_URL` a su servidor (p. ej. Ollama/llama.cpp `http://localhost:11434/v1`).

Verificaciones: `python code/validate_dataset.py` (ground truth vs. texto) y `python tests/test_pipeline.py` (prueba del pipeline con LLM simulado; no genera resultados).

B y B′ comparten el primer intento (misma caché). B′ permite hasta 3 intentos; el único feedback es el mensaje del parser/solver, junto con la salida previa del modelo. Nunca se envía el ground truth.

## Dataset

20 instancias de coloreo de grafos, 6 fáciles, 7 medias y 7 difíciles. La dificultad se operacionaliza mediante número de variables, restricciones binarias y pistas de color fijas. Cada JSON incluye el enunciado, modelo CSP construido manualmente, testigo de solución y métricas.

## Costos

El harness registra tokens (entrada y salida por separado) y tiempos. Para calcular costo monetario por respuesta correcta se debe completar `results/pricing.csv` con la tarifa real del proveedor/modelo usado (USD por millón de tokens de entrada/salida) y separar tokens de entrada/salida si el proveedor los reporta. No se debe atribuir un precio inventado.

## Integridad experimental

No se incluyen respuestas simuladas ni resultados de un modelo no ejecutado. Antes de entregar, ejecutar con un modelo real, conservar el nombre/tamaño del modelo y completar el informe y la taxonomía con las salidas reales.
