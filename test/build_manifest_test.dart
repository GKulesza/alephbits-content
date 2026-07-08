import 'dart:io';

import 'package:alephbits_content/manifest/builder.dart';
import 'package:alephbits_content/manifest/manifest_runner.dart';
import 'package:path/path.dart' as p;
import 'package:test/test.dart';

void main() {
  final repoRoot = p.normalize(Directory.current.path);

  group('build_manifest', () {
    test('generates manifest with both official packs', () {
      final manifest = ManifestBuilder().build(repoRoot);
      final packs = manifest['packs'] as List;
      expect(packs.length, 2);
      expect(manifest['officialPackCount'], 2);
      expect(manifest['communityPackCount'], 0);
      expect(manifest['experimentalPackCount'], 0);
    });

    test('builder output is deterministic', () {
      final first = ManifestBuilder().buildJson(repoRoot);
      final second = ManifestBuilder().buildJson(repoRoot);
      expect(first, second);
    });

    test('committed manifest matches build_manifest output', () {
      final drift = checkManifestDrift(repoRoot);
      expect(drift, isNull, reason: drift?.message);
    });

    test('library statistics include word counts', () {
      final stats = ManifestBuilder().build(repoRoot)['libraryStatistics']
          as Map<String, dynamic>;
      expect(stats['totalPacks'], 2);
      expect(stats['totalWords'], greaterThan(2000));
      expect(stats['largestPack'], isA<Map<String, dynamic>>());
    });
  });
}
