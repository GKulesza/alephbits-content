#!/usr/bin/env dart
// ignore_for_file: avoid_print

import 'dart:io';

import 'package:alephbits_content/manifest/builder.dart';
import 'package:alephbits_content/manifest/manifest_runner.dart';
import 'package:path/path.dart' as p;

/// Regenerates manifest.json from pack directories on disk.
///
/// Usage:
///   dart run tools/build_manifest.dart
///   dart run tools/build_manifest.dart --check
///   dart run tools/build_manifest.dart --overwrite
///   dart run tools/build_manifest.dart --dry-run
void main(List<String> args) {
  final options = _parseArgs(args);
  if (options.showHelp) {
    _printHelp();
    exit(0);
  }

  final repoRoot = Directory.current.path;
  final manifestPath = p.join(repoRoot, 'manifest.json');

  try {
    final builder = ManifestBuilder();
    final generated = builder.buildJson(repoRoot);

    if (options.check) {
      if (!File(manifestPath).existsSync()) {
        stderr.writeln('manifest.json is missing');
        exit(3);
      }
      final committed = File(manifestPath).readAsStringSync();
      if (!manifestSemanticallyEqual(committed, generated)) {
        stderr.writeln('manifest drift detected — run build_manifest --overwrite');
        exit(3);
      }
      print('✓ manifest.json matches build_manifest output');
      exit(0);
    }

    if (options.dryRun) {
      print('Would regenerate manifest.json');
      final drift = checkManifestDrift(repoRoot);
      if (drift != null) {
        print('  • ${drift.message}');
      } else {
        print('  • already up to date');
      }
      exit(0);
    }

    if (options.overwrite || checkManifestDrift(repoRoot) != null) {
      File(manifestPath).writeAsStringSync(generated);
      print('✓ Regenerated manifest.json');
    } else {
      print('✓ manifest.json already up to date (use --overwrite to force)');
    }
    exit(0);
  } on ManifestBuildException catch (e) {
    stderr.writeln('build_manifest failed: $e');
    exit(1);
  }
}

class _Options {
  _Options({
    required this.showHelp,
    required this.check,
    required this.overwrite,
    required this.dryRun,
  });

  final bool showHelp;
  final bool check;
  final bool overwrite;
  final bool dryRun;
}

_Options _parseArgs(List<String> args) {
  var check = false;
  var overwrite = false;
  var dryRun = false;

  for (final arg in args) {
    switch (arg) {
      case '--help':
      case '-h':
        return _Options(showHelp: true, check: false, overwrite: false, dryRun: false);
      case '--check':
        check = true;
      case '--overwrite':
        overwrite = true;
      case '--dry-run':
        dryRun = true;
      default:
        if (arg.startsWith('-')) {
          stderr.writeln('Unknown option: $arg');
          exit(1);
        }
    }
  }

  return _Options(showHelp: false, check: check, overwrite: overwrite, dryRun: dryRun);
}

void _printHelp() {
  print('''
build_manifest — regenerate manifest.json from pack directories

Usage:
  dart run tools/build_manifest.dart
  dart run tools/build_manifest.dart --check
  dart run tools/build_manifest.dart --overwrite
  dart run tools/build_manifest.dart --dry-run

Exit codes:
  0 success
  1 build error
  3 --check drift detected
''');
}
