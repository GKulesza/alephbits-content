# Contributing to AlephBits Content

Thank you for helping build a calm, trustworthy reading library.

## Before you start

1. Read [README.md](README.md) — repository and editorial philosophy.
2. Read the [Reading Pack Specification](https://github.com/alephbits/alephbits/blob/main/docs/content/READING_PACK_SPECIFICATION.md).
3. For AI-assisted authoring, see the [LLM Reading Pack Specification](https://github.com/alephbits/alephbits/blob/main/docs/content/LLM_READING_PACK_SPECIFICATION.md).

## Your first Reading Pack

### 1. Choose a tier

| Tier | Path | When to use |
|------|------|-------------|
| Experimental | `experimental/<slug>/` | Drafts, prototypes, personal experiments |
| Community | `community/<handle>/<slug>/` | Finished packs for public sharing |
| Official | `official/<writing_system>/<language>/<slug>/` | AlephBits Editorial only — do not self-submit |

### 2. Copy the template

Use `official/glagolitic/pl/spacer-po-krakowie/` as the reference layout:

```
your-pack/
├── lesson.json       # Required — metadata + reading text (+ optional inline quiz)
├── text.txt          # Recommended — diff-friendly prose (must match lesson.json text)
├── quiz.json         # Optional — must match lesson.json quiz if both exist
├── license.md        # Required — human-readable license
├── provenance.json   # Required for official — editorial audit trail
└── manifest.json     # Optional — book-level manifest for future translations
```

### 3. Fill required metadata

`lesson.json` must include at minimum:

- `id` — unique across the repository (snake_case)
- `title` — reader-facing title
- `language` — BCP 47 code (`pl`, `en`, …)
- `text` — full reading text (v1 apps load inline text)

Recommended fields: `description`, `author`, `license`, `recommendedWritingSystem`, `difficulty`, `estimatedReadingTime`, `translation`.

### 4. License

Every pack needs `license.md` with:

- License name
- SPDX identifier if applicable
- Link to full license text

Do not submit copyrighted material without clear permission or public-domain status.

### 5. Provenance (official packs)

`provenance.json` must document:

- Who edited the pack
- Whether AI was used and how it was reviewed
- Source of the text (original, public domain, licensed, adaptation)

### 6. Validate locally

```bash
dart pub get
dart run scripts/validate_pack.dart
```

Fix all reported errors before opening a PR.

### 7. Update the manifest

Add your pack to `manifest.json` under `packs` with correct `path`, `tier`, `writingSystem`, and `language`. Update `supportedLanguages`, `supportedWritingSystems`, and `officialPackCount` if applicable.

### 8. Open a pull request

CI runs `validate_pack` on every PR. Include in your PR description:

- Pack tier and intended audience
- License summary
- Source / provenance summary
- Whether AI assistance was used

## Review expectations

Reviewers check:

- [ ] `validate_pack` passes
- [ ] License is clear and acceptable
- [ ] Text quality is appropriate for the tier
- [ ] Quiz questions match the text (if present)
- [ ] No duplicate pack IDs
- [ ] Manifest entries are accurate

## Code of conduct

Be respectful. Disputed works are rejected or moved to `experimental/`. AlephBits moderators have final say on featuring and promotion.

## Questions

Open a GitHub issue in this repository or the main [alephbits](https://github.com/alephbits/alephbits) app repository.
