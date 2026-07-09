import 'dart:io';

import 'package:alephbits_content/manifest/builder.dart';
import 'package:alephbits_content/manifest/manifest_runner.dart';
import 'package:path/path.dart' as p;
import 'package:test/test.dart';

void main() {
  final repoRoot = p.normalize(Directory.current.path);

  group('build_manifest', () {
    test('generates manifest with all official packs', () {
      final manifest = ManifestBuilder().build(repoRoot);
      final packs = manifest['packs'] as List;
      expect(packs.length, greaterThanOrEqualTo(13));
      expect(manifest['officialPackCount'], packs.length);
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
      expect(stats['totalPacks'], greaterThanOrEqualTo(13));
      expect(stats['totalWords'], greaterThan(14000));
      expect(stats['largestPack'], isA<Map<String, dynamic>>());
    });

    test('emits explicit cover family when present in reading-pack metadata', () {
      final manifest = ManifestBuilder().build(repoRoot);
      final packs = (manifest['packs'] as List).whereType<Map<String, dynamic>>();
      final cenaWidoku = packs.firstWhere(
        (pack) => pack['id'] == 'polish_cena_widoku',
      );

      expect(cenaWidoku['coverFamily'], 'article');
    });
  });
}
