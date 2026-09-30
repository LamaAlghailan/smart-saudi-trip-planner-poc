from copy import deepcopy
from datetime import date
import json
import unittest
from trip_planner.engine import TripRequest
from trip_planner.retrieval import retrieve_candidates
from trip_planner.payload import build_llm_payload, ACTIVITY_FIELDS
from trip_planner.validation import validate_llm_output
from tests.fixtures import inventory, valid_output


class PayloadTests(unittest.TestCase):
    def test_compact_limit_fields_and_supplied_subset_validation(self):
        items=inventory()
        for item in items:
            item['ItemDescription']='VERBOSE_DESCRIPTION_' * 100
        request=TripRequest('Test',date(2026,6,1),date(2026,6,2))
        retrieval=retrieve_candidates(items,request,{})
        original=deepcopy(retrieval)
        package,stats=build_llm_payload(retrieval,2)
        self.assertEqual(retrieval,original)
        self.assertNotIn('VERBOSE_DESCRIPTION',json.dumps(package))
        for city in package['candidate_cities']:
            self.assertEqual(len(city['candidate_activities']),2)
            self.assertEqual(set(city),{'city','candidate_activities'})
            for activity in city['candidate_activities']:
                self.assertEqual(set(activity),set(ACTIVITY_FIELDS) | {'scheduling_windows'})
        self.assertEqual(stats['activities_sent'],6)
        self.assertGreater(stats['estimated_input_tokens'],0)
        supplied={a['ItemId'] for c in package['candidate_cities'] for a in c['candidate_activities']}
        omitted=next(a['ItemId'] for c in retrieval['candidate_package']['candidate_cities'] for a in c['candidate_activities'] if a['ItemId'] not in supplied)
        output=valid_output(package)
        output['itinerary'][0]['activities'][0]['item_id']=omitted
        result=validate_llm_output(output,{'candidate_package':package},request,items)
        self.assertIn(omitted,result['unsupplied_item_ids'])
        with self.assertRaisesRegex(ValueError,'at least trip_days'):
            build_llm_payload(retrieval,1)
