import csv
from collections import defaultdict
import matplotlib.pyplot as plt

# Read LLM results
with open("results/llm_responses.csv", encoding="utf-8") as f:
    llm = list(csv.DictReader(f))

# Read tool-augmented results
with open("results/tool_augmented.csv", encoding="utf-8") as f:
    tool = list(csv.DictReader(f))

# We plot each domain separately in the same figure.
# "Classical" A* optimality is 100% at every tested level.

puzzle_levels = [4, 8, 12, 16]
grid_levels = [5, 8, 12, 16]


def rate(rows, domain, level, field):
    selected = [
        r for r in rows
        if r["domain"] == domain and int(r["level"]) == level
    ]

    if not selected:
        return 0

    successes = sum(
        str(r[field]).lower() == "true"
        for r in selected
    )

    return 100.0 * successes / len(selected)


# ---------- 8-puzzle ----------
llm_puzzle = [
    rate(llm, "8puzzle", level, "optimal")
    for level in puzzle_levels
]

tool_puzzle = [
    rate(tool, "8puzzle", level, "optimal")
    for level in puzzle_levels
]

classical_puzzle = [100, 100, 100, 100]

plt.figure(figsize=(8, 5))

plt.plot(
    puzzle_levels,
    classical_puzzle,
    marker="o",
    label="Classical A*"
)

plt.plot(
    puzzle_levels,
    llm_puzzle,
    marker="o",
    label="LLM"
)

plt.plot(
    puzzle_levels,
    tool_puzzle,
    marker="o",
    label="Tool-augmented A* execution"
)

plt.xlabel("8-puzzle optimal solution depth")
plt.ylabel("Optimality rate (%)")
plt.ylim(-5, 105)
plt.title("Optimality scaling — 8-puzzle")
plt.legend()
plt.tight_layout()
plt.savefig("fig/fig5_optimality_puzzle.png", dpi=160)
plt.close()


# ---------- weighted grid ----------
llm_grid = [
    rate(llm, "grid", level, "optimal")
    for level in grid_levels
]

tool_grid = [
    rate(tool, "grid", level, "optimal")
    for level in grid_levels
]

classical_grid = [100, 100, 100, 100]

plt.figure(figsize=(8, 5))

plt.plot(
    grid_levels,
    classical_grid,
    marker="o",
    label="Classical A*"
)

plt.plot(
    grid_levels,
    llm_grid,
    marker="o",
    label="LLM"
)

plt.plot(
    grid_levels,
    tool_grid,
    marker="o",
    label="Tool-augmented A* execution"
)

plt.xlabel("Grid size (N × N)")
plt.ylabel("Optimality rate (%)")
plt.ylim(-5, 105)
plt.title("Optimality scaling — weighted grids")
plt.legend()
plt.tight_layout()
plt.savefig("fig/fig6_optimality_grid.png", dpi=160)
plt.close()


print("8-puzzle:")
print("LLM :", llm_puzzle)
print("Tool:", tool_puzzle)

print()

print("Grid:")
print("LLM :", llm_grid)
print("Tool:", tool_grid)

print()
print("Saved:")
print("fig/fig5_optimality_puzzle.png")
print("fig/fig6_optimality_grid.png")