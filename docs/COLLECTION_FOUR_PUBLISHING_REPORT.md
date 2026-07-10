# Collection Four — Publishing Report

**Date:** 2026-07-10  
**Phase:** 68  
**Manuscript:** `CollectionFour.md` (source of truth)  
**Pipeline:** `import_collection_four.py` → `compile_pack` → `build_manifest` → `validate_pack` → `bundle_content_assets`

---

## Summary

| Metric | Value |
|--------|-------|
| Books processed | 16 |
| Books passed validation | 16 |
| Books requiring manual editorial review | 7 |
| Estimated average reading time | 8.6 minutes |
| Total collection reading time | ~137 minutes |
| Average difficulty (1–8 scale) | 4.8 |
| Quiz questions per book | 5 (80 total) |
| Metadata completeness | 100% required fields |
| Official library size after publish | 42 packs |

---

## Books Published

| # | Title | Slug | Reading time | Difficulty | Cover family |
|---|-------|------|--------------|------------|--------------|
| 1 | Dostrojony dom | dostrojony-dom | 8 min | 4 | everyday_live |
| 2 | Gruby dzienniczek | gruby-dzienniczek | 7 min | 4 | psychology |
| 3 | Głosy z ziemi | glosy-z-ziemi | 13 min | 7 | history |
| 4 | Kamień pamięci | kamien-pamieci | 8 min | 6 | history |
| 5 | Cel na ten rok to... nic | cel-na-ten-rok-to-nic | 8 min | 4 | everyday_live |
| 6 | Dylemat szatniarza | dylemat-szatniarza | 8 min | 6 | article |
| 7 | Brudne pieniądze, czysta nauka | brudne-pieniadze-czysta-nauka | 9 min | 6 | science |
| 8 | Susza | susza | 9 min | 5 | nature |
| 9 | Kubek | kubek | 9 min | 4 | psychology |
| 10 | Wyraz, którego nie ma | wyraz-ktorego-nie-ma | 8 min | 3 | languages |
| 11 | Oczy, które nie widzą | oczy-ktore-nie-widza | 11 min | 5 | psychology |
| 12 | Worek z piaskiem | worek-z-piaskiem | 9 min | 5 | legends |
| 13 | Domek | domek | 8 min | 4 | everyday_live |
| 14 | Przerwa | przerwa | 7 min | 3 | psychology |
| 15 | Kamera na ulicy | kamera-na-ulicy | 8 min | 7 | law |
| 16 | Czarna skrzynka | czarna-skrzynka | 7 min | 4 | psychology |

---

## Validation

All pipeline steps completed without errors:

- `compile_pack` — 16/16 packs compiled
- `build_manifest` — manifest regenerated (42 official packs)
- `validate_pack` — all checks passed (schema, cover families, manifest drift)
- `bundle_content_assets` — app bundle updated (42 lessons)

---

## Metadata Completeness

Each pack includes:

- Pack ID (`polish_*`), version, title, subtitle, blurb
- Genres, cover family, series (Collection Four), audience
- Difficulty on 1–8 scale with reader stars
- Estimated reading time, publication date, writing system, profile, level
- Tags, keywords, editorial notes
- Editorial transparency (license CC0, trust classification, source video when available)
- Sources section with provenance
- Full manuscript text (unabridged)
- 5-question comprehension quiz with explanations

---

## Editorial Quality Pass — Manual Review Recommended

Issues worth human attention (text not altered unless noted):

### High priority (7 books)

1. **Dostrojony dom + Domek** — Near-duplicate decluttering plots (red dress after breakup, childhood drawing, therapeutic tidying). Consider collection positioning or future differentiation.
2. **Kamera na ulicy** — Adapted from Ana/Brian Walshe case (2023). Requires content warning; Tom/Brian name inconsistency in manuscript; graphic violence. Trust: *Adapted from real events*.
3. **Dylemat szatniarza** — Political fiction with direct allusions to Donald Tusk and contemporary Polish politics. Editorial disclaimer recommended for library context.
4. **Gruby dzienniczek** — References real public figure Miłosz Brzeziński. Trust: *Inspired by reality*.
5. **Brudne pieniądze, czysta nauka** — References Tomasz Rożek. Trust: *Inspired by reality*.
6. **Wyraz, którego nie ma / Oczy, które nie widzą** — Reference prof. Jagoda Cieszyńska; overlapping parenting/screen-time themes with *Kubek*. Title „Wyraz, którego nie ma” unexplained in text.
7. **Głosy z ziemi** — Possible surname inconsistency (Jędrzejowski vs Jędrzejewski). Verify against author intent.

### Lower priority (not blocking publish)

- **Czarna skrzynka** — Title suggests aviation; story is about control and letting go. No „black box” in text.
- **Cel na ten rok to... nic** — Title vs plot (choosing authentic goal: writing a book).
- **Przerwa** — Protagonist Patryk shares name with *Gruby dzienniczek*.
- **Susza** — Optimistic 2029 epilog may date quickly; climate statistics should carry year context in UI if surfaced.

No grammar, spelling, or pacing corrections were applied beyond preserving manuscript text as source of truth.

---

## Tooling Added

- `scripts/collection_four_catalog.json` — metadata + quizzes for all 16 stories
- `scripts/import_collection_four.py` — manuscript → `reading-pack.md` generator (re-runnable)

---

## Next Steps (awaiting review)

- Human editorial sign-off on flagged titles
- Git commit in `alephbits-content` (Collection Four packs + manifest + tooling)
- Git commit in `alephbits` (updated `content.bundle.zip`) if bundling should ship with app
- Remote library sync will deliver packs once content repo changes are published

**Not committed automatically — awaiting reviewer approval.**
