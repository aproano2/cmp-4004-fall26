from __future__ import annotations
import csv, os, statistics, math
from collections import defaultdict
import matplotlib.pyplot as plt

os.makedirs('results',exist_ok=True); os.makedirs('fig',exist_ok=True)
rows=[]
with open('results/classical_raw.csv') as f:
    for r in csv.DictReader(f):
        for k in ['level','instance','expansions','max_frontier','wall_time_s']: r[k]=float(r[k]) if k=='wall_time_s' else int(r[k])
        r['solution_cost']=float(r['solution_cost']) if r['solution_cost'] else None
        r['solution_length']=int(r['solution_length']) if r['solution_length'] else None
        r['timed_out']=r['timed_out']=='True'; rows.append(r)

def med_iqr(vals):
    vals=[x for x in vals if x is not None]
    if not vals:return '', ''
    vals=sorted(vals); med=statistics.median(vals)
    q1=statistics.median(vals[:len(vals)//2]); q3=statistics.median(vals[(len(vals)+1)//2:])
    return med,q3-q1
summary=[]
for key,g in __import__('itertools').groupby(sorted(rows,key=lambda x:(x['domain'],x['level'],x['algorithm'])), key=lambda x:(x['domain'],x['level'],x['algorithm'])):
    vals=list(g); out=[key[0],key[1],key[2]]
    for metric in ['solution_cost','solution_length','expansions','max_frontier','wall_time_s']:
        m,i=med_iqr([v[metric] for v in vals if not v['timed_out']]); out += [m,i]
    out += [sum(v['timed_out'] for v in vals),len(vals)]
    summary.append(out)
with open('results/classical_summary.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['domain','level','algorithm','cost_median','cost_iqr','length_median','length_iqr','expansions_median','expansions_iqr','frontier_median','frontier_iqr','time_median_s','time_iqr_s','timeouts','n']); w.writerows(summary)

# Figure 1: expansions by size
for domain, filename, xlabel in [('8puzzle','fig/fig1_expansions_puzzle.png','solution depth'),('grid','fig/fig2_expansions_grid.png','grid size')]:
    plt.figure(figsize=(8,5))
    algos=['BFS','UCS','A*_manhattan','A*_misplaced'] if domain=='8puzzle' else ['BFS','UCS','A*_grid']
    for a in algos:
        xs=[]; ys=[]
        for r in summary:
            if r[0]==domain and r[2]==a:
                xs.append(r[1]); ys.append(r[7])
        if xs: plt.plot(xs,ys,marker='o',label=a)
    plt.xlabel(xlabel); plt.ylabel('median node expansions'); plt.title(f'{domain}: search effort'); plt.legend(); plt.tight_layout(); plt.savefig(filename,dpi=160); plt.close()

# Figure 3: A* weight tradeoff on 8-puzzle
plt.figure(figsize=(8,5))
for a in ['A*_manhattan','A*_w3_manhattan']:
    xs=[]; ys=[]
    for r in summary:
        if r[0]=='8puzzle' and r[2]==a: xs.append(r[1]); ys.append(r[3])
    plt.plot(xs,ys,marker='o',label=a)
plt.xlabel('solution depth'); plt.ylabel('median solution cost'); plt.title('Weighted A*: solution-quality tradeoff'); plt.legend(); plt.tight_layout(); plt.savefig('fig/fig3_weighted_cost.png',dpi=160); plt.close()

# Figure 4: runtime
plt.figure(figsize=(8,5))
for a in ['BFS','UCS','A*_manhattan']:
    xs=[]; ys=[]
    for r in summary:
        if r[0]=='8puzzle' and r[2]==a: xs.append(r[1]); ys.append(r[11])
    plt.plot(xs,ys,marker='o',label=a)
plt.xlabel('solution depth'); plt.ylabel('median wall-clock time (s)'); plt.title('8-puzzle runtime scaling'); plt.legend(); plt.tight_layout(); plt.savefig('fig/fig4_runtime.png',dpi=160); plt.close()

# Automated checks for required claims
byinst=defaultdict(dict)
for r in rows: byinst[(r['domain'],r['level'],r['instance'])][r['algorithm']]=r
checks=[]
for k,d in byinst.items():
    if k[0]=='8puzzle':
        if all(a in d and not d[a]['timed_out'] for a in ['UCS','A*_manhattan']): checks.append(['UCS_vs_Astar_equal_cost',k[1],k[2],abs(d['UCS']['solution_cost']-d['A*_manhattan']['solution_cost'])<1e-9])
        if all(a in d and not d[a]['timed_out'] for a in ['A*_manhattan','A*_misplaced']): checks.append(['Manhattan_dominance',k[1],k[2],d['A*_manhattan']['expansions']<=d['A*_misplaced']['expansions']])
with open('results/required_checks.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['check','level','instance','passed']); w.writerows(checks)
