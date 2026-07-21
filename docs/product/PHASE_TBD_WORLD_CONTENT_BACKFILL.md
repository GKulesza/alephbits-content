# Phase TBD — World Content Backfill

**Date:** 2026-07-21  
**Repo:** `alephbits-content`  
**Branch:** `cursor/world-content-backfill`  
**Goal:** Curate semantic `world` metadata across the library and grow the shared World Dictionary.

---

## Compiler support

`compile_pack` now emits optional `world` into `lesson.json` when present in `reading-pack.md`.

| Behavior | Detail |
|----------|--------|
| Missing `world` | Valid — field omitted |
| Invalid ids | Dropped; compile continues |
| Format | Compact bullets or YAML-style lists under `**World:**` |

---

## Batch 1 (2026-07-21)

| Book | Elements |
|------|----------|
| Spacer po Krakowie | `market_square`, `castle`, `river` |
| Na targu | `market`, `mountain`, `jacket` |
| Legenda o Smoku Wawelskim | `dragon`, `castle`, `cave`, `river`, `stuffed_ram` |
| Niedźwiedź | `bear`, `home` |
| Cukierek z magicznego drzewa | `forest`, `magical_tree`, `candy`, `fox`, `rabbit` |
| Klucz do deszczowej krainy | `key`, `forest`, `rainy_realm`, `flower` |
| Ciekawska Zosia i skarb przyjaźni | `town`, `doll`, `treasure` |
| Koziołek Matołek | `goat`, `horseshoe`, `forge`, `town` |

**Reused across books:** `castle`, `river`, `forest`, `town`  
**New proposed ids:** 25 (all `proposed`)  
**Duplicate merges this batch:** none  
**Approved:** 0 (editorial review pending)

Dictionary: [world/dictionary.yaml](../../world/dictionary.yaml)

---

## Non-goals

QuietLibrary · Reader UI · Recommendations · Runtime AI
