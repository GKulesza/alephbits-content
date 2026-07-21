import 'package:path/path.dart' as p;

import 'world_metadata.dart';

class RevisionEntry {
  RevisionEntry({required this.version, required this.date, required this.note});

  final String version;
  final String date;
  final String note;
}

class SourceEntry {
  SourceEntry({
    required this.title,
    required this.author,
    required this.url,
    required this.license,
    required this.retrievalDate,
    required this.availability,
    required this.deprecated,
    required this.editorNotes,
    this.referenceDescription,
  });

  final String title;
  final String author;
  final String? url;
  final String license;
  final String? retrievalDate;
  final String availability;
  final bool deprecated;
  final String? editorNotes;
  final String? referenceDescription;
}

class QuizQuestion {
  QuizQuestion({
    required this.question,
    required this.answers,
    required this.correctIndex,
    this.explanation,
    this.textReference,
  });

  final String question;
  final List<String> answers;
  final int correctIndex;
  final String? explanation;
  final String? textReference;
}

class QuizSection {
  QuizSection({this.title, required this.questions});

  final String? title;
  final List<QuizQuestion> questions;
}

class ReadingPackDocument {
  ReadingPackDocument({
    required this.title,
    required this.metadata,
    required this.transparency,
    required this.revisions,
    required this.sources,
    required this.text,
    this.quiz,
    this.world,
  });

  final String title;
  final Map<String, String> metadata;
  final Map<String, String> transparency;
  final List<RevisionEntry> revisions;
  final List<SourceEntry> sources;
  final String text;
  final QuizSection? quiz;

  /// Optional semantic world furniture — never required for compile.
  final PackWorldMetadata? world;
}

class ReadingPackParseException implements Exception {
  ReadingPackParseException(this.message);
  final String message;

  @override
  String toString() => message;
}

class ReadingPackParser {
  /// Top-level reading-pack.md sections only. In-body `##` headings (e.g. chapter
  /// titles inside Text) must not start a new section.
  static const knownSections = <String>{
    'Metadata',
    'Editorial Transparency',
    'Sources',
    'Text',
    'Quiz',
    'Future Extensions',
  };

  ReadingPackDocument parse(String markdown, {String? packDirPath}) {
    final lines = markdown.replaceAll('\r\n', '\n').split('\n');
    if (lines.isEmpty || !lines.first.startsWith('# ')) {
      throw ReadingPackParseException('reading-pack.md must start with "# Title".');
    }

    final title = lines.first.substring(2).trim();
    final sections = _splitSections(lines.sublist(1));

    final metadata = _parseFields(sections['Metadata'] ?? '', requiredKeys: [
      'Pack ID',
      'Title',
      'Original language',
    ]);

    final transparency = _parseFields(sections['Editorial Transparency'] ?? '', requiredKeys: [
      'License',
    ]);

    final revisions = _parseRevisionTable(sections['Editorial Transparency'] ?? '');
    final sources = _parseSources(sections['Sources'] ?? '');
    final text = _parseTextSection(sections['Text'] ?? '');
    final quiz = _parseQuiz(sections['Quiz'] ?? '');
    final world = PackWorldMetadata.parse(sections['Metadata'] ?? '');

    if (text.trim().isEmpty) {
      throw ReadingPackParseException('Text section must not be empty.');
    }

    // Default book ID from directory slug when not in metadata.
    metadata.putIfAbsent('Book ID', () {
      if (packDirPath != null) {
        return p.basename(packDirPath);
      }
      return '';
    });

    return ReadingPackDocument(
      title: title,
      metadata: metadata,
      transparency: transparency,
      revisions: revisions,
      sources: sources,
      text: text.trim(),
      quiz: quiz,
      world: world,
    );
  }

  Map<String, String> _splitSections(List<String> lines) {
    final sections = <String, String>{};
    String? current;
    final buffer = <String>[];

    void flush() {
      if (current != null) {
        sections[current] = buffer.join('\n').trim();
      }
      buffer.clear();
    }

    for (final line in lines) {
      if (line.startsWith('## ')) {
        final name = line.substring(3).trim();
        if (knownSections.contains(name)) {
          flush();
          current = name;
          continue;
        }
      }
      if (current != null) {
        buffer.add(line);
      }
    }
    flush();
    return sections;
  }

  Map<String, String> _parseFields(String section, {List<String> requiredKeys = const []}) {
    final fields = <String, String>{};
    for (final line in section.split('\n')) {
      final match = RegExp(r'^\*\*([^*:]+):\*\*\s*(.+)$').firstMatch(line.trim());
      if (match == null) continue;
      fields[match.group(1)!.trim()] = _cleanValue(match.group(2)!);
    }

    for (final key in requiredKeys) {
      if (!fields.containsKey(key) || fields[key]!.isEmpty) {
        throw ReadingPackParseException('Missing required field: $key');
      }
    }
    return fields;
  }

  String _cleanValue(String raw) {
    var value = raw.trim();
    if (value.startsWith('`') && value.endsWith('`')) {
      value = value.substring(1, value.length - 1);
    }
    if (value.startsWith('*(') && value.endsWith(')*')) {
      return '';
    }
    return value;
  }

  List<RevisionEntry> _parseRevisionTable(String section) {
    final entries = <RevisionEntry>[];
    final lines = section.split('\n');
    var inTable = false;
    for (final line in lines) {
      if (line.startsWith('| Version |')) {
        inTable = true;
        continue;
      }
      if (!inTable) continue;
      if (!line.startsWith('|')) continue;
      if (line.contains('---')) continue;
      final cells = line
          .split('|')
          .map((c) => c.trim())
          .where((c) => c.isNotEmpty)
          .toList();
      if (cells.length >= 3) {
        entries.add(RevisionEntry(version: cells[0], date: cells[1], note: cells[2]));
      }
    }
    return entries;
  }

  List<SourceEntry> _parseSources(String section) {
    final sources = <SourceEntry>[];
    final blocks = section.split(RegExp(r'^### ', multiLine: true));
    for (final block in blocks) {
      if (block.trim().isEmpty) continue;
      final lines = block.split('\n');
      final heading = lines.first.trim();
      final title = heading.startsWith('Source') && heading.contains(':')
          ? heading.substring(heading.indexOf(':') + 1).trim()
          : heading;

      final fields = _parseFields(block);
      sources.add(SourceEntry(
        title: title,
        author: fields['Author'] ?? '',
        url: _nullableUrl(fields['URL']),
        license: fields['License'] ?? '',
        retrievalDate: fields['Retrieval date'],
        availability: fields['Availability'] ?? 'original',
        deprecated: (fields['Deprecated'] ?? 'no').toLowerCase() == 'yes',
        editorNotes: fields['Editor notes'],
        referenceDescription: fields['Reference description'],
      ));
    }
    return sources;
  }

  String? _nullableUrl(String? raw) {
    if (raw == null || raw.isEmpty) return null;
    if (raw.startsWith('http')) return raw;
    return null;
  }

  String _parseTextSection(String section) {
    var text = section.trim();
    if (text.startsWith('---')) {
      text = text.replaceFirst(RegExp(r'^---\s*\n?'), '');
    }
    text = text.replaceAll(RegExp(r'\n---\s*$'), '').trim();
    return text;
  }

  QuizSection? _parseQuiz(String section) {
    if (section.trim().isEmpty) return null;

    final fields = _parseFields(section);
    final questions = <QuizQuestion>[];
    final blocks = section.split(RegExp(r'^### Question \d+', multiLine: true));
    for (final block in blocks) {
      if (!block.contains('**Question:**')) continue;
      final qFields = _parseFields(block);
      final answers = <String>[];
      var inAnswers = false;
      for (final line in block.split('\n')) {
        if (line.trim() == '**Answers:**') {
          inAnswers = true;
          continue;
        }
        if (inAnswers) {
          if (line.startsWith('**')) break;
          final answerMatch = RegExp(r'^-\s*(?:[A-D]\)\s*)?(.+)$').firstMatch(line.trim());
          if (answerMatch != null) {
            answers.add(answerMatch.group(1)!.trim());
          }
        }
      }

      final correctRaw = qFields['Correct'] ?? '';
      final correctIndex = _resolveCorrectIndex(correctRaw, answers);

      questions.add(QuizQuestion(
        question: qFields['Question'] ?? '',
        answers: answers,
        correctIndex: correctIndex,
        explanation: qFields['Explanation'],
        textReference: qFields['Text reference'],
      ));
    }

    if (questions.isEmpty) return null;
    return QuizSection(title: fields['Quiz title'], questions: questions);
  }

  int _resolveCorrectIndex(String correctRaw, List<String> answers) {
    final letter = correctRaw.trim().toUpperCase();
    const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
    if (letters.contains(letter)) {
      return letters.indexOf(letter);
    }
    final idx = answers.indexWhere((a) => a.toLowerCase() == correctRaw.toLowerCase());
    return idx >= 0 ? idx : 0;
  }
}
