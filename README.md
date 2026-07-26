# AlephBits Content

The official open content repository for [AlephBits](https://github.com/alephbits/alephbits) — a calm, private reading library for discovering new writing systems through real books.

This repository holds **Reading Packs** under Content Model v2: curated texts with metadata, licenses, optional quizzes, vignettes, and editorial provenance. The AlephBits app syncs from this repository; packs are not buried inside the app binary.

## What lives here

| Directory | Purpose |
|-----------|---------|
| `books/` | **Canonical packs** — `books/<book_id>/<locale>/` editions + `book.yaml` + optional `default/` art |
| `studies/` | Optional experiment scenarios that reference existing books |
| `world/` | World Dictionary — shared vocabulary for pack `world` metadata |
| `covers/` | Temporary stock cover-family catalog (fallback until book-owned covers ship) |
| `schemas/` | JSON Schema validation contracts |
| `scripts/` | `validate_pack` and related validation |
| `tools/` | Living CLIs (`compile_pack`, `build_manifest`, optional bulk ops) |
| `docs/` | Repository docs — see [docs/README.md](docs/README.md) |
| `community/`, `experimental/` | Reserved tier markers (packs live under `books/` with `book.yaml` `status:`) |
| `official/starter-shelf/` | Historical category planning notes only — not pack paths |

## Content Model v2 (identity)

| Concept | Identity | Example |
|---------|----------|---------|
| Book | permanent `book_id` | `hgp8iy3x` |
| Edition | locale under book | `pl` |
| Content / pack id | `{book_id}:{locale}` | `hgp8iy3x:pl` |

Layout:

```text
books/<book_id>/
├── book.yaml              # identity + status only
├── default/               # shared cover.webp / vignette.webp
└── <locale>/
    ├── reading-pack.md    # SOURCE — edit this
    ├── lesson.json        # GENERATED
    ├── quiz.json          # GENERATED
    └── …
```

See [docs/EDITORIAL_OWNERSHIP.md](docs/EDITORIAL_OWNERSHIP.md), [docs/CONTENT_MODEL_DEFINITIONS.md](docs/CONTENT_MODEL_DEFINITIONS.md), [docs/MIGRATION_NOTES_V2.md](docs/MIGRATION_NOTES_V2.md), and [docs/METADATA_MODEL.md](docs/METADATA_MODEL.md).

## Repository philosophy

- **Books, not files** — A pack is a small book with a title page, not a disposable lesson fixture.
- **Transparent editorial** — Sources, licenses, AI assistance, and human review are visible.
- **Trust before scale** — Official packs never ship on uncertain public-domain status.
- **Platform, not storage** — The repository manifest describes shelves, categories, and discovery — not just a folder tree.
- **Graduated exposure** — `experimental` → `community` → `official` via `book.yaml` `status:`.

## Editorial philosophy

1. The text must reward reading on its own — conversion enhances, never replaces.
2. Native reading (without script conversion) is always valid.
3. Quizzes check comprehension gently; they are optional companions, not exams.
4. Provenance answers *where did this text come from?* for every official pack.
5. Categories grow in data — new genres do not require app releases.

Full editorial playbook (app repo): [EDITORIAL_PLAYBOOK.md](https://github.com/alephbits/alephbits/blob/main/docs/content/EDITORIAL_PLAYBOOK.md).

## How packs are reviewed

### Official (`status: official`)

- Two-human review before merge
- `license.md` and `provenance.json` required (generated from manuscript)
- Must pass `validate_pack` CI
- Fact-checking and license verification for adapted works

### Community (`status: community`)

- PR review checks schema, license, and basic quality
- Contributor maintains their pack; AlephBits moderates
- Not featured by default

### Experimental (`status: experimental`)

- Minimal bar — schema validity only
- Not featured; may break conventions
- Promotion to community or official requires full review

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

**Author in Markdown:** copy [docs/reading-pack.template.md](docs/reading-pack.template.md), fill sections, then:

```bash
dart run tools/compile_pack.dart --overwrite books/<book_id>/<locale>
dart run tools/build_manifest.dart --overwrite
dart run scripts/validate_pack.dart
```

Quick start:

1. Fork this repository.
2. Create `books/<book_id>/` (permanent id) with `book.yaml` and a locale folder; copy from `books/hgp8iy3x/pl/` as a structural example.
3. Set `status:` in `book.yaml` (`experimental` / `community` / `official`).
4. Validate and open a PR. CI runs the same validation.

## Manifest

`manifest.json` at the repository root is the **generated** library catalog. Never edit it by hand — regenerate with `dart run tools/build_manifest.dart --overwrite`. See [docs/MANIFEST.md](docs/MANIFEST.md).

## Validation

```bash
dart pub get
dart run scripts/validate_pack.dart
```

## App integration

The AlephBits app references this repository via a sibling checkout symlinked at `alephbits/alephbits-content`. Production builds pin the GitHub `main` catalog URL.

## License

Repository structure and tooling: MIT — see [LICENSE](LICENSE).

Individual packs carry their own licenses in `license.md`. Always check per-pack terms before redistribution.
