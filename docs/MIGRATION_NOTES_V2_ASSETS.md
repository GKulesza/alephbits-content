# Content Model v2 — Asset Ownership

## Summary

Part 3 completes visual asset ownership:

| Asset | Owner | Override |
|-------|-------|----------|
| `cover.webp` | `books/<book_id>/default/` | `books/<book_id>/<locale>/` |
| `vignette.webp` | `books/<book_id>/default/` | `books/<book_id>/<locale>/` |

## Resolve order

1. Locale language-tagged file (`cover.pl.webp`)
2. Default language-tagged file
3. Locale shared file (`cover.webp`)
4. Book default file (`default/cover.webp`)
5. Fallback: stock `covers/catalog.json` family (covers only) or none (vignettes)

## App

- `lib/content/book_asset_locator.dart` — shared locator
- Library shelf prefers book `cover.webp` before catalog stock art
- Bundle + remote sync fetch both cover and vignette candidates
- Obsolete custom cover ids removed from `CoverResolver`

## Content

- Validator skips catalog family requirements when `cover.webp` exists
- Custom cover id checks removed
- Fixture: `books/b3eu1z0s/default/{cover,vignette}.webp`
