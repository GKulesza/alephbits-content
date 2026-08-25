#!/usr/bin/env python3
"""Unit tests for the DeepSeek translation provider.

All API behavior is mocked via an injectable HTTP client — no network request
is ever made. The fake key ``test-secret-not-real`` is used throughout and
asserted never to leak into error output.

Run with:
  python3 tools/test_deepseek_translator.py
"""

import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import translators.deepseek_translator as ds

FAKE_KEY = "test-secret-not-real"

SAMPLE_MARKDOWN = (
    "# Spacer po Krakowie\n\n"
    "## Metadata\n\n"
    "**Pack ID:** hgp8iy3x\n"
    "**Book ID:** hgp8iy3x\n"
    "**Original language:** pl  \n"
    "**Version:** 1.0.0  \n\n"
    "## Editorial Transparency\n\n"
    "**License:** CC0 1.0 Universal (SPDX: CC0-1.0)\n\n"
    "## Text\n\n"
    "To jest polski tekst."
)


def ok_response(content):
    return json.dumps({"choices": [{"message": {"content": content}}]}, ensure_ascii=False)


class FakeHttp:
    """Records the request and returns a scripted response, or raises."""

    def __init__(self, status=200, body=ok_response("# Translated"), exc=None):
        self.status = status
        self.body = body
        self.exc = exc
        self.url = None
        self.headers = None
        self.request_body = None

    def __call__(self, url, headers, body):
        self.url = url
        self.headers = headers
        self.request_body = body
        if self.exc is not None:
            raise self.exc
        return self.status, self.body


class DeepSeekTranslatorTests(unittest.TestCase):
    def setUp(self):
        self.old_environ = dict(os.environ)
        os.environ.pop(ds.API_KEY_ENV, None)
        os.environ.pop(ds.MODEL_ENV, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_environ)

    def translate(self, http_post, *, key=FAKE_KEY, **kwargs):
        return ds.translate(
            SAMPLE_MARKDOWN,
            source_locale="pl",
            target_locale="en",
            api_key=key,
            http_post=http_post,
            **kwargs,
        )

    def test_missing_api_key(self):
        with self.assertRaises(ds.DeepSeekConfigError) as ctx:
            ds.translate(SAMPLE_MARKDOWN, source_locale="pl", target_locale="en")
        message = str(ctx.exception)
        self.assertEqual(message, "DEEPSEEK_API_KEY is not configured.")
        self.assertNotIn(FAKE_KEY, message)

    def test_successful_response_returns_content_exactly(self):
        expected = "# Translated Title\n\nZawartość."
        fake = FakeHttp(body=ok_response(expected))
        result = self.translate(fake)
        self.assertEqual(result, expected)

    def test_api_error_raises_without_key(self):
        fake = FakeHttp(
            status=401,
            body=json.dumps(
                {"error": {"message": f"Authentication failed for {FAKE_KEY}"}}
            ),
        )
        with self.assertRaises(ds.DeepSeekApiError) as ctx:
            self.translate(fake)
        message = str(ctx.exception)
        self.assertIn("HTTP 401", message)
        self.assertNotIn(FAKE_KEY, message)
        self.assertIn("[redacted]", message)

    def test_malformed_response(self):
        fake = FakeHttp(body="<html>gateway error</html>")
        with self.assertRaises(ds.DeepSeekResponseError):
            self.translate(fake)

    def test_empty_content(self):
        fake = FakeHttp(body=ok_response("   \n  "))
        with self.assertRaises(ds.DeepSeekResponseError) as ctx:
            self.translate(fake)
        self.assertIn("empty", str(ctx.exception).lower())

    def test_missing_choices_key(self):
        fake = FakeHttp(body=json.dumps({"unexpected": True}))
        with self.assertRaises(ds.DeepSeekResponseError):
            self.translate(fake)

    def test_timeout_raises_network_error(self):
        fake = FakeHttp(exc=TimeoutError("timed out"))
        with self.assertRaises(ds.DeepSeekNetworkError):
            self.translate(fake)

    def test_commentary_output_is_rejected(self):
        commentary = 'Here is your translation:\n\n# Title\n\nBody.'
        fake = FakeHttp(body=ok_response(commentary))
        with self.assertRaises(ds.DeepSeekResponseError):
            self.translate(fake)

    def test_source_locale_passed_in_request(self):
        fake = FakeHttp()
        self.translate(fake)
        body = json.loads(fake.request_body)
        user_prompt = body["messages"][1]["content"]
        self.assertIn("from Polish (source locale 'pl')", user_prompt)

    def test_target_locale_passed_in_request(self):
        fake = FakeHttp()
        self.translate(fake)
        body = json.loads(fake.request_body)
        user_prompt = body["messages"][1]["content"]
        self.assertIn("into English (target locale 'en')", user_prompt)

    def test_translation_instruction_contains_rules(self):
        fake = FakeHttp()
        self.translate(fake)
        body = json.loads(fake.request_body)
        system = body["messages"][0]["content"]
        for fragment in (
            "Do NOT translate or modify structural metadata",
            "Keep every quiz structurally identical",
            "Never change URLs",
            "SPDX identifiers",
            "Output ONLY the translated reading-pack Markdown document",
        ):
            self.assertIn(fragment, system)

    def test_markdown_payload_passed_intact(self):
        fake = FakeHttp()
        self.translate(fake)
        body = json.loads(fake.request_body)
        user_prompt = body["messages"][1]["content"]
        self.assertIn("--- BEGIN SOURCE DOCUMENT ---\n" + SAMPLE_MARKDOWN, user_prompt)

    def test_auth_header_uses_bearer_key(self):
        fake = FakeHttp()
        self.translate(fake)
        self.assertEqual(
            fake.headers["Authorization"], f"Bearer {FAKE_KEY}",
        )

    def test_model_env_override(self):
        fake = FakeHttp()
        os.environ[ds.MODEL_ENV] = "deepseek-custom"
        self.translate(fake)
        body = json.loads(fake.request_body)
        self.assertEqual(body["model"], "deepseek-custom")

    def test_default_model_fallback(self):
        # The default must be a current DeepSeek model, not the retired
        # "deepseek-chat" alias (retired 2026-07-24). Assert the literal
        # value so a regression back to the legacy default fails.
        fake = FakeHttp()
        os.environ.pop(ds.MODEL_ENV, None)
        self.translate(fake)
        body = json.loads(fake.request_body)
        self.assertEqual(body["model"], "deepseek-v4-flash")
        self.assertEqual(ds.DEFAULT_MODEL, "deepseek-v4-flash")

    def test_low_temperature_default(self):
        fake = FakeHttp()
        self.translate(fake)
        body = json.loads(fake.request_body)
        self.assertEqual(body["temperature"], ds.DEFAULT_TEMPERATURE)

    def test_no_real_network_client_used_in_tests(self):
        self.assertFalse(ds._HTTP_REQUEST_MADE)

    def test_module_loads_via_pipeline_contract(self):
        # Simulate the pipeline's load_translator: import the module by path and
        # call the translate symbol with only the contract arguments.
        module_path = Path(__file__).parent / "translators" / "deepseek_translator.py"
        spec = importlib.util.spec_from_file_location("deepseek_provider_contract", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.translate))
        fake = FakeHttp(body=ok_response("# Title\n\nOk."))
        result = module.translate(
            SAMPLE_MARKDOWN,
            source_locale="pl",
            target_locale="es",
            api_key=FAKE_KEY,
            http_post=fake,
        )
        self.assertEqual(result, "# Title\n\nOk.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
