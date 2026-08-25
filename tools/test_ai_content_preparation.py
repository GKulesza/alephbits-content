#!/usr/bin/env python3
"""Unit tests for the AI content preparation script.

All API behavior is mocked via an injectable HTTP client — no network request
is ever made. The fake key ``test-secret-not-real`` is used throughout and
asserted never to leak into error output or the returned proposal.

Run with:
  python3 tools/test_ai_content_preparation.py
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import translators.deepseek_translator as ds
import ai_content_preparation as prep

FAKE_KEY = "test-secret-not-real"

SOURCE_TEXT = (
    "# Przygoda w lesie\n\n"
    "Dawno temu żółw i królik spotkali się w lesie. "
    "Królik biegł szybko, ale żółw wytrwale szedł naprzód. "
    "Na koniec żółw wygrał wyścig."
)


def ok_response(content):
    return json.dumps({"choices": [{"message": {"content": content}}]}, ensure_ascii=False)


class FakeHttp:
    """Records the request and returns a scripted response, or raises."""

    def __init__(self, status=200, body=None, exc=None):
        self.status = status
        self.body = body if body is not None else ok_response(_valid_proposal())
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


def _valid_proposal(**overrides):
    data = {
        "proposed_text": SOURCE_TEXT,
        "proposed_quiz": {
            "title": "Sprawdź zrozumienie",
            "questions": [
                {
                    "question": "Kto wygrał wyścig?",
                    "answers": ["Żółw", "Królik", "Lis", "Sowa"],
                    "correct_index": 0,
                    "explanation": "Żółw wytrwale szedł i wygrał.",
                    "text_reference": "żółw wygrał wyścig",
                }
            ],
        },
        "proposed_metadata": {
            "audience": "children",
            "difficulty": 2,
            "category": "fairy_tale",
            "trust_classification": "Fiction",
            "recommended_writing_system": "glagolitic",
        },
        "warnings": [],
    }
    data.update(overrides)
    return json.dumps(data, ensure_ascii=False)


class AiContentPreparationTests(unittest.TestCase):
    def setUp(self):
        self.old_environ = dict(os.environ)
        os.environ.pop(ds.API_KEY_ENV, None)
        os.environ.pop(ds.MODEL_ENV, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_environ)

    def input_data(self, **overrides):
        data = {
            "title": "Przygoda w lesie",
            "text": SOURCE_TEXT,
            "metadata": {
                "audience": "everyone",
                "difficulty": 3,
                "category": "short_story",
            },
        }
        data.update(overrides)
        return data

    def prepare(self, http_post, *, key=FAKE_KEY, **kwargs):
        return prep.prepare(self.input_data(), api_key=key, http_post=http_post, **kwargs)

    # ------------------------------------------------------------------
    # Config / network errors
    # ------------------------------------------------------------------

    def test_missing_api_key(self):
        with self.assertRaises(ds.DeepSeekConfigError) as ctx:
            prep.prepare(self.input_data())
        message = str(ctx.exception)
        self.assertEqual(message, "DEEPSEEK_API_KEY is not configured.")
        self.assertNotIn(FAKE_KEY, message)

    def test_timeout_raises_network_error(self):
        fake = FakeHttp(exc=TimeoutError("timed out"))
        with self.assertRaises(ds.DeepSeekNetworkError):
            self.prepare(fake)

    def test_api_error_raises_without_key(self):
        fake = FakeHttp(
            status=401,
            body=json.dumps({"error": {"message": f"Authentication failed for {FAKE_KEY}"}}),
        )
        with self.assertRaises(ds.DeepSeekApiError) as ctx:
            self.prepare(fake)
        message = str(ctx.exception)
        self.assertIn("HTTP 401", message)
        self.assertNotIn(FAKE_KEY, message)
        self.assertIn("[redacted]", message)

    def test_malformed_response(self):
        fake = FakeHttp(body="<html>gateway error</html>")
        with self.assertRaises(ds.DeepSeekResponseError):
            self.prepare(fake)

    def test_non_object_json_response(self):
        fake = FakeHttp(body=ok_response(json.dumps(["not", "an", "object"])))
        with self.assertRaises(ds.DeepSeekResponseError):
            self.prepare(fake)

    def test_json_fence_is_tolerated(self):
        fenced = "```json\n" + _valid_proposal() + "\n```"
        fake = FakeHttp(body=ok_response(fenced))
        result = self.prepare(fake)
        self.assertTrue(result["ok"])

    # ------------------------------------------------------------------
    # Success path
    # ------------------------------------------------------------------

    def test_successful_proposal(self):
        fake = FakeHttp()
        result = self.prepare(fake)
        self.assertTrue(result["ok"])
        self.assertEqual(result["proposed_text"], SOURCE_TEXT)
        self.assertEqual(result["proposal_version"], prep.PROMPT_VERSION)
        self.assertIn("created_at", result)
        self.assertEqual(len(result["source_fingerprint"]), 64)

    def test_model_resolution_and_default(self):
        fake = FakeHttp()
        os.environ.pop(ds.MODEL_ENV, None)
        self.prepare(fake)
        body = json.loads(fake.request_body)
        self.assertEqual(body["model"], "deepseek-v4-flash")
        self.assertEqual(body["response_format"], {"type": "json_object"})

        os.environ[ds.MODEL_ENV] = "deepseek-custom"
        self.prepare(fake)
        body = json.loads(fake.request_body)
        self.assertEqual(body["model"], "deepseek-custom")

    def test_auth_header_uses_bearer_key(self):
        fake = FakeHttp()
        self.prepare(fake)
        self.assertEqual(fake.headers["Authorization"], f"Bearer {FAKE_KEY}")

    def test_request_body_contains_text_but_no_local_paths_or_keys(self):
        fake = FakeHttp()
        self.prepare(fake)
        body = json.loads(fake.request_body)
        user_prompt = body["messages"][1]["content"]
        self.assertIn(SOURCE_TEXT, user_prompt)
        self.assertNotIn(FAKE_KEY, user_prompt)
        self.assertNotIn("/Users/", user_prompt)
        self.assertNotIn("repoPath", user_prompt)
        self.assertNotIn("alephbits-content", user_prompt)
        self.assertNotIn(FAKE_KEY, json.dumps(body, ensure_ascii=False))

    def test_prompt_is_versioned_and_contains_rules(self):
        fake = FakeHttp()
        self.prepare(fake)
        body = json.loads(fake.request_body)
        system = body["messages"][0]["content"]
        for fragment in (
            prep.PROMPT_VERSION,
            "NEVER change the plot",
            "Do NOT truncate the text",
            "NEVER invent sources",
            "Do NOT change the title",
            "canonical quiz model",
        ):
            self.assertIn(fragment, system)

    def test_metadata_is_optional_in_request(self):
        fake = FakeHttp()
        prep.prepare(
            self.input_data(metadata=None),
            api_key=FAKE_KEY,
            http_post=fake,
        )
        body = json.loads(fake.request_body)
        self.assertNotIn("Existing metadata", body["messages"][1]["content"])

    # ------------------------------------------------------------------
    # Validation gates
    # ------------------------------------------------------------------

    def test_missing_proposed_text_is_rejected(self):
        fake = FakeHttp(
            body=ok_response(json.dumps({"proposed_quiz": None, "warnings": []}))
        )
        result = self.prepare(fake)
        self.assertFalse(result["ok"])
        self.assertTrue(any("proposed_text" in e for e in result["errors"]))

    def test_empty_input_text_is_rejected(self):
        fake = FakeHttp()
        result = prep.prepare(self.input_data(text="   "), api_key=FAKE_KEY, http_post=fake)
        self.assertFalse(result["ok"])
        self.assertIn("input text is empty", " ".join(result["errors"]))

    def test_suspicious_truncation_is_rejected(self):
        truncated = SOURCE_TEXT[: len(SOURCE_TEXT) // 3]
        fake = FakeHttp(body=ok_response(_valid_proposal(proposed_text=truncated)))
        result = self.prepare(fake)
        self.assertFalse(result["ok"])
        self.assertTrue(any("suspiciously short" in e for e in result["errors"]))

    def test_slight_shrink_issues_warning_not_error(self):
        # Remove one full sentence: ratio stays above the 0.5 error threshold
        # but below the 0.8 warning threshold.
        shortened = SOURCE_TEXT.replace(
            "Królik biegł szybko, ale żółw wytrwale szedł naprzód. ", ""
        )
        fake = FakeHttp(body=ok_response(_valid_proposal(proposed_text=shortened)))
        result = self.prepare(fake)
        self.assertTrue(result["ok"])
        self.assertTrue(any("noticeably shorter" in w for w in result["warnings"]))

    def test_identity_marker_in_proposal_is_rejected(self):
        polluted = "# X\n\n**Pack ID:** abc12345\n\n" + SOURCE_TEXT
        fake = FakeHttp(body=ok_response(_valid_proposal(proposed_text=polluted)))
        result = self.prepare(fake)
        self.assertFalse(result["ok"])
        self.assertTrue(any("identity marker" in e for e in result["errors"]))

    def test_quiz_structure_is_validated(self):
        bad = _valid_proposal(proposed_quiz={
            "questions": [
                {
                    "question": "Pytanie?",
                    "answers": ["Tylko jedna"],
                    "correct_index": 3,
                }
            ]
        })
        fake = FakeHttp(body=ok_response(bad))
        result = self.prepare(fake)
        self.assertFalse(result["ok"])
        self.assertTrue(any("correct_index" in e for e in result["errors"]))

    def test_metadata_invalid_values_dropped_with_warnings(self):
        bad = _valid_proposal(proposed_metadata={
            "audience": "aliens",
            "difficulty": 99,
            "category": "not_a_category",
            "trust_classification": "Fiction",
            "recommended_writing_system": "bad value!",
            "mystery_key": 1,
        })
        fake = FakeHttp(body=ok_response(bad))
        result = self.prepare(fake)
        self.assertTrue(result["ok"])
        metadata = result["proposed_metadata"]
        self.assertEqual(metadata, {"trust_classification": "Fiction"})
        warning_text = " ".join(result["warnings"])
        for fragment in ("audience", "difficulty", "category", "recommended_writing_system", "mystery_key"):
            self.assertIn(fragment, warning_text)

    def test_fabricated_url_warning_when_no_inspirations(self):
        with_url = "# X\n\n" + SOURCE_TEXT + "\n\nŹródło: https://przyklad.example/x"
        fake = FakeHttp(body=ok_response(_valid_proposal(proposed_text=with_url)))
        result = prep.prepare(
            self.input_data(inspirations=[]),
            api_key=FAKE_KEY,
            http_post=fake,
        )
        self.assertTrue(result["ok"])
        self.assertTrue(any("URL" in w for w in result["warnings"]))

    def test_source_urls_present_are_allowed(self):
        with_url = SOURCE_TEXT + "\n\nŹródło: https://www.youtube.com/watch?v=abc123"
        fake = FakeHttp(body=ok_response(_valid_proposal(proposed_text=with_url)))
        result = prep.prepare(
            self.input_data(text=with_url),
            api_key=FAKE_KEY,
            http_post=fake,
        )
        self.assertTrue(result["ok"])
        self.assertFalse(any("URL" in w for w in result["warnings"]))

    def test_fingerprint_echoes_source(self):
        fake = FakeHttp()
        result = self.prepare(fake)
        import hashlib
        self.assertEqual(
            result["source_fingerprint"],
            hashlib.sha256(SOURCE_TEXT.encode("utf-8")).hexdigest(),
        )

    def test_text_changed_flag(self):
        changed = SOURCE_TEXT.replace("spotkali", "spotykali") + "\n"
        fake = FakeHttp(body=ok_response(_valid_proposal(proposed_text=changed)))
        result = self.prepare(fake)
        self.assertTrue(result["ok"])
        self.assertTrue(result["text_changed"])

        fake = FakeHttp()
        result = self.prepare(fake)
        self.assertFalse(result["text_changed"])

    def test_no_real_network_client_used_in_tests(self):
        self.assertFalse(ds._HTTP_REQUEST_MADE)


if __name__ == "__main__":
    unittest.main(verbosity=2)
