import 'dart:convert';

/// Encodes [value] as pretty-printed JSON with 2-space indent and stable key order.
String encodeJsonPretty(Object? value) {
  return '${_encode(value, 0)}\n';
}

String _encode(Object? value, int indent) {
  if (value == null) return 'null';
  if (value is bool) return value ? 'true' : 'false';
  if (value is num) {
    if (value is int) return value.toString();
    final s = value.toString();
    return s.contains('.') ? s : '$s.0';
  }
  if (value is String) return jsonEncode(value);
  if (value is List) {
    if (value.isEmpty) return '[]';
    final pad = ' ' * indent;
    final inner = ' ' * (indent + 2);
    final items = value.map((e) => '$inner${_encode(e, indent + 2)}').join(',\n');
    return '[\n$items\n$pad]';
  }
  if (value is Map<String, dynamic>) {
    if (value.isEmpty) return '{}';
    final pad = ' ' * indent;
    final inner = ' ' * (indent + 2);
    final entries = value.entries.map((e) {
      return '$inner${jsonEncode(e.key)}: ${_encode(e.value, indent + 2)}';
    }).join(',\n');
    return '{\n$entries\n$pad}';
  }
  return jsonEncode(value);
}

/// Normalizes JSON for semantic comparison.
Object? normalizeJson(dynamic value) {
  if (value is Map) {
    final map = <String, dynamic>{};
    for (final entry in value.entries) {
      map[entry.key.toString()] = normalizeJson(entry.value);
    }
    return map;
  }
  if (value is List) {
    return value.map(normalizeJson).toList();
  }
  return value;
}

bool jsonSemanticallyEqual(String a, String b) {
  final decodedA = jsonDecode(a);
  final decodedB = jsonDecode(b);
  return jsonEncode(normalizeJson(decodedA)) == jsonEncode(normalizeJson(decodedB));
}

bool textSemanticallyEqual(String a, String b) {
  return a.replaceAll('\r\n', '\n').trim() == b.replaceAll('\r\n', '\n').trim();
}
