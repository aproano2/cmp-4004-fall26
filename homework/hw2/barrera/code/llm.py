"""Cliente mínimo de LLM con caché obligatoria (resources/setup.md).

Es el mismo cliente del duelo 1, con dos cambios: el número de tokens y el
contexto son parámetros (el brazo B′ acumula varias rondas de conversación) y
hay un backend `fake` para los tests, que responde con textos guionizados.

Backends:
    ollama   modelo local en http://127.0.0.1:11434 (por defecto qwen2.5:3b)
    manual   imprime el prompt y tú pegas la respuesta de cualquier chat
    fake     respuestas fijas (solo tests)

Cada llamada se guarda en .llm_cache/<sha256>.json con clave
(backend, modelo, mensajes, temperatura, semilla, opciones). Un acierto de caché
no toca el modelo: el análisis se repite gratis y los transcripts quedan como
evidencia auditable. Si la corrida se corta, el mismo comando sigue donde quedó.
"""
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / ".llm_cache"
# 127.0.0.1 y no "localhost": en Windows "localhost" prueba primero IPv6 y
# añade unos 2 s de espera a cada llamada (lo medimos en el duelo 1).
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
LLM_TIMEOUT_S = 600          # timeout duro por llamada
MAX_TOKENS = 1500            # tope de tokens generados por llamada
NUM_CTX = 8192               # B′ acumula hasta 4 rondas en el contexto
RETRIES = 4                  # reintentos ante un error HTTP de Ollama


class LLM:
    def __init__(self, backend="ollama", model="qwen2.5:3b", script=None):
        self.backend, self.model = backend, model
        self.script = list(script or [])          # backend fake
        self.used = set()
        CACHE.mkdir(exist_ok=True)

    def prune(self):
        """Borra los transcripts que esta corrida no usó, para que .llm_cache/
        contenga exactamente la evidencia de los CSV."""
        stale = [f for f in CACHE.glob("*.json") if f.name not in self.used]
        for f in stale:
            f.unlink()
        return len(stale)

    def _key(self, messages, temperature, seed, max_tokens):
        blob = json.dumps([self.backend, self.model, messages, temperature, seed,
                           max_tokens], sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def chat(self, messages, temperature=0.0, seed=0, max_tokens=MAX_TOKENS):
        """Devuelve dict: text, status ('ok'|'timeout'|'error'), latency_s,
        tokens_in, tokens_out, cached."""
        if self.backend == "fake":
            text = self.script.pop(0) if self.script else ""
            return {"text": text, "status": "ok", "latency_s": 0.0, "tokens_in": 100,
                    "tokens_out": len(text) // 4, "cached": False}
        f = CACHE / f"{self._key(messages, temperature, seed, max_tokens)}.json"
        self.used.add(f.name)
        if f.exists():
            rec = json.loads(f.read_text(encoding="utf-8"))
            rec["cached"] = True
            return rec
        t0 = time.perf_counter()
        if self.backend == "ollama":
            rec = self._ollama(messages, temperature, seed, max_tokens)
        elif self.backend == "manual":
            rec = self._manual(messages)
        else:
            raise ValueError(self.backend)
        rec.update({"backend": self.backend, "model": self.model,
                    "temperature": temperature, "seed": seed, "messages": messages,
                    "latency_s": round(time.perf_counter() - t0, 3)})
        if rec["status"] != "error":          # un error de conexión no es evidencia
            f.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
        rec["cached"] = False
        return rec

    def _ollama(self, messages, temperature, seed, max_tokens):
        body = json.dumps({
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": temperature, "seed": seed,
                        "num_predict": max_tokens, "num_ctx": NUM_CTX},
        }).encode("utf-8")
        req = urllib.request.Request(OLLAMA_URL, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            data = None
            for attempt in range(RETRIES):
                try:
                    with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_S) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    break
                except urllib.error.HTTPError as e:
                    print(f"  Ollama respondió HTTP {e.code}; reintento "
                          f"{attempt + 1}/{RETRIES}...", flush=True)
                    time.sleep(5 * (attempt + 1))
            if data is None:
                return {"text": "", "status": "error", "tokens_in": None, "tokens_out": None}
        except TimeoutError:
            return {"text": "", "status": "timeout", "tokens_in": None, "tokens_out": None}
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower():
                return {"text": "", "status": "timeout", "tokens_in": None, "tokens_out": None}
            raise SystemExit(
                f"No se pudo conectar con Ollama en {OLLAMA_URL} ({e}).\n"
                f"Abre Ollama y descarga el modelo:  ollama pull {self.model}")
        return {"text": data["message"]["content"], "status": "ok",
                "tokens_in": data.get("prompt_eval_count"),
                "tokens_out": data.get("eval_count"),
                "ollama_total_s": round(data.get("total_duration", 0) / 1e9, 3),
                "done_reason": data.get("done_reason")}

    def _manual(self, messages):
        print("\n" + "=" * 70 + "\nPega esto en un chat NUEVO:\n" + "=" * 70)
        for m in messages:
            print(f"[{m['role']}]\n{m['content']}\n")
        print("=" * 70 + "\nPega la respuesta y luego una línea que diga solo END:")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        return {"text": "\n".join(lines), "status": "ok", "tokens_in": None,
                "tokens_out": None}
