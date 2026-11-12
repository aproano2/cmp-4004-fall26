# CMP-4004 — Week 0

Self-paced, due **before our first class**. About 2 hours, most of
it waiting on a download.

Everything in this course runs on your own laptop: **no GPU, no paid API, no cloud
account, no credit card.** If you cannot install a local model there is a supported
fallback, and you lose no marks for using it.

---

## 1 · Start the model download now (~2 GB)

Install [Ollama](https://ollama.com), then run this and let it work while you read on:

```bash
ollama pull qwen2.5:3b       # ~2 GB, needs ~4 GB free RAM
ollama pull qwen2.5:1.5b     # use this one instead if you have ≤8 GB RAM
```

> **If Ollama will not install, you are not behind.** The notebook has a manual
> backend that works with any chat interface you can open in a browser. You will run
> smaller experiments, say so in your write-up, and lose nothing.

## 2 · Set up Python

From **this folder** (the one containing `aicourse/`):

```bash
python3 --version            # need 3.10+
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m aicourse.doctor
```

Run `doctor` until it prints `→ Ready.`, then save its output:

```bash
python -m aicourse.doctor > doctor.txt
```

⚠️ **Run everything from this folder.** If you see
`ModuleNotFoundError: aicourse`, that is why, Python cannot see the course
package from anywhere else.

If the LLM line says `manual`, **that is a pass, not a failure.**

## 3 · Read the slides

`week0-slides.md`: plain markdown, slides separated by `---`. Read it in VS Code,
on the web, or in any text editor.

## 4 · Do the notebook

```bash
jupyter lab                  # launch from THIS folder
```

Open **`week0.ipynb`** and run it top to bottom. Safe to "Run All" on any backend:
cells that need a live model detect its absence, skip, and **print the exact
prompts for you to run by hand.**

Five sections. **§3, parsing, is the most important twenty minutes of the week**,
every graded project later in the term depends on it. If you skip a section, don't
let it be that one.

1. Environment check
2. Calling an LLM programmatically, with a cache
3. **Turning model prose into typed data, with an explicit "could not parse" outcome**
4. Prompting as a controlled variable
5. Your first measured comparison: `sorted()` vs. an LLM at n = 5, 10, 20, 40

**Expect the LLM to do badly at n = 40.** That is the correct result, not a bug in
your work.

---

## What to hand in

| # | What | Where |
|---|---|---|
| 1 | `doctor.txt` | your `week00/` folder |
| 2 | `first_comparison.md`: the summary table and scorecard from §6, **all four TODOs filled in** | your `week00/` folder |
| 3 | One Failure Atlas entry, format below | class forum |
| 4 | One reply to a classmate, naming something *specific* | class forum |
| 5 | `AI_LOG.md`, started | your repo root |

Keep your work in one folder (or repo) for the whole semester, with a `week00/`
subfolder for this week. **Also keep the `.llm_cache/` folder the notebook creates.
Do not delete it.** The cache is not an optimization, it is your audit trail: it
is what makes "I ran 30 instances" checkable rather than just asserted.

### Failure Atlas entry format

Copy this shape exactly. You will write one every week.

```markdown
### [Wk0] LLM drops an element when sorting 40 integers
**Setup:** qwen2.5:3b, temp 0, "reply with only the sorted list"
**Classical:** sorted(). Correct, O(n log n), 0.00002 s
**LLM:** returned 39 of the 40 numbers, correctly ordered.
  Missing: 491. No hedging, no mention of uncertainty.
**Category:** wrong-but-confident | malformed | invalid | refused | timeout
**Why it matters:** The output LOOKS right. Sorted order is the thing you'd
  eyeball, and it was fine. Only a multiset check catches this. Any pipeline
  consuming this output silently loses data.
```

**"Why it matters" is the part that counts.** One sentence: what would break if you
shipped it?

For the reply, name something specific. An alternative explanation, a way to test
their claim, or a related failure you hit. One or two sentences is enough.

---

## Using AI in this course

**You may use AI assistants on any work in this course, including the classical
implementations. You must log it.** An undisclosed AI-assisted submission is an
honor code violation; a disclosed one is normal professional practice. There is no
penalty for AI use, only for hiding it.

Keep `AI_LOG.md` in your repo and append an entry whenever an assistant materially
shapes work you submit:

```markdown
## Week 0 — the sorting verifier

**Tool:** Claude / ChatGPT / Copilot / local model
**What I asked:** "Why does my verifier accept a list that is missing a number?"
**What I got:** Pointed out I was checking order but not the multiset.
**What I did with it:** Added a Counter comparison and a test case that fails
  without it.
**Did I understand it?** Yes, I can explain why order alone is not enough.
```

**That last field is the one that matters**, and writing "no" is allowed. Log it if
an assistant wrote code you submitted, explained a concept you then implemented,
debugged your code, drafted your prose, or generated your test cases. You do not
log autocomplete finishing a variable name, and you do not log the LLM's own
outputs when the LLM *is* the experiment. Those belong in the report.

Two checkpoints later in the term are individual and closed-book, and ask you to
trace algorithms by hand. That is what lets this policy stay permissive.

---

## If something breaks

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: aicourse` | run Python/Jupyter from this folder |
| Ollama: `connection refused` | run `ollama serve` in another terminal |
| Ollama: `model not found` | `ollama pull qwen2.5:3b` (or `:1.5b`) |
| unbearably slow | use `:1.5b`, cut the instance count; the cache means you pay **once** |
| nothing works at all | use the manual backend. `LLM(backend="manual")`. **A supported path.** |

**Ask on the forum, early.** A toolchain problem posted this week costs someone
fifteen minutes; the same problem the night before a graded project costs you a
grade. If you cannot get *any* backend working, submit `doctor.txt` plus the
classical half of the comparison and tell me. This will not become a zero.

---

## Bring one thing to the first class

> ### Which will win more of the fourteen comparisons this term: the classical algorithm, or the LLM?

**Write your answer down before you start.** Commit to a number. We come back to it
in week 14.
