"""Conexión con LLM, con caché en .llm_cache/ 

Backends:
-ollama: modelo local a través de Ollama 
-manual: imprime el prompt; pegas la respuesta de cualquier chat y terminas con "END".
-mock: modelo falso solo para pruebas. Sus resultados no van al reporte.

Cada llamada se guarda en un JSON identificado por un hash del backend, el modelo, los mensajes, la temperatura y la semilla. Si se repite una llamada, se lee de la caché y no se vuelve a consultar al modelo.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

DEFAULT_CACHE = Path(__file__).resolve().parent.parent / ".llm_cache"


class BackendError(Exception):
    """One call failed (e.g. it timed out). Recorded as a 'timeout' row."""


class BackendUnavailable(BackendError):
    """The backend cannot be reached at all (Ollama not running). Stops the run."""


DEFAULT_MAX_TOKENS = 1024


def cache_key(backend, model, messages, temperature, seed, max_tokens=DEFAULT_MAX_TOKENS, tools=None):
    parts = [backend, model, messages, temperature, seed]
    if max_tokens != DEFAULT_MAX_TOKENS:      # a different token budget is a different experiment
        parts.append({"max_tokens": max_tokens})
    if tools:                                 # native tool definitions are part of the prompt
        parts.append({"tools": tools})
    blob = json.dumps(parts, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


def read_record(path):
    """Cache files are UTF-8; files written by an older version on Windows may be cp1252."""
    raw = Path(path).read_bytes()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return json.loads(raw.decode("cp1252", errors="replace"))


class LLM:
    def __init__(self, backend="ollama", model="qwen2.5:3b", cache_dir=DEFAULT_CACHE, temperature=0.0,
                 seed=0, host="http://localhost:11434", max_tokens=DEFAULT_MAX_TOKENS, timeout=600, mock_fn=None):
        self.backend, self.model = backend, model
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temperature, self.seed = temperature, seed
        self.host, self.max_tokens, self.timeout = host, max_tokens, timeout
        self.mock_fn = mock_fn
        self.last = {}  # metadata of the most recent call: cached, latency_s, key

    # ------------------------------------------------------------------ API
    def chat(self, messages, temperature=None, seed=None, tools=None):
        """Returns the reply text. With `tools` (Ollama native tool calling), any tool calls the
        model made are in self.last["tool_calls"] as [{"name": ..., "arguments": {...}}]."""
        temperature = self.temperature if temperature is None else temperature
        seed = self.seed if seed is None else seed
        key = cache_key(self.backend, self.model, messages, temperature, seed, self.max_tokens, tools)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            rec = read_record(path)
            self.last = {"cached": True, "latency_s": rec.get("latency_s", 0.0), "key": key,
                         "tool_calls": rec.get("tool_calls", [])}
            return rec["response"]
        t0 = time.time()
        self._meta = {}
        response, tool_calls = self._call(messages, temperature, seed, tools)  # may raise -> NOT cached
        latency = time.time() - t0
        rec = {"backend": self.backend, "model": self.model, "temperature": temperature, "seed": seed,
               "max_tokens": self.max_tokens, "messages": messages, "response": response,
               "latency_s": round(latency, 3), "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
               **self._meta}
        if tools:
            rec["tools"] = tools
            rec["tool_calls"] = tool_calls
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
        self.last = {"cached": False, "latency_s": latency, "key": key, "tool_calls": tool_calls}
        return response

    # ------------------------------------------------------------- backends
    def _call(self, messages, temperature, seed, tools):
        """-> (text, tool_calls)."""
        if self.backend == "ollama":
            return self._ollama(messages, temperature, seed, tools)
        if self.backend == "manual":
            if tools:
                raise BackendUnavailable("native tool calling needs Ollama; use --tool-protocol text")
            return self._manual(messages), []
        if self.backend == "mock":
            out = self.mock_fn(messages, temperature, seed, tools=tools)
            if isinstance(out, dict):
                return out.get("content", ""), out.get("tool_calls", [])
            return out, []
        raise BackendError(f"unknown backend {self.backend!r}")

    def _ollama(self, messages, temperature, seed, tools=None):
        import requests
        try:
            body = {"model": self.model, "messages": messages, "stream": False,
                    "options": {"temperature": temperature, "seed": seed, "num_predict": self.max_tokens}}
            if tools:
                body["tools"] = tools
            r = requests.post(f"{self.host}/api/chat", timeout=self.timeout, json=body)
            r.raise_for_status()
            data = r.json()
            # done_reason "length" = cut off by max_tokens; "stop" = the model finished
            self._meta = {k: data[k] for k in ("done_reason", "eval_count", "prompt_eval_count") if k in data}
            msg = data["message"]
            calls = []
            for tc in msg.get("tool_calls") or []:
                fn = tc.get("function", {})
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        pass
                calls.append({"name": fn.get("name"), "arguments": args})
            return msg.get("content", ""), calls
        except requests.exceptions.ConnectionError as e:
            raise BackendUnavailable(
                f"cannot reach Ollama at {self.host}. Is it running? (`ollama serve`, then "
                f"`ollama pull {self.model}`)") from e
        except requests.exceptions.HTTPError as e:
            if r.status_code == 404:
                raise BackendUnavailable(f"model {self.model!r} not found: run `ollama pull {self.model}`") from e
            body = (r.text or "").strip().replace("\n", " ")[:300]
            raise BackendError(f"ollama HTTP {r.status_code}: {body}") from e
        except Exception as e:  # read timeout, bad JSON
            raise BackendError(f"ollama call failed: {e}") from e

    def _manual(self, messages):
        shown = messages if len(messages) <= 2 else messages[-1:]
        bar = "=" * 72
        print(f"\n{bar}\nPASTE THIS INTO YOUR CHAT"
              f"{' (same conversation as before)' if len(messages) > 2 else ' (start a NEW chat)'}"
              f"\n{bar}", file=sys.stderr)
        for m in shown:
            print(f"[{m['role']}]\n{m['content']}\n", file=sys.stderr)
        print(f"{bar}\nPaste the model's reply below, then type END on its own line:", file=sys.stderr)
        lines = []
        for line in sys.stdin:
            if line.strip() == "END":
                break
            lines.append(line)
        else:
            if not lines:
                raise BackendError("stdin closed with no reply")
        return "".join(lines).strip()


def ping(llm):
    """For `python llm.py --ping`: is the backend reachable?"""
    t0 = time.time()
    out = llm.chat([{"role": "user", "content": "Reply with the single word: ready"}], seed=0)
    return out.strip()[:80], time.time() - t0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ollama")
    ap.add_argument("--model", default="qwen2.5:3b")
    ap.add_argument("--ping", action="store_true")
    a = ap.parse_args()
    if a.ping:
        try:
            reply, dt = ping(LLM(a.backend, a.model))
            print(f"ok: {a.backend} ({a.model}) replied {reply!r} in {dt:.1f}s")
        except BackendError as e:
            print("FAILED:", e)
            sys.exit(1)
