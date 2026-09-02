# Primera Comparación: `sorted()` vs LLM

## 1. Scorecard (Tarjeta de Puntuación)

| Eje | sorted() | LLM |
|---|---|---|
| Exactitud | 20/20 (100%) | 2/20 (10%) |
| Garantía | **Garantizado de devolver una permutación no decreciente en O(n log n)** | **Sin garantía matemática; resolver n=5 no asegura resolver n=20** |
| Costo | **~0 tokens/ciclos de CPU** | **Alto costo computacional (generación de múltiples tokens)** |
| Latencia | 0.00s / 0.00s | 3.14s / 122.06s |
| Reproducibilidad | **100% determinista (siempre devuelve la misma respuesta)** | **Variable; las respuestas cambian según la temperatura y la semilla** |
| Escalabilidad | 100% → 100% → 100% → 100% | 40% → 0% → 0% → 0% |
| Interpretabilidad | **Algoritmo de ordenamiento transparente y matemáticamente probado** | **Caja negra; sin seguimiento lógico ni certificado de corrección** |
| Modo de falla | ninguno observado | invalid=9, malformed=2, wrong-but-confident=7 |

## 2. Leyendo la Tabla (Análisis)

**1. ¿Cayó la tasa de éxito del LLM al alargar la lista?**
Sí, observamos un "acantilado" severo. El LLM comenzó con una tasa de éxito del 40% para listas de tamaño 5, pero cayó inmediatamente al 0% para los tamaños 10, 20 y 40. 

**2. ¿Qué modo de falla dominó?**
El modo de falla `invalid` (inválido) dominó (9 instancias). Esto significa que el LLM omitió números de la lista original o inventó otros nuevos (cambiando el multiconjunto). El segundo más común fue `wrong-but-confident` (equivocado pero seguro, 7 instancias), donde mantuvo los números correctos pero falló al ordenarlos.

**3. ¿Cuánto costó cada instancia resuelta?**
El algoritmo clásico `sorted()` tomó 0.00s por instancia, aprovechando su eficiencia O(n log n). El LLM tomó una mediana de 3.14s y hasta 122.06s en el peor de los casos, haciéndolo inmensamente más lento y exponencialmente más costoso, sin ninguna prueba de escalabilidad.

## 3. Dónde pudimos haber sido injustos

- **¿Cambiaría el resultado un modelo más grande — y puedes saberlo sin ejecutarlo?**
  Usamos `qwen2.5:3b`, que es un modelo muy pequeño ejecutándose localmente en CPU. Un modelo de frontera (como GPT-4o o Claude 3.5) probablemente empujaría el "acantilado" más lejos (ej., fallando en n=100 en lugar de n=10), pero sin un cambio arquitectónico fundamental, la falta de garantía se mantiene.
- **¿Es la distribución de tus instancias accidentalmente favorable para uno de los lados?**
  Ordenar números enteros uniformemente aleatorios de hasta 999 es estándar para los algoritmos clásicos, pero es altamente antinatural para la distribución de entrenamiento de un LLM, la cual favorece el lenguaje natural sobre arreglos numéricos densos y aleatorios.
- **¿Ajustaste los parámetros de un lado pero usaste un prompt por defecto para el otro?**
  Usamos un prompt básico (zero-shot) para el LLM. No empleamos ejemplos previos (few-shot) ni técnicas avanzadas de Cadena de Pensamiento (Chain of Thought) específicamente ajustadas para ordenar, lo cual podría haberle dado al LLM una mejor oportunidad de razonar la lógica.