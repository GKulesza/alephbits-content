/// Optional semantic world furniture compiled into lesson.json.
class PackWorldMetadata {
  const PackWorldMetadata({
    this.objects = const [],
    this.creatures = const [],
    this.plants = const [],
    this.symbols = const [],
    this.places = const [],
  });

  final List<String> objects;
  final List<String> creatures;
  final List<String> plants;
  final List<String> symbols;
  final List<String> places;

  static final idPattern = RegExp(r'^[a-z][a-z0-9_]*$');

  bool get isEmpty =>
      objects.isEmpty &&
      creatures.isEmpty &&
      plants.isEmpty &&
      symbols.isEmpty &&
      places.isEmpty;

  Map<String, dynamic> toJson() {
    return {
      if (objects.isNotEmpty) 'objects': objects,
      if (creatures.isNotEmpty) 'creatures': creatures,
      if (plants.isNotEmpty) 'plants': plants,
      if (symbols.isNotEmpty) 'symbols': symbols,
      if (places.isNotEmpty) 'places': places,
    };
  }

  /// Parses optional World metadata from a Metadata section body.
  ///
  /// Supports compact bullets:
  /// ```
  /// **World:**
  /// - objects: flashlight, painting
  /// - places: forest
  /// ```
  ///
  /// And simple YAML-style lists:
  /// ```
  /// **World:**
  ///   objects:
  ///     - flashlight
  ///   places:
  ///     - forest
  /// ```
  ///
  /// Missing or empty World returns null. Invalid ids are dropped with a warning
  /// list — they never fail compilation.
  static PackWorldMetadata? parse(
    String metadataSection, {
    List<String>? warnings,
  }) {
    final lines = metadataSection.replaceAll('\r\n', '\n').split('\n');
    final start = _findWorldStart(lines);
    if (start == null) {
      return null;
    }

    final block = <String>[];
    for (var i = start + 1; i < lines.length; i++) {
      final line = lines[i];
      final trimmed = line.trim();
      if (trimmed.isEmpty) {
        if (block.isNotEmpty) {
          break;
        }
        continue;
      }
      if (trimmed == '---') {
        break;
      }
      if (RegExp(r'^\*\*[^*]+:\*\*').hasMatch(trimmed) &&
          !trimmed.toLowerCase().startsWith('**world')) {
        break;
      }
      if (trimmed.startsWith('```')) {
        // Skip fenced yaml markers; still collect inner lines.
        continue;
      }
      block.add(line);
    }

    if (block.isEmpty) {
      return null;
    }

    final objects = <String>[];
    final creatures = <String>[];
    final plants = <String>[];
    final symbols = <String>[];
    final places = <String>[];

    String? currentCategory;
    for (final raw in block) {
      final line = raw.trim();
      if (line.isEmpty || line == 'world:') {
        continue;
      }

      final compact = RegExp(
        r'^-\s*(objects|creatures|plants|symbols|places)\s*:\s*(.*)$',
        caseSensitive: false,
      ).firstMatch(line);
      if (compact != null) {
        currentCategory = compact.group(1)!.toLowerCase();
        _appendIds(
          category: currentCategory,
          raw: compact.group(2) ?? '',
          objects: objects,
          creatures: creatures,
          plants: plants,
          symbols: symbols,
          places: places,
          warnings: warnings,
        );
        continue;
      }

      final categoryHeader = RegExp(
        r'^(objects|creatures|plants|symbols|places)\s*:\s*(.*)$',
        caseSensitive: false,
      ).firstMatch(line);
      if (categoryHeader != null) {
        currentCategory = categoryHeader.group(1)!.toLowerCase();
        final inline = categoryHeader.group(2)?.trim() ?? '';
        if (inline.isNotEmpty && !inline.startsWith('-')) {
          _appendIds(
            category: currentCategory,
            raw: inline,
            objects: objects,
            creatures: creatures,
            plants: plants,
            symbols: symbols,
            places: places,
            warnings: warnings,
          );
        }
        continue;
      }

      final bullet = RegExp(r'^-\s+(.+)$').firstMatch(line);
      if (bullet != null && currentCategory != null) {
        _appendIds(
          category: currentCategory,
          raw: bullet.group(1)!,
          objects: objects,
          creatures: creatures,
          plants: plants,
          symbols: symbols,
          places: places,
          warnings: warnings,
        );
      }
    }

    final world = PackWorldMetadata(
      objects: _unique(objects),
      creatures: _unique(creatures),
      plants: _unique(plants),
      symbols: _unique(symbols),
      places: _unique(places),
    );
    return world.isEmpty ? null : world;
  }

  static int? _findWorldStart(List<String> lines) {
    for (var i = 0; i < lines.length; i++) {
      final trimmed = lines[i].trim();
      if (RegExp(r'^\*\*World:\*\*', caseSensitive: false).hasMatch(trimmed) ||
          RegExp(r'^World:\s*$', caseSensitive: false).hasMatch(trimmed)) {
        return i;
      }
    }
    return null;
  }

  static void _appendIds({
    required String category,
    required String raw,
    required List<String> objects,
    required List<String> creatures,
    required List<String> plants,
    required List<String> symbols,
    required List<String> places,
    List<String>? warnings,
  }) {
    final ids = raw
        .split(',')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();
    for (final id in ids) {
      if (!idPattern.hasMatch(id)) {
        warnings?.add('World element "$id" ignored — use snake_case ASCII ids.');
        continue;
      }
      switch (category) {
        case 'objects':
          objects.add(id);
        case 'creatures':
          creatures.add(id);
        case 'plants':
          plants.add(id);
        case 'symbols':
          symbols.add(id);
        case 'places':
          places.add(id);
      }
    }
  }

  static List<String> _unique(List<String> ids) {
    final seen = <String>{};
    final out = <String>[];
    for (final id in ids) {
      if (seen.add(id)) {
        out.add(id);
      }
    }
    return out;
  }
}
