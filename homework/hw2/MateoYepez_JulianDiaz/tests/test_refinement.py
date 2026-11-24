import json
import pytest
from satlab.arm_b import run as run_b
from satlab.arm_b_refinement import run as refine
from satlab.dataset import public_problem, load_dataset
from satlab.llm_client import LLMClient
from satlab.prompts import initial
from conftest import Transport


def test_pair_and_repair_no_truth(tmp_path,config):
    public=public_problem(load_dataset()[0])
    t=Transport(['bad','{"clauses":[[99]]}','{"clauses":[[1]]}'])
    client=LLMClient(config,tmp_path,t)
    first=run_b(public,client,0,10)
    attempts=refine(public,client,0,10,first)
    assert attempts[0] is first
    assert len(attempts)==3 and attempts[-1]['predicted_status']=='SAT'
    sent=json.dumps(t.calls)
    assert all(word not in sent for word in ['ground_truth','witness','reasoning','expected_status'])
    assert 'clauses' not in public


def test_three_repairs_only(tmp_path,config):
    t=Transport(['bad']*4); c=LLMClient(config,tmp_path,t)
    public=public_problem(load_dataset()[0])
    first=run_b(public,c,0,10)
    attempts=refine(public,c,0,10,first)
    assert len(attempts)==4 and len(t.calls)==4
    with pytest.raises(ValueError): refine(public,c,0,10,first,4)


def test_unsat_is_not_an_error(tmp_path,config):
    t=Transport(['{"clauses":[[]]}']); c=LLMClient(config,tmp_path,t)
    public=public_problem(load_dataset()[0]) # reference SAT deliberately unavailable to refine
    first=run_b(public,c,0,10)
    assert len(refine(public,c,0,10,first))==1
    assert first['predicted_status']=='UNSAT'


def test_public_prompt_whitelist():
    p=load_dataset()[0]
    p['ground_truth']['reasoning']='UNIQUE_PRIVATE_SENTINEL'
    for arm in ['B','C']:
        messages=json.dumps(initial(p,arm))
        assert 'UNIQUE_PRIVATE_SENTINEL' not in messages
        assert 'ground_truth' not in messages
    assert 'variables' not in initial(p,'C')[-1]['content']


def test_resume_partial_repairs(tmp_path,config):
    public=public_problem(load_dataset()[0])
    t=Transport(['bad','bad','{"clauses":[[1]]}']); c=LLMClient(config,tmp_path,t)
    first=run_b(public,c,0,10)
    prior=refine(public,c,0,10,first,max_repairs=1)
    resumed=refine(public,c,0,10,first,prior=prior)
    assert len(resumed)==3 and len(t.calls)==3
