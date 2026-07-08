import 'dart:io';

import 'package:alephbits_content/manifest/builder.dart';
import 'package:alephbits_content/repository/pack_discovery.dart';
import 'package:path/path.dart' as p;

class ManifestDrift {
  ManifestDrift(this.message);
  final String message;
}

ManifestDrift? checkManifestDrift(String repoRoot) {
  final manifestFile = File(p.join(repoRoot, 'manifest.json'));
  if (!manifestFile.existsSync()) {
    return ManifestDrift('manifest.json is missing');
  }

  final builder = ManifestBuilder();
  final generated = builder.buildJson(repoRoot);
  final committed = manifestFile.readAsStringSync();

  if (!manifestSemanticallyEqual(committed, generated)) {
    return ManifestDrift('manifest.json differs from build_manifest output');
  }
  return null;
}

void writeManifest(String repoRoot) {
  final builder = ManifestBuilder();
  File(p.join(repoRoot, 'manifest.json')).writeAsStringSync(builder.buildJson(repoRoot));
}

List<ManifestDrift> validateManifestCoverage(String repoRoot, Map<String, dynamic> manifest) {
  final drift = <ManifestDrift>[];
  final discovered = discoverPacksWithLesson(repoRoot);
  final discoveredPaths = discovered.map((p) => p.relativePath).toSet();

  final packs = manifest['packs'];
  if (packs is! List) {
    drift.add(ManifestDrift('manifest.json packs must be an array'));
    return drift;
  }

  final manifestPaths = <String>{};
  final manifestIds = <String>{};

  for (final entry in packs) {
    if (entry is! Map<String, dynamic>) continue;
    final id = entry['id'];
    final path = entry['path'];
    if (id is String) manifestIds.add(id);
    if (path is String) {
      manifestPaths.add(path);
      if (!Directory(p.join(repoRoot, path)).existsSync()) {
        drift.add(ManifestDrift('manifest references missing pack path: $path'));
      }
    }
  }

  for (final pack in discovered) {
    if (!manifestPaths.contains(pack.relativePath)) {
      drift.add(ManifestDrift('pack missing from manifest: ${pack.relativePath}'));
    }
  }

  for (final path in manifestPaths) {
    if (!discoveredPaths.contains(path)) {
      drift.add(ManifestDrift('manifest references pack not on disk: $path'));
    }
  }

  return drift;
}
