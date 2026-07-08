# Repository Manifest

`manifest.json` is the library catalog. The AlephBits app will use it to browse shelves and download packs selectively.

## Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `repositoryVersion` | string (semver) | yes | Version of the catalog as a whole. Bump on collection releases. |
| `schemaVersion` | string | yes | Manifest schema contract version. Increment when field shapes change. |
| `minimumAppVersion` | string (semver) | yes | Lowest AlephBits app version that can consume this manifest. |
| `generatedAt` | string (ISO 8601) | yes | Derived from the newest pack `updated` date — deterministic, not wall-clock time. |
| `officialPackCount` | integer | yes | Count of packs with `tier: "official"`. Must match indexed packs. |
| `communityPackCount` | integer | yes | Count of packs with `tier: "community"`. |
| `experimentalPackCount` | integer | yes | Count of packs with `tier: "experimental"`. |
| `supportedLanguages` | string[] | yes | BCP 47 codes with at least one published pack. |
| `supportedWritingSystems` | string[] | yes | Writing system IDs matching AlephBits engine assets. |
| `categories` | object[] | yes | Discovery categories (genres) available in the library. |
| `featuredCollections` | object[] | yes | Curated shelves for discovery surfaces. |
| `packs` | object[] | yes | Flat index of every published pack. |
| `libraryStatistics` | object | yes | Aggregate metrics: word counts, reading time, largest/newest/oldest pack. |

## Category object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Stable snake_case identifier (`travel`, `short_story`). |
| `title` | string | yes | Human-readable category name. |
| `description` | string | no | Short explanation for editors and discovery UI. |

## Featured collection object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Stable shelf identifier. |
| `title` | string | yes | Shelf title shown to readers. |
| `description` | string | no | Shelf subtitle or curator note. |
| `packIds` | string[] | yes | Pack IDs on this shelf. Every ID must exist in `packs`. |

## Pack entry object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Pack ID matching `lesson.json` `id`. Unique repository-wide. |
| `bookId` | string | yes | Stable book identifier across language variants. |
| `path` | string | yes | Repository-relative path to the pack directory. |
| `tier` | string | yes | `official`, `community`, or `experimental`. |
| `writingSystem` | string | yes | Target script ID (`glagolitic`, `hiragana`, …). |
| `language` | string | yes | BCP 47 source language of this variant. |
| `title` | string | yes | Reader-facing title for this language variant. |
| `version` | string | yes | Semver of this pack variant. |
| `categories` | string[] | no | Category IDs from `categories`. |
| `difficulty` | integer 1–10 | no | Estimated reading difficulty. |
| `estimatedReadingTime` | integer | no | Estimated minutes to read. |
| `featured` | boolean | no | Whether to highlight in discovery (default false). |

## Future fields (not yet implemented)

| Field | Purpose |
|-------|---------|
| `sha256` per pack | Integrity verification on download |
| `sizeBytes` | Download size hints |
| `deprecated` | Soft-removal without breaking installed packs |
| `featuredDiscoveryModes` | `random`, `short_reads`, etc. |

See [DELTA_UPDATES.md](DELTA_UPDATES.md) for how manifest diffs will drive selective sync.

## JSON Schema

Machine-readable contract: [`schemas/manifest.json`](../schemas/manifest.json).

## Regeneration

**`manifest.json` is generated — never edit by hand.**

```bash
dart run tools/build_manifest.dart --overwrite
dart run tools/build_manifest.dart --check   # CI drift detection
```

`validate_pack` fails when the committed manifest differs from `build_manifest` output or when packs on disk are missing from the index.

Category vocabulary and featured-shelf templates live in `lib/manifest/catalog.dart` — edit there when adding new discovery categories or shelves.
