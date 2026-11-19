import json
import pytest
from satlab.config import Config
from satlab.llm_client import LLMClient

@pytest.fixture
def config():
    return Config(provider='openai-compatible',model='test-only',api_key='secret-test-value',base_url='https://unit.invalid/v1',input_price=1,output_price=2)

class Response:
    def __init__(self,raw,usage=True): self.raw,self.usage=raw,usage
    def raise_for_status(self): pass
    def json(self):
        data={'model':'test-only','id':'test-response','choices':[{'message':{'content':self.raw}}]}
        if self.usage: data['usage']={'prompt_tokens':10,'completion_tokens':5}
        return data

class Transport:
    def __init__(self,outputs): self.outputs=list(outputs); self.calls=[]
    def __call__(self,url,**kwargs):
        self.calls.append(kwargs)
        if not self.outputs: raise AssertionError('unexpected duplicate request')
        return Response(self.outputs.pop(0))
