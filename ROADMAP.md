# What's left

Status as of 2026-07-28. Phases refer to the original five-phase plan.

## Done

| | |
|---|---|
| Phase 1 — core library | Python, canonical JSON, 256 figures, seniority |
| Phase 2 — mnemonic encoder | checksummed phrases, `odu` CLI, browser demo |
| Phase 3 — knowledge base | schema, text-based corpus, ingest, static site |
| TypeScript binding | reads the generated dataset, parity-tested against Python |
| Build tooling | `make`, 158 tests (129 Python + 29 TS) |

## Blocked on a physical source

### Verify the 16 principal figures — `0 of 16`

**This blocks nothing technically and everything epistemically.** Every artifact
in the repository derives from `data/principal_odu.json`. If a figure is wrong,
the 256 pages, the phrases, and the TS fixture are all wrong.

Web verification was attempted on 2026-07-28 and **failed**:

- The best citable source, Olagunju et al. (2023), represents the 16 as 4×2
  binary matrices. It is gold open access but CAPTCHA-gated at the publisher,
  and no mirror hosts the PDF. It is recorded in the corpus as a source with a
  `NOT YET CONSULTED` note.
- A search-engine summary asserted patterns conflicting with this table for
  **Ọ̀sá** and **Òtúrúpọ̀n**. Every page it pointed at was checked; none
  contained those patterns. The claim was untraceable and was not acted on.
- Structural checks still hold and are enforced by tests: the 16 legs cover
  every 4-bit value exactly once, and every consecutive seniority pair is a
  bitwise complement or bit-reversal. Those catch transcription errors, not
  wrongness.

**What would finish it.** One person, one afternoon, one of:

1. Olagunju et al. (2023), `doi:10.1016/j.sciaf.2023.e01729` — open access, just
   needs a human past the CAPTCHA. Cheapest route by far.
2. Bascom, *Ifa Divination* (1969), Table 1 — Internet Archive controlled
   lending, or any university library.
3. Abimbola (1976).

Record each with:

```sh
python3 scripts/verify_odu.py ogbe --against "Bascom 1969, Table 1, p. 44" --by "Name"
python3 scripts/verify_odu.py --status
```

**Video was tried on 2026-07-28 and is a real lead.** A hand-drawn chart of
all 16 in a YouTube Short was legible enough to read 10 figures, and all 10
agree with this table — including **Ọ̀sá (`0111`) and Òtúrúpọ̀n (`0010`)**, the
pair the untraceable claim had swapped. That contradicts the phantom claim but
does not verify anything: the source is an anonymous Short and cannot be cited.
Six figures (Ògúndá, Ìká, Òtúrá, Ìrẹtẹ̀, Ọ̀sẹ́, Òfún) were not legible.

Video is worth pursuing further. Ifá is an oral and visual tradition, so a
recorded practitioner drawing the figures is arguably closer to the source than
an anthropologist's transcription. The obstacle is attribution — a citable
record needs a named, checkable person, which a lecture from a named scholar or
an institutional recording would give and an anonymous Short does not.

**Check Ọ̀sá and Òtúrúpọ̀n first.** They are the two an unverified claim
disputed, so they are where a real error is most likely to be hiding. If a
source disagrees, mark `--dispute` rather than editing the table.

### Enter real verses — `0 verses`

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

### Push to a remote — 5 minutes, do this first

Six commits, no remote, one copy on one laptop. A preservation project that
exists in exactly one place is one disk failure from nothing.

```sh
gh repo create odu-core --private --source=. --push
```

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
