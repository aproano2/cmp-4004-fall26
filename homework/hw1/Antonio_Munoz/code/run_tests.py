"""Runs the course tests against THIS folder's files.
The provided tests do `import starter as s` and load `instances.json`; here the
implementations live in algorithms.py / heuristics_grid.py and the banks are named
instances_8puzzle.json / instances_grid.json, so we alias them at runtime
(no files are renamed or copied).   Run: python3 run_tests.py"""
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import algorithms
import gridworld
import heuristics_grid
import search

_orig_grid, _orig_8p = gridworld.load_instances, search.load_instances
gridworld.load_instances = lambda path=None: _orig_grid(path or HERE / "instances_grid.json")
search.load_instances = lambda path=None: _orig_8p(path or HERE / "instances_8puzzle.json")

for label, impl, test in (("week 3: uninformed search", algorithms, "test_search.py"),
                          ("week 4: heuristics", heuristics_grid, "test_heuristics.py")):
    print(f"== {label} ({test})")
    sys.modules["starter"] = impl
    runpy.run_path(str(HERE / test), run_name="__main__")
