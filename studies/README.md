# Studies

A **Study** is a linguistic or reading-comprehension experiment scenario.  
It reuses an existing book from the catalog. It is not a new application mode.

## Layout

```
studies/
  manifest.json          # index for sync + discovery
  ISV001/
    study.yaml           # study descriptor
    questions.pl.json    # question set (language-specific)
    questions.en.json
```

## study.yaml

```yaml
id: ISV001
title: Interslavic Comprehension
book: polish_przerwa        # pack id or bookId — never duplicate the book
language: pl
questions: questions.pl.json
export: true
```

## Sync

Studies are synchronized through the same GitHub raw overlay as books  
(`studies/manifest.json` + each study directory). No backend, no API, no database.

## Codes

Join codes normalize to the study `id`: case-insensitive, spaces and hyphens ignored  
(`ISV001`, `isv 001`, `IsV-001` → `ISV001`).

## Relationship to books

Studies never duplicate books. They reference a pack by catalog `id` or `bookId` under `official/`, `community/`, or `experimental/`.
