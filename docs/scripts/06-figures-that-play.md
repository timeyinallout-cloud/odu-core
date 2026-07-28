# Episode 6 — "The figures already tell you the rhythm"

**Length** ~4 min · **Shots**: `site/art.html`, a drum if you have one

---

**[0:00 — cold open]**

*Visual: art.html, click a figure, let it play.*

> I didn't design that rhythm. It was already there.

**[0:20 — the mapping]**

*Visual: one figure, large.*

> Every line of an Odù carries one mark or two.
>
> One mark, one stroke. Two marks, two strokes.
>
> That's the entire mapping. There's no clever encoding, no arbitrary choice.
> The figures are read aloud in rhythm already; this only writes down what the
> marks say.

**[1:00 — the range]**

```
Èjì Ogbè       x x x x | x x x x        8 strokes
Ọ̀yẹ̀kú Méjì    xx xx xx xx | xx xx xx xx   16 strokes
```

> All single marks gives you the sparsest figure — eight strokes. All double
> gives the densest — sixteen. Everything else sits between, and each of the
> 256 has a distinct pattern.

*Visual: play both back to back.*

> The accent falls on the first stroke of each leg, so you can hear where the
> figure divides.

**[1:50 — determinism, and why I care]**

> Nothing here is random. No seed, no noise function, no generation step.
> Every image and every rhythm is a pure function of the eight bits.
>
> Which means this figure sounds the same on your machine as mine, and the
> same in ten years.
>
> That matters more than it sounds. A generated image is only meaningful as
> *this figure's* image if it can't drift. The moment you add randomness you
> have made art *about* Ifá instead of art *of* it.

**[2:40 — the images]**

*Visual: scroll the contact sheet.*

> Same rule for the drawings. Marks are drawn the way a diviner draws them —
> strokes in two columns, right leg on the left of the page — not as an
> abstraction of the bits.
>
> The colours are earth pigments. Iyerosun, the pale wood dust the figures are
> marked in. Ochre, sienna, the wood of the divining tray. Picked from the byte
> value, so they're deterministic too, but spaced so neighbouring figures don't
> look identical.
>
> Deliberately not a rainbow. The figures aren't data visualisation.

**[3:20 — close]**

*Visual: play in seniority order, let it run under the outro.*

> That's all 256, in traditional seniority order. Ogbè first — the one that's
> also byte 255.
>
> Nothing you're hearing was invented. It was transcribed.

---

## Notes

- Web Audio directly, no Tone.js and no CDN — a preservation artifact
  shouldn't stop working because a host went away. Worth one line on screen.
- If you play along on a real drum, say so. The point lands harder when a
  human plays a pattern a 1969 ethnography wrote down.
- Do not label output with figure names unless the names are verified. They
  are now — but say that, because it's the reason this episode is last.
