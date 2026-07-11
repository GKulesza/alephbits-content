#!/usr/bin/env python3
"""Phase 79 — audit editorial blurbs across official packs."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "official" / "glagolitic" / "pl"

BAD_INTRO = re.compile(
    r"(?i)^(?:this story is about|this book tells|in this text|"
    r"opowieść o|historia .+ który|w tym tekście|książka opowiada|"
    r"ten tekst opowiada|ta opowieść)"
)
TITLE_REPEAT = re.compile(r"^#{1,3}\s|\*\*[A-ZĄĆĘŁŃÓŚŹŻ ]+\*\*")
PHASE_REF = re.compile(r"(?i)phase\s+\d+")


def extract_blurb(text: str) -> str | None:
    match = re.search(r"\*\*Blurb:\*\*\s*(.+?)(?:\n\n\*\*Genres:\*\*)", text, re.S)
    return match.group(1).strip() if match else None


def word_count(text: str) -> int:
    return len(re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE).split())


def normalize_for_dup(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def title_repeated(title: str, blurb: str) -> bool:
    title_norm = title.lower().strip()
    if len(title_norm) < 3:
        return False
    blurb_norm = normalize_for_dup(blurb)
    return bool(re.search(rf"\b{re.escape(title_norm)}\b", blurb_norm))


def rate_blurb(text: str, title: str) -> str:
    words = word_count(text)
    if (
        words < 20
        or words > 120
        or BAD_INTRO.match(text.strip())
        or TITLE_REPEAT.match(text.strip())
        or PHASE_REF.search(text)
        or title_repeated(title, text)
    ):
        return "Needs improvement"
    if 40 <= words <= 90:
        return "Excellent"
    if 30 <= words <= 100:
        return "Good"
    return "Needs improvement"


def main() -> None:
    rows: list[tuple[str, str, int, str, list[str]]] = []
    normalized: dict[str, list[str]] = {}

    for pack_dir in sorted(PACKS.iterdir()):
        slug = pack_dir.name
        md_path = pack_dir / "reading-pack.md"
        if not md_path.exists():
            continue
        raw = md_path.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)$", raw, re.M)
        title = title_match.group(1).strip() if title_match else slug
        blurb = extract_blurb(raw)
        if blurb is None:
            rows.append((slug, title, 0, "Needs improvement", ["missing blurb"]))
            continue

        words = word_count(blurb)
        flags: list[str] = []
        if words < 20:
            flags.append(f"too short ({words}w)")
        if words > 120:
            flags.append(f"too long ({words}w)")
        if words < 40:
            flags.append("below target (40–90w)")
        if BAD_INTRO.match(blurb.strip()):
            flags.append("AI-style intro")
        if TITLE_REPEAT.match(blurb.strip()):
            flags.append("title/header in blurb")
        if PHASE_REF.search(blurb):
            flags.append("phase reference")
        if title_repeated(title, blurb):
            flags.append("repeats title")

        norm = normalize_for_dup(blurb)
        normalized.setdefault(norm, []).append(slug)
        rating = rate_blurb(blurb, title)
        rows.append((slug, title, words, rating, flags))

    dup_slugs = {s for slugs in normalized.values() if len(slugs) > 1 for s in slugs}
    for i, (slug, title, words, rating, flags) in enumerate(rows):
        if slug in dup_slugs:
            flags = flags + ["duplicate wording"]
            if rating == "Excellent":
                rating = "Good"
        rows[i] = (slug, title, words, rating, flags)

    counts = Counter(r[3] for r in rows)
    weak = [r for r in rows if r[3] != "Excellent" or r[4]]

    print("Phase 79 blurb audit")
    print(f"Total packs: {len(rows)}")
    print(f"Excellent: {counts['Excellent']}")
    print(f"Good: {counts['Good']}")
    print(f"Needs improvement: {counts['Needs improvement']}")
    print(f"Founder review: {counts.get('Founder review', 0)}")
    print()
    if weak:
        print("Flagged:")
        for slug, title, words, rating, flags in weak:
            flag_str = ", ".join(flags) if flags else rating
            print(f"  {slug}: {words}w [{rating}] — {flag_str}")
    else:
        print("All blurbs pass editorial checks.")


if __name__ == "__main__":
    main()
