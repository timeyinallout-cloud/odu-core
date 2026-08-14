# A canonical byte mapping for the 256 Odù Ifá

**Draft, 2026-08-14.** Not submitted. Written to be checkable: every claim either
cites a source or is labelled as unsourced.

---

## Abstract

The Ifá divination system of the Yorùbá enumerates 256 figures (Odù), each a
pair of four-position columns marked singly or doubly. That structure is
exactly one byte. This correspondence is often noted in passing and rarely
pinned down: published accounts differ on which mark is 1, on which column is
most significant, and on the seniority ordering of the figures — so two
implementations can both claim to encode "the Odù" and disagree on every value.

We give an explicit, frozen convention; a canonical dataset of all 256 figures
keyed by bit pattern; and a verification of the 16 principal figures against a
published source. We argue that the bit pattern, not the seniority rank, must be
the primary key, because seniority varies by lineage while structure does not.

The dataset deliberately contains **no verse text**. We set out why a corpus of
ẹsẹ Ifá cannot responsibly be assembled from available sources, and what the
dataset records instead.

---

## 1. The problem with "Ifá is binary"

The observation that Ifá encodes binary information is old and correct, and by
itself does no work. A usable mapping has to fix four things that published
accounts leave open:

1. **Which mark is 1.** A single stroke and a double stroke are the two states;
   nothing in the practice designates either as the "on" state.
2. **Bit order within a column.** Four positions, read top to bottom or bottom
   to top.
3. **Which column is the high nibble.** The figure is cast as a pair; which is
   the left and which the right is a convention of transcription.
4. **The ordering of the figures.** Seniority is the traditional ordering, and
   it is *not* uniform.

Each is a free binary-ish choice, and the combinations disagree. A mapping that
does not state all four is not reproducible, however correct its intent.

## 2. The convention, frozen

    single mark   = 1
    double mark   = 0
    positions read top to bottom, top most significant
    right leg     = high nibble
    ordering      = southwestern-yoruba seniority

These are recorded in the dataset's own `convention` block rather than in prose,
and the specification is versioned. **Changing any one of them changes every byte
value**, so they are treated as frozen: a change is a new major version, not a
correction.

Worked example: Èjì Ogbè is four single marks in both columns — `1111 1111` —
byte 255. Ọ̀yẹ̀kú Méjì is four double marks in both — byte 0.

## 3. Bit pattern as primary key

The dataset is keyed by bit pattern, with seniority rank as an attribute.

This is the load-bearing design decision. Seniority ordering varies by lineage:
Bascom (1969) examined 86 lists from 61 sources and found the ordering genuinely
contested. Indexing by rank would fork the mapping — a Lucumí-ordered
implementation and a southwestern-Yorùbá one would assign different bytes to the
same figure, and neither would be wrong. Indexing by structure does not fork,
because the marks are the marks regardless of lineage.

The ordering is therefore recorded as a labelled attribute
(`southwestern-yoruba`), with variants held alongside it rather than replacing
it. The Ifẹ ordering — which Bascom himself uses throughout his study — differs
from the predominant one at positions 5–8 and 11–14 while sharing every bit
pattern, and is recorded as an alternative order.

A practical consequence worth stating: **Bascom numbers his 256 figures by the
Ifẹ order, so his figure numbers do not correspond to the seniority rank used
here.** Cross-referencing by number silently misaligns.

## 4. Verification

The 16 principal figures were checked against Bascom (1969), *Ifa Divination:
Communication Between Gods and Men*, Table 1 p. 4 and Table 3 column B p. 48,
read via Internet Archive controlled lending. Every bit pattern and every
seniority rank matched; no corrections were required.

Two findings from that check are worth recording because they contradict
commonly repeated claims:

* An earlier assertion that Ọ̀sá and Òtúrúpọ̀n were transposed in our data was
  **wrong** — Bascom confirms `0111` and `0010` as we had them.
* Bascom omits tone marks and writes **"Edi"** for Òdí. Orthographic variants are
  recorded as attested names rather than silently normalised.

**The main limitation of this work is that verification rests on a single
source.** A second independent attestation has not yet been obtained. Abimbola
(1975) is the natural counterweight — he was a babaláwo, Bascom was not — but
the accessible copies are unauthorised uploads, and it is widely miscited as a
UNESCO publication when the imprint is CELHTO, Niamey. Olagunju et al. (2023)
is a promising open-access candidate whose reported ordering appears to agree,
but it has not yet been read directly and is not claimed here as corroboration.

## 5. What is deliberately absent

The dataset contains **no ẹsẹ Ifá**. This is not an omission to be filled later
by scraping.

No openly licensed corpus of Ifá verse exists. Every substantial collection is
commercial and copyrighted; the recorded sources all disallow reproduction. More
importantly, some of the material is initiation-restricted within the practice
itself, and a public dataset is the wrong container for it regardless of
copyright.

What the knowledge base holds instead is **citations**: pointers to where a verse
was published or where a recitation may be heard. A pointer is not a
reproduction, which is why a recording may be cited even when its verse text
never could be.

Two rules enforce this in code rather than in policy:

* `source_id` is `NOT NULL` on every content table. Nothing is stored without a
  provenance.
* Publication is **default-deny**: material is published only if it is marked
  published, unrestricted, its source permits reproduction, and every contributor
  still consents. One narrow exception exists — an alternative *name* may publish
  from a copyrighted source, because a proper name is a fact rather than an
  expressive work.

The corpus ships empty. **No verse was ever generated**, and the design intends
that it cannot be: there is no path that writes content without a source.

For the same reason, 221 of the 256 figures carry a null traditional compound
name. Those names are lineage-specific contractions and elision is a spoken
convention, not a spelling rule, so they must be sourced rather than derived.
A null is a true statement about the evidence; a plausible generated name would
be a false one.

## 6. Implementation

The canonical JSON is the artifact; language bindings are thin readers over it.
Python and TypeScript packages are provided, the latter consuming the generated
JSON verbatim rather than re-deriving it, with a committed parity fixture so any
drift appears as a reviewable diff.

Whichever language owns the data becomes the one that cannot drift, making every
other binding second-class — hence data-first rather than library-first.

## 7. What would improve this

1. A second independent source for the ordering, ideally one that does not itself
   cite Bascom.
2. The 221 unsourced compound names, from a lineage able to attest them.
3. Attested orderings from other lineages — particularly Lucumí, currently
   unsourced — recorded as further alternatives rather than as corrections.

---

## References

Bascom, W. (1969). *Ifa Divination: Communication Between Gods and Men.*
Indiana University Press.

Abimbola, W. (1975). *Sixteen Great Poems of Ifá.* Niamey: CELHTO.
[Frequently miscited as a UNESCO publication; UNESCO provided financial
assistance only — see UNESDOC ark:/48223/pf0000019827.]

Olagunju, A. S., James, A. A., Adeyefa, E. O., & Joseph, F. L. (2023).
Algebraic characterization of Ifa main divination codes. *Scientific African*,
20, e01729. https://doi.org/10.1016/j.sciaf.2023.e01729
[Identified as a candidate second source; **not yet consulted directly.**]
