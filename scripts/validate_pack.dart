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
  final bookIds = <String>{};
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
      bookIds.add(bookId);
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
  final manifestPackIds = _manifestPackIds(repo, errors);

  for (final pack in discoverPacksWithLesson(repo.path)) {
    final relativePath = pack.relativePath;
    if (!seenBookPaths.add(relativePath)) {
      errors.add('Duplicate pack directory: $relativePath');
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
  if (difficulty is int && (difficulty < 1 || difficulty > 10)) {
    errors.add('$prefix difficulty must be between 1 and 10');
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
  if (references is List) {
    for (var i = 0; i < references.length; i++) {
      final ref = references[i];
      if (ref is! Map<String, dynamic>) {
        errors.add('$prefix references[$i] must be an object');
        continue;
      }
      final refTitle = ref['title'];
      if (refTitle is! String || refTitle.isEmpty) {
        errors.add('$prefix references[$i] missing "title"');
      }
      final url = ref['url'];
      if (url is String && url.isNotEmpty && !url.startsWith('http')) {
        errors.add('$prefix references[$i] url must be http(s): $url');
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
    }

    final correctIndex = question['correctIndex'];
    if (correctIndex is! int ||
        correctIndex < 0 ||
        correctIndex >= answers.length) {
      errors.add('$qPrefix has invalid correctIndex: $correctIndex');
    }
  }
}

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
