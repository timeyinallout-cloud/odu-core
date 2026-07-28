# Episode 2 — "The most senior figure is numerically last"

**Length** ~5 min · **Shots**: terminal, Bascom pp. 47–48, the seniority module

---

**[0:00 — cold open]**

> Ogbè is the most senior Odù. First in the order, the one the others answer to.
>
> Its bit pattern is all ones. Eleven-one-one-one-one-one-one-one.
>
> Which makes it byte two hundred and fifty-five. Dead last.

**[0:25 — the collision]**

*Visual: `odu table`, then sort by byte.*

> Two orderings of the same 256 things. Traditional seniority, and numeric
> order. And neither one follows from the other by any arithmetic you can do
> on the byte.
>
> Ogbè is 255 and first. Ọ̀yẹ̀kú is 0 and second. Then Ìwòrì at 6, Òdí at 9,
> Ìrosùn at 12. There's no pattern. There isn't meant to be one — the order is
> cultural, the number is structural, and they were never designed to agree.

**[1:10 — the design question]**

> So if you're building a database of this, you have to pick a primary key.
> And that choice is not a technical detail. It's a claim about what you think
> is beyond dispute.
>
> Key on the rank, and you're asserting the order is settled.

**[1:40 — what Bascom found]**

*Visual: page 47.*

> Bascom examined eighty-six lists of the sixteen figures, drawn from
> sixty-one sources — Yoruba, Fọn, Ewe, Cuban, Brazilian.
>
> One order was predominant. Forty-two of the eighty-six.
>
> That's less than half.

*Beat.*

> He recorded **twenty-one other rankings.** Some he thought were simply
> errors. But others tracked regions — the northeast around Ifẹ, Ilẹṣa and
> Ekiti ordered differently from Lagos, Abẹokuta and Ibadan in the southwest.

**[2:30 — the twist]**

*Visual: Table 3, page 48, both columns.*

> And here's the part I like. Bascom's own book doesn't use the dominant order.
> He follows the Ifẹ variant — given to him by four Ifẹ diviners.
>
> So the single most-cited source on Ifá numbers its 256 figures in an order
> that most of its own evidence disagrees with. He says so plainly. He just
> doesn't make a fuss about it.

*Visual: the two columns side by side, differences highlighted.*

> Look at what actually moves. Positions five through eight swap as a pair.
> Eleven through fourteen swap as a pair.
>
> And the bit patterns? Identical. Every figure has the same four marks in both
> columns. Only the ranking moves.

**[3:20 — the payoff]**

> That's the whole argument for the design.
>
> The structure is uncontested — sixteen figures, four lines, two states, one
> byte. The *order* is contested by at least twenty-two traditions.
>
> So index on the structure. Make seniority an attribute.

*Visual: `seniority.py`, the TRADITION constant.*

> In this library, adding Bascom's Ifẹ order was adding a field to a JSON file.
> No migration. No renumbering. Nothing downstream moved, because nothing
> downstream was ever keyed on the rank.
>
> Had I numbered them one to sixteen and keyed on that, adopting his ordering
> would have silently repointed every record in the database — and every test
> would still have passed, because the tests check the code, not the world.

**[4:20 — close]**

```
odu show 255
Èjì Ogbè
  byte        255 (0xFF, 11111111)
  seniority   1 of 256
```

> First and last, at the same time, and both are correct.
>
> When you digitise a tradition, the thing you pick as the key is the thing
> you're declaring settled. Pick the part that nobody argues about.

---

## Notes

- Resist calling the variants "wrong." Bascom doesn't, and the regional
  pattern is evidence they're real.
- Good place to mention that Lucumí ordering is a further open question the
  schema is ready for but which nothing in this project has sourced yet.
