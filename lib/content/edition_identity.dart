/// Content Model v2 identity helpers.
///
/// Book = permanent [bookId] (folder `books/<bookId>/`).
/// Edition = one locale of a book (`books/<bookId>/<locale>/`).
/// Edition id = `{bookId}:{locale}` and is the durable content/progress key.
library;

/// Builds a canonical edition id from [bookId] and [locale].
String editionIdFor({required String bookId, required String locale}) {
  final normalizedBook = bookId.trim();
  final normalizedLocale = primaryLocale(locale);
  if (normalizedBook.isEmpty || normalizedLocale.isEmpty) {
    throw ArgumentError('bookId and locale are required for an edition id');
  }
  return '$normalizedBook:$normalizedLocale';
}

/// Normalizes a language or content-locale code for edition identity.
///
/// BCP-47 region tags collapse (`pl-PL` → `pl`). Multi-script content folder
/// codes (`isv_cyrl`, `isv_glag`) are preserved whole so Interslavic script
/// editions do not collide with Latin `isv`.
String primaryLocale(String languageOrLocale) {
  final trimmed = languageOrLocale.trim().toLowerCase();
  if (trimmed.isEmpty) return '';
  final underscored = trimmed.replaceAll('-', '_');
  if (_preservedContentLocales.contains(underscored)) {
    return underscored;
  }
  return underscored.split('_').first;
}

const _preservedContentLocales = <String>{
  'isv_cyrl',
  'isv_glag',
};

/// Parses `{bookId}:{locale}` edition ids. Returns null when not edition-shaped.
({String bookId, String locale})? parseEditionId(String id) {
  final trimmed = id.trim();
  final colon = trimmed.indexOf(':');
  if (colon <= 0 || colon >= trimmed.length - 1) return null;
  if (trimmed.contains(':', colon + 1)) return null;
  final bookId = trimmed.substring(0, colon);
  final locale = primaryLocale(trimmed.substring(colon + 1));
  if (bookId.isEmpty || locale.isEmpty) return null;
  return (bookId: bookId, locale: locale);
}

/// True when [id] looks like `{bookId}:{locale}`.
bool isEditionId(String id) => parseEditionId(id) != null;
