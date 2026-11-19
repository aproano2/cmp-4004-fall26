import json
import pytest
import requests
from satlab.llm_client import LLMClient, cost
from satlab.config import Config
from conftest import Transport, Response


def test_cache_repeat_and_secret(tmp_path,config):
    t=Transport(['{"clauses":[]}','{"clauses":[]}'])
    client=LLMClient(config,tmp_path,t)
    messages=[{'role':'user','content':'test'}]
    a=client.call(messages,'p','B',0,0)
    b=LLMClient(config,tmp_path,t).call(messages,'p','B',0,0)
    c=client.call(messages,'p','B',1,0)
    assert len(t.calls)==2 and b['cache_hit'] and not c['cache_hit']
    assert b['llm_time_seconds']==a['llm_time_seconds']
    assert b['charged_cost_usd']==0
    assert a['token_source']=='provider'
    assert all(config.api_key not in p.read_text() for p in tmp_path.rglob('*.json*'))
    assert cost(config,1_000_000,1_000_000,1)==3
    config.output_price=None
    assert cost(config,1,1,1) is None


def test_estimated_tokens_and_timeout(tmp_path,config):
    c=LLMClient(config,tmp_path,lambda *a,**kw:Response('{}',usage=False))
    assert c.call([{'role':'user','content':'12345'}],'p','B',0,0)['token_source']=='estimated_chars_div_4'
    def timeout(*a,**kw): raise requests.Timeout('secret')
    r=LLMClient(config,tmp_path,timeout).call([],'p','C',0,0)
    assert r['error_category']=='llm_timeout' and 'secret' not in r['error_message']


def test_unconfigured_is_explicit(tmp_path):
    with pytest.raises(ValueError,match='not configured'): LLMClient(Config(),tmp_path).call([],'p','B',0,0)


def test_local_compute_cost(config):
    config.provider='ollama'; config.local_hourly_price=2
    assert cost(config,100,100,1800)==1


def test_ollama_wire_contract(tmp_path,config):
    config.provider='ollama'; config.seed=10
    observed=[]
    class LocalResponse:
        def raise_for_status(self): pass
        def json(self): return {'model':'test-only','message':{'content':'{"clauses":[]}'},'prompt_eval_count':8,'eval_count':4}
    def transport(url,**kwargs):
        observed.append((url,kwargs));return LocalResponse()
    r=LLMClient(config,tmp_path,transport).call([{'role':'user','content':'test'}],'p','B',2,0)
    assert observed[0][0].endswith('/api/chat')
    assert observed[0][1]['json']['options']['seed']==12
    assert observed[0][1]['json']['stream'] is False
    assert r['input_tokens']==8 and r['output_tokens']==4
