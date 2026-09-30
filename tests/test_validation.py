from datetime import date, timedelta
from copy import deepcopy
from dataclasses import replace
from datetime import date
import unittest

from trip_planner.engine import TripRequest
from trip_planner.profiles import BASIC
from trip_planner.retrieval import retrieve_candidates
from trip_planner.settings import Settings
from trip_planner.validation import validate_llm_output
from tests.fixtures import inventory, item, valid_output


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.items = inventory()
        self.request = TripRequest('Test', youngest_age=30, oldest_age=30, start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=2 - 1)))
        self.retrieval = retrieve_candidates(self.items, self.request, {}, BASIC, Settings(activities_per_city=2))
        self.output = valid_output(self.retrieval['candidate_package'], 1)

    def check(self, output=None, request=None, items=None):
        return validate_llm_output(output if output is not None else self.output, self.retrieval,
                                   request or self.request, items if items is not None else self.items)

    def test_valid_llm_may_choose_second_city(self):
        self.assertNotEqual(self.output['selected_destination'], self.retrieval['candidate_package']['candidate_cities'][0]['city'])
        self.assertTrue(self.check()['valid'])
        self.assertEqual(len(self.check()['validated_itinerary']), 2)

    def test_city_outside_candidates_rejected(self):
        self.output['selected_destination'] = 'Invented city'
        self.assertIn('city_not_supplied', [v['code'] for v in self.check()['constraint_violations']])
        self.assertFalse(self.check()['validated_itinerary'])

    def test_unknown_item_rejected(self):
        self.output['itinerary'][0]['activities'][0]['item_id'] = 'invented'
        result = self.check()
        self.assertIn('invented', result['invalid_item_ids'])
        self.assertIn('invented', result['unknown_item_ids'])

    def test_existing_but_not_supplied_item_rejected(self):
        supplied = {i['ItemId'] for c in self.retrieval['candidate_package']['candidate_cities'] for i in c['candidate_activities']}
        omitted = next(i['ItemId'] for i in self.items if i['ItemId'] not in supplied)
        self.output['itinerary'][0]['activities'][0]['item_id'] = omitted
        result = self.check()
        self.assertIn(omitted, result['unsupplied_item_ids'])
        self.assertNotIn(omitted, result['unknown_item_ids'])

    def test_cross_city_activity_rejected(self):
        self.output['itinerary'][0]['activities'][0]['item_id'] = self.retrieval['candidate_package']['candidate_cities'][0]['candidate_activities'][0]['ItemId']
        self.assertIn('wrong_city', [v['code'] for v in self.check()['constraint_violations']])

    def test_duplicate_ids_detected_across_days(self):
        duplicate = self.output['itinerary'][0]['activities'][0]['item_id']
        self.output['itinerary'][1]['activities'][0]['item_id'] = duplicate
        self.assertEqual(self.check()['duplicate_item_ids'], [duplicate])

    def test_duplicate_names_detected(self):
        ids = [d['activities'][0]['item_id'] for d in self.output['itinerary']]
        items = [i | {'ItemName': 'Same name'} if i['ItemId'] in ids else i for i in self.items]
        self.assertTrue(self.check(items=items)['duplicate_attraction_names'])

    def test_group_price_budget_and_age_checks(self):
        costly = self.check(request=replace(self.request, adults=2, budget=30))
        self.assertEqual(costly['total_group_cost'], 40)
        self.assertIn('budget', [v['code'] for v in costly['constraint_violations']])
        aged = self.check(request=replace(self.request, oldest_age=100))
        self.assertIn('traveler_suitability', [v['code'] for v in aged['constraint_violations']])

    def test_invalid_dates_inactive_and_child_suitability(self):
        result = self.check(request=replace(self.request, start_date=date(2035, 1, 1), end_date=date(2035, 1, 2)))
        self.assertIn('itinerary_date', [v['code'] for v in result['constraint_violations']])
        result = self.check(items=[i | {'IsActive': False} for i in self.items])
        self.assertIn('inactive', [v['code'] for v in result['constraint_violations']])
        result = self.check(request=replace(self.request, children=1, youngest_age=5),
                            items=[i | {'SuitableForChildren': 0} for i in self.items])
        self.assertIn('traveler_suitability', [v['code'] for v in result['constraint_violations']])

    def test_start_time_and_transfer_constraints(self):
        self.output['itinerary'][0]['activities'][0]['start_time'] = '08:00'
        self.assertIn('opening_hours', [v['code'] for v in self.check()['constraint_violations']])
        self.output['itinerary'][0]['activities'][0]['start_time'] = '09:00'
        activity = deepcopy(self.output['itinerary'][1]['activities'][0])
        activity['start_time'] = '10:15'
        self.output['itinerary'][0]['activities'].append(activity)
        self.assertIn('overlap_or_transfer', [v['code'] for v in self.check()['constraint_violations']])

    def test_delayed_valid_start_is_allowed(self):
        self.output['itinerary'][0]['activities'][0]['start_time'] = '10:00'
        self.assertTrue(self.check()['valid'])

    def test_overnight_closing_obeys_daily_end(self):
        modified = [i | {'opens': 1200, 'closes': 120} for i in self.items]
        for d in self.output['itinerary']:
            d['activities'][0]['start_time'] = '20:00'
        self.assertTrue(self.check(items=modified)['valid'])
        self.output['itinerary'][0]['activities'][0]['start_time'] = '21:30'
        self.assertFalse(self.check(items=modified)['valid'])

    def test_bad_schema_day_counts_and_activity_limits(self):
        for invalid in [[], {}, {'selected_destination': 4}]:
            self.assertFalse(self.check(output=invalid)['valid'])
        self.output['itinerary'][1]['day'] = 1
        self.output['itinerary'][0]['activities'] *= 4
        codes = [v['code'] for v in self.check()['constraint_violations']]
        self.assertIn('trip_days', codes)
        self.assertIn('daily_activity_count', codes)


if __name__ == '__main__':
    unittest.main()
