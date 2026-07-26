import 'dart:convert';
import 'dart:io';

import 'package:alephbits_content/reading_pack/compile_runner.dart';
import 'package:alephbits_content/reading_pack/parser.dart';
import 'package:alephbits_content/reading_pack/world_metadata.dart';
import 'package:path/path.dart' as p;
import 'package:test/test.dart';

void main() {
  group('PackWorldMetadata', () {
    test('parses compact bullet world metadata', () {
      const section = '''
**Pack ID:** `demo`
**World:**
- objects: flashlight, painting
- creatures: green_elephant
- places: forest
''';
      final world = PackWorldMetadata.parse(section);
      expect(world, isNotNull);
      expect(world!.objects, ['flashlight', 'painting']);
      expect(world.creatures, ['green_elephant']);
      expect(world.places, ['forest']);
    });

    test('parses yaml-style world lists', () {
      const section = '''
**World:**
  objects:
    - flashlight
  symbols:
    - red_ribbon
  places:
    - forest
''';
      final world = PackWorldMetadata.parse(section);
      expect(world!.objects, ['flashlight']);
      expect(world.symbols, ['red_ribbon']);
      expect(world.places, ['forest']);
    });

    test('missing world returns null', () {
      expect(PackWorldMetadata.parse('**Pack ID:** x'), isNull);
    });

    test('invalid ids are dropped with warnings', () {
      final warnings = <String>[];
      final world = PackWorldMetadata.parse(
        '**World:**\n- objects: Flash Light, flashlight\n',
        warnings: warnings,
      );
      expect(world!.objects, ['flashlight']);
      expect(warnings, isNotEmpty);
    });
  });

  group('compile world into lesson.json', () {
    test('emits world when present and never requires it', () {
      final dir = Directory.systemTemp.createTempSync('world_compile_');
      addTearDown(() => dir.deleteSync(recursive: true));

      File(p.join(dir.path, 'reading-pack.md')).writeAsStringSync('''
# World Demo

## Metadata

**Pack ID:** `world_demo_pack`
**Version:** 1.0.0
**Edition version:** 1.0.0
**Title:** World Demo
**Subtitle:** Test
**Blurb:** A short demo.
**Genres:** demo
**Audience:** adult
**Difficulty:** 1 (of 8)
**Estimated reading time:** 1 minutes
**Original language:** en
**Writing system:** glagolitic
**Recommended profile:** english_default
**Recommended level:** 1
**Tags:** demo
**Cover family:** travel

**World:**
- objects: flashlight
- places: forest

## Editorial Transparency

**Created by:** Test
**Editor:** Test
**LLM assisted:** no
**Trust classification:** Demo
**Human reviewed:** yes — 2026-07-21
**License:** CC0 1.0 Universal (SPDX: CC0-1.0)

### Revision history

| Version | Date | Note |
|---------|------|------|
| 1.0.0 | 2026-07-21 | test |

## Sources

### Source 1: Original

**Author:** Test
**License:** CC0
**Availability:** original
**Deprecated:** no

## Text

Once upon a time in a forest with a flashlight.

## Quiz
''');

      final compiled = compilePackDirectory(dir.path);
      final lesson = jsonDecode(compiled.lessonJson) as Map<String, dynamic>;
      expect(lesson['world'], isA<Map>());
      final world = lesson['world'] as Map<String, dynamic>;
      expect(world['objects'], ['flashlight']);
      expect(world['places'], ['forest']);
    });

    test('pack without world still compiles and omits world key', () {
      final dir = Directory.systemTemp.createTempSync('world_compile_empty_');
      addTearDown(() => dir.deleteSync(recursive: true));

      File(p.join(dir.path, 'reading-pack.md')).writeAsStringSync('''
# No World Demo

## Metadata

**Pack ID:** `no_world_demo_pack`
**Version:** 1.0.0
**Edition version:** 1.0.0
**Title:** No World Demo
**Subtitle:** Test
**Blurb:** A short demo.
**Genres:** demo
**Audience:** adult
**Difficulty:** 1 (of 8)
**Estimated reading time:** 1 minutes
**Original language:** en
**Writing system:** glagolitic
**Recommended profile:** english_default
**Recommended level:** 1
**Tags:** demo
**Cover family:** travel

## Editorial Transparency

**Created by:** Test
**Editor:** Test
**LLM assisted:** no
**Trust classification:** Demo
**Human reviewed:** yes — 2026-07-21
**License:** CC0 1.0 Universal (SPDX: CC0-1.0)

### Revision history

| Version | Date | Note |
|---------|------|------|
| 1.0.0 | 2026-07-21 | test |

## Sources

### Source 1: Original

**Author:** Test
**License:** CC0
**Availability:** original
**Deprecated:** no

## Text

A plain story without world furniture.

## Quiz
''');

      final doc = ReadingPackParser().parse(
        File(p.join(dir.path, 'reading-pack.md')).readAsStringSync(),
        packDirPath: dir.path,
      );
      expect(doc.world, isNull);
      final compiled = compilePackDirectory(dir.path);
      final lesson = jsonDecode(compiled.lessonJson) as Map<String, dynamic>;
      expect(lesson.containsKey('world'), isFalse);
    });
  });
}
