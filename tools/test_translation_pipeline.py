#!/usr/bin/env python3
"""Unit tests for the AlephBits translation pipeline.

Run with:
  python3 tools/test_translation_pipeline.py
  python3 -m unittest discover -s tools -p 'test_*.py'
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import translation_pipeline as tp


def pack_markdown(
    locale: str,
    version: str = "1.0.0",
    *,
    status=None,
    source=None,
    source_version=None,
    quiz=True,
) -> str:
    body = [
        "# Title",
        "",
        "## Metadata",
        "",
        "**Pack ID:** test",
        "**Book ID:** test",
        "**Original language:** %s  " % locale,
        "**Version:** %s  " % version,
        "**Edition version:** %s  " % version,
        "**Genres:** travel",
    ]
    if status:
        body.append("**Translation status:** %s  " % status)
        body.append("**Translation source:** %s  " % (source or "test:pl"))
        if source_version is not None:
            body.append("**Translation source version:** %s  " % source_version)
    body += [
        "",
        "## Editorial Transparency",
        "",
        "**License:** CC0 1.0 Universal (SPDX: CC0-1.0)",
        "",
        "## Text",
        "",
        "Some text.",
    ]
    if quiz:
        body += [
            "",
            "## Quiz",
            "",
            "**Quiz title:** Check",
            "",
            "### Question 1",
            "",
            "**Question:** Q one?",
            "",
            "**Answers:**",
            "- A) One",
            "- B) Two",
            "",
            "**Correct:** A",
            "",
            "### Question 2",
            "",
            "**Question:** Q two?",
            "",
            "**Answers:**",
            "- A) One",
            "- B) Two",
            "- C) Three",
            "",
            "**Correct:** B",
        ]
    return "\n".join(body) + "\n"


def write_book(root: Path, book_id: str = "test", source_locale: str = "pl") -> None:
    book_dir = root / "books" / book_id
    book_dir.mkdir(parents=True, exist_ok=True)
    (book_dir / "book.yaml").write_text(
        "book_id: %s\nstatus: official\ndefault_locale: %s\n" % (book_id, source_locale),
        encoding="utf-8",
    )
    write_edition(root, book_id, source_locale, version="1.0.0", lesson=True)


def write_edition(
    root: Path,
    book_id: str,
    locale: str,
    *,
    version: str,
    status=None,
    source=None,
    source_version=None,
    lesson=True,
) -> Path:
    edition = root / "books" / book_id / locale
    edition.mkdir(parents=True, exist_ok=True)
    md_path = edition / "reading-pack.md"
    md_path.write_text(
        pack_markdown(
            locale,
            version,
            status=status,
            source=source,
            source_version=source_version,
        ),
        encoding="utf-8",
    )
    if lesson:
        (edition / "lesson.json").write_text('{"id":"%s:%s"}' % (book_id, locale), encoding="utf-8")
    return md_path


class VersionTests(unittest.TestCase):
    def test_parse_versions(self):
        self.assertEqual(tp.parse_version("1.5"), (1, 5))
        self.assertEqual(tp.parse_version("1.0.0"), (1, 0, 0))
        self.assertEqual(tp.parse_version(""), ())
        self.assertEqual(tp.parse_version(None), ())
        self.assertEqual(tp.parse_version("v2.1-beta"), (2, 1))

    def test_compare_versions(self):
        self.assertEqual(tp.compare_versions("1.0.0", "1.0.0"), 0)
        self.assertEqual(tp.compare_versions("1.3", "1.5"), -1)
        self.assertEqual(tp.compare_versions("1.5", "1.3"), 1)
        self.assertEqual(tp.compare_versions("1.5", "1.5.0"), 0)
        self.assertEqual(tp.compare_versions("1.10", "1.9"), 1)
        self.assertEqual(tp.compare_versions(None, "1.0"), -1)
        self.assertEqual(tp.compare_versions(None, None), 0)


class TargetLocaleTests(unittest.TestCase):
    def test_derived_script_locales_are_not_translation_targets(self):
        for locale in tp.DERIVED_SCRIPT_LOCALES:
            self.assertNotIn(locale, tp.TRANSLATION_TARGET_LOCALES)
            self.assertIn(locale, tp.ALL_TARGET_LOCALES)

    def test_isv_latin_is_a_single_translation_target(self):
        self.assertIn("isv", tp.TRANSLATION_TARGET_LOCALES)


class FieldParsingTests(unittest.TestCase):
    def test_parse_edition_fields(self):
        md = pack_markdown("en", status="machine", source="test:pl", source_version="1.0.0")
        fields = tp.parse_edition_fields(md)
        self.assertEqual(fields["Translation status"], "machine")
        self.assertEqual(fields["Translation source"], "test:pl")
        self.assertEqual(fields["Translation source version"], "1.0.0")
        self.assertEqual(fields["Version"], "1.0.0")
        self.assertEqual(fields["Original language"], "en")

    def test_patch_translation_metadata_mirrors_and_stamps(self):
        md = pack_markdown("pl", version="1.5")
        patched = tp.patch_translation_metadata(
            md,
            book_id="test",
            target_locale="en",
            source_locale="pl",
            source_version="1.5",
            status="machine",
        )
        fields = tp.parse_edition_fields(patched)
        self.assertEqual(fields["Original language"], "en")
        self.assertEqual(fields["Version"], "1.5")
        self.assertEqual(fields["Edition version"], "1.5")
        self.assertEqual(fields["Translation status"], "machine")
        self.assertEqual(fields["Translation source"], "test:pl")
        self.assertEqual(fields["Translation source version"], "1.5")

    def test_patch_translation_metadata_replaces_stale_values(self):
        md = pack_markdown(
            "en",
            version="1.0",
            status="machine",
            source="test:pl",
            source_version="1.0",
        )
        patched = tp.patch_translation_metadata(
            md,
            book_id="test",
            target_locale="en",
            source_locale="pl",
            source_version="1.6",
            status="reviewed",
        )
        fields = tp.parse_edition_fields(patched)
        self.assertEqual(fields["Translation status"], "reviewed")
        self.assertEqual(fields["Translation source version"], "1.6")
        self.assertEqual(fields["Version"], "1.6")


class QuizGuardTests(unittest.TestCase):
    def test_quiz_shape(self):
        md = pack_markdown("pl")
        self.assertEqual(tp.quiz_shape(md), [2, 3])

    def test_quiz_shape_matches_for_same_structure(self):
        self.assertTrue(tp.quiz_shape_matches(pack_markdown("pl"), pack_markdown("en")))

    def test_quiz_shape_mismatch_when_answer_removed(self):
        tampered = pack_markdown("pl").replace("- A) One\n- B) Two\n", "- A) One\n", 1)
        self.assertFalse(tp.quiz_shape_matches(pack_markdown("pl"), tampered))

    def test_empty_quiz_matches(self):
        self.assertTrue(tp.quiz_shape_matches(pack_markdown("pl", quiz=False), pack_markdown("en", quiz=False)))


class ClassificationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def classify(self, locale, **kwargs):
        defaults = dict(
            repo_root=self.root,
            book_id="test",
            locale=locale,
            src_locale="pl",
            src_version="1.0.0",
        )
        defaults.update(kwargs)
        return tp.classify_edition(**defaults)

    def test_source_edition_is_skipped(self):
        write_book(self.root)
        state = self.classify("pl")
        self.assertEqual(state.state, "source")
        self.assertEqual(state.action, "skip")

    def test_missing_edition_is_created(self):
        write_book(self.root)
        state = self.classify("en", src_version="1.0.0")
        self.assertEqual(state.state, "missing")
        self.assertEqual(state.action, "create")

    def test_current_edition_is_skipped(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "en", version="1.0.0",
            status="machine", source="test:pl", source_version="1.0.0",
        )
        state = self.classify("en", src_version="1.0.0")
        self.assertEqual(state.state, "current")
        self.assertEqual(state.action, "skip")

    def test_stale_machine_is_regenerated(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "en", version="1.0.0",
            status="machine", source="test:pl", source_version="1.0.0",
        )
        state = self.classify("en", src_version="1.0.1")
        self.assertEqual(state.state, "stale")
        self.assertEqual(state.action, "regenerate")

    def test_stale_reviewed_is_skipped_without_flag(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "en", version="1.0.0",
            status="reviewed", source="test:pl", source_version="1.0.0",
        )
        state = self.classify("en", src_version="1.0.1")
        self.assertEqual(state.state, "reviewed_stale")
        self.assertEqual(state.action, "skip")
        state = self.classify("en", src_version="1.0.1", regenerate_reviewed=True)
        self.assertEqual(state.state, "stale")
        self.assertEqual(state.action, "regenerate")

    def test_final_is_protected_even_when_stale(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "en", version="1.0.0",
            status="final", source="test:pl", source_version="1.0.0",
        )
        state = self.classify("en", src_version="1.0.1")
        self.assertEqual(state.state, "final")
        self.assertEqual(state.action, "skip")

    def test_unlock_final_allows_regeneration(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "en", version="1.0.0",
            status="final", source="test:pl", source_version="1.0.0",
        )
        state = self.classify("en", src_version="1.0.1", unlock_final=True)
        self.assertEqual(state.state, "stale")
        self.assertEqual(state.action, "regenerate")

    def test_unclassified_legacy_is_skipped(self):
        write_book(self.root)
        write_edition(self.root, "test", "en", version="1.0.0")
        state = self.classify("en", src_version="1.0.1")
        self.assertEqual(state.state, "unclassified")
        self.assertEqual(state.action, "skip")

    def test_status_without_source_version_is_skipped(self):
        write_book(self.root)
        write_edition(self.root, "test", "en", version="1.0.0", status="machine")
        state = self.classify("en", src_version="1.0.1")
        self.assertEqual(state.state, "unclassified")
        self.assertEqual(state.action, "skip")

    def test_ahead_edition_is_skipped(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "en", version="1.0.1",
            status="machine", source="test:pl", source_version="1.0.1",
        )
        state = self.classify("en", src_version="1.0.0")
        self.assertEqual(state.state, "ahead")
        self.assertEqual(state.action, "skip")

    def test_incomplete_edition_recompiles(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "en", version="1.0.0",
            status="machine", source="test:pl", source_version="1.0.0",
            lesson=False,
        )
        state = self.classify("en", src_version="1.0.0")
        self.assertEqual(state.state, "incomplete")
        self.assertEqual(state.action, "recompile")

    def test_derived_missing_requires_isv_source(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "isv", version="1.0.0",
            status="machine", source="test:pl", source_version="1.0.0",
        )
        state = self.classify("isv_cyrl", src_locale="isv", src_version="1.0.0")
        self.assertEqual(state.state, "missing")
        self.assertEqual(state.action, "transliterate")

    def test_derived_skipped_when_isv_missing(self):
        write_book(self.root)
        state = self.classify("isv_cyrl", src_locale="isv", src_version=None)
        self.assertEqual(state.state, "unknown_source")
        self.assertEqual(state.action, "skip")

    def test_derived_stale_retransliterates(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "isv", version="1.0.0",
            status="machine", source="test:pl", source_version="1.0.0",
        )
        write_edition(
            self.root, "test", "isv_cyrl", version="1.0.0",
            status="machine", source="test:isv", source_version="1.0.0",
        )
        state = self.classify("isv_cyrl", src_locale="isv", src_version="1.0.1")
        self.assertEqual(state.state, "stale")
        self.assertEqual(state.action, "transliterate")

    def test_derived_final_is_protected(self):
        write_book(self.root)
        write_edition(
            self.root, "test", "isv", version="1.0.1",
            status="machine", source="test:pl", source_version="1.0.1",
        )
        write_edition(
            self.root, "test", "isv_cyrl", version="1.0.0",
            status="final", source="test:isv", source_version="1.0.0",
        )
        state = self.classify("isv_cyrl", src_locale="isv", src_version="1.0.1")
        self.assertEqual(state.state, "final")
        self.assertEqual(state.action, "skip")


class DerivedGenerationTests(unittest.TestCase):
    def test_derived_edition_generation_uses_transliteration(self):
        import generate_isv_script_editions as isv_tool

        isv_md = pack_markdown("isv", version="1.0.0")
        transformed = isv_tool.transform_pack(isv_md, "isv_cyrl")
        patched = tp.patch_translation_metadata(
            transformed,
            book_id="test",
            target_locale="isv_cyrl",
            source_locale="isv",
            source_version="1.0.0",
            status="machine",
        )
        fields = tp.parse_edition_fields(patched)
        self.assertEqual(fields["Original language"], "isv_cyrl")
        self.assertEqual(fields["Translation status"], "machine")
        self.assertEqual(fields["Translation source"], "test:isv")
        self.assertEqual(fields["Translation source version"], "1.0.0")
        # Structural headings and quiz shape survive derivation.
        self.assertIn("## Metadata", patched)
        self.assertIn("## Quiz", patched)
        self.assertTrue(tp.quiz_shape_matches(isv_md, patched))
        # Prose actually changed script (transliterated), not copied verbatim.
        self.assertNotEqual(transformed, isv_md)


class DiscoveryAndPlanTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_deterministic_book_discovery(self):
        for book_id in ("b2", "a1", "c3"):
            write_book(self.root, book_id=book_id)
        self.assertEqual(tp.discover_books(self.root), ["a1", "b2", "c3"])

    def test_book_source_locale_falls_back_to_pl(self):
        write_book(self.root, source_locale="en")
        self.assertEqual(tp.book_source_locale(self.root / "books" / "test"), "en")
        # No default_locale -> repository default.
        (self.root / "books" / "test" / "book.yaml").write_text(
            "book_id: test\nstatus: official\n", encoding="utf-8"
        )
        self.assertEqual(tp.book_source_locale(self.root / "books" / "test"), "pl")

    def test_plan_resumes_after_partial_generation(self):
        write_book(self.root, book_id="a1")
        write_book(self.root, book_id="b2")
        # Simulate a previous run that already created a1:en (current).
        write_edition(
            self.root, "a1", "en", version="1.0.0",
            status="machine", source="a1:pl", source_version="1.0.0",
        )
        plan_result = tp.plan(self.root)
        by_id = {(job.book_id, job.locale): job for job in plan_result.jobs}
        self.assertEqual(by_id[("a1", "en")].state, "current")
        self.assertEqual(by_id[("a1", "en")].action, "skip")
        self.assertEqual(by_id[("b2", "en")].state, "missing")
        self.assertEqual(by_id[("b2", "en")].action, "create")

    def test_plan_locale_filter(self):
        write_book(self.root, book_id="a1")
        plan_result = tp.plan(self.root, selected_locales=["en"])
        locales = {job.locale for job in plan_result.jobs}
        self.assertEqual(locales, {"en"})

    def test_plan_is_deterministic(self):
        for book_id in ("b2", "a1"):
            write_book(self.root, book_id=book_id)
        first = [(j.book_id, j.locale, j.state, j.action) for j in tp.plan(self.root).jobs]
        second = [(j.book_id, j.locale, j.state, j.action) for j in tp.plan(self.root).jobs]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main(verbosity=2)
