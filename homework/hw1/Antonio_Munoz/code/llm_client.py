"""llm_client.py -- cached client for a local Ollama server.

Every call is stored in ../.llm_cache/<sha256>.json (this folder is COMMITTED: it is
the raw evidence behind every LLM number in the report).  A call that is already in
the cache is returned instantly and costs nothing, so interrupted runs resume.

Cache key = SHA-256 of (backend, model, messages, temperature, seed, num_predict,
num_ctx, replicate).  `replicate` lets us store several independent calls with
IDENTICAL settings (needed for the reproducibility test); `tag` is only a label.
"""
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

HOST = "http://localhost:11434"
MODEL = "qwen2.5:3b"
MAX_RETRIES = 3          # transient server errors only (5xx / connection)
CACHE_DIR = Path(__file__).parent.parent / ".llm_cache"


def _key(request):
    return hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()


def chat(messages, model=MODEL, temperature=0.0, seed=0, num_predict=512,
         num_ctx=4096, replicate=0, tag="", tools=None):
    """Send `messages` (list of {role, content}) and return a record dict:
    text, done_reason, prompt_tokens, output_tokens, gen_latency_s, cached, key, ..."""
    request = {"backend": "ollama", "model": model, "messages": messages,
               "temperature": temperature, "seed": seed, "num_predict": num_predict,
               "num_ctx": num_ctx, "replicate": replicate}
    if tools is not None:              # only added when used: old cache keys stay valid
        request["tools"] = tools
    key = _key(request)
    path = CACHE_DIR / f"{key}.json"
    if path.exists():
        rec = json.loads(path.read_text())
        rec["cached"] = True
        return rec

    options = {"temperature": temperature, "num_predict": num_predict,
               "num_ctx": num_ctx}
    if seed is not None:               # seed=None -> the server picks a random seed
        options["seed"] = seed
    body = {"model": model, "messages": messages, "stream": False,
            "keep_alive": "60m", "options": options}
    if tools is not None:
        body["tools"] = tools
    req = urllib.request.Request(HOST + "/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    retries = 0
    while True:
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                resp = json.load(r)
            break
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            detail = ""
            if isinstance(e, urllib.error.HTTPError):
                try:
                    detail = e.read().decode(errors="replace")[:400]
                except Exception:
                    pass
            if isinstance(e, urllib.error.HTTPError) and e.code < 500:
                raise                      # a 4xx is OUR mistake: do not retry
            retries += 1
            print(f"   [llm_client] server error ({e}) {detail!r}; "
                  f"attempt {retries}/{MAX_RETRIES + 1}", flush=True)
            if retries > MAX_RETRIES:
                raise
            time.sleep(15)
    wall = time.perf_counter() - t0

    total = resp.get("total_duration", 0) / 1e9
    load = resp.get("load_duration", 0) / 1e9
    rec = {"key": key, "tag": tag, "request": request,
           "text": resp["message"]["content"],
           "tool_calls": resp["message"].get("tool_calls"),
           "done_reason": resp.get("done_reason"),
           "prompt_tokens": resp.get("prompt_eval_count"),
           "output_tokens": resp.get("eval_count"),
           "gen_latency_s": round(total - load, 3),   # excludes one-off model loading
           "load_s": round(load, 3), "wall_s": round(wall, 3),
           "retries": retries}
    CACHE_DIR.mkdir(exist_ok=True)
    path.write_text(json.dumps(rec, indent=1))
    rec["cached"] = False
    return rec
