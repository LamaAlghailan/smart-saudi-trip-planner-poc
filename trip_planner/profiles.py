"""Transparent WVS inference and mode-specific preference resolution."""
from collections import Counter, defaultdict
from copy import deepcopy
from statistics import mean
import re

from .data import CATEGORY_ALIASES, number

BASIC = 'Basic / No WVS'
WVS = 'WVS Cold-Start'

# POC semantic crosswalk, not a learned relationship or a source WVS mapping.
HOBBY_BY_CATEGORY = {
    'adventure': ('Hiking',),
    'beach': ('Beach & Water Activities',),
    'waterfront': ('Beach & Water Activities',),
    'marina': ('Beach & Water Activities',),
    'nature': ('Enjoying Nature', 'National Parks'),
    'cultural': ('Museums & Exhibitions', 'Guided Heritage Tours'),
    'art': ('Museums & Exhibitions',),
    'entertainment': ('Festivals & Theme Parks',),
    'shopping': ('Shopping & Malls',),
    'food': ('Luxury Dining',),
    'food & entertainment': ('Luxury Dining', 'Festivals & Theme Parks'),
}

# Candidate retrieval weights only. WVS adds a bounded 10% weak prior.
BASIC_WEIGHTS = {'group': .625, 'quality': .375}
WVS_WEIGHTS = {'quality': .90,
               'category': .05, 'hobby': .025, 'environment': .025}


def normalize_category(label):
    key = label.strip().casefold()
    return CATEGORY_ALIASES.get(key, key)


def evidence_error(row):
    """Honor supplied eligibility; never manufacture a rank for an excluded group."""
    if str(row.get('Eligible for Ranking', '')).casefold() != 'true':
        return 'Not eligible for ranking in source workbook'
    checks = {'WVS-Derived Signal (%)': (0, 100), 'Global Baseline (%)': (0, 100),
              'Relative vs Global (pp)': (-100, 100), 'Question Coverage (%)': (0, 100)}
    for field, (low, high) in checks.items():
        value = number(row.get(field))
        if value is None or not low <= value <= high:
            return f'Missing or invalid {field}'
    if number(row['Question Coverage (%)']) == 0:
        return 'Zero question coverage'
    for field in ('Raw N', 'Effective N', 'Country Rank'):
        value = number(row.get(field))
        if value is None or value <= 0:
            return f'Missing or invalid {field}'
    if abs(float(row['WVS-Derived Signal (%)']) - float(row['Global Baseline (%)'])
           - float(row['Relative vs Global (pp)'])) > .01:
        return 'Signal minus baseline does not match relative signal'
    return ''


def infer_profile(wvs, birth_country, mode):
    profile = {'birth_country': birth_country, 'hobbies': {}, 'categories': {},
               'environments': {}, 'evidence': [], 'warnings': [], 'eligible_rows': 0}
    if mode == BASIC:
        return profile
    for sheet, label, domain in [('HOBBY_RESULTS', 'Hobby', 'hobbies'),
                                  ('CATEGORY_RESULTS', 'Category', 'categories'),
                                  ('ENVIRONMENT_RESULTS', 'Environment', 'environments')]:
        rows = [r for r in wvs.get(sheet, []) if r.get('Birth Country') == birth_country]
        counts = Counter(r.get(label) for r in rows)
        grouped = defaultdict(list)
        for row in rows:
            reason = evidence_error(row)
            if not row.get(label) or counts[row.get(label)] != 1:
                reason = 'Missing or duplicate dimension label'
            affinity = None
            if not reason:
                # Relative-to-global evidence is a weak prior; preserve neutral
                # fallback and shrink low-coverage evidence rather than amplify it.
                delta = float(row['Relative vs Global (pp)']) / 100
                coverage = float(row['Question Coverage (%)']) / 100
                affinity = .5 + coverage * max(-.5, min(.5, delta))
                key = normalize_category(row[label]) if domain == 'categories' else row[label]
                grouped[key].append(affinity)
                profile['eligible_rows'] += 1
            profile['evidence'].append({'sheet': sheet, **row, 'used': not bool(reason),
                                        'affinity': affinity, 'exclusion_reason': reason})
        profile[domain] = {key: mean(values) for key, values in sorted(grouped.items())}
        if not grouped:
            profile['warnings'].append(f'No eligible {domain} evidence for {birth_country}; using neutral affinity 0.5.')
    return profile


def normalized_relative_profile(profile):
    """Experimental separation transform, not validated tourism behavior."""
    result = deepcopy(profile)
    diagnostics = {}
    for sheet, label, domain in [('HOBBY_RESULTS', 'Hobby', 'hobbies'),
                                ('CATEGORY_RESULTS', 'Category', 'categories'),
                                ('ENVIRONMENT_RESULTS', 'Environment', 'environments')]:
        rows = [r for r in result['evidence'] if r['sheet'] == sheet and r['used']]
        center = mean(float(r['Relative vs Global (pp)']) for r in rows) if rows else 0
        scale = max((abs(float(r['Relative vs Global (pp)']) - center) for r in rows), default=0)
        grouped = defaultdict(list)
        for row in rows:
            signal = (float(row['Relative vs Global (pp)']) - center) / scale if scale else 0
            row['raw_affinity'] = row['affinity']
            row['normalized_distinctiveness'] = signal
            row['affinity'] = .5 + .5 * signal * float(row['Question Coverage (%)']) / 100
            key = normalize_category(row[label]) if domain == 'categories' else row[label]
            grouped[key].append(row['affinity'])
        result[domain] = {key: mean(values) for key, values in grouped.items()}
        diagnostics[domain] = {'mean_relative_pp': center, 'max_absolute_centered_pp': scale}
    result['normalization'] = diagnostics
    return result


def semantic_mapping(item):
    """Ordered, word-boundary rules; broad labels alone never imply an activity."""
    category = item['category']
    text = ' '.join(str(item.get(k, '')) for k in ('ItemName', 'ItemDescription')).casefold()
    def has(pattern):
        return re.search(r'\b(?:' + pattern + r')\b', text) is not None
    def result(categories, hobbies, rule, status='derived'):
        return {'normalized_category': category, 'category_priors': categories,
                'hobby_priors': hobbies, 'environment_prior': item['environment'],
                'rule': rule, 'status': status}
    broad = category in ('urban', 'family', 'leisure', 'adventure', 'nature', 'food & entertainment')
    if category in ('beach', 'waterfront', 'marina') or (broad and has(r'snorkel\w*|diving|scuba|boat\w*|islands?|waterfront|marine|beach\w*|water sports')):
        return result(['beach'], ['Beach & Water Activities'], 'water destination or explicit water activity')
    if broad and has(r'hiking|hikes?|trails?|trek\w*'):
        return result(['adventure'], ['Hiking'], 'explicit hiking/trail/trek metadata')
    if category in ('urban', 'family', 'leisure') and has(r'malls?|shopping|retailers?'):
        return result(['shopping'], ['Shopping & Malls'], 'explicit mall/shopping/retail metadata')
    if broad:
        food = has(r'dining|restaurants?|food|dishes|flavors|cafes?')
        entertainment = has(r'theme park|amusement|play areas?|festivals?|cinema|zipline')
        if food or entertainment:
            categories = (['food'] if food else []) + (['entertainment'] if entertainment else [])
            hobbies = (['Luxury Dining'] if food else []) + (['Festivals & Theme Parks'] if entertainment else [])
            return result(categories, hobbies, 'explicit food/entertainment metadata; average matched domains')
        if has(r'parks?|picnic|forests?|greenery|green spaces|mountains?|viewpoints?|landscapes?|canyon|desert|dunes|camping'):
            return result(['nature'], ['Enjoying Nature', 'National Parks'], 'explicit nature/scenery metadata; no assumed hiking')
        if category != 'nature':
            return result([], [], 'insufficient metadata for broad category; neutral', 'missing')
    if category == 'cultural' and has(r'museums?|exhibitions?'):
        return result(['cultural'], ['Museums & Exhibitions'], 'museum/exhibition metadata within cultural category')
    if category == 'cultural' and has(r'heritage|historical|archaeological|castle'):
        return result(['cultural'], ['Guided Heritage Tours'], 'heritage metadata within cultural category')
    if category in ('cultural', 'nature', 'entertainment', 'shopping', 'food'):
        return result([category], list(HOBBY_BY_CATEGORY[category]), 'normalized category crosswalk', 'exact')
    if category == 'art':
        return result(['cultural'], ['Museums & Exhibitions'], 'art to cultural/exhibitions')
    return result([], [], 'unmapped category; neutral', 'missing')


def mapping_debug(item, profile):
    mapping = semantic_mapping(item)
    category = {k: profile['categories'].get(k, .5) for k in mapping['category_priors']}
    hobby = {k: profile['hobbies'].get(k, .5) for k in mapping['hobby_priors']}
    environment = profile['environments'].get(mapping['environment_prior'], .5)
    return {**mapping, 'matched_category_affinities': category, 'matched_hobby_affinities': hobby,
            'matched_environment_affinity': environment,
            'components': {'category': mean(category.values()) if category else .5,
                           'hobby': mean(hobby.values()) if hobby else .5, 'environment': environment}}


def preference_components(item, profile):
    return mapping_debug(item, profile)['components']


def resolve_profile(profile, mode):
    """Weights rank retrieval relevance; they never select a final destination."""
    return {'mode': mode, 'weights': dict(BASIC_WEIGHTS if mode == BASIC else WVS_WEIGHTS),
            'wvs_profile': profile if mode == WVS else None}
