"""Offline semantic mapping audit; never loads credentials or calls a provider."""
from collections import Counter
from datetime import date
from dataclasses import replace
import json
from statistics import mean
from unittest.mock import patch

from trip_planner.data import ROOT, load_tourism, load_wvs
from trip_planner.engine import TripRequest, unique_inventory, filter_by_trip_dates, group_compatible, group_cost, slot, DAY_START
from trip_planner.profiles import BASIC, WVS, HOBBY_BY_CATEGORY, semantic_mapping
from trip_planner.retrieval import retrieve_candidates


def main():
    items, _ = load_tourism()
    wvs = load_wvs()
    request = TripRequest('India', date(2026, 10, 15), date(2026, 10, 17), budget=1000, adults=2)
    eligible = [i for i in filter_by_trip_dates(unique_inventory(items), request.start_date, request.end_date)
                if i['IsActive'] and slot(i, DAY_START) and group_compatible(i, request) and group_cost(i, request) <= request.budget]
    def legacy(item, profile):
        category = item['category']
        hobbies = HOBBY_BY_CATEGORY.get(category, ())
        return {'category': profile['categories'].get(category, .5),
                'hobby': mean(profile['hobbies'].get(h, .5) for h in hobbies) if hobbies else .5,
                'environment': profile['environments'].get(item['environment'], .5)}
    runs, before = {}, {}
    for name, mode, country in [('Basic', BASIC, 'India'), ('India WVS', WVS, 'India'), ('Canada WVS', WVS, 'Canada')]:
        req = replace(request, birth_country=country)
        runs[name] = retrieve_candidates(items, req, wvs, mode)
        with patch('trip_planner.engine.preference_components', side_effect=legacy):
            before[name] = retrieve_candidates(items, req, wvs, mode)
    def ids(run):
        return {a['ItemId'] for c in run['candidate_package']['candidate_cities'] for a in c['candidate_activities']}
    def overlap(a, b):
        x, y = ids(a), ids(b)
        return {'intersection': len(x & y), 'union': len(x | y), 'jaccard': len(x & y) / len(x | y),
                'only_first': sorted(x-y), 'only_second': sorted(y-x)}
    report = {'scope': '159 date/hour/group/budget eligible records, before city feasibility and shortlist',
              'category_counts': dict(Counter(i['category'] for i in eligible)),
              'eligible_item_mappings': [{'ItemId': i['ItemId'], 'ItemName': i['ItemName'], **semantic_mapping(i)} for i in eligible],
              'runs': runs,
              'overlap': {'Basic vs India': overlap(runs['Basic'], runs['India WVS']),
                          'India vs Canada': overlap(runs['India WVS'], runs['Canada WVS'])},
              'before_after_overlap': {k: overlap(before[k], runs[k]) for k in runs}}
    (ROOT / 'outputs/mapping_audit.json').write_text(json.dumps(report, indent=2, default=str), encoding='utf-8')
    print('COUNTS', report['category_counts'])
    for name, run in runs.items():
        print(name)
        for c in run['city_rankings'][:10]:
            contribution = {k:v for k,v in c['contributions'].items() if k in ('category','hobby','environment')}
            print(c['rank'], c['city'], round(c['retrieval_score'], 9), contribution)
        print('CANDIDATES', [(c['city'], [a['ItemId'] for a in c['candidate_activities']]) for c in run['candidate_package']['candidate_cities']])
    print('OVERLAP', report['overlap'])
    print('BEFORE_AFTER', report['before_after_overlap'])


if __name__ == '__main__':
    main()
