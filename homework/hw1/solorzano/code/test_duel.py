"""Tests para la Parte 2 harness """

from pathlib import Path

import pandas as pd
import pytest

from duel_problems import (build_instances, get, index_moves_to_letters,
                           solve_grid, step8)
from gridworld import GridProblem
from run_duel import classical_answer, run_tool
from search import GOAL, EightPuzzle, search
from validator import (BADCOST, ILLEGAL, NOANSWER, OK, SUBOPT, parse_answer,
                       parse_tool_call, validate)

INST = build_instances()
CSV = Path(__file__).resolve().parent.parent / "results" / "classical_results.csv"

#consistency with Part 1
def test_eighty_instances_same_order_as_part1():
    assert len(INST) == 80
    assert [i["level"] for i in INST if i["domain"] == "8puzzle"] == [4] * 10 + [8] * 10 + [12] * 10 + [16] * 10


def test_optimal_cost_equals_part1_ucs():
    """Duel reference (Part-1 A*) == Part-1 UCS cost on all 80 instances."""
    if not CSV.exists():
        pytest.skip("results/classical_results.csv not present")
    d = pd.read_csv(CSV)
    ucs = d[d.algorithm == "UCS"].set_index(["domain", "level", "instance_id"]).solution_cost
    for i in INST:
        assert i["optimal_cost"] == ucs[(i["domain"], i["level"], i["instance_id"])], i["key"]


def test_8puzzle_depth_equals_level():
    for i in INST:
        if i["domain"] == "8puzzle":
            assert i["optimal_cost"] == i["level"] == len(i["optimal_path"])


def test_index_moves_to_letters_matches_search_py():
    s = tuple(get(INST, "8puzzle", 12, 3)["start"])
    node, _ = search(EightPuzzle(s), "priority")
    letters = index_moves_to_letters(s, node.path())
    for m in letters:
        s = step8(s, m)
    assert s == GOAL


#validator: 8-puzzle
P = get(INST, "8puzzle", 8, 1)


def test_8p_optimal_ok():
    assert validate(P, {"path": P["optimal_path"], "cost": 8})["category"] == OK


def test_8p_wrong_or_missing_cost_is_cat3():
    assert validate(P, {"path": P["optimal_path"], "cost": 7})["category"] == BADCOST
    assert validate(P, {"path": P["optimal_path"]})["category"] == BADCOST


def test_8p_longer_path_is_cat2_even_with_wrong_cost():
    r = validate(P, {"path": P["optimal_path"] + "UD", "cost": 8})
    assert r["category"] == SUBOPT and r["actual_cost"] == 10 and r["cost_reported_ok"] is False


def test_8p_illegal():
    assert validate(P, {"path": P["optimal_path"][:-1], "cost": 7})["category"] == ILLEGAL   #stops short
    assert validate(P, {"path": "LLLLLLLL", "cost": 8})["category"] == ILLEGAL              #off the board


def test_8p_unparseable():
    assert validate(P, {"path": "up, left", "cost": 2})["category"] == NOANSWER
    assert validate(P, None)["category"] == NOANSWER


#validator: grid
G = get(INST, "grid", 8, 1)

def test_grid_optimal_ok():
    assert validate(G, {"path": G["optimal_path"], "cost": G["optimal_cost"]})["category"] == OK

def test_grid_wrong_cost_is_cat3():
    assert validate(G, {"path": G["optimal_path"], "cost": G["optimal_cost"] + 3})["category"] == BADCOST

def test_grid_illegal_variants():
    p = G["optimal_path"]
    assert validate(G, {"path": p[:-1], "cost": 1})["category"] == ILLEGAL               #does not reach G
    assert validate(G, {"path": p[1:], "cost": 1})["category"] == ILLEGAL                #does not start at S
    assert validate(G, {"path": p[:2] + p[3:], "cost": 1})["category"] == ILLEGAL        #jumps a cell
    assert validate(G, {"path": [[-1, 1]] + p, "cost": 1})["category"] == ILLEGAL        #out of bounds

def test_grid_cost_is_recomputed_not_trusted():
    p = G["optimal_path"]
    detour = [p[0], p[1], p[0]] + p[1:]            #step out and back: legal, costs more
    r = validate(G, {"path": detour, "cost": G["optimal_cost"]})
    assert r["category"] == SUBOPT and r["actual_cost"] > G["optimal_cost"]

def test_part1_bfs_example_is_flagged_suboptimal():
    """The instance cited in Part 1 (grid 5x5, instance 3): BFS cost 5 vs UCS 3."""
    inst = get(INST, "grid", 5, 3)
    ans = classical_answer(inst, "bfs")
    r = validate(inst, ans)
    assert inst["optimal_cost"] == 3 and r["actual_cost"] == 5
    assert r["category"] == SUBOPT and r["cost_reported_ok"] is True

def test_classical_astar_is_always_ok():
    for i in INST:
        assert validate(i, classical_answer(i, "astar"))["category"] == OK, i["key"]

#parsing
def test_parse_answer_takes_last_json():
    t = 'maybe {"path": "U", "cost": 1}\n```json\n{"path": "UDL", "cost": 3}\n```'
    assert parse_answer(t) == {"path": "UDL", "cost": 3}
    assert parse_answer("no json") is None
    assert parse_answer('{"path": [[0,1],[1,1]], "cost": 3}')["path"] == [[0, 1], [1, 1]]

def test_parse_tool_call():
    assert parse_tool_call('{"tool": "astar", "args": {"start": [1]}}')["tool"] == "astar"
    assert parse_tool_call('{"path": "U"}') is None

#tool
def test_tool_runs_part1_astar_and_rejects_bad_args():
    res, err = run_tool("8puzzle", {"start": P["start"]})
    assert not err and res["cost"] == 8
    assert run_tool("8puzzle", {"start": P["start"][:8]})[1]
    assert run_tool("8puzzle", {"start": [2, 1, 3, 4, 5, 6, 7, 8, 0]})[1]       #unsolvable
    res, err = run_tool("grid", {"grid": G["rows"]})
    assert not err and res["cost"] == G["optimal_cost"]
    assert run_tool("grid", {"grid": G["rows"][:-1] + [G["rows"][-1][:-1]]})[1]   #ragged row
    assert run_tool("grid", {"grid": [r.replace(".", "o") for r in G["rows"]]})[1]  #bad characters
    assert run_tool("grid", {"grid": 42})[1]                                      #not rows at all


def test_tool_forgives_format_but_not_content():
    """Same board written differently is accepted; a wrong board is solved as written or rejected."""
    spaced = [" ".join(r) for r in G["rows"]]                                    #as shown in the prompt
    assert run_tool("grid", {"grid": spaced})[0]["cost"] == G["optimal_cost"]
    assert run_tool("grid", {"grid": "\n".join(spaced)})[0]["cost"] == G["optimal_cost"]
    nested = [P["start"][0:3], P["start"][3:6], P["start"][6:9]]
    assert run_tool("8puzzle", {"start": nested})[0]["cost"] == 8
    text = " ".join("_" if v == 0 else str(v) for v in P["start"])
    assert run_tool("8puzzle", {"start": text})[0]["cost"] == 8
    swapped = list(P["start"])
    i, j = [k for k, v in enumerate(swapped) if v != 0][:2]
    swapped[i], swapped[j] = swapped[j], swapped[i]                               #copy mistake
    assert run_tool("8puzzle", {"start": swapped})[1]                            #unsolvable -> rejected

def test_tool_result_validates_as_optimal():
    for i in (P, G):
        res, _ = run_tool(i["domain"], {"start": i["start"]} if i["domain"] == "8puzzle" else {"grid": i["rows"]})
        assert validate(i, res)["category"] == OK

def test_solve_grid_path_matches_cost():
    cells, cost, _ = solve_grid(G["rows"])
    problem = GridProblem(G["rows"])
    assert sum(problem.cost_of(c) for c in cells[1:]) == cost
