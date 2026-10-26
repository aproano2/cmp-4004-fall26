"""LLM backends + the transcript cache (.llm_cache/, commit it).

Three backends, same interface:
    manual     you paste prompts into a chat UI yourself (5 instances/level allowed)
    ollama     local model served by Ollama   (http://localhost:11434)
    anthropic  your own API key (ANTHROPIC_API_KEY)   [pip install anthropic]
    mock       only used by test_duel.py

Every call is cached by sha256(model, temperature, system, messages, sample,
prompt version). Re-running never re-spends calls and the transcripts ARE your
evidence for the report.
"""
import hashlib
import json
import os
import time
import urllib.request

from duel_common import CACHE_DIR, PROMPT_VERSION


class NeedManual(Exception):
    """Raised by the manual backend when a human must supply a response."""

    def __init__(self, key, system, messages):
        super().__init__(key)
        self.key, self.system, self.messages = key, system, messages


class Backend:
    name = "base"

    def __init__(self, model="", temperature=1.0, max_tokens=4096):
        self.model, self.temperature, self.max_tokens = model, temperature, max_tokens

    # -- cache -------------------------------------------------------------
    def key(self, system, messages, sample):
        blob = json.dumps([self.name, self.model, self.temperature, system,
                           messages, sample, PROMPT_VERSION], sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()[:12]

    def call(self, system, messages, sample=0):
        """Return dict(text, latency_s, in_tokens, out_tokens, cached, key)."""
        CACHE_DIR.mkdir(exist_ok=True)
        key = self.key(system, messages, sample)
        path = CACHE_DIR / f"{key}.json"
        if path.exists():
            rec = json.loads(path.read_text())
            rec["cached"] = True
            return rec
        text, latency, tin, tout = self._generate(key, system, messages)
        rec = dict(key=key, backend=self.name, model=self.model,
                   temperature=self.temperature, sample=sample,
                   prompt_version=PROMPT_VERSION, system=system,
                   messages=messages, text=text, latency_s=latency,
                   in_tokens=tin, out_tokens=tout,
                   timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"))
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
        rec["cached"] = False
        return rec

    def _generate(self, key, system, messages):
        raise NotImplementedError


class ManualBackend(Backend):
    """You are the backend. Missing responses are exported to pending.md."""
    name = "manual"

    def __init__(self, model="manual-chat", **kw):
        super().__init__(model=model, **kw)

    def _generate(self, key, system, messages):
        resp = CACHE_DIR / "manual" / "responses" / f"{key}.txt"
        if resp.exists():
            return resp.read_text().strip(), None, None, None
        raise NeedManual(key, system, messages)


class OllamaBackend(Backend):
    name = "ollama"

    def _generate(self, key, system, messages):
        body = json.dumps({
            "model": self.model, "stream": False,
            "messages": [{"role": "system", "content": system}] + messages,
            "options": {"temperature": self.temperature,
                        "num_predict": self.max_tokens},
        }).encode()
        req = urllib.request.Request(
            os.environ.get("OLLAMA_URL", "http://localhost:11434") + "/api/chat",
            data=body, headers={"Content-Type": "application/json"})
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.loads(r.read())
        return (d["message"]["content"], time.perf_counter() - t0,
                d.get("prompt_eval_count"), d.get("eval_count"))


class AnthropicBackend(Backend):
    name = "anthropic"

    def _generate(self, key, system, messages):
        import anthropic  # pip install anthropic
        client = anthropic.Anthropic()
        t0 = time.perf_counter()
        r = client.messages.create(model=self.model, max_tokens=self.max_tokens,
                                   temperature=self.temperature,
                                   system=system, messages=messages)
        text = "".join(b.text for b in r.content if b.type == "text")
        return (text, time.perf_counter() - t0,
                r.usage.input_tokens, r.usage.output_tokens)


def get_backend(name, model, temperature):
    if name == "manual":
        return ManualBackend(temperature=temperature)
    cls = {"ollama": OllamaBackend, "anthropic": AnthropicBackend}[name]
    return cls(model=model, temperature=temperature)


# ---------------------------------------------------------------------------
# Manual workflow helpers
# ---------------------------------------------------------------------------

def write_pending(pending):
    """pending: list of NeedManual. Writes .llm_cache/manual/pending.md"""
    d = CACHE_DIR / "manual"
    (d / "responses").mkdir(parents=True, exist_ok=True)
    lines = ["# Pending prompts\n",
             "For each block: open a NEW chat, paste the text under 'SEND THIS'. "
             "For blocks marked CONTINUE, send it in the SAME chat as the previous step.\n"
             "Then copy the model's full reply into responses.md under a line "
             "`### <KEY>` (see DUEL_GUIDE.md).\n"]
    for n in pending:
        msgs = n.messages
        lines.append(f"\n---\n## KEY: {n.key}\n")
        if len(msgs) > 1:
            lines.append("(CONTINUE the same chat; earlier turns shown for reference)\n")
            for m in msgs[:-1]:
                lines.append(f"[{m['role']}]\n{m['content']}\n")
        if len(msgs) == 1:
            lines.append("SYSTEM / first line of chat:\n" + n.system + "\n")
        lines.append("SEND THIS:\n" + msgs[-1]["content"] + "\n")
    (d / "pending.md").write_text("\n".join(lines))
    return d / "pending.md"


def import_responses(path):
    """Parse a file with blocks '### <KEY>' + reply text -> manual/responses/."""
    import re
    d = CACHE_DIR / "manual" / "responses"
    d.mkdir(parents=True, exist_ok=True)
    txt = open(path, encoding="utf-8").read()
    parts = re.split(r"^### *([0-9a-f]{12}) *$", txt, flags=re.M)
    n = 0
    for k in range(1, len(parts) - 1, 2):
        (d / f"{parts[k]}.txt").write_text(parts[k + 1].strip())
        n += 1
    return n
