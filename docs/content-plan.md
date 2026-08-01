# Phase 5 — content plan

Runs in parallel with everything else. Nothing here waits on verification, and
the honest state of the project is better material than a finished one would be.

## The framing that holds it together

Not *"look what I built."* The build is not the story — the **evidence problem**
is. Every episode is the same shape: here is a claim about Ifá that sounds
astonishing, here is what happens when you try to check it.

That framing does three things a hype framing cannot. It survives being wrong.
It is welcome among practitioners, because it treats the tradition as something
with authority rather than something to mine for a metaphor. And it produces
content whether the answer is yes or no.

---

## 1. "Your ancestors invented the byte" — and the asterisk

**Hook.** 2⁸ = 256. Ifá has exactly 256 Odù, each figure eight marks, each mark
one of two values. That is not *like* a byte. It is a byte.

**The turn.** The mapping is real and it is exact. What is *not* settled is
which byte value belongs to which name — that depends on conventions nobody
standardised, and on a seniority order that varies by lineage.

**Demo.** `odu show 44`, `odu encode --text "Ifá"`.

**Why this one is first.** It is the strongest claim in the project and the
easiest to overstate. Getting the asterisk in early buys credibility for
everything after it.

---

## 2. The ordering nobody expects

**Hook.** Ogbè is the most senior Odù. Its bit pattern is `1111 1111` — byte
255. Numerically last, traditionally first.

**Body.** Seniority order and binary order are genuinely different orderings of
the same 256 figures, and neither follows from the other by arithmetic. This is
the single design decision the whole library turns on: index by **bit pattern**,
which is structural and uncontested, and treat seniority as an *attribute*,
because it varies between traditions.

**The general lesson.** When you digitise a tradition, the thing you choose as
the primary key is the thing you are claiming is beyond dispute. Choose wrong
and every downstream record inherits a position you did not know you were
taking.

---

## 3. I tried to verify my own dataset and nearly got fooled

**This is the strongest episode. Lead with it if the channel is technical.**

**Hook.** 219 passing tests. A published library, a CLI, a knowledge base, two
language bindings. All of it derived from 16 rows I had never checked.

**Body — what actually happened, in order:**

1. Structural tests pass: the 16 legs cover every 4-bit value exactly once, and
   every consecutive seniority pair is a bitwise complement or reversal. That
   catches transcription errors. It cannot establish that the table matches
   tradition.
2. The best citable source found is a peer-reviewed paper that represents the
   16 as 4×2 binary matrices — gold open access, and **unreadable**: CAPTCHA on
   the publisher, no mirror hosting the PDF.
3. A search engine returned specific patterns that disagreed on exactly two
   figures, Ọ̀sá and Òtúrúpọ̀n. Following it up: **none of the pages contained
   those patterns.** The claim traced to no source at all.
4. Nothing was changed. Status stayed `unverified` — a true statement — rather
   than becoming `disputed` on an unattributable claim.
5. Bascom was then borrowed through the Internet Archive. All 16 matched,
   including the two the phantom claim disputed. It reached `16 of 16`.
6. It happened twice more — a miscitation repeated in academic
   bibliographies, and a library catalogue pointing at the wrong book. Then
   a Yorùbá speaker corrected a reading of the naming that verification had
   not caught, because it was a language question rather than a source one.

**The point.** The most important line of code in the project is the one that
refuses to store a verse without a source. Not because it prevents laziness,
but because I nearly got caught by a confident summary of nothing, and the only
reason I did not is that the schema had no field for *"I read it somewhere."*

**Why it matters beyond Ifá.** This is what digitising oral tradition actually
looks like: the infrastructure is the easy part, and there is enormous pressure
to fill the database because empty looks like failure. Empty is not failure.
Wrong is failure.

---

## 4. Why the corpus is empty on purpose

**Hook.** A knowledge base with 256 pages and zero verses.

**Body.** Ẹsẹ Ifá is living practice, not a dead archive. Some of it is
initiation-restricted. Most published collections are in copyright. So the
schema has a shape that reflects those facts rather than fighting them:

- `source_id` is `NOT NULL` — an unattributed verse fails to insert.
- A source can be citable without being republishable. Copyrighted material is
  stored as a page reference, never as reproduced text.
- Consent is per contributor and withdrawable, and withdrawal propagates to the
  next build.

**Demo.** Show the consent gate: publish a verse, withdraw consent, rebuild, and
the text disappears while the citation survives.

**The line worth landing.** Publication is default-deny. Forgetting a step hides
a record; it never exposes one. When the material is somebody's living religion,
that is the only direction the failure is allowed to point.

---

## 5. Eight bits per figure, and why that is not a wallet

**Hook.** A 32-byte key becomes 32 Odù names. It looks exactly like a seed
phrase.

**Body.** And it should not be used as one. Each figure carries 8 bits where a
BIP-39 word carries 11. BIP-39 is specified, audited, and interoperable; this is
not. The checksum catches typos, but it is not encryption and adds no entropy.

**Why make the episode at all.** Because the demo is genuinely beautiful and
somebody will build the unsafe version. Better that the first result explains
the limit than that it sells the idea.

---

## 6. The figures already tell you the rhythm

Double and single marks map to drum strokes almost too neatly: one mark, one
strike; two marks, two. Nothing is invented — the rhythm is transcribed.

Written before verification, this episode carried a restriction: build from
bit patterns, never label output with a figure's name. **That restriction is
lifted.** Names, ranks and patterns are all sourced now, which is worth saying
on camera — it is the reason this episode comes last.

---

## Production notes

- Every episode ends on the current verification count. It reached `16 of 16`
  on 28 July 2026; the count that still moves is names, at 54 of 256.
- Never show a verse on screen that is not sourced on screen.
- The repository is the receipt. Say what is unsourced before anyone asks —
  202 of the 256 figures still have no attested name, and that is the honest
  number, not an embarrassing one.
