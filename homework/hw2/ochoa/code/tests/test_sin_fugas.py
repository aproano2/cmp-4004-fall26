"""Comprueba que ningún prompt de B, B' o C contiene la respuesta correcta.

Recorre los intentos guardados (results/intentos_b.jsonl) y reconstruye los
prompts de cada problema: ni el gold ni el modelo a mano pueden aparecer.

    python code/tests/test_sin_fugas.py
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI))

import brazo_b  # noqa: E402
import respuesta_c  # noqa: E402
from problemas import cargar  # noqa: E402
from resultados import CARPETA  # noqa: E402


def _huellas(p):
    """Textos que delatarían el gold o el modelo a mano dentro de un prompt."""
    return [json.dumps(p["gold"], ensure_ascii=False), json.dumps(p["modelo_mano"], ensure_ascii=False),
            p["verificacion_manual"][:60]]


def test_prompts_iniciales():
    for p in cargar():
        for prompt in (brazo_b.construir_prompt(p), respuesta_c.construir_prompt(p)):
            for h in _huellas(p):
                assert h not in prompt, (p["id"], h[:40])


def test_mensajes_de_refinamiento():
    """El mensaje que recibe B' sale solo del solver: nunca nombra el gold."""
    problemas = {p["id"]: p for p in cargar()}
    ruta = CARPETA / "intentos_b.jsonl"
    if not ruta.exists():
        return
    for linea in open(ruta, encoding="utf-8"):
        it = json.loads(linea)
        p = problemas[it["problema_id"]]
        msg = it["mensaje_solver"]
        for h in _huellas(p):
            assert h not in msg, (p["id"], h[:40])
        assert "gold" not in msg.lower()


if __name__ == "__main__":
    test_prompts_iniciales()
    test_mensajes_de_refinamiento()
    print("ok: ningún prompt ni mensaje de refinamiento contiene la respuesta correcta")
