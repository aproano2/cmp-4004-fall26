"""A cached, multi-backend LLM client.

Backends, in order of preference:

    ollama  — a small local model on CPU. Free, scriptable, and its failures are
              frequent and instructive, which is pedagogically better than a
              frontier model that succeeds for reasons you cannot inspect.
    api     — your own key, if you happen to have one. Never required.
    manual  — you paste prompts into any chat interface and paste answers back.
              Always works. Nobody is ever blocked.
    echo    — a deterministic fake, for testing your analysis code without
              burning inference. Not a model; do not report results from it.

Usage:

    from aicourse import LLM
    llm = LLM(backend="ollama")
    r = llm.complete("What is 2+2?")
    print(r.text, r.cached, r.elapsed)

Command line:

    python -m aicourse.llm --prompt "hello"
    python -m aicourse.llm --backend manual --prompts prompts/week04.jsonl
    python -m aicourse.llm --cache-stats
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict

from .cache import Cache, cache_key

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("AICOURSE_MODEL", "qwen2.5:3b")


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------
@dataclass
class LLMResponse:
    """One completion, plus the metadata your duel report needs."""
    text: str
    backend: str
    model: str
    prompt: str
    temperature: float = 0.0
    seed: int | None = 0
    cached: bool = False
    elapsed: float = 0.0
    error: str | None = None
    meta: dict = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.error is None and bool(self.text.strip())

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Backend availability
# ---------------------------------------------------------------------------
def _ollama_up(timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=timeout):
            return True
    except (urllib.error.URLError, OSError, ValueError):
        return False


def ollama_models(timeout: float = 2.0) -> list[str]:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=timeout) as r:
            data = json.load(r)
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


def backends_available() -> dict[str, str]:
    """What can actually run right now. Used by `doctor` and by LLM(backend='auto')."""
    out: dict[str, str] = {}
    if shutil.which("ollama") or _ollama_up():
        if _ollama_up():
            models = ollama_models()
            out["ollama"] = f"serving ({len(models)} model(s))" if models else "serving, no models pulled"
        else:
            out["ollama"] = "installed but not serving — run `ollama serve`"
    if os.environ.get("AICOURSE_API_KEY"):
        out["api"] = "AICOURSE_API_KEY is set"
    out["manual"] = "always available"
    out["echo"] = "always available (testing only — not a model)"
    return out


# ---------------------------------------------------------------------------
# The client
# ---------------------------------------------------------------------------
class LLM:
    """Cached client. Every call goes through the cache first.

    temperature defaults to 0.0 and seed to 0 because a graded comparison should
    be reproducible by default. If you want to measure variability (scorecard
    axis 5), raise the temperature ON PURPOSE and vary the seed -- that is a
    measurement, not a mistake.
    """

    def __init__(self, backend: str = "auto", model: str | None = None,
                 cache_dir: str = ".llm_cache", temperature: float = 0.0,
                 seed: int | None = 0, timeout: float = 120.0,
                 verbose: bool = False):
        self.model = model or DEFAULT_MODEL
        self.temperature = temperature
        self.seed = seed
        self.timeout = timeout
        self.verbose = verbose
        self.cache = Cache(cache_dir)
        self.calls_made = 0          # real inferences, i.e. cache misses

        if backend == "auto":
            avail = backends_available()
            if "ollama" in avail and avail["ollama"].startswith("serving") \
                    and ollama_models():
                backend = "ollama"
            elif "api" in avail:
                backend = "api"
            else:
                backend = "manual"
            if self.verbose:
                print(f"[aicourse] auto-selected backend: {backend}",
                      file=sys.stderr)
        self.backend = backend

    # -- public API ----------------------------------------------------------
    def complete(self, prompt: str, *, temperature: float | None = None,
                 seed: int | None = ..., use_cache: bool = True) -> LLMResponse:
        temp = self.temperature if temperature is None else temperature
        sd = self.seed if seed is ... else seed

        key = cache_key(self.backend, self.model, prompt, temp, sd)

        if use_cache:
            hit = self.cache.get(key)
            if hit is not None:
                return LLMResponse(
                    text=hit.get("text", ""), backend=hit.get("backend", self.backend),
                    model=hit.get("model", self.model), prompt=prompt,
                    temperature=temp, seed=sd, cached=True,
                    elapsed=0.0, error=hit.get("error"),
                    meta=hit.get("meta", {}),
                )

        t0 = time.perf_counter()
        try:
            text, meta = self._dispatch(prompt, temp, sd)
            err = None
        except Exception as exc:                      # noqa: BLE001
            text, meta, err = "", {}, f"{type(exc).__name__}: {exc}"
        elapsed = time.perf_counter() - t0
        self.calls_made += 1

        resp = LLMResponse(text=text, backend=self.backend, model=self.model,
                           prompt=prompt, temperature=temp, seed=sd,
                           cached=False, elapsed=elapsed, error=err, meta=meta)
        if use_cache and err is None:
            # Never cache an error: the next run should retry, not inherit a
            # network hiccup forever.
            self.cache.put(key, {"text": text, "backend": self.backend,
                                 "model": self.model, "prompt": prompt,
                                 "temperature": temp, "seed": sd,
                                 "elapsed": elapsed, "meta": meta})
        return resp

    def complete_many(self, prompts, *, progress: bool = True, **kw):
        """Sequential by design -- a 3B model on CPU is not helped by threads,
        and sequential output is far easier to debug in a classroom."""
        out = []
        n = len(prompts)
        for i, p in enumerate(prompts, 1):
            r = self.complete(p, **kw)
            out.append(r)
            if progress:
                flag = "cache" if r.cached else f"{r.elapsed:5.1f}s"
                print(f"  [{i:>3}/{n}] {flag}  {p[:52]!r}", file=sys.stderr)
        return out

    # -- backends ------------------------------------------------------------
    def _dispatch(self, prompt: str, temperature: float, seed: int | None):
        fn = {
            "ollama": self._ollama,
            "api": self._api,
            "manual": self._manual,
            "echo": self._echo,
        }.get(self.backend)
        if fn is None:
            raise ValueError(f"unknown backend {self.backend!r}")
        return fn(prompt, temperature, seed)

    def _ollama(self, prompt, temperature, seed):
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if seed is not None:
            body["options"]["seed"] = seed
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = json.load(r)
        meta = {k: data[k] for k in
                ("eval_count", "prompt_eval_count", "total_duration")
                if k in data}
        return data.get("response", ""), meta

    def _api(self, prompt, temperature, seed):
        """Anthropic Messages API, if the student has a key. Optional path."""
        key = os.environ.get("AICOURSE_API_KEY")
        if not key:
            raise RuntimeError("AICOURSE_API_KEY is not set")
        model = os.environ.get("AICOURSE_API_MODEL", "claude-sonnet-5")
        body = {"model": model, "max_tokens": 1024,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]}
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "x-api-key": key,
                     "anthropic-version": "2023-06-01"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            data = json.load(r)
        parts = [b.get("text", "") for b in data.get("content", [])]
        return "".join(parts), {"usage": data.get("usage", {}), "model": model}

    def _manual(self, prompt, temperature, seed):
        """The universal fallback. Paste the prompt anywhere, paste the answer back.

        End your input with a line containing only  END
        """
        print("\n" + "=" * 68, file=sys.stderr)
        print("MANUAL BACKEND — copy the prompt below into any chat interface.",
              file=sys.stderr)
        print("=" * 68, file=sys.stderr)
        print(prompt)
        print("=" * 68, file=sys.stderr)
        print("Paste the response, then a line with only END", file=sys.stderr)
        if not sys.stdin.isatty():
            # Non-interactive (nbconvert, pytest, a piped script): there is
            # nobody to paste an answer. Fail LOUDLY rather than returning ""
            # and letting the caller record an empty response as data.
            raise RuntimeError(
                "manual backend needs an interactive terminal; stdin is not a TTY. "
                "Run this cell interactively, or use backend='echo' to exercise "
                "the plumbing without a model.")
        lines = []
        for line in sys.stdin:
            if line.strip() == "END":
                break
            lines.append(line)
        text = "".join(lines).strip()
        if not text:
            raise RuntimeError("manual backend received an empty response")
        return text, {"elicited": "manual"}

    def _echo(self, prompt, temperature, seed):
        """Deterministic fake. For testing analysis code, never for results."""
        return (f"[echo backend] {len(prompt)} chars received. "
                f"This is NOT a model response."), {"fake": True}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="python -m aicourse.llm",
        description="Cached multi-backend LLM client for CMP-4004.")
    ap.add_argument("--backend", default="auto",
                    choices=["auto", "ollama", "api", "manual", "echo"])
    ap.add_argument("--model", default=None)
    ap.add_argument("--prompt", default=None, help="a single prompt")
    ap.add_argument("--prompts", default=None,
                    help="JSONL file with one {\"prompt\": ...} per line")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--cache-dir", default=".llm_cache")
    ap.add_argument("--cache-stats", action="store_true",
                    help="print cache stats and exit")
    ap.add_argument("--list-backends", action="store_true")
    ap.add_argument("--out", default=None, help="write responses to this JSONL")
    args = ap.parse_args(argv)

    if args.list_backends:
        for name, status in backends_available().items():
            print(f"  {name:<8} {status}")
        return 0

    if args.cache_stats:
        c = Cache(args.cache_dir)
        s = c.stats()
        print(f"cache dir : {c.root}")
        print(f"entries   : {s['entries']}")
        return 0

    if not args.prompt and not args.prompts:
        ap.error("give --prompt or --prompts (or --cache-stats/--list-backends)")

    llm = LLM(backend=args.backend, model=args.model,
              cache_dir=args.cache_dir, temperature=args.temperature,
              seed=args.seed, verbose=True)

    prompts = []
    if args.prompt:
        prompts.append(args.prompt)
    if args.prompts:
        with open(args.prompts, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    prompts.append(json.loads(line)["prompt"])

    responses = llm.complete_many(prompts, progress=len(prompts) > 1,
                                 use_cache=not args.no_cache)

    for r in responses:
        if r.error:
            print(f"[error] {r.error}", file=sys.stderr)
        else:
            print(r.text)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for r in responses:
                fh.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
        print(f"[aicourse] wrote {len(responses)} response(s) to {args.out}",
              file=sys.stderr)

    hits = sum(r.cached for r in responses)
    print(f"[aicourse] {len(responses)} prompt(s), {hits} from cache, "
          f"{llm.calls_made} real call(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
