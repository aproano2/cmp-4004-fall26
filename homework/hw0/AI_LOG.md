## Week 0 — the sorting verifier

**Tool:** Gemini

**What I asked:** Cómo configurar el entorno virtual de Python en VS Code, cómo analizar las diferencias teóricas (garantías, costo, interpretabilidad) para llenar los "TODOs" de la tabla de comparación, y cómo extraer un caso de falla específico del código para publicarlo en el foro.

**What I got:** Instrucciones paso a paso para la terminal (`.venv`, dependencias), explicaciones teóricas basadas en los conceptos de la clase para comparar el algoritmo clásico frente al LLM, y un pequeño script de Python para aislar un error `invalid` de los resultados crudos.

**What I did with it:** Logré pasar el chequeo del entorno (`doctor.txt`), redacté mi reporte completo en `first_comparison.md` documentando los sesgos del experimento, y armé mi publicación del "Failure Atlas" demostrando cómo el LLM duplicó los elementos de la lista.

**Did I understand it?** Sí, entiendo claramente cómo aislar mi entorno de trabajo, por qué el algoritmo clásico tiene garantías matemáticas que el LLM no tiene, y la importancia de evaluar los modos de falla de los modelos estadísticos.