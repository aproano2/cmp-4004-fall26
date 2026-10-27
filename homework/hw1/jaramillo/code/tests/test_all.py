"""Tests. Desde la carpeta del deber:   python -m pytest code/tests -q"""
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import duel                                                       # noqa: E402
from domains import (EightPuzzle, GridProblem, GOAL, h_misplaced,  # noqa: E402
                     h_manhattan_puzzle, h_manhattan_grid, h_zero, is_solvable,
                     load_puzzles, load_grids)
from search import (bfs, dfs, ucs, ids, astar,                     # noqa: E402
                    effective_branching_factor)
from validator import validate, parse_reply                        # noqa: E402


class TinyGraph:
    """Grafo de la semana 3: start->A cuesta 10, start->B->A cuesta 2."""
    EDGES = {"start": [("A", 10), ("B", 1)], "B": [("A", 1)], "A": []}
    initial = "start"

    def actions(self, s):
        return [d for d, _ in self.EDGES[s]]

    def result(self, s, a):
        return a

    def is_goal(self, s):
        return s == "A"

    def step_cost(self, s, a):
        return dict(self.EDGES[s])[a]


def true_depths():
    """BFS exhaustivo hacia atrás desde la meta: profundidad óptima de cada estado."""
    pz, dist, q = EightPuzzle(GOAL), {GOAL: 0}, deque([GOAL])
    while q:
        s = q.popleft()
        for a in pz.actions(s):
            t = pz.result(s, a)
            if t not in dist:
                dist[t] = dist[s] + 1
                q.append(t)
    return dist


DIST = true_depths()
TINY_GRID = ["S~G",
             "..."]            # recto: 8 + 1 = 9; rodeando: 1+1+1+1 = 4


# ---- algoritmos -----------------------------------------------------------

def test_bfs_suboptimal_on_nonuniform_costs():
    assert bfs(TinyGraph()).cost == 10
    assert ucs(TinyGraph()).cost == 2
    assert bfs(GridProblem(TINY_GRID)).cost == 9


def test_ucs_and_astar_optimal_on_tiny_grid():
    p = GridProblem(TINY_GRID)
    assert ucs(p).cost == 4
    assert astar(p, h_manhattan_grid).cost == 4
    assert "".join(astar(p, h_manhattan_grid).path) == "DRRU"


def test_puzzle_bank_depths_and_optimal_algorithms():
    for depth, states in load_puzzles().items():
        for s in states:
            assert DIST[s] == depth
            p = EightPuzzle(s)
            for r in (bfs(p), ucs(p), ids(p), astar(p, h_misplaced),
                      astar(p, h_manhattan_puzzle)):
                assert r.solved and r.cost == depth == r.length, r.algorithm


def test_dfs_terminates_and_returns_a_legal_path():
    s = load_puzzles()[8][0]
    r = dfs(EightPuzzle(s))
    assert r.solved
    assert validate("puzzle", s, "".join(r.path), r.cost, 8).category == "suboptimal"


def test_ucs_equals_astar_on_every_grid():
    for grids in load_grids().values():
        for g in grids:
            p = GridProblem(g)
            assert ucs(p).cost == astar(p, h_manhattan_grid).cost \
                == astar(p, h_zero).cost


def test_timeout_is_reported_as_timeout():
    r = ids(GridProblem(load_grids()[16][0]), timeout=0.05)
    assert r.status in ("timeout", "solved")
    r = bfs(EightPuzzle(load_puzzles()[16][0]), timeout=0.0)
    assert r.status == "timeout" and r.cost is None


# ---- heurísticas -----------------------------------------------------------

def test_puzzle_heuristics_admissible_on_all_181440_states():
    p = EightPuzzle(GOAL)
    assert len(DIST) == 181440
    for s, d in DIST.items():
        assert h_misplaced(p, s) <= h_manhattan_puzzle(p, s) <= d


def test_manhattan_puzzle_consistent():
    p = EightPuzzle(GOAL)
    for s in list(DIST)[::97]:
        for a in p.actions(s):
            assert h_manhattan_puzzle(p, s) <= 1 + h_manhattan_puzzle(p, p.result(s, a))


def test_grid_heuristic_admissible_from_every_cell():
    g = load_grids()[8][0]
    for r in range(8):
        for c in range(8):
            rows = [row.replace("S", ".") for row in g]
            if rows[r][c] == "G":
                continue
            rows[r] = rows[r][:c] + "S" + rows[r][c + 1:]
            p = GridProblem(rows)
            assert h_manhattan_grid(p, p.initial) <= ucs(p).cost


def test_weighted_astar_can_be_suboptimal_but_never_better():
    worse = 0
    for grids in load_grids().values():
        for g in grids:
            p = GridProblem(g)
            a, w = astar(p, h_manhattan_grid), astar(p, h_manhattan_grid, weight=3)
            assert w.cost >= a.cost
            worse += w.cost > a.cost
    assert worse > 0


def test_effective_branching_factor():
    # R&N: 52 nodos a profundidad 5 -> b* = 1.92
    assert abs(effective_branching_factor(52, 5) - 1.92) < 0.01
    assert abs(effective_branching_factor(2 + 4 + 8, 3) - 2.0) < 1e-3


def test_solvability():
    assert is_solvable(GOAL)
    assert not is_solvable((1, 2, 3, 4, 5, 6, 8, 7, 0))


# ---- validador ------------------------------------------------------------

def test_parse_reply():
    assert parse_reply("thinking...\nPATH: DRRU\nCOST: 4") == ("DRRU", 4)
    assert parse_reply("**PATH:** D, R -> R U\n**COST:** 4") == ("DRRU", 4)
    assert parse_reply("PATH: RR\nCOST: 9\nwait\nPATH: DRRU\nCOST: 4") == ("DRRU", 4)
    assert parse_reply("I think it is right") == (None, None)


def test_validator_grid_categories():
    v = lambda path, cost: validate("grid", TINY_GRID, path, cost, 4).category
    assert v("DRRU", 4) == "correct"
    assert v("DRRU", 5) == "wrong_cost"
    assert v("DRRU", None) == "wrong_cost"
    assert v("RR", 9) == "suboptimal"
    assert v("RRR", 3) == "illegal"          # se sale del grid
    assert v("DR", 2) == "illegal"           # no llega a G
    assert v("DXRU", 4) == "illegal"         # movimiento desconocido
    assert v(None, 4) == "no_answer"
    assert validate("grid", ["S#G", "..."], "RR", 2, 4).category == "illegal"  # pared


def test_validator_puzzle_categories():
    s = (1, 2, 3, 4, 5, 6, 0, 7, 8)          # óptimo: RR
    v = lambda path, cost: validate("puzzle", s, path, cost, 2).category
    assert v("RR", 2) == "correct"
    assert v("RR", 3) == "wrong_cost"
    assert v("RLRR", 4) == "suboptimal"
    assert v("D", 1) == "illegal"            # el hueco se sale del tablero
    assert v("R", 1) == "illegal"            # no es la meta


# ---- brazo tool (con un modelo falso, no hace falta LLM) --------------------------

class FakeModel:
    def __init__(self, replies):
        self.replies, self.seen = list(replies), []

    def chat(self, messages, **kw):
        self.seen.append(messages)
        return {"text": self.replies.pop(0), "status": "ok", "latency_s": 0.1,
                "tokens_in": 10, "tokens_out": 5}


def test_extract_json_and_run_tool():
    call = duel.extract_json('sure:\n```json\n{"tool": "astar_solve", '
                             '"domain": "grid", "grid": ["S~G", "..."]}\n```')
    result, parsed = duel.run_tool(call)
    assert result["path"] == "DRRU" and result["cost"] == 4 and parsed == TINY_GRID
    assert "error" in duel.run_tool({"domain": "grid", "grid": ["S~", "..."]})[0]
    assert "error" in duel.run_tool({"domain": "puzzle",
                                     "state": [1, 2, 3, 4, 5, 6, 8, 7, 0]})[0]
    assert duel.extract_json("PATH: RR\nCOST: 2") is None
    # una llamada sin "tool" pero con argumentos cuenta; un resultado inventado no
    assert duel.extract_call('{"state": [1, 2, 3, 4, 5, 6, 0, 7, 8]}')["state"][6] == 0
    assert duel.extract_call('{"tool_result": "PATH: RR, COST: 2"}') is None
    assert duel.extract_call('{"x": 1}\n{"tool": "astar_solve", "grid": ["SG"]}')["grid"] == ["SG"]


def test_tool_arm_end_to_end():
    opt = astar(GridProblem(TINY_GRID), h_manhattan_grid)
    good = FakeModel(['{"tool": "astar_solve", "domain": "grid", '
                      '"grid": ["S~G", "..."]}', "PATH: DRRU\nCOST: 4"])
    row = duel.arm_tool(good, "grid", 2, 0, TINY_GRID, opt)
    assert row["category"] == "correct" and row["tool_calls"] == 1
    assert row["tool_args_match"] is True
    assert "TOOL RESULT" in good.seen[1][-1]["content"]

    # el modelo copia mal el grid: la herramienta resuelve otro problema
    bad = FakeModel(['{"tool": "astar_solve", "domain": "grid", '
                     '"grid": ["S.G", "..."]}', "PATH: RR\nCOST: 2"])
    row = duel.arm_tool(bad, "grid", 2, 0, TINY_GRID, opt)
    assert row["category"] == "suboptimal" and row["tool_args_match"] is False

    # el modelo ignora la herramienta
    lazy = FakeModel(["PATH: RR\nCOST: 9"])
    row = duel.arm_tool(lazy, "grid", 2, 0, TINY_GRID, opt)
    assert row["tool_calls"] == 0 and row["category"] == "suboptimal"


def test_llm_arm_and_summary():
    opt = astar(GridProblem(TINY_GRID), h_manhattan_grid)
    rows = [duel.arm_classical("grid", 2, 0, TINY_GRID, opt),
            duel.arm_llm(FakeModel(["PATH: DRRU\nCOST: 6"]), "grid", 2, 0,
                         TINY_GRID, opt)]
    assert [r["category"] for r in rows] == ["correct", "wrong_cost"]
    summ = {(s["arm"], s["domain"], s["level"]): s for s in duel.summarize(rows)}
    assert summ["llm", "grid", 2]["optimal_path_rate"] == 1.0
    assert summ["llm", "grid", 2]["fully_correct_rate"] == 0.0


def test_tool_is_lenient_on_format_but_not_on_content():
    # grid como un solo string y sin "domain": se acepta
    result, parsed = duel.run_tool({"tool": "astar_solve", "grid": "S ~ G\n. . ."})
    assert result["cost"] == 4 and parsed == TINY_GRID
    # celdas mal copiadas (fila corta): error, no se adivina
    assert "error" in duel.run_tool({"tool": "astar_solve", "grid": "S~G\n.."})[0]


def test_tool_arm_retries_after_a_tool_error():
    opt = astar(GridProblem(TINY_GRID), h_manhattan_grid)
    m = FakeModel(['{"tool": "astar_solve", "grid": ["S~G", ".."]}',
                   '{"tool": "astar_solve", "grid": ["S~G", "..."]}',
                   "PATH: DRRU\nCOST: 4"])
    row = duel.arm_tool(m, "grid", 2, 0, TINY_GRID, opt)
    assert row["category"] == "correct" and row["tool_calls"] == 2
    assert "Fix the call" in m.seen[1][-1]["content"]
