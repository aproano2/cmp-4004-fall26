"""Duel 1 / Part 2 — the machinery shared by both domains.

``duel.py`` is the entry point; it hands one *domain* at a time to
``run_domain`` below. A domain (``duel_grid.GridDomain``,
``duel_puzzle.PuzzleDomain``) supplies only what differs between problems:
its instances, prompts, output parser, A* tool and validator. Everything else
is written once, here:

    complete()       one cached, timed LLM call
    solve_*()        the three systems: A*, bare LLM, LLM + A* tool
    run_main()       every instance x every system
    run_repro()      five calls per (instance, temperature)
    summarize*()     counts per category, rates, medians / IQR / p95
    run_domain()     results/duel/<domain>/{raw,summary,repro,repro_summary}.csv
                     + failures.md

Every answer, from every system, is scored by the domain's validator — never
by a model.
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # .../hw1/<team>/
sys.path.insert(0, str(ROOT))                           # for `aicourse`

from aicourse import LLM                                # noqa: E402
from aicourse.cache import cache_key                    # noqa: E402

from validator import CATEGORIES                        # noqa: E402

RESULTS = ROOT / "results" / "duel"
CACHE_DIR = ROOT / ".llm_cache"
DEFAULT_MODEL = "qwen2.5:3b"
MAX_TOOL_TURNS = 3
LLM_TIMEOUT_S = 600            # per call; a 3B model on CPU is ~14 tok/s
SYSTEMS = ("A*", "LLM", "LLM+tool")

RAW_FIELDS = ["system", "model", "size", "instance", "category", "correct",
              "legal", "cost_ok", "optimal_cost", "true_cost", "reported_cost",
              "path_len", "seconds", "tokens_in", "tokens_out", "tool_calls",
              "expansions", "reasons"]


def make_llm(model: str = DEFAULT_MODEL) -> LLM:
    return LLM(backend="ollama", model=model, cache_dir=str(CACHE_DIR),
               temperature=0.0, seed=0, timeout=LLM_TIMEOUT_S)


# ---------------------------------------------------------------------------
# Parsing model output. Lenient on syntax (code fences, single quotes,
# tuples), strict on content: whatever we extract goes to the validator.
# ---------------------------------------------------------------------------
def json_objects(text: str) -> list[dict]:
    """Every balanced {...} in ``text`` that parses as a JSON object."""
    out, depth, start = [], 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                chunk = text[start:i + 1]
                for cand in (chunk,
                             chunk.replace("'", '"').replace("(", "[").replace(")", "]")):
                    try:
                        obj = json.loads(cand)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(obj, dict):
                        out.append(obj)
                    break
    return out


# ---------------------------------------------------------------------------
# Timed, cached LLM calls. A cache hit reports elapsed = 0, so we read the
# ORIGINAL inference time back out of the cache record — latency must survive
# a replay.
# ---------------------------------------------------------------------------
def complete(llm: LLM, prompt: str, temperature=None, seed=...):
    r = llm.complete(prompt, temperature=temperature, seed=seed)
    if r.error:
        raise RuntimeError(f"LLM call failed: {r.error}")
    secs = r.elapsed
    if r.cached:
        t = llm.temperature if temperature is None else temperature
        s = llm.seed if seed is ... else seed
        rec = llm.cache.get(cache_key(llm.backend, llm.model, prompt, t, s)) or {}
        secs = float(rec.get("elapsed", 0.0))
    m = r.meta or {}
    return r, secs, int(m.get("prompt_eval_count", 0)), int(m.get("eval_count", 0))


# ---------------------------------------------------------------------------
# The three systems. Each returns (row-dict, raw transcript text).
# ---------------------------------------------------------------------------
def _row(system, model, size, idx, verdict, answer, seconds, t_in=0, t_out=0,
         tool_calls=0, expansions=0):
    return {
        "system": system, "model": model, "size": size, "instance": idx,
        "category": verdict.category, "correct": int(verdict.correct),
        "legal": int(verdict.legal), "cost_ok": int(verdict.cost_ok),
        "optimal_cost": verdict.optimal_cost, "true_cost": verdict.true_cost,
        "reported_cost": verdict.reported_cost,
        "path_len": len(answer) if isinstance(answer, (list, str)) else "",
        "seconds": round(seconds, 4), "tokens_in": t_in, "tokens_out": t_out,
        "tool_calls": tool_calls, "expansions": expansions,
        "reasons": "; ".join(verdict.reasons),
    }


def solve_astar(dom, inst, size, idx, opt):
    t0 = time.perf_counter()
    answer, cost, exps = dom.solve_classical(inst)
    secs = time.perf_counter() - t0
    v = dom.validate(inst, answer, cost, opt)
    return (_row("A*", "A*+manhattan", size, idx, v, answer, secs, expansions=exps),
            json.dumps({dom.answer_key: answer, "cost": cost}))


def solve_llm(dom, llm, inst, size, idx, opt, temperature=None, seed=...):
    r, secs, t_in, t_out = complete(llm, dom.llm_prompt(inst), temperature, seed)
    answer, cost = dom.parse_answer(r.text)
    v = dom.validate(inst, answer, cost, opt)
    return _row("LLM", llm.model, size, idx, v, answer, secs, t_in, t_out), r.text


def solve_tool(dom, llm, inst, size, idx, opt, temperature=None, seed=...):
    prompt = dom.tool_prompt(inst)
    secs = t_in = t_out = calls = exps = 0
    transcript = []
    for _ in range(MAX_TOOL_TURNS + 1):
        r, s, ti, to = complete(llm, prompt, temperature, seed)
        secs, t_in, t_out = secs + s, t_in + ti, t_out + to
        transcript.append(r.text)
        call = dom.parse_tool_call(r.text)
        if call is None or calls >= MAX_TOOL_TURNS:
            break
        t0 = time.perf_counter()
        result, e = dom.run_tool(inst, call)
        secs += time.perf_counter() - t0
        calls, exps = calls + 1, exps + e
        transcript.append(f"[TOOL RESULT] {json.dumps(result)}")
        prompt += dom.followup(r.text.strip(), result)
    answer, cost = dom.parse_answer(transcript[-1])
    v = dom.validate(inst, answer, cost, opt)
    if calls == 0:
        v.reasons.append("never called the tool")
    return (_row("LLM+tool", llm.model, size, idx, v, answer, secs, t_in, t_out,
                 calls, exps), "\n---\n".join(transcript))


def _solve(system, dom, llm, inst, size, idx, opt, temperature=None, seed=...):
    if system == "A*":
        return solve_astar(dom, inst, size, idx, opt)
    if system == "LLM":
        return solve_llm(dom, llm, inst, size, idx, opt, temperature, seed)
    return solve_tool(dom, llm, inst, size, idx, opt, temperature, seed)


# ---------------------------------------------------------------------------
# Drivers
# ---------------------------------------------------------------------------
def run_main(dom, llm, systems=SYSTEMS):
    rows, failures = [], []
    for size, idx, inst, opt in dom.instances():
        for system in systems:
            row, text = _solve(system, dom, llm, inst, size, idx, opt)
            rows.append(row)
            print(f"  [{dom.name}] {system:<9} {dom.size_label(size):>8} #{idx}  "
                  f"{row['category']:<10} opt={opt} true={row['true_cost']} "
                  f"rep={row['reported_cost']}  {row['seconds']:.1f}s", flush=True)
            if row["category"] != "optimal":
                failures.append((row, inst, text))
    return rows, failures


def run_repro(dom, llm):
    """Instance 0 of each size: 5 calls at T=0 and 5 at T=0.7 (seeds 0-4, so
    the cache keys differ). Tool arm and A* on one size only."""
    rows = []
    for size, idx, inst, opt in dom.instances():
        if idx != 0:
            continue
        systems = ["LLM"] + (["LLM+tool", "A*"] if size == dom.repro_tool_size else [])
        for system in systems:
            for temp in (0.0, 0.7):
                for seed in range(5):
                    row, text = _solve(system, dom, llm, inst, size, 0, opt, temp, seed)
                    answer, cost = dom.parse_answer(text.split("\n---\n")[-1])
                    sig = (json.dumps({dom.answer_key: answer, "cost": cost})
                           if answer is not None
                           else "MALFORMED:" + " ".join(text.split())[:80])
                    rows.append({"system": system, "size": size, "instance": 0,
                                 "temperature": temp, "seed": seed,
                                 "category": row["category"], "answer": sig})
                    print(f"  [{dom.name}] repro {system:<9} {dom.size_label(size):>8} "
                          f"T={temp} seed={seed} {row['category']}", flush=True)
    return rows


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------
def _q(xs, p):
    xs = sorted(xs)
    if not xs:
        return ""
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def summarize(rows, sizes):
    out = []
    for system in [s for s in SYSTEMS if any(r["system"] == s for r in rows)]:
        for size in list(sizes) + ["all"]:
            sel = [r for r in rows if r["system"] == system
                   and (size == "all" or r["size"] == size)]
            if not sel:
                continue
            n = len(sel)
            secs = [float(r["seconds"]) for r in sel]
            tout = [int(r["tokens_out"]) for r in sel]
            tin = [int(r["tokens_in"]) for r in sel]
            exps = [int(r["expansions"]) for r in sel]
            ratios = [float(r["true_cost"]) / float(r["optimal_cost"])
                      for r in sel if r["true_cost"] not in ("", None)]
            row = {"system": system, "size": size, "n": n}
            for c in CATEGORIES:
                row[f"n_{c}"] = sum(r["category"] == c for r in sel)
            row["optimal_rate"] = round(row["n_optimal"] / n, 3)
            row["legal_rate"] = round(sum(int(r["legal"]) for r in sel) / n, 3)
            row["seconds_median"] = round(statistics.median(secs), 4)
            row["seconds_q1"] = round(_q(secs, .25), 4)
            row["seconds_q3"] = round(_q(secs, .75), 4)
            row["seconds_p95"] = round(_q(secs, .95), 4)
            row["tokens_in_median"] = statistics.median(tin)
            row["tokens_out_median"] = statistics.median(tout)
            row["tokens_out_q1"] = _q(tout, .25)
            row["tokens_out_q3"] = _q(tout, .75)
            row["expansions_median"] = statistics.median(exps)
            row["cost_ratio_legal_median"] = round(statistics.median(ratios), 3) if ratios else ""
            row["cost_ratio_legal_max"] = round(max(ratios), 3) if ratios else ""
            out.append(row)
    return out


def summarize_repro(rows):
    out = []
    keys = sorted({(r["system"], r["size"], r["temperature"]) for r in rows})
    for system, size, temp in keys:
        sel = [r for r in rows if (r["system"], r["size"], r["temperature"]) == (system, size, temp)]
        out.append({"system": system, "size": size, "temperature": temp,
                    "calls": len(sel),
                    "distinct_answers": len({r["answer"] for r in sel}),
                    "n_optimal": sum(r["category"] == "optimal" for r in sel)})
    return out


# ---------------------------------------------------------------------------
# Output files: results/duel/<domain>/
#
# A domain may have several prompt versions (the puzzle has v2, the main run,
# and v1, the archived first run). They share one folder: every file carries a
# ``prompt`` column, and failures.md has one section per version.
# ---------------------------------------------------------------------------
def write_csv(path: Path, rows, fields=None):
    fields = fields or list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.relative_to(ROOT).as_posix()} ({len(rows)} rows)")


def _failure_lines(dom, failures):
    lines = []
    for row, inst, text in failures:
        lines.append(f"### {row['system']} · {dom.size_label(row['size'])} · "
                     f"instance {row['instance']} · **{row['category']}**\n")
        lines.append(f"- optimal cost {row['optimal_cost']}, true cost of the "
                     f"answer {row['true_cost']}, reported {row['reported_cost']}")
        lines.append(f"- validator: {row['reasons'] or '—'}\n")
        lines.append("```text\n" + dom.show(inst) + "\n```\n")
        body = text.strip()
        if len(body) > 1500:
            body = body[:1500] + " …[truncated; full text in .llm_cache/]"
        lines.append("<details><summary>model output</summary>\n\n```text\n"
                     + body + "\n```\n</details>\n")
    return lines


def _tag(rows, prompt):
    """Prefix every row with its prompt version (multi-version domains only)."""
    return [{"prompt": prompt, **r} for r in rows] if prompt else rows


def run_domain(versions, llm, repro=True):
    """Run every system on every instance (plus the reproducibility calls) for
    each prompt version of one domain, and write ``results/duel/<folder>/``.

    ``versions`` is one domain object, or a list of them sharing ``folder``
    (main version first)."""
    versions = versions if isinstance(versions, list) else [versions]
    folder = versions[0].folder
    assert all(v.folder == folder for v in versions)
    multi = len(versions) > 1
    out = RESULTS / folder
    out.mkdir(parents=True, exist_ok=True)

    raw, summ, rep, rep_summ = [], [], [], []
    md = [f"# Duel 1 ({folder}) — every non-optimal answer\n",
          "Generated by `code/duel.py`. Categories and reasons come from "
          "`code/validator.py`; the raw model text is reproduced verbatim "
          "(also in `.llm_cache/`).\n"]
    for dom in versions:
        prompt = dom.prompt if multi else None
        print(f"== {dom.name} ==")
        rows, failures = run_main(dom, llm)
        rows.sort(key=lambda r: (SYSTEMS.index(r["system"]), r["size"], r["instance"]))
        raw += _tag(rows, prompt)
        summ += _tag(summarize(rows, dom.sizes), prompt)
        if multi:
            md.append(f"## Prompt {dom.prompt}{dom.prompt_note}\n")
        md += _failure_lines(dom, failures)
        if repro:
            r = run_repro(dom, llm)
            rep += _tag(r, prompt)
            rep_summ += _tag(summarize_repro(r), prompt)

    write_csv(out / "raw.csv", raw, (["prompt"] if multi else []) + RAW_FIELDS)
    write_csv(out / "summary.csv", summ)
    (out / "failures.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {(out / 'failures.md').relative_to(ROOT).as_posix()}")
    if repro:
        write_csv(out / "repro.csv", rep)
        write_csv(out / "repro_summary.csv", rep_summ)
