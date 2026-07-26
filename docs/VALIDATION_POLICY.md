# Validation Policy

**Status:** Phase 22 — defines what `validate_pack` enforces today and what should be added.  
**Tool:** `scripts/validate_pack.dart`

---

## Tiers

| Tier | Meaning | CI behavior |
|------|---------|-------------|
| **Required** | Merge blocked if failing | `validate_pack` exits non-zero |
| **Recommended** | Warning printed; merge allowed for now | Future: `--strict` flag |
| **Future** | Not implemented | Tracked in issues / roadmap |

---

## Repository manifest

| Check | Tier | Implemented |
|-------|------|-------------|
| `manifest.json` exists | Required | ✓ |
| All required top-level fields present | Required | ✓ |
| `packs` is array | Required | ✓ |
| No duplicate pack `id` | Required | ✓ |
| Every pack `path` exists on disk | Required | ✓ |
| `officialPackCount` matches indexed official packs | Required | ✓ |
| `featuredCollections[].packIds` reference valid packs | Required | ✓ |
| `generatedAt` is valid ISO 8601 | Recommended | — |
| Every pack `categories[]` id exists in `categories` | Recommended | — |
| `lesson.version` matches manifest pack `version` | Recommended | — |
| Pack `sha256` checksums | Future | — |

---

## Per-pack files

| Check | Tier | Implemented |
|-------|------|-------------|
| `reading-pack.md` exists under `books/` | Required | ✓ |
| `lesson.json` exists | Required | ✓ |
| `license.md` exists | Required | ✓ |
| Generated artifacts match `compile_pack` (read-only) | Required | ✓ |
| `generatedBy` / `generatedFrom` markers on JSON artifacts | Required | ✓ |
| `provenance.json` for official | Required | ✓ |
| Valid JSON in all `.json` files | Required | ✓ |
| `lesson.json`: `id`, `title`, `language`, `text` | Required | ✓ |
| `difficulty` in 1–8 | Required | ✓ |
| `audience` present and known (canonical or legacy alias) | Required | ✓ |
| Audience ≠ Category (axes independent) | Required (policy) | ✓ docs |
| Audience ≠ Difficulty (axes independent) | Required (policy) | ✓ docs |
| `text.txt` matches `lesson.json` text if present | Required | ✓ |
| `quiz.json` matches inline quiz if both present | Required | ✓ |
| `quiz.json` without `reading-pack.md` rejected | Required | ✓ |
| `provenance.packId` matches `lesson.id` | Required | ✓ |
| Official provenance not under wrong tier | Required | ✓ |
| Book `manifest.json` language consistency | Required | ✓ |
| `references[].title` present | Required | ✓ |
| `references[].url` is http(s) if present | Required | ✓ |
| `estimatedReadingTime` vs word count | Recommended | — |
| `author`, `description`, `license` in lesson | Recommended | — |
| Cover image exists if referenced | Future | — |

## Book ownership (`book.yaml`)

| Check | Tier | Implemented |
|-------|------|-------------|
| `book.yaml` present for each `books/<id>/` | Required | ✓ |
| Required: `book_id`, `status`, `default_locale` | Required | ✓ |
| Forbidden: `editorial_metadata`, `license`, `author` | Required | ✓ |

## Studies

| Check | Tier | Implemented |
|-------|------|-------------|
| `study.yaml` `book:` is a real `book_id` | Required | ✓ |
| `questions:` file exists | Required | ✓ |
| No `quiz.json` under `studies/` | Required | ✓ |

Ownership policy: [EDITORIAL_OWNERSHIP.md](EDITORIAL_OWNERSHIP.md).

---

## Quiz

| Check | Tier | Implemented |
|-------|------|-------------|
| At least one question | Required | ✓ |
| `type: single_choice` only (v1) | Required | ✓ |
| Non-empty question text | Required | ✓ |
| At least 2 answers | Required | ✓ |
| No duplicate answers (case-insensitive) | Required | ✓ |
| Valid `correctIndex` | Required | ✓ |
| Non-empty answers | Required | ✓ |
| Explanation present | Recommended | — |
| Question count within genre range | Future | — |
| Answer supported by text (NLP) | Future | — |

---

## Editorial quality (human gates)

These are **not** automated — see [EDITORIAL_QUALITY_STANDARDS.md](https://github.com/alephbits/alephbits/blob/main/docs/content/EDITORIAL_QUALITY_STANDARDS.md):

| Check | Tier |
|-------|------|
| Two-human review for official | Required (process) |
| License verification | Required (process) |
| Spelling ≤2/1000 words | Required (process) |
| Quiz answerability from text | Required (process) |

---

## Official pack publication gate

Before promoting to `status: official`:

1. All **Required** checks pass in CI
2. Human checklist in EDITORIAL_QUALITY_STANDARDS complete
3. Manifest pack entry added/updated
4. `officialPackCount` incremented if new official pack

---

## Running validation

```bash
dart pub get
dart run scripts/validate_pack.dart
```

Strict mode (future):

```bash
dart run scripts/validate_pack.dart --strict
```

---

## Related

- [schemas/](../schemas/) — JSON Schema contracts
- [CONTRIBUTING.md](../CONTRIBUTING.md) — contributor workflow
