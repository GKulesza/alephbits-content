# DeepSeek translation provider

The AlephBits translation pipeline supports pluggable translation providers. This
document covers the DeepSeek provider.

## Configuration

DeepSeek is configured through environment variables. **The API key must never be
stored in the repository.**

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | yes | — | DeepSeek API key (Bearer auth). |
| `DEEPSEEK_MODEL` | no | `deepseek-chat` | Model identifier. |
| `DEEPSEEK_TEMPERATURE` | no | `0.3` | Sampling temperature (lower = more deterministic). |
| `DEEPSEEK_TIMEOUT_SECONDS` | no | `180` | HTTP request timeout. |

Copy `.env.example` to `.env` for a local template. `.env` is git-ignored.

The provider fails with `DEEPSEEK_API_KEY is not configured.` when the key is
missing. It never prints, logs, or includes the key in error messages, and it
never falls back to another provider.

## Running the provider tests

All provider tests mock the HTTP layer — **no real network request is made**.

```bash
python3 tools/test_deepseek_translator.py
python3 tools/test_translation_pipeline.py   # pipeline + structural validation
```

## Dry-run usage

```bash
python3 tools/translation_pipeline.py --books <book_id>
```

A run without `--execute` only plans: it discovers books, classifies editions
(missing / stale / current / final / reviewed), and writes nothing.

## Execute usage (performs real writes)

```bash
DEEPSEEK_API_KEY=... python3 tools/translation_pipeline.py \
    --execute --translator tools/translators/deepseek_translator.py \
    --books <book_id>
```

> **WARNING:** `--execute` performs real writes — it creates and overwrites
> `reading-pack.md` and compiled artifacts for the affected editions. Always
> review the dry-run plan first. `final` editions are never touched unless
> `--unlock-final` is passed (destructive).

The first real pilot must be explicitly authorized by the founder and run in
stages (one book → one locale → validate → inspect), not as a bulk run.

## Security

- `DEEPSEEK_API_KEY` and any `.env` file must never be committed.
- Before committing provider work, verify no secret appears in `git status`,
  `git diff`, or `git diff --cached`.
- If a real key is ever detected in the working tree or history, stop and
  rotate it immediately.

## How it works

`tools/translators/deepseek_translator.py` exposes the pipeline translator
contract `translate(source_markdown, *, source_locale, target_locale) -> str`.
It calls DeepSeek's OpenAI-compatible chat-completions endpoint with a strict
system instruction (preserve Markdown, structural metadata, quiz shape, answer
order, correct-answer markers, URLs, SPDX data; translate prose only). The
response is validated strictly: it must be a Markdown document starting with
`# Title`; surrounding commentary is rejected, not cleaned. The pipeline then
runs `validate_translated_content` again before writing anything.

ISV Cyrillic and Glagolitic editions are never sent to DeepSeek — they are
derived deterministically from the ISV Latin edition by
`tools/generate_isv_script_editions.py`.
