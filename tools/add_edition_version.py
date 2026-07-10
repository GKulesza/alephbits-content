#!/usr/bin/env python3
"""Phase 73 — add explicit Edition version to every official reading-pack.md."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

for entry in manifest["packs"]:
    if entry.get("tier") != "official":
        continue
    rp = ROOT / entry["path"] / "reading-pack.md"
    text = rp.read_text(encoding="utf-8")
    if "**Edition version:**" in text:
        continue
    m = re.search(r"\*\*Version:\*\*\s*([^\n]+)", text)
    version = m.group(1).strip() if m else "1.0.0"
    text = text.replace(
        f"**Version:** {version}",
        f"**Version:** {version}  \n**Edition version:** {version}",
        1,
    )
    rp.write_text(text, encoding="utf-8")
    print(f"Added Edition version to {entry['bookId']}")

print("Done.")
