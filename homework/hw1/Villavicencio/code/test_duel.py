"""Tests for the validator and the whole pipeline with a FAKE model.
    python test_duel.py
Passing this means a bad score later is the model's fault, not your harness's.
"""
import json
import random

import duel_common as dc
import llm_backends as lb
import run_duel as rd


def ans(moves, cost):
    return "thinking...\n" + json.dumps({"moves": moves, "cost": cost})


def test_reference_matches_ucs_and_depth():
    from search import ucs
    for dom in ("puzzle", "grid"):
        for inst in dc.load_instances(dom, 10):
            c, _ = dc.reference_solution(inst)
            n, _, _ = dc.ucs(dc.make_problem(inst)) if hasattr(dc, "ucs") else ucs(dc.make_problem(inst))
            assert n.g == c, (dom, inst["level"], inst["idx"])
            if dom == "puzzle":
                assert c == inst["level"]


def test_validator_categories():
    inst = dc.load_instances("grid", 10)[0]
    cost, path = dc.reference_solution(inst)
    ok = dc.validate(inst, ans(path, cost), cost)
    assert ok["category"] == "optimal_correct"
    assert dc.validate(inst, ans(path, cost + 1), cost)["category"] == "wrong_cost"
    assert dc.validate(inst, ans(path[:-1], cost), cost)["category"] == "illegal"      # not at goal
    assert dc.validate(inst, ans(["U"] * 20, 1), cost)["category"] == "illegal"        # off the grid
    assert dc.validate(inst, "no json here", cost)["category"] == "illegal"
    # detour: legal but suboptimal (go away and come back)
    p = dc.make_problem(inst)
    for a in p.actions(p.initial):
        back = {"U": "D", "D": "U", "L": "R", "R": "L"}[a]
        v = dc.validate(inst, ans([a, back] + path, 99), cost)
        assert v["category"] == "suboptimal", v
        break


def test_puzzle_aliases():
    inst = dc.load_instances("puzzle", 10)[0]
    cost, path = dc.reference_solution(inst)
    short = [dc.SHORT[m] for m in path]
    assert dc.validate(inst, ans("".join(short), cost), cost)["category"] == "optimal_correct"
    assert dc.validate(inst, ans(short, cost), cost)["category"] == "optimal_correct"


class FakeModel(lb.Backend):
    """Solves the instance in self.current with a given error profile."""
    name = "mock"

    def __init__(self, mode, **kw):
        super().__init__(model=mode, **kw)
        self.mode, self.current, self.rng = mode, None, random.Random(0)

    def _generate(self, key, system, messages):
        inst = self.current
        cost, path = dc.reference_solution(inst)
        last = messages[-1]["content"]
        if self.mode == "tool":
            if last.startswith("Tool result:"):
                res = json.loads(last.split("\n", 1)[1])
                return ans(res["moves"], res["cost"]), 0.1, 10, 10
            key_ = "state" if inst["domain"] == "puzzle" else "grid"
            val = list(inst["data"])
            return json.dumps({"tool": "astar_solve", "arguments": {key_: val}}), 0.1, 10, 10
        r = self.rng.random()
        if r < .4:
            return ans(path, cost), 0.2, 10, 10
        if r < .6:
            return ans(path, cost + 1), 0.2, 10, 10
        if r < .8:
            return ans(path[:-1], cost), 0.2, 10, 10
        return "I give up", 0.2, 10, 10


def test_pipeline_with_fake_models(tmp_cache):
    for mode, runner in (("llm", rd.run_llm), ("tool", rd.run_tool)):
        be = FakeModel(mode, temperature=1.0)
        cats = []
        for inst in dc.load_instances("grid", 3) + dc.load_instances("puzzle", 3):
            be.current = inst
            ref, _ = dc.reference_solution(inst)
            v, ex = runner(be, inst, ref)
            row = rd.make_row("T", be, inst, 0, v, ex)
            assert set(rd.RAW_FIELDS) <= set(row)
            cats.append(v["category"])
        if mode == "tool":
            assert set(cats) == {"optimal_correct"}, cats
        else:
            assert len(set(cats)) > 1


def test_cache_roundtrip(tmp_cache):
    be = FakeModel("llm")
    inst = dc.load_instances("grid", 1)[0]
    be.current = inst
    a = be.call("s", [{"role": "user", "content": "x"}], 0)
    b = be.call("s", [{"role": "user", "content": "x"}], 0)
    c = be.call("s", [{"role": "user", "content": "x"}], 1)
    assert not a["cached"] and b["cached"] and a["key"] == b["key"] != c["key"]


if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    tmp = Path(tempfile.mkdtemp())
    dc.CACHE_DIR = lb.CACHE_DIR = tmp          # never pollute the real .llm_cache
    test_reference_matches_ucs_and_depth()
    test_validator_categories()
    test_puzzle_aliases()
    test_pipeline_with_fake_models(tmp)
    test_cache_roundtrip(tmp)
    print("all duel tests passed")
