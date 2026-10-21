### [Wk0] LLM swaps one element for an invented number while sorting 10 integers

**Setup:** qwen2.5:3b via ollama, temp 0, seed 0, course prompt: "Sort this list of integers
in ascending order. List: [310, 950, 851, 195, 336, 19, 56, 706, 39, 12]. Reply with ONLY the
sorted list as comma-separated integers inside a fenced code block. No explanation."
**Classical:** sorted() → [12, 19, 39, 56, 195, 310, 336, 706, 851, 950]. Correct by
construction, O(n log n), ~0.00002 s.
**LLM:** `12,19,39,56,195,310,336,390,706,950`
Ten numbers, perfectly ascending, right length — but 851 is gone and 390, which was never in
the input, appears in its place. No hedging, no mention of uncertainty.
**Category:** invalid
**Why it matters:** The output passes every check a human would casually do (count and order
are both fine); only a multiset comparison catches it, so any pipeline consuming this output
would silently replace real data with an invented value.
