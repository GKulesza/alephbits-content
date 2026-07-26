# Experimental Packs

Draft and prototype packs use Content Model v2 under `books/<book_id>/` with:

```yaml
# books/<book_id>/book.yaml
status: experimental
```

Do not create packs under `experimental/<slug>/` — that Collection v1 path is retired.

Promotion to `community` or `official` is a `book.yaml` `status:` change plus full review.
