#!/usr/bin/env python3
"""AI content preparation for a new AlephBits story — PROPOSAL ONLY.

This script prepares a PROPOSAL that the founder reviews in Studio. It NEVER
writes canonical content, NEVER modifies Git, and NEVER bumps versions. The
canonical `reading-pack.md` is written only after the founder accepts the
proposal in Studio (then the normal SAVE/VALIDATE/COMPILE/PUBLISH flow runs).

Provider reuse:
    The DeepSeek HTTP client, endpoint, model resolution (DEEPSEEK_MODEL with
    the current default "deepseek-v4-flash"), temperature and error classes are
    imported from tools/translators/deepseek_translator.py — there is no
    second provider configuration.

API key handling:
    Read from the environment variable DEEPSEEK_API_KEY only. It is injected
    into this subprocess by Studio for the duration of the request. It is
    never written to files, never logged, and never included in any message.

Network behavior:
    POST {DEEPSEEK_API_URL} (default https://api.deepseek.com/chat/completions)
    Authorization: Bearer <DEEPSEEK_API_KEY>
    Model: DEEPSEEK_MODEL (default deepseek-v4-flash)
    response_format: {"type": "json_object"} so the proposal is parseable JSON.

Usage (from the repository root):

    DEEPSEEK_API_KEY=... python3 tools/ai_content_preparation.py \
        --input /tmp/input.json --output /tmp/proposal.json

Input JSON (Studio builds it; only story data, never repo paths/keys):

    {
      "title": "optional title (context only)",
      "text": "full story Markdown",
      "source_fingerprint": "sha256 of text (echoed back, for stale checks)",
      "metadata": {"audience": "...", "difficulty": 2, "category": "...",
                   "trust_classification": "...",
                   "recommended_writing_system": "..."} | omitted,
      "quiz": {"title": "...", "questions": [...]} | omitted,
      "inspirations": [{"title": "...", "url": "...", "date": "..."}] | omitted
    }

Output JSON (always written, even on failure):

    {
      "ok": true,
      "proposal_version": "...",
      "proposed_text": "...",
      "text_changed": true,
      "proposed_quiz": {...} | null,
      "proposed_metadata": {...} | null,
      "warnings": ["..."],
      "model": "...",
      "created_at": "ISO UTC",
      "source_fingerprint": "..."
    }
    or, on failure:
    {
      "ok": false,
      "errors": ["..."],
      "warnings": ["..."]
    }
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Reuse the DeepSeek provider configuration and HTTP client — no duplication.
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

import translators.deepseek_translator as ds  # noqa: E402

#: Prompt identity, versioned in code (never assembled ad hoc in the UI).
PROMPT_VERSION = "alephbits-prepare-v1"

# ---------------------------------------------------------------------------
# Canonical vocabulary (mirrors alephbits-content canonical catalogs)
# ---------------------------------------------------------------------------

CANONICAL_AUDIENCE = {
    "children",
    "family_reading",
    "teens",
    "adults",
    "everyone",
}

CANONICAL_TRUST = {
    "Fiction",
    "fiction",
    "inspired_by_reality",
    "adapted_from_real_events",
    "popular_science",
    "instruction",
    "demo",
}

#: docs/reading-pack.template.md + lib/manifest/catalog.dart
CANONICAL_CATEGORIES = {
    "travel",
    "history",
    "popular_science",
    "fairy_tale",
    "legend",
    "article",
    "biography",
    "dialogue",
    "instruction",
    "short_story",
    "mythology",
    "science_fiction",
}

DIFFICULTY_MIN = 1
DIFFICULTY_MAX = 8

IDENTITY_MARKERS = ("**Pack ID:**", "**Book ID:**", "pack_id", "book_id", "legacy_pack_id")

#: Minimum accepted length ratio of proposal vs source. Language correction may
#: shorten slightly, but a drop below this ratio means content was dropped.
MIN_LENGTH_RATIO = 0.5
WARN_LENGTH_RATIO = 0.8

_URL_RE = re.compile(r"https?://\S+")

# ---------------------------------------------------------------------------
# Prompt (versioned)
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = f"""You are the AlephBits content-preparation assistant (prompt version {PROMPT_VERSION}). You prepare a NEW story for publication by producing a PROPOSAL. The founder reviews the proposal before anything is written to the canonical repository. You never write files and never change versions.

The input is a literary story (Polish), with optional metadata, an optional quiz, and optional inspiration sources (YouTube title/URL/date) provided as context.

YOUR JOB — LANGUAGE PREPARATION ONLY:
- Correct the Polish prose: obvious grammar errors, typos, punctuation, and clear awkward phrasing.
- NEVER change the plot, NEVER add events, NEVER remove passages, NEVER change the nature of characters or the style of the story.
- Preserve the meaning and tone of every sentence.
- Keep the Markdown structure intact (headings, paragraphs, blank-line separation).

QUIZ:
- If a quiz is provided: fix obvious language errors in questions, answers and explanations; verify every question is answerable from the text; verify the marked correct answer is truly correct. Keep the same number of questions, the same answer order, and change correct_index ONLY if the previously marked answer was factually wrong.
- If NO quiz is provided: you MAY propose a quiz that follows the AlephBits canonical quiz model (2-4 answers per question, exactly one correct answer, an explanation that quotes or paraphrases the text). A proposed quiz is only a suggestion for the founder.

METADATA (PROPOSALS ONLY):
- You may propose values for: audience, difficulty, category, trust_classification, recommended_writing_system.
- Use ONLY canonical values. Audience: children|family_reading|teens|adults|everyone. Difficulty: integer 1-8. Category: one of travel|history|popular_science|fairy_tale|legend|article|biography|dialogue|instruction|short_story|mythology|science_fiction. Trust classification: Fiction|inspired_by_reality|adapted_from_real_events|popular_science|instruction|demo. Recommended writing system: a single snake_case token (e.g. latin, cyrillic, glagolitic). If unsure about a value, omit that field.

SOURCES AND INSPIRATIONS:
- Use the provided inspiration context only to understand the story. NEVER invent sources, NEVER create URLs, NEVER add a URL that was not already present in the input text.

HARD RULES:
- Respond ONLY with a JSON object matching the schema below. No markdown, no code fences, no commentary outside the JSON.
- Do NOT include book IDs, pack IDs, or any identity fields.
- Do NOT change the title.
- Do NOT truncate the text: return the full corrected text. If the text needs no correction, return it verbatim.

Output JSON schema:
{{
  "proposed_text": "full corrected story text (Markdown)",
  "proposed_quiz": {{
      "title": "quiz title or null",
      "questions": [
        {{
          "question": "question text",
          "answers": ["answer", "answer", ...],
          "correct_index": 0,
          "explanation": "explanation",
          "text_reference": "quote from text"
        }}
      ]
    }} or null,
  "proposed_metadata": {{
      "audience": "canonical audience or omitted",
      "difficulty": 1..8 or omitted,
      "category": "canonical category id or omitted",
      "trust_classification": "canonical trust value or omitted",
      "recommended_writing_system": "snake_case token or omitted"
    }} or null,
  "warnings": ["optional list of human-readable notes"]
}}"""


def build_user_prompt(input_data: dict) -> str:
    """Build the user prompt embedding only the story data."""
    lines = [
        "Prepare the following story for AlephBits publication. Produce ONLY the JSON proposal described in the system instructions.",
        "",
        f"Title (context only, do not change it): {input_data.get('title') or '(none)'}",
        "",
        "--- BEGIN STORY TEXT ---",
        input_data.get("text", ""),
        "--- END STORY TEXT ---",
    ]
    metadata = input_data.get("metadata")
    if isinstance(metadata, dict) and metadata:
        lines.append("")
        lines.append("Existing metadata (context):")
        lines.append(json.dumps(metadata, ensure_ascii=False))
    quiz = input_data.get("quiz")
    if isinstance(quiz, dict) and quiz:
        lines.append("")
        lines.append("Existing quiz (correct it if needed):")
        lines.append(json.dumps(quiz, ensure_ascii=False))
    inspirations = input_data.get("inspirations")
    if isinstance(inspirations, list) and inspirations:
        lines.append("")
        lines.append("Inspirations (context only — never invent sources/URLs):")
        lines.append(json.dumps(inspirations, ensure_ascii=False))
    return "\n".join(lines)


def build_request_body(
    input_data: dict,
    *,
    model: str,
    temperature: float,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": build_user_prompt(input_data)},
        ],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    return json.dumps(payload, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Response extraction and validation
# ---------------------------------------------------------------------------


def _extract_json_object(response_text: str) -> dict:
    """Extract `choices[0].message.content` and parse it as a JSON object.

    Tolerates optional ```json code fences around the JSON payload.
    """
    try:
        decoded = json.loads(response_text)
    except ValueError as error:
        raise ds.DeepSeekResponseError(
            "DeepSeek returned a malformed (non-JSON) response."
        ) from error
    try:
        content = decoded["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise ds.DeepSeekResponseError(
            "DeepSeek response is missing choices[0].message.content."
        ) from error
    if not isinstance(content, str):
        raise ds.DeepSeekResponseError(
            "DeepSeek returned a non-text content payload."
        )
    text = content.strip()
    if not text:
        raise ds.DeepSeekResponseError(
            "DeepSeek returned an empty proposal."
        )
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        payload = json.loads(text)
    except ValueError as error:
        raise ds.DeepSeekResponseError(
            "DeepSeek returned a malformed (non-JSON) proposal."
        ) from error
    if not isinstance(payload, dict):
        raise ds.DeepSeekResponseError(
            "DeepSeek proposal is not a JSON object."
        )
    return payload


def _find_urls(text: str) -> list:
    if not isinstance(text, str):
        return []
    return list(dict.fromkeys(_URL_RE.findall(text)))


def _validate_quiz(quiz, errors: list, warnings: list) -> None:
    if not isinstance(quiz, dict):
        errors.append("proposed_quiz must be an object or null.")
        return
    questions = quiz.get("questions")
    if not isinstance(questions, list) or not questions:
        errors.append("proposed_quiz.questions must be a non-empty list.")
        return
    for i, q in enumerate(questions):
        prefix = f"quiz question {i + 1}"
        if not isinstance(q, dict):
            errors.append(f"{prefix} must be an object.")
            continue
        question = q.get("question")
        answers = q.get("answers")
        correct_index = q.get("correct_index")
        if not isinstance(question, str) or not question.strip():
            errors.append(f"{prefix} has an empty question.")
        if not isinstance(answers, list) or len(answers) < 2:
            errors.append(f"{prefix} must have at least 2 answers.")
        else:
            if any(not isinstance(a, str) or not a.strip() for a in answers):
                errors.append(f"{prefix} has empty answers.")
        if (
            not isinstance(correct_index, int)
            or not isinstance(answers, list)
            or not (0 <= correct_index < len(answers))
        ):
            errors.append(f"{prefix} has an invalid correct_index.")


def _validate_metadata(meta, errors: list, warnings: list) -> dict:
    """Validate metadata proposals; drop unsupported/invalid keys."""
    allowed_keys = {
        "audience",
        "difficulty",
        "category",
        "trust_classification",
        "recommended_writing_system",
    }
    cleaned: dict = {}
    for key, value in meta.items():
        if key not in allowed_keys:
            warnings.append(f"metadata key '{key}' is not supported and was dropped.")
            continue
        if key == "audience":
            if value in CANONICAL_AUDIENCE:
                cleaned[key] = value
            else:
                warnings.append(f"audience '{value}' is not a canonical value and was dropped.")
        elif key == "difficulty":
            try:
                number = int(value)
            except (TypeError, ValueError):
                number = -1
            if DIFFICULTY_MIN <= number <= DIFFICULTY_MAX:
                cleaned[key] = number
            else:
                warnings.append(f"difficulty '{value}' must be 1-{DIFFICULTY_MAX} and was dropped.")
        elif key == "category":
            if value in CANONICAL_CATEGORIES:
                cleaned[key] = value
            else:
                warnings.append(f"category '{value}' is not a canonical category and was dropped.")
        elif key == "trust_classification":
            if value in CANONICAL_TRUST:
                cleaned[key] = value
            else:
                warnings.append(f"trust_classification '{value}' is not canonical and was dropped.")
        elif key == "recommended_writing_system":
            if isinstance(value, str) and re.fullmatch(r"[a-z0-9_]+", value):
                cleaned[key] = value
            else:
                warnings.append(f"recommended_writing_system '{value}' is not a snake_case token and was dropped.")
    return cleaned


def validate_proposal(data: dict, source_text: str) -> tuple:
    """Validate the AI proposal. Returns (errors, warnings).

    Errors mean the proposal must NOT be shown as saveable; warnings are shown
    to the founder. This is the authoritative gate before Studio displays or
    accepts anything.
    """
    errors: list = []
    warnings: list = []

    proposed_text = data.get("proposed_text")
    if not isinstance(proposed_text, str) or not proposed_text.strip():
        errors.append("proposed_text is empty or missing.")
        proposed_text = ""
    else:
        ratio = len(proposed_text.strip()) / max(1, len(source_text.strip()))
        if ratio < MIN_LENGTH_RATIO:
            errors.append(
                f"proposed_text is suspiciously short ({ratio:.0%} of the source length)."
            )
        elif ratio < WARN_LENGTH_RATIO:
            warnings.append(
                f"proposed_text is noticeably shorter than the source ({ratio:.0%})."
            )
        for marker in IDENTITY_MARKERS:
            if marker in proposed_text:
                errors.append(
                    f"proposed_text contains identity marker '{marker}'; "
                    "identity is not editable by AI."
                )

    quiz = data.get("proposed_quiz")
    if quiz is not None:
        _validate_quiz(quiz, errors, warnings)

    metadata = data.get("proposed_metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            errors.append("proposed_metadata must be an object or null.")
        else:
            cleaned = _validate_metadata(metadata, errors, warnings)
            data["proposed_metadata"] = cleaned or None

    if proposed_text:
        source_urls = set(_find_urls(source_text))
        new_urls = set(
            _find_urls(proposed_text)
            + _find_urls(json.dumps(data.get("proposed_quiz") or {}, ensure_ascii=False))
        ) - source_urls
        if new_urls:
            warnings.append(
                "AI introduced URL(s) that were not in the source text — "
                "verify manually: "
                + ", ".join(sorted(new_urls)[:3])
            )

    return errors, warnings


# ---------------------------------------------------------------------------
# Provider entry point
# ---------------------------------------------------------------------------

HttpPost = Callable[[str, dict, str], tuple]


def prepare(
    input_data: dict,
    *,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    http_post: Optional[HttpPost] = None,
) -> dict:
    """Run AI content preparation for one story. Returns the proposal dict.

    The API key comes from ``DEEPSEEK_API_KEY`` unless explicitly injected
    (tests). Raises ``DeepSeekError`` subclasses on configuration, network,
    API, or malformed-response problems. The key is never included in any
    message. Validation failures are returned as ``{"ok": false, errors: ...}``
    — they are not exceptions, because Studio must surface them to the founder.
    """
    key = api_key if api_key is not None else os.environ.get(ds.API_KEY_ENV, "")
    if not key:
        raise ds.DeepSeekConfigError(f"{ds.API_KEY_ENV} is not configured.")

    source_text = input_data.get("text", "")
    if not isinstance(source_text, str) or not source_text.strip():
        return {"ok": False, "errors": ["input text is empty."], "warnings": []}

    resolved_model = model or os.environ.get(ds.MODEL_ENV, "") or ds.DEFAULT_MODEL
    resolved_temperature = temperature
    if resolved_temperature is None:
        resolved_temperature = ds._env_float(ds.TEMPERATURE_ENV, ds.DEFAULT_TEMPERATURE)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }
    body = build_request_body(input_data, model=resolved_model, temperature=resolved_temperature)

    poster = http_post or ds.default_http_post
    try:
        status, response_text = poster(ds.DEFAULT_API_URL, headers, body)
    except (TimeoutError, ConnectionError, OSError) as error:
        raise ds.DeepSeekNetworkError(
            "DeepSeek request failed or timed out; no proposal was produced."
        ) from error
    if status != 200:
        detail = ds._redact(ds._extract_error_detail(response_text), key)
        raise ds.DeepSeekApiError(f"DeepSeek API returned HTTP {status}.{detail}")

    data = _extract_json_object(response_text)

    errors, warnings = validate_proposal(data, source_text)
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}

    ai_warnings = data.get("warnings") or []
    if isinstance(ai_warnings, list):
        warnings = list(dict.fromkeys(warnings + [str(w) for w in ai_warnings]))

    proposal = {
        "ok": True,
        "proposal_version": PROMPT_VERSION,
        "proposed_text": data["proposed_text"],
        "text_changed": data["proposed_text"] != source_text,
        "proposed_quiz": data.get("proposed_quiz"),
        "proposed_metadata": data.get("proposed_metadata"),
        "warnings": warnings,
        "model": resolved_model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_fingerprint": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
    }
    return proposal


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to the input JSON file.")
    parser.add_argument("--output", required=True, help="Path for the output JSON file.")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as handle:
        input_data = json.load(handle)

    try:
        result = prepare(input_data)
    except ds.DeepSeekError as error:
        result = {"ok": False, "errors": [str(error)], "warnings": []}

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
