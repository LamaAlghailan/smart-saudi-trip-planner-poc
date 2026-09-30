from datetime import date
import unittest
from trip_planner.engine import TripRequest
from trip_planner.retrieval import retrieve_candidates
from trip_planner.payload import build_llm_payload
from trip_planner.scheduling import scheduling_windows
from trip_planner.validation import validate_llm_output
from trip_planner.experiment import run_mode
from trip_planner.profiles import BASIC
from trip_planner.settings import Settings
from tests.fixtures import item, valid_output, MockProvider


class SchedulingTests(unittest.TestCase):
    def setUp(self):
        self.request = TripRequest('Test', date(2026,6,1), date(2026,6,1))
        self.items = [item(ItemId='a', ItemName='First'), item(ItemId='b', ItemName='Second')]

    def check(self, start, **changes):
        items = [i | changes for i in self.items]
        retrieval = retrieve_candidates(items, self.request, {})
        package, _ = build_llm_payload(retrieval)
        output = valid_output(package)
        output['itinerary'][0]['activities'][0]['start_time'] = start
        return validate_llm_output(output, {'candidate_package': package}, self.request, items)

    def test_start_before_opening(self):
        self.assertFalse(self.check('09:00', opens=600)['valid'])

    def test_end_after_closing(self):
        self.assertFalse(self.check('16:30', closes=1020)['valid'])

    def test_duration_overrun(self):
        self.assertFalse(self.check('16:00', DurationMinutes=120, closes=1020)['valid'])

    def test_transfer_overlap_and_valid_boundary(self):
        retrieval = retrieve_candidates(self.items, self.request, {})
        package, _ = build_llm_payload(retrieval)
        output = valid_output(package)
        output['itinerary'][0]['activities'] = [
            {'item_id':'a','start_time':'09:00','reason':'First'},
            {'item_id':'b','start_time':'10:15','reason':'Second'}]
        result = validate_llm_output(output, {'candidate_package': package}, self.request, self.items)
        self.assertIn('overlap_or_transfer', {v['code'] for v in result['constraint_violations']})
        output['itinerary'][0]['activities'][1]['start_time'] = '10:30'
        self.assertTrue(validate_llm_output(output, {'candidate_package': package}, self.request, self.items)['valid'])

    def test_valid_schedule_at_closing(self):
        self.assertTrue(self.check('16:00', closes=1020)['valid'])

    def test_daily_precheck_duration_dates_and_overnight(self):
        package, _ = build_llm_payload(retrieve_candidates(self.items,self.request,{}))
        package['trip_days'] = 2
        activity = package['candidate_cities'][0]['candidate_activities'][0]
        activity.update(opens='20:00', closes='02:00', DurationMinutes=120, available_until='2026-06-01')
        rows = scheduling_windows(activity,package)
        self.assertEqual(rows[0],{'date':'2026-06-01','schedulable':True,'earliest_start':'20:00','latest_start':'20:00'})
        self.assertFalse(rows[1]['schedulable'])
        activity['DurationMinutes']=121
        self.assertEqual(scheduling_windows(activity,package)[0]['reason'],'duration_exceeds_window')

    def test_timing_only_failure_never_retried_or_accepted(self):
        class BadTimingProvider(MockProvider):
            def generate(self, package):
                answer = super().generate(package)
                answer['output']['itinerary'][0]['activities'][0]['start_time'] = '08:00'
                return answer
        provider = BadTimingProvider()
        result = run_mode(self.items,self.request,{},BASIC,Settings(),provider)
        self.assertEqual(len(provider.packages),1)
        self.assertEqual(result['status'],'validation_failed')
        self.assertIn('Timing validation failed',result['message'])
        self.assertFalse(result['validation']['validated_itinerary'])
