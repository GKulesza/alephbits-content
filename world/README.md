# World Dictionary

**Status:** Living editorial vocabulary for the AlephBits World Engine.  
**Authority file:** [dictionary.yaml](dictionary.yaml)  
**App counterpart:** in-app World Dictionary (aggregates from compiled `lesson.json`).

The dictionary should grow **slowly**. Long-term consistency beats precision.

---

## Editorial rules

### 1. Prefer existing concepts

Always search this file (and aliases) before creating a new id.

Avoid near-duplicates:

| Prefer | Avoid creating |
|--------|----------------|
| `flashlight` | `flash_light`, `torch_light` |
| `oak` | `oak_tree` |
| `tree` | `magical_tree` (unless magic is the whole point *and* no reuse is likely) |

### 2. Prefer generic concepts over story-specific ones

Ask: **Will this concept likely appear in another book?**

| If yes | Keep / reuse it |
|--------|-----------------|
| If no | Use a more general concept |

Good durable ids: `dragon`, `castle`, `market`, `forest`, `river`, `key`, `flower`

Avoid unless truly central *and* reusable: `rainy_realm`, `magical_tree`, `stuffed_ram`

### 3. World elements are not plot elements

Describe the **furniture of the fictional world**, not events.

| Good | Not |
|------|-----|
| `forest`, `dragon`, `bridge`, `castle` | `dragon_defeat`, `secret_mission`, `lost_key_found` |

### 4. Reuse beats creation

If an existing id expresses approximately the same concept, **reuse it**.

Do not optimize for perfect precision. Optimize for decades of shared vocabulary.

### 5. Categories (frozen)

Only these five:

- `objects`
- `creatures`
- `plants`
- `symbols`
- `places`

Do **not** add categories in this phase.

### 6. Status

- New ids: `status: proposed`
- Never auto-approve
- Approved entries are production-ready for future clients (QuietLibrary, etc.)

### 7. Density

Usually **3–5** elements per book. Sparse is better than noisy. Empty `world` is valid.

---

## Backfill

See [PHASE_TBD_WORLD_CONTENT_BACKFILL.md](../docs/product/PHASE_TBD_WORLD_CONTENT_BACKFILL.md).

## Review candidates

Living list with usage counts and reasons: [REVIEW_CANDIDATES.md](REVIEW_CANDIDATES.md).
