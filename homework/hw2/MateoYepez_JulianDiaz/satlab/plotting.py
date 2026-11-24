"""Figures contain observed results only; missing arms are labeled pending."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .dataset import ROOT
from .metrics import analyze

ARMS = ['A','B','B-prime','C']


def plot(root: Path = ROOT):
    data = analyze(root)
    df = data['runs']
    out = root/'fig'
    out.mkdir(exist_ok=True)
    def save(fig,name):
        fig.tight_layout()
        fig.savefig(out/name,dpi=200)
        plt.close(fig)
    fig,ax = plt.subplots(figsize=(7,4))
    levels = ['easy','medium','hard']
    for arm in ARMS:
        subset = df[df.arm.eq(arm)]
        if subset.empty:
            ax.plot([],[],label=f'Arm {arm.replace("B-prime","B′")}: pending',linestyle='--')
        else:
            values = subset.assign(correct=subset.correctness.eq('correct')).groupby('difficulty').correct.mean().reindex(levels)
            styles = {'A':dict(marker='D',linestyle='-'), 'B':dict(marker='s',linestyle='--'),
                      'B-prime':dict(marker='o',linestyle=':',markersize=10,fillstyle='none'),
                      'C':dict(marker='^',linestyle='-.')}
            ax.plot(range(3),values*100,label='Arm '+arm.replace('B-prime','B′'),**styles[arm])
    ax.set(xticks=range(3),xticklabels=['Easy','Medium','Hard'],ylabel='Accuracy (%)',ylim=(-2,105),title='Observed accuracy by difficulty')
    ax.legend()
    save(fig,'accuracy_vs_difficulty.png')
    fig,ax = plt.subplots(figsize=(7,4))
    means = df.groupby('arm')[['llm_time_seconds','solver_time_seconds','parse_validation_seconds']].mean()
    means.plot.bar(stacked=True,ax=ax)
    ax.set(ylabel='Seconds',title='Mean pipeline components (original call latency)',xlabel='Arm')
    save(fig,'latency_by_arm.png')
    fig,ax = plt.subplots(figsize=(8,4))
    errors = [e for e in data['errors'] if e['arm']=='B']
    if errors:
        from collections import Counter
        counts = Counter(e['taxonomy_category'] for e in errors)
        ax.barh(list(counts),list(counts.values()))
        ax.set_xlabel('Observed cases, including semantic mismatches with correct status')
    else:
        ax.text(.5,.5,'Arm B pending' if not df.arm.eq('B').any() else 'No observed Arm B failures',ha='center',transform=ax.transAxes)
        ax.set_xticks([])
    ax.set_title('Arm B error taxonomy')
    save(fig,'error_taxonomy.png')
    fig,ax = plt.subplots(figsize=(8,4))
    refinements = data['refinements']
    if refinements:
        labels = ['Initial','Repair 1','Repair 2','Repair 3','Final incorrect / no answer']
        values = [sum(r['final_correct'] and r['iterations']==i for r in refinements) for i in range(4)]
        values.append(sum(not r['final_correct'] for r in refinements))
        ax.bar(labels,values)
        ax.tick_params(axis='x',rotation=15)
        ax.set_ylabel('Paired runs')
    else:
        ax.text(.5,.5,'Arm B′ pending: no refinement runs',ha='center',transform=ax.transAxes)
        ax.set_xticks([])
    ax.set_title('Final correctness after refinement (not merely observable convergence)')
    save(fig,'refinement_success.png')
