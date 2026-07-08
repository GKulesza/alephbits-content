/// Canonical discovery categories for the AlephBits library catalog.
///
/// Editors add new categories here — not in manifest.json.
const canonicalCategories = <Map<String, String>>[
  {
    'id': 'travel',
    'title': 'Travel',
    'description': 'Journeys, places, and exploration.',
  },
  {
    'id': 'history',
    'title': 'History',
    'description': 'Historical narratives and context.',
  },
  {
    'id': 'popular_science',
    'title': 'Popular Science',
    'description': 'Popular science and natural world.',
  },
  {
    'id': 'fairy_tale',
    'title': 'Fairy Tale',
    'description': 'Classic and original fairy tales.',
  },
  {
    'id': 'legend',
    'title': 'Legend',
    'description': 'Folklore and legendary stories.',
  },
  {
    'id': 'article',
    'title': 'Article',
    'description': 'Short non-fiction articles.',
  },
  {
    'id': 'biography',
    'title': 'Biography',
    'description': 'Lives and memoirs.',
  },
  {
    'id': 'dialogue',
    'title': 'Dialogue',
    'description': 'Conversational texts for natural speech.',
  },
  {
    'id': 'instruction',
    'title': 'Instruction',
    'description': 'How-to and procedural texts.',
  },
  {
    'id': 'short_story',
    'title': 'Short Story',
    'description': 'Fiction in compact form.',
  },
  {
    'id': 'mythology',
    'title': 'Mythology',
    'description': 'Myths and sacred narratives.',
  },
  {
    'id': 'science_fiction',
    'title': 'Science Fiction',
    'description': 'Speculative and futuristic fiction.',
  },
];

/// Repository-wide constants used when generating manifest.json.
const repositoryVersion = '1.0.0';
const schemaVersion = '1';
const minimumAppVersion = '0.5.0';

/// Curated shelf templates — pack IDs are filled at build time.
const featuredCollectionTemplates = <Map<String, dynamic>>[
  {
    'id': 'starter_shelf',
    'title': 'Official Starter Shelf',
    'description': 'The first curated collection of AlephBits official reading packs.',
    'tiers': ['official'],
    'sort': 'title',
  },
  {
    'id': 'first_reads',
    'title': 'First Reads',
    'description': 'Best introductory texts for new readers.',
    'tiers': ['official'],
    'sort': 'difficulty',
  },
];
