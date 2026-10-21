"""The comparison harness used by every duel.

The point of this module is that a fair comparison has MOVING PARTS THAT ARE
EASY TO GET WRONG, and getting them wrong is the most common way a duel report
fails. So they are written once, here, and reused:

    Trial / Result     one (system, instance) measurement
    run_comparison()   run N systems over M instances, timing everything
    summarize()        per-system aggregates, including variance
    scaling_table()    performance BY PROBLEM SIZE -- scorecard axis 6
    scorecard_stub()   a pre-filled markdown table you must finish by hand

What this module deliberately does NOT do: decide who won. That is your job,
in prose, with the honesty section attached.
"""

from __future__ import annotations

import statistics
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Iterable


# ---------------------------------------------------------------------------
@dataclass
class Result:
    """One system's attempt at one instance."""
    system: str
    instance_id: str
    size: int
    correct: bool
    elapsed: float
    answer: object = None
    cost: float = 0.0            # nodes expanded, or tokens, or evaluations
    failure_mode: str | None = None   # see FAILURE_MODES
    notes: str = ""


FAILURE_MODES = (
    "wrong-but-confident",   # produced a confident wrong answer
    "malformed",             # output could not be parsed at all
    "refused",               # declined to answer
    "timeout",               # ran out of time
    "invalid",               # parseable but violates the problem's constraints
    None,                    # no failure
)


# ---------------------------------------------------------------------------
def run_comparison(systems: dict[str, Callable], instances: Iterable,
                   *, verifier: Callable | None = None,
                   size_of: Callable | None = None,
                   id_of: Callable | None = None,
                   timeout_s: float | None = None,
                   progress: bool = True) -> list[Result]:
    """Run every system on every instance.

    systems  : {"A*": fn, "LLM": fn} where fn(instance) -> answer
    verifier : verifier(instance, answer) -> (bool, failure_mode | None)
               If omitted, an answer is "correct" iff it is not None.

               USE A VERIFIER. This is the week-9 lesson applied to your own
               experiment: an unreliable generator plus a sound checker is a
               reliable measurement. Grading an LLM's answer by eye does not
               scale past instance 10 and is not reproducible.
    """
    instances = list(instances)
    size_of = size_of or (lambda x: getattr(x, "size", 0))
    id_of = id_of or (lambda x: str(getattr(x, "id", instances.index(x))))
    out: list[Result] = []

    for name, fn in systems.items():
        if progress:
            print(f"[{name}] {len(instances)} instance(s)")
        for i, inst in enumerate(instances, 1):
            t0 = time.perf_counter()
            answer, mode = None, None
            try:
                answer = fn(inst)
            except TimeoutError:
                mode = "timeout"
            except Exception as exc:                 # noqa: BLE001
                mode = "malformed"
                answer = None
                if progress:
                    print(f"    instance {i}: {type(exc).__name__}: {exc}")
            elapsed = time.perf_counter() - t0

            if timeout_s is not None and elapsed > timeout_s and mode is None:
                mode = "timeout"

            if mode is None:
                if verifier is not None:
                    correct, mode = verifier(inst, answer)
                else:
                    correct = answer is not None
            else:
                correct = False

            out.append(Result(system=name, instance_id=id_of(inst),
                              size=size_of(inst), correct=correct,
                              elapsed=elapsed, answer=answer,
                              failure_mode=mode))
            if progress and i % 10 == 0:
                print(f"    {i}/{len(instances)}")
    return out


# ---------------------------------------------------------------------------
def summarize(results: list[Result]) -> dict[str, dict]:
    """Per-system aggregates. Reports SPREAD, not just central tendency."""
    by_system = defaultdict(list)
    for r in results:
        by_system[r.system].append(r)

    out = {}
    for name, rs in by_system.items():
        times = sorted(r.elapsed for r in rs)
        n = len(rs)
        solved = sum(r.correct for r in rs)
        modes = defaultdict(int)
        for r in rs:
            if r.failure_mode:
                modes[r.failure_mode] += 1
        out[name] = {
            "n": n,
            "solved": solved,
            "solve_rate": solved / n if n else 0.0,
            "median_s": statistics.median(times) if times else 0.0,
            "p95_s": times[min(len(times) - 1, int(0.95 * len(times)))] if times else 0.0,
            "mean_cost": statistics.mean([r.cost for r in rs]) if rs else 0.0,
            "failure_modes": dict(modes),
        }
    return out


def scaling_table(results: list[Result]) -> dict[str, dict[int, float]]:
    """Solve rate by problem size. THIS is scorecard axis 6.

    A single aggregate solve rate hides the cliff. The whole empirical finding of
    this course lives in how these numbers change with size.
    """
    grid = defaultdict(lambda: defaultdict(list))
    for r in results:
        grid[r.system][r.size].append(r.correct)
    return {sys: {size: sum(v) / len(v) for size, v in sorted(sizes.items())}
            for sys, sizes in grid.items()}


def print_summary(results: list[Result]) -> None:
    s = summarize(results)
    print(f"\n  {'system':<16}{'n':>5}{'solved':>8}{'rate':>8}"
          f"{'median':>9}{'p95':>9}")
    print("  " + "-" * 55)
    for name, d in s.items():
        print(f"  {name:<16}{d['n']:>5}{d['solved']:>8}{d['solve_rate']:>7.0%}"
              f"{d['median_s']:>8.2f}s{d['p95_s']:>8.2f}s")

    modes = {n: d["failure_modes"] for n, d in s.items() if d["failure_modes"]}
    if modes:
        print("\n  failure modes:")
        for name, m in modes.items():
            parts = ", ".join(f"{k}={v}" for k, v in sorted(m.items()))
            print(f"    {name:<16}{parts}")

    scale = scaling_table(results)
    sizes = sorted({sz for d in scale.values() for sz in d})
    if len(sizes) > 1:
        print(f"\n  solve rate by size  (axis 6 — look for the cliff)")
        print("  " + " " * 16 + "".join(f"{sz:>8}" for sz in sizes))
        print("  " + "-" * (16 + 8 * len(sizes)))
        for name, d in scale.items():
            row = "".join(f"{d.get(sz, float('nan')):>7.0%} " if sz in d
                          else f"{'--':>8}" for sz in sizes)
            print(f"  {name:<16}{row}")
    else:
        print("\n  ! Only one problem size present. Scorecard axis 6 requires")
        print("    at least FOUR sizes. One point is not a curve.")


# ---------------------------------------------------------------------------
def scorecard_stub(results: list[Result], systems: list[str] | None = None) -> str:
    """Emit a partly-filled scorecard table.

    Four axes can be measured automatically. FOUR CANNOT, and they are left as
    TODO on purpose: guarantee, reproducibility, interpretability, and the
    honesty section are judgements, and a harness that guessed them would be
    teaching you the wrong lesson.
    """
    s = summarize(results)
    scale = scaling_table(results)
    names = systems or list(s)

    rows = [
        ("Correctness", lambda n: f"{s[n]['solved']}/{s[n]['n']} ({s[n]['solve_rate']:.0%})"),
        ("Guarantee", lambda n: "**TODO — state it as a conditional**"),
        ("Cost", lambda n: f"{s[n]['mean_cost']:.0f} (mean)" if s[n]["mean_cost"] else "**TODO**"),
        ("Latency", lambda n: f"{s[n]['median_s']:.2f}s / {s[n]['p95_s']:.2f}s"),
        ("Reproducibility", lambda n: "**TODO — run 5x, count distinct answers**"),
        ("Scaling", lambda n: " → ".join(f"{v:.0%}" for v in scale[n].values())),
        ("Interpretability", lambda n: "**TODO — can you extract a certificate?**"),
        ("Failure mode", lambda n: ", ".join(f"{k}={v}" for k, v in
                                            sorted(s[n]["failure_modes"].items()))
                                   or "none observed"),
    ]

    lines = ["| Axis | " + " | ".join(names) + " |",
             "|---|" + "---|" * len(names)]
    for axis, fn in rows:
        lines.append(f"| {axis} | " + " | ".join(fn(n) for n in names) + " |")

    lines += [
        "",
        "### Where we may have been unfair",
        "",
        "**TODO — this section is worth real credit. Address at least three:**",
        "",
        "- Did both systems get the same information?",
        "- Did you tune one side's parameters but use a default prompt for the other?",
        "- Is your instance distribution accidentally favourable to one side?",
        "- Did you count the time you spent writing the prompt? The heuristic?",
        "- Would a larger model change the result — and can you know without running it?",
    ]
    return "\n".join(lines)
