#!/usr/bin/env python3
"""Phase 83 — compare Collection Seven manuscript against the official catalog."""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONTENT_ROOT = SCRIPT_DIR.parent
PACK_ROOT = CONTENT_ROOT / "official" / "glagolitic" / "pl"
MANUSCRIPT_PATH = Path(
    "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/Books/CollectionSeven.md"
)
REPORT_PATH = CONTENT_ROOT / "docs" / "product" / "PHASE_83_IMPORT_REPORT.md"


@dataclass
class ManuscriptStory:
    title: str
    slug: str
    body: str
    source_date: str
    youtube_id: str


@dataclass
class CatalogEntry:
    slug: str
    title: str
    pack_id: str
    body: str
    edition_version: str


def normalize_title(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def slugify(title: str) -> str:
    value = normalize_title(title)
    replacements = {"z": "z", "s": "s"}
    value = value.replace(" ", "-")
    mapping = str.maketrans("ąćęłńóśźż", "acelnoszz")
    return value.translate(mapping)


def token_set(value: str) -> set[str]:
    return {token for token in re.findall(r"\w+", normalize_text(value), re.UNICODE) if len(token) > 2}


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def parse_manuscript(path: Path) -> list[ManuscriptStory]:
    raw = path.read_text(encoding="utf-8")
    stories: list[ManuscriptStory] = []

    title_match = re.search(r'^##\s+"([^"]+)"\s*$', raw, re.MULTILINE)
    if not title_match:
        raise ValueError("Collection Seven manuscript title not found")
    title = title_match.group(1)

    source_match = re.search(
        r"(\d{2}\.\d{2}\.\d{4})\s*->\s*(https?://\S+|([A-Za-z0-9_-]{11}))",
        raw,
    )
    source_date = ""
    youtube_id = ""
    if source_match:
        day, month, year = source_match.group(1).split(".")
        source_date = f"{year}-{month}-{day}"
        youtube_id = source_match.group(3) or re.search(
            r"[?&]v=([A-Za-z0-9_-]{11})", source_match.group(2) or ""
        ).group(1)

    body_match = re.search(
        r"# Opowiadanie:.*?\n\n---\n\n(.*?)\n\*\*KONIEC\*\*",
        raw,
        re.DOTALL,
    )
    if not body_match:
        raise ValueError("Collection Seven story body not found")
    body = body_match.group(1)
    body = re.sub(r"^## \d+\. .*$", "", body, flags=re.MULTILINE)
    body = re.sub(r"^---$", "", body, flags=re.MULTILINE)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()

    stories.append(
        ManuscriptStory(
            title=title,
            slug=slugify(title),
            body=body,
            source_date=source_date,
            youtube_id=youtube_id,
        )
    )
    return stories


def load_catalog() -> list[CatalogEntry]:
    entries: list[CatalogEntry] = []
    for pack_dir in sorted(PACK_ROOT.iterdir()):
        if not pack_dir.is_dir():
            continue
        reading_pack = pack_dir / "reading-pack.md"
        lesson_json = pack_dir / "lesson.json"
        if not reading_pack.exists():
            continue

        raw = reading_pack.read_text(encoding="utf-8")
        title_match = re.search(r"\*\*Title:\*\*\s*(.+)", raw)
        pack_id_match = re.search(r"\*\*Pack ID:\*\*\s*`([^`]+)`", raw)
        edition_match = re.search(r"\*\*Edition version:\*\*\s*(.+)", raw)
        text_match = re.search(r"## Text\s*\n+(.*?)\n---\n+\n## Quiz", raw, re.DOTALL)
        title = title_match.group(1).strip() if title_match else pack_dir.name
        pack_id = pack_id_match.group(1).strip() if pack_id_match else pack_dir.name
        edition = edition_match.group(1).strip() if edition_match else "unknown"
        body = text_match.group(1).strip() if text_match else ""
        if not body and lesson_json.exists():
            lesson = json.loads(lesson_json.read_text(encoding="utf-8"))
            body = lesson.get("text", "")

        entries.append(
            CatalogEntry(
                slug=pack_dir.name,
                title=title,
                pack_id=pack_id,
                body=body,
                edition_version=edition,
            )
        )
    return entries


def classify_story(story: ManuscriptStory, catalog: list[CatalogEntry], exclude_slugs: set[str] | None = None) -> dict:
    exclude = exclude_slugs or set()
    catalog = [entry for entry in catalog if entry.slug not in exclude]
    normalized_title = normalize_title(story.title)
    exact_slug = any(entry.slug == story.slug for entry in catalog)
    duplicate_title = [
        entry for entry in catalog if normalize_title(entry.title) == normalized_title
    ]

    content_matches: list[tuple[float, CatalogEntry]] = []
    near_matches: list[tuple[float, CatalogEntry, str]] = []
    story_tokens = token_set(story.body)

    for entry in catalog:
        ratio = similarity(story.body, entry.body)
        if ratio >= 0.92:
            content_matches.append((ratio, entry))
            continue

        entry_tokens = token_set(entry.body)
        if not entry_tokens:
            continue
        overlap = len(story_tokens & entry_tokens) / max(len(story_tokens | entry_tokens), 1)
        if ratio >= 0.55 or overlap >= 0.35:
            reason = []
            if ratio >= 0.55:
                reason.append(f"sequence similarity {ratio:.0%}")
            if overlap >= 0.35:
                reason.append(f"token overlap {overlap:.0%}")
            near_matches.append((max(ratio, overlap), entry, ", ".join(reason)))

    if exact_slug or duplicate_title:
        action = "skip"
        reason = "duplicate title / slug already in catalog"
    elif content_matches:
        action = "skip"
        best = max(content_matches, key=lambda item: item[0])
        reason = f"duplicate content ({best[0]:.0%} match with {best[1].slug})"
    elif near_matches:
        action = "import_with_review"
        best = max(near_matches, key=lambda item: item[0])
        reason = f"near duplicate of {best[1].slug} ({best[2]}) — manual review required"
    else:
        action = "import"
        reason = "no title, slug, or content collision with existing catalog"

    return {
        "action": action,
        "reason": reason,
        "duplicate_title": duplicate_title,
        "content_matches": content_matches,
        "near_matches": near_matches,
    }


def render_report(stories: list[ManuscriptStory], catalog: list[CatalogEntry]) -> str:
    imported: list[str] = []
    updated: list[str] = []
    skipped: list[str] = []

    lines = [
        "# Phase 83 — Collection Seven Import Report",
        "",
        f"**Manuscript:** `{MANUSCRIPT_PATH}`",
        f"**Catalog:** `{PACK_ROOT}` ({len(catalog)} official packs before import)",
        f"**Tool:** `tools/phase83_collection_seven_import.py`",
        "",
        "---",
        "",
    ]

    for story in stories:
        result = classify_story(story, catalog)
        row = f"| {story.title} | `{story.slug}` | {result['reason']} |"
        if result["action"] == "import":
            imported.append(row)
        elif result["action"] == "import_with_review":
            imported.append(row)
        elif result["action"] == "update":
            updated.append(row)
        else:
            skipped.append(row)

        lines.extend(
            [
                f"## {story.title}",
                "",
                f"- **Slug:** `{story.slug}`",
                f"- **Source date:** {story.source_date or '*(none)*'}",
                f"- **YouTube ID:** `{story.youtube_id or '*(none)*'}`",
                f"- **Decision:** {result['action']}",
                f"- **Reason:** {result['reason']}",
                "",
            ]
        )

        if result["duplicate_title"]:
            lines.append("**Duplicate title matches:**")
            for entry in result["duplicate_title"]:
                lines.append(f"- `{entry.slug}` — {entry.title}")
            lines.append("")

        if result["content_matches"]:
            lines.append("**Duplicate content matches:**")
            for ratio, entry in sorted(result["content_matches"], reverse=True):
                lines.append(f"- `{entry.slug}` — {ratio:.0%} similarity")
            lines.append("")

        if result["near_matches"]:
            lines.append("**Near duplicate signals:**")
            for score, entry, detail in sorted(result["near_matches"], reverse=True)[:5]:
                lines.append(f"- `{entry.slug}` — {detail}")
            lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Summary",
            "",
            "### Imported",
            "",
            "| Title | Slug | Reason |",
            "|-------|------|--------|",
        ]
    )
    lines.extend(imported or ["| *(none)* | | |"])
    lines.extend(
        [
            "",
            "### Updated",
            "",
            "| Title | Slug | Reason |",
            "|-------|------|--------|",
        ]
    )
    lines.extend(updated or ["| *(none)* | | |"])
    lines.extend(
        [
            "",
            "### Skipped",
            "",
            "| Title | Slug | Reason |",
            "|-------|------|--------|",
        ]
    )
    lines.extend(skipped or ["| *(none)* | | |"])
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    stories = parse_manuscript(MANUSCRIPT_PATH)
    catalog = load_catalog()
    report = render_report(stories, catalog)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nWrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
