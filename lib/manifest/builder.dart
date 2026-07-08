import 'dart:convert';
import 'dart:io';

import 'package:alephbits_content/manifest/catalog.dart';
import 'package:alephbits_content/reading_pack/json_writer.dart';
import 'package:alephbits_content/reading_pack/parser.dart';
import 'package:alephbits_content/repository/pack_discovery.dart';
import 'package:path/path.dart' as p;

class ManifestBuildException implements Exception {
  ManifestBuildException(this.message);
  final String message;

  @override
  String toString() => message;
}

class PackIndexEntry {
  PackIndexEntry({
    required this.id,
    required this.bookId,
    required this.path,
    required this.tier,
    required this.writingSystem,
    required this.language,
    required this.title,
    required this.version,
    required this.updated,
    required this.categories,
    required this.difficulty,
    required this.estimatedReadingTime,
    required this.wordCount,
    required this.featured,
  });

  final String id;
  final String bookId;
  final String path;
  final String tier;
  final String writingSystem;
  final String language;
  final String title;
  final String version;
  final String updated;
  final List<String> categories;
  final int difficulty;
  final int estimatedReadingTime;
  final int wordCount;
  final bool featured;

  Map<String, dynamic> toManifestEntry() {
    return {
      'id': id,
      'bookId': bookId,
      'path': path,
      'tier': tier,
      'writingSystem': writingSystem,
      'language': language,
      'title': title,
      'version': version,
      'categories': categories,
      'difficulty': difficulty,
      'estimatedReadingTime': estimatedReadingTime,
      'featured': featured,
    };
  }
}

class ManifestBuilder {
  Map<String, dynamic> build(String repoRoot) {
    final discovered = discoverPacksWithLesson(repoRoot);
    if (discovered.isEmpty) {
      throw ManifestBuildException('No Reading Packs found under official/, community/, or experimental/.');
    }

    final entries = <PackIndexEntry>[];
    for (final pack in discovered) {
      entries.add(_indexPack(repoRoot, pack));
    }

    entries.sort((a, b) => a.path.compareTo(b.path));

    final officialCount = entries.where((e) => e.tier == 'official').length;
    final communityCount = entries.where((e) => e.tier == 'community').length;
    final experimentalCount = entries.where((e) => e.tier == 'experimental').length;

    final languages = entries.map((e) => e.language).toSet().toList()..sort();
    final writingSystems = entries.map((e) => e.writingSystem).toSet().toList()..sort();

    final usedCategoryIds = entries.expand((e) => e.categories).toSet();
    final categories = canonicalCategories
        .where((c) => usedCategoryIds.contains(c['id']))
        .map((c) => Map<String, dynamic>.from(c))
        .toList();

    // Include pack-only category IDs (e.g. demo) not in canonical catalog.
    for (final id in usedCategoryIds) {
      if (!categories.any((c) => c['id'] == id)) {
        categories.add({
          'id': id,
          'title': _titleCaseId(id),
          'description': '',
        });
      }
    }
    categories.sort((a, b) => (a['id'] as String).compareTo(b['id'] as String));

    final featuredCollections = _buildFeaturedCollections(entries);
    final libraryStatistics = _buildLibraryStatistics(entries);

    return {
      'repositoryVersion': repositoryVersion,
      'schemaVersion': schemaVersion,
      'minimumAppVersion': minimumAppVersion,
      'generatedAt': _generatedAt(entries),
      'officialPackCount': officialCount,
      'communityPackCount': communityCount,
      'experimentalPackCount': experimentalCount,
      'supportedLanguages': languages,
      'supportedWritingSystems': writingSystems,
      'categories': categories,
      'featuredCollections': featuredCollections,
      'libraryStatistics': libraryStatistics,
      'packs': entries.map((e) => e.toManifestEntry()).toList(),
    };
  }

  String buildJson(String repoRoot) => encodeJsonPretty(build(repoRoot));

  PackIndexEntry _indexPack(String repoRoot, DiscoveredPack pack) {
    final lessonFile = File(p.join(pack.absolutePath, 'lesson.json'));
    if (!lessonFile.existsSync()) {
      throw ManifestBuildException('${pack.relativePath}: missing lesson.json');
    }

    final lesson = _readJsonObject(lessonFile);
    final id = _requireString(lesson, 'id', pack.relativePath);
    final title = _requireString(lesson, 'title', pack.relativePath);
    final language = _requireString(lesson, 'language', pack.relativePath);
    final version = _requireString(lesson, 'version', pack.relativePath);
    final updated = _requireString(lesson, 'updated', pack.relativePath);
    final text = _requireString(lesson, 'text', pack.relativePath);

    final writingSystem = _writingSystem(pack, lesson);
    final bookId = _bookId(pack);
    final categories = _categories(pack);
    final difficulty = _intField(lesson, 'difficulty', defaultValue: 1);
    final estimatedReadingTime =
        _intField(lesson, 'estimatedReadingTime', defaultValue: 1);
    final wordCount = _countWords(text);
    final featured = pack.tier == 'official';

    return PackIndexEntry(
      id: id,
      bookId: bookId,
      path: pack.relativePath,
      tier: pack.tier,
      writingSystem: writingSystem,
      language: language,
      title: title,
      version: version,
      updated: updated,
      categories: categories,
      difficulty: difficulty,
      estimatedReadingTime: estimatedReadingTime,
      wordCount: wordCount,
      featured: featured,
    );
  }

  String _writingSystem(DiscoveredPack pack, Map<String, dynamic> lesson) {
    if (pack.tier == 'official') {
      final parts = pack.relativePath.split('/');
      if (parts.length >= 3) {
        return parts[1];
      }
    }
    final fromLesson = lesson['recommendedWritingSystem'];
    if (fromLesson is String && fromLesson.isNotEmpty) {
      return fromLesson;
    }
    throw ManifestBuildException('${pack.relativePath}: cannot determine writing system');
  }

  String _bookId(DiscoveredPack pack) {
    final provenanceFile = File(p.join(pack.absolutePath, 'provenance.json'));
    if (provenanceFile.existsSync()) {
      final provenance = _readJsonObject(provenanceFile);
      final bookId = provenance['bookId'];
      if (bookId is String && bookId.isNotEmpty) {
        return bookId;
      }
    }
    return p.basename(pack.absolutePath);
  }

  List<String> _categories(DiscoveredPack pack) {
    final mdFile = File(p.join(pack.absolutePath, 'reading-pack.md'));
    if (mdFile.existsSync()) {
      final doc = ReadingPackParser().parse(
        mdFile.readAsStringSync(),
        packDirPath: pack.absolutePath,
      );
      final genres = doc.metadata['Genres'] ?? '';
      final parsed = genres
          .split(',')
          .map((s) => s.trim())
          .where((s) => s.isNotEmpty)
          .toList();
      if (parsed.isNotEmpty) {
        return parsed;
      }
    }

    final lesson = _readJsonObject(File(p.join(pack.absolutePath, 'lesson.json')));
    final tags = lesson['tags'];
    if (tags is List) {
      return tags.whereType<String>().where((t) => t.isNotEmpty).toList();
    }
    return [];
  }

  List<Map<String, dynamic>> _buildFeaturedCollections(List<PackIndexEntry> entries) {
    final collections = <Map<String, dynamic>>[];

    for (final template in featuredCollectionTemplates) {
      final tiers = (template['tiers'] as List).cast<String>();
      var matching = entries.where((e) => tiers.contains(e.tier)).toList();

      switch (template['sort']) {
        case 'difficulty':
          matching.sort((a, b) {
            final byDifficulty = a.difficulty.compareTo(b.difficulty);
            return byDifficulty != 0 ? byDifficulty : a.id.compareTo(b.id);
          });
        case 'title':
        default:
          matching.sort((a, b) => a.title.compareTo(b.title));
      }

      if (matching.isEmpty) continue;

      collections.add({
        'id': template['id'],
        'title': template['title'],
        'description': template['description'],
        'packIds': matching.map((e) => e.id).toList(),
      });
    }

    return collections;
  }

  Map<String, dynamic> _buildLibraryStatistics(List<PackIndexEntry> entries) {
    final totalWords = entries.fold<int>(0, (sum, e) => sum + e.wordCount);
    final totalReadingTime =
        entries.fold<int>(0, (sum, e) => sum + e.estimatedReadingTime);

    final usedCategories = entries.expand((e) => e.categories).toSet();

    PackIndexEntry largest = entries.first;
    PackIndexEntry newest = entries.first;
    PackIndexEntry oldest = entries.first;

    for (final entry in entries) {
      if (entry.wordCount > largest.wordCount) largest = entry;
      if (entry.updated.compareTo(newest.updated) > 0) newest = entry;
      if (entry.updated.compareTo(oldest.updated) < 0) oldest = entry;
    }

    return {
      'totalPacks': entries.length,
      'totalWords': totalWords,
      'totalEstimatedReadingTimeMinutes': totalReadingTime,
      'languageCount': entries.map((e) => e.language).toSet().length,
      'writingSystemCount': entries.map((e) => e.writingSystem).toSet().length,
      'categoryCount': usedCategories.length,
      'largestPack': {
        'id': largest.id,
        'bookId': largest.bookId,
        'wordCount': largest.wordCount,
      },
      'newestPack': {
        'id': newest.id,
        'bookId': newest.bookId,
        'updated': newest.updated,
      },
      'oldestPack': {
        'id': oldest.id,
        'bookId': oldest.bookId,
        'updated': oldest.updated,
      },
    };
  }

  String _generatedAt(List<PackIndexEntry> entries) {
    var latest = entries.first.updated;
    for (final entry in entries) {
      if (entry.updated.compareTo(latest) > 0) {
        latest = entry.updated;
      }
    }
    return '${latest}T00:00:00Z';
  }

  int _countWords(String text) {
    return text
        .trim()
        .split(RegExp(r'\s+'))
        .where((w) => w.isNotEmpty)
        .length;
  }

  String _titleCaseId(String id) {
    return id
        .split('_')
        .map((part) => part.isEmpty ? part : '${part[0].toUpperCase()}${part.substring(1)}')
        .join(' ');
  }

  int _intField(Map<String, dynamic> json, String key, {required int defaultValue}) {
    final value = json[key];
    if (value is int) return value;
    if (value is String) return int.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  String _requireString(Map<String, dynamic> json, String key, String label) {
    final value = json[key];
    if (value is String && value.isNotEmpty) return value;
    throw ManifestBuildException('$label: lesson.json missing "$key"');
  }

  Map<String, dynamic> _readJsonObject(File file) {
    final decoded = jsonDecode(file.readAsStringSync());
    if (decoded is! Map<String, dynamic>) {
      throw ManifestBuildException('${file.path}: root must be a JSON object');
    }
    return decoded;
  }
}

bool manifestSemanticallyEqual(String a, String b) => jsonSemanticallyEqual(a, b);
