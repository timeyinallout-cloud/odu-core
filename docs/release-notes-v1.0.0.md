# v1.0.0 — a verified foundation

The first version resting on a primary source rather than on recall.

## What is verified

All **16 principal Odù** — every bit pattern and every seniority rank — checked
against Bascom, *Ifa Divination: Communication Between Gods and Men in West
Africa* (1969), **Table 1 p. 4** and **Table 3 column B p. 48**, read through
Internet Archive controlled lending. Nothing required correction.

`odu verify` exits non-zero unless all 16 still carry a citation, a date and a
named checker. CI runs it on every push.

## What is deliberately empty

**202 of the 256 figures have no traditional name, and there are no verses.**

These are not gaps awaiting a contributor. Bascom's book indexes the figures he
collected verses for — 54 of 256 — and the contracted names appear only there.
No openly-licensed corpus of ẹsẹ Ifá exists, and some of it is
initiation-restricted, which is a question of standing rather than copyright.

`null` here means *no source found*. Everything of value in this dataset rests
on that remaining true.

## Contents

- 256 figures with bit patterns, seniority ranks, and legs
- 54 attested compound names, 31 with their spoken elision, all cited by page
- 54 citation-only verse records — page references, no reproduced text
- 4 cited recitations, linked and not hosted
- Python and TypeScript packages, parity-tested against a shared fixture
- A knowledge base whose schema makes unattributed content impossible to insert
- Deterministic art and rhythm derived from the bit patterns

## Conventions

Four choices fix the mapping. Change any one and every byte means something
different: single mark = 1, lines top to bottom with the top most significant,
right leg is the high nibble, southwestern Yorùbá seniority.

Bascom examined 86 lists from 61 sources and found that order predominant in 42
of them — and recorded **21 other rankings**. His own study follows the Ifẹ
variant, carried here in `alternativeOrders`. The library indexes by bit
pattern precisely because ordering is contested and structure is not.

## Corrections made before release

- An untraceable search-engine claim had Ọ̀sá and Òtúrúpọ̀n swapped. It was not
  acted on; Bascom later confirmed the dataset was right.
- The contracted names were first recorded with the elided vowel removed,
  reading Bascom's parenthesis as deletion. It marks the vowel as *optional*.
  Corrected by the maintainer, a Yorùbá speaker.
- An Internet Archive item catalogued as Bascom (1980) is a different book.
  Recorded and not used.
- *Sixteen Great Poems of Ifá* (1975) is widely miscited as a UNESCO
  publication. UNESCO funded it; the OAU published it.

## Citing this

DOI [`10.5281/zenodo.21743992`](https://doi.org/10.5281/zenodo.21743992) for this version; [`10.5281/zenodo.21743991`](https://doi.org/10.5281/zenodo.21743991) always resolves to the latest. See `CITATION.cff`. Please cite Bascom alongside it — this dataset is a
transcription, not a discovery.

## Contributing

Corrections are the point of it being public. See `CONTRIBUTING.md`; the
sourcing rule is stated first because it decides everything else.
