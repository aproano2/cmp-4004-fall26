### [Wk0] LLM sorted the numbers incorrectly

**Setup:** The LLM was asked to sort a list of integers in ascending order using Ollama with the qwen2.5:3b model.

**Classical:** The correct answer was `[207, 235, 276, 330, 709]`, obtained using Python's `sorted()` function.

**LLM:** `[330, 207, 235, 276, 709]`

**Category:** wrong-but-confident

**Why it matters:** Without a verifier, the system could accept an incorrectly ordered list as a correct result even though it contains all the original numbers.