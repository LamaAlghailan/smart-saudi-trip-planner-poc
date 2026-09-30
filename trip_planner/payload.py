"""Compact provider transport only; full retrieval remains available internally."""
from copy import deepcopy
import json
import math
from .llm import SYSTEM_PROMPT, response_schema
from .scheduling import scheduling_windows

ACTIVITY_FIELDS = ('ItemId', 'ItemName', 'City', 'Category', 'Environment', 'GroupCost',
                   'DurationMinutes', 'available_from', 'available_until', 'opens', 'closes',
                   'retrieval_score', 'Suitability', 'MinAge', 'MaxAge')


def build_llm_payload(retrieval, limit=5):
    full = retrieval['candidate_package']
    if full['trip_days'] > limit:
        raise ValueError('MAX_LLM_ACTIVITIES_PER_CITY must be at least trip_days to retain distinct daily visits.')
    package = {k: deepcopy(full[k]) for k in ('mode', 'tourist_facts', 'trip_start', 'trip_end', 'trip_days', 'planning_constraints')}
    package['candidate_cities'] = []
    anchors = {c['city']: set(c['daily_anchor_ids'].values()) for c in retrieval['city_rankings']}
    for city in full['candidate_cities']:
        keep = set(anchors[city['city']])
        for activity in city['candidate_activities']:
            if len(keep) >= limit:
                break
            keep.add(activity['ItemId'])
        package['candidate_cities'].append({'city': city['city'], 'candidate_activities': [
            {k: a[k] for k in ACTIVITY_FIELDS} for a in city['candidate_activities'] if a['ItemId'] in keep]})
    if 'wvs_prior' in full:
        # Only resolved eligible affinities, no source tables or debugging records.
        profile = full['wvs_prior']
        package['wvs_prior'] = {'used': True, **{k: profile[k] for k in ('hobbies','categories','environments')}}
    for city in package['candidate_cities']:
        for activity in city['candidate_activities']:
            activity['scheduling_windows'] = scheduling_windows(activity, package)
    encoded = json.dumps(package, ensure_ascii=False, separators=(',', ':'))
    request_text = SYSTEM_PROMPT + encoded + json.dumps(response_schema(package), separators=(',', ':'))
    stats = {'candidate_cities': len(package['candidate_cities']),
             'activities_sent': sum(len(c['candidate_activities']) for c in package['candidate_cities']),
             'payload_bytes': len(encoded.encode('utf-8')),
             'estimated_input_tokens': math.ceil(len(request_text)/4),
             'token_estimate_method': 'Approximate characters/4 including prompt and schema; not provider tokenizer or TPM accounting.'}
    return package, stats
