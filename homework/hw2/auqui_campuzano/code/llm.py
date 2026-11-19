"""OpenAI-compatible chat adapter with on-disk cache, retries and token accounting.

Env vars:
  OPENAI_API_KEY   (required)  API key of the provider
  MODEL_NAME       (required)  exact model id, e.g. llama-3.1-8b-instant
  OPENAI_BASE_URL  (optional)  default https://api.openai.com/v1 ; Groq: https://api.groq.com/openai/v1
  TEMPERATURE      (optional)  default 0.7
  MODEL_PROVIDER / MODEL_SIZE (optional, recorded in results/run_meta.json)
No credentials or model are bundled.
"""
import hashlib, json, os, pathlib, time, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE_DIR = pathlib.Path(os.getenv('LLM_CACHE_DIR', ROOT / '.llm_cache'))


class ModelUnavailable(RuntimeError):
    pass


class InfraError(RuntimeError):
    """Network / rate-limit / provider failure. Reported separately, never as a reasoning failure."""


def config():
    return {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('MODEL_NAME'),
        'base': os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/'),
        'temperature': float(os.getenv('TEMPERATURE', '0.7')),
    }


def chat(messages, rep=0, max_tokens=1500):
    """messages: list of {'role','content'}. Returns dict(text, seconds, prompt_tokens,
    completion_tokens, cached, elapsed). `seconds` is the provider latency of the original call
    (also when served from cache); `elapsed` is the real time this call took."""
    cfg = config()
    if not cfg['api_key'] or not cfg['model']:
        raise ModelUnavailable('Set OPENAI_API_KEY and MODEL_NAME (and OPENAI_BASE_URL for non-OpenAI providers).')
    key_obj = {'model': cfg['model'], 'base': cfg['base'], 'temperature': cfg['temperature'],
               'max_tokens': max_tokens, 'rep': rep, 'messages': messages}
    h = hashlib.sha256(json.dumps(key_obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    path = CACHE_DIR / f'{h}.json'
    t0 = time.perf_counter()
    if path.exists():
        d = json.loads(path.read_text())
        d['cached'] = True; d['elapsed'] = time.perf_counter() - t0
        return d
    payload = {'model': cfg['model'], 'temperature': cfg['temperature'], 'max_tokens': max_tokens, 'messages': messages}
    # A custom User-Agent matters: some providers (Cloudflare-fronted, e.g. Groq) reject "Python-urllib".
    headers = {'Authorization': 'Bearer ' + cfg['api_key'], 'Content-Type': 'application/json',
               'User-Agent': 'hw2-formalizer/1.0'}
    last = None
    for attempt in range(6):
        req = urllib.request.Request(cfg['base'] + '/chat/completions', data=json.dumps(payload).encode(), headers=headers)
        t = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
            sec = time.perf_counter() - t
            u = data.get('usage') or {}
            pt, ct = int(u.get('prompt_tokens', 0)), int(u.get('completion_tokens', 0))
            out = {'text': data['choices'][0]['message']['content'] or '', 'seconds': sec, 'prompt_tokens': pt,
                   'completion_tokens': ct, 'model': cfg['model'], 'key': key_obj}
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
            out = dict(out); out['cached'] = False; out['elapsed'] = time.perf_counter() - t0
            return out
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')[:300]
            last = f'HTTP {e.code}: {body}'
            if e.code in (429, 500, 502, 503, 504):
                wait = float(e.headers.get('Retry-After') or 0) or min(2 ** attempt * 2, 60)
                time.sleep(wait); continue
            raise InfraError(last)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = f'{type(e).__name__}: {e}'
            time.sleep(min(2 ** attempt * 2, 60))
    raise InfraError(last or 'unknown provider failure')


def extract_json(text):
    """Return the JSON value inside `text` (tolerates ```json fences and surrounding prose)."""
    t = text.strip()
    if t.startswith('```'):
        t = t.split('\n', 1)[1] if '\n' in t else ''
        t = t.rsplit('```', 1)[0].strip()
    a = t.find('{'); b = t.rfind('}')
    if a < 0 or b < a:
        raise ValueError('No JSON object found in the output')
    return json.loads(t[a:b + 1])


def extract_json_first(text):
    """Like extract_json but returns the FIRST JSON object and ignores any text after it (used for arm C)."""
    t = text.strip()
    if t.startswith('```'):
        t = t.split('\n', 1)[1] if '\n' in t else ''
    a = t.find('{')
    if a < 0:
        raise ValueError('No JSON object found in the output')
    obj, _ = __import__('json').JSONDecoder().raw_decode(t[a:])
    return obj
