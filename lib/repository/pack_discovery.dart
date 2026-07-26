import 'dart:io';

import 'package:path/path.dart' as p;

/// A Reading Pack directory discovered on disk.
class DiscoveredPack {
  DiscoveredPack({
    required this.tier,
    required this.relativePath,
    required this.absolutePath,
    this.bookId,
    this.locale,
  });

  final String tier;
  final String relativePath;
  final String absolutePath;
  final String? bookId;
  final String? locale;
}

/// Discovers pack directories containing `lesson.json` under `books/`.
///
/// Content Model v2 layout: `books/<book_id>/<locale>/lesson.json`.
/// Tier comes from `books/<book_id>/book.yaml` `status:` (default `official`).
List<DiscoveredPack> discoverPacksWithLesson(String repoRoot) {
  final results = <DiscoveredPack>[];

  final booksRoot = Directory(p.join(repoRoot, 'books'));
  if (booksRoot.existsSync()) {
    for (final bookDir in booksRoot.listSync().whereType<Directory>()) {
      final bookId = p.basename(bookDir.path);
      for (final localeDir in bookDir.listSync().whereType<Directory>()) {
        final locale = p.basename(localeDir.path);
        if (locale == 'default') continue;
        if (File(p.join(localeDir.path, 'lesson.json')).existsSync()) {
          results.add(DiscoveredPack(
            tier: _tierFromBookYaml(bookDir.path) ?? 'official',
            relativePath: _relativePath(repoRoot, localeDir.path),
            absolutePath: localeDir.path,
            bookId: bookId,
            locale: locale,
          ));
        }
      }
    }
  }

  results.sort((a, b) => a.relativePath.compareTo(b.relativePath));
  return results;
}

String? _tierFromBookYaml(String bookDirPath) {
  final file = File(p.join(bookDirPath, 'book.yaml'));
  if (!file.existsSync()) return null;
  for (final rawLine in file.readAsLinesSync()) {
    final line = rawLine.trim();
    if (line.startsWith('status:')) {
      final value = line.substring('status:'.length).trim();
      if (value.isNotEmpty) return value.replaceAll('"', '').replaceAll("'", '');
    }
  }
  return null;
}

String _relativePath(String repoRoot, String absolutePath) {
  final normalizedRoot = p.normalize(repoRoot);
  final normalizedPath = p.normalize(absolutePath);
  if (normalizedPath.startsWith(normalizedRoot)) {
    return normalizedPath.substring(normalizedRoot.length + 1);
  }
  return normalizedPath;
}
