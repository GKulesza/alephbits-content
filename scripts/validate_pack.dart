#!/usr/bin/env dart
// ignore_for_file: avoid_print

import 'dart:convert';
import 'dart:io';

import 'package:alephbits_content/manifest/builder.dart';
import 'package:alephbits_content/manifest/manifest_runner.dart';
import 'package:alephbits_content/reading_pack/compile_runner.dart';
import 'package:alephbits_content/repository/pack_discovery.dart';

/// Validates the alephbits-content repository.
///
/// Usage:
///   dart run scripts/validate_pack.dart [repository_root]
void main(List<String> args) {
  final root = args.isNotEmpty ? args.first : Directory.current.path;
  final repo = Directory(root);
  if (!repo.existsSync()) {
    _fail(['Repository root does not exist: $root']);
  }

  final errors = <String>[];
  _validateManifestDrift(repo, errors);
  _validateRepositoryManifest(repo, errors);
  _validateAllPacks(repo, errors);
  _validateCoverAudit(repo, errors);

  if (errors.isEmpty) {
    print('✓ All validations passed.');
    exit(0);
  }

  stderr.writeln('Validation failed with ${errors.length} issue(s):');
  for (final error in errors) {
    stderr.writeln('  • $error');
  }
  exit(1);
}

void _fail(List<String> errors) {
  for (final error in errors) {
    stderr.writeln('  • $error');
  }
  exit(1);
}

void _validateManifestDrift(Directory repo, List<String> errors) {
  try {
    final drift = checkManifestDrift(repo.path);
    if (drift != null) {
      errors.add('manifest.json: ${drift.message}');
    }

    final manifestFile = File('${repo.path}/manifest.json');
    if (manifestFile.existsSync()) {
      final manifest = _readJsonObject(manifestFile, errors, 'manifest.json');
      if (manifest != null) {
        for (final item in validateManifestCoverage(repo.path, manifest)) {
          errors.add('manifest.json: ${item.message}');
        }
      }
    }
  } on ManifestBuildException catch (e) {
    errors.add('build_manifest: $e');
  }
}

void _validateRepositoryManifest(Directory repo, List<String> errors) {
  final manifestFile = File('${repo.path}/manifest.json');
  if (!manifestFile.existsSync()) {
    errors.add('Missing repository manifest.json');
    return;
  }

  final manifest = _readJsonObject(manifestFile, errors, 'manifest.json');
  if (manifest == null) return;

  for (final field in [
    'repositoryVersion',
    'schemaVersion',
    'minimumAppVersion',
    'generatedAt',
    'officialPackCount',
    'communityPackCount',
    'experimentalPackCount',
    'supportedLanguages',
    'supportedWritingSystems',
    'categories',
    'featuredCollections',
    'libraryStatistics',
    'packs',
  ]) {
    if (!manifest.containsKey(field)) {
      errors.add('manifest.json: missing required field "$field"');
    }
  }

  final packs = manifest['packs'];
  if (packs is! List) {
    errors.add('manifest.json: "packs" must be an array');
    return;
  }

  final packIds = <String>{};
  final bookIdOwners = <String, String>{};
  var officialCount = 0;

  for (var i = 0; i < packs.length; i++) {
    final entry = packs[i];
    if (entry is! Map<String, dynamic>) {
      errors.add('manifest.json packs[$i]: must be an object');
      continue;
    }

    final id = entry['id'];
    final bookId = entry['bookId'];
    final path = entry['path'];
    final tier = entry['tier'];

    if (id is! String || id.isEmpty) {
      errors.add('manifest.json packs[$i]: missing "id"');
      continue;
    }
    if (packIds.contains(id)) {
      errors.add('manifest.json: duplicate pack id "$id"');
    }
    packIds.add(id);

    if (bookId is String && bookId.isNotEmpty) {
      final existing = bookIdOwners[bookId];
      if (existing != null) {
        errors.add(
          'manifest.json: duplicate bookId "$bookId" (packs "$existing" and "$id")',
        );
      } else {
        bookIdOwners[bookId] = id;
      }
    }

    if (path is! String || path.isEmpty) {
      errors.add('manifest.json pack "$id": missing "path"');
      continue;
    }

    final packDir = Directory('${repo.path}/$path');
    if (!packDir.existsSync()) {
      errors.add('manifest.json pack "$id": path does not exist: $path');
    }

    if (tier == 'official') {
      officialCount++;
    }
  }

  final declaredOfficial = manifest['officialPackCount'];
  if (declaredOfficial is int && declaredOfficial != officialCount) {
    errors.add(
      'manifest.json: officialPackCount is $declaredOfficial but '
      '$officialCount official packs are indexed',
    );
  }

  final declaredCommunity = manifest['communityPackCount'];
  if (declaredCommunity is int) {
    final communityCount = packs.where((p) {
      return p is Map<String, dynamic> && p['tier'] == 'community';
    }).length;
    if (declaredCommunity != communityCount) {
      errors.add(
        'manifest.json: communityPackCount is $declaredCommunity but '
        '$communityCount community packs are indexed',
      );
    }
  }

  final declaredExperimental = manifest['experimentalPackCount'];
  if (declaredExperimental is int) {
    final experimentalCount = packs.where((p) {
      return p is Map<String, dynamic> && p['tier'] == 'experimental';
    }).length;
    if (declaredExperimental != experimentalCount) {
      errors.add(
        'manifest.json: experimentalPackCount is $declaredExperimental but '
        '$experimentalCount experimental packs are indexed',
      );
    }
  }

  final collections = manifest['featuredCollections'];
  if (collections is List) {
    for (var i = 0; i < collections.length; i++) {
      final collection = collections[i];
      if (collection is! Map<String, dynamic>) continue;
      final collectionPackIds = collection['packIds'];
      if (collectionPackIds is List) {
        for (final packId in collectionPackIds) {
          if (packId is String && !packIds.contains(packId)) {
            errors.add(
              'manifest.json featuredCollections[$i]: '
              'references unknown pack id "$packId"',
            );
          }
        }
      }
    }
  }
}

void _validateAllPacks(Directory repo, List<String> errors) {
  final seenPackIds = <String>{};
  final seenBookPaths = <String>{};
  final seenSlugs = <String>{};
  final manifestPackIds = _manifestPackIds(repo, errors);

  for (final pack in discoverPacksWithLesson(repo.path)) {
    final relativePath = pack.relativePath;
    if (!seenBookPaths.add(relativePath)) {
      errors.add('Duplicate pack directory: $relativePath');
    }
    final slug = relativePath.split('/').last;
    if (!seenSlugs.add(slug)) {
      errors.add('Duplicate pack slug "$slug"');
    }
    _validatePackDirectory(
      repo,
      Directory(pack.absolutePath),
      pack.tier,
      seenPackIds,
      manifestPackIds,
      errors,
    );
  }
}

void _validateCoverAudit(Directory repo, List<String> errors) {
  final manifestFile = File('${repo.path}/manifest.json');
  if (!manifestFile.existsSync()) {
    return;
  }

  final manifest = _readJsonObject(manifestFile, errors, 'manifest.json');
  if (manifest == null) return;

  final catalogFile = File('${repo.path}/covers/catalog.json');
  if (!catalogFile.existsSync()) {
    errors.add('covers/catalog.json is missing');
    return;
  }

  final catalog = _readJsonObject(catalogFile, errors, 'covers/catalog.json');
  if (catalog == null) return;

  final defaultFamily = catalog['defaultFamily'];
  final families = catalog['families'];
  final customCovers = catalog['customCovers'];
  if (defaultFamily is! String || defaultFamily.isEmpty) {
    errors.add('covers/catalog.json missing non-empty "defaultFamily"');
    return;
  }
  if (families is! Map<String, dynamic>) {
    errors.add('covers/catalog.json missing "families" object');
    return;
  }

  for (final familyEntry in families.entries) {
    final family = familyEntry.value;
    if (family is! Map<String, dynamic>) {
      errors.add('covers/catalog.json family "${familyEntry.key}" must be an object');
      continue;
    }
    final variants = family['variants'];
    if (variants is! List || variants.isEmpty) {
      errors.add('covers/catalog.json family "${familyEntry.key}" has no variants');
      continue;
    }
    for (final variant in variants) {
      if (variant is! Map<String, dynamic>) {
        errors.add('covers/catalog.json family "${familyEntry.key}" contains invalid variant');
        continue;
      }
      final sourcePath = variant['sourcePath'];
      if (sourcePath is! String || sourcePath.isEmpty) {
        errors.add('covers/catalog.json family "${familyEntry.key}" variant missing sourcePath');
        continue;
      }
      if (!File('${repo.path}/$sourcePath').existsSync()) {
        errors.add(
          'covers/catalog.json family "${familyEntry.key}" references missing asset: $sourcePath',
        );
      }
    }
  }

  final packs = manifest['packs'];
  if (packs is! List) {
    return;
  }

  final customCoverMap =
      customCovers is Map<String, dynamic> ? customCovers : const <String, dynamic>{};

  for (final entry in packs.whereType<Map<String, dynamic>>()) {
    final id = entry['id'];
    final path = entry['path'];
    if (id is! String || path is! String) continue;

    final lessonFile = File('${repo.path}/$path/lesson.json');
    final lesson = _readJsonObject(lessonFile, errors, '$path/lesson.json');
    if (lesson == null) continue;

    final explicitCover = _nonEmptyString(entry['cover']) ?? _nonEmptyString(lesson['cover']);
    final explicitCoverFamily =
        _nonEmptyString(entry['coverFamily']) ?? _nonEmptyString(lesson['coverFamily']);
    final categories =
        (entry['categories'] is List)
            ? (entry['categories'] as List).whereType<String>().where((s) => s.isNotEmpty).toList()
            : const <String>[];

    if (explicitCover != null) {
      if (!customCoverMap.containsKey(explicitCover)) {
        errors.add('pack "$id" references missing custom cover "$explicitCover"');
      }
      continue;
    }

    if (explicitCoverFamily != null) {
      if (!families.containsKey(explicitCoverFamily)) {
        errors.add('pack "$id" references missing coverFamily "$explicitCoverFamily"');
      }
      continue;
    }

    final matchingCategoryFamily = categories.firstWhere(
      families.containsKey,
      orElse: () => '',
    );
    if (matchingCategoryFamily.isEmpty) {
      errors.add(
        'pack "$id" would fall back to default cover because no category or coverFamily matches a cover family',
      );
    }
  }
}

Set<String> _manifestPackIds(Directory repo, List<String> errors) {
  final manifestFile = File('${repo.path}/manifest.json');
  if (!manifestFile.existsSync()) return {};
  final manifest = _readJsonObject(manifestFile, errors, 'manifest.json');
  if (manifest == null) return {};
  final packs = manifest['packs'];
  if (packs is! List) return {};
  return packs
      .whereType<Map<String, dynamic>>()
      .map((p) => p['id'])
      .whereType<String>()
      .toSet();
}

void _validatePackDirectory(
  Directory repo,
  Directory packDir,
  String tier,
  Set<String> seenPackIds,
  Set<String> manifestPackIds,
  List<String> errors,
) {
  final relativePath = _relativePath(repo.path, packDir.path);
  final prefix = '$relativePath:';

  final lessonFile = File('${packDir.path}/lesson.json');
  final licenseFile = File('${packDir.path}/license.md');
  final textFile = File('${packDir.path}/text.txt');
  final quizFile = File('${packDir.path}/quiz.json');
  final provenanceFile = File('${packDir.path}/provenance.json');
  final bookManifestFile = File('${packDir.path}/manifest.json');

  if (!lessonFile.existsSync()) {
    errors.add('$prefix missing required lesson.json');
    return;
  }
  if (!licenseFile.existsSync()) {
    errors.add('$prefix missing required license.md');
  }

  final readingPackFile = File('${packDir.path}/reading-pack.md');
  if (readingPackFile.existsSync()) {
    final compileResult = compileAndCheckDirectory(packDir.path);
    if (compileResult.parseError != null) {
      errors.add('$prefix reading-pack.md parse error: ${compileResult.parseError}');
    } else if (compileResult.hasDrift) {
      for (final drift in compileResult.drift) {
        errors.add('$prefix compile drift in ${drift.file}: ${drift.message}');
      }
    }
  }

  final lesson = _readJsonObject(lessonFile, errors, '$relativePath/lesson.json');
  if (lesson == null) return;

  final id = lesson['id'];
  final title = lesson['title'];
  final language = lesson['language'];
  final text = lesson['text'];

  if (id is! String || id.isEmpty) {
    errors.add('$prefix lesson.json missing non-empty "id"');
  } else {
    if (!seenPackIds.add(id)) {
      errors.add('$prefix duplicate pack id "$id"');
    }
    if (!manifestPackIds.contains(id)) {
      errors.add('$prefix pack id "$id" missing from manifest.json');
    }
  }

  if (title is! String || title.isEmpty) {
    errors.add('$prefix lesson.json missing non-empty "title"');
  }
  if (language is! String || language.isEmpty) {
    errors.add('$prefix lesson.json missing non-empty "language"');
  }
  if (text is! String || text.isEmpty) {
    errors.add('$prefix lesson.json missing non-empty "text"');
  }

  final difficulty = lesson['difficulty'];
  if (difficulty is int && (difficulty < 1 || difficulty > 8)) {
    errors.add('$prefix difficulty must be between 1 and 8');
  }

  final editionVersion = lesson['editionVersion'];
  if (editionVersion is! String || editionVersion.isEmpty) {
    errors.add('$prefix lesson.json missing non-empty "editionVersion"');
  }

  final trustClassification = lesson['trustClassification'];
  if (trustClassification is! String || trustClassification.isEmpty) {
    errors.add('$prefix lesson.json missing non-empty "trustClassification"');
  }

  if (textFile.existsSync() && text is String) {
    final fileText = textFile.readAsStringSync().trim();
    final lessonText = text.trim();
    if (fileText != lessonText) {
      errors.add('$prefix text.txt does not match lesson.json "text" field');
    }
  }

  Map<String, dynamic>? inlineQuiz;
  if (lesson['quiz'] is Map<String, dynamic>) {
    inlineQuiz = lesson['quiz'] as Map<String, dynamic>;
    _validateQuiz(inlineQuiz, errors, '$prefix lesson.json quiz');
  }

  if (quizFile.existsSync()) {
    final quiz = _readJsonObject(quizFile, errors, '$relativePath/quiz.json');
    if (quiz != null) {
      _validateQuiz(quiz, errors, '$prefix quiz.json');
      if (inlineQuiz != null && !_quizzesEquivalent(inlineQuiz, quiz)) {
        errors.add('$prefix quiz.json does not match lesson.json "quiz" field');
      }
    }
  }

  if (tier == 'official' && !provenanceFile.existsSync()) {
    errors.add('$prefix official pack missing provenance.json');
  }

  if (provenanceFile.existsSync()) {
    final provenance = _readJsonObject(
      provenanceFile,
      errors,
      '$relativePath/provenance.json',
    );
    if (provenance != null) {
      final packId = provenance['packId'];
      if (packId is String && id is String && packId != id) {
        errors.add(
          '$prefix provenance.json packId "$packId" does not match lesson id "$id"',
        );
      }
      if (provenance['editorialStatus'] == 'official' && tier != 'official') {
        errors.add(
          '$prefix provenance marks official but pack is under $tier/',
        );
      }
    }
  }

  if (bookManifestFile.existsSync()) {
    final bookManifest = _readJsonObject(
      bookManifestFile,
      errors,
      '$relativePath/manifest.json',
    );
    if (bookManifest != null) {
      final defaultLang = bookManifest['defaultLanguage'];
      if (defaultLang is String && language is String && defaultLang != language) {
        errors.add(
          '$prefix book manifest defaultLanguage "$defaultLang" '
          'does not match lesson language "$language"',
        );
      }
      final translations = bookManifest['availableTranslations'];
      if (translations is Map<String, dynamic> && language is String) {
        if (!translations.containsKey(language)) {
          errors.add(
            '$prefix book manifest missing translation entry for "$language"',
          );
        }
      }
    }
  }

  final references = lesson['references'];
  if (references is List && references.isNotEmpty) {
    errors.add(
      '$prefix lesson.json must not use legacy references[] — use inspiredBy.youtube',
    );
  }

  final inspiredBy = lesson['inspiredBy'];
  if (inspiredBy is Map<String, dynamic>) {
    final youtube = inspiredBy['youtube'];
    if (youtube is String && youtube.isNotEmpty) {
      if (youtube.contains('http') || youtube.contains('youtube.com')) {
        errors.add('$prefix inspiredBy.youtube must store video IDs only');
      }
      final ids = youtube.split(',').map((s) => s.trim()).where((s) => s.isNotEmpty);
      final seen = <String>{};
      for (final id in ids) {
        if (!RegExp(r'^[A-Za-z0-9_-]{11}$').hasMatch(id)) {
          errors.add('$prefix inspiredBy.youtube has invalid video id: $id');
        }
        if (!seen.add(id)) {
          errors.add('$prefix inspiredBy.youtube duplicates video id: $id');
        }
      }
    }
  }

  final inspirationDates = lesson['inspirationDates'];
  if (inspirationDates is List) {
    for (var i = 0; i < inspirationDates.length; i++) {
      final date = inspirationDates[i];
      if (date is! String || !RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(date)) {
        errors.add('$prefix inspirationDates[$i] must be YYYY-MM-DD');
      }
    }
  }
}

void _validateQuiz(
  Map<String, dynamic> quiz,
  List<String> errors,
  String prefix,
) {
  final questions = quiz['questions'];
  if (questions is! List || questions.isEmpty) {
    errors.add('$prefix must have at least one question');
    return;
  }

  for (var i = 0; i < questions.length; i++) {
    final question = questions[i];
    final qPrefix = '$prefix questions[$i]';
    if (question is! Map<String, dynamic>) {
      errors.add('$qPrefix must be an object');
      continue;
    }

    final type = question['type'];
    if (type != 'single_choice') {
      errors.add('$qPrefix unsupported question type: $type');
    }

    final text = question['question'];
    if (text is! String || text.isEmpty) {
      errors.add('$qPrefix missing question text');
    } else {
      for (final pattern in _metadataQuizQuestionPatterns) {
        if (pattern.hasMatch(text)) {
          errors.add(
            '$qPrefix asks about metadata/title-page trivia: "$text"',
          );
          break;
        }
      }
    }

    final answers = question['answers'];
    if (answers is! List || answers.isEmpty) {
      errors.add('$qPrefix must have answers');
      continue;
    }

    final answerTexts = <String>{};
    for (var j = 0; j < answers.length; j++) {
      final answer = answers[j];
      if (answer is! String || answer.isEmpty) {
        errors.add('$qPrefix answers[$j] must be non-empty string');
        continue;
      }
      final key = answer.toLowerCase();
      if (!answerTexts.add(key)) {
        errors.add('$qPrefix has duplicate answer: $answer');
      }
      for (final pattern in _placeholderAnswerPatterns) {
        if (pattern.hasMatch(answer)) {
          errors.add('$qPrefix uses placeholder answer: "$answer"');
          break;
        }
      }
    }

    final correctIndex = question['correctIndex'];
    if (correctIndex is! int ||
        correctIndex < 0 ||
        correctIndex >= answers.length) {
      errors.add('$qPrefix has invalid correctIndex: $correctIndex');
    }
  }
}

final _metadataQuizQuestionPatterns = [
  RegExp(r'o czym opowiada tekst', caseSensitive: false),
  RegExp(r'do jakiej grupy czytelnik', caseSensitive: false),
  RegExp(r'jaki rodzaj tre[sś]ci', caseSensitive: false),
  RegExp(r'jaki gatunek tekstu', caseSensitive: false),
  RegExp(r'ile minut zajmuje orientacyjna', caseSensitive: false),
  RegExp(r'orientacyjna lektura', caseSensitive: false),
  RegExp(r'kończy się zdaniem domykającym', caseSensitive: false),
  RegExp(r'reading time', caseSensitive: false),
  RegExp(r'estimated reading time', caseSensitive: false),
  RegExp(r'trust classification', caseSensitive: false),
  RegExp(r'content type', caseSensitive: false),
  RegExp(r'\baudience\b', caseSensitive: false),
  RegExp(r'\bcategory\b', caseSensitive: false),
  RegExp(r'\bmetadata\b', caseSensitive: false),
  RegExp(r'\bedition version\b', caseSensitive: false),
];

final _placeholderAnswerPatterns = [
  RegExp(r'inna odpowied', caseSensitive: false),
  RegExp(r'nie wynika z tekstu', caseSensitive: false),
  RegExp(r'żadna z powyższych', caseSensitive: false),
  RegExp(r'zadna z powyzszych', caseSensitive: false),
];

bool _quizzesEquivalent(Map<String, dynamic> a, Map<String, dynamic> b) {
  return jsonEncode(_normalizeQuiz(a)) == jsonEncode(_normalizeQuiz(b));
}

Map<String, dynamic> _normalizeQuiz(Map<String, dynamic> quiz) {
  return {
    'title': quiz['title'],
    'questions': (quiz['questions'] as List?)?.map((q) {
      if (q is Map<String, dynamic>) {
        return {
          'type': q['type'],
          'question': q['question'],
          'answers': q['answers'],
          'correctIndex': q['correctIndex'],
          'explanation': q['explanation'],
        };
      }
      return q;
    }).toList(),
  };
}

Map<String, dynamic>? _readJsonObject(
  File file,
  List<String> errors,
  String label,
) {
  try {
    final decoded = jsonDecode(file.readAsStringSync());
    if (decoded is! Map<String, dynamic>) {
      errors.add('$label root must be a JSON object');
      return null;
    }
    return decoded;
  } on FormatException catch (e) {
    errors.add('$label invalid JSON: ${e.message}');
    return null;
  }
}

String _relativePath(String repoRoot, String absolutePath) {
  if (absolutePath.startsWith(repoRoot)) {
    return absolutePath.substring(repoRoot.length + 1);
  }
  return absolutePath;
}

String? _nonEmptyString(Object? value) {
  if (value is! String) return null;
  final trimmed = value.trim();
  return trimmed.isEmpty ? null : trimmed;
}
