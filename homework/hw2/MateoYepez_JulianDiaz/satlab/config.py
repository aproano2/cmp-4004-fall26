"""Environment configuration; secrets excluded from experiment identities."""
from dataclasses import dataclass, asdict, field
import os
from dotenv import load_dotenv
from .dataset import ROOT

@dataclass
class Config:
    provider: str = ''
    model: str = ''
    api_key: str = field(default='', repr=False)
    base_url: str = ''
    model_size: str = 'unknown'
    temperature: float = 0
    max_tokens: int = 2048
    timeout: float = 120
    solver_timeout: float = 10
    seed: int | None = None
    cache: bool = True
    input_price: float | None = None
    output_price: float | None = None
    local_hourly_price: float | None = None
    price_source: str = 'unconfigured; no monetary claim'
    price_date: str = ''

    def public(self) -> dict:
        return {k:v for k,v in asdict(self).items() if k != 'api_key'}

    def require_llm(self) -> None:
        if self.provider not in ('openai-compatible','ollama') or not self.model:
            raise ValueError('LLM not configured: set LLM_PROVIDER and LLM_MODEL in .env; see README.md')
        if self.provider == 'openai-compatible' and (not self.base_url or not self.api_key):
            raise ValueError('Set LLM_BASE_URL and LLM_API_KEY for the compatible provider')

    @classmethod
    def from_env(cls):
        load_dotenv(ROOT / '.env', override=False)
        def optional(name):
            return float(os.environ[name]) if os.getenv(name) else None
        return cls(provider=os.getenv('LLM_PROVIDER',''),model=os.getenv('LLM_MODEL',''),
                   api_key=os.getenv('LLM_API_KEY',''),base_url=os.getenv('LLM_BASE_URL',''),
                   model_size=os.getenv('LLM_MODEL_SIZE','unknown'),
                   temperature=float(os.getenv('LLM_TEMPERATURE','0')),
                   max_tokens=int(os.getenv('LLM_MAX_TOKENS','2048')),
                   timeout=float(os.getenv('LLM_TIMEOUT','120')),
                   solver_timeout=float(os.getenv('SOLVER_TIMEOUT','10')),
                   seed=int(os.environ['LLM_SEED']) if os.getenv('LLM_SEED') else None,
                   input_price=optional('INPUT_PRICE_PER_MILLION'),
                   output_price=optional('OUTPUT_PRICE_PER_MILLION'),
                   local_hourly_price=optional('LOCAL_PRICE_PER_HOUR'),
                   price_source=os.getenv('PRICE_SOURCE','unconfigured; no monetary claim'),
                   price_date=os.getenv('PRICE_DATE',''))
