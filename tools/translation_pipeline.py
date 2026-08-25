#!/usr/bin/env python3
"""AlephBits Translation Pipeline.

Repository-driven batch translation for the alephbits-content repository.

The pipeline discovers canonical books from `books/<book_id>/book.yaml`,
classifies every target edition, and creates or regenerates only editions
that are missing or stale. It never touches `final` editions unless
`--unlock-final` is passed. `isv_cyrl` and `isv_glag` are derived script
variants of the ISV Latin edition and are never independently
machine-translated.

State lives entirely in the repository itself:

  books/<book_id>/<locale>/reading-pack.md  **Translation status:**
  books/<book_id>/<locale>/reading-pack.md  **Translation source:**
  books/<book_id>/<locale>/reading-pack.md  **Translation source version:**

A rerun resumes from committed state; failed editions can simply be retried.
No database is required.

Usage:
  python3 tools/translation_pipeline.py                           # dry-run plan + report
  python3 tools/translation_pipeline.py --execute --translator builtin:copy
  python3 tools/translation_pipeline.py --execute --translator path/to/translator.py
  python3 tools/translation_pipeline.py --execute --translator builtin:copy --unlock-final
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import util as importlib_util
from pathlib import Path
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Canonical content locales (repository identity — do not duplicate families).
# ---------------------------------------------------------------------------

#: Locale used as the translation source when book.yaml has no default_locale.
DEFAULT_SOURCE_LOCALE = "pl"

#: Independent translation targets (Latin script ISV is one target).
TRANSLATION_TARGET_LOCALES = ["en", "es", "eo", "isv"]

#: Derived script variants of the ISV Latin edition — NOT translation targets.
DERIVED_SCRIPT_LOCALES = ["isv_cyrl", "isv_glag"]

ALL_TARGET_LOCALES = TRANSLATION_TARGET_LOCALES + DERIVED_SCRIPT_LOCALES

VALID_TRANSLATION_STATUSES = ("machine", "reviewed", "final")

# ---------------------------------------------------------------------------
# Version handling
# ---------------------------------------------------------------------------


def parse_version(text: Optional[str]) -> tuple:
    """Parse a version string into a comparable integer tuple.

    Accepts `1.5` and `1.0.0`; missing/non-numeric parts are dropped and
    shorter tuples are padded with zeroes during comparison.
    """
    if not text:
        return ()
    parts = re.findall(r"\d+", text)
    return tuple(int(part) for part in parts)


def compare_versions(a: Optional[str], b: Optional[str]) -> int:
    """Compare two version strings. -1, 0, 1 (a < b, a == b, a > b).

    An unparseable/missing version compares lower than any parseable one;
    two unparseable versions compare equal.
    """
    va, vb = parse_version(a), parse_version(b)
    if not va and not vb:
        return 0
    if not va:
        return -1
    if not vb:
        return 1
    length = max(len(va), len(vb))
    pa = va + (0,) * (length - len(va))
    pb = vb + (0,) * (length - len(vb))
    return (pa > pb) - (pa < pb)


# ---------------------------------------------------------------------------
# reading-pack.md field parsing
# ---------------------------------------------------------------------------

_FIELD_RE = re.compile(r"^\*\*([^*:]+):\*\*\s*(.*)$")


def parse_edition_fields(markdown: str) -> dict:
    """Extract `**Key:** value` lines from a reading-pack.md document."""
    fields: dict = {}
    for raw in markdown.splitlines():
        match = _FIELD_RE.match(raw.strip())
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def _replace_field(lines: list, key: str, value: str) -> list:
    pattern = re.compile(rf"^\*\*{re.escape(key)}:\*\*.*$")
    out: list = []
    replaced = False
    for line in lines:
        if not replaced and pattern.match(line.strip()):
            out.append(f"**{key}:** {value}  ")
            replaced = True
        else:
            out.append(line)
    return out


_TRANS_FIELD_RE = re.compile(r"^\*\*Translation (status|source|source version):\*\*.*$")


def _replace_or_insert_translation_fields(lines: list, insert_lines: list) -> list:
    """Remove existing Translation * fields and insert them after `Original language`."""
    stripped = [line for line in lines if not _TRANS_FIELD_RE.match(line.strip())]
    out: list = []
    inserted = False
    for line in stripped:
        out.append(line)
        if not inserted and line.strip().startswith("**Original language:**"):
            out.extend(insert_lines)
            inserted = True
    if not inserted:
        # Fall back to inserting right after the Metadata header.
        for i, line in enumerate(out):
            if line.strip() == "## Metadata":
                out = out[: i + 1] + insert_lines + out[i + 1 :]
                inserted = True
                break
    if not inserted:
        out = insert_lines + out
    return out


def patch_translation_metadata(
    markdown: str,
    *,
    book_id: str,
    target_locale: str,
    source_locale: str,
    source_version: str,
    status: str,
) -> str:
    """Make a translated/derived reading-pack.md self-describing.

    Mirrors the source edition version, retargets `Original language`, and
    stamps the translation provenance (status/source/source version). It
    never translates prose — the caller is responsible for localized fields.
    """
    lines = markdown.split("\n")
    lines = _replace_field(lines, "Version", source_version)
    lines = _replace_field(lines, "Edition version", source_version)
    lines = _replace_field(lines, "Original language", target_locale)
    insert_lines = [
        f"**Translation status:** {status}  ",
        f"**Translation source:** {book_id}:{source_locale}  ",
        f"**Translation source version:** {source_version}  ",
    ]
    lines = _replace_or_insert_translation_fields(lines, insert_lines)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Quiz answer-order guard
# ---------------------------------------------------------------------------


def quiz_shape(markdown: str) -> list:
    """Answer counts per question, in order (structural shape of the quiz).

    A translation must keep the same shape as its source edition so the
    positional `correctIndex` in the compiler keeps pointing at the same
    semantic answer.
    """
    shape: list = []
    for block in re.split(r"^### Question \d+\s*$", markdown, flags=re.MULTILINE):
        if "**Question:**" not in block:
            continue
        in_answers = False
        count = 0
        for line in block.splitlines():
            stripped = line.strip()
            if stripped == "**Answers:**":
                in_answers = True
                continue
            if in_answers:
                if stripped.startswith("**"):
                    break
                if stripped.startswith("- ") and len(stripped) > 2:
                    count += 1
        shape.append(count)
    return shape


def quiz_shape_matches(source_markdown: str, target_markdown: str) -> bool:
    """True when both documents carry an identical quiz structure.

    This protects the positional `correctIndex` invariant: answer count and
    order per question must survive translation.
    """
    return quiz_shape(source_markdown) == quiz_shape(target_markdown)


# ---------------------------------------------------------------------------
# Translators
# ---------------------------------------------------------------------------

Translator = Callable[..., str]

TRANSLATOR_REGISTRY: dict = {}


def register_translator(name: str):
    def decorator(fn):
        TRANSLATOR_REGISTRY[name] = fn
        return fn

    return decorator


@register_translator("copy")
def translate_copy(
    source_markdown: str,
    *,
    source_locale: str,
    target_locale: str,
) -> str:
    """Structural test translator.

    Produces a structurally valid reading-pack.md whose prose is the source
    text verbatim. Intended to exercise pipeline mechanics only — plug a real
    machine-translation provider in via `--translator`.
    """
    out: list = []
    for line in source_markdown.split("\n"):
        if line.startswith("**Original language:**"):
            out.append(f"**Original language:** {target_locale}  ")
        else:
            out.append(line)
    return "\n".join(out)


def load_translator(spec: str) -> Translator:
    """Resolve `builtin:<name>` or a python module exposing
    `translate(source_markdown, *, source_locale, target_locale) -> str`."""
    if spec.startswith("builtin:"):
        name = spec[len("builtin:") :]
        if name not in TRANSLATOR_REGISTRY:
            raise ValueError(
                f"unknown builtin translator '{name}' "
                f"(available: {', '.join(sorted(TRANSLATOR_REGISTRY))})"
            )
        return TRANSLATOR_REGISTRY[name]

    path = Path(spec).resolve()
    if not path.is_file():
        raise ValueError(f"translator module not found: {path}")
    module_name = f"alephbits_translator_{path.stem}"
    module_spec = importlib_util.spec_from_file_location(module_name, path)
    module = importlib_util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    fn = getattr(module, "translate", None)
    if not callable(fn):
        raise ValueError(
            f"{path}: expected a callable `translate(source_markdown, *, "
            "source_locale, target_locale) -> str`"
        )
    return fn


# ---------------------------------------------------------------------------
# Repository discovery
# ---------------------------------------------------------------------------


def discover_books(repo_root: Path) -> list:
    """All canonical books (directories with book.yaml), sorted deterministically."""
    books_dir = repo_root / "books"
    if not books_dir.is_dir():
        return []
    return sorted(
        d.name
        for d in books_dir.iterdir()
        if d.is_dir() and (d / "book.yaml").exists()
    )


def book_source_locale(book_dir: Path) -> str:
    """default_locale from book.yaml, falling back to the repository default."""
    yaml_file = book_dir / "book.yaml"
    if yaml_file.is_file():
        for raw in yaml_file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("default_locale:"):
                value = line.split(":", 1)[1].strip().strip('"').strip("'")
                if value:
                    return value
    return DEFAULT_SOURCE_LOCALE


def edition_dir(repo_root: Path, book_id: str, locale: str) -> Path:
    return repo_root / "books" / book_id / locale


def edition_markdown(repo_root: Path, book_id: str, locale: str) -> Optional[str]:
    md = edition_dir(repo_root, book_id, locale) / "reading-pack.md"
    if not md.is_file():
        return None
    return md.read_text(encoding="utf-8")


def edition_version(repo_root: Path, book_id: str, locale: str) -> Optional[str]:
    md = edition_markdown(repo_root, book_id, locale)
    if md is None:
        return None
    fields = parse_edition_fields(md)
    return fields.get("Version") or None


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

#: state -> human description used by reports.
STATE_LABELS = {
    "missing": "missing",
    "incomplete": "incomplete",
    "unclassified": "unclassified",
    "current": "current",
    "stale": "stale",
    "reviewed_stale": "reviewed-stale",
    "final": "final",
    "ahead": "ahead",
    "source": "source",
    "not_target": "not-target",
    "unknown_source": "unknown-source",
}


@dataclass(frozen=True)
class EditionState:
    book_id: str
    locale: str
    state: str
    action: str  # skip | create | regenerate | transliterate | recompile
    kind: str  # translation | derived
    status: Optional[str] = None
    edition_version: Optional[str] = None
    translation_source_version: Optional[str] = None
    translation_source: Optional[str] = None
    src_locale: Optional[str] = None
    src_version: Optional[str] = None
    reason: Optional[str] = None


def classify_edition(
    *,
    repo_root: Path,
    book_id: str,
    locale: str,
    src_locale: str,
    src_version: Optional[str],
    unlock_final: bool = False,
    regenerate_reviewed: bool = False,
) -> EditionState:
    """Classify one (book, locale) edition against its source edition.

    Repository state alone decides the outcome, which makes reruns resume
    partial batches without any external job database.
    """
    kind = "derived" if locale in DERIVED_SCRIPT_LOCALES else "translation"
    if locale == src_locale:
        return EditionState(book_id, locale, "source", "skip", kind)
    if locale not in ALL_TARGET_LOCALES:
        return EditionState(book_id, locale, "not_target", "skip", kind)

    md_path = edition_dir(repo_root, book_id, locale) / "reading-pack.md"
    lesson_path = edition_dir(repo_root, book_id, locale) / "lesson.json"

    if not md_path.is_file():
        if kind == "derived" and not src_version:
            return EditionState(
                book_id,
                locale,
                "unknown_source",
                "skip",
                kind,
                reason="derived source edition (isv) is missing",
            )
        action = "transliterate" if kind == "derived" else "create"
        return EditionState(book_id, locale, "missing", action, kind)

    markdown = md_path.read_text(encoding="utf-8")
    fields = parse_edition_fields(markdown)
    status = (fields.get("Translation status") or "").strip().lower()
    translation_source = fields.get("Translation source") or None
    translation_source_version = fields.get("Translation source version") or None
    edition_version = fields.get("Version") or None

    common = dict(
        book_id=book_id,
        locale=locale,
        kind=kind,
        status=status or None,
        edition_version=edition_version,
        translation_source_version=translation_source_version,
        translation_source=translation_source,
        src_locale=src_locale,
        src_version=src_version,
    )

    if status not in VALID_TRANSLATION_STATUSES:
        # Legacy edition without translation metadata — provenance unknown.
        # Never overwrite it silently.
        return EditionState(
            state="unclassified",
            action="skip",
            reason="missing translation metadata",
            **common,
        )

    if status == "final" and not unlock_final:
        return EditionState(
            state="final",
            action="skip",
            reason="protected final edition",
            **common,
        )

    # Generated artifacts missing — deterministic recompile from the committed
    # reading-pack.md is always safe (it never rewrites the editorial source).
    if not lesson_path.is_file():
        return EditionState(
            state="incomplete",
            action="recompile",
            reason="generated artifacts missing",
            **common,
        )

    if not src_version:
        return EditionState(
            state="unknown_source",
            action="skip",
            reason="source edition has no version",
            **common,
        )

    if not translation_source_version:
        return EditionState(
            state="unclassified",
            action="skip",
            reason="translation source version missing",
            **common,
        )

    comparison = compare_versions(translation_source_version, src_version)
    if comparison == 0:
        return EditionState(state="current", action="skip", **common)
    if comparison > 0:
        return EditionState(
            state="ahead",
            action="skip",
            reason="recorded source version is newer than current source",
            **common,
        )

    if status == "reviewed" and not regenerate_reviewed:
        return EditionState(
            state="reviewed_stale",
            action="skip",
            reason="reviewed edition is stale; pass --regenerate-reviewed to replace it",
            **common,
        )

    action = "transliterate" if kind == "derived" else "regenerate"
    return EditionState(state="stale", action=action, **common)


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------


@dataclass
class Plan:
    repo_root: Path
    books: list
    jobs: list = field(default_factory=list)
    errors: list = field(default_factory=list)


def plan(
    repo_root: Path,
    *,
    selected_books: Optional[list] = None,
    selected_locales: Optional[list] = None,
    unlock_final: bool = False,
    regenerate_reviewed: bool = False,
) -> Plan:
    result = Plan(repo_root=repo_root, books=discover_books(repo_root))
    if not result.books:
        result.errors.append("no canonical books found under books/ (missing book.yaml)")
        return result

    locales = [locale for locale in ALL_TARGET_LOCALES if not selected_locales or locale in selected_locales]

    for book_id in result.books:
        if selected_books and book_id not in selected_books:
            continue
        source_locale = book_source_locale(repo_root / "books" / book_id)
        source_version = edition_version(repo_root, book_id, source_locale)
        if not source_version:
            result.errors.append(f"{book_id}: source edition {source_locale} has no Version")
            continue
        isv_version = edition_version(repo_root, book_id, "isv")

        for locale in locales:
            if locale in DERIVED_SCRIPT_LOCALES:
                src_locale, src_version = "isv", isv_version
            else:
                src_locale, src_version = source_locale, source_version
            result.jobs.append(
                classify_edition(
                    repo_root=repo_root,
                    book_id=book_id,
                    locale=locale,
                    src_locale=src_locale,
                    src_version=src_version,
                    unlock_final=unlock_final,
                    regenerate_reviewed=regenerate_reviewed,
                )
            )
    return result


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _state_counts(jobs: list) -> Counter:
    return Counter(job.state for job in jobs)


def summarize(plan_result: Plan) -> dict:
    per_locale: dict = {}
    for job in plan_result.jobs:
        bucket = per_locale.setdefault(job.locale, Counter())
        bucket[job.state] += 1
    totals = _state_counts(plan_result.jobs)
    return {
        "booksDiscovered": len(plan_result.books),
        "editionsEvaluated": len(plan_result.jobs),
        "perLocale": {
            locale: dict(counts) for locale, counts in sorted(per_locale.items())
        },
        "totals": dict(totals),
        "errors": list(plan_result.errors),
    }


def render_human_report(plan_result: Plan, *, executing: bool) -> str:
    lines = ["AlephBits Translation Run", f"Repository: {plan_result.repo_root}"]
    lines.append(
        f"Books discovered: {len(plan_result.books)}"
        f" | Editions evaluated: {len(plan_result.jobs)}"
    )
    lines.append(
        "Mode: execute" if executing else "Mode: dry-run (no files will be written)"
    )

    per_locale: dict = {}
    for job in plan_result.jobs:
        per_locale.setdefault(job.locale, []).append(job)

    display_order = sorted(
        per_locale,
        key=lambda locale: (locale in TRANSLATION_TARGET_LOCALES, locale),
    )
    for locale in display_order:
        counts = _state_counts(per_locale[locale])
        header = locale.upper() if locale in TRANSLATION_TARGET_LOCALES else locale
        lines.append(f"{header}")
        for state in (
            "missing",
            "stale",
            "current",
            "final",
            "reviewed_stale",
            "unclassified",
            "incomplete",
            "ahead",
            "unknown_source",
        ):
            if counts.get(state):
                lines.append(f"  {STATE_LABELS[state]}: {counts[state]}")
        if not any(counts.get(state) for state in ("missing", "stale", "current", "final")):
            lines.append("  (no translatable editions)")

    totals = _state_counts(plan_result.jobs)
    action_counts = Counter(job.action for job in plan_result.jobs)
    transliterated_planned = action_counts["transliterate"]
    lines.append("")
    lines.append(f"Created: {totals['missing']}")
    lines.append(f"Regenerated: {totals['stale']}")
    lines.append(f"Transliterated: {transliterated_planned}")
    lines.append(f"Recompiled: {totals['incomplete']}")
    lines.append(f"Skipped current: {totals['current']}")
    lines.append(f"Skipped final: {totals['final']}")
    lines.append(f"Skipped reviewed-stale: {totals['reviewed_stale']}")
    lines.append(f"Skipped unclassified: {totals['unclassified']}")
    lines.append(f"Failed: 0")
    for error in plan_result.errors:
        lines.append(f"ERROR: {error}")
    return "\n".join(lines) + "\n"


def report_json(plan_result: Plan, *, executing: bool, run_summary: Optional[dict] = None) -> str:
    return json.dumps(
        {
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "mode": "execute" if executing else "dry-run",
            **summarize(plan_result),
            "run": run_summary,
        },
        indent=2,
        sort_keys=True,
    )


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".translation-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def compile_edition(repo_root: Path, book_id: str, locale: str) -> tuple:
    """Compile a locale directory through the canonical compile_pack tool."""
    result = subprocess.run(
        ["dart", "run", "tools/compile_pack.dart", "--overwrite", f"books/{book_id}/{locale}"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=600,
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip()


def run_compile_pack(repo_root: Path, book_id: str, locale: str) -> tuple:
    ok, output = compile_edition(repo_root, book_id, locale)
    if not ok:
        raise RuntimeError(f"compile_pack failed for {book_id}:{locale}\n{output}")
    return ok, output


def execute(
    plan_result: Plan,
    *,
    translator: Optional[Translator],
    status: str,
    build_manifest: bool = False,
    validate: bool = False,
) -> dict:
    created: list = []
    regenerated: list = []
    transliterated: list = []
    recompiled: list = []
    failed: list = []

    if plan_result.errors:
        return {
            "created": created,
            "regenerated": regenerated,
            "transliterated": transliterated,
            "recompiled": recompiled,
            "failed": [f"plan error: {error}" for error in plan_result.errors],
        }

    from generate_isv_script_editions import transform_pack  # tools/ sibling module

    for job in plan_result.jobs:
        edition = f"{job.book_id}:{job.locale}"
        if job.action == "skip":
            continue

        source_md = edition_markdown(plan_result.repo_root, job.book_id, job.src_locale)
        if source_md is None:
            failed.append(f"{edition}: source edition {job.src_locale} missing")
            continue

        try:
            if job.action in ("create", "regenerate"):
                if translator is None:
                    failed.append(
                        f"{edition}: translation required but no --translator provided "
                        "(pass --translator builtin:copy or a module path)"
                    )
                    continue
                translated = translator(
                    source_md,
                    source_locale=job.src_locale,
                    target_locale=job.locale,
                )
                translated = patch_translation_metadata(
                    translated,
                    book_id=job.book_id,
                    target_locale=job.locale,
                    source_locale=job.src_locale,
                    source_version=job.src_version,
                    status=status,
                )
                if not quiz_shape_matches(source_md, translated):
                    failed.append(
                        f"{edition}: quiz answer-order/structural guard failed — "
                        "translation changed the number of questions or answers"
                    )
                    continue
                write_text_atomic(
                    edition_dir(plan_result.repo_root, job.book_id, job.locale)
                    / "reading-pack.md",
                    translated,
                )
                run_compile_pack(plan_result.repo_root, job.book_id, job.locale)
                if job.action == "create":
                    created.append(edition)
                else:
                    regenerated.append(edition)

            elif job.action == "transliterate":
                transformed = transform_pack(source_md, job.locale)
                transformed = patch_translation_metadata(
                    transformed,
                    book_id=job.book_id,
                    target_locale=job.locale,
                    source_locale="isv",
                    source_version=job.src_version,
                    status=status,
                )
                if not quiz_shape_matches(source_md, transformed):
                    failed.append(
                        f"{edition}: quiz answer-order/structural guard failed during "
                        "ISV script derivation"
                    )
                    continue
                write_text_atomic(
                    edition_dir(plan_result.repo_root, job.book_id, job.locale)
                    / "reading-pack.md",
                    transformed,
                )
                run_compile_pack(plan_result.repo_root, job.book_id, job.locale)
                transliterated.append(edition)

            elif job.action == "recompile":
                run_compile_pack(plan_result.repo_root, job.book_id, job.locale)
                recompiled.append(edition)
        except Exception as error:  # per-edition isolation — never abort the batch
            failed.append(f"{edition}: {error}")

    if build_manifest:
        manifest_result = subprocess.run(
            ["dart", "run", "tools/build_manifest.dart", "--overwrite"],
            cwd=str(plan_result.repo_root),
            capture_output=True,
            text=True,
            timeout=600,
        )
        if manifest_result.returncode != 0:
            failed.append(
                "build_manifest failed: "
                + ((manifest_result.stdout or "") + (manifest_result.stderr or "")).strip()
            )

    if validate:
        validate_result = subprocess.run(
            ["dart", "run", "scripts/validate_pack.dart"],
            cwd=str(plan_result.repo_root),
            capture_output=True,
            text=True,
            timeout=900,
        )
        if validate_result.returncode != 0:
            failed.append(
                "validate_pack failed: "
                + ((validate_result.stdout or "") + (validate_result.stderr or "")).strip()
            )

    return {
        "created": created,
        "regenerated": regenerated,
        "transliterated": transliterated,
        "recompiled": recompiled,
        "failed": failed,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AlephBits translation pipeline — plan and execute repository-driven "
        "batch translation for alephbits-content.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Edition state is read from the repository itself:\n"
            "  **Translation status:**  machine | reviewed | final\n"
            "  **Translation source:**  <bookId>:<source-locale>\n"
            "  **Translation source version:** <version>\n\n"
            "Final editions are never overwritten unless --unlock-final is passed.\n"
            "Reviewed editions that are stale are reported and skipped unless "
            "--regenerate-reviewed is passed."
        ),
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually create/regenerate editions (default is a dry-run plan).",
    )
    parser.add_argument(
        "--translator",
        default=None,
        help="Translator: `builtin:copy` or a python module exposing "
        "`translate(source_markdown, *, source_locale, target_locale) -> str`. "
        "Required to create/regenerate.",
    )
    parser.add_argument(
        "--status",
        choices=["machine", "reviewed"],
        default="machine",
        help="Translation status stamped on newly generated editions (default: machine).",
    )
    parser.add_argument(
        "--unlock-final",
        action="store_true",
        help="DESTRUCTIVE: allow regenerating final editions. Never use in normal runs.",
    )
    parser.add_argument(
        "--regenerate-reviewed",
        action="store_true",
        help="Allow regenerating stale reviewed (non-final) editions. "
        "Without it, stale reviewed editions are reported and skipped.",
    )
    parser.add_argument(
        "--books",
        default=None,
        help="Comma-separated book ids to limit the run (default: all canonical books).",
    )
    parser.add_argument(
        "--locales",
        default=None,
        help="Comma-separated target locales (default: all targets).",
    )
    parser.add_argument(
        "--build-manifest",
        action="store_true",
        help="Run build_manifest --overwrite after a successful execution.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validate_pack after execution.",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Repository root (default: current working directory).",
    )
    parser.add_argument(
        "--report-json",
        default=None,
        help="Write the machine-readable report to this path.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list] = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo or os.getcwd()).resolve()

    selected_books = [b.strip() for b in args.books.split(",")] if args.books else None
    selected_locales = [l.strip() for l in args.locales.split(",")] if args.locales else None
    if selected_locales:
        invalid = [l for l in selected_locales if l not in ALL_TARGET_LOCALES]
        if invalid:
            print(
                f"ERROR: unknown target locale(s): {', '.join(invalid)} "
                f"(targets: {', '.join(TRANSLATION_TARGET_LOCALES)}; "
                f"derived: {', '.join(DERIVED_SCRIPT_LOCALES)})",
                file=sys.stderr,
            )
            return 1

    plan_result = plan(
        repo_root,
        selected_books=selected_books,
        selected_locales=selected_locales,
        unlock_final=args.unlock_final,
        regenerate_reviewed=args.regenerate_reviewed,
    )

    run_summary = None
    exit_code = 0
    if args.execute:
        translator = None
        if args.translator:
            try:
                translator = load_translator(args.translator)
            except (ValueError, OSError, ImportError) as error:
                print(f"ERROR: {error}", file=sys.stderr)
                return 1
        run_summary = execute(
            plan_result,
            translator=translator,
            status=args.status,
            build_manifest=args.build_manifest,
            validate=args.validate,
        )
        if run_summary["failed"]:
            exit_code = 1

    print(render_human_report(plan_result, executing=args.execute))

    if run_summary is not None:
        counts = {
            "created": len(run_summary["created"]),
            "regenerated": len(run_summary["regenerated"]),
            "transliterated": len(run_summary["transliterated"]),
            "recompiled": len(run_summary["recompiled"]),
            "failed": len(run_summary["failed"]),
        }
        print(
            f"Executed: created {counts['created']}, regenerated {counts['regenerated']}, "
            f"transliterated {counts['transliterated']}, "
            f"recompiled {counts['recompiled']}, failed {counts['failed']}"
        )
        for failure in run_summary["failed"]:
            print(f"FAILED: {failure}", file=sys.stderr)

    if args.report_json:
        output = report_json(plan_result, executing=args.execute, run_summary=run_summary)
        Path(args.report_json).write_text(output + "\n", encoding="utf-8")

    if plan_result.errors:
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
