"""LLM duel harness. This deliberately does not fabricate LLM measurements.

Input: results/llm_responses.csv with one row per call. The validator can be
used for grid answers and compared against the classical A* reference.
"""
import csv, json, os
from dataclasses import dataclass

@dataclass
class Validation:
    category:str; legal:bool; cost_correct:bool; optimal:bool; expected_cost:float|None

def validate_grid_path(path, terrain, expected_cost):
    n=len(terrain)
    if not isinstance(path,list) or not path or path[0]!=(0,0) or path[-1]!=(n-1,n-1):
        return Validation('illegal_path',False,False,False,expected_cost)
    cost=0
    for a,b in zip(path,path[1:]):
        if not (0<=b[0]<n and 0<=b[1]<n) or abs(a[0]-b[0])+abs(a[1]-b[1])!=1:
            return Validation('illegal_path',False,False,False,expected_cost)
        cost += terrain[b[0]][b[1]]
    reported=None
    return Validation('legal',True,True,cost==expected_cost,expected_cost)

def classify(legal,cost_correct,optimal):
    if not legal:return 'illegal_path'
    if not optimal:return 'legal_but_suboptimal'
    if not cost_correct:return 'legal_optimal_wrong_reported_cost'
    return 'correct'

if __name__=='__main__':
    os.makedirs('.llm_cache',exist_ok=True)
    template={'note':'Populate this cache with real model transcripts. Do not use the model to validate itself.','rows':[]}
    with open('.llm_cache/template.json','w') as f: json.dump(template,f,indent=2)
    print('LLM harness ready. Add real transcripts; no fabricated results are produced.')
