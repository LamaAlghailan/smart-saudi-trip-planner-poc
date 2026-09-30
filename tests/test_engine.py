from datetime import date, timedelta
from dataclasses import fields, replace
from datetime import date
import unittest

from trip_planner.data import load_tourism, load_wvs, parse_date, parse_time
from trip_planner.engine import TripRequest, daily_anchors, export_csv
from trip_planner.profiles import BASIC, WVS, infer_profile
from trip_planner.retrieval import retrieve_candidates
from trip_planner.settings import Settings
from tests.fixtures import evidence, inventory, item, wvs_fixture


class RetrievalTests(unittest.TestCase):
    def retrieve(self, items=None, request=None, wvs=None, mode=BASIC, settings=None):
        return retrieve_candidates(items if items is not None else inventory(),
                                   request or TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=1 - 1))),
                                   wvs if wvs is not None else wvs_fixture(), mode, settings)

    def test_multiple_cities_and_no_final_decision(self):
        result = self.retrieve()
        self.assertEqual(result['stats']['city_count'], 3)
        self.assertNotIn('selected_destination', result)
        self.assertNotIn('itinerary', result)
        self.assertNotIn('selected_destination', result['candidate_package'])
        self.assertFalse({f.name for f in fields(TripRequest)} &
                         {'city', 'destination', 'environment', 'explicit_interests', 'mode'})

    def test_basic_has_no_wvs_even_with_different_wvs_data(self):
        first = self.retrieve(wvs={})
        second = self.retrieve(wvs=wvs_fixture())
        self.assertEqual(first['candidate_package'], second['candidate_package'])
        self.assertNotIn('wvs_prior', first['candidate_package'])
        self.assertIsNone(first['wvs_profile'])
        self.assertEqual(set(first['candidate_package']['retrieval_weights']), {'group', 'quality'})

    def test_wvs_changes_rankings_and_is_only_ten_percent(self):
        basic = self.retrieve()
        prior = self.retrieve(mode=WVS)
        self.assertNotEqual(basic['candidate_package']['candidate_cities'][0]['city'],
                            prior['candidate_package']['candidate_cities'][0]['city'])
        self.assertEqual(prior['candidate_package']['candidate_cities'][0]['city'], 'Culture City')
        weights = prior['candidate_package']['retrieval_weights']
        self.assertAlmostEqual(sum(weights.values()), 1)
        self.assertAlmostEqual(sum(weights[k] for k in ('category', 'hobby', 'environment')), .10)

    def test_relative_signal_drives_prior_not_absolute_signal(self):
        row = evidence({'Category': 'Nature'}, 70) | {'Global Baseline (%)': '90', 'Relative vs Global (pp)': '-20'}
        profile = infer_profile({'CATEGORY_RESULTS': [row]}, 'Test', WVS)
        self.assertAlmostEqual(profile['categories']['nature'], .3)

    def test_hobby_and_environment_evidence_are_used(self):
        prior = self.retrieve(mode=WVS)
        first = prior['candidate_package']['candidate_cities'][0]
        self.assertGreater(first['city_profile']['components']['hobby'], .5)
        self.assertGreater(first['city_profile']['components']['environment'], .5)

    def test_birth_country_changes_prior(self):
        first = self.retrieve(mode=WVS)
        other = self.retrieve(mode=WVS, request=TripRequest('Other', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=1 - 1))))
        self.assertNotEqual(first['candidate_package']['candidate_cities'][0]['city'],
                            other['candidate_package']['candidate_cities'][0]['city'])

    def test_ineligible_or_duplicate_evidence_is_neutral(self):
        row = evidence({'Category': 'Cultural'}, 99, eligible='FALSE')
        self.assertFalse(infer_profile({'CATEGORY_RESULTS': [row]}, 'Test', WVS)['categories'])
        row['Eligible for Ranking'] = 'TRUE'
        self.assertFalse(infer_profile({'CATEGORY_RESULTS': [row, row]}, 'Test', WVS)['categories'])
        for change in [{'Effective N': ''}, {'Question Coverage (%)': 'nan'}, {'Relative vs Global (pp)': '0'}]:
            self.assertFalse(infer_profile({'CATEGORY_RESULTS': [row | change]}, 'Test', WVS)['categories'])

    def test_limits_and_exact_bounded_package(self):
        result = self.retrieve(settings=Settings(top_city_candidates=2, activities_per_city=2))
        self.assertEqual(result['stats']['city_count'], 2)
        self.assertEqual(result['stats']['activity_count'], 4)
        self.assertFalse(any('daily_anchor_ids' in c for c in result['candidate_package']['candidate_cities']))

    def test_shortlist_keeps_feasibility_anchors_for_long_trips(self):
        result = self.retrieve(request=TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=3 - 1))),
                               settings=Settings(top_city_candidates=2, activities_per_city=1))
        self.assertEqual(result['stats']['effective_activity_limit'], 3)
        self.assertEqual(result['stats']['activity_count'], 6)
        for city in result['candidate_package']['candidate_cities']:
            self.assertEqual(len({i['ItemId'] for i in city['candidate_activities']}), 3)

    def test_inventory_replication_does_not_add_score(self):
        small = [item(CityName='A')]
        large = [item(ItemId=str(i), ItemName=f'Copy {i}', CityName='B') for i in range(100)]
        result = self.retrieve(items=small + large)
        rows = result['city_rankings']
        self.assertAlmostEqual(rows[0]['retrieval_score'], rows[1]['retrieval_score'])
        self.assertEqual(rows[0]['city'], 'A')

    def test_deterministic_input_order_and_normalized_profiles(self):
        first = self.retrieve()
        second = self.retrieve(items=list(reversed(inventory())))
        self.assertEqual(first['candidate_package'], second['candidate_package'])
        for row in first['city_rankings']:
            self.assertAlmostEqual(sum(row['category_distribution'].values()), 1)
            self.assertAlmostEqual(sum(row['environment_distribution'].values()), 1)

    def test_hard_constraints_and_group_budget(self):
        for change in [{'IsActive': False}, {'Price': 300}, {'MaxAge': 20}, {'SuitableForAdults': 0}]:
            result = self.retrieve(items=[item(**change)],
                                   request=TripRequest('Test', adults=2, budget=500, oldest_age=30, start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=1 - 1))))
            self.assertFalse(result['candidate_package']['candidate_cities'])
        free = self.retrieve(items=[item(Price=0)], request=TripRequest('Test', budget=0, start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=1 - 1))))
        self.assertEqual(free['stats']['activity_count'], 1)

    def test_children_and_optional_age(self):
        request = TripRequest('Test', children=1, start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=1 - 1)))
        for change in [{'MinAge': 18}, {'SuitableForChildren': 'FALSE'}]:
            self.assertFalse(self.retrieve(items=[item(**change)], request=request)['stats']['city_count'])
        result = self.retrieve(request=request)
        self.assertTrue(result['stats']['city_count'])
        self.assertTrue(any('age' in w for w in result['warnings']))

    def test_dates_are_optional_or_enforced(self):
        self.assertEqual(self.retrieve()['candidate_package']['trip_days'], 1)
        expired = self.retrieve(request=TripRequest('Test', start_date=date(2035, 1, 1), end_date=(date(2035, 1, 1) + timedelta(days=1 - 1))))
        self.assertFalse(expired['stats']['city_count'])
        boundary = self.retrieve(items=[item(available_until=date(2026, 6, 1))],
                                 request=TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=1 - 1))))
        self.assertEqual(boundary['stats']['activity_count'], 1)

    def test_infeasible_cities_are_not_sent(self):
        result = self.retrieve(items=[item()], request=TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=2 - 1))))
        self.assertFalse(result['candidate_package']['candidate_cities'])

    def test_minimum_cost_distinct_date_matching(self):
        values = [item(ItemId='flexible', Price=10),
                  item(ItemId='first-day', Price=20, available_until=date(2026, 6, 1)),
                  item(ItemId='expensive', Price=100)]
        request = TripRequest('Test', budget=30, start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=2 - 1)))
        self.assertEqual(daily_anchors(values, request), {0: 'first-day', 1: 'flexible'})

    def test_invalid_facts(self):
        for values in [dict(end_date=date(2026, 5, 31)), dict(budget=-1), dict(budget=float('nan')),
                       dict(adults=0), dict(children=-1), dict(youngest_age=50, oldest_age=20),
                       dict(children=1, youngest_age=30), dict(birth_country='')]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.retrieve(request=replace(TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=2 - 1))), **values))

    def test_real_data_retrieval(self):
        items, audit = load_tourism()
        self.assertEqual(len(audit), 821)
        result = self.retrieve(items=items, wvs=load_wvs(), mode=WVS,
                               request=TripRequest('India', adults=2, budget=1000, start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=3 - 1))))
        self.assertGreaterEqual(result['stats']['city_count'], 2)
        self.assertLessEqual(result['stats']['city_count'], 4)
        self.assertLessEqual(result['stats']['activity_count'], 32)
        self.assertEqual(len(result['wvs_profile']['evidence']), 22)

    def test_parsers_and_export_safety(self):
        self.assertEqual(parse_date('5/13/2026 0:00'), date(2026, 5, 13))
        self.assertIsNone(parse_date('unknown'))
        self.assertEqual(parse_time('0:00'), 0)
        self.assertIsNone(parse_time('2026-01-01'))
        self.assertIn("'=SUM", export_csv([{'ItemName': '=SUM(1,2)'}]).decode('utf-8-sig'))


if __name__ == '__main__':
    unittest.main()
