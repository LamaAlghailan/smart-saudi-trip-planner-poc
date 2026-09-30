from datetime import date
from pathlib import Path
import tempfile
import unittest

from trip_planner.engine import TripRequest
from trip_planner.profiles import BASIC, WVS, infer_profile, normalized_relative_profile
from trip_planner.retrieval import retrieve_candidates
from trip_planner.settings import Settings, load_settings
from scripts.wvs_sensitivity import normalized_profile
from tests.fixtures import inventory, wvs_fixture


class ScoringMethodTests(unittest.TestCase):
    def test_default_switch_and_invalid_config(self):
        self.assertEqual(Settings().wvs_scoring_method, 'normalized_relative')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('WVS_SCORING_METHOD=raw_affinity\n')
            self.assertEqual(load_settings(path, environ={}).wvs_scoring_method, 'raw_affinity')
            self.assertEqual(load_settings(path, environ={'WVS_SCORING_METHOD':'normalized_relative'}).wvs_scoring_method, 'normalized_relative')
        with self.assertRaises(ValueError):
            Settings(wvs_scoring_method='unknown')

    def test_normalization_matches_offline_experiment_and_preserves_source(self):
        profile = infer_profile(wvs_fixture(), 'Test', WVS)
        normalized = normalized_relative_profile(profile)
        expected = normalized_profile(profile)
        for domain in ('hobbies','categories','environments'):
            self.assertEqual(normalized[domain], expected[domain])
        self.assertNotIn('normalization', profile)
        self.assertEqual(normalized['eligible_rows'], profile['eligible_rows'])

    def test_basic_unchanged_and_wvs_metadata(self):
        request = TripRequest('Test', date(2026,6,1), date(2026,6,2))
        results = {}
        for method in ('raw_affinity','normalized_relative'):
            settings = Settings(wvs_scoring_method=method)
            results[method] = retrieve_candidates(inventory(),request,wvs_fixture(),BASIC,settings)
            run = retrieve_candidates(inventory(),request,wvs_fixture(),WVS,settings)
            package = run['candidate_package']
            self.assertEqual(package['scoring']['method'],method)
            self.assertEqual(package['scoring']['wvs_weight'],.1)
            self.assertEqual(package['retrieval_weights'],{'quality':.9,'category':.05,'hobby':.025,'environment':.025})
        self.assertEqual(results['raw_affinity']['candidate_package'],results['normalized_relative']['candidate_package'])

    def test_zero_spread_and_missing_evidence_neutral(self):
        wvs = wvs_fixture()
        for rows in wvs.values():
            for row in rows:
                row['Relative vs Global (pp)'] = '0'
                row['WVS-Derived Signal (%)'] = '50'
        result = normalized_relative_profile(infer_profile(wvs,'Test',WVS))
        self.assertTrue(all(v == .5 for domain in ('hobbies','categories','environments') for v in result[domain].values()))
        self.assertEqual(normalized_relative_profile(infer_profile({},'Unknown',WVS))['categories'],{})
