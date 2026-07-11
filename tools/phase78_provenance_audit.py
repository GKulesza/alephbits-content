#!/usr/bin/env python3
"""Phase 78 — audit editorial provenance across official packs."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "official" / "glagolitic" / "pl"

YT_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
YT_URL = re.compile(
    r"(?:[?&]v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})"
)


def extract_ids(value: str) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for part in value.split(","):
        token = part.strip()
        if not token:
            continue
        if YT_ID.match(token):
            if token not in seen:
                seen.add(token)
                ids.append(token)
            continue
        match = YT_URL.search(token)
        if match and match.group(1) not in seen:
            seen.add(match.group(1))
            ids.append(match.group(1))
    return ids


def main() -> None:
    missing_dates: list[str] = []
    missing_inspiration: list[str] = []
    duplicate_ids: list[tuple[str, str]] = []
    malformed_urls: list[tuple[str, str]] = []
    legacy_references: list[str] = []
    legacy_source: list[str] = []
    dup_provenance: list[tuple[str, str]] = []

    for pack_dir in sorted(PACKS.iterdir()):
        slug = pack_dir.name
        lesson_path = pack_dir / "lesson.json"
        if not lesson_path.exists():
            continue
        lesson = json.loads(lesson_path.read_text(encoding="utf-8"))

        dates = lesson.get("inspirationDates") or []
        inspired = lesson.get("inspiredBy") or {}
        youtube_raw = inspired.get("youtube", "") if isinstance(inspired, dict) else ""

        if not dates:
            missing_dates.append(slug)
        if not youtube_raw:
            missing_inspiration.append(slug)

        ids = extract_ids(youtube_raw) if youtube_raw else []
        if youtube_raw:
            raw_parts = [p.strip() for p in youtube_raw.split(",") if p.strip()]
            if len(raw_parts) != len(set(raw_parts)):
                duplicate_ids.append((slug, youtube_raw))
            for part in raw_parts:
                if "http" in part or "youtube" in part.lower():
                    malformed_urls.append((slug, part))
                elif not YT_ID.match(part):
                    malformed_urls.append((slug, part))

        if lesson.get("references"):
            legacy_references.append(slug)
        if lesson.get("source"):
            legacy_source.append(slug)

        prov_path = pack_dir / "provenance.json"
        if prov_path.exists():
            prov = json.loads(prov_path.read_text(encoding="utf-8"))
            seen_prov: set[str] = set()
            for entry in prov.get("sources") or []:
                if entry.get("type") == "youtube":
                    vid = entry.get("videoId", "")
                    if vid in seen_prov:
                        dup_provenance.append((slug, vid))
                    seen_prov.add(vid)
                    if "url" in entry:
                        malformed_urls.append((slug, entry["url"]))

    print("Phase 78 provenance audit\n")
    print(f"Missing inspirationDates: {len(missing_dates)}")
    for slug in missing_dates[:10]:
        print(f"  - {slug}")
    if len(missing_dates) > 10:
        print(f"  ... +{len(missing_dates) - 10} more")

    print(f"\nMissing inspiredBy.youtube: {len(missing_inspiration)}")
    print(f"Duplicate YouTube IDs in lesson: {len(duplicate_ids)}")
    print(f"Malformed URL/id values: {len(malformed_urls)}")
    for slug, value in malformed_urls[:10]:
        print(f"  - {slug}: {value}")
    print(f"Legacy references[] still present: {len(legacy_references)}")
    for slug in legacy_references:
        print(f"  - {slug}")
    print(f"Legacy source field still present: {len(legacy_source)}")
    print(f"Duplicate provenance videoId: {len(dup_provenance)}")

    if malformed_urls or legacy_references or duplicate_ids or dup_provenance:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
