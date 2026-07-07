# Contributing to AlephBits Content

Thank you for helping build a calm, trustworthy reading library.

## Before you start

1. Read [README.md](README.md) — repository and editorial philosophy.
2. Read [Reading Pack Authoring Format](https://github.com/alephbits/alephbits/blob/main/docs/content/READING_PACK_AUTHORING_FORMAT.md) — **write `reading-pack.md` first**.
3. Copy [reading-pack.template.md](docs/reading-pack.template.md) or the [demo pack](official/glagolitic/pl/spacer-po-krakowie/reading-pack.md).

## Your first Reading Pack

### 1. Choose a tier

| Tier | Path | When to use |
|------|------|-------------|
| Experimental | `experimental/<slug>/` | Drafts, prototypes, personal experiments |
| Community | `community/<handle>/<slug>/` | Finished packs for public sharing |
| Official | `official/<writing_system>/<language>/<slug>/` | AlephBits Editorial only — do not self-submit |

### 2. Author `reading-pack.md`

**Preferred workflow (Phase 23+):**

```
your-pack/
├── reading-pack.md     # SOURCE — edit this
├── lesson.json         # GENERATED (commit during transition)
├── text.txt            # GENERATED
├── quiz.json           # GENERATED
├── license.md          # GENERATED
└── provenance.json     # GENERATED
```

Copy [docs/reading-pack.template.md](docs/reading-pack.template.md) or `official/glagolitic/pl/spacer-po-krakowie/reading-pack.md`.

Future: `dart run scripts/compile_pack.dart` generates JSON from Markdown.

### 3. Required sections in reading-pack.md

See [READING_PACK_AUTHORING_FORMAT.md](https://github.com/alephbits/alephbits/blob/main/docs/content/READING_PACK_AUTHORING_FORMAT.md):

- **Metadata** — title, pack id, difficulty, language, genres
- **Editorial Transparency** — license, AI disclosure, revision history
- **Sources** — every source with license and retrieval date
- **Text** — complete reading prose (plain Markdown)
- **Quiz** — comprehension questions with explanations

### 4. Legacy: direct JSON editing

Until `compile_pack` ships, you may edit `lesson.json` directly. New packs should still create `reading-pack.md` as the editorial source.

### 5. License

Every pack needs a license in **Editorial Transparency** (compiled to `license.md`):

- License name
- SPDX identifier if applicable
- Link to full license text

Do not submit copyrighted material without clear permission or public-domain status.

### 6. Provenance (official packs)

**Sources** and **Editorial Transparency** sections must document:

- Who edited the pack
- Whether AI was used and how it was reviewed
- Source of the text (original, public domain, licensed, adaptation)

### 7. Validate locally

```bash
dart pub get
dart run scripts/validate_pack.dart
```

Fix all reported errors before opening a PR.

### 8. Update the manifest

Add your pack to `manifest.json` under `packs` with correct `path`, `tier`, `writingSystem`, and `language`. Update `supportedLanguages`, `supportedWritingSystems`, and `officialPackCount` if applicable.

### 9. Open a pull request

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
