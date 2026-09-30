"""Run retrieval -> provider -> validation and persist inspectable comparisons."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from .data import ROOT
from .llm import create_provider, ProviderError, PROMPT_VERSION
from .profiles import BASIC, WVS
from .retrieval import retrieve_candidates
from .validation import validate_llm_output
from .payload import build_llm_payload


def run_mode(items, request, wvs, mode, settings, provider=None):
    started = perf_counter()
    retrieval = retrieve_candidates(items, request, wvs, mode, settings)
    payload, request_size = build_llm_payload(retrieval, settings.max_llm_activities_per_city)
    run = {'mode': mode, 'retrieval': retrieval, 'status': 'retrieval_only',
           'llm': None, 'validation': None, 'provider': settings.provider_name, 'model': settings.model or None,
           'prompt_version': PROMPT_VERSION, 'message': '', 'llm_latency_seconds': None}
    run['llm_candidate_package'] = payload
    run['request_size'] = request_size
    if not retrieval['candidate_package']['candidate_cities']:
        run['status'] = 'no_candidates'
        run['message'] = 'No viable candidate cities; no LLM request made.'
    elif provider is None and not settings.llm_available:
        run['message'] = settings.unavailable_reason + ' No LLM destination or itinerary was generated.'
    else:
        provider = provider or create_provider(settings)
        called_at = perf_counter()
        try:
            answer = provider.generate(deepcopy(payload))
            run['llm'] = answer
            run['provider'], run['model'] = answer['provider'], answer['model']
            run['validation'] = validate_llm_output(answer['output'], {'candidate_package': payload}, request, items)
            run['status'] = 'validated' if run['validation']['valid'] else 'validation_failed'
            run['message'] = 'Real LLM output.' if not answer['is_mock'] else 'TEST MOCK — not real LLM output.'
            timing_codes = {'opening_hours', 'overlap_or_transfer', 'invalid_start_time'}
            codes = {v['code'] for v in run['validation']['constraint_violations']}
            if codes and codes <= timing_codes:
                run['message'] = 'Timing validation failed. The itinerary is rejected; no automatic repair or retry was attempted.'
        except ProviderError as exc:
            run['status'] = 'provider_error'
            run['message'] = str(exc)
            run['error_diagnostics'] = exc.diagnostics
        finally:
            run['llm_latency_seconds'] = perf_counter() - called_at
    run['total_latency_seconds'] = perf_counter() - started
    return run


def overlap(left, right):
    a, b = set(left), set(right)
    return {'intersection': sorted(a & b), 'union_count': len(a | b),
            'jaccard': len(a & b) / len(a | b) if a | b else None,
            'only_basic': sorted(a - b), 'only_wvs': sorted(b - a)}


def run_summary(run):
    package = run['retrieval']['candidate_package']
    answer = run['llm']['output'] if run['llm'] and isinstance(run['llm']['output'], dict) else {}
    validation = run['validation']
    stops = validation['validated_itinerary'] if validation else []
    return {'mode': run['mode'], 'candidate_cities': [c['city'] for c in package['candidate_cities']],
            'candidate_item_ids': [a['ItemId'] for c in package['candidate_cities'] for a in c['candidate_activities']],
            'llm_selected_destination': answer.get('selected_destination'),
            'selected_item_ids': validation['selected_item_ids'] if validation else None,
            'invalid_item_ids': validation['invalid_item_ids'] if validation else None,
            'duplicates': validation['duplicate_item_ids'] if validation else None,
            'constraint_violations': validation['constraint_violations'] if validation else None,
            'valid': validation['valid'] if validation else None,
            'characteristics': {'category_counts': dict(Counter(i['category'] for i in stops)),
                                'environment_counts': dict(Counter(i['environment'] for i in stops)),
                                'total_group_cost': validation['total_group_cost'] if validation and validation['valid'] else None,
                                'scheduled_minutes': sum(i['DurationMinutes'] for i in stops) if stops else None},
            'latency_seconds': run['total_latency_seconds'],
            'llm_latency_seconds': run['llm_latency_seconds'], 'provider': run['provider'], 'model': run['model']}


def compare_runs(basic, wvs):
    a, b = run_summary(basic), run_summary(wvs)
    both_outputs = basic['llm'] is not None and wvs['llm'] is not None
    both_valid = a['valid'] is True and b['valid'] is True
    return {'basic': a, 'wvs': b,
            'candidate_city_overlap': overlap(a['candidate_cities'], b['candidate_cities']),
            'candidate_set_overlap': overlap(a['candidate_item_ids'], b['candidate_item_ids']),
            'itinerary_overlap': overlap(a['selected_item_ids'], b['selected_item_ids']) if both_outputs else None,
            'destination_changed': a['llm_selected_destination'] != b['llm_selected_destination'] if both_outputs else None,
            'both_itineraries_valid': both_valid,
            'interpretation': 'Observed differences only; no evidence that either mode is better.',
            'llm_comparison_status': 'Both outputs available; inspect validation before interpreting.' if both_outputs else
                                     'Candidate comparison only. LLM output comparison requires two successful API executions.'}


def run_comparison(items, request, wvs, settings, provider=None):
    # Exactly the same immutable factual request and settings in both arms.
    basic = run_mode(items, request, wvs, BASIC, settings, provider)
    prior = run_mode(items, request, wvs, WVS, settings, provider)
    return {'kind': 'comparison', 'runs': [basic, prior], 'comparison': compare_runs(basic, prior)}


def save_experiment(record, directory=ROOT / 'outputs/experiments'):
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    experiment_id = uuid4().hex
    result = {'experiment_id': experiment_id, 'created_at': datetime.now(timezone.utc).isoformat(), **record}
    path = target / f'{experiment_id}.json'
    # Only results, facts and candidate packages enter this record; Settings and keys never do.
    with path.open('x', encoding='utf-8') as f:
        json.dump(result, f, default=str, ensure_ascii=False, indent=2, allow_nan=False)
    return path
