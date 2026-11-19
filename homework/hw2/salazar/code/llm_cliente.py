"""Cliente LLM común para los brazos B, B' y C.

Usa el cliente `aicourse` del curso (copiado en code/aicourse, el mismo del
deber 1) con la caché obligatoria en `.llm_cache/` de esta carpeta. Añade lo que
pide la instrumentación del HW2:

  * tokens de entrada y salida (Ollama los da como prompt_eval_count y eval_count)
  * el tiempo del LLM medido en la llamada ORIGINAL, aunque ahora venga de la
    caché (si no, una segunda corrida diría que el LLM tardó 0 s)

Uso:
    from llm_cliente import ClienteLLM
    llm = ClienteLLM()                      # modelo y temperatura de config.py
    r = llm.llamar("prompt...", semilla=1)
    r.texto, r.tokens_entrada, r.tokens_salida, r.tiempo_llm_s, r.cache, r.error

Variables de entorno: AICOURSE_MODEL (por defecto el de config.py).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import config  # noqa: E402
from aicourse.cache import cache_key  # noqa: E402
from aicourse.llm import LLM, OLLAMA_URL  # noqa: E402

CACHE = AQUI.parent / ".llm_cache"
MODELO = os.environ.get("AICOURSE_MODEL", config.MODELO)


@dataclass
class RespuestaLLM:
    texto: str
    tokens_entrada: int
    tokens_salida: int
    tiempo_llm_s: float
    cache: bool
    modelo: str
    error: str | None = None


class ClienteLLM:
    def __init__(self, modelo: str = MODELO, backend: str = "ollama",
                 temperatura: float = config.TEMPERATURA, timeout: float = config.LIMITE_LLM_S):
        self.modelo = modelo
        self.temperatura = temperatura
        self._llm = LLM(backend=backend, model=modelo, cache_dir=str(CACHE),
                        temperature=temperatura, timeout=timeout)

    def _ollama_con_limite(self, prompt: str, semilla: int):
        """Llamada a Ollama en modo streaming con un límite de tiempo TOTAL.

        Si pasan LIMITE_LLM_S segundos cerramos la conexión (Ollama cancela la
        generación) y devolvemos "no_termina". Sin streaming, el timeout de urllib
        solo mide la espera entre bytes y una generación que se alarga no se corta.
        """
        cuerpo = {"model": self.modelo, "prompt": prompt, "stream": True,
                  "options": {"temperature": self.temperatura, "seed": semilla}}
        req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=json.dumps(cuerpo).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
        t0 = time.perf_counter()
        partes, final = [], {}
        try:
            with urllib.request.urlopen(req, timeout=config.LIMITE_LLM_S) as resp:
                for linea in resp:
                    if time.perf_counter() - t0 > config.LIMITE_LLM_S:
                        return None, {}, time.perf_counter() - t0, "no_termina"
                    if not linea.strip():
                        continue
                    trozo = json.loads(linea)
                    partes.append(trozo.get("response", ""))
                    if trozo.get("done"):
                        final = trozo
                        break
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            transcurrido = time.perf_counter() - t0
            return None, {}, transcurrido, ("no_termina" if transcurrido >= config.LIMITE_LLM_S - 1
                                             or "timed out" in str(e).lower() else f"{type(e).__name__}: {e}")
        meta = {k: final[k] for k in ("eval_count", "prompt_eval_count", "total_duration") if k in final}
        return "".join(partes), meta, time.perf_counter() - t0, None

    def llamar(self, prompt: str, semilla: int = 0) -> RespuestaLLM:
        key = cache_key(self._llm.backend, self.modelo, prompt, self.temperatura, semilla)
        guardado = self._llm.cache.get(key)
        if guardado is not None:
            texto, meta, cache = guardado.get("text", ""), guardado.get("meta", {}), True
            tiempo, error = float(guardado.get("elapsed", 0.0)), guardado.get("error")
        else:
            texto, meta, tiempo, error = self._ollama_con_limite(prompt, semilla)
            cache = False
            if error is None:
                self._llm.cache.put(key, {"text": texto, "backend": self._llm.backend, "model": self.modelo,
                                          "prompt": prompt, "temperature": self.temperatura, "seed": semilla,
                                          "elapsed": tiempo, "meta": meta})
        r = type("R", (), {"text": texto or "", "meta": meta, "cached": cache})()
        meta = r.meta or {}
        if error and "timed out" in error.lower():
            error = "no_termina"
        if not error and tiempo > config.LIMITE_LLM_S:
            # también si viene de una caché grabada con un límite mayor: el criterio es el mismo
            error = "no_termina"
        if error == "no_termina":
            tiempo = max(tiempo, config.LIMITE_LLM_S)
        return RespuestaLLM(
            texto=r.text or "",
            tokens_entrada=int(meta.get("prompt_eval_count", 0) or 0),
            tokens_salida=int(meta.get("eval_count", 0) or 0),
            tiempo_llm_s=tiempo,
            cache=r.cached,
            modelo=self.modelo,
            error=error,
        )


class ClienteFalso:
    """Para probar código sin Ollama: responde siempre `texto`. Sus resultados
    NO se reportan."""

    def __init__(self, texto: str = "{}"):
        self.texto = texto
        self.modelo = "falso"

    def llamar(self, prompt: str, semilla: int = 0) -> RespuestaLLM:
        return RespuestaLLM(self.texto, len(prompt) // 4, len(self.texto) // 4, 0.0, False, "falso")
