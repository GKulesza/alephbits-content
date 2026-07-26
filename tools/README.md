# Tools

## Living (use these)

| Script | Purpose |
|--------|---------|
| `compile_pack.dart` | Compile `reading-pack.md` → pack artifacts |
| `build_manifest.dart` | Regenerate root `manifest.json` |
| `../scripts/validate_pack.dart` | Full repository validation |

```bash
dart run tools/compile_pack.dart --overwrite official/glagolitic/pl/<slug>
dart run tools/build_manifest.dart --overwrite
dart run scripts/validate_pack.dart
```

## Historical one-shots

`phase*.py`, `phase*.json`, `migrate_*.py`, and similar scripts are **spent import/repair tooling**. Keep them for archaeology; do not run them against production content without a dedicated recovery plan. Prefer the living CLIs above for day-to-day work.
