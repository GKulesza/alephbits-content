import 'dart:io';

import 'package:path/path.dart' as p;

/// Book-owned visual assets under Content Model v2.
///
/// - Book owns `books/<book_id>/default/{cover,vignette}.webp`
/// - Locale may override with `books/<book_id>/<locale>/{cover,vignette}.webp`
abstract final class BookVisualAssets {
  static const coverFileName = 'cover.webp';
  static const vignetteFileName = 'vignette.webp';

  /// Whether a book-owned cover exists for [editionAbsolutePath].
  static bool hasCover(String editionAbsolutePath) =>
      resolveExisting(editionAbsolutePath, coverFileName) != null;

  /// Whether a book-owned vignette exists for [editionAbsolutePath].
  static bool hasVignette(String editionAbsolutePath) =>
      resolveExisting(editionAbsolutePath, vignetteFileName) != null;

  /// Absolute path to the best existing asset, or null.
  static String? resolveExisting(String editionAbsolutePath, String fileName) {
    for (final candidate in candidateAbsolutePaths(
      editionAbsolutePath,
      fileName,
    )) {
      if (File(candidate).existsSync()) {
        return candidate;
      }
    }
    return null;
  }

  /// Candidate absolute paths: locale first, then book `default/`.
  static List<String> candidateAbsolutePaths(
    String editionAbsolutePath,
    String fileName,
  ) {
    final edition = p.normalize(editionAbsolutePath);
    final candidates = <String>[p.join(edition, fileName)];
    final defaultRoot = defaultAssetRoot(edition);
    if (defaultRoot != null) {
      candidates.add(p.join(defaultRoot, fileName));
    }
    return candidates;
  }

  /// `…/books/<book_id>/default` when [editionAbsolutePath] is a locale folder.
  static String? defaultAssetRoot(String editionAbsolutePath) {
    final parts = p.split(p.normalize(editionAbsolutePath));
    final booksIndex = parts.lastIndexOf('books');
    if (booksIndex != -1 && booksIndex + 2 < parts.length) {
      return p.joinAll([
        ...parts.take(booksIndex + 2),
        'default',
      ]);
    }
    return null;
  }
}
