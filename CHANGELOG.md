# Changelog

Versions track the **data spec**, not the code. `spec_version()` is what
downstream artifacts — encoded data, generated art, mnemonic phrases — are
meaningful against, so the Python package, the TypeScript package and the JSON
always carry the same number.

A **major** bump means at least one of the four conventions changed (which mark
is 1, line order, which leg is the high nibble, seniority tradition). Every byte
value means something different after such a change, and anything encoded under
the previous spec silently becomes wrong.

## 1.0.0 — 2026-07-28

First version resting on a verified foundation.

**Verified.** All 16 principal figures checked against Bascom (1969), Table 1
p. 4 and Table 3 column B p. 48, via Internet Archive controlled lending. Every
bit pattern and every seniority rank matched; no corrections were needed.

**Seniority relabelled** from `yoruba-nigerian` to `southwestern-yoruba`, which
is Bascom's own term. He found this order predominant in 42 of 86 lists drawn
from 61 sources — and recorded 21 other rankings. His own study follows the Ifẹ
variant, now carried in `alternativeOrders`.

**Added.** `traditionalName` and `elidedForm` on the 256, sourced rather than
generated. Attested name variants on the principal figures.

### Corrections made along the way

- An untraceable search-engine claim had Ọ̀sá and Òtúrúpọ̀n swapped. It was not
  acted on, and Bascom later confirmed the dataset was right.
- The contracted names were first recorded as primary, reading Bascom's
  parenthesis as deletion. It marks an *optional* vowel — the name keeps it.
  Corrected on the authority of a Yorùbá speaker; the elision is now a variant.

## 0.2.0 — 2026-07-28

Per-figure verification tracking replaced a single blanket disclaimer.

## 0.1.0 — 2026-07-28

Initial mapping. Bit patterns internally consistent but unverified against any
primary source — a state this version was explicit about.
