"""Brazo B′ y análisis del equipo, compatible con el solver original."""
from pathlib import Path
import json, csv, time, sys, collections, math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / 'code'))
from logic_lm import parse_json, build_csp
from csp import backtrack_search
from aicourse.llm import LLM
from run_bc import prompt

MAX_RETRIES = 3 # three refinements following the initial B output
MODEL = 'qwen2.5:3b'

def bank():
    out={}
    for file in sorted((BASE/'problems').glob('problems_p*.json')):
        for p in json.loads(file.read_text(encoding='utf-8'))['puzzles']:
            if p['id'] in out: raise ValueError(f'Duplicate id {p["id"]}')
            out[p['id']]=p
    return out

def baseline_B():
    out={}
    for name in ('bc_results.csv','bc_p2.csv','bc_p3.csv'):
        path=BASE/'results'/name
        if path.exists():
            for r in csv.DictReader(path.open(encoding='utf-8',newline='')):
                if r['arm']=='B':out[r['id']]=r
    return out

def evaluate(raw, limit=200_000):
    t=time.perf_counter()
    try:
        spec=parse_json(raw)
        solver=build_csp(spec)
    except Exception as exc:
        return {'signal':'malformed_model','error':f'{type(exc).__name__}: {exc}', 'answer':None,'solver_time_s':time.perf_counter()-t}
    try:
        answer,_=backtrack_search(solver,use_fc=True,use_mrv=True,limit=limit)
    except Exception as exc:
        return {'signal':'solver_error','error':f'{type(exc).__name__}: {exc}', 'answer':None,'solver_time_s':time.perf_counter()-t}
    if answer=='TIMEOUT':return {'signal':'timeout','error':'solver call limit exceeded','answer':None,'solver_time_s':time.perf_counter()-t}
    if answer is None:return {'signal':'unsat','error':'solver reports UNSAT: no solution exists','answer':None,'solver_time_s':time.perf_counter()-t}
    return {'signal':'none','error':'','answer':answer,'solver_time_s':time.perf_counter()-t}

def feedback_prompt(puzzle, previous, error):
    # Does NOT use gold, A model, or whether the answer matched ground truth.
    return (prompt('B',puzzle)+'\n\nYour previous CSP model was:\n'+previous+
            '\n\nSolver error (only feedback):\n'+error+
            '\nCorrect the formal model. Return only the corrected JSON object.')

def run_refinement(ids=None, model=MODEL):
    problems=bank(); original=baseline_B()
    selected=list(ids) if ids is not None else list(problems)
    client=LLM(backend='ollama',model=model,cache_dir=str(BASE/'.llm_cache'),seed=0,temperature=0,timeout=300)
    results=[]; traces=[]
    for pid in selected:
        p=problems[pid];t0=time.perf_counter(); calls=[]; trials=[]
        prior=original.get(pid)
        if prior is not None and prior.get('model_output'):
            raw=prior['model_output'];initial='reused_B'
            tin=int(float(prior.get('tokens_in') or 0));tout=int(float(prior.get('tokens_out') or 0))
            # Account for initial B even if its output was reused rather than recomputed.
            llm_compute=float(prior.get('model_duration_s') or prior.get('llm_time_s') or 0)
            llm_wall=float(prior.get('llm_time_s') or 0)
        else:
            response=client.complete(prompt('B',p['puzzle']),use_cache=True)
            if response.error: raise RuntimeError(f'{pid}: {response.error}')
            raw=response.text;initial='generated_B';calls.append(response)
            tin=int(response.meta.get('prompt_eval_count',0));tout=int(response.meta.get('eval_count',0))
            llm_compute=float(response.meta.get('total_duration',0))/1e9
            llm_wall=float(response.elapsed)
        current=evaluate(raw)
        if prior is not None and prior.get('model_output'):
            # Reuse exactly the same initial B outcome: a CSP with multiple
            # solutions can return a different valid answer on another run.
            prior_signal=prior.get('signal','none')
            try:
                prior_answer=json.loads(prior.get('answer') or 'null')
            except (ValueError, TypeError):
                prior_answer=None
            current={'signal':prior_signal, 'error':prior.get('error') or '',
                     'answer':prior_answer,
                     'solver_time_s':float(prior.get('solver_time_s') or 0)}
        trials.append({'id':pid,'attempt':0,'signal':current['signal'],'error':current['error'],'model_output':raw,'answer':json.dumps(current['answer'],ensure_ascii=False)})
        solver_sum=current['solver_time_s'];fixes=0
        while current['signal']!='none' and fixes<MAX_RETRIES:
            correction=client.complete(feedback_prompt(p['puzzle'],raw,current['error']),use_cache=True)
            if correction.error:
                current={'signal':'llm_error','error':correction.error,'answer':None,'solver_time_s':0.0}
                trials.append({'id':pid,'attempt':fixes+1,'signal':'llm_error','error':correction.error,'model_output':'','answer':'null'})
                break
            calls.append(correction);tin+=int(correction.meta.get('prompt_eval_count',0));tout+=int(correction.meta.get('eval_count',0))
            llm_compute+=float(correction.meta.get('total_duration',0))/1e9
            llm_wall+=correction.elapsed
            fixes+=1;raw=correction.text;current=evaluate(raw);solver_sum+=current['solver_time_s']
            trials.append({'id':pid,'attempt':fixes,'signal':current['signal'],'error':current['error'],'model_output':raw,'answer':json.dumps(current['answer'],ensure_ascii=False)})
        # Ground truth is used ONLY here, after all retries are finished.
        answer=current['answer'];result=('no_answer' if answer is None else 'correct' if answer==p['gold'] else 'incorrect')
        results.append({'id':pid,'arm':'Bprime','level':p['level'],'result':result,'signal':current['signal'],
            'iterations':fixes,'converged':current['signal']=='none','wall_clock_s':round(time.perf_counter()-t0 + (float(prior.get('wall_clock_s') or 0) if prior is not None else 0),6),
            'llm_time_s':round(llm_wall,6),'model_duration_s':round(llm_compute,6),'solver_time_s':round(solver_sum,6),
            'tokens_in':tin,'tokens_out':tout,'model':model,'initial_source':initial,
            'answer':json.dumps(answer,ensure_ascii=False),'error':current['error'],'model_output':raw})
        traces.extend(trials)
        print(pid,result,current['signal'],'refinements',fixes,flush=True)
    resdir=BASE/'results';resdir.mkdir(exist_ok=True)
    pd.DataFrame(results).to_csv(resdir/'bprime_results.csv',index=False)
    pd.DataFrame(traces).to_csv(resdir/'bprime_traces.csv',index=False)
    return pd.DataFrame(results),pd.DataFrame(traces)

def combined_results():
    files=['arm_a_p1_results.csv','arm_a_p2_results.csv','arm_a_p3_results.csv','bc_results.csv','bc_p2.csv','bc_p3.csv','bprime_results.csv']
    all_rows=[]
    for filename in files:
        path = BASE / 'results' / filename
        if path.exists():all_rows.append(pd.read_csv(path).assign(_file=filename))
    if not all_rows:return pd.DataFrame()
    out=pd.concat(all_rows,ignore_index=True)
    out=out.drop_duplicates(['id','arm'],keep='last')
    return out

def scorecard(df):
    rows=[]
    for arm in ('A','B','Bprime','C'):
        group=df[df.arm==arm]
        count=len(group);correct=int((group.result=='correct').sum())
        rows.append({'arm':arm,'n':count,'correct':correct,'incorrect':int((group.result=='incorrect').sum()),
                     'no_answer':int(group.result.isin(['no_answer','no-answer']).sum()),'accuracy':correct/count if count else np.nan,
                     'tokens_in':group.tokens_in.fillna(0).sum() if count else 0,
                     'tokens_out':group.tokens_out.fillna(0).sum() if count else 0,
                     'llm_compute_s':group.model_duration_s.fillna(0).sum() if count and 'model_duration_s' in group else 0})
    return pd.DataFrame(rows)

def make_figures(df):
    folder=BASE/'fig';folder.mkdir(exist_ok=True)
    levels=['easy','medium','hard'];arms=['A','B','Bprime','C']
    accuracy=[]
    for lev in levels:
        for arm in arms:
            subset=df[(df.level==lev)&(df.arm==arm)]
            if len(subset):accuracy.append({'level':lev,'arm':arm,'accuracy':(subset.result=='correct').mean()})
    plot=pd.DataFrame(accuracy)
    fig,ax=plt.subplots(figsize=(8,4.8))
    for arm in arms:
        subset=plot[plot.arm==arm] if not plot.empty else pd.DataFrame()
        if len(subset):ax.plot(subset.level,100*subset.accuracy,marker='o',label=arm)
    ax.set(ylabel='Accuracy (%)',xlabel='Difficulty',ylim=(0,105),title='Accuracy by difficulty (measured runs only)');ax.legend();fig.tight_layout();fig.savefig(folder/'accuracy_vs_difficulty.png',dpi=180);plt.close(fig)
    summary=scorecard(df);subset=summary[summary.n>0]
    fig,ax=plt.subplots(figsize=(7,4.6));ax.bar(subset.arm,100*subset.accuracy)
    ax.set(ylabel='Accuracy (%)',ylim=(0,105),title='Arm accuracy (different n: see scorecard)');fig.tight_layout();fig.savefig(folder/'arm_accuracy.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.6))
    measurements=[]
    for arm in arms:
        group=df[df.arm==arm]
        if len(group):measurements.append((arm,float(group.solver_time_s.fillna(0).mean()),float(group.llm_time_s.fillna(0).mean())))
    names=[a for a,_,_ in measurements]; x=np.arange(len(names));w=.36
    ax.bar(x-w/2,[b for _,b,_ in measurements],w,label='Solver (s)')
    ax.bar(x+w/2,[c for _,_,c in measurements],w,label='LLM wall time (s)')
    ax.set_xticks(x,names);ax.set(ylabel='Average seconds per problem',title='Time by component (cache affects LLM wall time)');ax.legend();fig.tight_layout();fig.savefig(folder/'time_components.png',dpi=180);plt.close(fig)
    if 'Bprime' in set(df.arm):
        vals=df[df.arm=='Bprime'].iterations.value_counts().sort_index()
        fig,ax=plt.subplots(figsize=(7,4));ax.bar(vals.index.astype(str),vals.values)
        ax.set(xlabel='Corrections attempted',ylabel='Problems',title='B′ corrections attempted');fig.tight_layout();fig.savefig(folder/'refinement_iterations.png',dpi=180);plt.close(fig)
    return list(folder.glob('*.png'))

def taxonomy(df):
    ps=bank();rows=[]
    for _,r in df[(df.arm=='B')&(df.result!='correct')].iterrows():
        signal=str(r.get('signal','none'))
        if signal=='malformed_model':cat='Malformed syntax/schema';detect='yes'
        elif signal=='unsat':cat='Over-constrained (unsat)';detect='yes'
        elif signal=='timeout':cat='Solver timeout';detect='yes'
        elif signal=='none':cat='Solvable but incorrect: semantic / underconstrained / type error — manual review';detect='no / sometimes'
        else:cat='Other: '+signal;detect='depends'
        rows.append({'id':r.id,'category':cat,'detectable_without_gold':detect,'model_output':r.get('model_output',''),
                     'error':r.get('error',''),'answer':r.get('answer','')})
    out=pd.DataFrame(rows)
    if len(out):out.to_csv(BASE/'results'/'taxonomy_review.csv',index=False)
    return out

def cost_per_correct(df, compute_usd_per_hour=0.0, input_usd_per_m=0.0, output_usd_per_m=0.0):
    rows=[]
    for arm,g in df.groupby('arm'):
        correct=int((g.result=='correct').sum())
        model_secs=float(g.model_duration_s.fillna(0).sum()) if 'model_duration_s' in g else 0.
        ins=float(g.tokens_in.fillna(0).sum());outs=float(g.tokens_out.fillna(0).sum())
        estimated=model_secs/3600*compute_usd_per_hour+ins/1e6*input_usd_per_m+outs/1e6*output_usd_per_m
        rows.append({'arm':arm,'correct':correct,'tokens_in':ins,'tokens_out':outs,'model_compute_s':model_secs,
                     'estimated_total_usd':estimated if any([compute_usd_per_hour,input_usd_per_m,output_usd_per_m]) else np.nan,
                     'cost_per_correct_usd':(estimated/correct) if correct and any([compute_usd_per_hour,input_usd_per_m,output_usd_per_m]) else np.nan})
    return pd.DataFrame(rows)
