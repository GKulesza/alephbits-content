# Content Model v2 — Book vs Edition Identity

## Summary

Part 1 completes the identity model so one book can have many locales without further structural changes.

| Concept | Meaning | Example |
|---------|---------|---------|
| **Book** | Permanent work identity | `omqigct2` (`books/omqigct2/`) |
| **Edition** | One locale of a book | `pl` under `books/omqigct2/pl/` |
| **Edition id / content id** | Durable progress & sync key | `omqigct2:pl` |

Format: `{book_id}:{locale}` (primary language subtag).

## Subsystem ownership

| Subsystem | Uses |
|-----------|------|
| Repository folders | `book_id` |
| `book.yaml` | `book_id` |
| Manifest `packs[].bookId` | `book_id` |
| Manifest `packs[].id` | **edition id** |
| Bundle / sync / cache paths | edition path (`books/<book_id>/<locale>/`) |
| Sync version map keys | **edition id** |
| Library shelf card | one row per **book_id** (selected edition for display/open) |
| Library favorites | **book_id** |
| Cover seed | **book_id** |
| Reader open / sessions / attempts / verified / analytics | **edition id** |
| Studies `book:` | **book_id** |
| Study edition resolution | interface language → fallback chain → default |
| Start Here badge | **book_id** (`hgp8iy3x`) |

## Compatibility

On load, the app remaps:

- `polish_*` legacy pack ids → edition id
- bare `book_id` (from the intermediate v2 migration) → edition id
- favorite ids → `book_id`

## Adding locales

To add `en` / `es` / `ja` for an existing book:

1. Create `books/<book_id>/<locale>/` with `reading-pack.md` (+ optional assets).
2. Compile (`compile_pack`) — do **not** hand-author `quiz.json`.
3. Rebuild the manifest / app bundle.
4. No schema or app architecture changes required.

Validation allows multiple editions per `book_id` and rejects duplicate `(book_id, locale)` pairs.

## Files of note

- Content: `lib/content/edition_identity.dart`, compiler, manifest builder, validator
- App: `lib/content/content_identity.dart`, library grouping, study edition picker, progress remapper
