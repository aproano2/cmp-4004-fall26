# AI_LOG

Registro de asistencia con IA y ejecución experimental. Las notas de revisión del 16 de noviembre describen el estado del proyecto en esa fecha; la ejecución real se completó posteriormente.

- Herramienta: ChatGPT para asistencia en diseño, estructura y depuración del código.
- Modelo experimental: Ollama `qwen2.5:3b`, 3.1B, Q4_K_M, identificador `357c53fb659c` (detalles en `REPORT.md`, §1).
- Formalismo: SAT / CNF.
- Dominio: coloreado de grafos con tres colores.
- Intervención humana: revisión del dataset y ground truth, ejecución local, comprobación de resultados y redacción/revisión del análisis.
- Se ejecutó el experimento real y se guardaron los resultados en `results/`.


## Revisión asistida (Claude, 2026-11-16)
Se pidió a Claude revisar y mejorar el proyecto. Qué se hizo (todo verificable en el código y en los tests offline):
- **Correcciones de instrumentación:** la caché devolvía `llm_time_s = 0` (rompía tiempos y coste de B′) y cacheaba errores de red; ahora conserva la latencia original, no cachea errores e incluye semilla/num_predict/num_ctx en la clave.
- **Bucle de refinamiento:** el fallo de decodificación (SAT pero vértice con ≠1 color) ahora produce feedback en vez de detener el bucle; se guarda la traza de cada intento; timeout también se reintenta.
- **Prompt:** mapa explícito vértice→índice y color→índice; ejemplo de formato sin `...`; `extract_json` robusto.
- **Taxonomía:** separa fallos anunciados de silenciosos, añade diff de cláusulas (premisas omitidas / aristas alucinadas) y marca los aciertos «por las razones equivocadas».
- **Protocolo:** varias corridas con semillas, IC de Wilson, McNemar exacto, coste por respuesta correcta (precios como parámetro, no inventados), 6 figuras y `taxonomy.md` autogenerado.
- **Tests:** consistencia prompt↔datos, oráculo de backtracking independiente, solver vs. fuerza bruta (600 CNF), y un test de pipeline con un LLM *simulado* que inyecta fallos conocidos.
- **Estado al 2026-11-16:** en el entorno de Claude no se ejecutó el modelo real porque no había Ollama. Los tests con LLM simulado no se consideran resultados experimentales. La ejecución local real se realizó después (véase sección siguiente).


## Ejecución y análisis posterior (2026-11-18)
- **Ejecución real:** experimento local con Ollama `qwen2.5:3b` en MacBook Air M4 (16 GB), con 20 instancias, tres semillas (0, 1, 2) y cuatro brazos: 240 evaluaciones en total.
- **Resultados observados:** A 60/60, B 0/60, B′ 0/60 y C 22/60. B′ realizó 172 intentos en total.
- **Evidencia:** `results/metrics.csv`, `results/records.jsonl`, `results/bprime_traces.json`, `results/scorecard.md`, `results/taxonomy.json`, `taxonomy.md` y seis gráficos en `fig/`.
- **Asistencia de ChatGPT:** apoyo en la interpretación de los resultados, revisión de consistencia y preparación de los archivos de entrega. Las cifras se tomaron de los resultados generados por el experimento, no de respuestas inventadas por el asistente.
- **Responsabilidad humana:** revisar los resultados y figuras, construir el reporte y las conclusiones, conservar el código y las salidas reales, y la entrega de archivos.
