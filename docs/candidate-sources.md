# Candidate second sources

Everything in the mapping currently rests on **one book** — Bascom (1969) — which
`ROADMAP.md` correctly names as the main remaining weakness. These are leads
towards a second independent attestation. **Nothing here is verified, and
nothing here is in the KB.** A lead becomes a source only after someone reads
the actual text and records the table and page.

## 1. Olagunju et al. (2023) — strongest lead

> Olagunju, A. S., James, A. A., Adeyefa, E. O., & Joseph, F. L. (2023).
> *Algebraic characterization of Ifa main divination codes.*
> **Scientific African, 20, e01729.**
> DOI: [10.1016/j.sciaf.2023.e01729](https://doi.org/10.1016/j.sciaf.2023.e01729)

**Why this one matters.** It is the right *kind* of source for this project's
open question. The gap is the seniority ordering and the bit patterns — which
are structural facts — not verse text. This paper treats the 16 Oju Odù as 4×2
matrices forming an abelian group under addition mod 2, so its content is
mathematical throughout. No reproduction-rights problem, and no
initiation-restricted material.

It is also **open access**, indexed in DOAJ, in an Elsevier journal — so unlike
Abimbola 1975 it can be read legitimately rather than through an unauthorised
upload.

**Preliminary signal, NOT verification.** A search-engine summary reported the
order as: ogbe, oyeku, iwori, odi, irosun, iwonri, obara, okanran, ogunda, osa,
ika, oturupon, otura, irete, ose, ofun. Compared against
`data/principal_odu.json`, that agrees with our `southwestern-yoruba` order at
**16 of 16 positions**, and is *not* the Ifẹ variant recorded in
`alternativeOrders`. If the paper's own table says the same, this is genuine
independent corroboration of the predominant ordering.

**What still has to be done by hand**, because a summary is not a citation:

1. Open the DOI and read the actual table.
2. Record which mark is 1. Our frozen convention is **single mark = 1, double =
   0**, top-to-bottom with the top most significant, right leg = high nibble.
   A paper agreeing on the *order* while using the opposite bit convention
   corroborates the seniority list only — say so precisely rather than claiming
   the patterns are confirmed.
3. Check whether it cites its own source for the ordering, or asserts it. A
   paper repeating Bascom is not independent, and that distinction is the whole
   point of looking for a second source.
4. Note the licence (DOAJ suggests CC BY) before quoting anything.

`scripts/` has the source-entry path; do not shortcut it.

## 2. Abimbola (1975) — the intended counterweight, still not legitimately reachable

*Sixteen Great Poems of Ifá.* Niamey: CELHTO, 1975.

The natural counterweight to Bascom: Abimbola was a babaláwo, Bascom was not.

**Do not use the copies that surface in search.** The Internet Archive item
`sixteen-great-poems-of-ifa-wande-abimbola` is an individual's upload with no
licence and outside controlled lending; the Scribd and dokumen.pub copies are the
same material. Using them would break the exact discipline this project exists to
demonstrate.

Search results also repeat the **"UNESCO 1975"** miscitation, which was already
disproved here: UNESDOC `ark:/48223/pf0000019827` gives the imprint as CELHTO,
Niamey, with UNESCO only providing financial assistance. UNESCO's open-access
policy therefore does not apply.

Legitimate routes remain: `library@unesco.org`, `archives@unesco.org`, CELHTO
directly, or a library holding call number `896(662.1) ABI`.

## 3. Bascom (1980), *Sixteen Cowries* — still unconsulted

Would settle the Lucumí/New World ordering, which is currently unsourced.
**Catalogue trap:** Internet Archive item `sixteencowriesyo0000basc` is
catalogued as this book but the scan is *Explorations in African Systems of
Thought* (Karp & Bird) — same publisher and year, different book. Verify the
scan, never the metadata.

## 4. Other leads seen, unassessed

* Olagunju et al. (2018), *On the Code Characteristics of the Ifa Divination
  Codes* — likely the same group; check whether it is independent of (1).
* Longe, O. — frequently cited on Ifá and binary; primary text not yet located.

---

**Rule for all of these:** a second source is only worth having if it is
independent. If it turns out to cite Bascom for its ordering, record it as a
*restatement*, not as corroboration — and leave the single-source weakness
standing in ROADMAP.md rather than quietly declaring it closed.
