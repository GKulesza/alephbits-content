#!/usr/bin/env python3
"""Migrate Collection v1 layout to Content Model v2."""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import string
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO = Path(__file__).resolve().parents[1]
OLD_ROOT = REPO / "official" / "glagolitic" / "pl"
BOOKS_ROOT = REPO / "books"
ID_ALPHABET = string.ascii_lowercase + string.digits
ID_LEN = 8


def _new_book_id(existing: set[str]) -> str:
    while True:
        candidate = "".join(random.choice(ID_ALPHABET) for _ in range(ID_LEN))
        if candidate[0].isdigit():
            continue
        if candidate not in existing:
            existing.add(candidate)
            return candidate


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump_yaml(data: dict) -> str:
    if yaml is not None:
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)

    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for sub_key, sub_value in value.items():
                lines.append(f"  {sub_key}: {json.dumps(sub_value, ensure_ascii=False)}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {json.dumps(item, ensure_ascii=False)}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        elif value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def _rewrite_reading_pack(md_path: Path, *, book_id: str, legacy_pack_id: str) -> None:
    if not md_path.exists():
        return
    text = md_path.read_text(encoding="utf-8")
    text = re.sub(
        r"(\*\*Pack ID:\*\*\s*).*$",
        rf"\1{book_id}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if "**Book ID:**" in text:
        text = re.sub(
            r"(\*\*Book ID:\*\*\s*).*$",
            rf"\1{book_id}",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        text = re.sub(
            r"(\*\*Pack ID:\*\*.*\n)",
            rf"\1**Book ID:** {book_id}\n**Legacy Pack ID:** {legacy_pack_id}\n",
            text,
            count=1,
            flags=re.MULTILINE,
        )
    md_path.write_text(text, encoding="utf-8")


def _copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _migrate_pack(pack_dir: Path, *, book_id: str, dry_run: bool) -> dict:
    lesson = _load_json(pack_dir / "lesson.json")
    legacy_pack_id = lesson["id"]
    locale = (lesson.get("language") or "pl").split("-")[0].lower()
    slug = pack_dir.name

    book_dir = BOOKS_ROOT / book_id
    default_dir = book_dir / "default"
    locale_dir = book_dir / locale

    book_yaml = {
        "book_id": book_id,
        "created": date.today().isoformat(),
        "status": "official",
        "default_locale": locale,
        "legacy_pack_ids": [legacy_pack_id],
        "legacy_slug": slug,
    }
    if dry_run:
        return {
            "book_id": book_id,
            "legacy_pack_id": legacy_pack_id,
            "slug": slug,
            "locale": locale,
            "from": str(pack_dir.relative_to(REPO)),
            "to": str(book_dir.relative_to(REPO)),
        }

    default_dir.mkdir(parents=True, exist_ok=True)
    locale_dir.mkdir(parents=True, exist_ok=True)
    (book_dir / "book.yaml").write_text(_dump_yaml(book_yaml), encoding="utf-8")

    for name in (
        "reading-pack.md",
        "quiz.json",
        "lesson.json",
        "text.txt",
        "license.md",
        "provenance.json",
        "study.yaml",
    ):
        _copy_if_exists(pack_dir / name, locale_dir / name)

    for name in ("cover.webp", "vignette.webp"):
        _copy_if_exists(pack_dir / name, default_dir / name)

    for src in pack_dir.glob("cover.*.webp"):
        _copy_if_exists(src, locale_dir / src.name)
    for src in pack_dir.glob("vignette.*.webp"):
        _copy_if_exists(src, locale_dir / src.name)

    lesson_path = locale_dir / "lesson.json"
    lesson_out = _load_json(lesson_path)
    lesson_out["id"] = book_id
    lesson_out["bookId"] = book_id
    lesson_out["legacyPackId"] = legacy_pack_id
    lesson_out["legacySlug"] = slug
    lesson_path.write_text(
        json.dumps(lesson_out, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    quiz_path = locale_dir / "quiz.json"
    if not quiz_path.exists() and isinstance(lesson_out.get("quiz"), dict):
        quiz_path.write_text(
            json.dumps(lesson_out["quiz"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    _rewrite_reading_pack(
        locale_dir / "reading-pack.md",
        book_id=book_id,
        legacy_pack_id=legacy_pack_id,
    )

    return {
        "book_id": book_id,
        "legacy_pack_id": legacy_pack_id,
        "slug": slug,
        "locale": locale,
        "from": str(pack_dir.relative_to(REPO)),
        "to": str(book_dir.relative_to(REPO)),
    }


def _rewrite_studies(id_map: dict[str, str], *, dry_run: bool) -> list[dict]:
    changes: list[dict] = []
    studies_root = REPO / "studies"
    if not studies_root.exists():
        return changes

    for study_yaml in studies_root.glob("*/study.yaml"):
        text = study_yaml.read_text(encoding="utf-8")
        match = re.search(r"^book:\s*(\S+)\s*$", text, re.MULTILINE)
        if not match:
            continue
        old_ref = match.group(1)
        new_ref = id_map.get(old_ref)
        if not new_ref:
            continue
        changes.append(
            {"file": str(study_yaml.relative_to(REPO)), "from": old_ref, "to": new_ref}
        )
        if not dry_run:
            new_text = re.sub(
                r"^book:\s*\S+\s*$",
                f"book: {new_ref}",
                text,
                count=1,
                flags=re.MULTILINE,
            )
            study_yaml.write_text(new_text, encoding="utf-8")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--keep-old", action="store_true")
    args = parser.parse_args()
    random.seed(args.seed)

    if not OLD_ROOT.exists():
        print(f"ERROR: missing source tree: {OLD_ROOT}", file=sys.stderr)
        return 1

    packs = sorted(
        path for path in OLD_ROOT.iterdir() if path.is_dir() and (path / "lesson.json").exists()
    )
    if not packs:
        print("ERROR: no packs found", file=sys.stderr)
        return 1

    existing_ids = {path.name for path in BOOKS_ROOT.iterdir()} if BOOKS_ROOT.exists() else set()
    mapping: list[dict] = []
    id_map: dict[str, str] = {}

    print(f"Migrating {len(packs)} packs…")
    for pack_dir in packs:
        book_id = _new_book_id(existing_ids)
        info = _migrate_pack(pack_dir, book_id=book_id, dry_run=args.dry_run)
        mapping.append(info)
        id_map[info["legacy_pack_id"]] = book_id
        print(f"  {info['slug']} -> {book_id}")

    for change in _rewrite_studies(id_map, dry_run=args.dry_run):
        print(f"  study {change['file']}: {change['from']} -> {change['to']}")

    if not args.dry_run:
        docs_dir = REPO / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "content_model_v2_id_map.json").write_text(
            json.dumps(
                {
                    "version": 2,
                    "seed": args.seed,
                    "books": mapping,
                    "legacy_pack_id_to_book_id": id_map,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        if not args.keep_old:
            shutil.rmtree(OLD_ROOT)
            print(f"Removed {OLD_ROOT.relative_to(REPO)}")

    print(f"Done. dry_run={args.dry_run} migrated={len(mapping)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
