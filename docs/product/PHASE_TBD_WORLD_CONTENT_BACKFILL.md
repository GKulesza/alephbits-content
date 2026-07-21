# Phase TBD — World Content Backfill

**Date:** 2026-07-21  
**Repo:** `alephbits-content`  
**Branch:** `cursor/world-content-backfill`  
**Goal:** Curate semantic `world` metadata across the library and grow the shared World Dictionary **slowly**.

**Editorial authority:** [world/README.md](../../world/README.md)

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

Dictionary: [world/dictionary.yaml](../../world/dictionary.yaml)

---

## Non-goals

QuietLibrary · Reader UI · Recommendations · Runtime AI
