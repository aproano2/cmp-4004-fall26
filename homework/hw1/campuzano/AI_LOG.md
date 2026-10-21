# AI_LOG

## Use of AI

AI assistance was used during this assignment for project scaffolding, debugging, code organization, experimental scripting, and drafting/checking explanatory text for the report.

The classical search implementations and benchmark harness were executed locally. Reported classical measurements come from the generated CSV files and were not fabricated by an AI system.

## LLM Duel

The direct LLM arm used real calls to the local `qwen2.5:3b` model through Ollama and the course `aicourse.llm` interface.

The same 80 serialized benchmark instances used by the classical experiment were presented to the model: 40 8-puzzle instances and 40 weighted-grid instances.

Raw model responses were recorded in `.llm_cache/`, and per-instance evaluation results were stored in `results/llm_responses.csv`.

The model was not used to validate its own responses. A deterministic Python validator independently checked path legality, calculated actual path cost, and compared solution cost against an A* reference.

The measured LLM outcomes reported in `REPORT.md` were calculated from these real responses. No missing LLM performance measurements were invented.

## Reproducibility Test

One weighted-grid instance (5×5, instance 8) was submitted using the same prompt five times.

The five calls produced one distinct textual answer. The first call required approximately 34 seconds, while the following calls returned essentially immediately, indicating caching by the local LLM interface.

The reproducibility transcript and metadata are stored in `.llm_cache/reproducibility_grid5_instance8.json`. Because caching was observed, the report does not characterize these five responses as statistically independent model generations.

## Tool-Augmented Arm

A tool-augmented interface was implemented in which the language model is instructed to emit a structured JSON request for the `astar` tool instead of generating the complete path itself.

Real `qwen2.5:3b` calls were used to verify that the model could emit the intended A* tool request. The deterministic A* implementation was then executed on all 80 benchmark instances and its measurements were stored in `results/tool_augmented.csv`.

The 80 rows in `tool_augmented.csv` measure execution of the selected A* tool. They are not claimed to represent 80 independent LLM inference calls. This distinction is stated explicitly in `REPORT.md`.

## Analysis and Reporting Assistance

AI assistance was used to help inspect experimental outputs, calculate and interpret aggregate results, identify missing assignment requirements, and draft portions of the written analysis.

All numerical claims included in the final report were based on locally generated experimental results. In particular, AI assistance was not used to invent benchmark measurements, LLM responses, failure counts, or tool-execution results.

## Reproducibility

Classical benchmark instances are deterministic. Weighted grids use seed `20261002`, while 8-puzzle instances are selected through deterministic breadth-first enumeration from the goal state.

The classical benchmark uses a five-second hard timeout, ten instances per level, four difficulty levels per domain, and median/IQR summaries.

The submission includes the code, raw CSV measurements, figures, LLM transcripts, and validation outputs required to inspect and reproduce the experiment.