#!/usr/bin/env python3
"""Validate multilingual pilot editions for encoding and structural integrity."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|FIXME|TBD|PLACEHOLDER)\b|\[translation needed\]|lorem ipsum",
)


def validate_text(path: Path, text: str, issues: list[str]) -> None:
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        issues.append(f"{path}: not UTF-8 encodable ({exc})")
    nfc = unicodedata.normalize("NFC", text)
    if nfc != text:
        issues.append(f"{path}: not NFC-normalized")
    if PLACEHOLDER_RE.search(text):
        issues.append(f"{path}: placeholder-like string found")
    if "## Text" not in text or "## Quiz" not in text:
        issues.append(f"{path}: missing Text or Quiz section")
    if text.count("## Text") != 1 or text.count("## Quiz") != 1:
        issues.append(f"{path}: duplicated Text/Quiz section markers")
    # empty paragraphs check: three+ blank lines inside Text
    body = text.split("## Text", 1)[-1].split("## Quiz", 1)[0]
    if not body.strip():
        issues.append(f"{path}: empty Text section")


def validate_json(path: Path, issues: list[str]) -> None:
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        issues.append(f"{path}: broken JSON ({exc})")
        return
    if not isinstance(data, dict):
        issues.append(f"{path}: JSON root must be object")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args()
    issues: list[str] = []
    checked = 0
    for root in args.roots:
        for pack in root.rglob("reading-pack.md"):
            text = pack.read_text(encoding="utf-8")
            validate_text(pack, text, issues)
            checked += 1
        for generated in list(root.rglob("lesson.json")) + list(root.rglob("quiz.json")):
            validate_json(generated, issues)
            checked += 1
    print(f"checked {checked} files")
    if issues:
        print("ISSUES:")
        for issue in issues:
            print(f" - {issue}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
