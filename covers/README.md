# AlephBits Cover Assets

This directory contains **production cover assets only**.

Master PNG artwork lives outside the repository and must not be committed here. The repository stores lightweight JPEG derivatives plus a resolver catalog that remains compatible with the current app cover system.

## Layout

```text
covers/
├── README.md
├── build_cover_assets.py
├── catalog.json
├── biology/
│   ├── cover-01.jpg
│   ├── cover-02.jpg
│   ├── cover-03.jpg
│   ├── cover-04.jpg
│   └── cover-05.jpg
├── history/
│   └── cover-01.jpg ... cover-05.jpg
└── ...
```

## Processing rules

- Source format: founder-supplied PNG masters outside the repo
- Output format: progressive JPEG
- Output size: `200x300`
- JPEG quality: `80`
- Metadata: stripped on export
- Naming: `cover-01.jpg` to `cover-05.jpg`

`200x300` was kept for production because it stays extremely light while remaining acceptable for current shelf-card usage. This batch averaged about 12.6 KB per file, well under the founder's maximum size constraint.

## Regeneration

Create a Python virtualenv with Pillow installed, then run:

```bash
python3 -m venv .venv-cover
. .venv-cover/bin/activate
python -m pip install pillow
python covers/build_cover_assets.py "/absolute/path/to/AlephBitsImgBooksCovers" "/absolute/path/to/alephbits-content/covers"
```

The script will:

1. discover category folders automatically
2. require exactly 5 PNG masters per category
3. resize and pad to `200x300` without cropping
4. write optimized JPEGs
5. regenerate `catalog.json`
6. validate dimensions, filenames, and file formats
7. print size statistics

## Resolver compatibility

The current app still expects the legacy `families` contract in `covers/catalog.json`.

This pipeline preserves that contract while adding lightweight JPEG asset paths. The catalog also includes alias families for current repository categories such as `popular_science`, `science_fiction`, `legend`, `instruction`, and `short_story`, so the existing resolver continues to work without app changes.
