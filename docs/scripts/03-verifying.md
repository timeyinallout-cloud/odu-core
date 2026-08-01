# Episode 3 — "I tried to verify my own data and nearly got fooled"

**The strongest one. Lead the series with it if the audience is technical.**

**Length** ~9 min · **Shots**: terminal, search results, the CAPTCHA, the
YouTube Short, Bascom pp. 4 / 47 / 48

---

**[0:00 — cold open]**

*Visual: `make test` running green.*

> Two hundred and sixteen passing tests. A published library, a command-line
> tool, a knowledge base, two language bindings.
>
> All of it derived from sixteen rows in one file.
>
> Sixteen rows I had never checked.

**[0:25 — the setup]**

*Visual: `data/principal_odu.json`, scrolling.*

> This is the whole foundation. Sixteen figures, four marks each. Everything
> else in the project is generated from it — all 256 combinations, every byte
> value, every page of the site.
>
> If one of these rows is wrong, everything downstream is wrong, and every
> test still passes. Tests check that the code does what I said. They cannot
> check whether what I said is true.

**[1:00 — the structural checks, and their limit]**

*Visual: the two invariant tests.*

> I had two things going for me. The sixteen legs cover every four-bit value
> exactly once — if two figures shared a pattern the whole mapping would
> collapse. And every consecutive pair in the traditional order is either a
> mirror image or an exact inversion of its partner.
>
> Both hold. Both are real signals. And neither one proves the table matches
> tradition — they'd hold just as well for a table that was *consistently*
> wrong.

**[1:45 — attempt one: the paper]**

*Visual: the ScienceDirect page, then the CAPTCHA.*

> So I went looking for a source. The best one is a peer-reviewed paper that
> represents the sixteen figures as binary matrices. Open access. Free to read.
>
> And completely unreachable. CAPTCHA on the publisher, no mirror anywhere.
> An open-access paper I could not open.

**[2:20 — attempt two: the trap]**

*Visual: the search result, patterns highlighted.*

> Then a search gave me a straight answer. Sixteen figures, sixteen patterns.
>
> Fourteen of them matched my table exactly. Two didn't — Ọ̀sá and
> Òtúrúpọ̀n, swapped.

*Beat.*

> Now think about how convincing that is. If it had disagreed with everything,
> I'd have dismissed it. Fourteen out of sixteen looks like a careful source
> catching a small mistake. I was about to flag both figures as disputed.

**[3:00 — the check that saved it]**

*Visual: opening each cited page in turn, finding nothing.*

> Before changing anything I opened the pages it cited.
>
> The first one didn't contain the patterns. Neither did the second. Neither
> did the third.
>
> The claim came from nowhere. It was a summary of sources that didn't say it.

*Beat.*

> So I changed nothing. I wrote down that the attempt failed and left all
> sixteen marked unverified — because "unverified" was true, and "disputed"
> would have been a lie dressed as diligence.

**[3:50 — the near-miss is the point]**

> Here's what I want you to take from that.
>
> The most important rule in this project is that nothing gets stored without
> a source. I wrote it as a database constraint — a column that cannot be
> null — and I described it as being about rigour.
>
> It isn't. It's about *me*. It stopped me, personally, from writing down
> something confident and false, because there was nowhere to put "I read it
> somewhere."

**[4:30 — resolution]**

*Visual: archive.org, borrowing the book. Then page 4.*

> The book was on the Internet Archive the whole time. Free account, lending
> copy.
>
> Table 1, page 4. The sixteen basic figures of Ifá.

*Visual: linger on the table.*

> All sixteen matched. Including Ọ̀sá and Òtúrúpọ̀n — exactly as I had them.
> The confident summary was simply wrong.

**[5:15 — the bonus, which is better than the verification]**

*Visual: page 47.*

> And then page forty-seven told me something I didn't know I needed.
>
> Bascom examined eighty-six lists of the sixteen figures, from sixty-one
> sources. He found one order predominant — forty-two of the eighty-six.
>
> And **twenty-one other rankings.**

*Visual: Table 3, the two columns side by side.*

> There isn't one order. There are at least twenty-two, and they map to
> regions — the northeast orders differently from the southwest. His own book
> uses a variant that isn't the dominant one.
>
> The bit patterns are identical in both. Only the ranking moves.

**[6:10 — why that vindicates an early decision]**

*Visual: the seniority module.*

> Right at the start I made one architectural call: index everything by the
> **bit pattern**, and treat seniority rank as an attribute rather than a key.
>
> Structure is settled. Ordering is contested. So don't key your data on the
> contested thing.
>
> If I'd numbered the figures one to sixteen and keyed on that, adopting
> Bascom's own ordering would have silently repointed every record in the
> database — and every test would still have passed.

**[6:45 — it happened twice more]**

*Visual: the UNESCO catalogue record, then the Internet Archive item page.*

> That would be a decent story if it happened once. It happened three times in
> a week.
>
> A book everyone cites as "Abimbola 1975, UNESCO" — including published
> academic bibliographies. UNESCO's own catalogue says the publisher was the
> Organisation of African Unity in Niamey. UNESCO funded it. That distinction
> decides whether it's openly licensed, and it isn't.
>
> And an Internet Archive item catalogued as Bascom's *Sixteen Cowries*. I
> borrowed it. The scan is a different book entirely — same publisher, same
> year, different title. If I'd trusted the catalogue I'd have cited page
> numbers from a book I never opened.

**[7:30 — the one I couldn't catch]**

> Then, after all sixteen figures were verified against a primary source, I got
> the naming wrong anyway.
>
> Bascom writes the compound names with a letter in parentheses. I read the
> parenthesis as deletion — the vowel is dropped. I wrote a confident
> explanation of why that reading was correct.
>
> It marks the vowel as *optional*. Elided in speech, present in the name. A
> Yorùbá speaker told me, and he was right.

*Beat.*

> I had a primary source, a verification workflow, two hundred tests, and I
> still encoded an inference as a fact — because I was reading a tone language
> I don't speak.
>
> No amount of infrastructure substitutes for someone who knows the thing.

**[8:15 — close]**

```
odu verify
16 of 16 figures verified against a source
```

> Sixteen of sixteen, cited by table and by page. It's public now, and the
> tests run on every push.
>
> Two hundred and two of the two hundred and fifty-six figures still have no
> traditional name. There are no verses at all. Those are nulls that mean *no
> source found* — not gaps waiting to be filled.
>
> The infrastructure took a fortnight. The sixteen rows took the whole project.
> That ratio is what digitising oral tradition actually looks like, and the
> pressure to fill an empty database because empty looks like failure is
> constant.
>
> Empty isn't failure. Wrong is failure.

---

## Notes

- Screen-record Bascom from your own borrowed copy. Show the table; don't
  publish the scan.
- The near-miss is the spine. Don't soften it — the fact that it was
  *convincing* is the whole lesson.
- Credit the Internet Archive explicitly. Controlled lending is what made this
  possible.
