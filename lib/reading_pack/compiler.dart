import 'package:path/path.dart' as p;

import 'editorial_provenance.dart';
import 'json_writer.dart';
import 'parser.dart';
import 'trust_catalog.dart';

class CompiledArtifacts {
  CompiledArtifacts({
    required this.lessonJson,
    required this.textTxt,
    required this.quizJson,
    required this.provenanceJson,
    required this.licenseMd,
  });

  final String lessonJson;
  final String textTxt;
  final String quizJson;
  final String provenanceJson;
  final String licenseMd;

  Map<String, String> asFileMap() => {
    'lesson.json': lessonJson,
    'text.txt': textTxt,
    'quiz.json': quizJson,
    'provenance.json': provenanceJson,
    'license.md': licenseMd,
  };
}

class ReadingPackCompiler {
  CompiledArtifacts compile(
    ReadingPackDocument doc, {
    required String packDirPath,
  }) {
    final tier = _detectTier(packDirPath);
    final bookId = _bookId(doc, packDirPath);
    final text = _normalizeText(doc.text);
    final quiz = _buildQuiz(doc.quiz);
    final lesson = _buildLesson(doc, text, quiz);
    final provenance = _buildProvenance(doc, tier, bookId);
    final license = _buildLicense(doc);

    return CompiledArtifacts(
      lessonJson: encodeJsonPretty(lesson),
      textTxt: '$text\n',
      quizJson: encodeJsonPretty(quiz),
      provenanceJson: encodeJsonPretty(provenance),
      licenseMd: license,
    );
  }

  String _detectTier(String packDirPath) {
    final normalized = p.normalize(packDirPath);
    final parts = p.split(normalized);
    for (final tier in ['official', 'community', 'experimental']) {
      if (parts.contains(tier)) return tier;
    }
    return 'community';
  }

  String _bookId(ReadingPackDocument doc, String packDirPath) {
    final fromMetadata = doc.metadata['Book ID'];
    if (fromMetadata != null && fromMetadata.isNotEmpty) {
      return fromMetadata;
    }
    return p.basename(packDirPath);
  }

  String _normalizeText(String text) {
    final paragraphs = text
        .split(RegExp(r'\n\s*\n'))
        .map((p) => p.trim())
        .where((p) => p.isNotEmpty)
        .toList();
    return paragraphs.join('\n\n');
  }

  Map<String, dynamic> _buildLesson(
    ReadingPackDocument doc,
    String text,
    Map<String, dynamic> quiz,
  ) {
    final metadata = doc.metadata;
    final transparency = doc.transparency;
    final license = _parseLicense(transparency['License'] ?? '');
    final coverFamily = _nonEmpty(metadata['Cover family']);
    final audience = _nonEmpty(metadata['Audience']);
    final subtitle = _nonEmpty(metadata['Subtitle']);
    final editionVersion = _nonEmpty(metadata['Edition version']);
    final trustRaw = transparency['Trust classification'] ?? '';
    final trustClassification = TrustCatalog.canonicalId(trustRaw);
    if (trustClassification == null) {
      throw ReadingPackParseException('Missing required trust classification');
    }
    if (editionVersion == null || editionVersion.isEmpty) {
      throw ReadingPackParseException('Missing required metadata: Edition version');
    }

    final editorialHistory = _buildEditorialHistory(doc);
    final editorialProvenance = buildEditorialProvenance(doc);

    final lesson = <String, dynamic>{
      'id': metadata['Pack ID'] ?? '',
      'title': metadata['Title'] ?? doc.title,
      'language': metadata['Original language'] ?? '',
      'version': metadata['Version'] ?? '1.0.0',
      'editionVersion': editionVersion,
      'updated': _earliestRevisionDate(doc.revisions),
      'description': metadata['Blurb'] ?? '',
      'author': {'name': transparency['Created by'] ?? ''},
      'license': {
        'name': license.name,
        'url': transparency['License URL'] ?? '',
        'spdx': license.spdx,
      },
      'recommendedWritingSystem': metadata['Writing system'] ?? '',
      'recommendedProfile': metadata['Recommended profile'] ?? '',
      'recommendedLevel': metadata['Recommended level'] ?? '',
      'tags': _splitList(metadata['Tags'] ?? ''),
      'difficulty': _parseDifficulty(metadata['Difficulty'] ?? ''),
      'estimatedReadingTime': _parseReadingTime(
        metadata['Estimated reading time'] ?? '',
      ),
      'translation': metadata['Translation summary'] ?? '',
      'text': text,
      'quiz': quiz,
    };

    if (coverFamily != null) {
      lesson['coverFamily'] = coverFamily;
    }
    if (audience != null) {
      lesson['audience'] = audience;
    }
    if (subtitle != null) {
      lesson['subtitle'] = subtitle;
    }
    if (trustClassification != null) {
      lesson['trustClassification'] = trustClassification;
    }
    if (editorialHistory.isNotEmpty) {
      lesson['editorialHistory'] = editorialHistory;
    }

    lesson.addAll(editorialProvenance.toLessonJson());

    if (doc.world != null && !doc.world!.isEmpty) {
      lesson['world'] = doc.world!.toJson();
    }

    return lesson;
  }

  Map<String, dynamic> _buildQuiz(QuizSection? quiz) {
    if (quiz == null || quiz.questions.isEmpty) {
      return {'title': '', 'questions': <Map<String, dynamic>>[]};
    }

    return {
      'title': quiz.title ?? '',
      'questions': quiz.questions.map((q) {
        return {
          'type': 'single_choice',
          'question': q.question,
          'answers': q.answers,
          'correctIndex': q.correctIndex,
          if (q.explanation != null && q.explanation!.isNotEmpty)
            'explanation': q.explanation,
        };
      }).toList(),
    };
  }

  Map<String, dynamic> _buildProvenance(
    ReadingPackDocument doc,
    String tier,
    String bookId,
  ) {
    final metadata = doc.metadata;
    final transparency = doc.transparency;
    final editorialProvenance = buildEditorialProvenance(doc);

    return {
      'packId': metadata['Pack ID'] ?? '',
      'bookId': bookId,
      'editorialStatus': tier,
      'createdAt': _earliestRevisionDate(doc.revisions),
      'lastReviewedAt': _parseHumanReviewDate(
        transparency['Human reviewed'] ?? '',
      ),
      'editors': _splitList(transparency['Editor'] ?? ''),
      'aiAssistance': {
        'used': _parseBool(transparency['LLM assisted'] ?? 'no'),
        'tools': <String>[],
        'humanReview': _humanReviewNote(doc),
      },
      'sources': _buildProvenanceSources(doc, editorialProvenance),
      'revisionNotes': _revisionNotes(doc),
    };
  }

  String _buildLicense(ReadingPackDocument doc) {
    final title = doc.metadata['Title'] ?? doc.title;
    final license = _parseLicense(doc.transparency['License'] ?? '');
    final url = doc.transparency['License URL'] ?? '';
    final dedication = license.name.contains('CC0')
        ? ' (public domain dedication)'
        : '';

    return '''# License

**$title** is released under **${license.name}**$dedication.

- SPDX: `${license.spdx}`
- Full text: $url

You may copy, modify, and distribute this work for any purpose without asking permission.
''';
  }

  List<Map<String, dynamic>> _buildProvenanceSources(
    ReadingPackDocument doc,
    EditorialProvenance editorialProvenance,
  ) {
    if (editorialProvenance.youtubeVideoIds.isNotEmpty) {
      return editorialProvenance.toProvenanceSources();
    }

    final entries = <Map<String, dynamic>>[];
    for (final source in doc.sources) {
      if (source.deprecated) continue;
      if (!_isProvenanceSource(source.availability)) continue;
      entries.add({'type': source.availability, 'description': source.title});
    }
    return entries;
  }

  bool _isProvenanceSource(String availability) {
    return availability == 'original' ||
        availability == 'public_domain' ||
        availability == 'adaptation';
  }

  String _humanReviewNote(ReadingPackDocument doc) {
    for (final source in doc.sources) {
      if (source.availability == 'original' && source.editorNotes != null) {
        return source.editorNotes!;
      }
    }
    return doc.transparency['Editorial notes'] ??
        doc.metadata['Editorial notes'] ??
        '';
  }

  String _revisionNotes(ReadingPackDocument doc) {
    final explicit = doc.transparency['Revision notes'];
    if (explicit != null && explicit.isNotEmpty) {
      return explicit;
    }
    if (doc.revisions.isNotEmpty) {
      return doc.revisions.last.note;
    }
    return doc.metadata['Editorial notes'] ?? '';
  }

  String _earliestRevisionDate(List<RevisionEntry> revisions) {
    if (revisions.isEmpty) return '';
    final dates =
        revisions.map((r) => r.date).where((d) => d.isNotEmpty).toList()
          ..sort();
    return dates.isNotEmpty ? dates.first : '';
  }

  String _parseHumanReviewDate(String raw) {
    final match = RegExp(r'(\d{4}-\d{2}-\d{2})').firstMatch(raw);
    return match?.group(1) ?? '';
  }

  Map<String, dynamic> _buildEditorialHistory(ReadingPackDocument doc) {
    final dates = doc.revisions
        .map((r) => r.date)
        .where((d) => d.isNotEmpty)
        .toList()
      ..sort();
    final first = dates.isNotEmpty ? dates.first : '';
    final last = dates.isNotEmpty ? dates.last : '';
    final reviewed = _parseHumanReviewDate(
      doc.transparency['Human reviewed'] ?? '',
    );
    final lastUpdate = [last, reviewed].where((d) => d.isNotEmpty).toList()
      ..sort();
    final history = <String, dynamic>{};
    if (first.isNotEmpty) {
      history['firstPublished'] = first;
    }
    if (lastUpdate.isNotEmpty) {
      history['lastEditorialUpdate'] = lastUpdate.last;
    }
    return history;
  }

  int _parseDifficulty(String raw) {
    final match = RegExp(r'(\d+)').firstMatch(raw);
    return match != null ? int.parse(match.group(1)!) : 1;
  }

  int _parseReadingTime(String raw) {
    final match = RegExp(r'(\d+)').firstMatch(raw);
    return match != null ? int.parse(match.group(1)!) : 0;
  }

  bool _parseBool(String raw) {
    return raw.trim().toLowerCase().startsWith('yes');
  }

  List<String> _splitList(String raw) {
    return raw
        .split(',')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();
  }

  String? _nonEmpty(String? value) {
    if (value == null) return null;
    final trimmed = value.trim();
    return trimmed.isEmpty ? null : trimmed;
  }

  _LicenseInfo _parseLicense(String raw) {
    final spdxMatch = RegExp(r'SPDX:\s*([^\)]+)\)').firstMatch(raw);
    final spdx = spdxMatch?.group(1)?.trim() ?? '';
    final name = raw.replaceAll(RegExp(r'\s*\(SPDX:[^)]+\)'), '').trim();
    return _LicenseInfo(name: name.isEmpty ? raw : name, spdx: spdx);
  }
}

class _LicenseInfo {
  _LicenseInfo({required this.name, required this.spdx});
  final String name;
  final String spdx;
}
