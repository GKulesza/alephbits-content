# Compile Pipeline (`compile_pack`)

**Status:** Design only — **not implemented.**  
**Phase:** 23

**Canonical authoring format:** [READING_PACK_AUTHORING_FORMAT.md](https://github.com/alephbits/alephbits/blob/main/docs/content/READING_PACK_AUTHORING_FORMAT.md)

---

## Purpose

`compile_pack` transforms **`reading-pack.md`** (human source) into the JSON and Markdown files the app and validator consume today.

---

## Pipeline

```
reading-pack.md
      │
      ▼
 compile_pack.dart
      │
      ├── lesson.json      (metadata + inline text + quiz — v1 app)
      ├── text.txt         (extracted prose)
      ├── quiz.json        (extracted quiz)
      ├── license.md       (from Editorial Transparency)
      ├── provenance.json  (from Transparency + Sources)
      └── manifest.json    (optional book manifest — single-language v1)
      │
      ▼
 validate_pack.dart
```

Repository root `manifest.json` is updated separately (future: `build_manifest.dart`).

---

## CLI design (future)

```bash
# Compile one pack
dart run scripts/compile_pack.dart official/glagolitic/pl/spacer-po-krakowie/

# Compile all packs with reading-pack.md
dart run scripts/compile_pack.dart --all

# Check mode — fail if JSON drifts from Markdown (CI)
dart run scripts/compile_pack.dart --check official/glagolitic/pl/spacer-po-krakowie/
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
| **Metadata** | Bold `**Label:** value` lines; tables optional |
| **Editorial Transparency** | Revision table → `provenance.json` |
| **Sources** | Each `### Source N` → `sources[]` entry |
| **Text** | All content until `## Quiz` → `text.txt`; paragraphs joined with `\n\n` |
| **Quiz** | Each `### Question N` → `questions[]`; answers stripped of `A)` prefix |
| **Future Extensions** | Ignored in v1 |

### Determinism

- Stable key ordering in JSON output
- UTF-8 NFC normalization for text
- `updated` field: compile date unless **Revision history** specifies otherwise
- Same input file + compiler version → identical output (except configurable timestamp policy)

---

## CI integration (future)

```yaml
# .github/workflows/validate.yml (addition)
- name: Check compile drift
  run: dart run scripts/compile_pack.dart --check --all
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
