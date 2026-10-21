from __future__ import annotations
from collections import deque
import heapq, time
from dataclasses import dataclass
from math import inf

@dataclass
class SearchResult:
    path: list
    cost: float
    expansions: int
    max_frontier: int
    elapsed: float
    timed_out: bool = False


def reconstruct(parent, state):
    p=[]
    while state is not None:
        p.append(state); state=parent[state]
    p.reverse(); return p


def _run(fn, timeout):
    t0=time.perf_counter()
    try: return fn(t0, timeout)
    except TimeoutError:
        return SearchResult([], inf, 0, 0, time.perf_counter()-t0, True)


def bfs(problem, timeout=5.0):
    def go(t0, lim):
        q=deque([problem.start]); parent={problem.start:None}; cost={problem.start:0}; exp=0; mf=1
        while q:
            if time.perf_counter()-t0 > lim: raise TimeoutError
            s=q.popleft(); exp+=1
            if s==problem.goal:
                path=reconstruct(parent,s); return SearchResult(path,cost[s],exp,mf,time.perf_counter()-t0)
            for ns,step in problem.neighbors(s):
                if ns not in parent:
                    parent[ns]=s; cost[ns]=cost[s]+step; q.append(ns)
            mf=max(mf,len(q))
        return SearchResult([],inf,exp,mf,time.perf_counter()-t0)
    return _run(go,timeout)


def dfs(problem, timeout=5.0):
    def go(t0, lim):
        st=[problem.start]; parent={problem.start:None}; cost={problem.start:0}; exp=0; mf=1
        while st:
            if time.perf_counter()-t0 > lim: raise TimeoutError
            s=st.pop(); exp+=1
            if s==problem.goal:
                path=reconstruct(parent,s); return SearchResult(path,cost[s],exp,mf,time.perf_counter()-t0)
            nbr=list(problem.neighbors(s)); nbr.reverse()
            for ns,step in nbr:
                if ns not in parent:
                    parent[ns]=s; cost[ns]=cost[s]+step; st.append(ns)
            mf=max(mf,len(st))
        return SearchResult([],inf,exp,mf,time.perf_counter()-t0)
    return _run(go,timeout)


def ucs(problem, timeout=5.0):
    def go(t0, lim):
        pq=[(0,0,problem.start)]; counter=1; best={problem.start:0}; parent={problem.start:None}; exp=0; mf=1
        while pq:
            if time.perf_counter()-t0 > lim: raise TimeoutError
            g,_,s=heapq.heappop(pq)
            if g!=best.get(s): continue
            exp+=1
            if s==problem.goal:
                return SearchResult(reconstruct(parent,s),g,exp,mf,time.perf_counter()-t0)
            for ns,step in problem.neighbors(s):
                ng=g+step
                if ng<best.get(ns,inf):
                    best[ns]=ng; parent[ns]=s; heapq.heappush(pq,(ng,counter,ns)); counter+=1
            mf=max(mf,len(pq))
        return SearchResult([],inf,exp,mf,time.perf_counter()-t0)
    return _run(go,timeout)


def astar(problem, heuristic, weight=1.0, timeout=5.0):
    def go(t0, lim):
        h0=heuristic(problem.start, problem.goal, problem)
        pq=[(weight*h0,0,problem.start)]; counter=1; best={problem.start:0}; parent={problem.start:None}; exp=0; mf=1
        while pq:
            if time.perf_counter()-t0 > lim: raise TimeoutError
            f,_,s=heapq.heappop(pq); g=best.get(s)
            if g is None: continue
            expected=g+weight*heuristic(s,problem.goal,problem)
            if abs(f-expected)>1e-12: continue
            exp+=1
            if s==problem.goal:
                return SearchResult(reconstruct(parent,s),g,exp,mf,time.perf_counter()-t0)
            for ns,step in problem.neighbors(s):
                ng=g+step
                if ng<best.get(ns,inf):
                    best[ns]=ng; parent[ns]=s
                    heapq.heappush(pq,(ng+weight*heuristic(ns,problem.goal,problem),counter,ns)); counter+=1
            mf=max(mf,len(pq))
        return SearchResult([],inf,exp,mf,time.perf_counter()-t0)
    return _run(go,timeout)


def ids(problem, timeout=5.0, max_depth=80):
    def go(t0, lim):
        total_exp=0; max_front=0
        def dls(limit):
            nonlocal total_exp,max_front
            stack=[(problem.start,None,0,0)]; pathset={problem.start}; parent={problem.start:None}; gmap={problem.start:0}; mf=1
            while stack:
                if time.perf_counter()-t0>lim: raise TimeoutError
                s,par,d,g=stack.pop(); total_exp+=1
                if s==problem.goal: return reconstruct(parent,s),g
                if d<limit:
                    nbr=list(problem.neighbors(s)); nbr.reverse()
                    for ns,step in nbr:
                        if ns not in pathset:
                            pathset.add(ns); parent[ns]=s; gmap[ns]=g+step; stack.append((ns,s,d+1,g+step))
                    max_front=max(max_front,len(stack))
            return None
        for depth in range(max_depth+1):
            ans=dls(depth)
            if ans:
                path,cost=ans; return SearchResult(path,cost,total_exp,max_front,time.perf_counter()-t0)
        return SearchResult([],inf,total_exp,max_front,time.perf_counter()-t0)
    return _run(go,timeout)
