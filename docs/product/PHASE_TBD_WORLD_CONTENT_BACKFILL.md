# Phase TBD — World Content Backfill

**Date:** 2026-07-21  
**Repo:** `alephbits-content`  
**Branch:** `cursor/world-content-backfill`  
**Goal:** Curate semantic `world` metadata across the library and grow the shared World Dictionary **slowly**.

**Editorial authority:** [world/README.md](../../world/README.md)  
**Milestone Review 01:** [WORLD_DICTIONARY_MILESTONE_REVIEW_01.md](WORLD_DICTIONARY_MILESTONE_REVIEW_01.md)

---

## Stability rules (summary)

1. Prefer existing concepts — search before inventing.  
2. Prefer **generic** over story-specific (`tree` not `magical_tree`).  
3. World furniture ≠ plot events.  
4. Reuse beats creation.  
5. Taxonomy frozen: objects · creatures · plants · symbols · places.  
6. Small batches; quality over speed.

---

## Compiler support

`compile_pack` emits optional `world` into `lesson.json` when present in `reading-pack.md`.

| Behavior | Detail |
|----------|--------|
| Missing `world` | Valid — field omitted |
| Invalid ids | Dropped; compile continues |
| Format | Compact bullets or YAML-style lists under `**World:**` |

---

## Batch 1 (2026-07-21) — later normalized

| Book | Elements |
|------|----------|
| Spacer po Krakowie | `market_square`, `castle`, `river` |
| Na targu | `market`, `mountain`, `jacket` |
| Legenda o Smoku Wawelskim | `dragon`, `ram`, `castle`, `cave`, `river` |
| Niedźwiedź | `bear`, `home` |
| Cukierek z magicznego drzewa | `forest`, `tree`, `candy`, `fox`, `rabbit` |
| Klucz do deszczowej krainy | `key`, `forest`, `flower` |
| Ciekawska Zosia i skarb przyjaźni | `town`, `doll`, `treasure` |
| Koziołek Matołek | `goat`, `horseshoe`, `forge`, `town` |

**Normalization merges:** `magical_tree` → `tree`; `stuffed_ram` → `ram`; dropped `rainy_realm`.

---

## Batch 2 (2026-07-21)

| Book | Elements |
|------|----------|
| Ciche serce dzwonka | `bell`, `shop`, `street` |
| Czarny mnich z Nikiszowca | `gate`, `street`, `monk` |
| Czterech w łódce | `boat`, `office` |
| Kąkuter i chomik | `hamster`, `home` |
| Pies Pankracy… | `dog`, `school`, `ball` |
| Ognioskoczek | `forest`, `library`, `book`, `stone` |
| Kapuściana tajemnica | `cabbage`, `home`, `clock` |
| Nowy ogród | `garden`, `burrow`, `corn`, `flower` |

---

## Batch 3 (2026-07-21) — dictionary gravity

Maximize reuse; only three new ids (`bridge`, `window`, `glass`).

| Book | Elements | New? |
|------|----------|------|
| Franek i mały Karolek | `street`, `market`, `garden`, `home`, `book` | none |
| Cudaczek-Wyśmiewaczek | `town`, `river`, `home` | none |
| Wiatr nad rzeką | `river`, `bridge` | `bridge` |
| Susza | `forest`, `tree` | none |
| Dobra dziewczynka | `home`, `book` | none |
| Domek | `home`, `window` | `window` |
| Cisza | `home`, `glass` | `glass` |
| Betonowy dom | `home`, `shop` | none |

---

## Batch 4 (2026-07-21) — zero growth

**New concepts: 0.** All 21 element slots reused existing vocabulary.

| Book | Elements |
|------|----------|
| Dostrojony dom | `home`, `window` |
| Klucz babci Rózi | `key`, `flower`, `home`, `town` |
| Kamień pamięci | `stone`, `office` |
| Kubek | `home`, `glass`, `book` |
| Jak ugotować herbatę | `home`, `glass` |
| W kawiarni | `shop`, `town`, `glass` |
| Jeszcze | `school`, `home`, `book` |
| Radio w głowie | `school`, `home` |

**Singleton → multi-use this batch:** `key`, `stone`, `office`, `window`, `school`, `glass`, `shop`  
**Approximate reuse notes:** café → `shop`; mug/cup/tea vessel → `glass`

---

## Batch 5 (2026-07-21) — zero growth, denser network

**New concepts: 0.** Element slots: 22. Reuse ratio ∞.

| Book | Elements |
|------|----------|
| Chór | `home`, `glass` |
| Kamera na ulicy | `street`, `home` |
| Pudełko po ciastkach | `home`, `town`, `window` |
| Na dworcu | `town`, `street` |
| Buty | `office`, `home` |
| Gruby dzienniczek | `book`, `home`, `street` |
| Złoto i zwykłe szczęście | `castle`, `town`, `shop`, `treasure` |
| Próg | `home`, `clock`, `window`, `book` |

### Editorial approximations (Batch 5)

| Approximation | Reason |
|---------------|--------|
| train station → `town` + `street` | Station not in dictionary; journey world is civic streetscape |
| cobbler workshop → `shop` | Workshop as place of trade |
| gold duck / gold fortune → `treasure` | Symbol already present; promotes singleton |
| shoes (title of *Buty*) deferred | Avoid new `shoe` singleton; story world is clinic/office |

### Review candidates (accumulated)

Living list: [world/REVIEW_CANDIDATES.md](../../world/REVIEW_CANDIDATES.md).

---

## Batch 6 (2026-07-21) — zero growth, singleton promotion

**New concepts: 0.** Element slots: 22. Reuse ratio ∞.

| Book | Elements |
|------|----------|
| Naczynia połączone | `school`, `home` |
| Kij i marchewka | `home`, `school` |
| Powrót | `home`, `street`, `dog`, `window` |
| Przedszkole bez ścian | `school`, `forest`, `garden` |
| Ułamki | `home`, `school`, `clock` |
| Nowy pacjent | `office`, `library`, `book` |
| Siedem gór i jeden ocean | `mountain`, `home`, `book` |
| W pełni | `home`, `book` |

### Editorial approximations (Batch 6)

| Mapping | Status | Reason |
|---------|--------|--------|
| preschool → `school` | acceptable | Learning place for children |
| Almaty flat → `home` | excellent | Dwelling |
| clinic bookshelves → `library` | acceptable | Knowledge room |
| ocean (title) → deferred; used `mountain` | temporary | Prefer existing; `ocean` on review list |

### Concepts becoming multi-use

`dog`, `library`, `mountain`

Dictionary: [world/dictionary.yaml](../../world/dictionary.yaml)

---

## Batch 7 (2026-07-21) — zero growth, inevitable-concept discipline

**New concepts: 0.** Element slots: 20. Reuse ratio ∞.

| Book | Elements |
|------|----------|
| Przerwa | `home`, `window` |
| Taniec | `home`, `window` |
| Mowa | `home`, `glass`, `book` |
| Rozmowa z lekarzem | `office`, `home` |
| Opowieści z poprzedniego życia | `home`, `street`, `ball` |
| Etykieta | `home`, `school` |
| Głos i cisza | `castle`, `river` |
| Maria Skłodowska-Curie | `home`, `town`, `school`, `book` |

### Editorial approximations (Batch 7)

| Mapping | Status | Possible future concept |
|---------|--------|-------------------------|
| sea palace → `castle` | excellent | — |
| deep ocean → `river` (alias `ocean`) | temporary | `ocean` |
| playground → `street` + `ball` | acceptable | `playground` |
| dance hall → `home` | temporary | `hall` / `stage` |

### Concepts becoming multi-use

`ball`

### Review candidate classifications

Updated in [world/REVIEW_CANDIDATES.md](../../world/REVIEW_CANDIDATES.md) (`keep` / `merge` / `generalize` / `revisit later`).

Dictionary: [world/dictionary.yaml](../../world/dictionary.yaml)

---

## Non-goals

QuietLibrary · Reader UI · Recommendations · Runtime AI
