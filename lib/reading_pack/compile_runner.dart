import 'dart:io';

import 'package:path/path.dart' as p;

import 'compiler.dart';
import 'json_writer.dart';
import 'parser.dart';

class CompileDrift {
  CompileDrift(this.file, this.message);
  final String file;
  final String message;
}

class CompileResult {
  CompileResult({
    required this.artifacts,
    required this.drift,
    required this.parseError,
  });

  final CompiledArtifacts? artifacts;
  final List<CompileDrift> drift;
  final String? parseError;

  bool get success => parseError == null;
  bool get hasDrift => drift.isNotEmpty;
}

CompiledArtifacts compilePackDirectory(String packDirPath) {
  final mdFile = File(p.join(packDirPath, 'reading-pack.md'));
  if (!mdFile.existsSync()) {
    throw ReadingPackParseException('Missing reading-pack.md in $packDirPath');
  }
  final markdown = mdFile.readAsStringSync();
  final doc = ReadingPackParser().parse(markdown, packDirPath: packDirPath);
  return ReadingPackCompiler().compile(doc, packDirPath: packDirPath);
}

CompileResult compileAndCheckDirectory(String packDirPath) {
  try {
    final compiled = compilePackDirectory(packDirPath);
    final drift = checkDrift(packDirPath, compiled);
    return CompileResult(artifacts: compiled, drift: drift, parseError: null);
  } on ReadingPackParseException catch (e) {
    return CompileResult(artifacts: null, drift: const [], parseError: e.message);
  }
}

List<CompileDrift> checkDrift(String packDirPath, CompiledArtifacts compiled) {
  final drift = <CompileDrift>[];
  for (final entry in compiled.asFileMap().entries) {
    final file = File(p.join(packDirPath, entry.key));
    if (!file.existsSync()) {
      drift.add(CompileDrift(entry.key, 'missing committed file'));
      continue;
    }
    final existing = file.readAsStringSync();
    final generated = entry.value;
    if (entry.key.endsWith('.json')) {
      if (!jsonSemanticallyEqual(existing, generated)) {
        drift.add(CompileDrift(entry.key, 'JSON differs from compiled output'));
      }
    } else if (!textSemanticallyEqual(existing, generated)) {
      drift.add(CompileDrift(entry.key, 'content differs from compiled output'));
    }
  }
  return drift;
}

void writeArtifacts(String packDirPath, CompiledArtifacts compiled) {
  for (final entry in compiled.asFileMap().entries) {
    File(p.join(packDirPath, entry.key)).writeAsStringSync(entry.value);
  }
}

List<String> discoverPackDirectoriesWithReadingPack(String repoRoot) {
  final results = <String>[];
  for (final tier in ['official', 'community', 'experimental']) {
    final tierDir = Directory(p.join(repoRoot, tier));
    if (!tierDir.existsSync()) continue;
    for (final entity in tierDir.listSync(recursive: true)) {
      if (entity is! Directory) continue;
      final md = File(p.join(entity.path, 'reading-pack.md'));
      if (md.existsSync()) {
        results.add(entity.path);
      }
    }
  }
  results.sort();
  return results;
}
