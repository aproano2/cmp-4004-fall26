# AI Use Policy

## The short version

**You may use AI assistants on any work in this course, including the classical
implementations. You must log it.**

An undisclosed AI-assisted submission is an honor code violation. A disclosed one
is normal professional practice.

---

## Why this policy

Banning AI assistance in an AI course is incoherent, and unenforceable besides.
Pretending it doesn't affect learning is equally wrong: a student who has
Claude write their A* implementation and never reads it has skipped the single
most valuable hour of the semester.

So the policy targets the actual risk — *unexamined* delegation — rather than the
tool.

---

## The AI log

Maintain `AI_LOG.md` in your repository. Append an entry every time an AI
assistant materially shapes work you submit.

```markdown
## Week 4 — A* implementation

**Tool:** Claude / ChatGPT / Copilot / local model
**What I asked:** "Why is my A* returning suboptimal paths on grid 7?"
**What I got:** Pointed out I was checking the goal on generation rather than
  on expansion, which breaks optimality with non-uniform costs.
**What I did with it:** Moved the goal test into the expansion step. Re-read
  R&N §3.4 to confirm why generation-time testing breaks the optimality
  argument. Wrote `test_optimality_nonuniform_cost` to pin it.
**Did I understand it?** Yes — I can now explain why the frontier ordering
  matters. Initially I did not; I thought the two were equivalent.
```

That last field is the one that matters. It is also the one that catches
students out, because writing "no" is allowed — and writing "yes" when you can't
defend it in a checkpoint is not.

### What needs logging

| Situation | Log it? |
|---|---|
| AI wrote code you submitted | **Yes** |
| AI explained a concept and you then wrote the code | **Yes** |
| AI debugged your code | **Yes** |
| AI drafted or edited your report prose | **Yes** |
| AI generated your test cases | **Yes** |
| The LLM *is the subject of the experiment* (every duel) | No — that's in the report |
| Autocomplete finishing a variable name | No |
| You read the official docs, which happen to be AI-generated | No |

### Grading

The log is worth credit in every duel:

- **Complete, reflective log** — full marks. A log showing you got stuck, got
  help, and then went and understood the underlying idea is *exactly* the
  behavior this course wants.
- **Present but hollow** ("used AI to help with code") — partial.
- **Absent when the code says otherwise** — treated as an honor code matter.

There is no penalty for heavy AI use. There is a penalty for hiding it, and
there is a natural consequence for not understanding your own submission: the
checkpoints are closed-book and ask you to reason about algorithms by hand.

---

## The checkpoint backstop

Two checkpoints (weeks 7 and 13) are individual, closed-book, and ask you to:

- Trace an algorithm by hand on a small instance
- State what a technique guarantees and under exactly what condition
- Read an unfamiliar snippet and identify what breaks

No AI can sit those for you. This is deliberate: it means the policy above can
stay permissive without the degree becoming meaningless. If you have genuinely
understood the work your log describes, the checkpoints are straightforward.

---

## A note on the irony

You are in a course about comparing classical algorithms to language models,
using language models, while logging your use of language models. Take the
meta-lesson seriously: the discipline of recording what a tool did for you, and
whether you understood it, is the same discipline that makes the duel reports
credible. Both are about the difference between *having an answer* and *being
able to defend it*.
