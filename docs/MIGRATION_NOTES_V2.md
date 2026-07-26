# Content Model v2 Migration Notes

## Summary

QuietLibrary now uses a book-first repository layout:

```text
books/<book_id>/
  book.yaml
  default/
  <locale>/
```

This replaces the Collection v1 layout:

```text
official/glagolitic/pl/<slug>/
```

## Architectural changes

### 1. Permanent identity

- Each migrated book now has a permanent random 8-character `book_id`.
- `book_id` is the repository identity and no longer depends on title, slug, locale, or folder name.
- Legacy v1 `Pack ID` values are preserved only for compatibility during application-side progress migration.

### 2. Repository layout

- Books now live under `books/`.
- Shared assets live under `default/`.
- Locale-specific editorial/runtime files live under `<locale>/`.
- Writing system is no longer encoded in the repository path.

### 3. Editorial ownership

See [EDITORIAL_OWNERSHIP.md](EDITORIAL_OWNERSHIP.md).

| File | Role |
|------|------|
| `reading-pack.md` | **Editorial SoT** for the locale edition (prose, quiz, edition metadata) |
| `book.yaml` | **Editorial SoT** for book identity / status only |
| `quiz.json`, `lesson.json`, `text.txt`, `provenance.json`, `license.md` | **Generated** by `compile_pack` — read-only |
| `study.yaml` + `questions.*.json` | **Editorial SoT** for studies (separate from pack quiz) |

### 4. Studies

- `studies/` remains separate from books.
- Study `book:` references were rewritten from legacy pack IDs to v2 `book_id` values.

## Tooling changes

### Discovery

Content discovery now recognizes:

- `books/<book_id>/<locale>/lesson.json`
- legacy v1 tier roots when present

### Manifest generation

- Manifest entries now point at locale directories under `books/`.
- `bookId` is derived from the `books/<book_id>/` directory.
- `tier` comes from `book.yaml` instead of path segments.

### Compiler

- `Book ID` defaults to the `books/<book_id>/` parent when compiling locale content.
- Compiler output now includes v2 identity fields needed by the app migration layer.

### Validation

- Validator accepts v2 `books/` layout.
- Legacy duplicate-slug assumptions no longer apply to locale directories like `pl/`.

## Application changes required by v2

The app was updated to:

- load manifests pointing at `books/<book_id>/<locale>`
- bundle and sync locale files from that layout
- resolve vignette fallbacks from `books/<book_id>/default/`
- migrate legacy reading progress/session identifiers to v2 content IDs

## Migration procedure used

1. Generate deterministic random `book_id` values.
2. Create `books/<book_id>/book.yaml`.
3. Move shared assets to `default/`.
4. Move locale content to `<locale>/`.
5. Rewrite study references to `book_id`.
6. Regenerate locale artifacts.
7. Rebuild `manifest.json`.
8. Rebuild the app content bundle.

## Important compatibility note

The repository identity is now `book_id`. Legacy v1 pack IDs are retained only as compatibility metadata so existing local reader progress can be migrated forward instead of being lost.
