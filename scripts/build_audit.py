from datetime import date, timedelta
"""Generate derived audit and a reproducible example without changing sources."""
from collections import Counter
from datetime import date
import csv
import hashlib
import json

from trip_planner.data import ROOT, load_tourism, load_wvs
from trip_planner.engine import TripRequest
from trip_planner.experiment import run_comparison
from trip_planner.settings import Settings


def main():
    items, audit = load_tourism()
    wvs = load_wvs()
    output = ROOT / 'outputs'
    output.mkdir(exist_ok=True)
    with (output / 'tourism_quality_audit.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(audit[0]))
        writer.writeheader()
        writer.writerows(audit)
    summary = {'source_rows': len(audit), 'validated_rows': len(items),
               'quarantined_rows': sum(not r['eligible'] for r in audit),
               'validated_active_rows': sum(i['IsActive'] for i in items),
               'issue_counts': dict(Counter(issue for r in audit if not r['eligible'] for issue in r['issues'].split('; '))),
               'validated_active_by_city': dict(Counter(i['CityName'] for i in items if i['IsActive'])),
               'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in [*ROOT.glob('data/raw/*'), *ROOT.glob('docs/*.docx')] if p.is_file()}}
    (output / 'quality_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    prefs = TripRequest('India', start_date=date(2026, 6, 1), budget=1000, adults=2, end_date=(date(2026, 6, 1) + timedelta(days=3 - 1)))
    # Offline audit never uses .env or calls a provider.
    example = run_comparison(items, prefs, wvs, Settings())
    (output / 'example_candidate_comparison.json').write_text(json.dumps(example, default=str, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))
    print('Example: India birth country, 2026-06-01, 3 days, 2 adults, SAR 1000 group cap')
    print('Candidate counts:', [(r['mode'], r['retrieval']['stats']) for r in example['runs']])
    print('Offline audit only. No final destination or itinerary generated.')


if __name__ == '__main__':
    main()
