"""Read-only local model provenance; no inference or private dataset access."""
import json
import requests
from .config import Config
from .dataset import ROOT
from .llm_client import atomic_json


def main():
    cfg=Config.from_env()
    cfg.require_llm()
    if cfg.provider!='ollama': raise ValueError('snapshot currently supports Ollama')
    base=(cfg.base_url or 'http://localhost:11434').rstrip('/')
    tags=requests.get(base+'/api/tags',timeout=10)
    tags.raise_for_status()
    match=next((m for m in tags.json()['models'] if m['name']==cfg.model),None)
    response=requests.post(base+'/api/show',json={'model':cfg.model},timeout=10)
    response.raise_for_status()
    body=response.json()
    running=requests.get(base+'/api/ps',timeout=10)
    running.raise_for_status()
    snapshot={'running_models':running.json(), 'configured_model':cfg.model,'installed_model':match,
              'details':body.get('details'), 'model_info':body.get('model_info'),
              'parameters':body.get('parameters'),'capabilities':body.get('capabilities')}
    atomic_json(ROOT/'results/provider_snapshot.json',snapshot)
    print(json.dumps({'model':cfg.model,'details':body.get('details'),'digest':match.get('digest') if match else None,'running_models':running.json()},indent=2))

if __name__=='__main__': main()
