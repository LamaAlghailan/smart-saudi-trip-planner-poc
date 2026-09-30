"""Bounded, grounded candidate packages. No final city or itinerary selection."""
from dataclasses import asdict
import json
from time import perf_counter

from .engine import (DAY_END, DAY_START, STOPS_PER_DAY, TRANSFER_MINUTES, clock_string,
                     rank_candidate_activities, rank_candidate_cities, suitability, filter_by_trip_dates, unique_inventory)
from .profiles import BASIC, WVS, infer_profile, resolve_profile, normalized_relative_profile
from .settings import Settings


def compact_activity(item):
    return {'ItemId': item['ItemId'], 'ItemName': item['ItemName'], 'City': item['CityName'],
            'Description': item.get('ItemDescription', '')[:240],
            'Category': item['category'], 'Environment': item['environment'],
            'Price': item['Price'], 'GroupCost': item['group_cost'],
            'DurationMinutes': item['DurationMinutes'], 'Rating': item['AvgRating'],
            'Popularity': item['PopularityScore'],
            'Suitability': {key: suitability(item.get(key)) for key in
                            ('SuitableForAdults', 'SuitableForChildren', 'SuitableForInfants')},
            'MinAge': item['MinAge'], 'MaxAge': item['MaxAge'],
            'available_from': item['available_from'].isoformat(),
            'available_until': item['available_until'].isoformat(),
            'availability_policy': item.get('availability_policy', 'source_interval'),
            'mapping_debug': item.get('mapping_debug'),
            'opens': clock_string(item['opens']), 'closes': clock_string(item['closes']),
            'retrieval_score': round(item['retrieval_score'], 4),
            'retrieval_components': {k: round(v, 4) for k, v in item['components'].items()}}


def retrieve_candidates(items, request, wvs, mode=BASIC, settings=None):
    started = perf_counter()
    request.validate()
    if mode not in (BASIC, WVS):
        raise ValueError('Choose Basic / No WVS or WVS Cold-Start.')
    settings = settings or Settings()
    if not 1 <= settings.top_city_candidates <= 5 or not 1 <= settings.activities_per_city <= 20:
        raise ValueError('Candidate limits must be 1–5 cities and 1–20 activities per city.')
    active = [i for i in unique_inventory(items) if i['IsActive']]
    available = filter_by_trip_dates(active, request.start_date, request.end_date)
    profile = infer_profile(wvs, request.birth_country, mode)
    if mode == WVS and settings.wvs_scoring_method == 'normalized_relative':
        profile = normalized_relative_profile(profile)
    resolved = resolve_profile(profile, mode)
    rankings, pools = rank_candidate_cities(available, request, resolved)
    city_packages = []
    # Preserve the feasibility witness in a limited package. This ensures trimming
    # does not remove the only cheap/date-valid activity supporting a trip day.
    activity_limit = max(settings.activities_per_city, request.days)
    for city in rankings[:settings.top_city_candidates]:
        ranked = rank_candidate_activities(pools[city['city']], request, resolved)
        retained_ids = set(city['daily_anchor_ids'].values())
        for item in ranked:
            if len(retained_ids) >= activity_limit:
                break
            retained_ids.add(item['ItemId'])
        activities = [compact_activity(i) for i in ranked if i['ItemId'] in retained_ids]
        city_packages.append({'city': city['city'], 'retrieval_score': round(city['retrieval_score'], 4),
                              'city_profile': {k: city[k] for k in ('category_distribution',
                                  'environment_distribution', 'budget_distribution',
                                  'group_compatible_fraction', 'components', 'contributions')},
                              'candidate_activities': activities})
    facts = asdict(request)
    facts['start_date'] = request.start_date.isoformat()
    facts['end_date'] = request.end_date.isoformat()
    facts['trip_days'] = request.days
    package = {'package_version': 'llm-candidates-v2', 'mode': mode, 'tourist_facts': facts,
               'scoring': {'method': settings.wvs_scoring_method if mode == WVS else 'basic',
                           'wvs_weight': .10 if mode == WVS else 0,
                           'experimental': mode == WVS and settings.wvs_scoring_method == 'normalized_relative'},
               'trip_start': facts['start_date'], 'trip_end': facts['end_date'], 'trip_days': request.days,
               'planning_constraints': {'day_start': clock_string(DAY_START), 'day_end': clock_string(DAY_END),
                   'max_activities_per_day': STOPS_PER_DAY, 'transfer_minutes': TRANSFER_MINUTES,
                   'pricing': 'SAR per traveler; GroupCost = Price * (adults + children); no child discount',
                   'availability': 'Inclusive normalized intervals; unknown availability excluded. Year-round validated records use 0001-01-01 through 9999-12-31.',
                   'unknown_ages': 'Age bounds not supplied must not be invented.'},
               'retrieval_weights': resolved['weights'], 'candidate_cities': city_packages}
    if mode == WVS:
        package['wvs_prior'] = profile
    warnings = list(profile['warnings']) if mode == WVS else []
    if mode == WVS and settings.wvs_scoring_method == 'normalized_relative':
        warnings.append('Experimental normalized WVS weak prior: Relative-vs-Global is transformed only to improve retrieval separation. Not validated against real tourism behavior.')
    if len(city_packages) < settings.top_city_candidates:
        warnings.append(f'Only {len(city_packages)} viable cities are available; no extra city is invented to meet the configured limit.')
    if not city_packages:
        warnings.append('No city can provide a distinct affordable visit for every requested day. The LLM will not be called.')
    if request.youngest_age is None or request.oldest_age is None:
        warnings.append('One or both ages are unspecified; exact age-bound validation is incomplete.')
    return {'mode': mode, 'candidate_package': package, 'city_rankings': rankings,
            'wvs_profile': profile if mode == WVS else None, 'warnings': warnings,
            'stats': {'validated_count': len(items), 'validated_active_count': sum(i['IsActive'] for i in items),
                      'before_date_filter': len(active),
                      'after_date_filter': len(available), 'excluded_by_dates': len(active) - len(available),
                      'city_count': len(city_packages),
                      'activity_count': sum(len(c['candidate_activities']) for c in city_packages),
                      'effective_activity_limit': activity_limit,
                      'package_bytes': len(json.dumps(package, ensure_ascii=False).encode('utf-8'))},
            'retrieval_latency_seconds': perf_counter() - started}
