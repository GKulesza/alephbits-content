/// Content Model v2 audience vocabulary (mirrors app [PackAudience]).
abstract final class AudienceVocabulary {
  static const children = 'children';
  static const familyReading = 'family_reading';
  static const teens = 'teens';
  static const adults = 'adults';
  static const everyone = 'everyone';

  static const canonical = {
    children,
    familyReading,
    teens,
    adults,
    everyone,
  };

  static const legacyAliases = {
    'child',
    'family',
    'children_8_12',
    'teen',
    'adult',
  };

  static const accepted = {...canonical, ...legacyAliases};

  static String? canonicalize(String? raw) {
    final id = raw?.trim();
    if (id == null || id.isEmpty) return null;
    return switch (id) {
      children || 'child' || 'children_8_12' => children,
      familyReading || 'family' => familyReading,
      teens || 'teen' => teens,
      adults || 'adult' => adults,
      everyone => everyone,
      _ => null,
    };
  }

  static bool isLegacy(String? raw) {
    final id = raw?.trim();
    if (id == null || id.isEmpty) return false;
    return !canonical.contains(id) && accepted.contains(id);
  }
}
