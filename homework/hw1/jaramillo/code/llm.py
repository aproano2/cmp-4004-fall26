"""Cliente mínimo de LLM con caché obligatoria (resources/setup.md).

Backends:
    ollama   modelo local en http://localhost:11434 (por defecto qwen2.5:3b)
    manual   imprime el prompt y tú pegas la respuesta de cualquier chat

Cada llamada se guarda en .llm_cache/<sha256>.json, con clave
(backend, modelo, mensajes, temperatura, semilla, rep). `rep` existe solo para
que la prueba de reproducibilidad pueda hacer cinco llamadas idénticas sin que
la caché conteste las últimas cuatro. Un acierto de caché no toca el modelo,
así que el análisis se puede repetir gratis y los transcripts quedan como
evidencia auditable.
"""
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / ".llm_cache"
# 127.0.0.1 y no "localhost": en Windows "localhost" prueba primero IPv6 y añade
# unos 2 s de espera a CADA llamada, lo que inflaba la latencia medida.
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
LLM_TIMEOUT_S = 300          # timeout duro por llamada al modelo
MAX_TOKENS = 600             # tope de tokens generados por llamada
NUM_CTX = 4096
RETRIES = 4                  # reintentos ante un error HTTP de Ollama


class LLM:
    def __init__(self, backend="ollama", model="qwen2.5:3b"):
        self.backend, self.model = backend, model
        CACHE.mkdir(exist_ok=True)
        self.used = set()            # transcripts usados en esta corrida

    def prune(self):
        """Borra de la caché los transcripts que esta corrida NO usó (quedan de
        versiones anteriores del experimento). Así .llm_cache/ contiene
        exactamente la evidencia de los CSV. Devuelve cuántos borró."""
        stale = [f for f in CACHE.glob("*.json") if f.name not in self.used]
        for f in stale:
            f.unlink()
        return len(stale)

    def _key(self, messages, temperature, seed, rep):
        blob = json.dumps([self.backend, self.model, messages, temperature, seed, rep],
                          sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def chat(self, messages, temperature=0.0, seed=0, rep=0):
        """Devuelve un dict: text, status ('ok' | 'timeout' | 'error'),
        latency_s, tokens_in, tokens_out, cached."""
        f = CACHE / f"{self._key(messages, temperature, seed, rep)}.json"
        self.used.add(f.name)
        if f.exists():
            rec = json.loads(f.read_text(encoding="utf-8"))
            rec["cached"] = True
            return rec

        t0 = time.perf_counter()
        if self.backend == "ollama":
            rec = self._ollama(messages, temperature, seed)
        elif self.backend == "manual":
            rec = self._manual(messages)
        else:
            raise ValueError(self.backend)
        rec.update({"backend": self.backend, "model": self.model,
                    "temperature": temperature, "seed": seed, "rep": rep,
                    "messages": messages,
                    "latency_s": round(time.perf_counter() - t0, 3)})
        if rec["status"] != "error":      # un error de conexión no es evidencia
            f.write_text(json.dumps(rec, indent=2, ensure_ascii=False),
                         encoding="utf-8")
        rec["cached"] = False
        return rec

    def _ollama(self, messages, temperature, seed):
        body = json.dumps({
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": temperature, "seed": seed,
                        "num_predict": MAX_TOKENS, "num_ctx": NUM_CTX},
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
                    # Ollama a veces responde 500 (el modelo se descargó de
                    # memoria, etc.). Se espera y se reintenta la misma llamada.
                    print(f"  Ollama respondió HTTP {e.code}; reintento "
                          f"{attempt + 1}/{RETRIES}...", flush=True)
                    time.sleep(5 * (attempt + 1))
            if data is None:              # no se guarda en caché: no es evidencia
                return {"text": "", "status": "error", "tokens_in": None,
                        "tokens_out": None}
        except TimeoutError:
            return {"text": "", "status": "timeout", "tokens_in": None,
                    "tokens_out": None}
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower():
                return {"text": "", "status": "timeout", "tokens_in": None,
                        "tokens_out": None}
            raise SystemExit(
                f"No se pudo conectar con Ollama en {OLLAMA_URL} ({e}).\n"
                f"Abre Ollama y descarga el modelo:  ollama pull {self.model}")
        return {"text": data["message"]["content"], "status": "ok",
                "tokens_in": data.get("prompt_eval_count"),
                "tokens_out": data.get("eval_count"),
                # tiempo medido por el propio Ollama (ns -> s), sin la red
                "ollama_total_s": round(data.get("total_duration", 0) / 1e9, 3)}

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
