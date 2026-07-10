#!/usr/bin/env python3
"""Phase 71 — normalize official reading-pack metadata in place."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "manifest.json"
WORDS_PER_MINUTE = 200

CANONICAL_TRUST = {
    "Fiction",
    "Inspired by reality",
    "Adapted from real events",
    "Popular science",
    "Instruction",
    "Demo",
}

TRUST_MAP = {
    "biography": "Inspired by reality",
    "historical_fiction": "Fiction",
    "history": "Inspired by reality",
    "technology": "Popular science",
    "science": "Popular science",
    "guide": "Instruction",
    "manual / reference": "Instruction",
    "opinion": "Inspired by reality",
    "inspired_by_real_events": "Inspired by reality",
    "fiction": "Fiction",
}

DEFAULT_TRUST_BY_SLUG = {
    "spacer-po-krakowie": "Demo",
    "na-targu": "Fiction",
}

AUDIENCE_MAP = {
    "adult readers": "adult",
    "adult readers, parents": "family",
    "adult beginners": "adult",
    "adult": "adult",
    "child": "child",
    "family": "family",
    "teen": "teen",
}

GENRE_TO_COVER = {
    "biography": "biography",
    "history": "history",
    "popular_science": "popular_science",
    "science": "science",
    "legend": "legend",
    "legends": "legends",
    "instruction": "instruction",
    "short_story": "short_story",
    "travel": "travel",
    "demo": "demo",
    "dialogue": "dialogue",
    "science_fiction": "science_fiction",
    "article": "article",
    "psychology": "psychology",
    "law": "law",
    "nature": "nature",
    "everyday_live": "everyday_live",
    "languages": "languages",
    "fantasy": "fantasy",
    "philosophy": "philosophy",
    "mathematics": "mathematics",
    "medicine": "medicine",
    "economics": "economics",
}

SUBTITLE_FIXES = {
    "spacer-po-krakowie": "Pierwsza lekcja — spacer po Krakowie",
}

KNOWN_SECTIONS = {
    "Metadata",
    "Editorial Transparency",
    "Sources",
    "Text",
    "Quiz",
    "Future Extensions",
}


@dataclass
class PackChange:
    slug: str
    lesson_id: str
    version: str
    changes: list[str] = field(default_factory=list)


def split_sections(md: str) -> dict[str, str]:
    lines = md.replace("\r\n", "\n").split("\n")
    sections: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if current is not None:
            sections[current] = "\n".join(buffer).strip()
        buffer = []

    for line in lines[1:]:  # skip # title
        if line.startswith("## "):
            name = line[3:].strip()
            if name in KNOWN_SECTIONS:
                flush()
                current = name
                continue
        if current is not None:
            buffer.append(line)
    flush()
    return sections


def parse_fields(section: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in section.splitlines():
        m = re.match(r"\*\*([^*]+):\*\*\s*(.*)", line.strip())
        if m:
            val = m.group(2).strip().strip("`")
            if val.startswith("*(") and val.endswith(")*"):
                val = ""
            fields[m.group(1).strip()] = val
    return fields


def set_field(section: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^\*\*{re.escape(key)}:\*\*.*$", re.MULTILINE)
    replacement = f"**{key}:** {value}"
    if pattern.search(section):
        return pattern.sub(replacement, section, count=1)
    return section.rstrip() + f"\n\n{replacement}\n"


def migrate_difficulty(raw: str) -> tuple[str, bool]:
    m = re.search(r"(\d+)\s*\(of\s*(\d+)\)", raw)
    if not m:
        return raw, False
    n, scale = int(m.group(1)), int(m.group(2))
    if scale == 10:
        new_n = max(1, min(8, round(n * 8 / 10)))
    else:
        new_n = max(1, min(8, n))
    new_raw = f"{new_n} (of 8)"
    return new_raw, new_raw != raw


def normalize_trust(raw: str, slug: str) -> tuple[str, bool]:
    if raw in CANONICAL_TRUST:
        return raw, False
    if not raw:
        return DEFAULT_TRUST_BY_SLUG.get(slug, "Fiction"), True
    mapped = TRUST_MAP.get(raw.lower(), raw)
    if mapped not in CANONICAL_TRUST:
        mapped = TRUST_MAP.get(raw.replace(" ", "_").lower(), "Inspired by reality")
    return mapped, mapped != raw


def normalize_audience(raw: str) -> tuple[str, bool]:
    mapped = AUDIENCE_MAP.get(raw.lower().strip(), raw)
    if mapped in {"child", "family", "teen", "adult"}:
        return mapped, mapped != raw
    return "adult", True


def pick_cover_family(genres: str) -> str:
    items = [g.strip() for g in genres.split(",") if g.strip()]
    for g in items:
        if g in GENRE_TO_COVER and g != "article":
            return GENRE_TO_COVER[g]
    for g in items:
        if g in GENRE_TO_COVER:
            return GENRE_TO_COVER[g]
    return "article"


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def extract_text_body(md: str) -> str:
    sections = split_sections(md)
    body = sections.get("Text", "")
    body = re.split(r"\n## Quiz\b", body)[0]
    return body.strip()


def estimated_minutes(text: str) -> int:
    wc = word_count(text)
    return max(1, math.ceil(wc / WORDS_PER_MINUTE)) if wc else 1


def insert_trust_classification(transparency: str, trust: str) -> str:
    if "**Trust classification:**" in transparency:
        return transparency
    marker = "**Human reviewed:**"
    if marker in transparency:
        return transparency.replace(
            marker,
            f"**Trust classification:** {trust}\n{marker}",
            1,
        )
    return f"**Trust classification:** {trust}\n\n{transparency}"


def polish_pack(path: str, entry: dict) -> PackChange | None:
    pack_dir = REPO_ROOT / path
    rp = pack_dir / "reading-pack.md"
    slug = entry["bookId"]
    change = PackChange(slug=slug, lesson_id=entry["id"], version=entry.get("version", ""))
    md = rp.read_text(encoding="utf-8")
    sections = split_sections(md)
    meta = sections.get("Metadata", "")
    trans = sections.get("Editorial Transparency", "")
    fields = parse_fields(meta)
    trans_fields = parse_fields(trans)

    # Subtitle
    subtitle = fields.get("Subtitle", "")
    if not subtitle or subtitle in {"*(none)*", "(none)"}:
        new_sub = SUBTITLE_FIXES.get(slug, "")
        if new_sub:
            meta = set_field(meta, "Subtitle", new_sub)
            change.changes.append(f"subtitle → {new_sub}")

    # Cover family
    if not fields.get("Cover family"):
        cover = pick_cover_family(fields.get("Genres", ""))
        meta = set_field(meta, "Cover family", cover)
        change.changes.append(f"cover family → {cover}")

    # Difficulty
    diff_raw = fields.get("Difficulty", "")
    new_diff, diff_changed = migrate_difficulty(diff_raw)
    if diff_changed:
        meta = set_field(meta, "Difficulty", new_diff)
        change.changes.append(f"difficulty {diff_raw} → {new_diff}")

    # Audience
    aud_raw = fields.get("Audience", "")
    new_aud, aud_changed = normalize_audience(aud_raw)
    if aud_changed:
        meta = set_field(meta, "Audience", new_aud)
        change.changes.append(f"audience {aud_raw!r} → {new_aud}")

    # Reading time from full text body
    text_body = extract_text_body(md)
    wc = word_count(text_body)
    new_est = estimated_minutes(text_body)
    est_raw = fields.get("Estimated reading time", "")
    est_m = int(re.search(r"(\d+)", est_raw).group(1)) if re.search(r"(\d+)", est_raw or "") else 0
    if wc > 50 and est_m != new_est:
        meta = set_field(meta, "Estimated reading time", f"{new_est} minutes")
        change.changes.append(f"reading time {est_m} → {new_est} min ({wc} words)")

    # Trust
    trust_raw = trans_fields.get("Trust classification", "")
    new_trust, trust_changed = normalize_trust(trust_raw, slug)
    if trust_changed or not trust_raw:
        if "**Trust classification:**" in trans:
            trans = re.sub(
                r"\*\*Trust classification:\*\*.*",
                f"**Trust classification:** {new_trust}",
                trans,
                count=1,
            )
        else:
            trans = insert_trust_classification(trans, new_trust)
        change.changes.append(f"trust {trust_raw!r} → {new_trust}")

    if not change.changes:
        return None

    # Reassemble markdown
    title_line = md.split("\n", 1)[0]
    new_md = title_line + "\n\n## Metadata\n\n" + meta.strip() + "\n"
    if sections.get("Editorial Transparency"):
        new_md += "\n---\n\n## Editorial Transparency\n\n" + trans.strip() + "\n"
    for sec_name in ("Sources", "Text", "Quiz", "Future Extensions"):
        if sections.get(sec_name):
            new_md += f"\n---\n\n## {sec_name}\n\n{sections[sec_name].strip()}\n"
    if not new_md.endswith("\n"):
        new_md += "\n"
    rp.write_text(new_md, encoding="utf-8")
    return change


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    all_changes: list[PackChange] = []
    for entry in manifest["packs"]:
        if entry.get("tier") != "official":
            continue
        result = polish_pack(entry["path"], entry)
        if result:
            all_changes.append(result)

    print(f"Polished {len(all_changes)} / {manifest['officialPackCount']} official packs")
    for c in all_changes:
        print(f"  {c.slug}: {len(c.changes)} change(s)")
        for ch in c.changes:
            print(f"    - {ch}")

    report_path = REPO_ROOT.parent / "alephbits" / "docs" / "product" / "METADATA_FIX_REPORT.md"
    if not report_path.parent.exists():
        report_path = Path("/Users/admin/Developer/alephbits/docs/product/METADATA_FIX_REPORT.md")
    _write_metadata_report(report_path, all_changes, manifest)


def _write_metadata_report(path: Path, changes: list[PackChange], manifest: dict) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Metadata Fix Report",
        "",
        f"Generated: {now}",
        f"Official packs: **{manifest['officialPackCount']}**",
        f"Packs modified: **{len(changes)}**",
        "",
        "## Summary",
        "",
        "| Change type | Count |",
        "|-------------|-------|",
    ]
    counters: dict[str, int] = {}
    for c in changes:
        for ch in c.changes:
            key = ch.split()[0]
            counters[key] = counters.get(key, 0) + 1
    for k, v in sorted(counters.items()):
        lines.append(f"| {k} | {v} |")
    lines.extend(["", "## Per-pack changes", ""])
    for c in sorted(changes, key=lambda x: x.slug):
        lines.append(f"### {c.slug}")
        lines.append("")
        lines.append(f"- lessonId: `{c.lesson_id}` (unchanged)")
        lines.append(f"- version: `{c.version}` (unchanged)")
        for ch in c.changes:
            lines.append(f"- {ch}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
