# HW2 · The Formalizer (CSP) · Salazar, Ochoa, Chano

Probamos la arquitectura "el LLM traduce a un modelo formal y un solver lo resuelve" con CSP, sobre 21 problemas propios, con `qwen2.5:3b` (y `qwen2.5:7b` como experimento de tamaño) y cuatro brazos (A a mano, B híbrido, B′ con refinamiento, C directo).

| Qué | Dónde |
|---|---|
| Reporte | [`REPORT.md`](REPORT.md) |
| Taxonomía de cada fallo de B, con la salida del modelo | [`taxonomy.md`](taxonomy.md) |
| Notebook de presentación (ejecutado) | `hw2_salazarD_ochoaA_chanoJ.ipynb` y `.html` |
| Problemas, gold y verificación a mano | [`problems/`](problems/) |
| Código: solver, brazos, refinamiento, taxonomía, figuras, costos | [`code/`](code/) |
| Resultados por instancia | [`results/`](results/) |
| Figuras | [`fig/`](fig/) |
| Respuestas del modelo (caché) | `.llm_cache/` |
| Uso de IA | [`AI_LOG.md`](AI_LOG.md) |

## Reproducir

```powershell
python -m pip install -r requirements.txt
$env:PYTHONIOENCODING="utf-8"
python code\tests\test_base.py            # pruebas del solver y del formato
python code\tests\test_sin_fugas.py       # ningún prompt contiene la respuesta
python code\verificar_dataset.py          # solución única e igual al gold en los 21 problemas
python code\brazo_a.py                    # A: modelo a mano -> solver
python code\brazo_b.py                    # B y B′ (usa la caché; sin caché necesita Ollama con qwen2.5:3b)
python code\brazo_c.py                    # C: respuesta directa
python code\taxonomia.py; python code\figuras.py; python code\costos.py; python code\scorecard.py
```
