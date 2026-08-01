# Periodic claim audit

`scripts/check_claims.py` runs on every commit and every push. It catches
numbers that have gone wrong and a short list of phrases that were true once.
It cannot read.

This is the part that needs a person, or an agent with judgement. Roughly
monthly, or after any stretch of heavy work.

## Why this exists

On 2026-08-01 an audit found ten stale claims. `RELEASING.md` opened with
"nothing here is published yet" after the repository had been public for days.
`docs/content-plan.md` summarised episode 3 with an ending the story had
already moved past, and told the reader not to label generated output with
figure names — a restriction verification had lifted.

None of that was catchable by a test. Every file was internally consistent and
every generated artifact matched its source. The sentences had simply stopped
being true.

## What to check

**Tense and status.** Anything phrased as *not yet*, *deferred*, *planned*,
*still open*, *pending*. These age fastest. Grep for them and read each hit.

**Superseded decisions.** A document explaining why something is *not* done is
worse than useless once it is done — it actively misleads. `ROADMAP.md`,
`RELEASING.md` and `docs/decisions.md` are the usual offenders.

**Restrictions that were lifted.** Constraints written under uncertainty stay
written after the uncertainty resolves. The naming restriction in episode 6 sat
there for a week after verification removed its reason.

**Narrative summaries.** `docs/content-plan.md` and `docs/scripts/*.md` retell
the project's own history. When the history gains a chapter, the retellings do
not update themselves.

**Counts the checker does not know about.** Add any new one to `CLAIMS` in
`check_claims.py` rather than leaving it unwatched.

## What not to touch

Some things look stale and are not:

- **`verification.history` in `data/principal_odu.json`** — a record of what was
  attempted and failed. Rewriting it would defeat its purpose.
- **`CHANGELOG.md`** — historical by design.
- **The Abimbola 1976 note** saying publication details are unverified. Still
  true; that book has never been consulted.
- **Byte values that happen to equal a stale-looking number.** 169 and 221 are
  real seniority ranks.

## Running it

```sh
make claims          # the mechanical subset
git grep -niE "not yet|deferred|planned|still open|pending|for now" -- '*.md'
```

Then read the hits. The question for each is not *is this well written* but
**was this true when written, and is it true now**.
