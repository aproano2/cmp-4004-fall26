# Brazos B y B′

Ollama debe estar ejecutándose por separado con `qwen2.5:3b`. No se instala ni inicia otro servidor.

```bash
python -m pytest code/test_arm_b.py -q
python code/arm_b.py F01 --out results/pilot_f01.jsonl
python code/arm_b.py --out results/arm_b_raw.jsonl
python code/evaluate_b.py results/arm_b_raw.jsonl
```

El piloto y la ejecución completa comparten la caché `.llm_cache/`. Los archivos de salida no se
sobrescriben: escoja otro nombre para cada ejecución. El JSONL guarda la salida literal y el resultado
del solver por intento. El evaluador, separado del runner, lee ground truth y genera `arm_b.csv` y
`arm_b_refined.csv`; no ejecuta el modelo. La categoría de error se deja vacía para revisión manual.
Costos sin tarifa aparecen vacíos, no como cero. Para calcular USD especifique `--input-price` y
`--output-price`, ambos en USD por millón de tokens, y registre fuente y fecha en el informe.

**Acuerdo para C:** mismo `statement` y `answer_format` público, `qwen2.5:3b` Q4_K_M, temperatura 0,
semilla 0, máximo 4096 tokens de salida y una ejecución por problema. Se pueden usar máquinas Ollama
independientes; registrar hardware, versión de Ollama y digest del modelo en ambos equipos. C responde
directamente, sin solver. No enviar dificultad, modelos manuales ni respuestas de referencia a ningún LLM.

B′ reutiliza exactamente la primera respuesta de B y recibe únicamente el mensaje de error del parser
o del solver, además del historial previo. Hay hasta tres refinamientos después del primer intento.
Se reintenta solo tras `spec_error` o `unsat`; `multiple` se registra y se devuelve la primera solución,
y timeout no se reintenta. Un fallo de conexión se registra por separado, no se presenta como fallo CSP.
La caché conserva la duración original de inferencia; `wall_s` suma los tiempos originales de cada
intento más su procesamiento, y no incluye carga inicial ni la escritura del archivo de resultados.
Con semilla fija no se mide la variabilidad entre generaciones; repetir con distintas semillas y
temperatura positiva en archivos separados si el equipo decide medirla.
