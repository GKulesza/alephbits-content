import 'dart:convert';
import 'dart:io';

import 'package:alephbits_content/manifest/builder.dart';
import 'package:alephbits_content/reading_pack/compiler.dart';
import 'package:alephbits_content/reading_pack/parser.dart';
import 'package:path/path.dart' as p;
import 'package:test/test.dart';

void main() {
  final repoRoot = p.normalize(Directory.current.path);
  final demoPack = p.join(repoRoot, 'books/hgp8iy3x/pl');
  final sourceMd = File(p.join(demoPack, 'reading-pack.md')).readAsStringSync();

  String withTranslationMetadata(String md, {String status = 'machine'}) {
    return md.replaceFirst(
      '**Original language:** pl  ',
      '**Original language:** pl  \n'
      '**Translation status:** $status  \n'
      '**Translation source:** hgp8iy3x:pl  \n'
      '**Translation source version:** 1.0.0  ',
    );
  }

  group('translation metadata', () {
    test('compiler emits translation metadata into lesson.json when declared', () {
      final doc = ReadingPackParser().parse(
        withTranslationMetadata(sourceMd),
        packDirPath: demoPack,
      );
      final compiled = ReadingPackCompiler().compile(doc, packDirPath: demoPack);
      final lesson = jsonDecode(compiled.lessonJson) as Map<String, dynamic>;
      expect(lesson['translationStatus'], 'machine');
      expect(lesson['translationSource'], 'hgp8iy3x:pl');
      expect(lesson['translationSourceVersion'], '1.0.0');
    });

    test('compiler emits translation metadata into provenance.json when declared', () {
      final doc = ReadingPackParser().parse(
        withTranslationMetadata(sourceMd, status: 'reviewed'),
        packDirPath: demoPack,
      );
      final compiled = ReadingPackCompiler().compile(doc, packDirPath: demoPack);
      final provenance = jsonDecode(compiled.provenanceJson) as Map<String, dynamic>;
      expect(provenance['translationStatus'], 'reviewed');
      expect(provenance['translationSource'], 'hgp8iy3x:pl');
      expect(provenance['translationSourceVersion'], '1.0.0');
    });

    test('compiler omits translation metadata when not declared (no drift)', () {
      final doc = ReadingPackParser().parse(sourceMd, packDirPath: demoPack);
      final compiled = ReadingPackCompiler().compile(doc, packDirPath: demoPack);
      final lesson = jsonDecode(compiled.lessonJson) as Map<String, dynamic>;
      expect(lesson.containsKey('translationStatus'), isFalse);
      expect(lesson.containsKey('translationSource'), isFalse);
      expect(lesson.containsKey('translationSourceVersion'), isFalse);
      final provenance = jsonDecode(compiled.provenanceJson) as Map<String, dynamic>;
      expect(provenance.containsKey('translationStatus'), isFalse);
    });

    test('compiled output is deterministic with translation metadata', () {
      final md = withTranslationMetadata(sourceMd);
      final first = ReadingPackCompiler().compile(
        ReadingPackParser().parse(md, packDirPath: demoPack),
        packDirPath: demoPack,
      );
      final second = ReadingPackCompiler().compile(
        ReadingPackParser().parse(md, packDirPath: demoPack),
        packDirPath: demoPack,
      );
      expect(first.lessonJson, second.lessonJson);
      expect(first.provenanceJson, second.provenanceJson);
    });
  });

  group('manifest translation status', () {
    test('pack entry exposes translationStatus when declared', () {
      final entry = PackIndexEntry(
        id: 'hgp8iy3x:en',
        bookId: 'hgp8iy3x',
        path: 'books/hgp8iy3x/en',
        tier: 'official',
        writingSystem: 'glagolitic',
        language: 'en',
        title: 'A Walk Through Kraków',
        version: '1.0.0',
        editionVersion: '1.0.0',
        updated: '2026-07-01',
        categories: const ['travel', 'demo'],
        coverFamily: 'travel',
        difficulty: 2,
        estimatedReadingTime: 2,
        wordCount: 120,
        featured: true,
        translationStatus: 'machine',
        translationSource: 'hgp8iy3x:pl',
        translationSourceVersion: '1.0.0',
      );
      final map = entry.toManifestEntry();
      expect(map['translationStatus'], 'machine');
      expect(map['translationSource'], 'hgp8iy3x:pl');
      expect(map['translationSourceVersion'], '1.0.0');
    });

    test('pack entry omits translationStatus when absent', () {
      final entry = PackIndexEntry(
        id: 'hgp8iy3x:pl',
        bookId: 'hgp8iy3x',
        path: 'books/hgp8iy3x/pl',
        tier: 'official',
        writingSystem: 'glagolitic',
        language: 'pl',
        title: 'Spacer po Krakowie',
        version: '1.0.0',
        editionVersion: '1.0.0',
        updated: '2026-07-01',
        categories: const ['travel', 'demo'],
        coverFamily: 'travel',
        difficulty: 2,
        estimatedReadingTime: 2,
        wordCount: 120,
        featured: true,
      );
      final map = entry.toManifestEntry();
      expect(map.containsKey('translationStatus'), isFalse);
      expect(map.containsKey('translationSource'), isFalse);
      expect(map.containsKey('translationSourceVersion'), isFalse);
    });
  });
}
