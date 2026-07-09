#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from PIL import Image, ImageOps

TARGET_W = 200
TARGET_H = 300
JPEG_QUALITY = 80
MAX_BYTES = 40 * 1024
RESAMPLING = Image.Resampling.LANCZOS
SUPPORTED_EXTS = {'.png', '.PNG'}
RESERVED_FILES = {'README.md', 'build_cover_assets.py', 'catalog.json'}

CATEGORY_ALIASES = {
    'article': 'everyday_live',
    'biography': 'history',
    'demo': 'nature',
    'dialogue': 'languages',
    'fairy_tale': 'fairy_tales',
    'history': 'history',
    'instruction': 'survival',
    'legend': 'legends',
    'mythology': 'fantasy',
    'popular_science': 'science',
    'science_fiction': 'science_fiction',
    'short_story': 'fantasy',
    'travel': 'travel',
}
CUSTOM_COVERS = {
    'krakow_walk_flagship': 'travel/cover_02',
}
DEFAULT_FAMILY = 'nature'


@dataclass
class CoverStat:
    family_id: str
    filename: str
    bytes_size: int


def snake_case(name: str) -> str:
    replacements = str.maketrans({
        'ł': 'l', 'Ł': 'L', 'ś': 's', 'Ś': 'S', 'ż': 'z', 'Ż': 'Z',
        'ź': 'z', 'Ź': 'Z', 'ć': 'c', 'Ć': 'C', 'ń': 'n', 'Ń': 'N',
        'ą': 'a', 'Ą': 'A', 'ę': 'e', 'Ę': 'E', 'ó': 'o', 'Ó': 'O',
    })
    name = name.translate(replacements)
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    normalized = unicodedata.normalize('NFKD', name)
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    ascii_name = re.sub(r'[^A-Za-z0-9]+', '_', ascii_name).strip('_').lower()
    return ascii_name


def display_name(category_id: str) -> str:
    return ' '.join(part.capitalize() for part in category_id.split('_'))


def average_border_color(image: Image.Image) -> tuple[int, int, int]:
    rgb = image.convert('RGB')
    w, h = rgb.size
    samples = [
        rgb.getpixel((0, 0)),
        rgb.getpixel((w - 1, 0)),
        rgb.getpixel((0, h - 1)),
        rgb.getpixel((w - 1, h - 1)),
        rgb.getpixel((w // 2, 0)),
        rgb.getpixel((w // 2, h - 1)),
        rgb.getpixel((0, h // 2)),
        rgb.getpixel((w - 1, h // 2)),
    ]
    return tuple(int(sum(px[i] for px in samples) / len(samples)) for i in range(3))


def fit_cover(source_path: Path) -> Image.Image:
    with Image.open(source_path) as img:
        img = ImageOps.exif_transpose(img)
        bg = average_border_color(img)
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA') if 'A' in img.getbands() else img.convert('RGB')
        if img.mode == 'RGBA':
            background = Image.new('RGBA', img.size, bg + (255,))
            background.alpha_composite(img)
            img = background.convert('RGB')
        else:
            img = img.convert('RGB')

        fitted = ImageOps.contain(img, (TARGET_W, TARGET_H), method=RESAMPLING)
        canvas = Image.new('RGB', (TARGET_W, TARGET_H), bg)
        x = (TARGET_W - fitted.width) // 2
        y = (TARGET_H - fitted.height) // 2
        canvas.paste(fitted, (x, y))
        return canvas


def write_progressive_jpeg(image: Image.Image, destination: Path) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(
        destination,
        format='JPEG',
        quality=JPEG_QUALITY,
        optimize=True,
        progressive=True,
        subsampling=2,
    )
    return destination.stat().st_size


def repo_size_bytes(root: Path) -> int:
    total = 0
    for path in root.rglob('*'):
        if path.is_file():
            total += path.stat().st_size
    return total


def validate_output(covers_root: Path, discovered: dict[str, list[Path]]) -> None:
    pngs = list(covers_root.rglob('*.png'))
    if pngs:
        raise SystemExit(f'PNG files entered repository: {[str(p) for p in pngs]}')

    for category_id in discovered:
        category_dir = covers_root / category_id
        files = sorted(category_dir.glob('cover-*.jpg'))
        if len(files) != 5:
            raise SystemExit(f'{category_id}: expected 5 covers, found {len(files)}')
        expected = [f'cover-{i:02d}.jpg' for i in range(1, 6)]
        actual = [f.name for f in files]
        if actual != expected:
            raise SystemExit(f'{category_id}: filenames not consecutive: {actual}')
        for path in files:
            with Image.open(path) as img:
                if img.size != (TARGET_W, TARGET_H):
                    raise SystemExit(f'{path}: unexpected size {img.size}')
                if img.format != 'JPEG':
                    raise SystemExit(f'{path}: not a JPEG')
            if path.stat().st_size > MAX_BYTES:
                raise SystemExit(f'{path}: exceeds {MAX_BYTES} bytes')


def build_catalog(discovered: dict[str, list[Path]]) -> dict:
    families: dict[str, dict] = {}

    def family_entry(family_id: str, source_family: str, is_default: bool) -> dict:
        return {
            'id': family_id,
            'displayName': display_name(family_id),
            'title': display_name(family_id),
            'variantsCount': 5,
            'format': 'jpg',
            'width': TARGET_W,
            'height': TARGET_H,
            'quality': JPEG_QUALITY,
            'default': is_default,
            'sourceFamily': source_family,
            'variants': [
                {
                    'variantId': f'cover_{i:02d}',
                    'directory': f'covers/{source_family}',
                    'thumbnailPath': f'covers/{source_family}/cover-{i:02d}.jpg',
                    'sourcePath': f'covers/{source_family}/cover-{i:02d}.jpg',
                }
                for i in range(1, 6)
            ],
        }

    for family_id in sorted(discovered):
        families[family_id] = family_entry(family_id, family_id, family_id == DEFAULT_FAMILY)

    for alias_id, source_family in CATEGORY_ALIASES.items():
        if source_family in discovered and alias_id not in families:
            families[alias_id] = family_entry(alias_id, source_family, alias_id == DEFAULT_FAMILY)

    return {
        'version': '1',
        'defaultFamily': DEFAULT_FAMILY,
        'families': families,
        'customCovers': CUSTOM_COVERS,
    }


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: build_cover_assets.py <master_png_root> [covers_root]')

    master_root = Path(sys.argv[1]).expanduser().resolve()
    covers_root = Path(sys.argv[2]).expanduser().resolve() if len(sys.argv) > 2 else Path(__file__).resolve().parent
    if not master_root.exists():
        raise SystemExit(f'Master directory not found: {master_root}')

    before_size = repo_size_bytes(covers_root)

    discovered: dict[str, list[Path]] = {}
    master_total = 0
    for category_dir in sorted(p for p in master_root.iterdir() if p.is_dir()):
        category_id = snake_case(category_dir.name)
        pngs = sorted(p for p in category_dir.iterdir() if p.suffix in SUPPORTED_EXTS)
        if len(pngs) != 5:
            raise SystemExit(f'{category_dir.name}: expected exactly 5 PNG masters, found {len(pngs)}')
        discovered[category_id] = pngs
        master_total += sum(p.stat().st_size for p in pngs)

    for path in covers_root.iterdir():
        if path.name in RESERVED_FILES:
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    stats: list[CoverStat] = []
    for category_id, pngs in discovered.items():
        out_dir = covers_root / category_id
        out_dir.mkdir(parents=True, exist_ok=True)
        for index, png_path in enumerate(pngs, start=1):
            out_name = f'cover-{index:02d}.jpg'
            out_path = out_dir / out_name
            image = fit_cover(png_path)
            size_bytes = write_progressive_jpeg(image, out_path)
            stats.append(CoverStat(category_id, out_name, size_bytes))

    catalog = build_catalog(discovered)
    (covers_root / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    validate_output(covers_root, discovered)

    after_size = repo_size_bytes(covers_root)
    avg_size = int(mean(s.bytes_size for s in stats)) if stats else 0
    largest = max(stats, key=lambda s: s.bytes_size)
    smallest = min(stats, key=lambda s: s.bytes_size)
    ratio = (master_total / after_size) if after_size else 0.0

    report = {
        'categories': len(discovered),
        'covers': len(stats),
        'averageJpgSizeBytes': avg_size,
        'largestCover': {'path': f'{largest.family_id}/{largest.filename}', 'bytes': largest.bytes_size},
        'smallestCover': {'path': f'{smallest.family_id}/{smallest.filename}', 'bytes': smallest.bytes_size},
        'coversDirectorySizeBeforeBytes': before_size,
        'coversDirectorySizeAfterBytes': after_size,
        'masterPngTotalBytes': master_total,
        'compressionRatioVsMasters': round(ratio, 2),
        'estimatedDownloadSavingsBytes': master_total - after_size,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
