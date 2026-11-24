"""OpenAI-compatible HTTP and Ollama; immutable responses and JSONL audit trail."""
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
import requests
from .config import Config
from .prompts import VERSION


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2))
    tmp.replace(path)


def cost(config: Config, input_tokens: int, output_tokens: int, seconds: float):
    if config.provider == 'ollama' and config.local_hourly_price is not None:
        return seconds / 3600 * config.local_hourly_price
    if config.input_price is None or config.output_price is None:
        return None
    return (input_tokens*config.input_price + output_tokens*config.output_price)/1e6


class LLMClient:
    def __init__(self, config: Config, root: Path, transport=None):
        self.config, self.root = config, root
        self.transport = transport or requests.post
        self.events = []

    def call(self, messages: list[dict], problem_id: str, arm: str, repeat: int, iteration: int) -> dict:
        self.config.require_llm()
        cfg = self.config
        params = {'temperature':cfg.temperature,'max_tokens':cfg.max_tokens}
        if cfg.seed is not None:
            params['seed'] = cfg.seed + repeat
        identity = {'provider':cfg.provider,'model':cfg.model,'base_url':cfg.base_url,
                    'prompt_version':VERSION,'messages':messages,'parameters':params,
                    'repeat':repeat,'problem_id':problem_id,'arm':arm,'iteration':iteration}
        key = digest(identity)
        path = self.root / '.llm_cache' / f'{key}.json'
        started = time.perf_counter()
        if cfg.cache and path.exists():
            result = json.loads(path.read_text())
            result['cache_hit'] = True
            result['access_seconds'] = time.perf_counter()-started
            result['charged_cost_usd'] = 0.0
        else:
            raw, usage, error, category, response_id, reported_model = '', {}, '', '', '', ''
            try:
                if cfg.provider == 'ollama':
                    options = {'temperature':cfg.temperature,'num_predict':cfg.max_tokens,'use_mmap':True,'num_ctx':cfg.max_tokens}
                    if 'seed' in params: options['seed'] = params['seed']
                    response = self.transport((cfg.base_url or 'http://localhost:11434').rstrip('/')+'/api/chat',
                        json={'model':cfg.model,'messages':messages,'stream':False,'options':options},timeout=cfg.timeout)
                    response.raise_for_status()
                    body = response.json()
                    raw = body['message']['content']
                    usage = {'input':body.get('prompt_eval_count'),'output':body.get('eval_count')}
                else:
                    response = self.transport(cfg.base_url.rstrip('/')+'/chat/completions',
                        headers={'Authorization':f'Bearer {cfg.api_key}'},
                        json={'model':cfg.model,'messages':messages,**params},timeout=cfg.timeout)
                    response.raise_for_status()
                    body = response.json()
                    raw = body['choices'][0]['message']['content'] or ''
                    u = body.get('usage',{})
                    usage = {'input':u.get('prompt_tokens'),'output':u.get('completion_tokens')}
                response_id = body.get('id','')
                reported_model = body.get('model',cfg.model)
                if not isinstance(raw,str): raise ValueError('provider content is not text')
            except requests.Timeout:
                category,error = 'llm_timeout','LLM request timed out'
            except Exception as exc:
                # Do not persist exception bodies/URLs, which can echo secrets.
                category,error = 'api_error',f'Provider request failed ({type(exc).__name__})'
            elapsed = time.perf_counter()-started
            estimated = any(usage.get(k) is None for k in ('input','output'))
            it = usage.get('input')
            ot = usage.get('output')
            if it is None: it = math.ceil(sum(len(m['content']) for m in messages)/4)
            if ot is None: ot = math.ceil(len(raw)/4)
            money = cost(cfg,it,ot,elapsed) if not error else None
            result = {**identity,'call_id':key,'raw':raw,'model_size':cfg.model_size,
                      'reported_model':reported_model,'response_id':response_id,
                      'input_tokens':it,'output_tokens':ot,'token_source':'estimated_chars_div_4' if estimated else 'provider',
                      'llm_time_seconds':elapsed,'access_seconds':elapsed,'cache_hit':False,
                      'estimated_cost_usd':money,'charged_cost_usd':money,'error_category':category,
                      'error_message':error,'timestamp':datetime.now(timezone.utc).isoformat()}
            # Failed requests are logged but not cached, allowing explicit retry.
            if cfg.cache and not error: atomic_json(path,result)
        log = self.root / 'results/calls.jsonl'
        log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('a') as handle: handle.write(json.dumps(result,ensure_ascii=False)+'\n')
        self.events.append(result)
        return result
