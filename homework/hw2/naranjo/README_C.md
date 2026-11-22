# Brazo C y evaluación conjunta

Ollama debe estar ejecutándose con `qwen2.5:3b` (Q4_K_M, digest
`357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b`).

```bash
python -m pytest code/test_arm_c.py code/test_arm_b.py -q
python code/arm_c.py F01 F04 M08 --out results/pilot_c_v2.jsonl      # piloto
python code/arm_c.py --out results/arm_c_raw.jsonl                    # T=0, semilla 0
python code/evaluate_c.py results/arm_c_raw.jsonl                     # -> results/arm_c.csv
# varianza de C (T=0,7, semillas 1–5; repetir con --seed 2..5)
python code/arm_c.py --seed 1 --temperature 0.7 --out results/variance/arm_c_t07_s1.jsonl
python code/evaluation.py        # scorecard, tablas, varianza y 3 figuras en fig/
```

**Acuerdo respetado (README_B.md):** mismo `statement` y `answer_format` público, mismo modelo,
temperatura 0, semilla 0, `num_predict` 4096, una ejecución por problema y la misma función
`complete()` y caché `.llm_cache/` de B. C responde directamente, sin solver. `arm_c.py` nunca
abre `problems/ground_truth/`; solo `evaluate_c.py` y `evaluation.py` lo leen.

**Prompt.** El piloto v1 (`results/pilot_c_f01_prompt_v1.jsonl`) mostró que el modelo copiaba la
estructura `{"keys": …, "allowed_values": …}` en lugar de responder. La v2 añade un esqueleto
`{"OP1": "?", …}` construido solo con las claves públicas. Se fijó antes de la ejecución completa y
se validó en tres problemas (F01, F04, M08) solo por formato, sin mirar si acertaban.

**Lectura de la respuesta.** Primero `json.loads` estricto, como B. Si falla, se extrae el primer
`{...}` (`parse_mode = extracted`). En la ejecución principal las 20 respuestas pasaron en modo
estricto.

**Señal sin ground truth.** Para C solo se puede comprobar el formato contra el `answer_format`
público: JSON legible, todas las claves y valores dentro del dominio (`format_errors`). Lo demás es
silencioso.

**Hardware de C y de la varianza:** AMD Ryzen 9 6900HX, NVIDIA RTX 3080 Ti Laptop, 15,3 GB de RAM,
Windows 11, Ollama 0.30.5. La ejecución principal de B/B′ se hizo en otro equipo, por lo que sus
latencias no son directamente comparables. `evaluation.py` solo lee los CSV de A, B y B′; no los
modifica.

**Costo.** `evaluation.py` usa por defecto 0,30 USD por millón de tokens de entrada y 0,30 USD por
millón de tokens de salida: es la tarifa de Together AI para *Qwen2.5 7B Instruct Turbo*, el Qwen2.5
alojado más pequeño que lista together.ai/pricing (consultado el 2026-11-17). Como el modelo es de
7B, es una cota superior para uno de 3B. Las columnas `cost_usd` de los CSV por brazo quedan vacías;
el costo está en `results/scorecard.csv`.
