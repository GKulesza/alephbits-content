#!/usr/bin/env python3
"""Import Collection Four stories into official glagolitic reading packs."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CONTENT_ROOT = SCRIPT_DIR.parent
OUTPUT_ROOT = CONTENT_ROOT / "official" / "glagolitic" / "pl"
CATALOG_PATH = SCRIPT_DIR / "collection_four_catalog.json"
MANUSCRIPT_PATH = Path(
    "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/CollectionFour.md"
)
TODAY = "2026-07-10"
SERIES = "Collection Four"
WORDS_PER_MINUTE = 200


def star_rating(difficulty: int) -> str:
    if difficulty <= 2:
        filled = 1
    elif difficulty <= 4:
        filled = 2
    elif difficulty <= 6:
        filled = 3
    else:
        filled = 4
    return ("★" * filled) + ("☆" * (5 - filled))


def parse_date_polish(raw: str) -> str:
    match = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", raw.strip())
    if not match:
        return TODAY
    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


def extract_source_before_title(manuscript: str, title: str) -> tuple[str, str]:
    """Return (source_block_line, url) from the block preceding the story title."""
    pattern = re.compile(
        rf"(?:```(?:source)?\s*\n)?(\d{{2}}\.\d{{2}}\.\d{{4}}\s*->\s*(\S+))\s*\n```\s*\n```\s*\n#\s*{re.escape(title)}",
        re.DOTALL,
    )
    match = pattern.search(manuscript)
    if not match:
        return "", ""
    return match.group(1).strip(), match.group(2).strip()


def extract_story_body(manuscript: str, title: str) -> str:
    pattern = re.compile(
        rf"#\s*{re.escape(title)}\s*\n\n## Opowiadanie\s*\n\n---\s*\n\n(.*?)\n\*\*KONIEC\*\*",
        re.DOTALL,
    )
    match = pattern.search(manuscript)
    if not match:
        raise ValueError(f"Could not extract story body for: {title!r}")
    return match.group(1).rstrip()


def format_quiz(questions: list[dict]) -> str:
    parts = ["## Quiz", "", "**Quiz title:** Sprawdź zrozumienie", ""]
    for index, question in enumerate(questions, 1):
        parts.append(f"### Question {index}")
        parts.append("")
        parts.append(f"**Question:** {question['question']}")
        parts.append("")
        parts.append("**Answers:**")
        for letter in "ABCD":
            parts.append(f"- {letter}) {question['answers'][letter]}")
        parts.append("")
        parts.append(f"**Correct:** {question['correct']}")
        parts.append(f"**Explanation:** {question['explanation']}")
        text_ref = question.get("textReference", "")
        if text_ref:
            parts.append(f"**Text reference:** {text_ref}")
        parts.append("")
    return "\n".join(parts).rstrip()


def format_sources(source_label: str, source_block: str, url: str, retrieval_date: str, availability: str) -> str:
    parts = ["## Sources", "", f"### Source 1: {source_label}", ""]
    parts.append("**Author:** AlephBits Editorial (adaptation)  ")
    if url:
        parts.append(f"**URL:** {url}  ")
        editor_note = "Materiał źródłowy wskazany w bloku source manuskryptu."
    else:
        parts.append("**URL:** *(none)*  ")
        editor_note = "Migrated from Collection Four manuscript."
    parts.append("**License:** CC0 1.0 Universal (text); source material per original availability  ")
    parts.append(f"**Retrieval date:** {retrieval_date}  ")
    parts.append(f"**Availability:** {availability}  ")
    parts.append("**Deprecated:** no  ")
    parts.append(f"**Editor notes:** {editor_note}")
    return "\n".join(parts)


def build_reading_pack(entry: dict, body: str, source_block: str, url: str, retrieval_date: str) -> str:
    title = entry["title"]
    slug = entry["slug"]
    pack_id = entry["packId"]
    difficulty = entry["difficulty"]
    genres = ", ".join(entry["genres"])
    tags = ", ".join(entry.get("themes", []))
    keywords = entry["keywords"]
    editorial_notes = entry.get("editorialNotes", f"Migrated from {SERIES} manuscript. Full text preserved — not abridged.")
    trust = entry["trustClassification"]
    availability = entry["availability"]
    reading_time = max(1, math.ceil(len(body.split()) / WORDS_PER_MINUTE))
    audience = entry["audience"]
    uppercase_title = title.upper()

    source_block_line = source_block or "(none)"
    revision_notes = editorial_notes

    text_section = f"**{uppercase_title}**\n\n\n{body}\n\n\n**KONIEC**"

    return f"""# {title}

## Metadata

**Pack ID:** `{pack_id}`  
**Version:** 1.0.0  

**Title:** {title}  
**Subtitle:** {entry['subtitle']}  
**Blurb:** {entry['summary']}

**Genres:** {genres}  
**Cover family:** {entry['coverFamily']}  
**Series:** {SERIES}  
**Audience:** {audience}  

**Difficulty:** {difficulty} (of 8)  
**Reader difficulty:** {star_rating(difficulty)}  
**Estimated reading time:** {reading_time} minutes  

**Publication date:** *(original — 2026)*  
**Historical period:** *(varies — see text)*  

**Original language:** pl  
**Translation summary:** {title} — {SERIES} official reading pack (Polish).  

**Writing system:** glagolitic  
**Recommended profile:** polish_default  
**Recommended level:** {entry['recommendedLevel']}  

**Tags:** {tags}  

**Keywords:** {keywords}  

**Editorial notes:** {editorial_notes}

---

## Editorial Transparency

**Created by:** AlephBits Editorial  
**Editor:** AlephBits Editorial  
**LLM assisted:** yes  
**LLM model:** Claude  
**Human reviewed:** yes — {TODAY}  
**Trust classification:** {trust}  
**License:** CC0 1.0 Universal (SPDX: CC0-1.0)  
**License URL:** https://creativecommons.org/publicdomain/zero/1.0/  
**Source block:** {source_block_line}  
**Revision notes:** {revision_notes}

### Revision history

| Version | Date | Note |
|---------|------|------|
| 1.0.0 | {TODAY} | {SERIES} migration |

---

{format_sources(f"{SERIES} manuscript", source_block, url, retrieval_date, availability)}

---

## Text

{text_section}

---

{format_quiz(entry['quiz'])}

---

## Future Extensions

### Images
*(none)*

### Illustrations
*(none)*

### Audio narration
*(none)*

### Pronunciation
*(none)*

### Handwriting
*(none)*

### Exercises
*(none)*

### Vocabulary
*(none)*
"""


def main() -> None:
    catalog: list[dict] = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    manuscript = MANUSCRIPT_PATH.read_text(encoding="utf-8")

    if not OUTPUT_ROOT.exists():
        OUTPUT_ROOT.mkdir(parents=True)

    written: list[str] = []
    for entry in catalog:
        title = entry["title"]
        slug = entry["slug"]
        source_block, url = extract_source_before_title(manuscript, title)
        retrieval_date = parse_date_polish(source_block.split("->")[0].strip()) if source_block else TODAY
        body = extract_story_body(manuscript, title)

        pack_dir = OUTPUT_ROOT / slug
        pack_dir.mkdir(parents=True, exist_ok=True)
        output_path = pack_dir / "reading-pack.md"
        output_path.write_text(
            build_reading_pack(entry, body, source_block, url, retrieval_date),
            encoding="utf-8",
        )
        written.append(str(output_path))
        print(f"✓ {slug} ({len(body.split())} words, ~{max(1, math.ceil(len(body.split()) / WORDS_PER_MINUTE))} min)")

    print(f"\nWrote {len(written)} reading packs from {SERIES}:")
    for path in written:
        print(f"  {path}")


if __name__ == "__main__":
    main()
