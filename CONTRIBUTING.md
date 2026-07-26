# Contributing to AlephBits Content

Thank you for helping build a calm, trustworthy reading library.

## Before you start

1. Read [README.md](README.md) — repository and editorial philosophy.
2. Read [Reading Pack Authoring Format](https://github.com/alephbits/alephbits/blob/main/docs/content/READING_PACK_AUTHORING_FORMAT.md) — **write `reading-pack.md` first**.
3. Copy [reading-pack.template.md](docs/reading-pack.template.md) or the demo edition [`books/hgp8iy3x/pl/reading-pack.md`](books/hgp8iy3x/pl/reading-pack.md).

## Your first Reading Pack

### 1. Choose book id, locale, and status

| Field | Where | Notes |
|-------|-------|-------|
| `book_id` | Directory `books/<book_id>/` | Permanent random id — **not** a title slug |
| Locale | `books/<book_id>/<locale>/` | Edition identity; pack id is `{book_id}:{locale}` |
| Status / tier | `book.yaml` `status:` | `experimental` · `community` · `official` |

Do **not** place packs under `official/<writing_system>/<language>/<slug>/` — that Collection v1 layout is retired.

### 2. Author `reading-pack.md`

```
books/<book_id>/
├── book.yaml           # SOURCE — identity / status only
├── default/            # OPTIONAL shared cover.webp / vignette.webp
└── <locale>/
    ├── reading-pack.md # SOURCE — edit this
    ├── lesson.json     # GENERATED
    ├── text.txt        # GENERATED
    ├── quiz.json       # GENERATED
    ├── license.md      # GENERATED
    └── provenance.json # GENERATED
```

### 3. Compile and catalog

```bash
dart pub get
dart run tools/compile_pack.dart --overwrite books/<book_id>/<locale>
dart run tools/build_manifest.dart --overwrite
```

Do **not** hand-edit `manifest.json`. See [docs/MANIFEST.md](docs/MANIFEST.md) and [docs/COMPILE_PIPELINE.md](docs/COMPILE_PIPELINE.md).

### 4. Required sections in `reading-pack.md`

- **Metadata** — title, audience, difficulty, language, genres, cover family
- **Editorial Transparency** — license, AI disclosure, revision history
- **Sources** — every source with license and retrieval date
- **Text** — complete reading prose
- **Quiz** — comprehension questions with explanations (count by length; see app quiz guidelines)

Edition pack id (`{book_id}:{locale}`) is derived at compile time — do not invent `polish_*` ids.

### 5. Optional art

Prefer book-owned assets:

```text
books/<book_id>/default/cover.webp
books/<book_id>/default/vignette.webp
# optional locale overrides under books/<book_id>/<locale>/
```

Full rules: [VIGNETTE_ASSET_SPEC.md](https://github.com/alephbits/alephbits/blob/main/docs/content/VIGNETTE_ASSET_SPEC.md) and [docs/MIGRATION_NOTES_V2_ASSETS.md](docs/MIGRATION_NOTES_V2_ASSETS.md).

### 6. License

Every pack needs a license in **Editorial Transparency** (compiled to `license.md`):

- License name
- SPDX identifier if applicable
- Link to full license text

Do not submit copyrighted material without clear permission or public-domain status.

### 7. Provenance (official packs)

**Sources** and **Editorial Transparency** must document:

- Who edited the pack
- Whether AI was used and how it was reviewed
- Source of the text (original, public domain, licensed, adaptation)

### 8. Validate locally

```bash
dart run scripts/validate_pack.dart
```

Fix all reported errors before opening a PR.

### 9. Open a pull request

CI runs `validate_pack` on every PR. Include:

- Intended `status:` and audience
- License summary
- Source / provenance summary
- Whether AI assistance was used

## Review expectations

- [ ] `validate_pack` passes
- [ ] License is clear and acceptable
- [ ] Text quality is appropriate for the status
- [ ] Quiz questions match the text (if present)
- [ ] No duplicate edition ids
- [ ] Manifest regenerated (not hand-edited)
- [ ] Assets (if present) match the asset specs

## Code of conduct

Be respectful. Disputed works are rejected or kept at `status: experimental`. AlephBits moderators have final say on featuring and promotion.

## Questions

Open a GitHub issue in this repository or the main [alephbits](https://github.com/alephbits/alephbits) app repository.
