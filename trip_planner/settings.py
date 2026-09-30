"""Read local configuration without exposing credentials or mutating .env."""
from dataclasses import dataclass, field
import os

from dotenv import dotenv_values
from .data import ROOT


@dataclass(frozen=True)
class Settings:
    api_key: str = field(default='', repr=False)
    model: str = ''
    top_city_candidates: int = 4
    activities_per_city: int = 8
    timeout_seconds: float = 90
    max_output_tokens: int = 6000
    wvs_scoring_method: str = 'normalized_relative'
    provider: str = 'openai'
    max_llm_activities_per_city: int = 5

    def __post_init__(self):
        if type(self.max_llm_activities_per_city) is not int or not 1 <= self.max_llm_activities_per_city <= 20:
            raise ValueError('MAX_LLM_ACTIVITIES_PER_CITY must be from 1 to 20.')
        if self.provider not in ('openai', 'groq'):
            raise ValueError('Unsupported LLM_PROVIDER. Use openai or groq.')
        if self.wvs_scoring_method not in ('raw_affinity', 'normalized_relative'):
            raise ValueError('WVS_SCORING_METHOD must be raw_affinity or normalized_relative.')

    @property
    def llm_available(self):
        return bool(self.api_key.strip() and self.model.strip())

    @property
    def provider_name(self):
        return {'openai': 'OpenAI', 'groq': 'Groq'}[self.provider]

    @property
    def unavailable_reason(self):
        prefix = self.provider.upper()
        missing = [name for name, value in [(prefix + '_API_KEY', self.api_key), (prefix + '_MODEL', self.model)] if not value.strip()]
        return 'Missing ' + ', '.join(missing) + '. Candidate retrieval remains available.' if missing else ''


def load_settings(env_path=ROOT / '.env', environ=None):
    values = {**dotenv_values(env_path, encoding='utf-8-sig'), **(os.environ if environ is None else environ)}
    def integer(name, default, low, high):
        try:
            value = int(values.get(name, default))
        except (TypeError, ValueError):
            raise ValueError(f'{name} must be an integer from {low} to {high}.') from None
        if not low <= value <= high:
            raise ValueError(f'{name} must be from {low} to {high}.')
        return value
    provider = (values.get('LLM_PROVIDER') or 'openai').strip().lower()
    if provider not in ('openai', 'groq'):
        raise ValueError('Unsupported LLM_PROVIDER. Use openai or groq.')
    prefix = provider.upper()
    return Settings(provider=provider, api_key=values.get(prefix + '_API_KEY') or '', model=values.get(prefix + '_MODEL') or '',
                    wvs_scoring_method=values.get('WVS_SCORING_METHOD', 'normalized_relative'),
                    top_city_candidates=integer('TOP_CITY_CANDIDATES', 4, 1, 5),
                    activities_per_city=integer('ACTIVITIES_PER_CITY', 8, 1, 20),
                    max_llm_activities_per_city=integer('MAX_LLM_ACTIVITIES_PER_CITY', 5, 1, 20),
                    timeout_seconds=integer('OPENAI_TIMEOUT_SECONDS', 90, 10, 180),
                    max_output_tokens=integer('OPENAI_MAX_OUTPUT_TOKENS', 6000, 1024, 16000))
