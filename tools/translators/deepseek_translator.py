#!/usr/bin/env python3
"""DeepSeek translation provider for the AlephBits translation pipeline.

Implements the pipeline translator contract:

    translate(source_markdown, *, source_locale, target_locale) -> str

The API key is NEVER stored in the repository. It is read from the
environment variable ``DEEPSEEK_API_KEY`` (or injected explicitly for tests).
The key is never printed, logged, or included in exception messages.

Uses DeepSeek's OpenAI-compatible chat completions API with the standard
library only — no third-party SDK or network dependency is introduced.

Network behavior:
    * POST https://api.deepseek.com/chat/completions
    * Authorization: Bearer <DEEPSEEK_API_KEY>
    * Model: DEEPSEEK_MODEL (default "deepseek-v4-flash")
    * Temperature: DEEPSEEK_TEMPERATURE (default 0.3) for deterministic output

Output policy (strict):
    * The response must be a Markdown document starting with a top-level
      title heading. Anything else (surrounding commentary such as
      "Here is your translation:") is rejected — never cleaned up.
    * The model is instructed to translate prose only and to preserve
      structural metadata, Markdown structure, quiz shape, answer order,
      correct-answer markers, identifiers, URLs, and SPDX/license data.
      The pipeline enforces these invariants again before writing.

Example (from the repository root):

    DEEPSEEK_API_KEY=... python3 tools/translation_pipeline.py \\
        --execute --translator tools/translators/deepseek_translator.py \\
        --books <book_id>
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY_ENV = "DEEPSEEK_API_KEY"
MODEL_ENV = "DEEPSEEK_MODEL"
TEMPERATURE_ENV = "DEEPSEEK_TEMPERATURE"
TIMEOUT_ENV = "DEEPSEEK_TIMEOUT_SECONDS"

DEFAULT_API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_TIMEOUT_SECONDS = 180

#: Human names for prompt construction. Raw codes are used as a fallback.
LOCALE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "eo": "Esperanto",
    "isv": "Interslavic (Latin script)",
    "isv_cyrl": "Interslavic (Cyrillic script)",
    "isv_glag": "Interslavic (Glagolitic script)",
    "pl": "Polish",
}

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class DeepSeekError(Exception):
    """Base class for all DeepSeek provider failures."""


class DeepSeekConfigError(DeepSeekError):
    """Missing or invalid configuration (never reveals the key)."""


class DeepSeekApiError(DeepSeekError):
    """The API returned a non-success HTTP status."""


class DeepSeekResponseError(DeepSeekError):
    """The API response was malformed, empty, or not a Markdown document."""


class DeepSeekNetworkError(DeepSeekError):
    """A network failure or timeout occurred."""


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = """You are a machine translator for the AlephBits reading-library publishing pipeline.

You translate an AlephBits "reading-pack" edition: a single Markdown document that is the editorial source for one book edition. You translate prose into the requested target language. You do NOT edit, review, improve, or redesign the source.

Hard rules:
- Translate only human-readable prose: the title, subtitle, blurb/description, main text, quiz title, quiz questions, quiz answers, quiz explanations, and the localized translation summary.
- Preserve the Markdown structure exactly: top-level "# Title" heading, all "##" section headings, "###" blocks, lists, blank-line separation, and the bold-label metadata format ("**Key:** value").
- Do NOT translate or modify structural metadata values: Pack ID, Book ID, Legacy Pack ID, Genres (canonical IDs), Audience, Difficulty, Estimated reading time, Recommended profile, Recommended level, Writing system, Trust classification, Tags, Cover family, Series, Version, Edition version, Publication date, Historical period, Original language, Translation status, Translation source, Translation source version, or any other metadata identifier.
- Do NOT translate the version numbers, edition identifiers, or the locale code.
- Keep every quiz structurally identical: the same number of questions, the same number of answers per question, the same answer order, and the same "**Correct:**" letter marker. Never reorder answers.
- Never change URLs, source anchors, SPDX identifiers, or license identifiers.
- Do not invent metadata, do not add sections, do not add commentary, and do not write anything outside the Markdown document.
- Output ONLY the translated reading-pack Markdown document. No introductory or closing text, no code fences, no quotes around the document."""


def _locale_name(locale: str) -> str:
    return LOCALE_NAMES.get(locale, locale)


def build_user_prompt(source_markdown: str, source_locale: str, target_locale: str) -> str:
    """Build the user prompt embedding the untranslated source document."""
    return (
        f"Translate the following AlephBits reading-pack edition "
        f"from {_locale_name(source_locale)} (source locale '{source_locale}') "
        f"into {_locale_name(target_locale)} (target locale '{target_locale}').\n\n"
        "Translate the prose as described in the system instructions. "
        "Preserve all Markdown structure and structural metadata. "
        "Preserve quiz answer order and correct-answer markers. "
        "Output only the translated document.\n\n"
        "--- BEGIN SOURCE DOCUMENT ---\n"
        f"{source_markdown}\n"
        "--- END SOURCE DOCUMENT ---"
    )


def build_messages(source_markdown: str, source_locale: str, target_locale: str) -> list:
    return [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {
            "role": "user",
            "content": build_user_prompt(source_markdown, source_locale, target_locale),
        },
    ]


def build_request_body(
    source_markdown: str,
    source_locale: str,
    target_locale: str,
    model: str,
    temperature: float,
) -> str:
    payload = {
        "model": model,
        "messages": build_messages(source_markdown, source_locale, target_locale),
        "temperature": temperature,
    }
    return json.dumps(payload, ensure_ascii=False)


# ---------------------------------------------------------------------------
# HTTP layer
# ---------------------------------------------------------------------------

#: (url, headers, body) -> (status_code, response_text)
HttpPost = Callable[[str, dict, str], tuple]

# Sentinel so tests can detect whether the default real-network client was used.
_HTTP_REQUEST_MADE = False


def default_http_post(url: str, headers: dict, body: str) -> tuple:
    """Real network client built on the standard library. Not used by tests."""
    global _HTTP_REQUEST_MADE
    request = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
    timeout = _env_float(TIMEOUT_ENV, DEFAULT_TIMEOUT_SECONDS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            _HTTP_REQUEST_MADE = True
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        _HTTP_REQUEST_MADE = True
        return error.code, error.read().decode("utf-8")


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "")
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Provider entry point (pipeline translator contract)
# ---------------------------------------------------------------------------


def translate(
    source_markdown: str,
    *,
    source_locale: str,
    target_locale: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    http_post: Optional[HttpPost] = None,
) -> str:
    """Translate one reading-pack Markdown edition into [target_locale].

    The API key comes from ``DEEPSEEK_API_KEY`` unless explicitly injected
    (tests). Returns the raw translated Markdown string, which the pipeline
    validates before writing.

    Raises DeepSeekError subclasses on configuration, network, API, or
    response problems. The API key is never included in any message.
    """
    key = api_key if api_key is not None else os.environ.get(API_KEY_ENV, "")
    if not key:
        raise DeepSeekConfigError(f"{API_KEY_ENV} is not configured.")

    resolved_model = model or os.environ.get(MODEL_ENV, "") or DEFAULT_MODEL
    resolved_temperature = temperature
    if resolved_temperature is None:
        resolved_temperature = _env_float(TEMPERATURE_ENV, DEFAULT_TEMPERATURE)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    body = build_request_body(source_markdown, source_locale, target_locale, resolved_model, resolved_temperature)

    poster = http_post or default_http_post
    try:
        status, response_text = poster(DEFAULT_API_URL, headers, body)
    except (TimeoutError, ConnectionError, OSError) as error:
        raise DeepSeekNetworkError(
            "DeepSeek request failed or timed out; no translation was produced."
        ) from error
    if status != 200:
        detail = _redact(_extract_error_detail(response_text), key)
        raise DeepSeekApiError(f"DeepSeek API returned HTTP {status}.{detail}")

    return _extract_content(response_text)


def _redact(text: str, secret: str) -> str:
    """Defensive redaction so a key can never surface in an error message."""
    if not secret:
        return text
    return text.replace(secret, "[redacted]")


def _extract_error_detail(response_text: str) -> str:
    """Best-effort human detail from an error body. Never echoes headers/key."""
    try:
        decoded = json.loads(response_text)
        message = decoded.get("error", {}).get("message") if isinstance(decoded, dict) else None
        if isinstance(message, str) and message.strip():
            return f" {message.strip()}"
    except (ValueError, AttributeError):
        pass
    return ""


def _extract_content(response_text: str) -> str:
    """Parse the chat-completions JSON and validate the result strictly."""
    try:
        decoded = json.loads(response_text)
    except ValueError as error:
        raise DeepSeekResponseError(
            "DeepSeek returned a malformed (non-JSON) response."
        ) from error

    try:
        content = decoded["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise DeepSeekResponseError(
            "DeepSeek response is missing choices[0].message.content."
        ) from error

    if not isinstance(content, str):
        raise DeepSeekResponseError("DeepSeek returned a non-text content payload.")

    stripped = content.strip()
    if not stripped:
        raise DeepSeekResponseError("DeepSeek returned an empty translation.")

    # Strict rejection of surrounding commentary: a reading-pack always begins
    # with a top-level title heading. We never attempt clever cleanup.
    if not re.match(r"^#\s+\S", stripped):
        raise DeepSeekResponseError(
            "DeepSeek response is not a Markdown reading-pack document "
            "(missing leading '# Title'). Rejected instead of cleaned."
        )

    return stripped
