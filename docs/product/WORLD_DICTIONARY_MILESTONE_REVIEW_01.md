# Editorial Milestone Review 01 — World Dictionary

**Date:** 2026-07-21  
**Repo:** `alephbits-content`  
**Branch:** `cursor/world-content-backfill`  
**Checkpoint:** First half of the library (~45% coverage)  
**Nature:** Evaluation only — no taxonomy changes, no QuietLibrary implementation, no application work.

---

## 1. Dictionary overview

| Metric | Value |
|--------|------:|
| Total books (official PL packs) | 125 |
| Books with world metadata | 56 |
| Coverage | **44.8%** |
| Remaining books | 69 |
| Total concepts | 46 |
| Multi-use concepts | 24 |
| Single-use concepts | 22 |
| Reuse health | **52%** |
| Batches completed | 1–7 |
| New concepts since Batch 3 | 0 (Batches 4–7) |

### Concepts by category

| Category | Count | Share |
|----------|------:|------:|
| places | 19 | 41% |
| objects | 13 | 28% |
| creatures | 8 | 17% |
| plants | 4 | 9% |
| symbols | 2 | 4% |

### Growth trajectory (editorial)

| Batch | New concepts | Element slots reused | Coverage after |
|------:|-------------:|---------------------:|---------------:|
| 1 (+norm) | ~22 net after merges | — | 8 packs |
| 2 | 19 | — | 16 |
| 3 | 3 | heavy reuse | 24 |
| 4 | **0** | 21 | 32 |
| 5 | **0** | 22 | 40 |
| 6 | **0** | 22 | 48 |
| 7 | **0** | 20 | 56 |

**Verdict:** The dictionary has entered maturation. Size is stable; density and reuse health are rising.

---

## 2. Vocabulary quality

### Strengths

1. **Reuse-first discipline works.** Four consecutive zero-growth batches while coverage rose from 26% → 45%.  
2. **Identifier quality is high.** Almost all ids are generic English `snake_case` concepts (`home`, `forest`, `book`) rather than plot phrases.  
3. **Duplicate prevention is effective.** Near-duplicates (`magical_tree`, `flash_light`-style) were normalized early; aliases absorb wording variants (`glass` ← mug/cup).  
4. **Semantic backbone is clear.** A small set of places/objects recurs across dozens of packs and already feels like one literary universe.  
5. **Editorial process is documented.** Approximations and review candidates are logged, not improvised silently.

### Weaknesses

1. **Category imbalance.** Places dominate (41%); symbols (4%) and plants (9%) are thin.  
2. **Creature layer is mostly singletons.** Only `dog` is multi-use among creatures; the rest await natural reuse.  
3. **Some early specificity remains.** `market_square`, `forge`, `horseshoe` still look like first-pass leftovers.  
4. **Temporary approximations accumulate.** `ocean`, `station`, `hall`/`stage`, `playground` are deferred concepts that will need a deliberate decision before QuietLibrary.  
5. **Coverage ≠ completeness.** Domestic/learning packs are over-represented relative to science essays and abstract nonfiction, which may under-fill nature/legend rooms until later batches.

### Overall editorial quality

**Good — coherent and curated.** The vocabulary is already usable as a semantic model for the processed half of the library. It is not yet balanced enough to freeze as final QuietLibrary input, but it is healthy enough to finish the remaining books under the same rules.

---

## 3. Category review

Taxonomy stays frozen: objects · creatures · plants · symbols · places.

| Category | Balance | Assessment | Attention needed? |
|----------|---------|------------|-------------------|
| **places** | Overrepresented | Expected for narrative settings; backbone of reuse (`home`, `town`, `school`, `street`) | Light — watch for over-specific place ids (`market_square`, `forge`) |
| **objects** | Balanced | Strong domestic/learning props (`book`, `window`, `glass`) | Light — promote reusable props carefully; avoid packaging/title props |
| **creatures** | Underrepresented (as multi-use) | Count OK (8), but 7/8 are singletons | Medium — prefer reuse of `dog`, `dragon`, etc. before new fauna |
| **plants** | Underrepresented | Only `flower`/`tree` carry weight | Medium — when nature books appear, prefer these before new plants |
| **symbols** | Underrepresented | Only `treasure`, `monk` | Medium — add symbols sparingly when truly emblematic |

**Do not add categories.** Balance should improve by selective reuse and careful new ids in under-filled layers, not by taxonomy growth.

---

## 4. Reuse analysis — top twenty

| Rank | Concept | Uses | Category | Why it recurs |
|-----:|---------|-----:|----------|---------------|
| 1 | `home` | 34 | places | Domestic realism is the library’s center of gravity |
| 2 | `book` | 12 | objects | Reading, school, memory, diaries |
| 3 | `town` | 9 | places | Civic backdrop for adult and children’s stories |
| 4 | `school` | 9 | places | Teaching, childhood, parenting arcs |
| 5 | `street` | 8 | places | Movement between home and public life |
| 6 | `window` | 7 | objects | Interior ↔ outside threshold |
| 7 | `glass` | 6 | objects | Tea/tea/conversation rituals |
| 8 | `office` | 5 | places | Clinics, clinics, institutional rooms |
| 9 | `river` | 5 | places | Landscape + (temporary) water/ocean stand-in |
| 10 | `forest` | 5 | places | Wonder, childhood nature, fairy-tale edge |
| 11 | `shop` | 4 | places | Trade, café, workshop |
| 12 | `castle` | 4 | places | Legend / fairy-tale architecture |
| 13 | `garden` | 3 | places | Cultivation, childhood outdoor space |
| 14 | `clock` | 3 | objects | Time pressure, mornings, thresholds |
| 15 | `flower` | 3 | plants | Soft nature / care |
| 16 | `treasure` | 2 | symbols | Fortune, gift, moral wealth |
| 17 | `tree` | 2 | plants | Forest companion |
| 18 | `market` | 2 | places | Trade / gathering |
| 19 | `stone` | 2 | objects | Memory, weight, landmark |
| 20 | `key` | 2 | objects | Access, wonder, threshold |

### Semantic backbone

The backbone is unmistakably:

**`home` — `street`/`town` — `school`/`book` — `forest`/`river` — `castle`**

This is a world of households connected to civic space, learning, and a thinner but real layer of nature and legend.

---

## 5. Singleton analysis

| Identifier | Classification | Note |
|------------|----------------|------|
| `bear` | keep / probably reusable | Title creature; await second psychological/animal story |
| `bell` | keep / probably reusable | Strong object identity |
| `boat` | keep / probably reusable | Travel/water stories pending |
| `bridge` | keep / probably reusable | Natural pair with `river` |
| `burrow` | intentionally unique (for now) | Animal-home niche |
| `cabbage` | merge later / revisit | Story plant; low QuietLibrary value |
| `candy` | intentionally unique (for now) | Magic-tree story prop |
| `cave` | keep / probably reusable | Dragon/castle cluster |
| `corn` | revisit later | Garden niche |
| `doll` | keep / probably reusable | Childhood object |
| `dragon` | keep / probably reusable | High legend / QuietLibrary value |
| `forge` | merge later | Prefer `shop` |
| `fox` | keep / probably reusable | Fairy-tale fauna |
| `gate` | keep / probably reusable | Settlement architecture |
| `goat` | keep / probably reusable | Folk/children’s travel |
| `hamster` | intentionally unique (for now) | Contemporary pet niche |
| `horseshoe` | intentionally unique (for now) | Matołek-specific |
| `jacket` | revisit later | Market prop |
| `market_square` | generalize later | Prefer `market` / `town` |
| `monk` | keep / intentionally unique | Local legend symbol |
| `rabbit` | keep / probably reusable | Fairy-tale fauna |
| `ram` | intentionally unique (for now) | Wawel legend solution |

**Policy going forward:** Promote singletons only when a second book genuinely needs them. Do not invent second uses.

---

## 6. Approximation review

| Mapping | Classification | Future concept? |
|---------|----------------|-----------------|
| café → `shop` | excellent | Unlikely needed |
| mug/cup/tea → `glass` | acceptable | Unlikely; vessel family is enough |
| cobbler workshop → `shop` | excellent | Unlikely |
| gold fortune → `treasure` | excellent | No |
| doctor/embassy/clinic → `office` | excellent | No |
| Almaty flat → `home` | excellent | No |
| preschool → `school` | acceptable | Unlikely |
| clinic shelves → `library` | acceptable | Borderline; keep watching |
| sea palace → `castle` | excellent | No |
| station → `town` + `street` | temporary | **Likely yes: `station`** |
| ocean → `river` (+alias) / omitted | temporary | **Likely yes: `ocean`** |
| playground → `street` + `ball` | temporary/acceptable | **Possible: `playground`** |
| dance hall → `home` | temporary | **Possible: `hall` or `stage`** |

Temporary approximations that deserve a future decision (not during this review): **`station`**, **`ocean`**, optionally **`hall`/`stage`**, **`playground`**.

---

## 7. Review candidates — summary by action

Source of truth: [world/REVIEW_CANDIDATES.md](../../world/REVIEW_CANDIDATES.md)

| Action | Items |
|--------|-------|
| **keep** | `dragon`, `cave`, `boat`, `bridge`, `bell`, `ball`, `library`, `mountain`, `dog`, `gate`, `doll`, most creatures |
| **merge** | `forge` → `shop` |
| **generalize** | `market_square` → `market` / `town` |
| **revisit later** | `ram`, `burrow`, `cabbage`, `corn`, `candy`, `horseshoe`, `jacket`, deferred `ocean` / `station` / `plane` / `shoe` / `camera` / `box` |
| **remove** | none recommended yet |

### Priorities before finishing the library

1. When editing packs that use `forge` or `market_square`, perform the merge/generalize.  
2. Decide whether to introduce **`ocean`** and **`station`** once several water/travel books demand them (inevitable-concept test).  
3. Keep creature/plant/symbol growth slower than places.  
4. Do not approve (`status: approved`) bulk entries until coverage is complete and temporary approximations are resolved.

---

## 8. Emerging literary world

Supported by processed books only:

### Domestic life (dominant)

Homes, windows, glass, clocks, family interiors. The AlephBits world is primarily lived indoors and at the threshold of the street.

### Learning

Schools, books, libraries, preschool-as-school. Teaching and childhood form a second major axis.

### Civic / everyday public space

Towns, streets, shops, offices, markets. Adult realism moves between home and institutional rooms.

### Nature

Forests, rivers, mountains, gardens, trees, flowers — present but thinner than domestic life.

### Legend / wonder

Castles, dragons, caves, keys, treasure, occasional monks and magical thresholds — a minority but vivid layer.

### Friendship / companions

Dogs, balls, childhood creatures — social warmth around the domestic/learning core.

**Not yet strongly evidenced as separate worlds:** pure science-lab culture, industrial modernity, war as setting (except sparse historical interiors), ocean as first-class place (currently approximated).

---

## 9. QuietLibrary preparation (observation only)

No implementation. Suggested future rooms from recurring themes:

| Room name (working) | Dominant concepts | Richness |
|---------------------|-------------------|----------|
| **The House** | `home`, `window`, `glass`, `clock` | **high** |
| **The Street & Town** | `street`, `town`, `shop`, `market` | **high** |
| **The School** | `school`, `book`, `library` | **high** |
| **The Forest Edge** | `forest`, `tree`, `flower`, `garden` | **medium** |
| **The River** | `river`, `bridge`, `boat` | **medium** (boat/bridge still thin) |
| **The Castle** | `castle`, `dragon`, `cave`, `key`, `treasure` | **medium** |
| **The Companion Corner** | `dog`, `ball`, childhood creatures | **low–medium** |
| **The Clinic / Desk** | `office`, `book` | **low–medium** (functional, less atmospheric) |

QuietLibrary should consume **Approved** dictionary entries only (per World Engine architecture). Today all entries remain `proposed` — correct for this phase.

---

## 10. Recommendations (before remaining ~69 books)

### Dictionary growth

- Continue **reuse-first**; allow new concepts only when inevitable.  
- Expect modest growth (perhaps toward ~55–65), not another doubling.  
- Prefer filling underrepresented layers (plants, symbols, multi-use creatures) over new place micro-variants.

### Editorial discipline

- Keep the three-question gate (existing? multi-book? enriches whole?).  
- Log every approximation with status + possible future concept.  
- Update `REVIEW_CANDIDATES.md` each batch; do not rewrite from scratch.

### Category balance

- Do not change taxonomy.  
- When nature/legend books appear, deliberately strengthen plants/symbols/creatures via reuse.  
- Resist more office/home-only packs creating further place skew without adding atmosphere.

### Approximation policy

- **Excellent/acceptable** approximations may remain permanently.  
- **Temporary** ones (`station`, `ocean`, `hall`, `playground`) need a mid/late-library decision: introduce the concept or formally retire the aspiration.

### Singleton policy

- Singletons are allowed when characteristic.  
- Prefer promoting existing singletons over minting peers.  
- Schedule a cleanup pass for `forge` / `market_square` merges when convenient.

### Long-term maintainability

- Regenerate `dictionary.yaml` from compiled `lesson.json` after each batch (current practice).  
- Keep content dictionary as editorial authority; app dictionary remains aggregate + founder status.  
- Defer `approved` status until post-coverage editorial pass.  
- Run **Milestone Review 02** at ~100% coverage (or earlier if concepts jump past ~60 unexpectedly).

---

## Checkpoint decision

| Question | Answer |
|----------|--------|
| Is the dictionary a coherent semantic model for the processed half? | **Yes** |
| Ready to freeze for QuietLibrary? | **No** — still proposed; temporary approx unresolved; coverage incomplete |
| Ready to continue remaining books under same rules? | **Yes** |
| Resume Batch 8? | **Yes, after this report is committed** |

---

## Appendix — category inventories (current)

**places (19):** home, school, town, street, forest, office, river, castle, shop, garden, library, market, mountain, bridge, burrow, cave, forge, gate, market_square  

**objects (13):** book, window, glass, clock, ball, key, stone, bell, boat, candy, doll, horseshoe, jacket  

**creatures (8):** dog, bear, dragon, fox, goat, hamster, rabbit, ram  

**plants (4):** flower, tree, cabbage, corn  

**symbols (2):** treasure, monk  

---

*End of Editorial Milestone Review 01.*
