#!/usr/bin/env dart
// ignore_for_file: avoid_print

import 'dart:io';

import 'package:alephbits_content/reading_pack/compile_runner.dart';
import 'package:path/path.dart' as p;

/// Compiles reading-pack.md into pack artifacts.
///
/// Usage:
///   dart run tools/compile_pack.dart path/to/pack
///   dart run tools/compile_pack.dart --check path/to/pack
///   dart run tools/compile_pack.dart --overwrite path/to/pack
///   dart run tools/compile_pack.dart --dry-run path/to/pack
///   dart run tools/compile_pack.dart --all [--check|--overwrite|--dry-run]
void main(List<String> args) {
  final options = _parseArgs(args);
  if (options.showHelp) {
    _printHelp();
    exit(0);
  }

  final repoRoot = Directory.current.path;
  final packPaths = options.all
      ? discoverPackDirectoriesWithReadingPack(repoRoot)
      : options.packPaths.map((path) => _resolvePath(repoRoot, path)).toList();

  if (packPaths.isEmpty) {
    stderr.writeln('No pack directories found.');
    exit(1);
  }

  var exitCode = 0;
  for (final packPath in packPaths) {
    final relative = p.relative(packPath, from: repoRoot);
    if (!File(p.join(packPath, 'reading-pack.md')).existsSync()) {
      stderr.writeln('$relative: missing reading-pack.md');
      exitCode = 1;
      continue;
    }

    final result = compileAndCheckDirectory(packPath);
    if (result.parseError != null) {
      stderr.writeln('$relative: parse error — ${result.parseError}');
      exitCode = 1;
      continue;
    }

    if (options.check) {
      if (result.hasDrift) {
        exitCode = 3;
        stderr.writeln('$relative: compile drift detected');
        for (final item in result.drift) {
          stderr.writeln('  • ${item.file}: ${item.message}');
        }
      } else {
        print('✓ $relative matches reading-pack.md');
      }
      continue;
    }

    if (options.dryRun) {
      print('Would compile $relative (${result.drift.length} drift item(s) vs committed)');
      for (final item in result.drift) {
        print('  • ${item.file}: ${item.message}');
      }
      continue;
    }

    if (options.overwrite || result.hasDrift) {
      writeArtifacts(packPath, result.artifacts!);
      print('✓ Compiled $relative');
    } else {
      print('✓ $relative already up to date (use --overwrite to force)');
    }
  }

  exit(exitCode);
}

class _Options {
  _Options({
    required this.showHelp,
    required this.check,
    required this.overwrite,
    required this.dryRun,
    required this.all,
    required this.packPaths,
  });

  final bool showHelp;
  final bool check;
  final bool overwrite;
  final bool dryRun;
  final bool all;
  final List<String> packPaths;
}

_Options _parseArgs(List<String> args) {
  var check = false;
  var overwrite = false;
  var dryRun = false;
  var all = false;
  final packPaths = <String>[];

  for (final arg in args) {
    switch (arg) {
      case '--help':
      case '-h':
        return _Options(
          showHelp: true,
          check: false,
          overwrite: false,
          dryRun: false,
          all: false,
          packPaths: const [],
        );
      case '--check':
        check = true;
      case '--overwrite':
        overwrite = true;
      case '--dry-run':
        dryRun = true;
      case '--all':
        all = true;
      default:
        if (arg.startsWith('-')) {
          stderr.writeln('Unknown option: $arg');
          exit(1);
        }
        packPaths.add(arg);
    }
  }

  if (!all && packPaths.isEmpty) {
    stderr.writeln('Missing pack path. Use --all or provide path/to/pack.');
    exit(1);
  }

  return _Options(
    showHelp: false,
    check: check,
    overwrite: overwrite,
    dryRun: dryRun,
    all: all,
    packPaths: packPaths,
  );
}

String _resolvePath(String repoRoot, String input) {
  if (p.isAbsolute(input)) return p.normalize(input);
  return p.normalize(p.join(repoRoot, input));
}

void _printHelp() {
  print('''
compile_pack — deterministic reading-pack.md compiler

Usage:
  dart run tools/compile_pack.dart path/to/pack
  dart run tools/compile_pack.dart --check path/to/pack
  dart run tools/compile_pack.dart --overwrite path/to/pack
  dart run tools/compile_pack.dart --dry-run path/to/pack
  dart run tools/compile_pack.dart --all [--check|--overwrite|--dry-run]

Exit codes:
  0 success
  1 parse or usage error
  3 --check drift detected
''');
}
