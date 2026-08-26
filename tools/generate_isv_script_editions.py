#!/usr/bin/env python3
"""Generate isv_cyrl / isv_glag reading-pack.md from Interslavic Latin source.

Transliterates human-readable prose fields while preserving Markdown structure,
URLs, SPDX ids, and structural labels.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LATIN_TO_CYR_MULTI = {
    "DŽ": "Џ",
    "Dž": "Џ",
    "dž": "џ",
    "NJ": "Њ",
    "Nj": "Њ",
    "nj": "њ",
    "LJ": "Љ",
    "Lj": "Љ",
    "lj": "љ",
}

LATIN_TO_CYR = {
    "A": "А",
    "B": "Б",
    "C": "Ц",
    "Č": "Ч",
    "D": "Д",
    "E": "Е",
    "Ě": "Є",
    "F": "Ф",
    "G": "Г",
    "H": "Х",
    "I": "И",
    "J": "Ј",
    "K": "К",
    "L": "Л",
    "M": "М",
    "N": "Н",
    "O": "О",
    "P": "П",
    "R": "Р",
    "S": "С",
    "Š": "Ш",
    "T": "Т",
    "U": "У",
    "V": "В",
    "Y": "Ы",
    "Z": "З",
    "Ž": "Ж",
    "a": "а",
    "b": "б",
    "c": "ц",
    "č": "ч",
    "d": "д",
    "e": "е",
    "ě": "є",
    "f": "ф",
    "g": "г",
    "h": "х",
    "i": "и",
    "j": "ј",
    "k": "к",
    "l": "л",
    "m": "м",
    "n": "н",
    "o": "о",
    "p": "п",
    "r": "р",
    "s": "с",
    "š": "ш",
    "t": "т",
    "u": "у",
    "v": "в",
    "y": "ы",
    "z": "з",
    "ž": "ж",
}

LATIN_TO_GLAG_MULTI = {
    "DŽ": "Ⱛ",
    "Dž": "Ⱛ",
    "dž": "ⱛ",
    "NJ": "Ⱘ",
    "Nj": "Ⱘ",
    "nj": "ⱘ",
    "LJ": "Ⱙ",
    "Lj": "Ⱙ",
    "lj": "ⱙ",
}

LATIN_TO_GLAG = {
    "A": "Ⰰ",
    "B": "Ⰱ",
    "V": "Ⰲ",
    "G": "Ⰳ",
    "D": "Ⰴ",
    "E": "Ⰵ",
    "Ž": "Ⰶ",
    "Z": "Ⰷ",
    "I": "Ⰸ",
    "J": "Ⰹ",
    "K": "Ⰺ",
    "L": "Ⰻ",
    "M": "Ⰼ",
    "N": "Ⰽ",
    "O": "Ⰾ",
    "P": "Ⰿ",
    "R": "Ⱀ",
    "S": "Ⱁ",
    "T": "Ⱂ",
    "U": "Ⱃ",
    "F": "Ⱄ",
    "H": "Ⱅ",
    "C": "Ⱆ",
    "Č": "Ⱇ",
    "Š": "Ⱈ",
    "a": "ⰰ",
    "b": "ⰱ",
    "v": "ⰲ",
    "g": "ⰳ",
    "d": "ⰴ",
    "e": "ⰵ",
    "ž": "ⰶ",
    "z": "ⰷ",
    "i": "ⰸ",
    "j": "ⰹ",
    "k": "ⰺ",
    "l": "ⰻ",
    "m": "ⰼ",
    "n": "ⰽ",
    "o": "ⰾ",
    "p": "ⰿ",
    "r": "ⱀ",
    "s": "ⱁ",
    "t": "ⱂ",
    "u": "ⱃ",
    "f": "ⱄ",
    "h": "ⱅ",
    "c": "ⱆ",
    "č": "ⱇ",
    "š": "ⱈ",
    "y": "ⱑ",
    "ě": "ⱑ",
}


def transliterate(text: str, multi: dict[str, str], single: dict[str, str]) -> str:
    result = text
    for src, dst in multi.items():
        result = result.replace(src, dst)
    return "".join(single.get(ch, ch) for ch in result)


_STRUCTURAL_HEADINGS = {
    "## Metadata",
    "## Editorial Transparency",
    "## Sources",
    "## Text",
    "## Quiz",
    "## Future Extensions",
    "### Revision history",
    "### Editorial history",
    "### Images",
    "### Illustrations",
    "### Audio narration",
    "### Pronunciation",
    "### Handwriting",
    "### Exercises",
    "### Vocabulary",
}


def should_preserve_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped in _STRUCTURAL_HEADINGS:
        return True
    if re.match(r"^### Question \d+$", stripped) or re.match(r"^### Source \d+", stripped):
        return True
    if stripped.startswith("http"):
        return True
    if "SPDX:" in stripped or "creativecommons.org" in stripped:
        return True
    if stripped.startswith("**Pack ID:**") or stripped.startswith("**Book ID:**"):
        return True
    if stripped.startswith("**Legacy Pack ID:**"):
        return True
    if stripped.startswith("**Version:**") or stripped.startswith("**Edition version:**"):
        return True
    if stripped.startswith("**Genres:**") or stripped.startswith("**Tags:**"):
        return True
    if stripped.startswith("**Writing system:**") or stripped.startswith("**Recommended"):
        return True
    if stripped.startswith("**Difficulty:**") or stripped.startswith("**Reader difficulty:**"):
        return True
    if stripped.startswith("**Estimated reading time:**"):
        return True
    if stripped.startswith("**Publication date:**"):
        return True
    if stripped.startswith("**Correct:**"):
        return True
    if stripped.startswith("**License:**") or stripped.startswith("**License URL:**"):
        return True
    if stripped.startswith("**URL:**") or stripped.startswith("**Retrieval date:**"):
        return True
    if stripped.startswith("**Source block:**"):
        return True
    if stripped.startswith("**Source video:**"):
        return True
    if stripped.startswith("**Source date (manuscript):**"):
        return True
    if stripped.startswith("**Availability:**") or stripped.startswith("**Deprecated:**"):
        return True
    if stripped.startswith("**Cover family:**") or stripped.startswith("**Audience:**"):
        return True
    if stripped.startswith("**Series:**") or stripped.startswith("**World:**"):
        return True
    if stripped.startswith("**LLM assisted:**") or stripped.startswith("**LLM model:**"):
        return True
    if stripped.startswith("**Human reviewed:**") or stripped.startswith("**Trust classification:**"):
        return True
    if stripped.startswith("**Created by:**") or stripped.startswith("**Editor:**"):
        return True
    if stripped.startswith("- places:") or stripped.startswith("- plants:"):
        return True
    if stripped.startswith("- objects:") or stripped.startswith("- creatures:"):
        return True
    if stripped.startswith("| Version") or stripped.startswith("|------") or stripped.startswith("| Date"):
        return True
    if re.match(r"^\| [\d.]+ \|", stripped):
        return True
    return False


def transform_value_line(line: str, multi: dict[str, str], single: dict[str, str]) -> str:
    """Transliterate values after known bold labels; preserve label keys."""
    m = re.match(r"^(\*\*[^*]+:\*\*\s*)(.*)$", line)
    if m:
        return m.group(1) + transliterate(m.group(2), multi, single)
    if line.lstrip().startswith("- A)") or line.lstrip().startswith("- B)") or line.lstrip().startswith("- C)") or line.lstrip().startswith("- D)"):
        prefix, _, rest = line.partition(") ")
        return prefix + ") " + transliterate(rest, multi, single)
    return transliterate(line, multi, single)


def transform_pack(text: str, target_locale: str) -> str:
    if target_locale == "isv_cyrl":
        multi, single = LATIN_TO_CYR_MULTI, LATIN_TO_CYR
        lang_value = "isv_cyrl"
    elif target_locale == "isv_glag":
        multi, single = LATIN_TO_GLAG_MULTI, LATIN_TO_GLAG
        lang_value = "isv_glag"
    else:
        raise ValueError(target_locale)

    out_lines: list[str] = []
    for line in text.splitlines():
        if "**Original language:**" in line:
            out_lines.append(f"**Original language:** {lang_value}  ")
            continue
        if should_preserve_line(line):
            # Still transliterate title H1 and localized label values on preserved structural lines? 
            # Headings starting with # are fully preserved (compile anchors).
            out_lines.append(line)
            continue
        out_lines.append(transform_value_line(line, multi, single))
    return "\n".join(out_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("isv_pack", type=Path, help="Path to books/<id>/isv/reading-pack.md")
    parser.add_argument("--targets", nargs="+", default=["isv_cyrl", "isv_glag"])
    args = parser.parse_args()

    source = args.isv_pack.read_text(encoding="utf-8")
    book_dir = args.isv_pack.parent.parent
    for target in args.targets:
        out_dir = book_dir / target
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "reading-pack.md"
        out_path.write_text(transform_pack(source, target), encoding="utf-8")
        print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
