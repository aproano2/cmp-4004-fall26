# Setup

> **Students: work through [`../weeks/week-00.md`](../weeks/week-00.md) and
> [`../notebooks/week-00-programming-with-llms.ipynb`](../notebooks/week-00-programming-with-llms.ipynb)
> instead of reading this page top to bottom.** The notebook walks you through
> everything here in order, and checks each step. This page is the reference you
> come back to when something breaks.

**Design constraint:** every lab in this course runs on a student laptop with no
GPU, no paid API key, and no cloud account. Nothing is gated behind money.

Assume the weakest realistic machine: 4 cores, 8 GB RAM, integrated graphics.
Every requirement below has been chosen to fit that.

---

## 1. Core toolchain

```bash
python3 --version          # need 3.10+
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt`:

```
numpy>=1.24
matplotlib>=3.7
pytest>=7.4
pandas>=2.0
scikit-learn>=1.3      # week 12 baselines only, never for the from-scratch work
networkx>=3.1          # graph visualization only, never for search itself
pyperplan>=2.1         # week 9 STRIPS planner (GPLv3 — see note below)
requests>=2.31
```

> **Licensing note:** `pyperplan` is GPLv3. That is fine for coursework you do
> not redistribute, but if a student wants to publish a capstone repo publicly,
> point them at it — it is a genuine teaching moment about dependency licensing.

### Non-Python tooling

| Tool | Weeks | Install |
|------|-------|---------|
| SWI-Prolog | 8, 9 | `brew install swi-prolog` / `apt install swi-prolog` / [swi-prolog.org](https://www.swi-prolog.org/Download.html) |
| Git | all | preinstalled or `brew install git` |

SWI-Prolog is the only non-Python install and it has a working installer on all
three platforms. Verify with `swipl --version`.

---

## 2. LLM access without a budget

This is the part that needs care. Students have **their own laptops and nothing
else**, so the course supports two backends and requires neither specifically.

### Backend A — local model (preferred, free, scriptable)

[Ollama](https://ollama.com) runs a small model on CPU. Install it, then:

```bash
ollama pull qwen2.5:3b       # ~2 GB, runs in ~4 GB RAM
# fallback for very constrained machines:
ollama pull qwen2.5:1.5b     # ~1 GB
```

Expect roughly 5–20 tokens/second on CPU. That is slow but entirely usable for
30–100 instance benchmarks if you let them run during the studio session.

**A small local model is pedagogically better than a frontier model here.** Its
failures are frequent, visible, and instructive. When a 3B model fabricates an
invalid A* path, the lesson lands harder than when a frontier model gets it right
for reasons the student cannot inspect.

### Backend B — manual transcript (universal fallback)

Any student with access to any chat interface can run every lab by pasting
prompts and saving responses. The harness supports this explicitly:

```bash
python -m aicourse.llm --backend manual --prompts prompts/week04.jsonl
# writes prompts to stdout one at a time, reads pasted responses back,
# and stores them in the same cache format as the automated backends
```

This is slower and caps benchmark size (budget ~20 instances rather than 100),
but **no student is ever blocked**. Students using this backend report a reduced
*n* and note it in the honesty section of their report; they are not penalized.

### Backend C — student's own API key (optional)

If a student happens to have API access, the harness reads a key from the
environment. Never required, never assumed, and never necessary for full marks.

```bash
export AICOURSE_API_KEY=...      # optional
export AICOURSE_MODEL=...        # optional
```

### The cache is mandatory

All backends write to `.llm_cache/` keyed by SHA-256 of
`(backend, model, prompt, temperature, seed)`.

Three reasons this matters, all of which are course content:

1. **Reproducibility** — a graded result must be re-derivable. Cached
   transcripts are the evidence.
2. **Cost** — a cache hit is free, so iterating on analysis code does not mean
   re-running inference.
3. **Honesty** — the cache is an audit trail. It makes "we ran 30 instances"
   checkable.

**Students commit `.llm_cache/` to their repo.** It is the raw data behind their
claims.

---

## 3. Verify everything

```bash
python -m aicourse.doctor
```

Expected output:

```
✔ Python 3.11.6
✔ numpy 1.26.0, matplotlib 3.8.0, pytest 7.4.3, pandas 2.1.1
✔ pyperplan 2.1
✔ SWI-Prolog 9.0.4
✔ LLM backend: ollama (qwen2.5:3b) — responded in 2.1 s
✔ .llm_cache/ writable
→ Ready.
```

If the LLM line reports `manual`, that is a pass, not a failure.

Students run `doctor` in **Week 0** and paste the output as their first
submission. This surfaces every environment problem *before the course starts*
rather than the night before Duel 1 is due.

⚠️ **Run it from the `course-en/` directory**, or install the package first with
`pip install -e .`. Otherwise Python cannot find `aicourse` — this is the most
common Week 0 support question.

---

## 4. Repository conventions

Each student works in one repo for the whole semester:

```
cmp4004-<lastname>/
├── week00/                   doctor.txt + first_comparison.md
├── week01/ … week14/         one directory per week
├── duels/{1,2,3}/            graded duel reports + code
├── capstone/
├── .llm_cache/              committed — this is your data
└── AI_LOG.md                see resources/ai-policy.md
```

Studio sessions ship code by the end of the session. A commit timestamped during
the session is part of the participation grade — it is how attendance is measured
in a virtual class without policing cameras.
