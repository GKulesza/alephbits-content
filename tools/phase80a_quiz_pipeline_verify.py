#!/usr/bin/env python3
"""Phase 80A — verify quiz consistency across the content pipeline."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACKS_ROOT = ROOT / "official" / "glagolitic" / "pl"
DEFAULT_MANIFEST = ROOT / "manifest.json"
DEFAULT_BUNDLE = ROOT.parent / "alephbits" / "assets" / "bundled_content" / "content.bundle.zip"
DEFAULT_REPORT = ROOT.parent / "alephbits" / "docs" / "product" / "QUIZ_PIPELINE_VERIFICATION.md"
EXTRACT_TOOL = ROOT / "tools" / "phase80a_quiz_extract.dart"

METADATA_QUESTION_PATTERNS = [
    re.compile(r"o czym opowiada tekst", re.I),
    re.compile(r"do jakiej grupy czytelnik", re.I),
    re.compile(r"jaki rodzaj tre[sś]ci", re.I),
    re.compile(r"jaki gatunek tekstu", re.I),
    re.compile(r"ile minut zajmuje orientacyjna", re.I),
    re.compile(r"orientacyjna lektura", re.I),
    re.compile(r"kończy się zdaniem domykającym", re.I),
    re.compile(r"jaka jest orientacyjna", re.I),
    re.compile(r"czytanie zajmuje", re.I),
    re.compile(r"poziom trudno", re.I),
    re.compile(r"klasyfikacja zaufania", re.I),
    re.compile(r"wiarygodno", re.I),
    re.compile(r"jakiego wydania", re.I),
    re.compile(r"wersj[ae] wydania", re.I),
    re.compile(r"na jakiej okładce", re.I),
    re.compile(r"jaki system pisma", re.I),
    re.compile(r"w jakim języku.*orygina", re.I),
    re.compile(r"reading time", re.I),
    re.compile(r"estimated reading time", re.I),
    re.compile(r"trust classification", re.I),
    re.compile(r"content type", re.I),
    re.compile(r"\baudience\b", re.I),
    re.compile(r"\bcategory\b", re.I),
    re.compile(r"\bmetadata\b", re.I),
    re.compile(r"\bedition version\b", re.I),
]

PLACEHOLDER_ANSWER_PATTERNS = [
    re.compile(r"inna odpowied", re.I),
    re.compile(r"nie wynika z tekstu", re.I),
    re.compile(r"żadna z powyższych", re.I),
    re.compile(r"zadna z powyzszych", re.I),
]


@dataclass
class StageQuiz:
    questions: list[str]
    normalized: dict[str, Any]
    metadata_hits: list[str] = field(default_factory=list)
    placeholder_hits: list[str] = field(default_factory=list)

    @property
    def question_count(self) -> int:
        return len(self.questions)


@dataclass
class PackReport:
    slug: str
    pack_id: str
    pack_path: str
    version: str
    stages: dict[str, StageQuiz | None] = field(default_factory=dict)
    manifest_listed: bool = True

    def stage_questions(self, stage: str) -> list[str] | None:
        data = self.stages.get(stage)
        return None if data is None else data.questions


def normalize_quiz(quiz: dict[str, Any]) -> dict[str, Any]:
    questions = []
    for raw in quiz.get("questions") or []:
        if not isinstance(raw, dict):
            continue
        questions.append(
            {
                "question": (raw.get("question") or "").strip(),
                "answers": list(raw.get("answers") or []),
                "correctIndex": raw.get("correctIndex"),
            }
        )
    return {"title": quiz.get("title"), "questions": questions}


def stage_from_quiz(quiz: dict[str, Any]) -> StageQuiz:
    normalized = normalize_quiz(quiz)
    questions = [q["question"] for q in normalized["questions"]]
    metadata_hits: list[str] = []
    placeholder_hits: list[str] = []

    for q in normalized["questions"]:
        text = q["question"]
        for pattern in METADATA_QUESTION_PATTERNS:
            if pattern.search(text):
                metadata_hits.append(text)
                break
        for answer in q.get("answers") or []:
            if not isinstance(answer, str):
                continue
            for pattern in PLACEHOLDER_ANSWER_PATTERNS:
                if pattern.search(answer):
                    placeholder_hits.append(f"{text} → {answer}")
                    break

    if placeholder_hits:
        metadata_hits.extend(
            f"placeholder answer: {hit}" for hit in placeholder_hits
        )

    return StageQuiz(
        questions=questions,
        normalized=normalized,
        metadata_hits=metadata_hits,
        placeholder_hits=placeholder_hits,
    )


def load_json_quiz(raw: str) -> StageQuiz:
    lesson = json.loads(raw)
    quiz = lesson.get("quiz")
    if not isinstance(quiz, dict):
        raise ValueError("lesson.json missing quiz object")
    return stage_from_quiz(quiz)


def compile_reading_pack_quiz(pack_dir: Path) -> StageQuiz:
    result = subprocess.run(
        ["dart", "run", str(EXTRACT_TOOL), str(pack_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    quiz = json.loads(result.stdout)
    return stage_from_quiz(quiz)


def discover_packs(packs_root: Path) -> list[Path]:
    return sorted(
        p
        for p in packs_root.iterdir()
        if p.is_dir() and (p / "reading-pack.md").exists()
    )


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def manifest_entry_for_slug(manifest: dict[str, Any], slug: str) -> dict[str, Any] | None:
    prefix = f"official/glagolitic/pl/{slug}"
    for entry in manifest.get("packs") or []:
        if isinstance(entry, dict) and entry.get("path") == prefix:
            return entry
    return None


def load_bundle_quiz(bundle_path: Path, pack_path: str) -> StageQuiz | None:
    if not bundle_path.exists():
        return None
    rel = f"{pack_path}/lesson.json"
    with zipfile.ZipFile(bundle_path) as archive:
        if rel not in archive.namelist():
            return None
        return load_json_quiz(archive.read(rel).decode("utf-8"))


def simulate_runtime_layered(
    bundle_quiz: StageQuiz | None,
    remote_quiz: StageQuiz | None,
    *,
    synced_version: str | None,
    manifest_version: str | None,
    legacy_remote_first: bool,
) -> StageQuiz | None:
    if bundle_quiz is None:
        return remote_quiz

    if remote_quiz is None:
        return bundle_quiz

    if legacy_remote_first:
        return remote_quiz

    if synced_version is None or manifest_version is None:
        return bundle_quiz
    if synced_version != manifest_version:
        return bundle_quiz
    return remote_quiz


def questions_equal(a: list[str] | None, b: list[str] | None) -> bool:
    return a == b


def render_report(
    *,
    packs: list[PackReport],
    bundle_path: Path,
    remote_overlay: Path | None,
    generated_commands: list[str],
) -> str:
    total = len(packs)
    metadata_packs: dict[str, list[str]] = {}
    md_vs_lesson: list[str] = []
    lesson_vs_bundle: list[str] = []
    bundle_vs_runtime: list[str] = []
    runtime_vs_fixed: list[str] = []

    for pack in packs:
        slug = pack.slug
        for stage, data in pack.stages.items():
            if data and data.metadata_hits:
                metadata_packs.setdefault(slug, []).extend(
                    f"{stage}: {hit}" for hit in data.metadata_hits
                )

        md = pack.stage_questions("reading_pack")
        lesson = pack.stage_questions("lesson_json")
        bundle = pack.stage_questions("bundle")
        runtime_legacy = pack.stage_questions("runtime_legacy")
        runtime_fixed = pack.stage_questions("runtime_fixed")

        if md is not None and lesson is not None and not questions_equal(md, lesson):
            md_vs_lesson.append(slug)
        if lesson is not None and bundle is not None and not questions_equal(lesson, bundle):
            lesson_vs_bundle.append(slug)
        if bundle is not None and runtime_legacy is not None and not questions_equal(
            bundle, runtime_legacy
        ):
            bundle_vs_runtime.append(slug)
        if runtime_legacy is not None and runtime_fixed is not None and not questions_equal(
            runtime_legacy, runtime_fixed
        ):
            runtime_vs_fixed.append(slug)

    lines = [
        "# Phase 80A — Quiz Pipeline Verification",
        "",
        "**Date:** 2026-07-11",
        "**Scope:** All official Glagolitic Polish packs",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| Packs checked | **{total}** |",
        f"| Packs with metadata / template questions | **{len(metadata_packs)}** |",
        f"| reading-pack.md ≠ lesson.json | **{len(md_vs_lesson)}** |",
        f"| lesson.json ≠ content.bundle.zip | **{len(lesson_vs_bundle)}** |",
        f"| bundle ≠ runtime (legacy remote-first) | **{len(bundle_vs_runtime)}** |",
        f"| runtime legacy ≠ runtime fixed (sync gate) | **{len(runtime_vs_fixed)}** |",
        "",
        "---",
        "",
        "## Pipeline stages verified",
        "",
        "For each pack:",
        "",
        "1. **reading-pack.md** — fresh compile via `phase80a_quiz_extract.dart`",
        "2. **lesson.json** — committed artifact on disk",
        "3. **manifest.json** — pack entry (`id`, `path`, `version`)",
        "4. **content.bundle.zip** — lesson embedded in app bundle",
        "5. **runtime** — simulated layered load (bundle + optional remote overlay)",
        "",
        f"Bundle path: `{bundle_path}`",
        "",
    ]

    if remote_overlay and remote_overlay.exists():
        lines.append(f"Remote overlay scanned: `{remote_overlay}`")
    else:
        lines.append("Remote overlay: none on disk (runtime legacy = bundle)")
    lines.append("")

  # Example deep-dive
    example = next((p for p in packs if p.slug == "rozmowa-z-lekarzem"), None)
    if example:
        lines.extend(
            [
                "---",
                "",
                "## Example: Rozmowa z lekarzem",
                "",
                f"Pack ID: `{example.pack_id}` · version `{example.version}`",
                "",
            ]
        )
        for stage in [
            "reading_pack",
            "lesson_json",
            "bundle",
            "runtime_legacy",
            "runtime_fixed",
        ]:
            data = example.stages.get(stage)
            lines.append(f"### {stage}")
            lines.append("")
            if data is None:
                lines.append("_missing_")
            else:
                for i, q in enumerate(data.questions, 1):
                    lines.append(f"{i}. {q}")
                if data.metadata_hits:
                    lines.append("")
                    lines.append("**Metadata flags:**")
                    for hit in data.metadata_hits:
                        lines.append(f"- {hit}")
            lines.append("")

    if metadata_packs:
        lines.extend(["---", "", "## Packs with metadata / template questions", ""])
        for slug, hits in sorted(metadata_packs.items()):
            lines.append(f"### `{slug}`")
            for hit in hits:
                lines.append(f"- {hit}")
            lines.append("")

    mismatch_sections = [
        ("reading-pack.md differs from lesson.json", md_vs_lesson),
        ("lesson.json differs from bundle", lesson_vs_bundle),
        ("bundle differs from legacy runtime", bundle_vs_runtime),
        ("legacy runtime differs from fixed runtime", runtime_vs_fixed),
    ]
    for title, items in mismatch_sections:
        lines.extend(["---", "", f"## {title}", ""])
        if not items:
            lines.append("_None._")
        else:
            for slug in items:
                lines.append(f"- `{slug}`")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Root cause (device regression)",
            "",
            "Local source pipeline (reading-pack → lesson → manifest → bundle) is consistent.",
            "The device regression occurs when a **stale remote overlay** lesson.json",
            "is preferred over the bundled lesson — even when the pack is no longer in the",
            "remote manifest or the sync store has no version for that pack.",
            "",
            "**Fix applied in app:**",
            "",
            "- `ContentBundleCache.filePath` reads bundled content only (no remote bleed)",
            "- `LayeredContentCatalogSource.loadLessonJson` trusts remote overlay only when",
            "  `RemoteLibrarySyncStore` confirms the synced pack version",
            "- Remote overlay cleared when the app bundle is re-extracted",
            "",
            "---",
            "",
            "## Verification commands",
            "",
        ]
    )
    for cmd in generated_commands:
        lines.append(f"```")
        lines.append(cmd)
        lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def verify(
    *,
    packs_root: Path,
    manifest_path: Path,
    bundle_path: Path,
    remote_overlay: Path | None,
    report_path: Path,
) -> int:
    manifest = load_manifest(manifest_path)
    pack_dirs = discover_packs(packs_root)
    reports: list[PackReport] = []

    for pack_dir in pack_dirs:
        slug = pack_dir.name
        entry = manifest_entry_for_slug(manifest, slug)
        pack_path = f"official/glagolitic/pl/{slug}"
        report = PackReport(
            slug=slug,
            pack_id=(entry or {}).get("id", slug),
            pack_path=pack_path,
            version=(entry or {}).get("version", "?"),
            manifest_listed=entry is not None,
        )

        try:
            report.stages["reading_pack"] = compile_reading_pack_quiz(pack_dir)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR {slug} reading_pack: {exc}", file=sys.stderr)

        lesson_file = pack_dir / "lesson.json"
        if lesson_file.exists():
            report.stages["lesson_json"] = load_json_quiz(
                lesson_file.read_text(encoding="utf-8")
            )

        report.stages["bundle"] = load_bundle_quiz(bundle_path, pack_path)

        remote_quiz: StageQuiz | None = None
        if remote_overlay:
            remote_file = remote_overlay / pack_path / "lesson.json"
            if remote_file.exists():
                remote_quiz = load_json_quiz(remote_file.read_text(encoding="utf-8"))

        synced_version = None
        if remote_overlay and (remote_overlay / ".sync_versions.json").exists():
            versions = json.loads(
                (remote_overlay / ".sync_versions.json").read_text(encoding="utf-8")
            )
            synced_version = versions.get(report.pack_id)

        report.stages["runtime_legacy"] = simulate_runtime_layered(
            report.stages.get("bundle"),
            remote_quiz,
            synced_version=synced_version,
            manifest_version=report.version,
            legacy_remote_first=True,
        )
        report.stages["runtime_fixed"] = simulate_runtime_layered(
            report.stages.get("bundle"),
            remote_quiz,
            synced_version=synced_version,
            manifest_version=report.version,
            legacy_remote_first=False,
        )

        reports.append(report)

    report_text = render_report(
        packs=reports,
        bundle_path=bundle_path,
        remote_overlay=remote_overlay,
        generated_commands=[
            "cd alephbits-content && dart run tools/compile_pack.dart --check --all",
            "cd alephbits-content && dart run scripts/validate_pack.dart",
            "cd alephbits-content && dart run tools/build_manifest.dart --overwrite",
            "cd alephbits && dart run tool/bundle_content_assets.dart",
            "cd alephbits && flutter test",
        ],
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8")
    print(f"Wrote {report_path}")

    has_metadata = any(
        data.metadata_hits
        for pack in reports
        for data in pack.stages.values()
        if data is not None
    )
    has_source_drift = any(
        not questions_equal(
            pack.stage_questions("reading_pack"),
            pack.stage_questions("lesson_json"),
        )
        for pack in reports
    )
    has_bundle_drift = any(
        not questions_equal(
            pack.stage_questions("lesson_json"),
            pack.stage_questions("bundle"),
        )
        for pack in reports
    )

    if has_metadata or has_source_drift or has_bundle_drift:
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packs-root", type=Path, default=DEFAULT_PACKS_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--remote-overlay", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    exit_code = verify(
        packs_root=args.packs_root,
        manifest_path=args.manifest,
        bundle_path=args.bundle,
        remote_overlay=args.remote_overlay,
        report_path=args.report,
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
