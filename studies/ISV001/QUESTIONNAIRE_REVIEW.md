# ISV001 Questionnaire Review

**Study:** ISV001 · **Version:** 2 · **Date:** 2026-07-19  
**Book:** `polish_przerwa` (“Przerwa”)  
**Primary instrument:** `questions.pl.json` (English mirror: `questions.en.json`)

---

## Issues found in demonstration v1

| # | Issue | Severity | Resolution in v2 |
|---|--------|----------|------------------|
| 1 | Every `correctIndex` was `1` (position bias) | High | Correct answers spread across indices 0–3 |
| 2 | “Jak kończy się **ta noc**?” ambiguous (opening night vs epilogue) | High | Reworded to “Jak kończy się **opowiadanie**?” |
| 3 | Title implied Interslavic text; book is Polish literary prose | Medium | Study title/description reframed as comprehension pilot on *Przerwa*; Interslavic reserved for future packs |
| 4 | No item covering mid-story traffic-jam beat | Low | Added podcast/stress question from section II |
| 5 | Theme item overlapped heavily with stress item | Low | Theme item removed; stress + ending kept distinct |
| 6 | Empty `institution` | Low | Set to AlephBits Research Program |

---

## v2 item map

| # | Construct | Correct index (PL/EN) | Source in text |
|---|-----------|------------------------|----------------|
| 1 | Fact — work hours | 2 | §I opening |
| 2 | Fact — notebook entry | 0 | §I first page |
| 3 | Fact — notebook origin | 3 | §I drawer |
| 4 | Fact — spoken question in jam | 1 | §II Wisłostrada |
| 5 | Inference — stress as information | 2 | §IV closing reflection |
| 6 | Fact — story ending | 3 | §IV final paragraph |

---

## Verification checklist

- [x] No duplicate questions
- [x] No ambiguous “which night” wording
- [x] Exactly one correct answer per item
- [x] Distractors plausible but text-falsifiable
- [x] Difficulty mix: 4 factual + 1 inference + 1 global ending
- [x] Consistent character name (Patryk) and terminology (notes / notebook, stres / stress)
- [x] PL and EN instruments aligned (same order, same correct indices)

---

## Residual limitations

- Primary questionnaire language is Polish; English file is a translation mirror for documentation and future UI language switching (loader currently uses `questions:` from YAML → `questions.pl.json`).
- Text is literary Polish, not Interslavic — suitable for platform/pilot validation; not a test of Interslavic medical lexicon.
