from __future__ import annotations
from dataclasses import dataclass
from random import Random
from collections import deque

@dataclass(frozen=True)
class Puzzle:
    start: tuple
    goal: tuple = (1,2,3,4,5,6,7,8,0)
    @property
    def start_state(self): return self.start
    def neighbors(self,s):
        z=s.index(0); r,c=divmod(z,3)
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            rr,cc=r+dr,c+dc
            if 0<=rr<3 and 0<=cc<3:
                j=rr*3+cc; a=list(s); a[z],a[j]=a[j],a[z]; yield tuple(a),1
    @property
    def goal_state(self): return self.goal

@dataclass(frozen=True)
class Grid:
    terrain: tuple
    start: tuple=(0,0)
    goal: tuple=None
    def __post_init__(self):
        if self.goal is None: object.__setattr__(self,'goal',(len(self.terrain)-1,len(self.terrain)-1))
    @property
    def start_state(self): return self.start
    @property
    def goal_state(self): return self.goal
    def neighbors(self,s):
        r,c=s; n=len(self.terrain)
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            rr,cc=r+dr,c+dc
            if 0<=rr<n and 0<=cc<n:
                yield (rr,cc), self.terrain[rr][cc]

# Compatibility with algorithm interface
for cls in (Puzzle,Grid):
    cls.start=cls.start if hasattr(cls,'start') else None

def puzzle_heuristic_manhattan(s,g,problem):
    pos={v:i for i,v in enumerate(g)}; total=0
    for i,v in enumerate(s):
        if v:
            j=pos[v]; total+=abs(i//3-j//3)+abs(i%3-j%3)
    return total

def puzzle_heuristic_misplaced(s,g,problem):
    return sum(a!=b and a!=0 for a,b in zip(s,g))

def grid_heuristic(s,g,problem):
    # Minimum possible terrain-entry cost is 1 because generated terrain costs are >=1.
    return abs(s[0]-g[0])+abs(s[1]-g[1])

def generate_puzzle_instances(depths, per_level=10):
    goal=(1,2,3,4,5,6,7,8,0)
    q=deque([(goal,0)]); by={d:[] for d in depths}; seen={goal}
    while q and any(len(by[d])<per_level for d in depths):
        s,d=q.popleft()
        if d in by and len(by[d])<per_level: by[d].append(s)
        if d<max(depths):
            z=s.index(0); r,c=divmod(z,3)
            for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
                rr,cc=r+dr,c+dc
                if 0<=rr<3 and 0<=cc<3:
                    j=rr*3+cc; a=list(s); a[z],a[j]=a[j],a[z]; t=tuple(a)
                    if t not in seen: seen.add(t); q.append((t,d+1))
    return {d: [Puzzle(s) for s in by[d][:per_level]] for d in depths}

def generate_grid_instances(sizes, per_level=10, seed=20261002):
    out={}; rng=Random(seed)
    for n in sizes:
        arr=[]
        for i in range(per_level):
            # Deterministic terrain with costs 1..9. Reject rare trivial cases where BFS is optimal.
            for attempt in range(200):
                terrain=tuple(tuple(rng.randint(1,9) for _ in range(n)) for _ in range(n))
                arr.append(Grid(terrain))
                break
        out[n]=arr
    return out
