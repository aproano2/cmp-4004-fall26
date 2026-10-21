# Duel 1 — Search

Run from the project root:

```bash
python code/benchmark.py
python code/analyze.py
```

This produces raw measurements in `results/`, summaries and required checks, and figures in `fig/`.

The LLM arm is intentionally not populated with invented measurements. Exported instances are produced with:

```bash
python code/make_instances.py
```

Then record actual model transcripts in `.llm_cache/` and evaluate them with `code/llm_duel.py`.
