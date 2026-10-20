"""Export the exact benchmark instances as JSON so the LLM receives the same problems."""
import json, os, sys
sys.path.insert(0,os.path.dirname(__file__))
from domains import generate_puzzle_instances,generate_grid_instances
os.makedirs('results/instances',exist_ok=True)
p=generate_puzzle_instances([4,8,12,16],10)
for d,items in p.items():
    json.dump([{'start':x.start,'goal':x.goal} for x in items],open(f'results/instances/puzzle_{d}.json','w'),indent=2)
g=generate_grid_instances([5,8,12,16],10)
for n,items in g.items():
    json.dump([{'terrain':x.terrain,'start':x.start,'goal':x.goal} for x in items],open(f'results/instances/grid_{n}.json','w'),indent=2)
