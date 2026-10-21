"""Tests for the validator, on hand-checked cases and on the real instance bank.
Run: python3 test_validator.py"""
import csv
from pathlib import Path

import duel_lib as D
import gridworld as GW

HERE = Path(__file__).parent
G3 = ["S.,", ".~.", ",.G"]          # optimum = 6 (DDRR or RRDD); RDRD costs 11
WALL = ["S#G", "...", "..."]        # wall at (0,1); optimum = 4 (D R R U), passed explicitly


def cat(grid, text, opt=None):
    return D.validate(grid, text, optimal=opt)


def test_cases():
    c = cat(G3, "PATH: DDRR\nCOST: 6");              assert c["category"] == "correct", c
    c = cat(G3, "PATH: RRDD\nCOST: 6");              assert c["category"] == "correct", c
    c = cat(G3, "PATH: DDRR\nCOST: 5");              assert c["category"] == "wrong_cost", c
    c = cat(G3, "PATH: RDRD\nCOST: 11")
    assert c["category"] == "suboptimal" and c["cost_reported_ok"] is True, c
    c = cat(G3, "PATH: RDRD\nCOST: 10")
    assert c["category"] == "suboptimal" and c["cost_reported_ok"] is False, c
    c = cat(G3, "PATH: UDRR\nCOST: 6");              assert c["reason"] == "out_of_bounds", c
    c = cat(G3, "PATH: DD\nCOST: 4");                assert c["reason"] == "not_at_goal", c
    c = cat(G3, "PATH: DDXR\nCOST: 6");              assert c["reason"] == "invalid_char", c
    c = cat(WALL, "PATH: RRDD\nCOST: 4", opt=4);     assert c["reason"] == "wall", c
    c = cat(G3, "I think the answer is down down.");  assert c["category"] == "malformed", c
    c = cat(G3, "**PATH:** D D R R\n**COST:** 6");   assert c["category"] == "correct", c
    c = cat(G3, "first try PATH: RR\nfinal\nPATH: DDRR\nCOST: 6")
    assert c["category"] == "correct", c            # last occurrence wins
    c = cat(G3, "PATH: DDRR");                       assert c["category"] == "wrong_cost", c
    print("  ok  hand-made cases (all 5 categories + parser quirks)")


def test_real_bank():
    """For every provided grid: A*'s own path must validate as correct, a wrong cost as
    wrong_cost, and BFS's path as suboptimal exactly when BFS cost > optimum."""
    bank = GW.load_instances(HERE / "instances_grid.json")
    rows = list(csv.DictReader(open(HERE.parent / "results" / "classical_grid.csv")))
    by = {(int(r["level"]), int(r["instance"]), r["algo"]): r for r in rows}
    n_sub = 0
    for size, grids in bank.items():
        for i, g in enumerate(grids):
            astar, bfs = by[(size, i, "astar_manhattan")], by[(size, i, "bfs")]
            ap, ac = astar["path"].replace(",", ""), int(astar["cost"])
            assert cat(g, f"PATH: {ap}\nCOST: {ac}")["category"] == "correct"
            assert cat(g, f"PATH: {ap}\nCOST: {ac + 1}")["category"] == "wrong_cost"
            bp, bc = bfs["path"].replace(",", ""), int(bfs["cost"])
            res = cat(g, f"PATH: {bp}\nCOST: {bc}")
            assert (res["category"] == "suboptimal") == (bc > ac), (size, i, res)
            n_sub += res["category"] == "suboptimal"
    print(f"  ok  validator agrees with A*/BFS ground truth on all 40 grids "
          f"({n_sub} BFS paths flagged suboptimal)")


if __name__ == "__main__":
    test_cases()
    test_real_bank()
    print("\nall validator tests pass")
