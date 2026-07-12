#!/usr/bin/env python3
"""Phase 102 — import Collection Seven (remaining) + Collection Eight stories."""

from __future__ import annotations

import json
import math
import re
import subprocess
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACK_ROOT = REPO / "official" / "glagolitic" / "pl"
SPECS_PATH = REPO / "tools" / "phase102_pack_specs.json"
MANUSCRIPTS = [
    Path(
        "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/Books/CollectionSeven.md"
    ),
    Path(
        "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App Ideas/alephBits/Books/CollectionEight.md"
    ),
]
ROMAN = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")
WORDS_PER_MIN = 200
ACT_SECTIONS = {
    "WSTĘP",
    "ROZWINIĘCIE",
    "ZAKOŃCZENIE",
    "EPILOG",
    "CO WIEDZIAŁ",
}


@dataclass
class QuizQ:
    question: str
    answers: tuple[str, str, str, str]
    correct: str
    explanation: str
    reference: str


@dataclass
class PackSpec:
    manuscript_title: str
    slug: str
    pack_id: str
    display_title: str
    subtitle: str
    blurb: str
    genres: str
    cover_family: str
    audience: str
    difficulty: int
    reader_stars: str
    trust: str
    tags: str
    keywords: str
    editorial_notes: str
    revision_notes: str
    philosophy_stars: int
    philosophy_note: str
    founder_notes: list[str] = field(default_factory=list)
    quiz: list[QuizQ] = field(default_factory=list)
    inspiration: str = ""
    youtube_ids: list[str] = field(default_factory=list)
    series: str = "Collection Seven"


@dataclass
class ParsedStory:
    title: str
    source_block: str
    body_raw: str
    youtube_ids: list[str]
    source_dates: list[str]


def slugify(title: str) -> str:
    value = unicodedata.normalize("NFKD", title)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def is_story_header(title: str) -> bool:
    t = title.strip()
    if not t:
        return False
    if re.match(r"^\d+\.", t):
        return False
    if re.match(r"^[IVX]+\.$", t):
        return False
    if t.upper() in ACT_SECTIONS:
        return False
    return True


def parse_manuscript(path: Path) -> list[ParsedStory]:
    raw = path.read_text(encoding="utf-8")
    header = re.compile(r'^##\s+(?:"([^"]+)"|([^\n"]+?))\s*$', re.MULTILINE)
    matches = [
        m
        for m in header.finditer(raw)
        if is_story_header((m.group(1) or m.group(2)).strip())
    ]
    stories: list[ParsedStory] = []

    for i, match in enumerate(matches):
        title = (match.group(1) or match.group(2)).strip()
        chunk = raw[match.end() : matches[i + 1].start() if i + 1 < len(matches) else len(raw)]

        source_block = ""
        src = re.search(r"```source\n(.*?)```", chunk, re.DOTALL)
        if src:
            source_block = src.group(1).strip()

        body = ""
        story_match = re.search(r"```story\n(.*?)```", chunk, re.DOTALL)
        if story_match:
            body = story_match.group(1).strip()
        else:
            body_match = re.search(
                r"```source\n.*?```\s*\n+```\n(.*?)```",
                chunk,
                re.DOTALL,
            )
            if body_match:
                body = body_match.group(1).strip()
            else:
                blocks = re.findall(r"```[^\n]*\n(.*?)```", chunk, re.DOTALL)
                for block in blocks:
                    if re.search(r"(?i)OPOWIADANIE|##\s+\d+\.\s+|^#\s+", block, re.M):
                        body = block.strip()
                        break
                if not body and blocks:
                    body = blocks[-1].strip()
                if not source_block:
                    for block in blocks:
                        if block is body or re.search(
                            r"(?i)OPOWIADANIE|##\s+\d+\.\s+", block
                        ):
                            continue
                        if re.search(
                            r"youtube\.com|^\d{2}\.\d{2}\.\d{4}\s*->",
                            block,
                            re.M,
                        ):
                            source_block = block.strip()
                            break

        youtube_ids = re.findall(r"[?&]v=([A-Za-z0-9_-]{11})", source_block)
        youtube_ids += re.findall(r"->\s*([A-Za-z0-9_-]{11})\s*$", source_block, re.M)
        youtube_ids += re.findall(r"[?&]v=([A-Za-z0-9_-]{11})", body)
        dates = re.findall(r"(\d{2})\.(\d{2})\.(\d{4})", source_block or body)

        stories.append(
            ParsedStory(
                title=title,
                source_block=source_block,
                body_raw=body,
                youtube_ids=list(dict.fromkeys(youtube_ids)),
                source_dates=[f"{y}-{m}-{d}" for d, m, y in dates],
            )
        )
    return stories


def convert_body(body: str, display_title: str) -> str:
    text = body
    text = re.sub(r"^# OPOWIADANIE:.*?\n+", "", text, flags=re.I)
    text = re.sub(r"^# [^\n]+\n+", "", text, count=1)
    text = re.sub(r"^---\s*\n+", "", text)

    def section_repl(m: re.Match[str]) -> str:
        num = int(m.group(1))
        name = m.group(2).strip()
        label = ROMAN[num - 1] if 0 < num <= len(ROMAN) else str(num)
        return f"\n## {label}. {name}\n"

    text = re.sub(r"^## (\d+)\.\s*(.+)$", section_repl, text, flags=re.M)
    text = re.sub(r"^## ([IVX]+)\.\s*$", r"\n## \1\n", text, flags=re.M)
    text = re.sub(r"\n---\n+", "\n---\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    banner = f"**{display_title.upper()}**"
    if not text.startswith("**"):
        text = f"{banner}\n\n{text}"
    if "**KONIEC**" not in text:
        text += "\n\n**KONIEC**"
    return text


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def reading_minutes(text: str) -> int:
    return max(1, math.ceil(word_count(text) / WORDS_PER_MIN))


def render_quiz(questions: list[QuizQ]) -> str:
    lines = ["## Quiz", "", "**Quiz title:** Sprawdź zrozumienie", ""]
    for i, q in enumerate(questions, 1):
        lines.extend(
            [
                f"### Question {i}",
                "",
                f"**Question:** {q.question}",
                "",
                "**Answers:**",
                f"- A) {q.answers[0]}",
                f"- B) {q.answers[1]}",
                f"- C) {q.answers[2]}",
                f"- D) {q.answers[3]}",
                "",
                f"**Correct:** {q.correct}",
                f"**Explanation:** {q.explanation}",
                f"**Text reference:** {q.reference}",
                "",
            ]
        )
    return "\n".join(lines)


def render_reading_pack(spec: PackSpec, story: ParsedStory, text_body: str) -> str:
    est = reading_minutes(text_body)
    yt = story.youtube_ids[0] if story.youtube_ids else ""
    src_date = story.source_dates[0] if story.source_dates else "2026-07-12"
    source_url = f"https://www.youtube.com/watch?v={yt}" if yt else "*(none — manuscript)*"

    lines = [
        f"# {spec.display_title}",
        "",
        "## Metadata",
        "",
        f"**Pack ID:** `{spec.pack_id}`  ",
        "**Version:** 1.0.0  ",
        "**Edition version:** 1.0.0  ",
        "",
        f"**Title:** {spec.display_title}  ",
        f"**Subtitle:** {spec.subtitle}  ",
        f"**Blurb:** {spec.blurb}",
        "",
        f"**Genres:** {spec.genres}  ",
        f"**Series:** {spec.series}  ",
        f"**Audience:** {spec.audience}",
        "",
        f"**Difficulty:** {spec.difficulty} (of 8)  ",
        f"**Reader difficulty:** {spec.reader_stars}  ",
        f"**Estimated reading time:** {est} minutes",
        "",
        "**Publication date:** *(original — 2026)*  ",
        "**Historical period:** contemporary  ",
        "",
        "**Original language:** pl  ",
        f"**Translation summary:** {spec.display_title} — {spec.series} official reading pack (Polish).  ",
        "",
        "**Writing system:** glagolitic  ",
        "**Recommended profile:** polish_default  ",
        f"**Recommended level:** {max(2, spec.difficulty - 2)}  ",
        "",
        f"**Tags:** {spec.tags}  ",
        "",
        f"**Keywords:** {spec.keywords}  ",
        "",
        f"**Cover family:** {spec.cover_family}",
        "",
        f"**Editorial notes:** {spec.editorial_notes}",
        "",
        "**Inspiration:** " + (spec.inspiration or f"{spec.series} manuscript — editorial adaptation."),
        "",
        "---",
        "",
        "## Editorial Transparency",
        "",
        "**Created by:** AlephBits Editorial  ",
        "**Editor:** AlephBits Editorial  ",
        "**LLM assisted:** yes  ",
        "**LLM model:** Claude  ",
        "**Human reviewed:** yes — 2026-07-12  ",
        f"**Trust classification:** {spec.trust}  ",
        "**License:** CC0 1.0 Universal (SPDX: CC0-1.0)  ",
        "**License URL:** https://creativecommons.org/publicdomain/zero/1.0/  ",
        f"**Source block:** {story.source_block.replace(chr(10), ' / ') if story.source_block else '*(manuscript)*'}  ",
        f"**Revision notes:** {spec.revision_notes}",
        "",
        "### Revision history",
        "",
        "| Version | Date | Note |",
        "|---------|------|------|",
        "| 1.0.0 | 2026-07-12 | Collection editorial import (Phase 102) |",
        "",
        "### Editorial history",
        "",
        "| Date | Editor | Note |",
        "|------|--------|------|",
        f"| 2026-07-12 | AlephBits Editorial | Phase 102 import; philosophy fit {spec.philosophy_stars}/5 — {spec.philosophy_note} |",
        "",
        "---",
        "",
        "## Sources",
        "",
        f"### Source 1: {spec.series} manuscript",
        "",
        "**Author:** AlephBits Editorial (adaptation)  ",
        f"**URL:** {source_url}  ",
        "**License:** CC0 1.0 Universal (text); source material per original availability  ",
        f"**Retrieval date:** {src_date}  ",
        "**Availability:** adaptation  ",
        "**Deprecated:** no  ",
        "**Editor notes:** Materiał źródłowy wskazany w bloku source manuskryptu; tekst jest adaptacją redakcyjną.",
        "",
        "---",
        "",
        "## Text",
        "",
        text_body,
        "",
        "---",
        "",
        render_quiz(spec.quiz),
        "",
        "---",
        "",
        "## Future Extensions",
        "",
        "### Images",
        "*(none)*",
        "",
        "### Illustrations",
        "*(none)*",
        "",
        "### Audio narration",
        "*(none)*",
        "",
        "### Pronunciation",
        "*(none)*",
        "",
        "### Handwriting",
        "*(none)*",
        "",
        "### Exercises",
        "*(none)*",
        "",
        "### Vocabulary",
        "*(none)*",
        "",
    ]
    return "\n".join(lines)


def write_license(pack_dir: Path, title: str) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "license.md").write_text(
        f"# License\n\n**{title}** is released under **CC0 1.0 Universal** (public domain dedication).\n\n"
        "- SPDX: `CC0-1.0`\n"
        "- Full text: https://creativecommons.org/publicdomain/zero/1.0/\n\n"
        "You may copy, modify, and distribute this work for any purpose without asking permission.\n",
        encoding="utf-8",
    )


def write_provenance(pack_dir: Path, spec: PackSpec, story: ParsedStory) -> None:
    sources = [{"type": "youtube", "videoId": vid} for vid in story.youtube_ids]
    data = {
        "packId": spec.pack_id,
        "bookId": spec.slug,
        "editorialStatus": "official",
        "createdAt": "2026-07-12",
        "lastReviewedAt": "2026-07-12",
        "editors": ["AlephBits Editorial"],
        "aiAssistance": {
            "used": True,
            "tools": [],
            "humanReview": spec.revision_notes,
        },
        "sources": sources,
        "revisionNotes": spec.revision_notes,
        "philosophyFit": {
            "stars": spec.philosophy_stars,
            "note": spec.philosophy_note,
        },
        "founderNotes": spec.founder_notes,
    }
    (pack_dir / "provenance.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_specs() -> dict[str, PackSpec]:
    raw = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
    specs: dict[str, PackSpec] = {}
    for title, data in raw.items():
        quiz = [
            QuizQ(
                q["question"],
                tuple(q["answers"]),
                q["correct"],
                q["explanation"],
                q["reference"],
            )
            for q in data["quiz"]
        ]
        specs[title] = PackSpec(
            manuscript_title=data["manuscript_title"],
            slug=data["slug"],
            pack_id=data["pack_id"],
            display_title=data["display_title"],
            subtitle=data["subtitle"],
            blurb=data["blurb"],
            genres=data["genres"],
            cover_family=data["cover_family"],
            audience=data["audience"],
            difficulty=data["difficulty"],
            reader_stars=data["reader_stars"],
            trust=data["trust"],
            tags=data["tags"],
            keywords=data["keywords"],
            editorial_notes=data["editorial_notes"],
            revision_notes=data.get("revision_notes", "Phase 102 import."),
            philosophy_stars=data["philosophy_stars"],
            philosophy_note=data["philosophy_note"],
            founder_notes=data.get("founder_notes", []),
            quiz=quiz,
            inspiration=data.get("inspiration", ""),
            series=data.get("series", "Collection Seven"),
        )
    return specs


def existing_slugs() -> set[str]:
    return {p.name for p in PACK_ROOT.iterdir() if p.is_dir()}


def import_story(spec: PackSpec, story: ParsedStory) -> Path:
    pack_dir = PACK_ROOT / spec.slug
    body = convert_body(story.body_raw, spec.display_title)
    rp = render_reading_pack(spec, story, body)
    write_license(pack_dir, spec.display_title)
    write_provenance(pack_dir, spec, story)
    (pack_dir / "reading-pack.md").write_text(rp, encoding="utf-8")
    return pack_dir


def run_cmd(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    specs = load_specs()
    existing = existing_slugs()
    imported: list[str] = []
    skipped: list[str] = []
    seen_slugs: set[str] = set()

    for manuscript in MANUSCRIPTS:
        for story in parse_manuscript(manuscript):
            spec = specs.get(story.title)
            if not spec:
                skipped.append(f"{story.title} — no PackSpec")
                continue
            if spec.slug in existing or spec.slug in seen_slugs:
                skipped.append(f"{story.title} ({spec.slug}) — already official")
                continue
            if not story.body_raw.strip():
                raise ValueError(f"Empty body for story: {story.title}")
            import_story(spec, story)
            seen_slugs.add(spec.slug)
            imported.append(f"{spec.display_title} → {spec.slug}")
            print(f"✓ {spec.slug}")

    print(f"\nImported {len(imported)} pack(s), skipped {len(skipped)}")
    for s in skipped:
        print(f"  skip: {s}")

    run_cmd(["dart", "run", "tools/compile_pack.dart", "--all", "--overwrite"], REPO)
    run_cmd(["dart", "run", "tools/build_manifest.dart"], REPO)
    run_cmd(["dart", "run", "scripts/validate_pack.dart"], REPO)

    app_repo = REPO.parent / "alephbits"
    if app_repo.exists():
        run_cmd(["dart", "run", "tool/bundle_content_assets.dart"], app_repo)
        run_cmd(["flutter", "test"], app_repo)

    print("Phase 102 import complete.")


if __name__ == "__main__":
    main()
