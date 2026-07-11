import 'dart:convert';
import 'dart:io';

import 'package:alephbits_content/reading_pack/compile_runner.dart';
import 'package:path/path.dart' as p;
import 'package:test/test.dart';

void main() {
  final repoRoot = p.normalize(p.join(Directory.current.path));

  test('compiles YouTube inspiration as video IDs only', () {
    final pack = p.join(
      repoRoot,
      'official/glagolitic/pl/jak-ugotowac-herbate',
    );
    final compiled = compilePackDirectory(pack);
    final lesson = jsonDecode(compiled.lessonJson) as Map<String, dynamic>;

    expect(lesson.containsKey('references'), isFalse);
    expect(lesson.containsKey('source'), isFalse);
    expect(lesson['inspiredBy'], isNotNull);
    final youtube = (lesson['inspiredBy'] as Map)['youtube'] as String;
    expect(youtube, contains('M1_TL3gHz6s'));
    expect(youtube.contains('http'), isFalse);
    expect(lesson['inspirationDates'], isA<List>());
    expect((lesson['inspirationDates'] as List).length, greaterThan(0));
  });
}
