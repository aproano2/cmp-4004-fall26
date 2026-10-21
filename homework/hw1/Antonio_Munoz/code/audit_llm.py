"""audit_llm.py -- is '0 correct' real, or an artifact of our strict reply parser?

Reads ../results/llm_grid.csv and the RAW replies in ../.llm_cache and prints:
  1. which characters made the invalid_char replies invalid, with examples;
  2. a LENIENT re-scoring (keep only the letters U/D/L/R of the PATH line) next to the
     strict one. The strict result stays the official one; this is a sensitivity check
     that tells us whether the conclusion depends on the parser.
Run: python3 audit_llm.py
"""
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

import duel_lib as D
import gridworld as GW

HERE = Path(__file__).parent
RES, CACHE = HERE.parent / "results", HERE.parent / ".llm_cache"
bank = GW.load_instances(HERE / "instances_grid.json")
df = pd.read_csv(RES / "llm_grid.csv")

bad_chars, examples, lenient = Counter(), [], []
for r in df.itertuples():
    text = json.loads((CACHE / f"{r.key}.json").read_text())["text"]
    found = re.findall(r"PATH[\s*`_]*:[\s*`_]*([^\n]*)", text, flags=re.I)
    line = found[-1].strip() if found else None
    if line is None:
        lenient.append("malformed")
        continue
    if r.category == "illegal" and r.reason == "invalid_char":
        cleaned = re.sub(r"[\s,`*\-]", "", line).upper()
        bad_chars.update(set(cleaned) - set("UDLR"))
        if len(examples) < 10:
            examples.append((r.size, r.instance, line[:70]))
    keep = "".join(ch for ch in line.upper() if ch in "UDLR")
    cost = "" if pd.isna(r.reported_cost) else int(r.reported_cost)
    lenient.append(D.validate(bank[r.size][r.instance],
                              f"PATH: {keep}\nCOST: {cost}")["category"])
df["lenient"] = lenient

print("== caracteres que hicieron invalida la ruta (cuenta de respuestas) ==")
print(dict(bad_chars) or "ninguno")
print("\n== ejemplos de la linea PATH en respuestas invalid_char ==")
for size, inst, line in examples:
    print(f"  {size}x{size} #{inst}: {line!r}")
print("\n== ESTRICTO (oficial), por tamano ==")
print(pd.crosstab(df["size"], df["category"]))
print("\n== INDULGENTE (solo letras U/D/L/R), por tamano ==")
print(pd.crosstab(df["size"], df["lenient"]))
