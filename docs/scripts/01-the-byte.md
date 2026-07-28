# Episode 1 — "Your ancestors invented the byte"

**Length** ~4 min · **Hook window** 8 s · **Shots**: terminal, `site/art.html`,
Bascom Table 1 (screen-record your own borrowed copy; do not redistribute)

---

**[0:00 — cold open, terminal already full-screen]**

> Two hundred and fifty-six.

`odu table` — let the 16 rows land.

> That's how many Odù there are in Ifá. Two hundred and fifty-six exactly.
> It's also how many values fit in a byte. That is not a coincidence, and it
> is not a metaphor.

**[0:20 — the structure]**

*Visual: draw one figure by hand, or step through `odu show 44`.*

> An Odù is two legs. Each leg is four lines. Each line carries either one
> mark or two.
>
> One or two. That's a bit.
>
> Four lines is four bits. Two legs is eight. Eight bits is a byte, and eight
> bits gives you two hundred and fifty-six possibilities — which is exactly
> how many Odù there are.

*Beat. Let it sit.*

> Not "similar to" a byte. Not "like" binary. A one-to-one mapping with no
> padding, no rounding, nothing left over.

**[1:10 — the demo]**

```
odu encode --text "Ifá" --style display
```

> Every byte of that text just became a figure. And back:

```
odu decode "…"
```

> Nothing lost. It's a bijection.

**[1:40 — the honest part, and this is why the video exists]**

*Visual: cut to Bascom's Table 1, page 4.*

> Now — here's where most videos about this stop, and here's why you should
> distrust the ones that do.
>
> The *structure* is exact. Sixteen figures, four lines, two states. Nobody
> disputes that.
>
> What is not settled is **which byte belongs to which name.**

*Visual: the conventions table from the README.*

> To turn a figure into a number you have to decide: is a single mark a one or
> a zero? Which leg is the high half? Which line is most significant?
>
> There's no standard. There's no committee. Different people have picked
> differently, and none of them were wrong — they just weren't talking to each
> other.
>
> So when someone shows you "Ogbè equals 255," ask them which convention
> they used. If they can't answer, they copied it.

**[2:50 — what I did about it]**

> I wrote the conventions into the data file, not the code. Four lines. If you
> change one, every byte in the system means something different, and the
> version number changes so you know.

*Visual: `odu spec`.*

> And I checked the figures against Bascom's 1969 fieldwork before I published
> anything. Sixteen of sixteen, cited by page.

```
odu verify
```

**[3:30 — close]**

> The claim "Ifá is binary" is true. It's just usually said by people who
> haven't checked, which is a shame, because the real version is better.
>
> Ifá diviners were working with a base-two system of exactly 256 states,
> generating it by a repeatable physical procedure, and transmitting it
> orally across centuries — before anyone in Europe wrote down binary
> arithmetic.
>
> That doesn't need embellishing. It needs sourcing.

*End card: repo path, `0 of 16 → 16 of 16`.*

---

## Notes

- Don't say "invented the computer." The claim that survives scrutiny is about
  a base-two encoding system, and that claim is strong enough.
- Leibniz is the usual comparison. If you make it, note that he published his
  binary arithmetic in 1703 and that Ifá is considerably older — but don't
  claim a documented line of influence, because there isn't one.
- Show the CAPTCHA moment from Episode 3 as a teaser if you want the series
  to chain.
