# Contributing

Corrections are the point of this being public. Especially from practitioners,
Yorùbá speakers, and anyone who can reach a source we can't.

## The one rule

**Nothing is stored without a source.** Not discouraged — impossible. The
schema has `source_id NOT NULL` on every content table, so an unattributed
verse fails to insert rather than landing quietly in the corpus.

This is not bureaucracy. A dataset about a living tradition that cannot say
where a line came from is worse than an empty one, because it launders a guess
into a citation.

## The gaps are deliberate, not an invitation

Before offering to fill them, please read why they're empty:

**202 figures have no traditional name.** They are not missing. Bascom's book
indexes the figures he collected verses for — 54 of 256 — and the contracted
names appear only there. `traditionalName: null` is a statement about the
evidence.

**There are no verses.** No openly-licensed corpus of ẹsẹ Ifá exists. The
corpus holds page references and pointers instead. Some ẹsẹ Ifá are
initiation-restricted, which is a question of standing, not copyright — no
licence lifts it.

A pull request adding names or verses from an unsourced list will be declined,
however accurate it looks. If you have a source, that changes everything.

## What is most useful

| | |
|---|---|
| **A second independent source** | Everything verified rests on Bascom (1969). See `docs/second-source-enquiry.md`. |
| **Orthography corrections** | Tone is meaning. If a name is wrong, say so — a previous reading of Bascom's elision notation was backwards until a speaker corrected it. |
| **Regional variants** | Bascom recorded 21 orderings besides ours. Variants are recorded alongside, never instead of. Disagreement is data. |
| **Recitations** | We cite where a recitation can be heard. We do not host audio or transcribe verses. |
| **Telling us something is wrong** | An issue costs you nothing and is worth more than a guess. |

## If you are a practitioner

If anything here misrepresents the tradition, that is a defect regardless of
what the licence permits, and correcting it takes priority over everything
else in this file. Open an issue, or get in touch privately if that's more
appropriate.

If material here should not be circulating — the `restricted` flag exists for
exactly that, and it is an absolute bar. Tell us and it comes down.

## Practical

```sh
git clone https://github.com/timeyinallout-cloud/odu-core
cd odu-core
make                      # build every derived artifact
make test                 # 211 Python + 29 TypeScript
python3 scripts/ingest.py --check
```

Enable the local hook once with `git config core.hooksPath .githooks`; it runs
the same gates CI does.

**Never edit a derived file by hand.** `data/odu_256.json`, `site/`, `web/` and
`kb/odu.db` are all generated. CI fails if a generated file disagrees with its
source. Edit `data/principal_odu.json` or `kb/content/` and regenerate.

Adding content means adding a file under `kb/content/sources/` — one file per
source, because provenance is the organising fact. See the README there.
