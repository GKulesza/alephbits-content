import 'parser.dart';

/// Canonical reader-facing provenance extracted from Sources + vault blocks.
class EditorialProvenance {
  EditorialProvenance({
    required this.inspirationDates,
    required this.youtubeVideoIds,
  });

  final List<String> inspirationDates;
  final List<String> youtubeVideoIds;

  bool get isEmpty => inspirationDates.isEmpty && youtubeVideoIds.isEmpty;

  Map<String, dynamic> toLessonJson() {
    final map = <String, dynamic>{};
    if (inspirationDates.isNotEmpty) {
      map['inspirationDates'] = inspirationDates;
    }
    if (youtubeVideoIds.isNotEmpty) {
      map['inspiredBy'] = {'youtube': youtubeVideoIds.join(', ')};
    }
    return map;
  }

  List<Map<String, dynamic>> toProvenanceSources() {
    return youtubeVideoIds
        .map((id) => {'type': 'youtube', 'videoId': id})
        .toList();
  }
}

EditorialProvenance buildEditorialProvenance(ReadingPackDocument doc) {
  final dates = <String>{};
  final ids = <String>[];
  final seenIds = <String>{};

  void addDate(String? raw) {
    final normalized = normalizeEditorialDate(raw);
    if (normalized != null) {
      dates.add(normalized);
    }
  }

  void addYouTubeFromUrl(String? url) {
    final id = extractYouTubeVideoId(url);
    if (id != null && seenIds.add(id)) {
      ids.add(id);
    }
  }

  for (final entry in _parseVaultSourceBlocks(doc.transparency)) {
    addDate(entry.date);
    addYouTubeFromUrl(entry.url);
  }

  for (final source in doc.sources) {
    if (source.deprecated) continue;
    addDate(source.retrievalDate);
    addYouTubeFromUrl(source.url);
  }

  final sortedDates = dates.toList()..sort();
  return EditorialProvenance(
    inspirationDates: sortedDates,
    youtubeVideoIds: ids,
  );
}

class _VaultSourceEntry {
  _VaultSourceEntry({this.date, this.url});

  final String? date;
  final String? url;
}

List<_VaultSourceEntry> _parseVaultSourceBlocks(Map<String, String> transparency) {
  final entries = <_VaultSourceEntry>[];
  for (final key in ['Source block', 'Source video']) {
    final raw = transparency[key];
    if (raw == null || raw.trim().isEmpty) continue;
    if (raw == '(none)' || raw.startsWith('*(')) continue;

    final chunks = raw.split(RegExp(r'<br\s*/?>|\n', caseSensitive: false));
    for (final chunk in chunks) {
      final trimmed = chunk.trim();
      if (trimmed.isEmpty) continue;

      final arrowMatch = RegExp(
        r'^(\d{1,2}\.\d{1,2}\.\d{4}|\d{4}-\d{2}-\d{2})\s*->\s*(.+)$',
      ).firstMatch(trimmed);
      if (arrowMatch != null) {
        entries.add(
          _VaultSourceEntry(
            date: arrowMatch.group(1),
            url: arrowMatch.group(2)!.trim(),
          ),
        );
        continue;
      }

      addYouTubeUrlIfPresent(trimmed, entries);
    }
  }
  return entries;
}

void addYouTubeUrlIfPresent(String raw, List<_VaultSourceEntry> entries) {
  final urlMatch = RegExp(r'https?://[^\s<]+').firstMatch(raw);
  if (urlMatch != null) {
    entries.add(_VaultSourceEntry(url: urlMatch.group(0)));
  }
}

String? normalizeEditorialDate(String? raw) {
  if (raw == null) return null;
  final value = raw.trim();
  if (value.isEmpty) return null;

  final iso = RegExp(r'^(\d{4})-(\d{2})-(\d{2})$').firstMatch(value);
  if (iso != null) return value;

  final dotted = RegExp(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$').firstMatch(value);
  if (dotted != null) {
    final day = dotted.group(1)!.padLeft(2, '0');
    final month = dotted.group(2)!.padLeft(2, '0');
    final year = dotted.group(3)!;
    return '$year-$month-$day';
  }
  return null;
}

String? extractYouTubeVideoId(String? raw) {
  if (raw == null) return null;
  final url = raw.trim();
  if (url.isEmpty) return null;

  final patterns = [
    RegExp(r'[?&]v=([A-Za-z0-9_-]{11})'),
    RegExp(r'youtu\.be/([A-Za-z0-9_-]{11})'),
    RegExp(r'youtube\.com/embed/([A-Za-z0-9_-]{11})'),
    RegExp(r'youtube\.com/shorts/([A-Za-z0-9_-]{11})'),
  ];
  for (final pattern in patterns) {
    final match = pattern.firstMatch(url);
    if (match != null) return match.group(1);
  }

  if (RegExp(r'^[A-Za-z0-9_-]{11}$').hasMatch(url)) {
    return url;
  }
  return null;
}
