## Week 0 — Environment Setup and First Comparison

**Tool:** Gemini (LLM)

**What I asked:** 
1. "Vamos a hacer este laboratorio que debo hacer primero, guiame" (I asked for initial guidance on setting up the lab environment).
2. "Al hacer el doctor me sale sto... ModuleNotFoundError" (I asked for help troubleshooting a Python virtual environment error when running `aicourse.doctor`).
3. "Explicame que se quiere demostrar en la seccion 4 que no entiendo" (I asked for an explanation of the prompt engineering variable section).
4. "No entiendo ya ejecute todo el notebook y esto fue lo que obtuve pero no entiendo de la seccion 6 para abajo" (I asked for help interpreting the execution results of the classical vs. LLM sorting comparison, specifically the scorecard and failure modes).

**What I got:** 
1. Step-by-step instructions to pull the Ollama model and set up the `.venv`.
2. An explanation that the `.venv` wasn't active on Windows and the exact commands to activate it and reinstall dependencies.
3. An explanation of how changing the prompt makes the output machine-readable without necessarily making the model "smarter," and a warning against p-hacking.
4. A detailed breakdown of the execution table, explaining the "cliff" effect, the failure modes (like `invalid` and `wrong-but-confident`), and a generated Spanish draft for the `first_comparison.md` file.
**What I did with it:** 
I used the troubleshooting steps to successfully run the environment check (`doctor.txt`). I used the explanations to understand the parsing and scaling concepts, and I used the generated draft to create my `first_comparison_es.md` submission.
**Did I understand it?** 
Yes, I understand why the virtual environment is necessary, why parsing is critical to avoid silent errors, and why the LLM failed at scaling (the cliff) compared to the O(n log n) classical algorithm.