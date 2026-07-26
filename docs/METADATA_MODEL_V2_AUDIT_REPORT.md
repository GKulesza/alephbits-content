# Content Model v2 — Editorial Metadata Audit Report (Part 4)

**Date:** 2026-07-27  
**Scope:** Audience, Category, Difficulty across 126 books  
**Policy:** No silent reclassification. Content files were not modified.

---

## Current live distribution

| Stored `audience` | Count | UI filter after Part 4 |
|-------------------|------:|------------------------|
| `adult` | 91 | Adults |
| `family` | 19 | **Family Reading** (was incorrectly folded into Children) |
| `children_8_12` | 14 | Children |
| `teen` | 2 | Teens |
| `child` | 0 | — |
| `everyone` | 0 | — |

Difficulty (1–8): 2×14, 3×27, 4×29, 5×22, 6×26, 7×7, 8×1. No difficulty 1.

Independence check (good): children/family packs stay at difficulty 2–4; adult packs span 2–8. No children/family pack at difficulty ≥ 5.

---

## Incorrect / inconsistent audience values

No freeform or unknown audience strings in compiled `lesson.json`.

Problems are **vocabulary / product modeling**, not corrupt data:

1. **Family Reading collapsed into Children**  
   Nineteen `family` packs were filtered as Children. That contradicts the editorial definition of Family Reading as a distinct shared-reading audience.

2. **Two youth ids (`child` unused, `children_8_12` live)**  
   Youth fiction uses age-banded id `children_8_12` instead of intended-audience id `children`.

3. **Singular legacy ids (`adult`, `teen`, `family`)**  
   Not aligned with the long-term plural / descriptive vocabulary (`adults`, `teens`, `family_reading`).

4. **No `everyone` yet**  
   No pack currently claims cross-age “Everyone”. Some Family Reading or mild adult/demo titles may deserve review later — not auto-changed.

---

## Places where two concepts are mixed

| Issue | Evidence | Recommendation |
|-------|----------|----------------|
| `family` used as Genres topic | `yj5ci6vg` *Opowieści z poprzedniego życia* — Genres includes `family`, audience=`adult` | Remove `family` from Genres; keep psychology / short_story. Audience stays adult until an editor decides otherwise. |
| Fairy tale ≈ children proxy | All 10 `fairy_tale` packs are `children_8_12` | Acceptable correlation; do **not** encode as a rule. Adults may write fairy tales for adults later. |
| Starter / roadmap docs list “target audience” inside category briefs | CONTENT_ROADMAP, COLLECTION docs | Keep category briefs free of Audience when rewriting. |
| Difficulty tables imply “typical audience” by band | Authoring format difficulty mapping | Keep heuristics editorial-only; validators must not couple axes. |
| Review chips use parallel age groups (`family_read_aloud`, `child_6_8`, …) | `EditorialAgeGroup` | Keep review UX separate for now; document the dual vocabulary. |

---

## Proposed metadata changes (editorial — not applied)

### A. Normalize audience ids (recommended bulk rename)

| From | To | Packs | Notes |
|------|----|------:|-------|
| `adult` | `adults` | 91 | Mechanical rename |
| `family` | `family_reading` | 19 | Mechanical rename; keeps Family Reading distinct |
| `children_8_12` | `children` | 14 | Mechanical rename; drops age band from id |
| `teen` | `teens` | 2 | Mechanical rename |

**Do not auto-map any pack to `everyone`.** That requires editorial judgment.

### B. Category cleanup (one pack)

| Book | Change |
|------|--------|
| `yj5ci6vg` *Opowieści z poprzedniego życia* | Remove topic `family` from Genres / manifest categories |

### C. Family Reading membership review (optional, human)

These are currently `family`. Most fit Family Reading. Flag for a calm second look if any are really Children-only or Adults-only:

- Instruction / dialogue demos: *Jak ugotować herbatę*, *Rozmowa z lekarzem*
- Popular science: *Dlaczego niebo jest niebieskie?*, *Pierwszy lot na Marsa*
- Parenting / psychology shorts: *Kij i marchewka*, *Przedszkole bez ścian*, *Etykieta*, …

No change proposed without founder read-through.

### D. Teen membership review (optional)

| Book | Current | Note |
|------|---------|------|
| *Bogini i liczby* | teen, d=6 | Biography — confirm Teens vs Adults |
| *Maria Skłodowska-Curie* | teen, d=4 | Biography — confirm Teens vs Adults / Everyone |

---

## Normalization decisions (implemented in tooling/docs)

1. Canonical Audience vocabulary: `children`, `family_reading`, `teens`, `adults`, `everyone`.
2. Legacy aliases remain **accepted** by validators so existing content continues to validate.
3. Library filters: Children, Family Reading, Teens, Adults, Everyone, Unknown.
4. `children_8_12` maps to **Children** (not a separate “Young Readers” shelf).
5. `family` maps to **Family Reading** (no longer Children).
6. Difficulty enforced as **1–8** in app + content validators; independent of Audience.
7. Category must not use audience words as topics (`family` remains blocked).

---

## Unresolved editorial questions

1. Should any current Family Reading packs become Children or Adults after a founder pass?
2. Should either Teen biography move to Adults or Everyone?
3. When should `everyone` be used vs Family Reading? (Proposed: Everyone = no preferred age; Family Reading = deliberately shared child–adult experience.)
4. Should review-mode age chips (`EditorialAgeGroup`) converge on the same vocabulary?
5. Timing of the bulk rename in content (`adult` → `adults`, …) — recommend a dedicated editorial PR after this model lands.

---

## Validation behavior after Part 4

| Check | Behavior |
|-------|----------|
| Missing audience | Error (content CI) |
| Unknown audience id | Error (content CI) / Warning (app) |
| Legacy alias | Accepted (content CI); Warning prefer canonical (app) |
| Difficulty outside 1–8 | Error |
| Audience vs Category coupling | Not enforced (axes stay independent) |
| Audience vs Difficulty coupling | Not enforced |

---

## Files touched (implementation)

- App: `PackAudience`, `LibraryAudienceFilter`, labels, vocabulary, validators, tests
- Content: `AudienceVocabulary`, `validate_pack` audience check
- Docs: this report, `METADATA_MODEL.md`, vocabulary / authoring updates

**Content manuscripts:** unchanged.
