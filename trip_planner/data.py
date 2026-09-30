"""Read sources without mutation; normalize labels and quarantine unsafe rows."""
from collections import Counter
from datetime import date, datetime
import csv
import math
from pathlib import Path

from scripts.inspect_sources import read_workbook

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / 'data/raw/items.csv'
WVS_PATH = ROOT / 'data/raw/WVS_Phase2_BirthCountry_Pattern_Results.xlsx'

# Explicit, reviewable label aliases. Broad labels are not forced into WVS classes.
CATEGORY_ALIASES = {
    'culture': 'cultural', 'museum': 'cultural', 'historical': 'cultural',
    'historical landmark': 'cultural', 'historical district': 'cultural',
    'historic district': 'cultural', 'historical area': 'cultural',
    'archaeological site': 'cultural', 'cultural center': 'cultural',
    'shopping mall': 'shopping', 'market': 'shopping', 'mosque': 'religious',
    'park': 'nature', 'island park': 'nature', 'national park': 'nature',
    'garden': 'nature', 'mountain': 'nature', 'farm': 'nature',
    'island': 'nature', 'amusement park': 'entertainment',
    'festival': 'entertainment', 'sports venue': 'sports', 'university': 'education',
}


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def parse_date(value):
    if not isinstance(value, str) or value.strip().casefold() in ('true', 'false', '0', '1', 'yes', 'no', ''):
        return None
    try:
        return datetime.fromisoformat(value.strip()).date()
    except ValueError:
        pass
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%Y %H:%M', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            pass
    return None


def parse_time(value):
    try:
        parsed = datetime.strptime(value.strip(), '%H:%M')
        return parsed.hour * 60 + parsed.minute
    except (ValueError, AttributeError):
        return None


def load_tourism(path=CSV_PATH):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames
    required = {'ItemId', 'ItemName', 'Category', 'CityName', 'Price', 'DurationMinutes',
                'Activity_Indoor_Outdoor', 'MinAge', 'MaxAge', 'StartTime', 'EndTime',
                'AvailableDate', 'EndDate', 'IsActive', 'Is_year_Around', 'BudgetLevel',
                'PopularityScore', 'AvgRating', 'Latitude', 'longitude',
                'IsFamilySuitable', 'IsSeniorsSuitable', 'ItemDescription'}
    if not required.issubset(columns or []):
        raise ValueError(f'Tourism CSV missing columns: {sorted(required - set(columns or []))}')
    ids = Counter(r['ItemId'] for r in rows)
    items, audit = [], []
    for line, raw in enumerate(rows, 2):
        issues = []
        if None in raw or any(v is None for v in raw.values()):
            issues.append('column_count_mismatch')
        r = {k: (v or '').strip() for k, v in raw.items() if k is not None}
        category_raw = r['Category']
        category = CATEGORY_ALIASES.get(category_raw.casefold(), category_raw.casefold())
        budget = {'moderate': 'mid'}.get(r['BudgetLevel'].casefold(), r['BudgetLevel'].casefold())
        if not r['ItemId'] or ids[r['ItemId']] > 1:
            issues.append('missing_or_duplicate_item_id')
        for field in ('ItemName', 'CityName', 'Category'):
            if not r[field]:
                issues.append('missing_' + field)
        numeric = {}
        bounds = {'Price': (0, None), 'DurationMinutes': (1, 1440),
                  'MinAge': (0, 120), 'MaxAge': (0, 120),
                  'PopularityScore': (0, 1), 'AvgRating': (0, 5),
                  'Latitude': (16, 33), 'longitude': (34, 56)}
        for key, (low, high) in bounds.items():
            n = number(r[key])
            numeric[key] = n
            if n is None or n < low or (high is not None and n > high):
                issues.append('invalid_' + key)
        if numeric['MinAge'] is not None and numeric['MaxAge'] is not None and numeric['MinAge'] > numeric['MaxAge']:
            issues.append('reversed_age_range')
        flags = {}
        for key in ('IsActive', 'Is_year_Around', 'IsFamilySuitable', 'IsSeniorsSuitable'):
            value = r[key].casefold()
            flags[key] = value == 'true'
            if value not in ('true', 'false'):
                issues.append('invalid_' + key)
        if budget not in ('free', 'low', 'mid', 'high', 'luxury'):
            issues.append('invalid_BudgetLevel')
        environment = r['Activity_Indoor_Outdoor'].title()
        if environment not in ('Indoor', 'Outdoor', 'Both'):
            issues.append('invalid_environment')
        start, end = parse_date(r['AvailableDate']), parse_date(r['EndDate'])
        if start is None or end is None:
            issues.append('invalid_availability_dates')
        elif start > end:
            issues.append('reversed_availability_dates')
        opening, closing = parse_time(r['StartTime']), parse_time(r['EndTime'])
        if opening is None or closing is None:
            issues.append('invalid_opening_hours')
        elif opening == closing:
            issues.append('ambiguous_opening_hours')
        audit.append({'source_row': line, 'ItemId': r['ItemId'], 'ItemName': r['ItemName'],
                      'CityName': r['CityName'], 'eligible': not issues,
                      'active': flags['IsActive'], 'issues': '; '.join(issues),
                      'raw_category': category_raw, 'normalized_category': category,
                      'raw_budget': r['BudgetLevel'], 'normalized_budget': budget,
                      'unknown_available_from': start is None, 'unknown_available_until': end is None,
                      'reversed_date_range': start is not None and end is not None and start > end,
                      'boolean_like_date': any(r[k].casefold() in ('true', 'false', '0', '1', 'yes', 'no') for k in ('AvailableDate', 'EndDate')),
                      'year_round': flags['Is_year_Around']})
        if issues:
            continue
        items.append({**r, **numeric, **flags, 'category': category, 'budget': budget,
                      'environment': environment, 'available_from': date.min if flags['Is_year_Around'] else start,
                      'available_until': date.max if flags['Is_year_Around'] else end,
                      'availability_policy': 'year_round' if flags['Is_year_Around'] else 'source_interval',
                      'opens': opening, 'closes': closing,
                      'source_row': line})
    return items, audit


def load_wvs(path=WVS_PATH):
    sheets = read_workbook(path)
    required = {'HOBBY_RESULTS': 'Hobby', 'CATEGORY_RESULTS': 'Category',
                'ENVIRONMENT_RESULTS': 'Environment', 'STATISTICAL_EFFECTS': 'Hobby'}
    result = {}
    for sheet, dimension in required.items():
        values = sheets.get(sheet)
        if not values or dimension not in values[0]:
            raise ValueError(f'Missing WVS sheet or column: {sheet}/{dimension}')
        if sheet != 'STATISTICAL_EFFECTS':
            fields = {'Birth Country', 'ISO3', 'Relative vs Global (pp)', 'Raw N',
                      'Effective N', 'Question Coverage (%)', 'Eligible for Ranking', 'Country Rank'}
            if not fields.issubset(values[0]):
                raise ValueError(f'Missing WVS quality columns in {sheet}')
        result[sheet] = [dict(zip(values[0], row + [''] * (len(values[0]) - len(row)))) for row in values[1:]]
    return result
