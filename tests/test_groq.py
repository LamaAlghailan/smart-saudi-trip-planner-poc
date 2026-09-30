import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from datetime import date
import httpx
from openai import BadRequestError
from streamlit.testing.v1 import AppTest

from trip_planner.settings import Settings, load_settings
from trip_planner.llm import GroqProvider, OpenAIProvider, create_provider, ProviderError, SYSTEM_PROMPT, response_schema
from trip_planner.engine import TripRequest
from trip_planner.retrieval import retrieve_candidates
from tests.fixtures import inventory, valid_output


class GroqTests(unittest.TestCase):
    def test_provider_configuration(self):
        with TemporaryDirectory() as directory:
            path = Path(directory)/'.env'
            path.write_text('LLM_PROVIDER=groq\nGROQ_API_KEY=test-groq\nGROQ_MODEL=openai/gpt-oss-120b\n')
            config = load_settings(path, environ={})
            self.assertTrue(config.llm_available)
            self.assertEqual(config.model,'openai/gpt-oss-120b')
            self.assertIsInstance(create_provider(config),GroqProvider)
            self.assertEqual(config.unavailable_reason,'')
            config = load_settings(path,environ={'LLM_PROVIDER':'openai','OPENAI_API_KEY':'test-openai','OPENAI_MODEL':'test-model'})
            self.assertEqual(config.api_key,'test-openai')
            self.assertEqual(type(create_provider(config)),OpenAIProvider)
            with self.assertRaisesRegex(ValueError,'Unsupported LLM_PROVIDER'):
                load_settings(path,environ={'LLM_PROVIDER':'unsupported'})
        self.assertNotIn('OPENAI',Settings(provider='groq').unavailable_reason)

    @patch('trip_planner.llm.OpenAI')
    def test_mocked_groq_payload_and_errors(self, constructor):
        config=Settings(provider='groq',api_key='gsk_testsecret',model='openai/gpt-oss-120b')
        package=retrieve_candidates(inventory(),TripRequest('Test',date(2026,6,1),date(2026,6,2)),{})['candidate_package']
        client=constructor.return_value.__enter__.return_value
        client.responses.create.return_value=SimpleNamespace(status='completed',model=config.model,id='test',usage=None,output_text=json.dumps(valid_output(package)))
        answer=create_provider(config).generate(package)
        self.assertEqual(answer['provider'],'Groq')
        self.assertEqual(constructor.call_args.kwargs['base_url'],'https://api.groq.com/openai/v1')
        self.assertEqual(constructor.call_args.kwargs['max_retries'],0)
        payload=client.responses.create.call_args.kwargs
        self.assertEqual(json.loads(payload['input']),package)
        self.assertEqual(payload['instructions'],SYSTEM_PROMPT)
        self.assertEqual(payload['text']['format']['schema'],response_schema(package))
        response=httpx.Response(400,request=httpx.Request('POST','https://api.groq.com/openai/v1/responses'))
        client.responses.create.side_effect=BadRequestError('failure',response=response,body={'error':{'code':'bad_request','type':'invalid_request_error','message':'gsk_testsecret gsk_masked***suffix'}})
        with self.assertRaises(ProviderError) as caught:
            create_provider(config).generate(package)
        self.assertNotIn('gsk_',json.dumps(caught.exception.diagnostics))
        self.assertEqual(caught.exception.diagnostics['http_status'],400)

    def test_groq_provider_model_in_ui(self):
        config=Settings(provider='groq',model='openai/gpt-oss-120b')
        with patch('trip_planner.settings.load_settings',return_value=config), patch('trip_planner.llm.OpenAI') as guard:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertTrue(any('Provider: Groq | Model: openai/gpt-oss-120b' in c.value for c in app.caption))
            self.assertFalse(any('OPENAI_MODEL' in w.value for w in app.warning))
            guard.assert_not_called()
