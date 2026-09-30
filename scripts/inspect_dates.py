"""Read-only date inspection plus reproducible offline retrieval diagnostics."""
from collections import Counter
import csv
from datetime import datetime, date
import json

from trip_planner.data import CSV_PATH, ROOT, load_tourism, load_wvs, parse_date
from trip_planner.engine import TripRequest
from trip_planner.profiles import BASIC, WVS
from trip_planner.retrieval import retrieve_candidates


def main():
    with CSV_PATH.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    def format_of(value):
        if parse_date(value) is None:
            return 'unknown/invalid'
        for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%Y %H:%M', '%m/%d/%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
            try:
                datetime.strptime(value.strip(), fmt)
                return fmt
            except ValueError:
                pass
        return 'ISO datetime'
    items, audit = load_tourism()
    request = TripRequest('India', date(2026, 10, 15), date(2026, 10, 17), budget=1000, adults=2)
    report = {
        'columns': ['AvailableDate', 'EndDate', 'StartTime', 'EndTime', 'Is_year_Around'],
        'date_formats': {k: dict(Counter(format_of(r[k]) for r in rows)) for k in ('AvailableDate', 'EndDate')},
        'diagnostics': {k: sum(r[k] for r in audit) for k in ('unknown_available_from', 'unknown_available_until', 'reversed_date_range', 'boolean_like_date')},
        'invalid_opening_hours': sum('invalid_opening_hours' in r['issues'] for r in audit),
        'ambiguous_opening_hours': sum('ambiguous_opening_hours' in r['issues'] for r in audit),
        'raw_year_round_flags': dict(Counter(r['Is_year_Around'] for r in rows)),
        'validated_year_round': sum(i['Is_year_Around'] for i in items),
        'year_round_rule': 'Otherwise valid TRUE records use date.min/date.max; malformed/reversed source ranges are still quarantined. FALSE records retain inclusive source bounds.',
        'source_records': len(rows), 'validated_records': len(items),
        'sample': {'birth_country': 'India', 'trip_start': '2026-10-15', 'trip_end': '2026-10-17', 'trip_days': 3, 'adults': 2, 'children': 0, 'budget': 1000},
        'sample_counts': {mode: retrieve_candidates(items, request, load_wvs(), mode)['stats'] for mode in (BASIC, WVS)},
    }
    text = json.dumps(report, indent=2)
    (ROOT / 'outputs/date_inspection.json').write_text(text + '\n', encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
