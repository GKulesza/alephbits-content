/// Canonical trust classification identifiers for Reading Packs.
///
/// Display labels are resolved in the app — never inferred from tags.
abstract final class TrustCatalog {
  static const fiction = 'fiction';
  static const inspiredByReality = 'inspired_by_reality';
  static const adaptedFromRealEvents = 'adapted_from_real_events';
  static const popularScience = 'popular_science';
  static const instruction = 'instruction';
  static const demo = 'demo';

  static const all = [
    fiction,
    inspiredByReality,
    adaptedFromRealEvents,
    popularScience,
    instruction,
    demo,
  ];

  /// Maps reading-pack.md **Trust classification:** display text to canonical id.
  static const displayToId = <String, String>{
    'Fiction': fiction,
    'fiction': fiction,
    'Inspired by reality': inspiredByReality,
    'inspired_by_real_events': inspiredByReality,
    'Adapted from real events': adaptedFromRealEvents,
    'Popular science': popularScience,
    'science': popularScience,
    'Instruction': instruction,
    'guide': instruction,
    'Manual / Reference': instruction,
    'Demo': demo,
    'biography': inspiredByReality,
    'history': inspiredByReality,
    'historical_fiction': fiction,
    'technology': popularScience,
    'opinion': inspiredByReality,
  };

  static String? canonicalId(String? displayOrId) {
    if (displayOrId == null || displayOrId.trim().isEmpty) return null;
    final trimmed = displayOrId.trim();
    if (all.contains(trimmed)) return trimmed;
    return displayToId[trimmed];
  }
}
