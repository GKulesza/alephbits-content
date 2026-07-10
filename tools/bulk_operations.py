#!/usr/bin/env python3
"""Bulk editorial operations on official reading packs (dry-run by default)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "manifest.json"

FIELD_ALIASES = {
    "audience": "Audience",
    "cover_family": "Cover family",
    "edition_version": "Edition version",
    "version": "Version",
    "trust": "Trust classification",
    "subtitle": "Subtitle",
}

AUDIENCE_IDS = {"child", "family", "teen", "adult"}


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def official_pack_dirs(manifest: dict) -> list[Path]:
    dirs: list[Path] = []
    for entry in manifest.get("packs", []):
        if entry.get("tier") != "official":
            continue
        pack_dir = REPO_ROOT / entry["path"]
        if pack_dir.exists():
            dirs.append(pack_dir)
    return dirs


def replace_metadata_field(text: str, field: str, value: str) -> str:
    pattern = rf"(\*\*{re.escape(field)}:\*\*\s*)(.*)"
    if re.search(pattern, text):
        return re.sub(pattern, lambda m: f"{m.group(1)}{value}", text, count=1)
    marker = "## Metadata"
    if marker not in text:
        raise ValueError("reading-pack.md missing Metadata section")
    return text.replace(marker, f"{marker}\n\n**{field}:** {value}", 1)


def replace_transparency_field(text: str, field: str, value: str) -> str:
    pattern = rf"(\*\*{re.escape(field)}:\*\*\s*)(.*)"
    if re.search(pattern, text):
        return re.sub(pattern, lambda m: f"{m.group(1)}{value}", text, count=1)
    marker = "## Editorial Transparency"
    if marker not in text:
        raise ValueError("reading-pack.md missing Editorial Transparency section")
    return text.replace(marker, f"{marker}\n\n**{field}:** {value}", 1)


def bump_semver(version: str, part: str) -> str:
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def cmd_metadata(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    field = FIELD_ALIASES[args.field]
    changed = 0
    for pack_dir in official_pack_dirs(manifest):
        if args.slug and pack_dir.name not in args.slug:
            continue
        md_path = pack_dir / "reading-pack.md"
        text = md_path.read_text(encoding="utf-8")
        if field == "Trust classification":
            updated = replace_transparency_field(text, field, args.value)
        else:
            updated = replace_metadata_field(text, field, args.value)
        if updated != text:
            changed += 1
            print(f"{'[dry-run] ' if args.dry_run else ''}update {pack_dir.name}: {field} -> {args.value}")
            if not args.dry_run:
                md_path.write_text(updated, encoding="utf-8")
    print(f"{'Would update' if args.dry_run else 'Updated'} {changed} pack(s). Re-run compile_pack + build_manifest.")
    return 0


def cmd_category_rename(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    categories = manifest.get("categories", [])
    found = False
    for cat in categories:
        if cat.get("id") == args.from_id:
            cat["id"] = args.to_id
            if args.label:
                cat["label"] = args.label
            found = True
            break
    if not found:
        print(f"Category id not found: {args.from_id}", file=sys.stderr)
        return 1

    pack_updates = 0
    for pack_dir in official_pack_dirs(manifest):
        md_path = pack_dir / "reading-pack.md"
        text = md_path.read_text(encoding="utf-8")
        updated = re.sub(
            rf"(\*\*Genres:\*\*\s*)(.*\b){re.escape(args.from_id)}(\b.*)",
            rf"\1\2{args.to_id}\3",
            text,
        )
        if updated != text:
            pack_updates += 1
            print(f"{'[dry-run] ' if args.dry_run else ''}genre rename in {pack_dir.name}")
            if not args.dry_run:
                md_path.write_text(updated, encoding="utf-8")

    print(f"{'Would update' if args.dry_run else 'Updated'} manifest category + {pack_updates} pack(s).")
    if not args.dry_run:
        manifest["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


def cmd_audience(args: argparse.Namespace) -> int:
    if args.audience not in AUDIENCE_IDS:
        print(f"Audience must be one of: {', '.join(sorted(AUDIENCE_IDS))}", file=sys.stderr)
        return 1
    args.field = "audience"
    args.value = args.audience
    return cmd_metadata(args)


def cmd_edition_bump(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    changed = 0
    for pack_dir in official_pack_dirs(manifest):
        if args.slug and pack_dir.name not in args.slug:
            continue
        md_path = pack_dir / "reading-pack.md"
        text = md_path.read_text(encoding="utf-8")
        m = re.search(r"\*\*Edition version:\*\*\s*([0-9]+\.[0-9]+\.[0-9]+)", text)
        if not m:
            print(f"skip {pack_dir.name}: no Edition version", file=sys.stderr)
            continue
        new_version = bump_semver(m.group(1), args.part)
        updated = replace_metadata_field(text, "Edition version", new_version)
        if updated != text:
            changed += 1
            print(f"{'[dry-run] ' if args.dry_run else ''}{pack_dir.name}: {m.group(1)} -> {new_version}")
            if not args.dry_run:
                md_path.write_text(updated, encoding="utf-8")
    print(f"{'Would bump' if args.dry_run else 'Bumped'} {changed} pack(s). Re-run compile_pack + build_manifest.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes (default is dry-run)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    metadata = sub.add_parser("metadata", help="Bulk edit a Metadata / Transparency field")
    metadata.add_argument("field", choices=sorted(FIELD_ALIASES))
    metadata.add_argument("value")
    metadata.add_argument("--slug", nargs="*", help="Limit to pack slug(s)")
    metadata.set_defaults(func=cmd_metadata)

    category = sub.add_parser("category-rename", help="Rename manifest category id")
    category.add_argument("from_id")
    category.add_argument("to_id")
    category.add_argument("--label")
    category.set_defaults(func=cmd_category_rename)

    audience = sub.add_parser("audience", help="Bulk set Audience metadata")
    audience.add_argument("audience", choices=sorted(AUDIENCE_IDS))
    audience.add_argument("--slug", nargs="*")
    audience.set_defaults(func=cmd_audience)

    edition = sub.add_parser("edition-bump", help="Bump Edition version across packs")
    edition.add_argument("part", choices=["major", "minor", "patch"], default="patch", nargs="?")
    edition.add_argument("--slug", nargs="*")
    edition.set_defaults(func=cmd_edition_bump)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.dry_run = not args.apply
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
