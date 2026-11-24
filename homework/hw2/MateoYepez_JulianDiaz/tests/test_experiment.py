import json
import shutil
import pandas as pd
import pytest
from satlab.dataset import load_dataset, ROOT
from satlab.experiment import run_experiment
from satlab.llm_client import LLMClient
from satlab.metrics import analyze, summarize
from satlab.plotting import plot
from satlab.reporting import report
from conftest import Transport


def test_full_harness_resume_metrics_figures(tmp_path,config):
    shutil.copytree(ROOT/'problems',tmp_path/'problems')
    problem=load_dataset()[0]
    # Test fixtures only: intentional malformed translation followed by a toy SAT model.
    t=Transport(['broken','{"clauses":[[1]]}','{"answer":"UNSAT","explanation":"test fixture"}'])
    c=LLMClient(config,tmp_path,t)
    df=run_experiment([problem],['A','B','B-prime','C'],1,config,tmp_path,client=c)
    assert len(df)==4 and len(t.calls)==3
    b=df[df.arm.eq('B')].iloc[0]; bp=df[df.arm.eq('B-prime')].iloc[0]
    assert b.initial_call_id==bp.initial_call_id and bp.total_tokens==30
    assert b.correctness=='no-answer' and bp.correctness=='correct'
    assert df[df.arm.eq('A')].iloc[0].total_tokens==0
    resumed=run_experiment([problem],['A','B','B-prime','C'],1,config,tmp_path,client=c)
    assert len(resumed)==4 and len(t.calls)==3
    data=analyze(tmp_path)
    assert data['facts']['refinement_delta_percentage_points']==100
    assert data['facts']['physical_provider_requests']==3
    assert data['refinements'][0]['improved']
    plot(tmp_path); report(tmp_path)
    assert len(list((tmp_path/'fig').glob('*.png')))==4
    assert len((tmp_path/'REPORT.md').read_text().split())<=2500
    assert 'broken' in (tmp_path/'taxonomy.md').read_text()
    assert len(pd.read_csv(tmp_path/'results/errors.csv'))>=2
    from satlab.audit import audit
    assert audit(tmp_path)['valid']


def test_bprime_separate_invocation_reuses_initial_without_cache(tmp_path,config):
    config.cache=False
    p=load_dataset()[0]
    t=Transport(['{"clauses":[[1]]}']); c=LLMClient(config,tmp_path,t)
    run_experiment([p],['B'],1,config,tmp_path,client=c)
    df=run_experiment([p],['B-prime'],1,config,tmp_path,client=c)
    assert len(t.calls)==1
    assert len(set(df.initial_call_id))==1


def test_repetitions_are_distinct(tmp_path,config):
    p=load_dataset()[0]
    t=Transport(['{"clauses":[]}','{"clauses":[]}']); c=LLMClient(config,tmp_path,t)
    df=run_experiment([p],['B'],2,config,tmp_path,client=c)
    s=summarize(df).iloc[0]
    assert s.instances==1 and s.repeats==2 and s.attempts==2
    assert len(set(df.initial_call_id))==2


def test_zero_correct_cost_undefined(tmp_path,config):
    t=Transport(['{"answer":"UNSAT","explanation":"fixture"}'])
    df=run_experiment([load_dataset()[0]],['C'],1,config,tmp_path,client=LLMClient(config,tmp_path,t))
    s=summarize(df).iloc[0]
    assert pd.isna(s.cost_per_correct_answer) and s.error_detection_rate==0


def test_infrastructure_failure_persisted_and_stops(tmp_path,config):
    import requests
    def transport(*a,**kw): raise requests.Timeout()
    with pytest.raises(ValueError,match='Infrastructure failure saved'):
        run_experiment(load_dataset()[:2],['B'],1,config,tmp_path,client=LLMClient(config,tmp_path,transport))
    df=pd.read_csv(tmp_path/'results/runs.csv')
    assert len(df)==1 and df.iloc[0].error_category=='llm_timeout'


def test_artifact_recovers_missing_csv(tmp_path,config):
    t=Transport(['{"clauses":[]}']);c=LLMClient(config,tmp_path,t)
    run_experiment(load_dataset()[:1],['B'],1,config,tmp_path,client=c)
    (tmp_path/'results/runs.csv').unlink()
    df=run_experiment(load_dataset()[:1],['B'],1,config,tmp_path,client=c)
    assert len(df)==1 and len(t.calls)==1
    assert (tmp_path/'results/runs.csv').exists()
