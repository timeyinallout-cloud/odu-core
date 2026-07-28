# Episode 4 — "A knowledge base with 256 pages and no verses"

**Length** ~5 min · **Shots**: `site/`, the schema, a live consent demo

---

**[0:00 — cold open]**

*Visual: the index, 256 figures. Click into one. Scroll to "Verses". It's empty.*

> Two hundred and fifty-six pages. Zero verses.
>
> That's not unfinished. That's the design.

**[0:25 — why]**

> Ẹsẹ Ifá — the verses — are not an archive. They're living practice. Some are
> initiation-restricted. Most of what's been published is in copyright. And
> the people who hold them are alive and can change their minds.
>
> So the question isn't "how do I fill this database." It's "what shape does a
> database have to be before it *deserves* to be filled."

**[1:00 — rule one]**

*Visual: `kb/schema.sql`, the NOT NULL on source_id.*

> Every piece of content points at a source. Not "should" — the column can't
> be null. An unattributed verse doesn't get flagged for review. It fails to
> insert.
>
> A corpus that can't say where a line came from is worthless. A corpus of
> somebody's living religion that can't say so is worse than worthless.

**[1:40 — rule two: citable isn't republishable]**

*Visual: the failing insert.*

> Bascom's book is in copyright. So I can't store his verses.
>
> But I can store *where they are*. Page 164 to 170, four verses, this figure.

*Visual: a figure page showing a citation with no text.*

> A pointer to where a verse lives is a real contribution. Reproducing it is a
> copyright violation. The schema knows the difference — try to store the text
> from a restricted source and it refuses, with a message telling you to use a
> page reference instead.

**[2:30 — rule three: consent is a live wire]**

*Visual: the demo. Publish a contributed verse. Show it on the page.*

> Say someone contributes a verse and consents to it being published. Here it
> is on the site.
>
> Now they change their mind.

*Visual: flip consent to withdrawn. Rebuild. Refresh.*

> Gone. Next build, it's gone — and I didn't have to remember to remove it.
> The publication view checks consent every time it runs.

**[3:15 — the direction failure points]**

> Four gates: published, not restricted, source allows reproduction,
> contributor still consents. All four have to be true.
>
> Which means forgetting a step **hides** something. It never exposes
> something.
>
> That's the only direction the failure is allowed to point when the material
> is someone's religion. Most systems default the other way — visible unless
> restricted — because that's easier and it makes the demo look fuller.

**[4:00 — what's actually in there]**

*Visual: `python3 scripts/ingest.py`.*

> Right now: four sources. Thirty-six citations. Nineteen traditional names,
> each with the page it came from.
>
> Zero verses. Because I don't have the right to publish any of them yet, and
> I'm not going to write my own and call them traditional.

**[4:35 — close]**

> Every AI system in the world would happily generate you two hundred and
> fifty-six plausible Ifá verses this afternoon. They'd read well. Some would
> even be close.
>
> And they would poison the thing permanently, because in ten years nobody
> would be able to tell which ones came from a diviner and which came from a
> language model.
>
> The empty database is the feature.

---

## Notes

- Do the consent demo live. Watching text disappear on rebuild lands harder
  than any explanation of the schema.
- If someone asks "why not just add verses from the internet" — the honest
  answer is that no openly-licensed corpus exists. Every collection found was
  commercial and copyrighted. Say that plainly.
