from datetime import date, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from openai import OpenAIError
from openai import RateLimitError
import httpx
from trip_planner.engine import TripRequest
from trip_planner.experiment import run_comparison, run_mode, save_experiment
from trip_planner.llm import OpenAIProvider, ProviderError
from trip_planner.profiles import BASIC, WVS
from trip_planner.retrieval import retrieve_candidates
from trip_planner.settings import Settings, load_settings
from tests.fixtures import MockProvider, inventory, valid_output, wvs_fixture


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.request = TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=2 - 1)))
        self.package = retrieve_candidates(inventory(), self.request, {}, BASIC)['candidate_package']
        self.settings = Settings(api_key='test-only-key', model='test-only-model')

    @patch('trip_planner.llm.OpenAI')
    def test_openai_receives_only_retrieved_context_and_strict_schema(self, constructor):
        client = constructor.return_value.__enter__.return_value
        client.responses.create.return_value = SimpleNamespace(status='completed', model='test-only-model', id='test-id',
                                                               usage=None, output_text=json.dumps(valid_output(self.package, 1)))
        result = OpenAIProvider(self.settings).generate(self.package)
        kwargs = client.responses.create.call_args.kwargs
        self.assertEqual(json.loads(kwargs['input']), self.package)
        self.assertNotIn('tools', kwargs)
        self.assertFalse(kwargs['store'])
        self.assertTrue(kwargs['text']['format']['strict'])
        self.assertIn('You are not being asked to search for Saudi tourism information.', kwargs['instructions'])
        cities = kwargs['text']['format']['schema']['properties']['selected_destination']['enum']
        self.assertEqual(cities, [c['city'] for c in self.package['candidate_cities']])
        self.assertNotIn('test-only-key', kwargs['input'])
        self.assertEqual(result['output']['selected_destination'], self.package['candidate_cities'][1]['city'])

    @patch('trip_planner.llm.OpenAI')
    def test_missing_configuration_never_calls_sdk(self, constructor):
        with self.assertRaises(ProviderError):
            OpenAIProvider(Settings()).generate(self.package)
        constructor.assert_not_called()

    @patch('trip_planner.llm.OpenAI')
    def test_provider_errors_are_sanitized_and_have_no_fallback(self, constructor):
        constructor.return_value.__enter__.return_value.responses.create.side_effect = OpenAIError('test-only-key should not escape')
        with self.assertRaises(ProviderError) as caught:
            OpenAIProvider(self.settings).generate(self.package)
        self.assertNotIn('test-only-key', str(caught.exception))

    @patch('trip_planner.llm.OpenAI')
    def test_structured_error_diagnostics_redact_credentials(self, constructor):
        response = httpx.Response(429, request=httpx.Request('POST', 'https://api.openai.com/v1/responses'),
                                 headers={'x-request-id':'req-test', 'Retry-After':'30'})
        error = RateLimitError('failure', response=response, body={'error': {
            'type':'quota', 'code':'insufficient_quota',
            'message':'test-only-key sk-proj-masked***suffix Bearer private-token'}})
        client = constructor.return_value.__enter__.return_value
        client.responses.create.side_effect = error
        with self.assertRaises(ProviderError) as caught:
            OpenAIProvider(self.settings).generate(self.package)
        details = caught.exception.diagnostics
        self.assertEqual(details['http_status'],429)
        self.assertEqual(details['error']['code'],'insufficient_quota')
        self.assertEqual(details['request_id'],'req-test')
        self.assertEqual(details['retry_after'],'30')
        for secret in ('test-only-key','sk-proj','private-token'):
            self.assertNotIn(secret,json.dumps(details))
        client.responses.create.assert_called_once()
        self.assertEqual(constructor.call_args.kwargs['max_retries'],0)

    @patch('trip_planner.llm.OpenAI')
    def test_incomplete_refusal_and_malformed_json(self, constructor):
        client = constructor.return_value.__enter__.return_value
        for status, content in [('incomplete', '{}'), ('completed', ''), ('completed', 'not JSON')]:
            client.responses.create.return_value = SimpleNamespace(status=status, output_text=content)
            with self.assertRaises(ProviderError):
                OpenAIProvider(self.settings).generate(self.package)

    def test_env_settings_no_secret_repr_and_process_override(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / '.env'
            path.write_text('OPENAI_API_KEY=test-only-key\nOPENAI_MODEL=from-file\n', encoding='utf-8')
            settings = load_settings(path, {'OPENAI_MODEL': 'from-process'})
            self.assertTrue(settings.llm_available)
            self.assertEqual(settings.model, 'from-process')
            self.assertNotIn('test-only-key', repr(settings))
            with self.assertRaises(ValueError):
                load_settings(path, {'TOP_CITY_CANDIDATES': '821'})


class ExperimentTests(unittest.TestCase):
    def test_no_api_comparison_keeps_candidates_but_no_llm_decision(self):
        with patch('trip_planner.llm.OpenAI') as constructor:
            result = run_comparison(inventory(), TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=2 - 1))), wvs_fixture(), Settings())
        constructor.assert_not_called()
        for run in result['runs']:
            self.assertEqual(run['status'], 'retrieval_only')
            self.assertIsNone(run['llm'])
            self.assertIsNone(run['validation'])
        self.assertIsNone(result['comparison']['itinerary_overlap'])
        self.assertIsNotNone(result['comparison']['candidate_set_overlap'])

    def test_comparison_shares_facts_and_persists_required_metrics(self):
        provider = MockProvider()
        result = run_comparison(inventory(), TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=2 - 1))), wvs_fixture(), Settings(), provider)
        self.assertEqual(provider.packages[0]['tourist_facts'], provider.packages[1]['tourist_facts'])
        self.assertNotIn('wvs_prior', provider.packages[0])
        self.assertIn('wvs_prior', provider.packages[1])
        self.assertTrue(result['comparison']['both_itineraries_valid'])
        for key in ('candidate_set_overlap', 'candidate_city_overlap', 'itinerary_overlap', 'destination_changed'):
            self.assertIn(key, result['comparison'])
        for arm in ('basic', 'wvs'):
            self.assertIsNotNone(result['comparison'][arm]['selected_item_ids'])
            self.assertIn('constraint_violations', result['comparison'][arm])
        with TemporaryDirectory() as directory:
            path = save_experiment(result, directory)
            loaded = json.loads(path.read_text(encoding='utf-8'))
            self.assertIn('experiment_id', loaded)
            self.assertTrue(loaded['runs'][0]['llm']['is_mock'])
            self.assertNotIn('api_key', path.read_text(encoding='utf-8'))

    def test_invalid_output_is_stored_but_never_accepted(self):
        provider = MockProvider()
        original = provider.generate
        def bad(package):
            response = original(package)
            response['output']['selected_destination'] = 'Not supplied'
            return response
        provider.generate = bad
        run = run_mode(inventory(), TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=1 - 1))), {}, BASIC, Settings(), provider)
        self.assertEqual(run['status'], 'validation_failed')
        self.assertTrue(run['llm'])
        self.assertFalse(run['validation']['validated_itinerary'])

    def test_no_candidates_never_calls_provider(self):
        provider = MockProvider()
        run = run_mode([], TripRequest('Test', start_date=date(2026, 6, 1), end_date=(date(2026, 6, 1) + timedelta(days=2 - 1))), {}, WVS, Settings(), provider)
        self.assertEqual(run['status'], 'no_candidates')
        self.assertFalse(provider.packages)


if __name__ == '__main__':
    unittest.main()
