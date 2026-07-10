import 'dart:convert';
import 'dart:io';

import 'package:alephbits_content/reading_pack/compile_runner.dart';
import 'package:alephbits_content/reading_pack/json_writer.dart';
import 'package:alephbits_content/reading_pack/parser.dart';
import 'package:path/path.dart' as p;
import 'package:test/test.dart';

void main() {
  final repoRoot = p.normalize(p.join(Directory.current.path));
  final demoPack = p.join(
    repoRoot,
    'official/glagolitic/pl/spacer-po-krakowie',
  );

  group('compile_pack', () {
    test('parses demo reading-pack.md', () {
      final markdown = File(p.join(demoPack, 'reading-pack.md')).readAsStringSync();
      final doc = ReadingPackParser().parse(markdown, packDirPath: demoPack);
      expect(doc.metadata['Pack ID'], 'polish_demo_lesson');
      expect(doc.title, 'Spacer po Krakowie');
      expect(doc.quiz?.questions.length, 3);
    });

    test('parses Text section with in-body chapter headings', () {
      final pack = p.join(
        repoRoot,
        'official/glagolitic/pl/brudne-pieniadze-czysta-nauka',
      );
      final markdown = File(p.join(pack, 'reading-pack.md')).readAsStringSync();
      final doc = ReadingPackParser().parse(markdown, packDirPath: pack);
      expect(doc.text, contains('Dr Anna Kowalska'));
      expect(doc.text.split(RegExp(r'\s+')).length, greaterThan(1500));
    });

    test('compiles trust and edition metadata', () {
      final pack = p.join(
        repoRoot,
        'official/glagolitic/pl/spacer-po-krakowie',
      );
      final compiled = compilePackDirectory(pack);
      final lesson = jsonDecode(compiled.lessonJson) as Map<String, dynamic>;
      expect(lesson['editionVersion'], '1.0.0');
      expect(lesson['trustClassification'], 'demo');
      expect(lesson['subtitle'], isNotEmpty);
    });

    test('compiles demo pack without drift', () {
      final result = compileAndCheckDirectory(demoPack);
      expect(result.parseError, isNull, reason: result.parseError);
      expect(result.drift, isEmpty, reason: result.drift.map((d) => d.file).join(', '));
    });

    test('compiler output is deterministic', () {
      final first = compilePackDirectory(demoPack);
      final second = compilePackDirectory(demoPack);
      expect(first.lessonJson, second.lessonJson);
      expect(first.textTxt, second.textTxt);
      expect(first.quizJson, second.quizJson);
      expect(first.provenanceJson, second.provenanceJson);
      expect(first.licenseMd, second.licenseMd);
    });

    test('generated lesson.json matches committed file semantically', () {
      final compiled = compilePackDirectory(demoPack);
      final committed = File(p.join(demoPack, 'lesson.json')).readAsStringSync();
      expect(jsonSemanticallyEqual(committed, compiled.lessonJson), isTrue);
    });
  });
}
