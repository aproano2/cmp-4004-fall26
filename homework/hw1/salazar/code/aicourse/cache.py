"""Content-addressed cache for LLM responses.

Why this exists (all three reasons are course content):

1. REPRODUCIBILITY — a graded result must be re-derivable. The cache is the
   evidence that you ran what you said you ran.
2. COST — a cache hit is free. Iterating on your analysis code should not mean
   re-running 100 slow CPU inferences.
3. HONESTY — the cache is an audit trail. It makes "we ran 30 instances"
   checkable by someone who does not trust you.

You commit `.llm_cache/` to your repo. It is raw data, not build output.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path


def cache_key(backend: str, model: str, prompt: str,
              temperature: float, seed: int | None) -> str:
    """SHA-256 over everything that could change the response.

    Note what is included: temperature and seed. If you change either, you get a
    different key and a real call. That is deliberate -- a cache that ignored
    temperature would silently serve you a greedy answer when you asked for a
    sampled one.
    """
    payload = json.dumps({
        "backend": backend,
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "seed": seed,
    }, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Cache:
    """One JSON file per response, named by its key.

    One file per response rather than a single big file, for two practical
    reasons: concurrent writes never corrupt each other, and `git diff` shows
    you exactly which responses are new in a commit.
    """

    def __init__(self, root: str | os.PathLike = ".llm_cache"):
        self.root = Path(root)
        self.hits = 0
        self.misses = 0

    # -- paths ---------------------------------------------------------------
    def _path(self, key: str) -> Path:
        # Shard by the first two hex chars so no directory holds 10k files.
        return self.root / key[:2] / f"{key}.json"

    # -- read / write --------------------------------------------------------
    def get(self, key: str) -> dict | None:
        p = self._path(key)
        if not p.exists():
            self.misses += 1
            return None
        try:
            with p.open(encoding="utf-8") as fh:
                record = json.load(fh)
        except (json.JSONDecodeError, OSError):
            # A corrupt cache entry is a miss, not a crash. Students WILL
            # interrupt a run mid-write at some point.
            self.misses += 1
            return None
        self.hits += 1
        return record

    def put(self, key: str, record: dict) -> None:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        record = dict(record)
        record.setdefault("cached_at", time.strftime("%Y-%m-%dT%H:%M:%S"))
        # Write to a temp file then rename: an interrupted run leaves no
        # half-written JSON behind.
        tmp = p.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, ensure_ascii=False)
        tmp.replace(p)

    # -- introspection ------------------------------------------------------
    def __len__(self) -> int:
        if not self.root.exists():
            return 0
        return sum(1 for _ in self.root.glob("*/*.json"))

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "entries": len(self),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": (self.hits / total) if total else 0.0,
        }

    def writable(self) -> bool:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            probe = self.root / ".write-probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return True
        except OSError:
            return False
