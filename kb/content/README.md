# Content files

**This directory is the corpus.** `kb/odu.db` is a derived index rebuilt from
these files by `scripts/ingest.py` — it can be deleted and regenerated at any
time, and it is not version-controlled.

The reasoning is the same one behind `data/principal_odu.json`: whatever holds
the truth must be the thing that gets reviewed, diffed, and kept. A binary
SQLite file fails all three. A preservation project cannot have its corpus live
only in an artifact that no one can read in a pull request.

## Layout

One file per source, named for it. Grouping by source rather than by figure is
deliberate — provenance is the organising fact here, and it means adding a book
is adding one file rather than touching two hundred.

```
kb/content/
  contributors.json          people, and their consent
  sources/
    bascom-1969.json         a source plus everything drawn from it
    abimbola-1976.json
```

## Source file shape

```json
{
  "source": {
    "slug": "bascom-1969",
    "kind": "book",
    "title": "Ifa Divination: Communication Between Gods and Men in West Africa",
    "author": "William R. Bascom",
    "year": 1969,
    "publisher": "Indiana University Press",
    "rights": "all-rights-reserved"
  },
  "verses": [
    {
      "odu": "ogbe-ogbe",
      "pageReference": "p. 314",
      "status": "published"
    }
  ],
  "notes": []
}
```

`odu` accepts a slug (`ogbe-oyeku`), a byte (`0`-`255`), or a name. It is
resolved through odu-core, so a typo fails the ingest rather than landing on the
wrong figure.

## Rules the ingest enforces

- Every verse and note belongs to a source. There is nowhere to put an
  unattributed one.
- `yorubaText` is only accepted when the source's `rights` permit reproduction.
  Otherwise record a `pageReference` — a pointer to where a verse lives is a
  real contribution, and a copyright violation is not.
- A verse needs either text or a page reference. Neither means it asserts
  nothing.
- Contributors are referenced by slug and must exist in `contributors.json`
  with a recorded consent status.

Run `python3 scripts/ingest.py --check` to validate without writing anything.

## Adding to the corpus

Entries are made by hand, from a source, one at a time. Nothing in this
directory was generated, and nothing in it should be. If you cannot cite it,
it does not go in.
