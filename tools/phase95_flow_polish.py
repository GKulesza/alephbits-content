#!/usr/bin/env python3
"""Phase 95 — safe reading-flow polish (structure only, no literary rewrites)."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKS = REPO_ROOT / "official" / "glagolitic" / "pl"


def collapse_duplicate_rules(md: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    original = md

    # Triple or double horizontal rules with blank lines between
    while re.search(r"^---\s*\n\s*\n---\s*$", md, re.M):
        md = re.sub(r"^---\s*\n\s*\n---\s*$", "---", md, flags=re.M)
        changes.append("collapsed duplicate ---")

    # --- followed immediately by another --- on next non-empty line block
    prev = None
    while prev != md:
        prev = md
        md = re.sub(r"(^---\s*\n)\s*\n(?=---\s*$)", r"\1", md, flags=re.M)

    # Extra blank line before ## Quiz after ---
    md = re.sub(r"^---\s*\n\s*\n\s*\n(?=## Quiz)", "---\n\n", md, flags=re.M)

    # Ensure Metadata block ends with --- before Editorial when missing
    if "## Editorial Transparency" in md and "**Cover family:**" in md:
        md = re.sub(
            r"(\*\*Cover family:\*\*[^\n]+)\n\n(?=## Editorial Transparency)",
            r"\1\n\n---\n\n",
            md,
            count=1,
        )

    if md != original and "collapsed duplicate ---" not in changes:
        changes.append("normalized section spacing")

    return md, changes


def polish_file(path: Path) -> list[str]:
    md = path.read_text(encoding="utf-8")
    new_md, changes = collapse_duplicate_rules(md)
    if new_md != md:
        path.write_text(new_md, encoding="utf-8")
    return changes


def main() -> None:
    total = 0
    for pack_dir in sorted(PACKS.iterdir()):
        rp = pack_dir / "reading-pack.md"
        if not rp.exists():
            continue
        changes = polish_file(rp)
        if changes:
            total += 1
            print(f"{pack_dir.name}: {', '.join(changes)}")
    print(f"Polished {total} pack(s)")


if __name__ == "__main__":
    main()
