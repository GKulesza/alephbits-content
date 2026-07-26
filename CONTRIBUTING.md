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

```
your-pack/
├── reading-pack.md     # SOURCE — edit this
├── lesson.json         # GENERATED
├── text.txt            # GENERATED
├── quiz.json           # GENERATED
├── license.md          # GENERATED
├── provenance.json     # GENERATED
└── vignette.webp       # OPTIONAL — see vignettes below
```

Copy [docs/reading-pack.template.md](docs/reading-pack.template.md) or `official/glagolitic/pl/spacer-po-krakowie/reading-pack.md`.

### 3. Compile and catalog

```bash
dart pub get
dart run tools/compile_pack.dart --overwrite path/to/your-pack
dart run tools/build_manifest.dart --overwrite
```

Do **not** hand-edit `manifest.json`. See [docs/MANIFEST.md](docs/MANIFEST.md) and [docs/COMPILE_PIPELINE.md](docs/COMPILE_PIPELINE.md).

### 4. Required sections in `reading-pack.md`

- **Metadata** — title, pack id, difficulty, language, genres, cover family
- **Editorial Transparency** — license, AI disclosure, revision history
- **Sources** — every source with license and retrieval date
- **Text** — complete reading prose
- **Quiz** — comprehension questions with explanations (count by length; see app quiz guidelines)

### 5. Optional vignette

A pack may ship a literary title vignette:

```text
vignette.webp            # 512×512 transparent WebP (preferred)
vignette.<lang>.webp     # exceptional language override
```

Symbolic only — not a cover, not typography, not the opening scene.  
Full production rules: [VIGNETTE_ASSET_SPEC.md](https://github.com/alephbits/alephbits/blob/main/docs/content/VIGNETTE_ASSET_SPEC.md) (app repository). Keep source art outside this repo.

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

- Pack tier and intended audience
- License summary
- Source / provenance summary
- Whether AI assistance was used

## Review expectations

- [ ] `validate_pack` passes
- [ ] License is clear and acceptable
- [ ] Text quality is appropriate for the tier
- [ ] Quiz questions match the text (if present)
- [ ] No duplicate pack IDs
- [ ] Manifest regenerated (not hand-edited)
- [ ] Vignette (if present) matches the asset spec

## Code of conduct

Be respectful. Disputed works are rejected or moved to `experimental/`. AlephBits moderators have final say on featuring and promotion.

## Questions

Open a GitHub issue in this repository or the main [alephbits](https://github.com/alephbits/alephbits) app repository.
