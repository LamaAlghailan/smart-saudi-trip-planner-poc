"""Offline calibration only. Does not read .env or mutate production weights."""
from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict
from datetime import date
import hashlib
import json
from statistics import mean

from trip_planner.data import ROOT, load_tourism, load_wvs
from trip_planner.engine import (TripRequest, unique_inventory, filter_by_trip_dates,
    rank_candidate_cities, rank_candidate_activities)
from trip_planner.profiles import WVS, infer_profile, normalize_category
from trip_planner.retrieval import compact_activity

LEVELS = (0, 10, 20, 30, 40, 50)
COUNTRIES = ('India', 'Canada')


def normalized_profile(profile):
    result = deepcopy(profile)
    diagnostics = {}
    for sheet, label, domain in [('HOBBY_RESULTS', 'Hobby', 'hobbies'),
                                ('CATEGORY_RESULTS', 'Category', 'categories'),
                                ('ENVIRONMENT_RESULTS', 'Environment', 'environments')]:
        rows = [r for r in result['evidence'] if r['sheet'] == sheet and r['used']]
        center = mean(float(r['Relative vs Global (pp)']) for r in rows) if rows else 0
        scale = max((abs(float(r['Relative vs Global (pp)']) - center) for r in rows), default=0)
        grouped = defaultdict(list)
        for r in rows:
            signal = (float(r['Relative vs Global (pp)']) - center) / scale if scale else 0
            affinity = .5 + .5 * signal * float(r['Question Coverage (%)']) / 100
            r['affinity'] = affinity
            r['normalized_distinctiveness'] = signal
            key = normalize_category(r[label]) if domain == 'categories' else r[label]
            grouped[key].append(affinity)
        result[domain] = {k: mean(v) for k, v in grouped.items()}
        diagnostics[domain] = {'mean_relative_pp': center, 'max_absolute_centered_pp': scale}
    result['normalization'] = diagnostics
    return result


def overlap(a, b):
    return {'intersection': len(a & b), 'union': len(a | b),
            'jaccard': len(a & b) / len(a | b) if a | b else 1,
            'only_first': sorted(a-b), 'only_second': sorted(b-a)}


def city_set(run):
    return {c['city'] for c in run['shortlist']}


def activities(run):
    return {a['ItemId'] for c in run['shortlist'] for a in c['activities']}


def run_configuration(items, request, profile, level):
    w = level / 100
    weights = {'quality': 1-w, 'category': w/2, 'hobby': w/4, 'environment': w/4}
    # No group or budget component enters weighted_score, even though the reused
    # factual engine retains them for constraints and diagnostic city profiles.
    resolved = {'weights': weights, 'wvs_profile': profile if level else None}
    if not level:
        resolved['weights'] = {'quality': 1.0}
    rankings, pools = rank_candidate_cities(items, request, resolved)
    shortlist = []
    for city in rankings[:4]:
        ranked = rank_candidate_activities(pools[city['city']], request, resolved)
        keep = set(city['daily_anchor_ids'].values())
        for item in ranked:
            if len(keep) >= max(8, request.days):
                break
            keep.add(item['ItemId'])
        chosen = [dict(compact_activity(i), full_pool_rank=n) for n, i in enumerate(ranked, 1) if i['ItemId'] in keep]
        shortlist.append({'city': city['city'], 'activities': chosen})
    return {'wvs_percent': level, 'weights': resolved['weights'], 'city_rankings': rankings,
            'top10': [c['city'] for c in rankings[:10]], 'shortlist': shortlist,
            'eligible_pool_ids': {c: sorted(i['ItemId'] for i in pool) for c, pool in pools.items()},
            'margins': {f'{a}-{b}': rankings[a-1]['retrieval_score']-rankings[b-1]['retrieval_score']
                        for a,b in [(3,4),(4,5),(5,6),(3,6)]}}


def main():
    production = [ROOT/'trip_planner'/f for f in ('profiles.py','engine.py','retrieval.py','settings.py')]
    hashes = lambda: {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in production}
    before = hashes()
    items, audit = load_tourism()
    wvs = load_wvs()
    request = TripRequest('India', date(2026,10,15), date(2026,10,17), budget=1000, adults=2)
    active = [i for i in unique_inventory(items) if i['IsActive']]
    available = filter_by_trip_dates(active, request.start_date, request.end_date)
    profiles = {c: infer_profile(wvs,c,WVS) for c in COUNTRIES}
    baseline = run_configuration(available,request,profiles['India'],0)
    base_ranks = {c['city']: c['rank'] for c in baseline['city_rankings']}
    results = {}
    for experiment in ('raw_affinity', 'centered_relative_distinctiveness'):
        runs = []
        for level in LEVELS:
            pair = {}
            for country in COUNTRIES:
                profile = profiles[country] if experiment == 'raw_affinity' else normalized_profile(profiles[country])
                run = run_configuration(available,request,profile,level)
                assert run['eligible_pool_ids'] == baseline['eligible_pool_ids']
                run['country'] = country
                run['profile'] = profile
                run['city_overlap_vs_basic'] = overlap(city_set(baseline),city_set(run))
                run['activity_overlap_vs_basic'] = overlap(activities(baseline),activities(run))
                run['city_rank_changes'] = {c['city']: {'basic':base_ranks[c['city']], 'current':c['rank'],
                    'positions_gained':base_ranks[c['city']]-c['rank']} for c in run['city_rankings']}
                run['shortlist_mean_source_quality'] = mean(c['components']['quality'] for c in run['city_rankings'][:4])
                pair[country] = run
            runs.append({'wvs_percent':level,'countries':pair,
                         'country_city_overlap':overlap(city_set(pair['India']),city_set(pair['Canada'])),
                         'country_activity_overlap':overlap(activities(pair['India']),activities(pair['Canada']))})
        results[experiment] = {'levels':runs,
            'first_shortlist_change_vs_basic':{c:next((r['wvs_percent'] for r in runs if city_set(r['countries'][c]) != city_set(baseline)),None) for c in COUNTRIES},
            'first_country_shortlist_difference':next((r['wvs_percent'] for r in runs if r['country_city_overlap']['jaccard']<1),None)}
    report = {'facts':asdict(request), 'levels':LEVELS,
        'baseline_definition':'Offline quality-only baseline, NOT production Basic. Quality = 0.6 popularity + 0.4 rating/5. Production group ranking weights untouched.',
        'normalization':'Within each country and source domain: center eligible Relative-vs-Global pp by domain mean; divide by maximum absolute centered value; affinity=0.5+0.5*normalized_signal*coverage/100. Zero spread -> neutral. Normalize before category alias averaging and item semantic mapping. Eligibility gates unchanged.',
        'normalization_caveat':'Amplifies within-country contrasts and discards absolute distance from global. Negative global deltas may become above-neutral relative preferences. Country-domain max scaling is outlier-sensitive; especially fragile with only three environments. Exploratory, not calibrated confidence.',
        'filter_counts':{'source':len(audit),'validated':len(items),'distinct_active':len(active),'date_available':len(available),
                         'feasible_cities':len(baseline['city_rankings'])},
        'eligibility_identical_all_runs':True,'results':results,
        'production_hashes_before':before,'production_hashes_after':hashes()}
    assert before == hashes()
    path = ROOT/'outputs/wvs_sensitivity_audit.json'
    path.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    lines = ['# Offline WVS sensitivity audit', report['baseline_definition'], '', report['normalization'], '', report['normalization_caveat']]
    for experiment, result in results.items():
        lines.extend(['', '## '+experiment, str({k:v for k,v in result.items() if k!='levels'})])
        print(experiment, {k:v for k,v in result.items() if k!='levels'})
        for row in result['levels']:
            lines.extend(['', f"### WVS {row['wvs_percent']}%", 'Country overlap: '+json.dumps({k:v for k,v in row.items() if k not in ('countries','wvs_percent')})])
            for country, run in row['countries'].items():
                lines.extend(['', '**'+country+'**', 'Top 10: '+ ' > '.join(run['top10']),
                    'Top 4: '+', '.join(c['city'] for c in run['shortlist']),
                    'Overlaps vs Basic: '+json.dumps({'city':run['city_overlap_vs_basic'],'activity':run['activity_overlap_vs_basic']}),
                    'Rank changes: '+json.dumps(run['city_rank_changes']), 'Margins: '+json.dumps(run['margins'])])
                for c in run['shortlist']:
                    lines.append(c['city']+': '+'; '.join(f"{a['ItemName']} [{a['ItemId']}] ({a['retrieval_score']})" for a in c['activities']))
                print(row['wvs_percent'],country,'TOP10',run['top10'],'ACT',run['activity_overlap_vs_basic']['jaccard'],'MARGINS',run['margins'],'Q',run['shortlist_mean_source_quality'])
            print('COUNTRY_OVERLAP',row['country_city_overlap'],row['country_activity_overlap'])
    (ROOT/'outputs/wvs_sensitivity_audit.md').write_text('\n\n'.join(lines),encoding='utf-8')


if __name__ == '__main__':
    main()
