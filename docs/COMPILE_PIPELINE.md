# Compile Pipeline (`compile_pack`)

**Status:** **Implemented** (Phase 25).  
**Phase:** 23 (design) → 25 (implementation)

**Canonical authoring format:** [READING_PACK_AUTHORING_FORMAT.md](https://github.com/alephbits/alephbits/blob/main/docs/content/READING_PACK_AUTHORING_FORMAT.md)

---

## Purpose

`compile_pack` transforms **`reading-pack.md`** (the only editorial source for an edition) into generated runtime artifacts. See [EDITORIAL_OWNERSHIP.md](EDITORIAL_OWNERSHIP.md).

`quiz.json` is **generated**, never hand-edited.

Book visual assets (`cover.webp`, `vignette.webp`) are **not** compiled — they are authored under `default/` (locale may override) and discovered by the app. See [MIGRATION_NOTES_V2_ASSETS.md](MIGRATION_NOTES_V2_ASSETS.md).

---

## Pipeline

```
reading-pack.md (+ book.yaml identity/status)
      │
      ▼
 compile_pack.dart
      │
      ├── lesson.json      GENERATED (runtime monolith)
      ├── text.txt         GENERATED
      ├── quiz.json        GENERATED
      ├── license.md       GENERATED
      ├── provenance.json  GENERATED
      │
      ▼
 validate_pack.dart   (fails if generated files drift)
```

Repository root `manifest.json` is updated separately by `build_manifest.dart`.

---

## CLI (implemented)

```bash
# Compile one locale edition
dart run tools/compile_pack.dart books/hgp8iy3x/pl/

# Flags: --check, --overwrite, --dry-run, --all
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Parse error in reading-pack.md |
| 2 | Compile output fails validate_pack |
| 3 | `--check` drift detected |

---

## Parsing rules

| Section | Parser behavior |
|---------|-----------------|
| **Metadata** | Bold `**Label:** value` lines; tables optional; optional multi-line `**World:**` → `lesson.json` `world` |
| **Editorial Transparency** | Revision table → `provenance.json` |
| **Sources** | Each `### Source N` → `sources[]` entry |
| **Text** | All content until `## Quiz` → `text.txt`; paragraphs joined with `\n\n` |
| **Quiz** | Each `### Question N` → `questions[]`; answers stripped of `A)` prefix |
| **Future Extensions** | Ignored in v1 |

### Optional `world` metadata

When present under Metadata:

```markdown
**World:**
- objects: flashlight, painting
- creatures: green_elephant
- places: forest
```

Compiled into `lesson.json` as:

```json
"world": {
  "objects": ["flashlight", "painting"],
  "creatures": ["green_elephant"],
  "places": ["forest"]
}
```

Missing `world` never fails compile. Invalid ids are skipped.

Shared vocabulary: [world/dictionary.yaml](../world/dictionary.yaml).


### Determinism

- Stable key ordering in JSON output
- UTF-8 NFC normalization for text
- `updated` field: earliest revision date when revision history is present
- Same input file + compiler version → identical output (except configurable timestamp policy)

---

## CI integration (implemented)

```yaml
# .github/workflows/validate.yml
- name: Check compile drift
  run: dart run tools/compile_pack.dart --check --all
- name: Validate packs
  run: dart run scripts/validate_pack.dart
```

Order: **compile --check** then **validate_pack**.

---

## Repository policy

See [READING_PACK_AUTHORING_FORMAT.md — Repository philosophy](https://github.com/alephbits/alephbits/blob/main/docs/content/READING_PACK_AUTHORING_FORMAT.md#repository-philosophy).

**Phase 23 recommendation:** commit `reading-pack.md` + JSON until `--check` is enforced; then JSON may become CI-only artifact.

---

## Related

- [VALIDATION_POLICY.md](VALIDATION_POLICY.md)
- [schemas/](../schemas/)
