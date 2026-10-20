from __future__ import annotations
import csv, os, sys, statistics
sys.path.insert(0, os.path.dirname(__file__))
from domains import generate_puzzle_instances, generate_grid_instances, puzzle_heuristic_manhattan, puzzle_heuristic_misplaced, grid_heuristic
from search_algorithms import bfs,dfs,ucs,ids,astar

TIMEOUT=5.0
ALGOS={'BFS':bfs,'DFS':dfs,'UCS':ucs,'IDS':ids,'A*_manhattan':lambda p,timeout:astar(p,puzzle_heuristic_manhattan,1,timeout),'A*_misplaced':lambda p,timeout:astar(p,puzzle_heuristic_misplaced,1,timeout),'A*_w3_manhattan':lambda p,timeout:astar(p,puzzle_heuristic_manhattan,3,timeout)}

def run():
    os.makedirs('results',exist_ok=True); os.makedirs('fig',exist_ok=True)
    rows=[]
    puzzles=generate_puzzle_instances([4,8,12,16],10)
    for depth,insts in puzzles.items():
        for idx,p in enumerate(insts):
            for name,fn in ALGOS.items():
                r=fn(p,TIMEOUT); rows.append(['8puzzle',depth,idx,name,r.cost if r.path else '',len(r.path)-1 if r.path else '',r.expansions,r.max_frontier,r.elapsed,r.timed_out])
    grids=generate_grid_instances([5,8,12,16],10)
    for size,insts in grids.items():
        for idx,p in enumerate(insts):
            for name,fn in {'BFS':bfs,'DFS':dfs,'UCS':ucs,'IDS':ids,'A*_grid':lambda p,timeout:astar(p,grid_heuristic,1,timeout),'A*_grid_w3':lambda p,timeout:astar(p,grid_heuristic,3,timeout)}.items():
                r=fn(p,TIMEOUT); rows.append(['grid',size,idx,name,r.cost if r.path else '',len(r.path)-1 if r.path else '',r.expansions,r.max_frontier,r.elapsed,r.timed_out])
    with open('results/classical_raw.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['domain','level','instance','algorithm','solution_cost','solution_length','expansions','max_frontier','wall_time_s','timed_out']); w.writerows(rows)
    return rows
if __name__=='__main__': run()
