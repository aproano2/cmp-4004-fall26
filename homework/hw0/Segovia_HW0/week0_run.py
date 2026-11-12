import sys, subprocess
r = subprocess.run([sys.executable, "-m", "aicourse.doctor"],
                   capture_output=True, text=True)
print(r.stdout or r.stderr)
print("exit code:", r.returncode, "(0 = all required checks passed)")

from aicourse import LLM

llm = LLM(backend="auto")          # picks ollama > api > manual
AUTOMATED_EARLY = llm.backend in ("ollama", "api")
print("backend:", llm.backend, "| model:", llm.model)

r = llm.complete("In one sentence: what is a heuristic in search?")
if r.error:
    print(f"\n[no response: {r.error}]")
    print("\nIf that mentions 'not a TTY', you ran this with Run All on the")
    print("manual backend. Run this cell on its own so you can paste an answer,")
    print("or set up Ollama. Either is fine.")
else:
    print("\n" + r.text.strip()[:400])
    print(f"\n[{r.elapsed:.1f}s, cached={r.cached}]")

fake = LLM(backend="echo")
print(fake.complete("anything").text)

import time

probe = "Name the author of the 1950 paper 'Computing Machinery and Intelligence'."

# Use whichever backend is available -- the caching behaviour is identical.
demo = llm if AUTOMATED_EARLY else LLM(backend="echo")
t0 = time.perf_counter(); a = demo.complete(probe); t1 = time.perf_counter()
b = demo.complete(probe); t2 = time.perf_counter()

print(f"first  call: {t1-t0:7.3f}s   cached={a.cached}")
print(f"second call: {t2-t1:7.3f}s   cached={b.cached}")
print(f"same text  : {a.text == b.text}")
print(f"\ncache: {demo.cache.stats()}")
if not AUTOMATED_EARLY:
    print("(shown with the echo backend; behaviour is identical for a real model)")

from aicourse.cache import cache_key

base = cache_key("ollama", "qwen2.5:3b", "hello", 0.0, 0)
print("baseline           ", base[:16])
for label, args in [
    ("different prompt   ", ("ollama", "qwen2.5:3b", "hello!", 0.0, 0)),
    ("different temp     ", ("ollama", "qwen2.5:3b", "hello", 0.7, 0)),
    ("different seed     ", ("ollama", "qwen2.5:3b", "hello", 0.0, 1)),
    ("different model    ", ("ollama", "qwen2.5:1.5b", "hello", 0.0, 0)),
    ("identical          ", ("ollama", "qwen2.5:3b", "hello", 0.0, 0)),
]:
    k = cache_key(*args)
    print(f"{label} {k[:16]}   {'SAME' if k == base else 'different'}")

# Realistic variations on "answer with a number". None are unreasonable;
# all of them break a naive parser.
samples = [
    "4",
    "The answer is 4.",
    "4.0",
    "**4**",
    "Four.",
    "I think it's 4, but it depends on the encoding.",
    "```\n4\n```",
    "The answer is 4. Let me explain why: 2+2 means...",
    "Sure! Here you go: 42 is the answer to 2+2? No — 4.",
    "",
]

def parse_naive(text):
    """The parser everybody writes first."""
    return int(text.strip())

print(f"  {'output':<52}{'result'}")
print("  " + "-" * 68)
for s in samples:
    try:
        got = parse_naive(s)
    except Exception as exc:
        got = f"{type(exc).__name__}"
    print(f"  {s[:50]!r:<52}{got}")

import re

def parse_int(text):
    """Return (value, failure_mode). NEVER guesses."""
    if text is None or not text.strip():
        return None, "empty"
    # Prefer a fenced or final-line answer, which is what we asked for.
    fence = re.search(r"```(?:\w+)?\s*(-?\d+)\s*```", text)
    if fence:
        return int(fence.group(1)), None
    tagged = re.search(r"ANSWER\s*[:=]\s*(-?\d+)", text, re.IGNORECASE)
    if tagged:
        return int(tagged.group(1)), None
    # Match integers AND decimals, so "4.0" is one number rather than two.
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not nums:
        return None, "no-number-found"
    vals = []
    for tok in nums:
        f = float(tok)
        if f != int(f):
            return None, "not-an-integer"      # 4.5 is not an int answer
        vals.append(int(f))
    if len(set(vals)) > 1:
        # Two DIFFERENT numbers and no marker: we genuinely do not know which
        # one is the answer. Refusing to guess is the correct behaviour.
        return None, "ambiguous"
    return vals[0], None


print(f"  {'output':<52}{'value':>8}  failure")
print("  " + "-" * 76)
for s in samples:
    v, mode = parse_int(s)
    print(f"  {s[:50]!r:<52}{str(v):>8}  {mode or ''}")

TASK = "What is 17 * 23?"

PROMPTS = {
    "bare":        TASK,
    "format":      TASK + "\nReply with only the number.",
    "tagged":      TASK + "\nReply with exactly: ANSWER: <number>",
    "fenced+cot":  (TASK + "\nThink step by step, then give the final answer "
                    "in a fenced code block containing only the number."),
}

AUTOMATED = llm.backend in ("ollama", "api")

if AUTOMATED:
    print(f"  {'prompt style':<14}{'parsed':>9}{'failure':>16}   raw (truncated)")
    print("  " + "-" * 78)
    for name, p in PROMPTS.items():
        resp = llm.complete(p)
        val, mode = parse_int(resp.text)
        raw = resp.text.strip().replace("\n", " ")[:30]
        print(f"  {name:<14}{str(val):>9}{str(mode or ''):>16}   {raw!r}")
    print(f"\n  ground truth: {17*23}")
else:
    print("Skipped: needs an automated backend (ollama or api).\n")
    print("MANUAL BACKEND: do this by hand. Send all four prompts below to any")
    print("chat interface, paste each answer through parse_int(), and record the")
    print("table yourself. It is four prompts -- worth doing, this is the cell")
    print("that teaches prompt format as an engineering variable.\n")
    for name, p in PROMPTS.items():
        print(f"  --- {name} " + "-" * (60 - len(name)))
        for line in p.splitlines():
            print(f"    {line}")
    print(f"\n  ground truth: {17*23}")

PROBE = ("List three uses of a paperclip. "
         "Reply with exactly three comma-separated items and nothing else.")

def variability(llm, prompt, n=3, temperature=0.0, use_cache=False):
    outs = []
    for i in range(n):
        r = llm.complete(prompt, temperature=temperature, seed=i,
                         use_cache=use_cache)
        outs.append(r.text.strip())
    return outs

if llm.backend in ("ollama", "api"):    # same as AUTOMATED, defined below
    print(f"temperature = 0.0, varying seed:")
    outs = variability(llm, PROBE, n=3, temperature=0.0)
    for i, o in enumerate(outs):
        print(f"  run {i}: {o[:70]!r}")
    print(f"  distinct answers: {len(set(outs))} of {len(outs)}")

    print(f"\ntemperature = 1.0, varying seed:")
    outs_hot = variability(llm, PROBE, n=3, temperature=1.0)
    for i, o in enumerate(outs_hot):
        print(f"  run {i}: {o[:70]!r}")
    print(f"  distinct answers: {len(set(outs_hot))} of {len(outs_hot)}")
else:
    print("Skipped: needs an automated backend (ollama or api).")
    print("""
On the manual backend, do this ONCE by hand: send the same prompt three times in
a fresh chat each time and record whether the answers differ. Report n=3 and note
the method. That is a legitimate measurement.""")

print("""
WHAT TO REPORT for axis 5: "5 runs, k distinct answers, at temperature T."
A system that returns 4 different answers to the same question has a property your
A* implementation does not, and that belongs in the table.""")

import random
from dataclasses import dataclass

@dataclass
class SortInstance:
    id: str
    size: int
    items: list

def make_instances(sizes=(5, 10, 20, 40), per_size=5, seed=20250806):
    rng = random.Random(seed)
    out = []
    for n in sizes:
        for k in range(per_size):
            items = [rng.randint(0, 999) for _ in range(n)]
            out.append(SortInstance(id=f"n{n}-{k}", size=n, items=items))
    return out

INSTANCES = make_instances()
print(f"{len(INSTANCES)} instances across sizes "
      f"{sorted({i.size for i in INSTANCES})}")
print(f"example: {INSTANCES[0].id} -> {INSTANCES[0].items}")

# --- the classical system -------------------------------------------------
def classical_sort(inst):
    return sorted(inst.items)


# --- the LLM system -------------------------------------------------------
def make_llm_sort(llm):
    def llm_sort(inst):
        prompt = (
            "Sort this list of integers in ascending order.\n"
            f"List: {inst.items}\n"
            "Reply with ONLY the sorted list as comma-separated integers "
            "inside a fenced code block. No explanation."
        )
        text = llm.complete(prompt).text
        return parse_int_list(text)
    return llm_sort


def parse_int_list(text):
    """Prose -> list[int], or None. Same discipline as parse_int."""
    if not text or not text.strip():
        return None
    fence = re.search(r"```(?:\w+)?\s*(.*?)```", text, re.DOTALL)
    body = fence.group(1) if fence else text
    nums = re.findall(r"-?\d+", body)
    return [int(x) for x in nums] if nums else None


# --- the VERIFIER: this is the important part -----------------------------
def verify_sort(inst, answer):
    """Sound check. Returns (correct, failure_mode).

    Note it checks three separate things. An LLM can fail any of them
    independently, and lumping them together as 'wrong' throws away the most
    interesting part of your data.
    """
    if answer is None:
        return False, "malformed"
    if len(answer) != len(inst.items):
        return False, "invalid"                      # dropped or invented items
    if sorted(answer) != sorted(inst.items):
        return False, "invalid"                      # changed the multiset
    if any(answer[i] > answer[i+1] for i in range(len(answer)-1)):
        return False, "wrong-but-confident"          # right items, wrong order
    return True, None


# Sanity-check the verifier itself, on cases where we know the answer.
probe = SortInstance("t", 3, [3, 1, 2])
for ans, expect in [([1,2,3], True), ([3,2,1], False), ([1,2], False),
                    ([1,2,4], False), (None, False)]:
    ok, mode = verify_sort(probe, ans)
    assert ok == expect, (ans, ok, expect)
    print(f"  verify({str(ans):<10}) -> {str(ok):<6} {mode or ''}")
print("\nVerifier agrees with all five known cases. NOW it can be trusted.")

from aicourse.compare import run_comparison, print_summary, scorecard_stub

systems = {"sorted()": classical_sort}
if AUTOMATED:
    systems["LLM"] = make_llm_sort(llm)
else:
    print("Manual backend: the classical arm runs below. For the LLM arm, do")
    print("FOUR instances by hand -- one per size -- and add those rows to your")
    print("table. Report n=4 and say so in the write-up.\n")
    print("Prompts to send (one per size):")
    for size in sorted({i.size for i in INSTANCES}):
        inst = next(i for i in INSTANCES if i.size == size)
        print(f"\n  --- {inst.id} " + "-" * 52)
        print(f"    Sort this list of integers in ascending order.")
        print(f"    List: {inst.items}")
        print(f"    Reply with ONLY the sorted list as comma-separated integers")
        print(f"    inside a fenced code block. No explanation.")
    print()

results = run_comparison(
    systems, INSTANCES,
    verifier=verify_sort,
    size_of=lambda i: i.size,
    id_of=lambda i: i.id,
    progress=False,
)
print_summary(results)

print(scorecard_stub(results))