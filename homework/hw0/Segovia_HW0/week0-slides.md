---
marp: true
theme: default
paginate: true
header: 'CMP-4004 · Week 0 · Getting Ready'
---

<!-- Self-paced. Read this, then work through week0.ipynb. -->

# Week 0 — Getting Ready

## Programming *with* an LLM, not chatting with one

**CMP-4004** · self-paced · do this before our first class

---

# What this course does

In this semester, you will build a classical AI algorithm, then **measure it
against an LLM doing the same task.**

| | |
|---|---|
| Weeks 3–11 | search, logic, planning, optimization, **with proofs** |
| Weeks 12–14 | probability, sequence models, neural networks |
| **Every week** | **a measured comparison, and a scorecard** |

The classical material is **not history**. It is the **control group.**

> ## This is not an anti-LLM course, and not an LLM-hype course.
> ## It is a course about knowing what you can prove.

---

# Why Week 0 exists

The comparison is only worth something if **the LLM side is done properly.**

| Chatting with a model | Programming with one |
|---|---|
| interactive | **batched** |
| forgiving | **parsed and validated** |
| unreproducible | **cached and seeded** |
| one answer | **120 instances and a curve** |

You are going to put numbers in a report that someone will challenge. Week 0 is
where you build the machinery that makes those numbers defensible.

**Budget: 90–120 minutes, plus download time.**

---

# What you need (and what you do *not*)

## Required

- **Python 3.10+** and about 15 minutes of `pip install`
- Any laptop. **4 cores and 8 GB RAM is enough.**

## ⚠️ NOT required — ever, for full marks

- A GPU
- A paid API key
- A cloud account
- A credit card

Every lab in this course runs on the weakest realistic machine. That is a design
constraint, not an aspiration.

---

# Three LLM backends. The third always works.

| Backend | What it needs | Speed |
|---|---|---|
| **`ollama`** | ~2 GB download, 4 GB free RAM | 5–20 tokens/s on CPU |
| **`api`** | your own key, if you happen to have one | fast |
| **`manual`** | **any chat interface, anywhere** | slow but universal |

## `LLM backend: manual` is a PASS

If Ollama will not install on your machine, **you are not behind.** You will paste
prompts into a chat window, run smaller benchmarks, note the reduced *n* in your
report, and **lose no marks for it.**

Ask for help early if you are stuck. A problem posted on Thursday is fifteen
minutes of someone's time.

---

# Why a *small* local model is better here

`qwen2.5:3b` is not very good. **That is the point.**

- Its failures are **frequent**, **visible**, and **instructive**
- When a 3B model fabricates an invalid A\* path, the lesson lands
- When a frontier model gets it right, it does so for reasons you **cannot
  inspect**, and you learn nothing about *why*

> ## You are studying the failure modes of a class of system.
> ## A system that rarely fails is a bad specimen.

---

# ⚠️ The hard part: prose is not data

An LLM returns **text**. Your experiment needs a **number**.

All ten of these are reasonable answers to *"what is 2+2?"*:

````
4                                    Four.
The answer is 4.                     ```\n4\n```
4.0                                  The answer is 4. Let me explain...
**4**                                Sure! 42 is the answer? No — 4.
I think it's 4, but it depends       (empty string)
````

`int(text.strip())` handles **one** of them.

The gap between prose and data is where **silent measurement errors** live, and
the notebook makes you feel it before it can cost you a grade.

---

# The fix, in priority order

## 1 · Constrain the format in the prompt

Cheapest and most effective. `"Reply with exactly: ANSWER: <number>"`

## 2 · Parse defensively

Return `(value, failure_mode)`. Have an explicit **"could not parse"** outcome.

## 3 · ⚠️ Never silently coerce

> A `None` that you **counted** is a data point.
> A `0` that you **invented** is a lie in your results table.

### The case that teaches the most

`"42 is the answer to 2+2? No — 4."` → two numbers, no marker.

First-number and last-number parsers **disagree**, and both are guesses dressed as
measurements. The honest answer is `ambiguous`, and it belongs in your
**failure-mode** column, not your accuracy column.

---

# The cache is not an optimization

Every call is stored, keyed by `SHA-256(backend, model, prompt, temperature, seed)`.

| Reason | Why it is course content |
|---|---|
| **Reproducibility** | a graded claim must be re-derivable |
| **Cost** | you will rewrite your analysis ten times; inference is slow |
| **Honesty** | it makes *"we ran 30 instances"* **checkable** |

## You commit `.llm_cache/` to your repo

It is **raw data**, not build output. It is the evidence behind your claims.

---

# ⚠️ Your parser is part of your experiment

Two ways to accidentally cheat, both common, both easy to avoid:

## Tuning the parser until the LLM looks good

Then you have measured **your parser**. Write it *before* you see the results, and
report how many outputs it failed to parse.

## Trying four prompts and reporting the best

That is **p-hacking**. Legitimate procedure:

1. Choose your prompt on a small **development set**
2. **Freeze it**
3. *Then* run the benchmark
4. State in the report which prompt you used and how you chose it

**Give both sides the same care.** An hour tuning the prompt and a default
heuristic is not a fair comparison.

---

# The verifier: today's real lesson

Your first comparison is **sorting a list of integers**: trivial classically,
**exactly verifiable**, and it scales.

The verifier checks three things **separately**:

| Check | Failure mode | What it means |
|---|---|---|
| parses at all | `malformed` | output was not a list |
| same multiset | `invalid` | **dropped or invented numbers** |
| non-decreasing | `wrong-but-confident` | right numbers, wrong order |

Lumping these together as "wrong" throws away the most interesting part of your
data. A model that drops one element has a **different** problem from one that
mis-orders.

---

# ⚠️ Test the verifier before you trust it

The notebook asserts it against five cases with known answers **before** using it
on a single model output.

> ## A broken verifier does not crash.
> ## It silently produces a plausible number that you then publish.

You will meet this exact lesson twice more:

| Week | The verifier |
|---|---|
| **0** | your sort checker |
| **9** | a sound plan validator — *the keystone of the course* |
| **14** | gradient checking your own backprop |

---

# The pattern you will use fourteen times

```
        ┌─────────────┐
        │  instances  │   several sizes, fixed seed
        └──────┬──────┘
      ┌────────┴────────┐
      ▼                 ▼
┌───────────┐    ┌─────────────┐
│ classical │    │ LLM + parse │  ← prose becomes data here
└─────┬─────┘    └──────┬──────┘
      └────────┬────────┘
               ▼
        ┌─────────────┐
        │  VERIFIER   │  ← sound, tested, trusts nobody
        └──────┬──────┘
               ▼
   scorecard + scaling curve + honesty section
```

Every duel is this diagram with a different box in the middle.

---

# One point is not a curve

The scorecard has eight axes. **Axis 6 is where this course lands.**

```
solve rate
  100% |●———●———●———●     ← classical (flat: cost grows, correctness doesn't)
       |     ○———○
   50% |          ╲○
       |            ╲
    0% |              ○   ← LLM (the cliff)
       +——————————————————
        4    8   12   16    problem size
```

**Minimum for every duel: four problem sizes, ten instances each.**

If your plot shows **no** cliff, that is an interesting result — but you must show
the plot.

---

# The axis students undervalue

## Axis 2: Guarantee

These are **not** the same kind of claim:

> `sorted()` returns a permutation of its input in non-decreasing order, for
> **every** input, in O(n log n). **No condition.**

> The LLM produced a correct sort on 12/20 instances.
> **No claim is made about the 21st.**

Telling those apart is the entire subject of this course.

State every guarantee as a **conditional**: *A\* is optimal **provided** `h` never
overestimates.*

---

# We grade the experiment, not the verdict

| Score | Meaning |
|---|---|
| 0 | not addressed |
| 1 | asserted ("it was faster") |
| 2 | measured once |
| 3 | measured across instances, with a statistic |
| 4 | **across instances *and* sizes, with variance and a stated limitation** |

> ## A careful study concluding "the LLM won" scores higher than a sloppy study
> ## concluding "classical won."

### And every report has a section titled *"Where we may have been unfair"*

It is worth real credit. **A student who finds a genuine flaw in their own
experiment has learned the thing this course is actually teaching.**

---

# Your Week 0 deliverable

In `week00/` of your course repo, before our first class:

| # | File | What |
|---|---|---|
| 1 | `doctor.txt` | output of `python -m aicourse.doctor` |
| 2 | `first_comparison.md` | your table + scorecard, **all four TODOs filled in** |
| 3 | *(forum)* | **one** Failure Atlas entry, in the required format |
| 4 | *(forum)* | **one** reply to a classmate, naming something specific |
| 5 | `AI_LOG.md` | started — used an assistant? log it. That is allowed. |

Small credit. Mostly it means **your toolchain works before it matters**, and we
never spend studio time on `PATH` problems.

---

# Failure Atlas entry format

Copy this shape exactly. You will write one every week.

```markdown
### [Wk0] LLM drops an element when sorting 40 integers
**Setup:** qwen2.5:3b, temp 0, "reply with only the sorted list"
**Classical:** sorted() — correct, O(n log n), 0.00002 s
**LLM:** returned 39 of the 40 numbers, correctly ordered.
  Missing: 491. No hedging, no mention of uncertainty.
**Category:** invalid
**Why it matters:** The output LOOKS right. Sorted order is the thing you'd
  eyeball, and it was fine — only a multiset check catches this. Any pipeline
  consuming this output silently loses data.
```

**"Why it matters" is the part that counts.** One sentence: what would break if
you shipped it?

---

# If something is broken

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: aicourse` | run Jupyter from the `cmp4004-week0/` folder (the one containing `aicourse/`) |
| ollama: `connection refused` | `ollama serve` in another terminal |
| ollama: `model not found` | `ollama pull qwen2.5:3b` (or `:1.5b` if ≤ 8 GB RAM) |
| unbearably slow | use `:1.5b`; cut instances; the cache means you pay **once** |
| nothing works at all | `LLM(backend="manual")` — **a supported path** |

## Ask early

A toolchain problem posted **Thursday** costs someone fifteen minutes.
The same problem at **11 pm before Duel 1** costs you a grade.

---

# Start the model download *now*

`qwen2.5:3b` is about **2 GB**.

Not tonight. Not before class. **Now**, while you read the rest of this.

```bash
ollama pull qwen2.5:3b
```

---


# Bring one thing to Session 1A

> # Which will win more of the fourteen duels, the classical algorithm, or the LLM?

**Write your answer down.** Commit to a number.

We check it in **week 14**, next to the sealed prediction you will write in
Session 1A.

> ## Being wrong in public, on the record, with data. That is the job.


