"""Tests for the Part 2 duel: the validator, both domains' parsers and tools,
and the prompts.

The validator is the instrument the whole duel is measured with, so it is
tested on hand-built answers for every category, in both domains, before it is
trusted on model output — and A*'s own answers must come out ``optimal`` on all
80 instances.

Run: ``python test_duel.py`` (or ``pytest test_duel.py``).
"""

from __future__ import annotations

from duel_core import solve_astar
from duel_grid import (TOOL_FOLLOWUP, GridDomain, llm_prompt, parse_answer,
                       parse_tool_call, run_astar_tool, tool_prompt)
import duel_puzzle as dp
from validator import (ILLEGAL, MALFORMED, OPTIMAL, SUBOPTIMAL, WRONG_COST,
                       check_path, optimal_cost, puzzle_optimal_cost, validate,
                       validate_puzzle)

#   col 0 1 2
G3 = ["S,.",     # row 0
      ".~.",     # row 1
      "..G"]     # row 2
# optimal: down the left side then right: (1,0)=1 (2,0)=1 (2,1)=1 (2,2)=1 -> 4
OPT_PATH = [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]]


def test_reference_optimum():
    assert optimal_cost(G3) == 4


def test_optimal():
    v = validate(G3, OPT_PATH, 4)
    assert v.category == OPTIMAL and v.correct and v.cost_ok


def test_wrong_cost_is_category_3():
    v = validate(G3, OPT_PATH, 5)
    assert v.category == WRONG_COST and v.legal and not v.correct


def test_string_cost_is_accepted():
    assert validate(G3, OPT_PATH, "4").category == OPTIMAL


def test_suboptimal_is_category_2():
    # across the top: (0,1)=3 (0,2)=1 (1,2)=1 (2,2)=1 -> 6
    v = validate(G3, [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]], 6)
    assert v.category == SUBOPTIMAL and v.true_cost == 6 and v.cost_ok


def test_illegal_jump():
    v = validate(G3, [[0, 0], [2, 0], [2, 1], [2, 2]], 3)
    assert v.category == ILLEGAL and "not a single" in v.reasons[0]


def test_illegal_diagonal():
    assert validate(G3, [[0, 0], [1, 1], [2, 2]], 9).category == ILLEGAL


def test_illegal_out_of_bounds():
    v = validate(G3, [[0, 0], [-1, 0], [0, 0]], 1)
    assert v.category == ILLEGAL


def test_illegal_wrong_endpoints():
    v = validate(G3, [[1, 0], [2, 0], [2, 1]], 2)
    assert v.category == ILLEGAL
    assert any("starts at" in r for r in v.reasons)
    assert any("ends at" in r for r in v.reasons)


def test_illegal_wall():
    walled = ["S#.", "...", "..G"]
    legal, _, reasons = check_path(walled, [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]])
    assert not legal and any("wall" in r for r in reasons)


def test_malformed():
    assert validate(G3, None, None).category == MALFORMED


def test_non_pair_cells_are_illegal():
    assert validate(G3, ["D", "D", "R", "R"], 4).category == ILLEGAL


def test_parser_takes_last_path_object_through_noise():
    text = ('Sure! First guess {"path": [[9,9]], "cost": 1}\n```json\n'
            '{"path": [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]], "cost": 4}\n```')
    path, cost = parse_answer(text)
    assert path == OPT_PATH and cost == 4


def test_parser_accepts_tuples_and_single_quotes():
    path, cost = parse_answer("{'path': [(0, 0), (1, 0)], 'cost': 1}")
    assert path == [[0, 0], [1, 0]] and cost == 1


def test_parser_no_json_is_malformed():
    assert parse_answer("Go down twice then right twice.") == (None, None)


def test_tool_call_parse_and_run():
    call = parse_tool_call('{"tool": "astar", "start": [0, 0], "goal": [2, 2]}')
    result, exps = run_astar_tool(G3, call)
    assert result["cost"] == 4 and result["path"] == OPT_PATH and exps > 0


def test_tool_rejects_out_of_grid_endpoints():
    result, _ = run_astar_tool(G3, {"tool": "astar", "start": [0, 0], "goal": [7, 7]})
    assert "error" in result


def test_prompt_states_endpoints_and_costs():
    p = llm_prompt(G3)
    assert "S is at [0, 0]. G is at [2, 2]." in p and "'~' water = 8" in p
    # regression: un-formatted templates once leaked "{{" into the prompt and
    # the model copied it, making every answer unparseable
    assert "{{" not in p and "{{" not in tool_prompt(G3)
    followup = TOOL_FOLLOWUP.format(reply="r", result="{}")
    assert "{{" not in followup


def test_astar_passes_its_own_validator_on_all_40_grids():
    dom = GridDomain()
    for size, idx, grid, opt in dom.instances():
        row, _ = solve_astar(dom, grid, size, idx, opt)
        assert row["category"] == OPTIMAL, (size, idx, row["reasons"])


# ---- 8-puzzle --------------------------------------------------------------
#   1 2 3
#   4 5 6
#   _ 7 8      optimal: R R (blank right twice), cost 2
P2 = (1, 2, 3, 4, 5, 6, 0, 7, 8)


def test_puzzle_reference_optimum():
    assert puzzle_optimal_cost(P2) == 2


def test_puzzle_optimal_and_word_moves():
    assert validate_puzzle(P2, ["R", "R"], 2).category == OPTIMAL
    assert validate_puzzle(P2, ["right", "Right"], "2").category == OPTIMAL
    assert validate_puzzle(P2, "RR", 2).category == OPTIMAL


def test_puzzle_wrong_cost_is_category_3():
    v = validate_puzzle(P2, ["R", "R"], 3)
    assert v.category == WRONG_COST and v.legal


def test_puzzle_suboptimal_is_category_2():
    v = validate_puzzle(P2, ["R", "L", "R", "R"], 4)
    assert v.category == SUBOPTIMAL and v.true_cost == 4


def test_puzzle_off_board_is_illegal():
    v = validate_puzzle(P2, ["L"], 1)
    assert v.category == ILLEGAL and "off the board" in v.reasons[0]


def test_puzzle_not_reaching_goal_is_illegal():
    v = validate_puzzle(P2, ["R"], 1)
    assert v.category == ILLEGAL and "not the goal" in v.reasons[0]


def test_puzzle_bad_token_and_malformed():
    assert validate_puzzle(P2, ["R", "X"], 2).category == ILLEGAL
    assert validate_puzzle(P2, None, None).category == MALFORMED


def test_puzzle_parser_and_tool():
    moves, cost = dp.parse_answer('ok ```json\n{"moves": ["R", "R"], "cost": 2}\n```')
    assert moves == ["R", "R"] and cost == 2
    call = dp.parse_tool_call('{"tool": "astar", "state": [1,2,3,4,5,6,0,7,8]}')
    result, exps = dp.run_astar_tool(call)
    assert result == {"moves": ["R", "R"], "cost": 2} and exps > 0
    nested, _ = dp.run_astar_tool({"state": [[1, 2, 3], [4, 5, 6], [0, 7, 8]]})
    assert nested["cost"] == 2


def test_puzzle_tool_rejects_bad_states():
    assert "error" in dp.run_astar_tool({"state": [1, 2, 3]})[0]
    assert "error" in dp.run_astar_tool({"state": [2, 1, 3, 4, 5, 6, 7, 8, 0]})[0]  # odd parity


def test_puzzle_prompt_is_clean():
    dom = dp.PuzzleDomain()
    p, t, f = dom.llm_prompt(P2), dom.tool_prompt(P2), dom.followup("r", {})
    assert "current = [1, 2, 3, 4, 5, 6, 0, 7, 8]" in p
    assert "{{" not in p + t + f
    # regression: v1's format example listed real moves ("U", "L") and the
    # model copied them into 37/40 tool-arm answers. The default prompt must
    # show a placeholder only; v1 must still rebuild its archived prompts.
    assert dom.folder == "puzzle" and dom.prompt == "v2"
    for text in (p, t, f):
        assert '["<move>", "<move>", ...]' in text and '["U", "L"' not in text
    v1 = dp.PuzzleDomain("v1")
    assert v1.folder == "puzzle" and '["U", "L", ...]' in v1.llm_prompt(P2)


def test_astar_passes_puzzle_validator_on_all_40_states():
    dom = dp.PuzzleDomain()
    for depth, idx, state, opt in dom.instances():
        row, _ = solve_astar(dom, state, depth, idx, opt)
        assert row["category"] == OPTIMAL, (depth, idx, row["reasons"])


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"  ok  {name}")
    print(f"{len(tests)}/{len(tests)} passed")
