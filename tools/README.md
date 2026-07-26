# Tools

Living maintenance CLIs only. Spent phase importers were removed; recover from git history if needed.

| Script | Purpose |
|--------|---------|
| `compile_pack.dart` | Compile `reading-pack.md` → pack artifacts |
| `build_manifest.dart` | Regenerate root `manifest.json` |
| `bulk_operations.py` | Optional bulk metadata edits (dry-run by default) |
| `../scripts/validate_pack.dart` | Full repository validation |

```bash
dart run tools/compile_pack.dart --overwrite books/<book_id>/<locale>
dart run tools/build_manifest.dart --overwrite
dart run scripts/validate_pack.dart
```
