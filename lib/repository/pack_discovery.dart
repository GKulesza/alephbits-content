import 'dart:io';

import 'package:path/path.dart' as p;

/// A Reading Pack directory discovered on disk.
class DiscoveredPack {
  DiscoveredPack({
    required this.tier,
    required this.relativePath,
    required this.absolutePath,
  });

  final String tier;
  final String relativePath;
  final String absolutePath;
}

/// Discovers pack directories containing `lesson.json` under tier roots.
List<DiscoveredPack> discoverPacksWithLesson(String repoRoot) {
  final results = <DiscoveredPack>[];

  for (final tier in ['official', 'community', 'experimental']) {
    final tierDir = Directory(p.join(repoRoot, tier));
    if (!tierDir.existsSync()) continue;

    for (final packDir in _discoverPackDirectories(tierDir, tier)) {
      results.add(DiscoveredPack(
        tier: tier,
        relativePath: _relativePath(repoRoot, packDir.path),
        absolutePath: packDir.path,
      ));
    }
  }

  results.sort((a, b) => a.relativePath.compareTo(b.relativePath));
  return results;
}

List<Directory> _discoverPackDirectories(Directory tierDir, String tier) {
  final results = <Directory>[];

  if (tier == 'official') {
    for (final ws in tierDir.listSync().whereType<Directory>()) {
      if (p.basename(ws.path) == 'starter-shelf') continue;
      for (final lang in ws.listSync().whereType<Directory>()) {
        for (final pack in lang.listSync().whereType<Directory>()) {
          if (File(p.join(pack.path, 'lesson.json')).existsSync()) {
            results.add(pack);
          }
        }
      }
    }
    return results;
  }

  for (final entity in tierDir.listSync(recursive: true)) {
    if (entity is Directory && File(p.join(entity.path, 'lesson.json')).existsSync()) {
      final parentHasLesson =
          File(p.join(p.dirname(entity.path), 'lesson.json')).existsSync();
      if (!parentHasLesson) {
        results.add(entity);
      }
    }
  }
  return results;
}

String _relativePath(String repoRoot, String absolutePath) {
  final normalizedRoot = p.normalize(repoRoot);
  final normalizedPath = p.normalize(absolutePath);
  if (normalizedPath.startsWith(normalizedRoot)) {
    return normalizedPath.substring(normalizedRoot.length + 1);
  }
  return normalizedPath;
}
