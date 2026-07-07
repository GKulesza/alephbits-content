<<<<<<< HEAD
# AlephBits Content

The official open content repository for [AlephBits](https://github.com/alephbits/alephbits) — a calm, private reading library for discovering new writing systems through real books.

This repository holds **Reading Packs**: curated texts with metadata, licenses, optional quizzes, and editorial provenance. The AlephBits app syncs from this repository; packs are not buried inside the app binary.

## What lives here

| Directory | Purpose |
|-----------|---------|
| `official/` | AlephBits Editorial packs — full quality bar, provenance required |
| `community/` | Contributor packs — PR review, license required |
| `experimental/` | Drafts and prototypes — hidden unless explicitly enabled |
| `schemas/` | JSON Schema validation contracts |
| `scripts/` | `validate_pack` CLI and future tooling |
| `docs/` | Repository philosophy and future sync design |

## Repository philosophy

- **Books, not files** — A pack is a small book with a title page, not a disposable lesson fixture.
- **Transparent editorial** — Sources, licenses, AI assistance, and human review are visible.
- **Trust before scale** — Official packs never ship on uncertain public-domain status.
- **Platform, not storage** — The repository manifest describes shelves, categories, and discovery — not just a folder tree.
- **Graduated exposure** — `experimental/` → `community/` → `official/` promotion path.

## Editorial philosophy

AlephBits Editorial treats every pack as a reading invitation:

1. The text must reward reading on its own — conversion enhances, never replaces.
2. Native reading (without script conversion) is always valid.
3. Quizzes check comprehension gently; they are optional companions, not exams.
4. Provenance answers *where did this text come from?* for every official pack.
5. Categories grow in data — new genres do not require app releases.

See the main app docs for the full editorial playbook: [EDITORIAL_PLAYBOOK.md](https://github.com/alephbits/alephbits/blob/main/docs/content/EDITORIAL_PLAYBOOK.md).

## How packs are reviewed

### Official (`official/`)

- Two-human review before merge
- `license.md` and `provenance.json` required
- Must pass `validate_pack` CI
- Fact-checking and license verification for adapted works

### Community (`community/`)

- PR review checks schema, license, and basic quality
- Contributor maintains their pack; AlephBits moderates
- Not featured by default

### Experimental (`experimental/`)

- Minimal bar — schema validity only
- Not featured; may break conventions
- Promotion to community or official requires full review

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

Quick start for your first pack:

1. Fork this repository.
2. Copy the structure from `official/glagolitic/pl/spacer-po-krakowie/`.
3. Place community packs under `community/<your-handle>/<slug>/`.
4. Run validation locally:

```bash
dart pub get
dart run scripts/validate_pack.dart
```

5. Open a PR. CI runs the same validation automatically.

## Manifest

`manifest.json` at the repository root is the library catalog. It indexes every pack, category, and featured collection. See [docs/MANIFEST.md](docs/MANIFEST.md) for field documentation.

## Validation

```bash
dart pub get
dart run scripts/validate_pack.dart
```

The validator checks:

- Required files (`lesson.json`, `license.md`, `provenance.json` for official)
- Schema structural validity
- Duplicate pack IDs
- `text.txt` / `quiz.json` consistency with `lesson.json`
- Manifest references to existing pack paths
- Quiz answer integrity

## App integration

The AlephBits app references this repository via a sibling checkout symlinked at `alephbits/alephbits-content`. Future releases will sync packs from the repository manifest with selective download.

## License

Repository structure and tooling: MIT — see [LICENSE](LICENSE).

Individual packs carry their own licenses in `license.md`. Always check per-pack terms before redistribution.

## Related documents

- [Reading Pack Specification](https://github.com/alephbits/alephbits/blob/main/docs/content/READING_PACK_SPECIFICATION.md)
- [Delta update philosophy](docs/DELTA_UPDATES.md)
- [Manifest field reference](docs/MANIFEST.md)
- [Validation policy](docs/VALIDATION_POLICY.md)
=======
# alephbits-content
Official Reading Pack library for AlephBits. Multilingual educational content with transparent sources and editorial metadata.
>>>>>>> 74e434635b761147a697a0605c848a2aaa92ee52
