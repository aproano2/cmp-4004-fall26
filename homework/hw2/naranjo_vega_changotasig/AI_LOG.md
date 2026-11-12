# AI_LOG.md — Homework 2: The Formalizer

Registro de uso de IA según [`resources/ai-policy.md`](../../../resources/ai-policy.md): se registra cada intervención importante de un asistente de IA en el trabajo entregado. El campo **¿Lo entendí?** es el que se califica.

El uso del LLM **como sujeto del experimento** en los brazos B, B′ y C se documenta en `REPORT.md` y `.llm_cache/`, no aquí. Cada integrante registra el uso de IA correspondiente a su trabajo.

---

## Integrante 1 — Diego Changotasig

| N.º y actividad | Herramienta | ¿Qué pedí? | ¿Qué obtuve? | ¿Qué hice con ello? | ¿Lo entendí? |
|---|---|---|---|---|---|
| **1. Dataset: 20 problemas CSP** | Claude (Claude Opus 5.5) | Crear 20 problemas industriales (7 fáciles, 7 intermedios y 6 difíciles), cada uno con enunciado, variables, dominios, restricciones, solución única y deducción. Separar los problemas públicos de las respuestas. | Claude generó los 20 enunciados y modelos, ajustó sus restricciones con un solucionador hasta obtener soluciones únicas y redactó las deducciones. Se guardaron en `ground_truth.json` y en los archivos exportados. | Revisé manualmente los 20 problemas, sus restricciones y sus soluciones. | **Sí.** Entiendo cómo representar un problema mediante variables, dominios y restricciones. Por ejemplo, en D16, si P1 va a L1, P8 debe ir a L3 y el par P2–P5 no cabe en ninguna línea; por eso se descarta esa alternativa. Al comprobar las capacidades y las demás restricciones se obtiene una única asignación. |
| **2. Solucionador CSP** | Claude (Claude Opus 5.5) | Crear un solucionador compatible con los conceptos de la semana 6, pero capaz de manejar restricciones industriales más variadas. | Claude desarrolló `code/csp_spec.py` y un formato JSON que admite `alldiff`, `count`, `implies` y comparaciones. El solucionador utiliza backtracking, MRV, desempate por grado, consistencia de nodo y forward checking limitado. No utiliza AC-3. | Ejecuté los scripts en VS Code con Python 3.12.7 y comprobé su funcionamiento. | **Sí.** MRV selecciona la variable con menos valores disponibles. El forward checking implementado descarta valores cuando a una restricción solo le queda una variable por asignar; no propaga todas las restricciones como AC-3. Las expresiones se validan antes de evaluarlas para impedir que se ejecute código arbitrario generado por el LLM. |
| **3. Exportación y verificación** | Claude (Claude Opus 5.5) | Separar los enunciados de las soluciones de referencia y crear una forma de verificar los problemas automáticamente. | Claude escribió `export_problem_files.py`, que genera los archivos públicos, `formulations.md` y las métricas de dificultad, y `verify_ground_truth.py`, que comprueba soluciones con backtracking y fuerza bruta, revisa la cobertura de reglas y detecta datos privados en los archivos públicos. | Ejecuté ambos scripts: se exportaron 20 problemas y los 20 pasaron la verificación, registrada en `results/ground_truth_check.csv`. | **Sí.** La verificación automática prueba que una solución cumple **las restricciones escritas** y que es única, pero no que esas restricciones representen correctamente el enunciado. Por eso también hice una revisión manual. |
| **4. Revisión manual del ground truth** | ChatGPT | Pedir un procedimiento para revisar cada problema y ayuda para comprender restricciones, deducciones y las notas de revisión. | Recibí una guía para comparar cada regla con su expresión | Revisé los 20 problemas y marqué `manual_review: "OK"` con mi nombre y una nota por caso. No modifiqué sus modelos ni soluciones. | **Sí.** Comprobé que las condiciones en lenguaje natural coincidan con las expresiones. |
| **5. Brazo A y formato común de resultados** | Claude (Claude Opus 5.5) | Generar el programa del brazo A, registrar sus resultados y definir un formato común para comparar los brazos del experimento. | Claude creó `code/arm_a.py` y `code/results_schema.py`. | Ejecute el brazo A y obtuvo 20/20 respuestas correctas, con tiempos calculados como mediana de cinco repeticiones. También probe la clasificación de respuestas correctas, incorrectas y sin respuesta | **Sí.** El brazo A parte de modelos y respuestas de referencia ya verificados; por eso su 100 % de acierto es esperable «por construcción». Su utilidad es comprobar que el solucionador y la evaluación funcionan, y servir como punto de referencia para B, B′ y C; no demuestra que un LLM sepa formular correctamente los problemas. |
| **6. Estructura de `REPORT.md` y `AI_LOG.md`** | ChatGPT (primeros borradores) y Claude (revisión de estructura) | Pedir un formato para `REPORT.md` y `AI_LOG.md` conforme a la tarea, con mi contribución documentada y espacios para los resultados de mis compañeros. | ChatGPT preparó borradores del informe y del registro de IA. Después, Claude reorganizó `REPORT.md` en las siete secciones, incorporó los resultados del brazo A y dejó pendientes los resultados de B, B′ y C. También ajustó `AI_LOG.md` para registrar con más precisión qué produjo cada herramienta. | Utilicé esos borradores como base. | **Sí.** `REPORT.md` explica el método, las comparaciones y los resultados del proyecto; `AI_LOG.md` deja constancia de qué pedí a la IA, qué generó y qué comprobé yo. |

---

## Integrante 2 — [nombre]

[Pendiente: entradas de los brazos B y B′, con el mismo formato.]

## Integrante 3 — [nombre]

[Pendiente: entradas del brazo C, la evaluación, las figuras y la taxonomía, con el mismo formato.]

---

## Criterios que seguimos con la IA (Integrante 1)

1. Ningún prompt de los brazos B, B′ o C incluye `problems/ground_truth/` (modelos, soluciones ni deducciones). Los LLM solo reciben `problems/public/problems.json`.
2. El ciclo de refinamiento B′ solo recibe el mensaje de error del solver, nunca la respuesta de referencia.
3. El solver no implementa AC-3 y no debe presentarse como si lo hiciera.
4. Que el solver confirme una solución única no prueba que el modelo traduzca bien el enunciado. Por eso hubo una revisión manual aparte (entrada 4).
5. El dataset fue generado por un LLM (Claude). Si alguno de los brazos usa un modelo de la misma familia, hay que mencionarlo en el reporte como un posible sesgo.
