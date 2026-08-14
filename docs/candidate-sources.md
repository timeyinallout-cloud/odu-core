# Candidate second sources

Everything in the mapping currently rests on **one book** — Bascom (1969) — which
`ROADMAP.md` correctly names as the main remaining weakness. These are leads
towards a second independent attestation. **Nothing here is verified, and
nothing here is in the KB.** A lead becomes a source only after someone reads
the actual text and records the table and page.

## 1. Olagunju et al. (2023) — CONSULTED 2026-08-14. Corroborates the order,
##    conflicts on two figures.

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

**Read directly on 2026-08-14** — Table 1, *"Two-arm representation of the
signature of 16 principal Odu"*, which gives hierarchy, name, méjì name and the
four marks per figure. Confirmed **open access under a Creative Commons licence**
on the article page.

Compared against `data/principal_odu.json` on **marks**, not bit values, so the
comparison holds regardless of either side's 0/1 mapping:

| | result |
|---|---|
| seniority ranks | **16 of 16 agree** |
| mark patterns | **14 of 16 agree** |
| conflicts | **Ọ̀sá and Òtúrúpọ̀n — exactly transposed** |

Ours (from Bascom): Ọ̀sá `II I I I`, Òtúrúpọ̀n `II II I II`.
Olagunju et al.: Ọ̀sá `II II I II`, Òtúrúpọ̀n `II I I I`.

Every other figure matches mark for mark, and the ordering is the predominant
`southwestern-yoruba` one, not the Ifẹ variant. So this is **genuine independent
corroboration of the seniority ordering** — the single-source weakness on the
ordering is now materially reduced.

### The conflict is the interesting part

ROADMAP and the memory of this project record an earlier claim that Ọ̀sá and
Òtúrúpọ̀n were transposed in our data, which was investigated, found
**untraceable**, and rightly not acted on — Bascom's Table 1 p. 4 and Table 3
col. B p. 48 were read directly and confirm our assignment.

That claim now has a traceable source. It is not a rumour and it is not an error
in our reading; it is a **published disagreement** between:

* Bascom (1969), read via controlled lending — our assignment, and
* Olagunju et al. (2023), peer-reviewed and open access — the transposition.

**Do not silently change the data.** Our figures were verified against the
primary source we actually read, and the frozen convention means any change to a
mark pattern changes byte values. The honest record is that two published
sources disagree on these two figures, exactly as they disagree on seniority
ordering across lineages.

### It is independent of Bascom — checked

The decisive question was whether this restates Bascom (in which case the
conflict would just be a transcription slip) or attests independently. Its
reference list was read in full on 2026-08-14: **15 references, and Bascom
appears in none of them.**

Its Ifá sources are the Nigerian scholarly and practitioner literature:

* **Abimbola, W. (1976). *IFA: An Exposition of Ifa Literary Corpus.* Oxford
  University Press** — the very counterweight this project has been seeking, and
  the one Bascom cannot supply: Abimbola was a babaláwo.
* Adegbindin, O. (2014); Ogunleye, A. R. (2011, 2019); Falokun, F. (1992);
  Ilori, K. A. (1986); Paul-Kolade, T. (2020); Odeyemi, I. (2016).
* **Oluwade, D. & Longe, O. (2003). On the code characteristics of the Ifa
  divination codes.** *J. Comput. Sci. Appl.* 9(1) — the Longe work previously
  noted as a lead with no located text.

The remainder are abstract-algebra textbooks supporting the group-theoretic
argument.

**So the Ọ̀sá / Òtúrúpọ̀n conflict is a disagreement between two independent
lineages of scholarship**, not an error in either reading:

| | Ọ̀sá | Òtúrúpọ̀n |
|---|---|---|
| Bascom (1969), American anthropologist, southwestern Yorùbá informants | `II I I I` | `II II I II` |
| Olagunju et al. (2023), via Abimbola (1976) and the Nigerian literature | `II II I II` | `II I I I` |

This is the same *kind* of variation already recorded for seniority ordering,
where Bascom himself found 86 lists from 61 sources. It is now attested for mark
patterns too, on exactly two figures.

### What this changes

1. **The ordering weakness is materially reduced.** A source that does not cite
   Bascom independently gives the same `southwestern-yoruba` order, 16 of 16.
2. **A new, sharper open question replaces it**: which mark pattern belongs to
   Ọ̀sá. Both assignments are published; ours is verified against the source we
   read directly.
3. **Abimbola 1976 is now the priority acquisition** — not 1975. It is cited here
   as an Oxford University Press book, which is far more likely to be reachable
   through a library than the CELHTO imprint. Consulting it directly would settle
   whether the transposition originates with Abimbola or with this paper's
   reading of him.

### Still to check

* Whether Olagunju et al. state a source for Table 1 specifically, or present it
  as common knowledge drawn from the corpus above.
* Whether the companion paper (Olagunju et al. 2018) carries the same table.
* Their bit convention: the paper represents signatures "using indexes 0 and 1".
  This does not affect the mark comparison, which was done on marks, but it
  matters before citing any byte value of theirs.

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
