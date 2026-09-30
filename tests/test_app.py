from datetime import date
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from trip_planner.profiles import BASIC, WVS
from trip_planner.settings import Settings
from tests.fixtures import MockProvider


def start_app():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
    app.date_input(key='start_date').set_value(date(2026, 6, 1))
    app.date_input(key='end_date').set_value(date(2026, 6, 2))
    return app


def submit(app, label='Run experiment'):
    return next(b for b in app.button if b.label == label).click().run()


class AppTests(unittest.TestCase):
    def test_both_dates_required(self):
        app = start_app()
        app.selectbox(key='birth_country').set_value('India')
        app.date_input(key='end_date').set_value(None)
        submit(app)
        self.assertTrue(app.error)
        self.assertNotIn('experiment', app.session_state)
        self.api_guard.assert_not_called()

    def setUp(self):
        # Never read real API configuration or write real run logs during UI tests.
        self.enterContext(patch('trip_planner.settings.load_settings', return_value=Settings()))
        self.enterContext(patch('trip_planner.experiment.save_experiment', return_value=Path('test-only.json')))
        self.api_guard = self.enterContext(patch('trip_planner.llm.OpenAI', side_effect=AssertionError('Unexpected live API call')))

    def test_only_factual_inputs_and_two_experiment_modes(self):
        app = start_app()
        self.assertFalse(app.exception)
        self.assertEqual(list(app.radio(key='mode').options), [BASIC, WVS])
        self.assertFalse(app.multiselect)
        labels = [s.label.lower() for s in app.selectbox]
        self.assertFalse(any('city' in s or 'destination' in s or 'setting' in s or 'interest' in s for s in labels))
        self.assertIsNone(app.number_input(key='youngest').value)
        self.assertIsNone(app.number_input(key='oldest').value)
        self.assertEqual(len(app.date_input), 2)
        self.assertFalse(any(n.label == 'Trip days' for n in app.number_input))

    def test_no_api_basic_produces_candidates_only(self):
        app = start_app()
        app.selectbox(key='birth_country').set_value('India')
        submit(app)
        self.assertFalse(app.exception)
        run = app.session_state['experiment']['runs'][0]
        self.assertEqual(run['status'], 'retrieval_only')
        self.assertGreater(run['retrieval']['stats']['city_count'], 1)
        self.assertIsNone(run['llm'])
        self.assertIsNone(run['retrieval']['wvs_profile'])
        self.api_guard.assert_not_called()

    def test_no_api_comparison_is_visible_and_has_same_facts(self):
        app = start_app()
        app.selectbox(key='birth_country').set_value('India')
        submit(app, 'Compare both modes')
        self.assertFalse(app.exception)
        record = app.session_state['experiment']
        self.assertEqual(len(record['runs']), 2)
        a, b = [r['retrieval']['candidate_package'] for r in record['runs']]
        self.assertEqual(a['tourist_facts'], b['tourist_facts'])
        self.assertNotIn('wvs_prior', a)
        self.assertIn('wvs_prior', b)
        self.assertIsNone(record['comparison']['itinerary_overlap'])

    def test_wvs_mode_displays_evidence_and_no_synthetic_itinerary(self):
        app = start_app()
        app.radio(key='mode').set_value(WVS).run()
        app.selectbox(key='birth_country').set_value('India')
        submit(app)
        self.assertFalse(app.exception)
        run = app.session_state['experiment']['runs'][0]
        self.assertTrue(run['retrieval']['wvs_profile']['evidence'])
        self.assertIsNone(run['llm'])

    def test_mocked_provider_output_visible_with_mock_label(self):
        with patch('trip_planner.settings.load_settings', return_value=Settings(api_key='test-key', model='test-model')):
            mock = MockProvider(city_index=1)
            with patch('trip_planner.llm.OpenAIProvider.generate', side_effect=mock.generate):
                app = start_app()
                app.selectbox(key='birth_country').set_value('India')
                submit(app)
        self.assertFalse(app.exception)
        self.assertTrue(any('TEST MOCK' in w.value for w in app.warning))
        self.assertIsNotNone(app.session_state['experiment']['runs'][0]['llm'])

    def test_invalid_facts_and_unavailable_dates(self):
        app = start_app()
        submit(app)
        self.assertTrue(app.error)
        app.selectbox(key='birth_country').set_value('India')
        app.number_input(key='youngest').set_value(60)
        app.number_input(key='oldest').set_value(20)
        submit(app)
        self.assertTrue(app.error)
        self.assertNotIn('experiment', app.session_state)
        app.number_input(key='youngest').set_value(20)
        app.date_input(key='start_date').set_value(date(2035, 1, 1))
        app.date_input(key='end_date').set_value(date(2034, 1, 1))
        submit(app)
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertNotIn('experiment', app.session_state)

    def test_malformed_llm_output_is_rejected_without_ui_crash(self):
        with patch('trip_planner.settings.load_settings', return_value=Settings(api_key='test-key', model='test-model')):
            response = {'output': {'selected_destination': 'Invented', 'destination_reasoning': None},
                        'provider': 'TEST MOCK', 'model': 'test-model', 'is_mock': True}
            with patch('trip_planner.llm.OpenAIProvider.generate', return_value=response):
                app = start_app()
                app.selectbox(key='birth_country').set_value('India')
                submit(app)
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['experiment']['runs'][0]['status'], 'validation_failed')
        self.assertTrue(app.error)

    def test_mocked_comparison_renders_both_outputs(self):
        with patch('trip_planner.settings.load_settings', return_value=Settings(api_key='test-key', model='test-model')):
            mock = MockProvider()
            with patch('trip_planner.llm.OpenAIProvider.generate', side_effect=mock.generate):
                app = start_app()
                app.selectbox(key='birth_country').set_value('India')
                submit(app, 'Compare both modes')
        self.assertFalse(app.exception)
        self.assertEqual(len(mock.packages), 2)
        self.assertIsNotNone(app.session_state['experiment']['comparison']['itinerary_overlap'])

    def test_mode_switch_clears_previous_experiment(self):
        app = start_app()
        app.selectbox(key='birth_country').set_value('India')
        submit(app)
        app.radio(key='mode').set_value(WVS).run()
        self.assertNotIn('experiment', app.session_state)


if __name__ == '__main__':
    unittest.main()
