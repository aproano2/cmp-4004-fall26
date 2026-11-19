"""Ollama adapter with a disk cache that preserves the ORIGINAL measured latency/tokens.

Fixes vs. the first version
- a cache hit used to return llm_time_s = 0, which zeroed every re-run's timing and made B' cost wrong;
  now the original latency is stored and returned (flag `cached` tells you it was replayed);
- transport errors are NOT cached any more (a flaky connection used to poison the cache forever);
- the cache key includes seed, num_predict and num_ctx, not just model+temperature+prompt;
- `done_reason` is recorded so truncated outputs (done_reason == "length") are visible in the taxonomy;
- the backend is pluggable (tests replace `BACKEND` with a fault-injecting mock).
"""
import hashlib, json, os, urllib.request
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".llm_cache"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "3072"))
NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
HTTP_TIMEOUT_S = int(os.getenv("OLLAMA_HTTP_TIMEOUT", "300"))


def _ollama_backend(prompt, temperature, seed):
    payload = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
                          "options": {"temperature": temperature, "seed": seed,
                                      "num_predict": NUM_PREDICT, "num_ctx": NUM_CTX}}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    start = perf_counter()
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as response:
        raw = json.loads(response.read().decode("utf-8"))
    return {"response": raw.get("response", ""),
            "prompt_tokens": raw.get("prompt_eval_count", 0),
            "completion_tokens": raw.get("eval_count", 0),
            "done_reason": raw.get("done_reason", ""),
            "llm_time_s": perf_counter() - start}


BACKEND = _ollama_backend


def call_llm(prompt, temperature=0.0, seed=0):
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(json.dumps({"model": MODEL, "t": temperature, "seed": seed,
                                     "np": NUM_PREDICT, "ctx": NUM_CTX, "prompt": prompt},
                                    sort_keys=True).encode()).hexdigest()
    path = CACHE / f"{key}.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        data["cached"] = True               # llm_time_s / tokens are the ORIGINAL measurements
        return data
    start = perf_counter()
    try:
        result = BACKEND(prompt, temperature, seed)
    except Exception as exc:                # infrastructure failure: report, never cache
        return {"response": "", "error": f"{type(exc).__name__}: {exc}", "prompt_tokens": 0,
                "completion_tokens": 0, "done_reason": "", "llm_time_s": perf_counter() - start,
                "cached": False, "model": MODEL}
    result.update({"cached": False, "model": MODEL, "temperature": temperature, "seed": seed})
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result
