# QuietLibrary Editorial Metadata Model (Content Model v2)

**Status:** Canonical — Part 4  
**Audience:** Editors, contributors, validators, future discovery / recommendation systems

This document defines the long-term metadata axes for QuietLibrary books.
Each axis is independent. Do not merge them.

| Axis | Field | Cardinality | Purpose |
|------|-------|-------------|---------|
| **Audience** | `audience` | Exactly one | Intended primary readership |
| **Category** | `Genres` → manifest `categories` | One format + zero or more topics | Content shape + subject |
| **Difficulty** | `difficulty` | Exactly one (1–8) | Reading demand |
| **Nature** | `trustClassification` | Exactly one | Fiction / reality relationship |

Source of truth for edition metadata: `books/<book_id>/<locale>/reading-pack.md`.  
`book.yaml` must not store these fields.

---

## Audience

Audience describes the **intended primary audience** of the book.

It is **not**:

- a genre
- a reading method
- an age rating
- a censorship label

### Canonical ids

| Id | Label | Definition |
|----|-------|------------|
| `children` | Children | Books primarily written for children (fairy tales, animals, imagination, simple adventures, everyday childhood stories). A parent may read aloud, but the story itself is primarily for children. |
| `family_reading` | Family Reading | Books intentionally designed for **shared** reading. Should engage both children and adults: multiple levels of interpretation, conversation starters, moral reflection, parenting / emotional development topics. Distinct from Children. |
| `teens` | Teens | Books primarily intended for teenagers. |
| `adults` | Adults | Books primarily intended for adult readers (philosophy, politics, psychology, economics, biographies, serious non-fiction, crime, mature themes, complex emotional topics). Adults does **not** mean censored — it means intended audience. |
| `everyone` | Everyone | Books that naturally work across all age groups. |

### Legacy aliases (accepted; do not use in new packs)

| Legacy id | Maps to |
|-----------|---------|
| `child` | `children` |
| `children_8_12` | `children` |
| `family` | `family_reading` |
| `teen` | `teens` |
| `adult` | `adults` |

New manuscripts must use canonical ids only.

### Authoring example

```markdown
**Audience:** family_reading
```

---

## Category (independent from Audience)

Category / Genres describe **what the book is about / what shape it has**, not who it is for.

A History book may have Audience `children`, `family_reading`, `teens`, or `adults`.

### Format ids (exactly one)

`short_story`, `fairy_tale`, `article`, `dialogue`, `legend`, `instruction`, `science_fiction`

### Topic ids (zero or more)

Examples: `adventure`, `animals`, `biography`, `history`, `nature`, `philosophy`, `poetry`, `science`, `travel`, `psychology`, …

**Do not** use audience words as topics (`family`, `children`, `adults`, …).

---

## Difficulty (independent from Audience)

| Property | Rule |
|----------|------|
| Range | Integer **1–8** |
| Meaning | Reading demand of the text |
| Independence | Children ≠ Easy; Adults ≠ Difficult |

Authoring:

```markdown
**Difficulty:** 3 (of 8)
```

---

## Nature (trust classification)

`fiction` · `inspired_by_reality` · `adapted_from_real_events` · `popular_science` · `instruction` · `demo`

Orthogonal to Audience and Category.

---

## Related

- [LIBRARY_METADATA_VOCABULARY.md](../product/LIBRARY_METADATA_VOCABULARY.md)
- [METADATA_MODEL_V2_AUDIT_REPORT.md](METADATA_MODEL_V2_AUDIT_REPORT.md)
- [EDITORIAL_OWNERSHIP.md](../../alephbits-content/docs/EDITORIAL_OWNERSHIP.md)
- [READING_PACK_AUTHORING_FORMAT.md](READING_PACK_AUTHORING_FORMAT.md)
