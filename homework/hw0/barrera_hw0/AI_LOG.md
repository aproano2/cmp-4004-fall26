# AI_LOG — CMP-4004

Log of AI assistance that materially shaped submitted work, per the course policy in
START-HERE.md (§ Using AI in this course).

## Week 0 — environment setup and write-up

**Tool:** Claude
**What I asked:** I did not know how to do the Week 0 assignment. I shared START-HERE.md and
week0.ipynb and asked for help doing it, step by step.
**What I got:**
- Step-by-step guidance to install Ollama, pull qwen2.5:3b, set up Python on Windows, and run
  `aicourse.doctor` and the notebook (I ran all commands on my machine; the notebook's LLM
  calls are the real model's answers, cached in `.llm_cache/`).
- Debugging help: a PowerShell execution-policy error when activating the venv, a doctor.txt
  saved with broken encoding by PowerShell's `>` redirect (fixed with `cmd /c` + UTF-8), and
  diagnosing that a second terminal had auto-activated the venv without the packages.
- Analysis of my cached results (it identified the n10-3 failure where the model replaced 851
  with an invented 390), and a first draft of `first_comparison.md` (scorecard TODOs and the
  four §6 answers) and of my Failure Atlas entry, based on my actual run data. I reviewed and
  am responsible for the final text.
**What I did with it:** Followed the setup steps, ran the notebook myself, and reviewed/edited
the drafted write-up before submitting it.
**Did I understand it?** Yes. The model's answer on n10-3 looks correct because it is
perfectly ordered, but it is not the original data: 851 disappeared and an invented 390 took
its place. If a program consumed that list believing it was right, it would keep running on
corrupted data and cause problems later, with no error at the moment it happened. That is why
checking order alone is not enough — the verifier also has to check that the output contains
exactly the same numbers as the input (the multiset check).
