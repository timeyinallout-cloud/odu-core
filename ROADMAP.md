# What's left

Status as of 2026-07-28. Phases refer to the original five-phase plan.

## Done

| | |
|---|---|
| Phase 1 — core library | Python, canonical JSON, 256 figures, seniority |
| Phase 2 — mnemonic encoder | checksummed phrases, `odu` CLI, browser demo |
| Phase 3 — knowledge base | schema, text-based corpus, ingest, static site |
| TypeScript binding | reads the generated dataset, parity-tested against Python |
| Build tooling | `make`, 219 tests (190 Python + 29 TS) |

## Resolved

### Verify the 16 principal figures — `16 of 16` ✓

Done 2026-07-28 against Bascom (1969), Table 1 p. 4 and Table 3 col. B p. 48,
via Internet Archive controlled lending. **All 16 bit patterns and all 16
seniority ranks matched with no corrections.**

Three things came out of it worth keeping:

1. **The untraceable search claim was wrong.** It had Ọ̀sá and Òtúrúpọ̀n
   swapped; Bascom confirms `0111` and `0010` as this dataset had them.
   Declining to act on an unattributable source was the right call.
2. **Seniority is genuinely contested and now documented.** Bascom found 86
   lists from 61 sources: this order is predominant at 42 of 86, but 21 other
   rankings exist. His own study uses the Ifẹ variant, now recorded in
   `alternativeOrders`.
3. **Bascom's name forms are recorded** as `attestedNames` — notably **Edi**
   for Òdí. He omits tone marks throughout.

The tradition label is now `southwestern-yoruba`, Bascom's own term, rather
than the vaguer `yoruba-nigerian`. Spec bumped to `1.0.0`.

## Settled 2026-07-29

| Item | Outcome |
|---|---|
| Leg order | **Corroborated.** Bascom Figure 2 p. 41 numbers the eight marks 1-8 with odd numbers in the right column — the right leg is marked first. First-named = right leg = high nibble holds. |
| Corpus | 36 -> **54** records. A second contents page held 18 entries missed on the first pass. |
| Second source | Not obtained. `docs/second-source-enquiry.md` has a drafted enquiry and three routes. |
| `disputed` path | Now exercised end to end by a test. |
| Contributor model | Documented template in `kb/content/contributors.json`. No fabricated consent. |
| Citation | `CITATION.cff`, citing Bascom alongside the dataset. |
| Versioning | `CHANGELOG.md`, including the corrections made along the way. |
| Data licence | `LICENSE-DATA.md` — MIT code, CC BY-SA compilation, nothing claimed over the verses. |
| Yorùbá interface | `lang="yo"` on every Yorùbá string (512 across the site). Translation deliberately deferred — see `docs/decisions.md`. |

### The one caveat on leg order

Figure 2 proves the *marking* order: right column first. The step from "marked
first" to "named first" rests on the naming convention and was not read
verbatim from Bascom's text. That is a materially stronger position than the
bare assumption it replaces, and the residual gap is stated in
`build_bascom_content.py` rather than hidden.

## Also done (2026-07-28)

| | |
|---|---|
| Corpus | 54 sourced verse citations, 54 attested compound names, 9 sources |
| Phase 4 | `odu_core.generative` + `site/art.html` — 256 figures drawn and playable |
| CI | `.githooks/pre-commit` active; GitHub Actions green on every push |
| Phase 5 | All six scripts in `docs/scripts/`, plus a shot runbook |
| Packaging | Both at 1.0.0, tracking the data spec. Registries still untouched. |

## Still open

### Published — no longer open

The repository is public at `github.com/timeyinallout-cloud/odu-core`, v1.0.0
is released, and Zenodo has minted
[`10.5281/zenodo.21743991`](https://doi.org/10.5281/zenodo.21743991). CI runs
on every push. PyPI and npm remain deliberately untouched — see `RELEASING.md`
for the checklist and the two open questions (npm scope, PyPI name).

### The remaining 202 compound names — not obtainable from Bascom

54 of 256 are sourced and reach `data/odu_256.json`. **The other 202 are not
in Bascom's book at all.** His contents index the figures he published verses
for — 54 of 256 — and the contracted forms appear only in that list. Paging
through pp. 140–563 would revisit the same 54 headings.

So this needs a different source, and no legitimate one has been found. The
contracted names are lineage-specific, which is why they must be sourced
rather than derived: the elision that turns *Ogbe Ọyẹku* into *Ogbe Yẹku* is
a spoken convention, not a spelling rule that can be applied mechanically.

`traditionalName: null` on the other 202 is therefore a true statement about
the evidence, and should stay until a source exists.

### A second independent source — the real remaining weakness

Everything verified so far rests on **one book**. Bascom is careful and shows
his working, but a single source is a single point of failure for a project
whose whole claim is provenance.

Abimbola is the obvious counterweight — he was himself a babaláwo, which
Bascom was not. Two candidates:

- *Ifá: An Exposition of Ifá Literary Corpus* (1976) — not found on the
  Internet Archive; would need a library.
- *Sixteen Great Poems of Ifá* (1975) — **checked; UNESCO is not the
  publisher.** The UNESDOC record (ark:/48223/pf0000019827) gives the imprint
  as *Niamey: OAU Centre for Linguistic and Historical Studies by Oral
  Tradition, 1975*, with the note "Pub. with the financial assistance of
  UNESCO". UNESCO funded it, the OAU published it — so its open-access policy
  does not apply, and UNESDOC itself states "Full-text not available".
  Widely miscited as "UNESCO 1975", including in academic bibliographies.

  Legitimate routes remain: `library@unesco.org` and `archives@unesco.org`
  (the addresses UNESDOC gives), CELHTO directly, or a library holding call
  number `896(662.1) ABI`. The archive.org scan stays unused.

### Verses themselves — still `0`

#### Why they are still zero

Cannot be done from the internet. No public-domain or openly-licensed ẹsẹ Ifá
corpus exists; every collection found is commercial and in copyright. The
schema handles this — copyrighted sources are stored as page references rather
than reproduced text — but producing those references needs the books.

Four real sources are now recorded (Bascom, Abimbola, UNESCO ICH, Olagunju et
al.) with verified citations and correct rights metadata. Zero contain verses.

**Next step:** ten citation-only records from one source. Ten, not a hundred —
the schema has never processed a real verse, and every design decision in it is
untested against reality while changing it is still cheap.

## Not blocked

### Phase 5 — content

Plan written: `docs/content-plan.md`. Six episodes, none dependent on
verification. The strongest is episode 3, the failed verification attempt above.

### CI — ~20 minutes

Nothing runs `make check`. A GitHub Actions workflow running both suites plus
`odu verify` would turn the verification gap into a visible red badge instead of
something to remember. `odu verify` already exits non-zero while incomplete.

### Phase 4 — generative art and music

Safe to start **with one restriction**: bit patterns are structurally certain,
names are not. Build visuals and rhythms keyed to patterns; do not label output
with figure names until verification is done.

## Known limitations

- **Compound names.** All 240 non-méjì figures carry descriptive
  `"<right> <left>"` names and `traditionalName: null`. Contracted forms vary by
  lineage and must be sourced, never generated.
- **One tradition only.** Seniority is Yorùbá/Nigerian. Lucumí ordering differs.
  Adding it means a field in the canonical JSON, not new logic — the library
  indexes by bit pattern precisely so this stays cheap.
- **Native TS stripping needs Amaro.** Distro Node builds often lack it. Check
  `node -p 'process.config.variables.node_use_amaro'`.
- **Build via `npm run build` or `make`, never bare `tsc`** — a post-compile step
  fixes declaration import extensions, and skipping it ships types no consumer
  can resolve. Guarded by `ts/test/dist.test.js`.
