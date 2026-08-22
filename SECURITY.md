# Security

## What is actually at risk here

This is a dataset and two small libraries with no network calls, no
credentials, and no server. The realistic risks are not the usual ones:

**Data integrity is the real threat model.** The damage a bad actor could do is
not to run code on your machine — it is to quietly change what the dataset says
an Odù is. A wrong bit in `data/principal_odu.json` propagates to all 256
figures and to every downstream consumer, silently.

This is why the repo verifies rather than trusts: a pre-commit hook runs the
Python and TypeScript suites, validates content, checks documented claims, and
requires 16 of 16 principal figures to verify against their sources. A pull
request that changes data and passes those gates has done real work; one that
disables them is the thing to be suspicious of.

## Reporting

**Do not open a public issue for a security problem.** Use GitHub's private
vulnerability reporting on this repository, or contact the maintainer via the
address in [`CITATION.cff`](CITATION.cff).

Include what you found, how to reproduce it, and what you think the impact is.
You will get an acknowledgement; if the report is valid you will be credited in
`CHANGELOG.md` unless you ask otherwise.

## Supported versions

The latest released version is supported. Given the nature of the project, a
data correction is more likely than a patch release — corrections land on
`main` and are described in `CHANGELOG.md`.

## Scope

In scope: anything that lets a consumer of this package get a wrong answer they
would reasonably trust — corrupted data, a bypassed verification gate, a
packaging or supply-chain problem in the published PyPI or npm artifacts.

Out of scope: disagreements about tradition, orthography, or seniority
ordering. Those are corrections, not vulnerabilities — open an issue using the
correction template.
