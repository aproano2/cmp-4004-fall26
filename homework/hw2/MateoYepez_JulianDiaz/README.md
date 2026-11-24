# Homework 2 — SAT formalization harness

The implementation is in `satlab/` instead of `code/`: the latter shadows Python's standard-library `code` module and breaks pytest/pdb on this environment. `student_lastname/` and the report's team-member marker are placeholders; no personal names were inferred. The original `hw2.md` and `HW2-SAT-dataset/` are untouched.

## Install and run

Python 3.11+ on POSIX, in the main thread (the deadline adapter uses SIGALRM):

```bash
cd homework/hw2/student_lastname
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m satlab.cli validate
python -m satlab.cli run --arm A --repeats 3
python -m satlab.cli analyze
python -m satlab.cli plot
python -m satlab.cli report
python -m satlab.audit
```

The four figures include explicit pending labels for missing arms. No missing model experiment is filled with a fabricated zero. The current real dataset is 20 instances, not 60 independent problems. The user selected the installed local Llama 3.1 8.0B Q4_K_M model; its exact digest is saved in `results/provider_snapshot.json`. A 120-second preflight timeout is preserved separately under `results/pilot_timeout120/`; the main local campaign uses a 300-second LLM timeout. Read `results/summary.csv` and `REPORT.md` for actual completed runs.

## Configure a model

Copy `.env.example` to `.env`, then choose exactly one provider:

* `LLM_PROVIDER=openai-compatible`, a model supported by your endpoint, `LLM_BASE_URL` ending in `/v1`, and `LLM_API_KEY`. This client uses the chat-completions contract with `temperature` and `max_tokens`; choose a model/endpoint supporting those fields. Unsupported parameters become explicit API errors; no silent retry changes the experiment.
* `LLM_PROVIDER=ollama`, an already installed local model's exact name, and `LLM_BASE_URL=http://localhost:11434`. Start your Ollama server separately. No API key is needed for this local endpoint. Record parameter size in `LLM_MODEL_SIZE` when known. Pin a model version/digest externally where possible.

Leave price fields blank if unknown. For hosted models supply input/output USD per million tokens and a documented `PRICE_SOURCE` and `PRICE_DATE`. For local models supply `LOCAL_PRICE_PER_HOUR` or equivalent token prices. All monetary values are estimates/scenarios, not verified invoices. No tariff is bundled. Seeds are optional and not supported by every compatible endpoint; omit `LLM_SEED` when unsupported. Repetitions get distinct cache keys even at temperature zero; this does not guarantee different or statistically independent outputs.

```bash
python -m satlab.cli run --all --repeats 3
# Or separate runs, keeping the same configuration:
python -m satlab.cli run --arm B --repeats 3
python -m satlab.cli run --arm B-prime --repeats 3
python -m satlab.cli run --arm C --repeats 3
python -m satlab.cli run --arm B --problems sat_01 sat_02 --levels easy --repeats 1
python -m satlab.cli run --arm B --provider ollama --model YOUR_INSTALLED_MODEL --no-cache
python -m satlab.cli run --help
```

Without configuration, an LLM command exits with a clear error and creates no fake model results. The tests inject a simulated HTTP transport only in temporary pytest directories. There is no production mock mode or reuse of fixtures as experimental evidence.

## Protocol and architecture

* `dataset.py` exposes a whitelist of public fields; `validation.py` supplies an independent exhaustive oracle. All 20 original files are preserved byte-for-byte.
* `vendor/week07_dpll.py` is an unchanged copy of `studios/week-07/dpll.py`. `solver_adapter.py` adds deadlines, explicit states, complete witnesses and verification. There is no third-party SAT solver. Duplicate literals are converted to sets only at the existing engine boundary, preserving propositional semantics; raw clauses remain unchanged in artifacts.
* `llm_client.py` implements provider calls, structured call logs, cache keys and token/cost accounting. `prompts.py` and `parser.py` enforce fixed prompts and strict JSON. Fences, duplicate JSON keys, booleans as literals and unknown variables are rejected, never repaired silently. Empty clauses are legitimate UNSAT constraints; tautologies and duplicates are logged as warnings.
* `arm_a.py`, `arm_b.py`, `arm_b_refinement.py`, `arm_c.py` execute the four pipelines. B′ reuses the exact initial B attempt, including across separate commands. If B′ is run first, its B generation is saved as a paired checkpoint for a later B run. No reference data is passed into refinement.
* `taxonomy.py` is privileged evaluation only: exhaustive solution-set comparisons distinguish strict subsets, supersets and incomparable models. Correct SAT/UNSAT status can coexist with semantic error. Clause differences do not automatically prove a linguistic error. Quantifier/arity errors are not applicable to propositional CNF.
* `experiment.py` persists individual artifacts and resumable checkpoints; `metrics.py`, `plotting.py`, `reporting.py` generate offline deliverables.

B′ stops on valid SAT **or** UNSAT. Only parse/schema/solver failures or solver timeouts trigger a maximum of three corrections after generation zero. API failures and LLM timeouts stop as infrastructure failures. This conservative policy follows the user's clarification of the assignment: an observed UNSAT is not evidence that the translation is wrong. C's schema is checked, but its unstructured explanation is not claimed to have an automatic semantic consistency validator.

## Resume, timing and costs

Resume is enabled by default and uses instance/configuration/repetition identities. `--no-resume` explicitly reruns selected units; combine with `--no-cache` to make new calls. Run B first when intentionally replacing a pair's initial response. Keep B and B′ parameters identical. Completed units are persisted after each run; intermediate repairs are checkpointed. Single-process execution is supported; concurrent writers to the same output directory are not.

`results/runs.csv` has one row per arm/instance/repetition. `results/artifacts/` retains all intermediate attempts and raw responses even with caching disabled. `.llm_cache/` stores successful HTTP responses and original call timings; failed requests remain in `results/calls.jsonl` and are not cached. `cache_hit` means a response-cache read, not reuse of the paired B artifact. Paired reuse is an experimental dependency, not a second model call. Do not sum standalone B and B′ latency or cost as physical experiment consumption.

`wall_clock_seconds` is the actual measured current arm invocation; `llm_time_seconds` retains original generation latency and `pipeline_time_seconds` reconstructs full policy computation, including B's shared initial step for B′. Cache read time is separate. These reconstructed policy times can exceed measured wall time when calls/checkpoints are reused. Solver and parser time are separate. Physical request costs are in `analysis.json`; standalone policy costs, including all repairs, are in `costs.csv`. Tokens on API failures are labeled estimates and do not establish billable usage. Unknown prices and zero-correct denominators remain undefined.

Different model/protocol configurations should use separate copies of the project/output directory. Analysis refuses mixed LLM campaigns or duplicate arm/instance/repetition units rather than silently pooling them. Per-instance and per-repeat aggregations accompany the aggregate scorecard. Missing arms and undefined detection rates stay pending/N/A.

## Offline regeneration and evidence

```bash
python -m satlab.cli analyze
python -m satlab.cli plot
python -m satlab.cli report
python -m satlab.audit
```

These commands never instantiate the LLM client. `report` regenerates technical `REPORT.md` and `taxonomy.md`; keep personal declarations in `AI_LOG.md`, which is never rewritten by it. Existing `Team members:` lines are retained. Do not put personal prose into autogenerated report sections without keeping a separate copy.

Outputs: `runs.csv`, `summary.csv`, `costs.csv`, `refinement.csv`, `errors.csv`, `attempts.csv`, `by_instance.csv`, `by_repeat.csv`, `by_difficulty.csv`, `dataset_structure.csv`, `dataset_validation.json`, `experiment_metadata.json`, `analysis.json`, four PNG figures, `taxonomy.md`, and a report capped at 2500 words. `errors.csv` includes every status failure plus semantic mismatches despite correct status; infrastructure categories are distinct. At least five **real** outputs can be illustrated only after model calls exist.

API contracts consulted: [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md), [OpenAI Chat API reference](https://developers.openai.com/api/reference/typescript/resources/chat). This client targets the common chat contract, not every provider-specific feature.

Infrastructure errors are persisted and stop a campaign to avoid repeated failed requests. Resolve the service issue, rerun the affected B unit with `--no-resume --no-cache`, then rerun its B′ pair with `--no-resume`. Do not combine different timeout protocols in an accuracy comparison.

`python -m satlab.audit` checks all persisted call prompts against the public templates, paired response equality, iteration budgets, token/time totals, original dataset hashes, PNG signatures and report length. `results/acceptance_audit.json` distinguishes software validity from complete experimental coverage. Explicit reruns archive previous unit artifacts under `results/history/`.
