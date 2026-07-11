#!/usr/bin/env dart
// ignore_for_file: avoid_print

import 'dart:convert';
import 'dart:io';

import 'package:alephbits_content/reading_pack/compile_runner.dart';
import 'package:alephbits_content/reading_pack/parser.dart';

/// Emits normalized quiz JSON from reading-pack.md for pipeline verification.
///
/// Usage:
///   dart run tools/phase80a_quiz_extract.dart path/to/pack
void main(List<String> args) {
  if (args.isEmpty) {
    stderr.writeln('Usage: dart run tools/phase80a_quiz_extract.dart <pack_dir>');
    exit(1);
  }

  final packDir = Directory(args.first);
  if (!File('${packDir.path}/reading-pack.md').existsSync()) {
    stderr.writeln('Missing reading-pack.md in ${packDir.path}');
    exit(1);
  }

  try {
    final compiled = compilePackDirectory(packDir.path);
    final lesson = jsonDecode(compiled.lessonJson) as Map<String, dynamic>;
    final quiz = lesson['quiz'];
    if (quiz is! Map<String, dynamic>) {
      stderr.writeln('Compiled lesson has no quiz object');
      exit(1);
    }
    stdout.writeln(jsonEncode(_normalizeQuiz(quiz)));
  } on ReadingPackParseException catch (e) {
    stderr.writeln('Parse error: $e');
    exit(1);
  }
}

Map<String, dynamic> _normalizeQuiz(Map<String, dynamic> quiz) {
  final questions = (quiz['questions'] as List?)?.map((raw) {
    if (raw is! Map<String, dynamic>) {
      return <String, dynamic>{};
    }
    return {
      'question': raw['question'],
      'answers': raw['answers'],
      'correctIndex': raw['correctIndex'],
    };
  }).toList();

  return {
    'title': quiz['title'],
    'questions': questions,
  };
}
