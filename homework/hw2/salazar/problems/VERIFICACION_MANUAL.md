# HW2 · Registro de verificaciones manuales

**Equipo:** Daniel Salazar, Andretty Ochoa y Jalil Chano  
**Fecha de la revisión registrada:** 18 de noviembre de 2026

## 1. Objetivo y método

El objetivo de esta revisión es comprobar que las pistas de los enunciados llevan a las respuestas esperadas, sin tomar el `gold` como punto de partida. Para cada ejemplo, primero reconstruimos la solución mediante deducciones lógicas a partir de sus pistas; después la comparamos con el campo `gold` del JSON. Como control adicional, ejecutamos una enumeración exhaustiva independiente en Python para comprobar que **no existen otras asignaciones válidas**.

Los razonamientos de la sección 2 son reconstrucciones explicadas paso a paso. La sección 3 distingue expresamente esa explicación de la corrida automática. Las verificaciones documentadas corresponden a los tres problemas allí identificados, no a una repetición completa de los cuatro brazos del experimento.

## 2. Registro de razonamientos y contraste con el gold

| Problema | Quién | Fecha | Cómo lo resolvimos (pistas clave) | ¿Coincide con el gold? | Observaciones |
|---|---|---|---|---|---|
| `facil-01` | Revisión del equipo, con apoyo de IA | 2026-11-18 | Lucas ocupa la casa 3. Sofía está inmediatamente a la derecha de Mateo, por lo que la pareja debe quedar en 1 y 2. Mateo vive en la roja; la azul sigue a la amarilla, y ambas quedan en 2 y 3. | **Sí** | Las seis variables coinciden; una solución válida en la comprobación automática. |
| `facil-02` | Revisión del equipo, con apoyo de IA | 2026-11-18 | Jingle va después de la franja 3 y le siguen Traffic y News: sus posiciones son 4, 5 y 6. Weather e Interview deben ir seguidos, antes de Quiz, así que ocupan 1, 2 y 3. | **Sí** | Las seis actividades coinciden; una solución válida en la comprobación automática. |
| `facil-05` | Revisión del equipo, con apoyo de IA | 2026-11-18 | Trim=3 implica Stamp=4 y Dry=5. Sketch y Center van juntos y Center debe preceder a Trim, de modo que ocupan 1 y 2. Glaze, Fire y Pack llenan 6, 7 y 8. | **Sí** | Las ocho actividades coinciden; una solución válida en la comprobación automática. |

### `facil-01` · Casas, personas y colores

**Deducción a partir de las cuatro pistas:**

1. Lucas vive en la casa **3**.
2. Sofía vive inmediatamente a la derecha de Mateo. Como la casa 3 ya pertenece a Lucas, Mateo no puede estar en la 2; entonces **Mateo = 1** y **Sofía = 2**.
3. Mateo vive en la casa roja, por lo tanto **Red = 1**.
4. La casa azul está inmediatamente a la derecha de la amarilla. Como los colores son distintos y la casa 1 ya es roja, las casas restantes deben ser **Yellow = 2** y **Blue = 3**.

**Respuesta reconstruida:** `Mateo=1, Sofía=2, Lucas=3, Red=1, Yellow=2, Blue=3`.  
**Comparación:** coincide exactamente con `gold`. Todas las pistas quedan satisfechas.

### `facil-02` · Horarios de radio

**Deducción a partir de las cinco pistas:**

1. Jingle debe estar **después** de la franja 3; sus posiciones posibles serían 4, 5 o 6.
2. Traffic va inmediatamente después de Jingle y News inmediatamente después de Traffic. El bloque necesita tres franjas consecutivas: si comenzara en 5 o 6, se saldría del horario. Por lo tanto, **Jingle = 4, Traffic = 5 y News = 6**.
3. Quedan las franjas **1, 2 y 3** para Weather, Interview y Quiz.
4. Interview va inmediatamente después de Weather y antes de Quiz. La única posibilidad es **Weather = 1, Interview = 2 y Quiz = 3**.

**Respuesta reconstruida:** `Weather=1, Interview=2, Quiz=3, Jingle=4, Traffic=5, News=6`.  
**Comparación:** coincide exactamente con `gold` y respeta el orden de las cinco pistas.

### `facil-05` · Actividades de cerámica

**Deducción a partir de las ocho pistas:**

1. Trim está fijado en la franja **3**.
2. Stamp va inmediatamente después de Trim, así que **Stamp = 4**. Dry va inmediatamente después de Stamp, así que **Dry = 5**.
3. Center está inmediatamente después de Sketch y además debe ocurrir antes de Trim. Como las franjas 3, 4 y 5 ya están ocupadas, el par consecutivo solo puede ser **Sketch = 1 y Center = 2**.
4. Quedan las franjas **6, 7 y 8** para Glaze, Fire y Pack. Fire va inmediatamente después de Glaze y Pack inmediatamente después de Fire: **Glaze = 6, Fire = 7 y Pack = 8**. Se cumple también que Dry ocurre antes de Glaze.

**Respuesta reconstruida:** `Sketch=1, Center=2, Trim=3, Stamp=4, Dry=5, Glaze=6, Fire=7, Pack=8`.  
**Comparación:** coincide exactamente con `gold`; las ocho pistas son compatibles con la asignación.

## 3. Corrida automática independiente (evidencia complementaria)

Después de reconstruir las respuestas con las pistas, ejecutamos una comprobación independiente en Python (`code/verificar_enumeracion.py`, que se puede volver a correr). Para `facil-01` se enumeraron las seis variables sobre tres posiciones y se exigieron las restricciones de distinción, igualdad y contigüidad; para los dos problemas de horarios se generaron permutaciones completas de los puestos, filtrando las restricciones de orden y contigüidad. En **ninguno** de los tres casos se utilizó el `gold` para encontrar la solución: la comparación se hizo al final.

| Problema | Asignaciones evaluadas por Python | Soluciones que cumplen las pistas | ¿Igual al gold? |
|---|---:|---:|---|
| `facil-01` | 729 (= 3⁶) | 1 | Sí |
| `facil-02` | 720 (= 6!) | 1 | Sí |
| `facil-05` | 40.320 (= 8!) | 1 | Sí |
| **Total** | **41.769** | **3** | **3/3** |

**Interpretación:** 41.769 es el número de **asignaciones examinadas automáticamente**, **no** el número de ejercicios resueltos a mano ni el número de corridas del LLM. El dato importante es que en cada problema apareció una única asignación compatible con todas las pistas y esa asignación es la del `gold`.

## 4. Conclusión

En los tres ejemplos documentados, el razonamiento paso a paso conduce a la misma respuesta almacenada en `gold`. La comprobación automática adicional confirmó que esa respuesta es **única** en cada caso. Así pudimos contrastar los enunciados, las restricciones y las soluciones esperadas con dos enfoques complementarios: deducción explicada y enumeración de posibilidades. Las herramientas de IA se usaron como apoyo para organizar y comprobar los resultados; la evidencia de las corridas está diferenciada del razonamiento de los ejercicios.
