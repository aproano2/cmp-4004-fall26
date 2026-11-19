# AI usage log

- Se utilizó ChatGPT para apoyar la planificación del experimento, estructurar el repositorio, redactar documentación inicial y generar código de apoyo.
- El dataset de 20 instancias se construyó programáticamente; cada instancia incluye un modelo CSP y un testigo de solución para validación.
- El código del solver, el harness y los datos deben ser revisados y ejecutados por los integrantes antes de la entrega.
- Registrar aquí cualquier uso adicional de IA, incluyendo modelo, fecha, propósito y prompts relevantes.
- No se han fabricado respuestas de LLM, ejemplos verbatim, métricas ni costos: todo proviene de la ejecución real; el costo en USD usa una tarifa proxy declarada.

## Revisión y completado del entregable (Claude, Anthropic)
- Fecha: 2026-11-17. Modelo: Claude Sonnet 5.5 (claude.ai). Propósito: auditar el paquete y completar el harness. Los autores deben revisar el código antes de entregar.
- Hallazgos corregidos: (1) las pistas de color de los enunciados difíciles estaban en inglés dentro de prompts en español (red/green/blue) → ahora rojo/verde/azul; (2) `llm.py` sin caché, sin reintentos y sin separar tokens de entrada/salida; (3) el reintento de B′ no enviaba la salida previa del modelo; (4) la taxonomía no distinguía sub-/sobre-restricción, alcance/aridad ni premisas omitidas/alucinadas; (5) `validate_dataset.py` no comprobaba el ground truth contra el texto del enunciado; (6) faltaban repeticiones (varianza), análisis, figuras y generación del informe.
- Se probó el pipeline con un LLM **simulado** (`tests/test_pipeline.py`) solo para verificar el código; esos datos **no** son resultados experimentales y no se guardaron en `results/`.
- No se ha fabricado ninguna respuesta de LLM, métrica, costo ni ejemplo verbatim.
- Ejecución real (2026-11-17): modelo allam-2-7b vía Groq (el modelo llama-3.1-8b-instant ya no existía en la cuenta), 3 repeticiones, temperatura 0.7. Las respuestas del modelo están en `.llm_cache/` y `results/per_instance.csv`.
- Corrección posterior (Claude): el evaluador del brazo C rechazaba claves en minúsculas ("r1") y tomaba solo hasta el primer objeto JSON; se corrigió y se re-puntuó desde la caché (C: 17 % -> 35 %). La recomendación del informe se cambió de B′ a B porque los datos mostraron que B′ no rescata ninguna ejecución.
- `REPORT.md`, `taxonomy.md`, `results/*.csv` y `fig/*.png` se generan con `code/analyze.py` a partir de los datos reales; los autores deben revisar y, si lo creen necesario, editar el texto.
