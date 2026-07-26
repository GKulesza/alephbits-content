# RFC – QuietLibrary Experience

**Status:** Proposal (architecture & UX only)  
**Date:** 2026-07-21  
**Audience:** Founder, product, future client implementers  
**Depends on:** World Engine Foundation · World Dictionary (100% coverage) · [WORLD_DICTIONARY_FINAL_REPORT.md](WORLD_DICTIONARY_FINAL_REPORT.md) · Milestone Review 01  

**Non-goals for this RFC:** Do **not** implement QuietLibrary, Reader changes, recommendations, AI runtime, SVG artwork, or approval automation. This document designs the experience only.

---

## 1. Summary

QuietLibrary is not a bookshelf and not a gamified meta-layer.

It is **the reader’s memory made spatial** — a calm, living place that slowly accumulates traces of stories that have been read. The place changes. Objects and characters remember. Dialogue deepens. Nothing announces itself as a reward.

The World Dictionary supplies the semantic vocabulary. QuietLibrary consumes **Approved** dictionary entries and reading memory — never raw book metadata, never spoilers, never title lists.

---

## 2. Vision

> Books gradually leave traces inside a living library.  
> The library slowly changes as more stories are read.  
> The reader discovers those changes naturally.  
> Nothing should feel like a game reward.  
> Everything should feel like remembering.

QuietLibrary is a **place**, not a feature.

| It is | It is not |
|-------|-----------|
| Memory | Achievement system |
| Atmosphere | Dashboard |
| Literary echoes | Quest log |
| Slow recognition | Unlock notifications |
| Personal over time | Social leaderboard |

---

## 3. Principles

### Feel

Calm · Slow · Surprising · Personal · Alive

### Forbidden UX patterns

- Achievements, badges, trophies  
- Points, XP, levels  
- Quests, missions, checklists  
- Progress bars toward “completion”  
- Push notifications for new dialogue or décor  
- “Unlocked after reading…” copy  

### Design tests

1. **Reward test:** If removing a celebration animation makes the moment clearer, remove it.  
2. **Memory test:** Would this still make sense if the reader forgot *which* book caused it, but remembered the *feeling*?  
3. **Place test:** Does this belong in a room, or on a settings screen? If the latter, it is not QuietLibrary.  
4. **Spoiler test:** Could a visitor who has not read the book understand the change without learning the plot? If not, soften or delay it.

---

## 4. Data foundations (non-negotiable)

| Source | QuietLibrary may use | QuietLibrary must not use |
|--------|----------------------|---------------------------|
| World Dictionary | **Approved** entries only | Proposed-only ids; raw pack `world` blocks |
| Reading memory | Books completed / last opened (local) | Exact spoilers, quiz answers, full text |
| Time | Local calendar gaps (days/months away) | Server-side surveillance |
| Cross-book links | Shared dictionary ids & curated echo rules | Explicit title cross-references in UI |

Book metadata remains for the Reader and Library. QuietLibrary sees **memory + approved vocabulary**, not the content catalog as a shopping list.

---

## 5. User journey

### 5.1 First arrival

The reader opens QuietLibrary for the first time.

- A nearly empty room: shelves, a window, soft light.  
- Perhaps one quiet figure (librarian or cat) who says little or nothing.  
- No tutorial overlay. No “Get started by reading 3 books.”  
- Optional: a single line of dialogue that establishes tone, then silence.

**Feeling:** You have entered a place that was waiting, not a feature that needs onboarding.

### 5.2 Early reading (few books)

After one or two completed books:

- Atmosphere may shift slightly (season, dust, candle).  
- One artifact related to a characteristic world element may appear on a shelf or table — not celebrated.  
- Architecture remains sparse. Living spaces may not yet form.

**Feeling:** Something is different, but you are not sure when it changed.

### 5.3 Habit (dozens of books)

Recurring themes from the World Dictionary begin to shape **living spaces**:

- The House thickens (home, window, glass, clock).  
- A School corner gathers books.  
- A Forest Edge appears near the window if nature ids accumulate.

Artifacts multiply slowly. Characters notice the reader more often.

**Feeling:** The room knows your reading life without summarizing it.

### 5.4 Return after absence

Months later:

Librarian: *“I haven’t seen you for a long time.”*  
Cat (later, if present): *“Exactly two months and four days.”*

No streak reminder. No “Welcome back — claim reward.”

**Feeling:** Being remembered.

### 5.5 Deep memory (years)

Objects speak in layers. Cross-book echoes appear. A dragon reacts differently after a second dragon-marked story. A key that once forgot its door now hopes for a spell to break — without explaining the intervening books.

**Feeling:** Literary déjà vu. Recognition is the reader’s private pleasure.

---

## 6. Multi-layer environment

QuietLibrary is rendered as stacked **visual layers**. Each layer has a different relationship to data and time.

```text
┌─────────────────────────────────────────┐
│  L6 Ambient life        (motion, dust)  │
│  L5 Characters          (observers)     │
│  L4 Artifacts           (memories) ★    │
│  L3 Living spaces       (theme rooms)   │
│  L2 Architecture        (common frame)  │
│  L1 Atmosphere          (mood weather)  │
└─────────────────────────────────────────┘
```

### Layer 1 — Atmosphere

**Purpose:** Mood. Not inventory.

Examples: snow, rain, dust, smoke, candlelight, television interference, leaves, fog, soft dusk, winter window frost.

| Driven by | Examples |
|-----------|----------|
| Season / local time | Winter snow; evening candlelight |
| Soft aggregates of themes | Many forest books → occasional leaves |
| Absence | Dust after long gaps |

Atmosphere never “unlocks.” It drifts.

### Layer 2 — Architecture

**Purpose:** Stable spatial grammar of the library building.

Examples: shelves, windows, stairs, arches, doors, railings, floor grain.

Built mostly from **common, approved place/object concepts** that almost every reader will eventually touch (`home`, `window`, `book`, `street` as motifs of structure — not as literal street tiles).

Architecture changes rarely and slowly (a new arch after many civic books; a taller shelf after many books). Never a construction animation with confetti.

### Layer 3 — Living spaces

**Purpose:** Recurring semantic themes become inhabitable corners.

Aligned with Milestone / Final Report observations:

| Living space (working name) | Dominant approved concepts | Notes |
|----------------------------|----------------------------|-------|
| The House | `home`, `window`, `glass`, `clock` | Highest richness today |
| The Street & Town | `street`, `town`, `shop`, `market` | Civic realism |
| The School | `school`, `book`, `library` | Learning axis |
| The Forest Edge | `forest`, `tree`, `flower`, `garden` | Medium; grows with nature reads |
| The River | `river`, `bridge`, `boat` | Medium; `boat`/`bridge` still thin |
| The Castle | `castle`, `dragon`, `cave`, `key`, `treasure` | Legend alcove |
| Companion Corner | `dog`, `ball`, childhood creatures | Warmth, not quests |

Spaces appear as **regions within one continuous library**, not as a map menu of levels. The reader walks or pans; they do not select “Forest DLC.”

### Layer 4 — Artifacts ★ (most important)

**Purpose:** Memorable objects from stories. **Memories, not collectibles.**

Rules:

1. An artifact may come from a **single** book if it is characteristic of that fictional world.  
2. Artifacts map to World Dictionary ids (objects, symbols, sometimes creatures-as-objects).  
3. Presentation is quiet: placed, not awarded.  
4. No rarity tiers, no “legendary drop.”  
5. Visual fidelity may begin as Unicode / simple glyph placeholders; later SVG or illustration.

Examples (illustrative — not all exist as approved ids yet):

- rusty key (`key`)  
- candy tin (may need future id or map to `candy`)  
- red ribbon (future symbol)  
- old clock (`clock`)  
- lantern / flashlight (future or deferred)  
- ballet shoes (future — only if inevitable)

**Artifact presence ≠ dialogue.** An object may sit for months without speaking.

### Layer 5 — Characters

**Purpose:** Observers of the reader. Not quest givers.

Examples: librarian, cat, raven, owl.

| They may | They must not |
|----------|---------------|
| Notice absence | Assign tasks |
| Comment on atmosphere | Explain unlock conditions |
| Echo themes the reader has lived | Spoil plots or name titles |
| Remain silent for long stretches | Nag |

Characters are sparse. One or two is enough for years.

### Layer 6 — Ambient life

**Purpose:** Aliveness without obligation.

Birds at the window. A cat crossing the floor. Curtains. Fireplace. Dust motes. Shelf settling.

Ambient life is almost never gated. It exists so the place breathes.

---

## 7. Dialogue architecture

### 7.1 Who may speak

- Artifacts (Layer 4)  
- Characters (Layer 5)  
- Rarely: the room itself (architecture), in very spare lines  

Atmosphere and ambient life do not speak in words.

### 7.2 When dialogue exists

Dialogue is **conditional on reader experience**, never random noise.

Condition inputs (local only):

| Signal | Use |
|--------|-----|
| Completed books carrying approved world ids | Theme depth, artifact awakening |
| Time since last QuietLibrary visit | Absence lines |
| Time since last reading session | Soft staleness |
| Prior dialogue stage for this speaker | Progression |
| Shared ids across completed books | Cross-book echoes |

No RNG for “daily quote.” Silence is valid and common.

### 7.3 Progression philosophy

```text
Silent object
    ↓  (reader has lived a related memory)
First thought  — incomplete, wistful
    ↓  (more related reading, or time + return)
Second thought — sharper, still unexplained
    ↓  (optional deep echo)
Third thought  — literary recognition for those who notice
```

The reader is **never** told why a line changed.

### 7.4 Presentation (JRPG-calm)

```text
┌──────────┬──────────────────────────────┐
│          │                              │
│ Portrait │  “I don’t remember which     │
│  (glyph) │   door I belonged to.”       │
│          │                              │
│          │              — Rusty Key     │
└──────────┴──────────────────────────────┘
```

- Portrait left (or right in RTL later).  
- Dialogue box opposite.  
- Advance by tap / click / key — no voice acting required.  
- Portraits may start as Unicode placeholders (🔑, 🐈, 📚) until art exists.  
- One speaker at a time. No branching skill trees.

### 7.5 Dialogue examples

**Absence**

> Librarian: *I haven’t seen you for a long time.*  
> Cat: *Exactly two months and four days.*

**Artifact awakening**

> Key (early): *I don’t remember which door I belonged to.*  
> Key (later): *Perhaps you’ll finally find someone who can break this spell.*

**Cross-book echo (no titles)**

> Key: *There was another like me once. Quieter. Hungrier for rain.*  
> Dragon: *The air smells of a second fire. Older. Or younger. I can’t tell.*  
> Ribbon (future): *Someone else also tied a promise and walked away.*

**Character memory of the reader**

> Librarian: *You always stop at this window first.*  
> (Only after many visits — never on visit two.)

---

## 8. Cross-book memory (literary echoes)

### Intent

Books reference one another **indirectly** through shared World Dictionary concepts and curated echo rules.

### Rules

1. Never display another book’s title in QuietLibrary dialogue.  
2. Never spoil plot outcomes.  
3. Prefer metaphor and mood over facts.  
4. Echo strength grows with approved shared ids among **completed** books.  
5. Editorial echo packs (optional later) may define special pairs (`key`↔`key`, `dragon`↔`dragon`) without naming packs.

### Recognition

The reward is the reader thinking: *I’ve felt this before.*  
Not a UI stamp: *Connection unlocked.*

---

## 9. Interaction model

### Primary interactions

| Action | Result |
|--------|--------|
| Enter QuietLibrary | Show current layers; no summary modal |
| Pan / walk slowly | Discover spaces and artifacts |
| Tap artifact / character | Open dialogue if any stage is available; else a calm empty beat (look, not error) |
| Leave | Persist state locally; no “session score” |

### Non-interactions

- No inventory screen of “all memories.”  
- No filter “show only unlocked.”  
- No share-to-social of achievements.  
- No forced dialogue on entry.

### Optional secondary (future, still quiet)

- Sit in a chair (changes ambient only).  
- Open a window (atmosphere shift).  
- These must never gate content.

---

## 10. Progression philosophy (summary)

| Progresses | How the reader notices |
|------------|------------------------|
| Atmosphere | Weather of memory |
| Architecture | Building feels slightly more itself |
| Living spaces | New corners to wander |
| Artifacts | Objects that were not there — or newly attentive |
| Dialogue stages | Words that changed since last time |
| Character familiarity | Being known |

| Does not progress | |
|-------------------|--|
| Player level | |
| Completion % of QuietLibrary | |
| Streak counters | |

Time is an ingredient. Absence is content.

---

## 11. Relationship to World Dictionary

| Dictionary role | QuietLibrary use |
|-----------------|------------------|
| Approved `places` | Living spaces + architecture hints |
| Approved `objects` / `symbols` | Artifacts |
| Approved `creatures` | Occasional characters or companion presence |
| Approved `plants` | Forest Edge / atmosphere |
| Proposed entries | **Invisible** until approved |

Singleton artifacts are **encouraged** when characteristic — QuietLibrary differs from dictionary gravity here: the dictionary stays reusable; the *room* may hold a one-story memory without demanding a second book.

Editorial approval remains the gate from vocabulary → visible memory.

---

## 12. Future expansion ideas (out of scope now)

- Illustrated portraits replacing Unicode  
- Seasonal festivals that only change atmosphere  
- Multi-device sync of QuietLibrary state via Reader Memory (still local-first)  
- Very rare “shared echo” between two readers’ libraries (opt-in, still no gamification)  
- Gentle export of a still image of one’s room (memory postcard — not a score)  
- Editor tools to author dialogue stages bound to approved ids  

---

## 13. Acceptance criteria for this RFC

PASS when stakeholders agree that:

1. QuietLibrary is defined as **living literary memory**, not a reward loop.  
2. Six visual layers and their responsibilities are clear.  
3. Dialogue is experience-gated, silent-by-default, and JRPG-calm in presentation.  
4. Cross-book memory never names titles or spoils plots.  
5. Discovery has no notifications.  
6. Data contracts respect Approved World Dictionary + local reading memory.  
7. No implementation is implied by accepting this RFC alone.

---

## 14. Decision

| Option | Meaning |
|--------|---------|
| **Accept** | Freeze vision, layers, dialogue philosophy; schedule implementation phases later |
| **Revise** | Adjust layers, artifact vs dictionary tension, or dialogue tone |
| **Defer** | Keep World Dictionary only; revisit QuietLibrary when art/time allow |

---

## 15. References

- [WORLD_DICTIONARY_FINAL_REPORT.md](WORLD_DICTIONARY_FINAL_REPORT.md)  
- [WORLD_DICTIONARY_MILESTONE_REVIEW_01.md](WORLD_DICTIONARY_MILESTONE_REVIEW_01.md)  
- [world/README.md](../../world/README.md)  
- [world/REVIEW_CANDIDATES.md](../../world/REVIEW_CANDIDATES.md)  
- App-layer: World Engine Foundation · RFC Book World Metadata (alephbits)

---

*QuietLibrary should feel like returning to a room that has been thinking about you — never like opening a feature that has been waiting to grade you.*
