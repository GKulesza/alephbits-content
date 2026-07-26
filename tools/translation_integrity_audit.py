#!/usr/bin/env python3
"""Translation Integrity Audit.

Verifies data consistency across every edition (locale) of the same
canonical Book in the alephbits-content repository.

Checks:
  - Structural metadata that must match across editions of one book
    (bookId, category/coverFamily, author, unlock/progression requirements,
     tier, difficulty, estimatedReadingTime, tags, ordering/featured flags,
     cover artwork, illustration/audio references).
  - Only localized fields (title, subtitle, description, body text, quiz,
    table of contents) are expected to differ.
  - Asset reachability: manifest entries, lesson.json / quiz.json /
    provenance.json presence, cover family existence in covers/catalog.json.
  - Cross-edition validation: every edition belongs to an existing
    canonical Book (book.yaml), no orphan editions, no duplicate edition
    ids, valid locale codes, every edition reachable from manifest.

Produces a Markdown report. Can optionally auto-fix a small set of safe,
unambiguous inconsistencies (see --fix).
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOKS_DIR = REPO_ROOT / "books"
MANIFEST_PATH = REPO_ROOT / "manifest.json"
COVERS_CATALOG_PATH = REPO_ROOT / "covers" / "catalog.json"

# Fields that must be IDENTICAL across every edition of the same book.
# (Structural metadata — anything not explicitly "localized".)
STRUCTURAL_FIELDS = [
    "bookId",
    "coverFamily",          # category / cover artwork family
    "author",
    "recommendedWritingSystem",  # unlock requirement (writing system)
    "recommendedProfile",        # unlock requirement (profile)
    "recommendedLevel",          # unlock requirement (progression)
    "trustClassification",       # product tier / trust surface
    "audience",
    "difficulty",                 # reading difficulty
    "estimatedReadingTime",       # estimated reading time
    "tags",                       # tags (order-insensitive compare)
    "world",                      # illustration/world references
]

# Fields that are EXPECTED to vary between editions (localized fields).
LOCALIZED_FIELDS = {
    "title",
    "subtitle",
    "description",
    "text",
    "quiz",
    "translation",
    "language",
    "locale",
    "id",
    "generatedFrom",
    "generatedBy",
    "version",
    "editionVersion",
    "updated",
    "editorialHistory",
    "inspirationDates",
    "legacyPackId",
    "legacySlug",
    "license",
}

VALID_LOCALE_RE_PARTS = {
    "en", "pl", "es", "eo", "isv", "isv_cyrl", "isv_glag",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml_simple(path: Path) -> dict[str, Any]:
    """Minimal YAML parser sufficient for book.yaml's flat key/list format."""
    data: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith("  - "):
            if current_list_key:
                data.setdefault(current_list_key, []).append(
                    line.strip()[2:].strip().strip('"')
                )
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                current_list_key = key
                data[key] = []
            else:
                current_list_key = None
                data[key] = value.strip('"')
    return data


class Report:
    def __init__(self) -> None:
        self.metadata_mismatches: list[str] = []
        self.missing_assets: list[str] = []
        self.orphan_editions: list[str] = []
        self.duplicate_edition_ids: list[str] = []
        self.invalid_locales: list[str] = []
        self.unreachable_editions: list[str] = []
        self.other_issues: list[str] = []
        self.fixes_applied: list[str] = []

    def has_issues(self) -> bool:
        return any(
            [
                self.metadata_mismatches,
                self.missing_assets,
                self.orphan_editions,
                self.duplicate_edition_ids,
                self.invalid_locales,
                self.unreachable_editions,
                self.other_issues,
            ]
        )


def normalize_for_compare(value: Any) -> Any:
    if isinstance(value, list):
        try:
            return sorted(value)
        except TypeError:
            return value
    return value


def audit(fix: bool) -> Report:
    report = Report()

    manifest = load_json(MANIFEST_PATH)
    manifest_packs: dict[str, dict[str, Any]] = {p["id"]: p for p in manifest.get("packs", [])}
    manifest_ids = set(manifest_packs.keys())
    supported_languages = set(manifest.get("supportedLanguages", []))

    covers_catalog = {}
    if COVERS_CATALOG_PATH.exists():
        try:
            covers_catalog = load_json(COVERS_CATALOG_PATH)
        except Exception:
            covers_catalog = {}
    known_cover_families: set[str] = set()
    if isinstance(covers_catalog, dict):
        known_cover_families = set(covers_catalog.get("families", covers_catalog.keys()))

    # --- Discover book dirs and their editions on disk ---
    book_dirs = sorted(d for d in BOOKS_DIR.iterdir() if d.is_dir())
    disk_edition_ids: set[str] = set()
    book_editions: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)  # bookId -> locale -> lesson data
    book_yaml_data: dict[str, dict[str, Any]] = {}

    for book_dir in book_dirs:
        book_id = book_dir.name
        book_yaml_path = book_dir / "book.yaml"
        if not book_yaml_path.exists():
            report.other_issues.append(f"{book_id}: missing book.yaml (no canonical Book record)")
            continue
        book_yaml = load_yaml_simple(book_yaml_path)
        book_yaml_data[book_id] = book_yaml
        declared_book_id = book_yaml.get("book_id", "").strip()
        if declared_book_id and declared_book_id != book_id:
            report.other_issues.append(
                f"{book_id}: book.yaml book_id '{declared_book_id}' != directory name"
            )

        locale_dirs = sorted(
            d for d in book_dir.iterdir() if d.is_dir() and d.name != "default"
        )
        for locale_dir in locale_dirs:
            locale = locale_dir.name
            edition_id = f"{book_id}:{locale}"
            disk_edition_ids.add(edition_id)

            # locale validity
            if locale not in VALID_LOCALE_RE_PARTS and locale not in supported_languages:
                report.invalid_locales.append(f"{edition_id}: locale '{locale}' not in supportedLanguages")

            lesson_path = locale_dir / "lesson.json"
            quiz_path = locale_dir / "quiz.json"
            provenance_path = locale_dir / "provenance.json"
            reading_pack_path = locale_dir / "reading-pack.md"
            license_path = locale_dir / "license.md"
            text_path = locale_dir / "text.txt"

            for required, label in [
                (lesson_path, "lesson.json"),
                (reading_pack_path, "reading-pack.md"),
            ]:
                if not required.exists():
                    report.missing_assets.append(f"{edition_id}: missing {label}")

            for optional, label in [
                (quiz_path, "quiz.json"),
                (provenance_path, "provenance.json"),
                (license_path, "license.md"),
                (text_path, "text.txt"),
            ]:
                if not optional.exists():
                    report.missing_assets.append(f"{edition_id}: missing {label} (expected sibling asset)")

            if not lesson_path.exists():
                continue
            try:
                lesson = load_json(lesson_path)
            except Exception as exc:  # noqa: BLE001
                report.other_issues.append(f"{edition_id}: lesson.json parse error ({exc})")
                continue
            book_editions[book_id][locale] = lesson

            # id / bookId consistency inside lesson.json itself
            if lesson.get("id") != edition_id:
                report.other_issues.append(
                    f"{edition_id}: lesson.json id '{lesson.get('id')}' != expected '{edition_id}'"
                )
            if lesson.get("bookId") != book_id:
                report.other_issues.append(
                    f"{edition_id}: lesson.json bookId '{lesson.get('bookId')}' != directory book_id '{book_id}'"
                )
            if lesson.get("locale") != locale:
                report.other_issues.append(
                    f"{edition_id}: lesson.json locale '{lesson.get('locale')}' != directory locale '{locale}'"
                )

            # provenance cross-check
            if provenance_path.exists():
                try:
                    prov = load_json(provenance_path)
                    if prov.get("packId") != edition_id:
                        report.other_issues.append(
                            f"{edition_id}: provenance.json packId '{prov.get('packId')}' != '{edition_id}'"
                        )
                    if prov.get("bookId") != book_id:
                        report.other_issues.append(
                            f"{edition_id}: provenance.json bookId '{prov.get('bookId')}' != '{book_id}'"
                        )
                except Exception as exc:  # noqa: BLE001
                    report.other_issues.append(f"{edition_id}: provenance.json parse error ({exc})")

            # cover family known?
            cover_family = lesson.get("coverFamily")
            if known_cover_families and cover_family and cover_family not in known_cover_families:
                report.missing_assets.append(
                    f"{edition_id}: coverFamily '{cover_family}' not found in covers/catalog.json"
                )

    # --- Duplicate edition ids in manifest ---
    seen_ids: dict[str, int] = defaultdict(int)
    for pack in manifest.get("packs", []):
        seen_ids[pack["id"]] += 1
    for edition_id, count in seen_ids.items():
        if count > 1:
            report.duplicate_edition_ids.append(f"{edition_id}: appears {count} times in manifest.packs")

    # --- Orphan editions: on disk but not in manifest, or in manifest but no book.yaml ---
    for edition_id in sorted(disk_edition_ids):
        if edition_id not in manifest_ids:
            report.unreachable_editions.append(
                f"{edition_id}: exists on disk but missing from manifest.json packs[]"
            )
    for edition_id in sorted(manifest_ids):
        book_id, _, locale = edition_id.partition(":")
        if book_id not in book_yaml_data:
            report.orphan_editions.append(
                f"{edition_id}: listed in manifest but book '{book_id}' has no book.yaml (no canonical Book)"
            )
        elif edition_id not in disk_edition_ids:
            report.unreachable_editions.append(
                f"{edition_id}: listed in manifest but missing on-disk edition directory"
            )

    # --- Structural metadata consistency per book ---
    for book_id, editions in sorted(book_editions.items()):
        if len(editions) < 2:
            continue
        locales = sorted(editions.keys())
        baseline_locale = locales[0]
        baseline = editions[baseline_locale]
        for locale in locales[1:]:
            lesson = editions[locale]
            for field in STRUCTURAL_FIELDS:
                base_val = normalize_for_compare(baseline.get(field))
                other_val = normalize_for_compare(lesson.get(field))
                if base_val != other_val:
                    report.metadata_mismatches.append(
                        f"{book_id}: field '{field}' differs — "
                        f"{baseline_locale}={base_val!r} vs {locale}={other_val!r}"
                    )

        # featured flag / ordering consistency comes from manifest, check there too
        featured_vals = {}
        for locale in locales:
            pack = manifest_packs.get(f"{book_id}:{locale}")
            if pack is not None:
                featured_vals[locale] = pack.get("featured")
        distinct = set(featured_vals.values())
        if len(distinct) > 1:
            report.metadata_mismatches.append(
                f"{book_id}: manifest 'featured' flag differs across editions — {featured_vals}"
            )

    # --- Auto-fix safe inconsistencies ---
    if fix:
        _apply_safe_fixes(report, book_editions, manifest_packs)

    return report


def _apply_safe_fixes(
    report: Report,
    book_editions: dict[str, dict[str, dict[str, Any]]],
    manifest_packs: dict[str, dict[str, Any]],
) -> None:
    """Fix only unambiguous, low-risk inconsistencies:

    - Copy structural metadata from the book's default_locale edition onto
      other editions when they differ (source of truth = default locale).
    - Does NOT touch localized fields, ids, or text.
    """
    for book_id, editions in sorted(book_editions.items()):
        if len(editions) < 2:
            continue
        book_yaml_path = BOOKS_DIR / book_id / "book.yaml"
        default_locale = "pl"
        if book_yaml_path.exists():
            yaml_data = load_yaml_simple(book_yaml_path)
            default_locale = yaml_data.get("default_locale", "pl")
        if default_locale not in editions:
            continue
        source = editions[default_locale]
        for locale, lesson in editions.items():
            if locale == default_locale:
                continue
            changed = False
            for field in STRUCTURAL_FIELDS:
                if field in ("bookId",):
                    continue  # never rewrite identity fields automatically
                src_val = source.get(field)
                cur_val = lesson.get(field)
                if normalize_for_compare(src_val) != normalize_for_compare(cur_val) and src_val is not None:
                    lesson[field] = src_val
                    changed = True
                    report.fixes_applied.append(
                        f"{book_id}:{locale}: field '{field}' set to match "
                        f"{default_locale} edition ({src_val!r})"
                    )
            if changed:
                lesson_path = BOOKS_DIR / book_id / locale / "lesson.json"
                lesson_path.write_text(
                    json.dumps(lesson, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )


def render_report(report: Report) -> str:
    lines = ["# Translation Integrity Audit Report", ""]
    lines.append(f"**Generated by:** `tools/translation_integrity_audit.py`")
    lines.append("")

    def section(title: str, items: list[str]) -> None:
        lines.append(f"## {title} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("None found.")
        else:
            for item in sorted(items):
                lines.append(f"- {item}")
        lines.append("")

    section("Metadata mismatches (structural fields differing across editions)", report.metadata_mismatches)
    section("Missing assets", report.missing_assets)
    section("Orphan editions (no canonical Book)", report.orphan_editions)
    section("Duplicate edition IDs", report.duplicate_edition_ids)
    section("Invalid locale codes", report.invalid_locales)
    section("Unreachable / unregistered editions", report.unreachable_editions)
    section("Other issues", report.other_issues)

    lines.append("## Fixes applied")
    lines.append("")
    if report.fixes_applied:
        for item in report.fixes_applied:
            lines.append(f"- {item}")
    else:
        lines.append("None — no fixes were applied in this run.")
    lines.append("")

    lines.append("## Recommendations before translating the remaining library")
    lines.append("")
    lines.append(
        "1. Treat the book's `default_locale` edition as the source of truth for all "
        "structural (non-localized) fields; new translations should copy these fields "
        "verbatim rather than re-authoring them.\n"
    )
    lines.append(
        "2. Add a CI check (this script, `--check` mode) to the translation batch "
        "workflow described in `docs/product/MULTILINGUAL_TRANSLATION_PILOT.md`, "
        "run after `compile_pack` + `build_manifest` + before `bundle_content_assets`.\n"
    )
    lines.append(
        "3. Extend `lesson.json` schema validation (`schemas/lesson.json`) to reject "
        "structural-field drift between editions of the same `bookId` at compile time, "
        "not just at audit time.\n"
    )
    lines.append(
        "4. Keep `featured` / ordering flags on the *book*, not per-edition, in a future "
        "manifest schema revision — today they must be manually kept in sync per edition.\n"
    )
    lines.append(
        "5. Re-run this audit after resolving flagged items, then proceed with the "
        "remaining category batches from the pilot plan.\n"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply safe auto-fixes (copy structural fields from default_locale edition).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any issues are found (CI mode). Implies no --fix.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "docs" / "TRANSLATION_INTEGRITY_AUDIT_REPORT.md",
        help="Where to write the Markdown report.",
    )
    args = parser.parse_args()

    report = audit(fix=args.fix and not args.check)
    rendered = render_report(report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(rendered)

    if args.check and report.has_issues():
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
