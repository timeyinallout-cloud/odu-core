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

## Still blocked on a physical source

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
