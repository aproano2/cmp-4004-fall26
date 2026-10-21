# Corrida descartada: dos procesos a la vez contra Ollama (4 de octubre)

Al cambiar cómo clasificamos las respuestas que no terminan (`no_termina`), detuvimos la primera corrida del brazo LLM. El script se detuvo, pero el proceso de Python que había lanzado siguió corriendo. Durante unos 25 minutos hubo **dos corridas a la vez** contra el mismo servidor de Ollama, y el proceso viejo clasificaba con la versión anterior del código.

Con dos procesos, el modelo responde más lento. Aparecen timeouts que una sola corrida no habría tenido y las latencias guardadas quedan infladas. Por eso estos datos **no** se usan en el reporte. Los conservamos como registro del proceso.

| Archivo | Contenido |
|---|---|
| `llm_cache/` | las 21 respuestas que se guardaron en la caché ese día (texto del modelo y latencia medida con dos procesos) |
| `llm_calls.jsonl` | registro de llamadas de ambos procesos mezclados |
| `consola_mezclada.log` | salida de consola, con las líneas de los dos procesos intercaladas |

La corrida oficial se repitió desde cero con un solo proceso. Antes de lanzarla comprobamos que no hubiera otro proceso de Python usando Ollama.
