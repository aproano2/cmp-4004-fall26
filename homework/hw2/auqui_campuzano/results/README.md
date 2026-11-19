# Results

Full four-arm run: model `allam-2-7b` (Groq, 7B), temperature 0.7, 3 repeats, 20 problems (see `run_meta.json`).
`per_instance.csv` = raw rows (one per problem x arm x repeat; model output and every refinement attempt included).
`scorecard.csv`, `accuracy_by_difficulty.csv`, `taxonomy_counts.csv`, `refinement.csv`, `cost.csv` are derived by `code/analyze.py`.
Cost uses a proxy tariff (see `pricing.csv`). All LLM calls are cached in `../.llm_cache`, so `run_experiment.py` + `analyze.py` reproduce these files without API access.
