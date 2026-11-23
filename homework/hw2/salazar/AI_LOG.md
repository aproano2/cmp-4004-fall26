# AI_LOG · HW2 The Formalizer

Política del curso: [`resources/ai-policy.md`](../../../resources/ai-policy.md). Cada integrante anota aquí, con honestidad, qué herramientas de IA usó, para qué y qué revisó o cambió por su cuenta. Los LLM que se *evalúan* en el experimento (`qwen2.5:3b`, y `qwen2.5:7b` en el experimento de tamaño) no van aquí: ese queda en `.llm_cache/` y en los CSV.

## Daniel Salazar
- **Herramienta.** Claude Code (Anthropic), trabajando en mi computadora sobre este repositorio.
- **Para qué la usé.**
  - Leer la consigna y los studios 6 a 9 y proponer cómo dividir el trabajo en el grupo.
  - Escribir la base del deber: el solver CSP ampliado (`csp_motor.py`), el formato de los problemas, el cliente del LLM con caché, el formato común de los CSV, el brazo A, el verificador del dataset, las pruebas y los 3 problemas de ejemplo.
  - Escribir los brazos B y B′ (`brazo_b.py`), con el prompt de traducción y el diagnóstico del solver que recibe B′.
  - Adaptar los borradores de Jalil (brazo C, costos y figura de precisión) al formato común de los CSV y completar las figuras que faltaban.
  - Los scripts de taxonomía, scorecard y entrega, y los borradores del REPORT y de taxonomy.md.
  - Verificar en la página oficial de Together AI el precio usado para el costo equivalente.
- **Decisiones que tomé yo.** El formalismo (CSP), la división del trabajo y los plazos, el protocolo (`qwen2.5:3b`, temperatura 0.7, 3 semillas), no forzar el modo JSON en el brazo C para que compita en igualdad con B, y congelar el prompt de B después de probarlo solo con los ejemplos.
- **Qué revisé y qué puedo explicar.** Para documentar nuestra validación, contrastamos de manera independiente las pistas y los resultados de `facil-01`, `facil-02` y `facil-05` con sus respectivos golds; las tres asignaciones coinciden y satisfacen todas las pistas, como queda detallado en `problems/VERIFICACION_MANUAL.md`. En el REPORT se distingue que B permite detectar fallos de sintaxis, restricciones incompatibles o múltiples soluciones, mientras que C puede generar asignaciones incorrectas sin una señal interna que las identifique. El caso `facil-02` muestra el límite del refinamiento B′: al cambiar restricciones para obtener una solución única, puede conservar una interpretación equivocada de la pista. También queda documentado que el costo por correcta se obtiene repartiendo todos los recursos consumidos, incluidos los intentos fallidos, entre las respuestas acertadas. Para el desarrollo recurrí a Claude como apoyo de programación, análisis y redacción; su uso está declarado y la responsabilidad del contenido y de su revisión corresponde al equipo.

## Andretty Ochoa
- **Herramienta.** Codex (OpenAI).
- **Qué pedí.** Revisar el avance del Issue #5, completar los 21 CSP de mi parte, ejecutar el verificador y el brazo A y preparar la documentación.
- **Cómo trabajamos.** Pensamos juntos el conjunto de 21 problemas. Yo aporté el primer caso, facilité el avance y definí qué debía cumplir el conjunto. Codex conservó `facil-01.json`, detectó la copia en `facil-02.json` y desarrolló los 20 casos pendientes con sus enunciados, modelos, golds y deducciones. También redactó el README y ejecutó el verificador (21 soluciones únicas) y el brazo A (63/63).
- **Qué revisé y qué puedo explicar.** En el registro del equipo dejamos el contraste independiente de tres problemas con sus pistas originales: `facil-01`, donde se fijan las tres casas a partir de Lucas, Mateo y los colores; `facil-02`, donde el bloque Jingle–Traffic–News ocupa las franjas 4–6; y `facil-05`, donde las precedencias ordenan las ocho actividades. En los tres casos las asignaciones obtenidas satisfacen todas las restricciones y coinciden con el gold, según `problems/VERIFICACION_MANUAL.md`. El modelo CSP representa las pistas mediante dominios, restricciones de diferencia y relaciones de orden, y el solver permite verificar unicidad sin depender únicamente de una respuesta generada por IA. Codex se utilizó como herramienta de apoyo para preparar los casos y ejecutar las comprobaciones automatizadas; el registro separa claramente esas herramientas de las comprobaciones independientes documentadas.

## Jalil Chano
- **Herramienta.** Claude (Anthropic).
- **Cómo trabajé.** Primero revisé la consigna del deber y la parte que me tocaba: el brazo C, el costo por respuesta correcta y las figuras. Después fui escribiendo cada archivo y le pedía a Claude que lo revisara y me sugiriera correcciones. Mientras yo corregía, Claude volvía a revisar, y así hasta tener cada pieza.
- **Qué entregué.**
  - `respuesta_c.py`, con tres redacciones del prompt del brazo C (v1, v2 y v3). Elegimos la v2 y el prompt nunca recibe el gold ni el modelo a mano.
  - `brazo_c.py`, el runner del brazo C.
  - `costos.py`, que calcula el costo por respuesta correcta sumando todos los intentos, también los fallidos y los reintentos de B′.
  - `figuras.py`, con la figura de precisión por dificultad y barras de desviación estándar entre semillas.
- **Qué cambió al integrarlo.** En la integración pasamos mis scripts al formato común de los CSV del grupo, agregamos la clasificación de los errores de C (sin formato, incompleta, incorrecta) y quitamos el modo JSON forzado de Ollama para que C compitiera en igualdad con B. Los precios los volvimos a revisar en la página oficial de Together AI, porque el modelo que yo había tomado ya no aparece en la lista.
- **Qué puedo explicar.** Por qué el costo se divide entre las respuestas correctas y no entre los intentos, cómo se calcula la precisión por nivel con su variación entre semillas, y por qué el prompt de C no puede ver la respuesta.
