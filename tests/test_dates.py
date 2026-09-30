import csv
from datetime import date
from pathlib import Path
import tempfile
import unittest

from trip_planner.data import CSV_PATH, load_tourism, parse_date
from trip_planner.engine import TripRequest, filter_by_trip_dates
from trip_planner.retrieval import retrieve_candidates
from trip_planner.profiles import BASIC, WVS
from trip_planner.validation import validate_llm_output
from tests.fixtures import item, inventory, valid_output, wvs_fixture


class DateTests(unittest.TestCase):
    def test_inclusive_trip_days_and_invalid_ranges(self):
        self.assertEqual(TripRequest('Test', date(2026, 6, 1), date(2026, 6, 3)).days, 3)
        self.assertEqual(TripRequest('Test', date(2026, 6, 1), date(2026, 6, 1)).days, 1)
        for start, end in [(None, None), (date(2026, 6, 2), date(2026, 6, 1))]:
            with self.assertRaises(ValueError):
                TripRequest('Test', start, end).validate()

    def test_overlap_boundaries_partial_none_unknown(self):
        source = item(available_from=date(2026, 6, 2), available_until=date(2026, 6, 4))
        for start, end, expected in [(1, 2, 1), (4, 5, 1), (3, 5, 1), (1, 1, 0), (5, 6, 0)]:
            self.assertEqual(len(filter_by_trip_dates([source], date(2026, 6, start), date(2026, 6, end))), expected)
        self.assertFalse(filter_by_trip_dates([source | {'available_from': None}], date(2026, 6, 1), date(2026, 6, 5)))

    def test_source_date_parsing(self):
        for value in ['2026-06-01', '6/1/2026', '6/1/2026 0:00', '2026-06-01T10:20:30', '2026-06-01 10:20:30']:
            self.assertEqual(parse_date(value), date(2026, 6, 1))
        for value in ['TRUE', 'FALSE', True, False, '1', '0', '', None, '2026-02-30', 'unknown']:
            self.assertIsNone(parse_date(value))

    def test_year_round_and_malformed_source_quarantine(self):
        _, audit = load_tourism()
        good_id = next(r['ItemId'] for r in audit if r['eligible'])
        with CSV_PATH.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            source = next(r for r in reader if r['ItemId'] == good_id)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'items.csv'
            def load(value, year_round='TRUE'):
                with path.open('w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fields)
                    writer.writeheader()
                    writer.writerow(source | {'AvailableDate': value, 'EndDate': '12/31/2026', 'Is_year_Around': year_round})
                return load_tourism(path)
            records, _ = load('1/1/2026')
            self.assertEqual(records[0]['available_from'], date.min)
            self.assertEqual(records[0]['available_until'], date.max)
            self.assertTrue(filter_by_trip_dates(records, date(2035, 1, 1), date(2035, 1, 2)))
            records, _ = load('1/1/2026', 'FALSE')
            self.assertFalse(filter_by_trip_dates(records, date(2035, 1, 1), date(2035, 1, 2)))
            for value in ['TRUE', 'unknown']:
                records, diagnostics = load(value)
                self.assertFalse(records)
                self.assertTrue(diagnostics[0]['unknown_available_from'])
                self.assertEqual(diagnostics[0]['boolean_like_date'], value == 'TRUE')

    def test_same_filters_and_no_cheapness_reward(self):
        request = TripRequest('Test', date(2026, 6, 1), date(2026, 6, 2))
        items = inventory()
        runs = [retrieve_candidates(items, request, wvs_fixture(), mode) for mode in (BASIC, WVS)]
        self.assertEqual(runs[0]['candidate_package']['tourist_facts'], runs[1]['candidate_package']['tourist_facts'])
        for key in ['before_date_filter', 'after_date_filter']:
            self.assertEqual(runs[0]['stats'][key], runs[1]['stats'][key])
        cheap = retrieve_candidates(items, request, {}, BASIC)
        dear = retrieve_candidates([i | {'Price': 100} for i in items], request, {}, BASIC)
        self.assertEqual([c['retrieval_score'] for c in cheap['city_rankings']], [c['retrieval_score'] for c in dear['city_rankings']])

    def test_calendar_date_and_day_specific_availability(self):
        request = TripRequest('Test', date(2026, 6, 1), date(2026, 6, 2))
        items = inventory()
        retrieval = retrieve_candidates(items, request, {}, BASIC)
        output = valid_output(retrieval['candidate_package'])
        second_id = output['itinerary'][1]['activities'][0]['item_id']
        items = [i | {'available_until': date(2026, 6, 1)} if i['ItemId'] == second_id else i for i in items]
        retrieval = retrieve_candidates(items, request, {}, BASIC)
        codes = lambda: {v['code'] for v in validate_llm_output(output, retrieval, request, items)['constraint_violations']}
        self.assertIn('date_availability', codes())
        output['itinerary'][1]['date'] = '2026-06-03'
        self.assertIn('itinerary_date', codes())
        self.assertIn('day_date_mismatch', codes())
        output['itinerary'][1]['date'] = '2026-06-01'
        self.assertIn('day_date_mismatch', codes())
