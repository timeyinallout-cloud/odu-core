# odu-core

The 256 Odù Ifá as a canonical byte mapping, with Yorùbá orthography intact.

An Odù figure is two legs of four lines each, and every line carries either one
mark or two. That is four bits per leg, eight bits per figure, and exactly 256
figures — a bijection with the byte that needs no padding and loses nothing.

```python
from odu_core import from_byte, encode, decode

from_byte(255).name          # 'Èjì Ogbè'
from_byte(0).name            # 'Ọ̀yẹ̀kú Méjì'
from_byte(44).name           # 'Òtúrúpọ̀n Ìrosùn'

decode(encode(b"hello")) == b"hello"   # True
```

## The data is the project

`data/principal_odu.json` holds the 16 principal Odù and is the single source of
truth. Everything else — all 256 figures, every byte value, every ordering — is
derived from it. `data/odu_256.json` is the generated artifact other languages
and surfaces import, so nothing re-derives the mapping for itself.

Regenerate after any change to the canonical 16:

```sh
python3 scripts/generate.py
```

## Conventions

Four choices fully determine the mapping. Change any one and every byte value
means something different, so they are recorded in the data file rather than
buried in code:

| Choice | This library |
|---|---|
| Single mark | `1` |
| Double mark | `0` |
| Line order | top to bottom, top line most significant |
| Leg order | right leg is the high nibble |
| Seniority | southwestern Yorùbá (Bascom's predominant order) |

There is no universal digital standard for any of these. Interoperability with
anyone else's work depends on stating them explicitly, which is why
`spec_version()` exists — encoded data, generated art, and mnemonics are only
meaningful against a known version.

## Mnemonic phrases

Bytes become figures, with a checksum figure appended so that a mistyped or
transposed figure is caught on decode instead of silently yielding different
bytes.

```python
from odu_core.mnemonic import to_phrase, from_phrase, format_phrase

phrase = to_phrase(b"heritage computing")
format_phrase(phrase, "display")   # 'Ìwòrì Ọ̀bàrà · Ìwòrì Òfún · …'
from_phrase(phrase)                # b'heritage computing'
```

From the command line:

```sh
odu encode --text "Ifá" --style display
odu random --bytes 32 --style numbered
odu decode "ika-odi iwori-iwori irosun-owonrin ose-okanran irosun-ofun"
odu show 44          # describe and draw one figure
odu table            # the 16 principal Odù
odu spec             # the bit conventions in use
```

Slug form (`ika-odi`) is the canonical written form — ASCII, one token per
figure. Display form keeps full orthography and needs a separator, since figure
names are themselves two words. Both parse back.

A browser demo of the same thing lives in `web/`:

```sh
python3 scripts/build_web.py && python3 -m http.server -d web
```

### Before using this for key material

The checksum detects accidental corruption. It is not authentication, it is not
encryption, and it adds no entropy — a phrase reveals exactly the bytes it
encodes to anyone holding it.

Each figure carries 8 bits where a BIP-39 word carries 11, so 24 figures are 192
bits against a 24-word BIP-39 phrase's 264. **If you are encoding a wallet seed,
use BIP-39** — it is specified, audited, and interoperable across wallets. This
layer is built for memory, teaching, and art.

## Building

```sh
make          # everything, in dependency order
make test     # Python (132) and TypeScript (29) suites
make check    # validate content, type-check, report verification coverage
make clean    # remove derived artifacts
```

Everything derives from `data/principal_odu.json`. The Makefile encodes the
order so it cannot be got wrong by running scripts out of sequence.

## TypeScript

`ts/` is a thin binding that **reads** `data/odu_256.json` rather than
re-deriving the mapping. Two implementations that each compute the table can
drift apart; one that computes and one that reads cannot.

```ts
import { fromByte, toPhrase, formatPhrase } from "@odu/core";

fromByte(255).name;                        // 'Èjì Ogbè'
formatPhrase(toPhrase(new TextEncoder().encode("Ifá")));
```

Its test suite asserts against `ts/test/fixtures/parity.json`, generated from
the Python implementation, so the two cannot silently disagree about a name, a
seniority rank, or a checksum.

Source files import with `.ts` extensions, so Node runs them directly with
native type stripping — no build step for a quick check:

```sh
node -e 'import("./ts/src/index.ts").then(m => console.log(m.fromByte(44).name))'
```

`tsc` rewrites those to `.js` on the way into `dist/`. It does **not** rewrite
them in declaration files, which would leave `dist/*.d.ts` pointing at a
`./types.ts` that isn't there and break every TypeScript consumer — so
`npm run build` runs `scripts/fix-decl-extensions.mjs` afterwards, and
`test/dist.test.js` fails the build if any `.ts` specifier survives. Build
through `npm run build` or `make`, never bare `tsc`.

Native stripping needs a Node built with Amaro. Distro packages often are not
(`node -p 'process.config.variables.node_use_amaro'` must print `true`); an
official nodejs.org or nvm build is.

## Knowledge base

Sourced content keyed to the 256 figures.

**`kb/content/` is the corpus; `kb/odu.db` is a derived index.** The database is
rebuilt from scratch on every ingest and is not version-controlled — whatever
holds the truth must be the thing that gets reviewed and diffed, and a binary
SQLite file fails that.

```sh
python3 scripts/ingest.py --check   # validate content files, write nothing
python3 scripts/ingest.py           # rebuild kb/odu.db
python3 scripts/build_kb_site.py    # generate site/ — 256 permalinks + index
```

**Nothing can be stored without a source.** `source_id` is `NOT NULL` on every
content table, so an unattributed verse does not merely get flagged — it fails
to insert. A corpus that cannot say where a line came from has no value, and a
corpus of living sacred material that cannot say so is worse than empty.

**The corpus ships empty, deliberately.** No verse in this repository was
generated. Filling it means sitting with the sources and entering records one at
a time, which is the slow part of the project and the part that cannot be
automated.

### Publication is default-deny

The site generator reads only the `publishable_*` views. A record reaches the
public site only if *all* of these hold:

| Gate | Reason |
|---|---|
| `status = 'published'` | drafts stay private |
| `restricted = 0` | some ẹsẹ Ifá are initiation-restricted |
| source permits reproduction | citable ≠ republishable |
| every contributor still consents | consent is withdrawable, and withdrawal propagates |

Forgetting any one of them hides the record rather than exposing it. Withdrawing
a contributor's consent retracts their material from the next build while
leaving citation-only records intact — there is an end-to-end test for exactly
that.

A source under copyright is still useful: store a `page_reference` instead of
the text. Attempting to store reproduced text from such a source raises rather
than silently accepting it.

## Seniority is not numeric order

Ogbè is the most senior Odù, but its leg is `1111` — byte 255, last numerically.
The two orderings are genuinely different and neither follows from the other by
arithmetic on the byte.

This is why the library indexes by **bit pattern**, not by rank. Bit patterns are
structural and uncontested; seniority varies by lineage and region, so it lives
as an attribute that can hold more than one tradition. Adding the Lucumí ordering
means adding a field to the JSON, not rewriting the mapping.

```python
from odu_core import by_seniority
by_seniority()[0].name       # 'Èjì Ogbè'  (byte 255)
```

## Orthography

Yorùbá carries two independent diacritic systems: sub-dots that distinguish
letters (ẹ, ọ, ṣ) and tone marks that carry pitch (à, á). Both are meaningful —
stripping either produces a different word, not a cosmetic variant.

Canonical data keeps full diacritics and is NFC-normalized (tested). ASCII slugs
exist alongside as identifiers only, and the conversion is deliberately one-way.

```python
from odu_core import principal
principal("Ọ̀yẹ̀kú") is principal("oyeku")   # True — both resolve
```

## Status and verification

**All 16 principal figures are verified — `16 of 16`.** Checked 2026-07-28
against Bascom, *Ifa Divination* (1969), **Table 1 p. 4** and **Table 3
column B p. 48**, read via Internet Archive controlled lending. Every bit
pattern and every seniority rank matched; no corrections were needed.

```sh
odu verify                             # exits 0 only when all 16 are verified
python3 scripts/verify_odu.py --status # per-figure detail with citations
```

`--against` and `--by` are both required, so a verification without a source
and a name cannot be recorded. Tests assert that no figure claims `verified`
without a citation, a checker, and a date.

### Seniority is southwestern Yoruba, and that is a choice

Bascom examined **86 lists from 61 sources**. The order used here is the
predominant one — 42 of 86 lists, including 30 of 60 Yoruba lists, 5 of 6
Cuban, and the single Brazilian list. But **twenty-one other rankings are
recorded** (Bascom 1969, pp. 47–48), and Bascom's own study follows a
different one: the Ifẹ variant, kept in `alternativeOrders` in the canonical
JSON.

The two differ only in the order of two pairs, positions 5–8 and 11–14. Bit
patterns are identical in both. This is exactly why the library indexes by
**bit pattern** and treats rank as an attribute — the structure is settled,
the ordering is not.

Structural invariants are still enforced by tests: the 16 legs cover every
4-bit value exactly once, and every consecutive seniority pair is a bitwise
complement or bit-reversal.

## Mnemonic phrases

Bytes become figures, with a checksum figure appended so that a mistyped or
transposed figure is caught on decode instead of silently yielding different
bytes.

```python
from odu_core.mnemonic import to_phrase, from_phrase, format_phrase

phrase = to_phrase(b"heritage computing")
format_phrase(phrase, "display")   # 'Ìwòrì Ọ̀bàrà · Ìwòrì Òfún · …'
from_phrase(phrase)                # b'heritage computing'
```

From the command line:

```sh
odu encode --text "Ifá" --style display
odu random --bytes 32 --style numbered
odu decode "ika-odi iwori-iwori irosun-owonrin ose-okanran irosun-ofun"
odu show 44          # describe and draw one figure
odu table            # the 16 principal Odù
odu spec             # the bit conventions in use
```

Slug form (`ika-odi`) is the canonical written form — ASCII, one token per
figure. Display form keeps full orthography and needs a separator, since figure
names are themselves two words. Both parse back.

A browser demo of the same thing lives in `web/`:

```sh
python3 scripts/build_web.py && python3 -m http.server -d web
```

### Before using this for key material

The checksum detects accidental corruption. It is not authentication, it is not
encryption, and it adds no entropy — a phrase reveals exactly the bytes it
encodes to anyone holding it.

Each figure carries 8 bits where a BIP-39 word carries 11, so 24 figures are 192
bits against a 24-word BIP-39 phrase's 264. **If you are encoding a wallet seed,
use BIP-39** — it is specified, audited, and interoperable across wallets. This
layer is built for memory, teaching, and art.

## Building

```sh
make          # everything, in dependency order
make test     # Python (132) and TypeScript (29) suites
make check    # validate content, type-check, report verification coverage
make clean    # remove derived artifacts
```

Everything derives from `data/principal_odu.json`. The Makefile encodes the
order so it cannot be got wrong by running scripts out of sequence.

## TypeScript

`ts/` is a thin binding that **reads** `data/odu_256.json` rather than
re-deriving the mapping. Two implementations that each compute the table can
drift apart; one that computes and one that reads cannot.

```ts
import { fromByte, toPhrase, formatPhrase } from "@odu/core";

fromByte(255).name;                        // 'Èjì Ogbè'
formatPhrase(toPhrase(new TextEncoder().encode("Ifá")));
```

Its test suite asserts against `ts/test/fixtures/parity.json`, generated from
the Python implementation, so the two cannot silently disagree about a name, a
seniority rank, or a checksum.

Source files import with `.ts` extensions, so Node runs them directly with
native type stripping — no build step for a quick check:

```sh
node -e 'import("./ts/src/index.ts").then(m => console.log(m.fromByte(44).name))'
```

`tsc` rewrites those to `.js` on the way into `dist/`. It does **not** rewrite
them in declaration files, which would leave `dist/*.d.ts` pointing at a
`./types.ts` that isn't there and break every TypeScript consumer — so
`npm run build` runs `scripts/fix-decl-extensions.mjs` afterwards, and
`test/dist.test.js` fails the build if any `.ts` specifier survives. Build
through `npm run build` or `make`, never bare `tsc`.

Native stripping needs a Node built with Amaro. Distro packages often are not
(`node -p 'process.config.variables.node_use_amaro'` must print `true`); an
official nodejs.org or nvm build is.

## Knowledge base

Sourced content keyed to the 256 figures.

**`kb/content/` is the corpus; `kb/odu.db` is a derived index.** The database is
rebuilt from scratch on every ingest and is not version-controlled — whatever
holds the truth must be the thing that gets reviewed and diffed, and a binary
SQLite file fails that.

```sh
python3 scripts/ingest.py --check   # validate content files, write nothing
python3 scripts/ingest.py           # rebuild kb/odu.db
python3 scripts/build_kb_site.py    # generate site/ — 256 permalinks + index
```

**Nothing can be stored without a source.** `source_id` is `NOT NULL` on every
content table, so an unattributed verse does not merely get flagged — it fails
to insert. A corpus that cannot say where a line came from has no value, and a
corpus of living sacred material that cannot say so is worse than empty.

**The corpus ships empty, deliberately.** No verse in this repository was
generated. Filling it means sitting with the sources and entering records one at
a time, which is the slow part of the project and the part that cannot be
automated.

### Publication is default-deny

The site generator reads only the `publishable_*` views. A record reaches the
public site only if *all* of these hold:

| Gate | Reason |
|---|---|
| `status = 'published'` | drafts stay private |
| `restricted = 0` | some ẹsẹ Ifá are initiation-restricted |
| source permits reproduction | citable ≠ republishable |
| every contributor still consents | consent is withdrawable, and withdrawal propagates |

Forgetting any one of them hides the record rather than exposing it. Withdrawing
a contributor's consent retracts their material from the next build while
leaving citation-only records intact — there is an end-to-end test for exactly
that.

A source under copyright is still useful: store a `page_reference` instead of
the text. Attempting to store reproduced text from such a source raises rather
than silently accepting it.

## Seniority is not numeric order

Ogbè is the most senior Odù, but its leg is `1111` — byte 255, last numerically.
The two orderings are genuinely different and neither follows from the other by
arithmetic on the byte.

This is why the library indexes by **bit pattern**, not by rank. Bit patterns are
structural and uncontested; seniority varies by lineage and region, so it lives
as an attribute that can hold more than one tradition. Adding the Lucumí ordering
means adding a field to the JSON, not rewriting the mapping.

```python
from odu_core import by_seniority
by_seniority()[0].name       # 'Èjì Ogbè'  (byte 255)
```

## Orthography

Yorùbá carries two independent diacritic systems: sub-dots that distinguish
letters (ẹ, ọ, ṣ) and tone marks that carry pitch (à, á). Both are meaningful —
stripping either produces a different word, not a cosmetic variant.

Canonical data keeps full diacritics and is NFC-normalized (tested). ASCII slugs
exist alongside as identifiers only, and the conversion is deliberately one-way.

```python
from odu_core import principal
principal("Ọ̀yẹ̀kú") is principal("oyeku")   # True — both resolve
```

## Status and verification

**The bit patterns are unverified against a primary source.** They are
internally consistent — the 16 legs cover every 4-bit value exactly once, and
every consecutive pair in seniority order is either a bitwise complement or a
bit-reversal of its partner, both enforced by tests. That catches transcription
errors but it does not establish correctness.

Verification is tracked per figure rather than as one blanket disclaimer, so the
work is resumable and the current state is a fact rather than a memory:

```sh
python3 scripts/verify_odu.py --status      # what is still open
python3 scripts/verify_odu.py ogbe \
    --against "Bascom 1969, Table 1, p. 44" --by "Your Name"
```

`--against` and `--by` are both required — a verification without a source and a
name records nothing checkable. `odu verify` exits non-zero while any figure is
unverified, so CI can gate on it. Figures can also be marked `disputed`, because
sources genuinely disagree and a project about provenance needs somewhere to say
so rather than silently picking a winner.

This is the one part of the project that cannot be automated: it needs a person
with the book open. What is automated is the tracking.

The 240 compound figures carry descriptive `"<right> <left>"` names. Their
contracted traditional names vary by lineage and are left as
`traditionalName: null` — those must come from a citable source, never from
generation.

## Tests

```sh
python3 -m pytest tests/ -q
```

The mapping is small enough to test exhaustively, so every assertion about the
256 figures checks all 256 rather than sampling.

## License

MIT for the code and the structural mapping. Verse content added later needs
separate terms — some published collections are copyrighted, and oral
contributions need attribution and consent terms agreed with contributors.
