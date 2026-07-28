# Episode 5 — "This looks exactly like a seed phrase. Don't use it as one."

**Length** ~4 min · **Shots**: terminal, `web/index.html`

---

**[0:00 — cold open]**

```
odu random --bytes 32 --style numbered
```

*Let all 32 figures scroll.*

> Thirty-two random bytes, as thirty-two Odù. It round-trips exactly — feed
> the names back, you get the same bytes.
>
> It looks precisely like a crypto seed phrase. And you should not use it as
> one. Let me explain why, because the reasons are more interesting than the
> warning.

**[0:35 — what it does do]**

> Each figure carries exactly one byte, so there's no padding and no waste.
> And there's a checksum figure on the end.

*Visual: transpose two figures, decode, watch it fail.*

```
odu: checksum mismatch: phrase ends with Ìwòrì Òtúrúpọ̀n (0x62) but its
18 payload figures require 0xBD. Usually a mistyped or transposed figure.
```

> Without that, swapping two figures gives you *different bytes, silently*.
> That's the failure mode that makes a mnemonic dangerous — not that it breaks,
> but that it succeeds and hands you the wrong answer.

**[1:20 — reason one: density]**

> BIP-39, the wallet standard, uses a 2048-word list. Eleven bits per word.
>
> There are 256 Odù. Eight bits per figure.
>
> So a 24-word BIP-39 phrase is 264 bits. Twenty-four Odù are 192. To match a
> 256-bit seed you need 32 figures plus a checksum — 33 things to remember
> instead of 24.

**[2:00 — reason two, which matters more]**

> But density isn't the real reason.
>
> BIP-39 is a specification. It's been audited, it's implemented in dozens of
> wallets, and if your hardware dies you can type your words into somebody
> else's software and get your money back.
>
> This is a library I wrote. It has tests, and I verified the data against a
> 1969 ethnography — but there is exactly one implementation of this scheme,
> and it's mine.
>
> If I have an off-by-one in the checksum, nobody catches it. And you find out
> when you need your funds and can't get them.

**[2:50 — the honest framing]**

> The checksum catches typos. It is not encryption, it is not authentication,
> and it adds no secrecy — anyone holding the phrase has the bytes.
>
> So what is it for? Memory. Teaching. Art.
>
> Thirty-two figures with names, images and rhythms attached is a genuinely
> good memory system — better than hex, and considerably more beautiful. Use
> it to memorise something you can afford to lose.

**[3:30 — close]**

*Visual: the warning banner in the web demo.*

> I put that warning in four places: the module docstring, the README, the CLI
> help text, and the top of the demo page.
>
> Not because I expect you to need telling. Because somebody will find this
> repository in three years, think it's a clever idea, and ship it — and I'd
> rather the first thing they read is the limit.

---

## Notes

- Don't be coy. Show the round-trip working, then say plainly not to trust it.
- If asked "but what if lots of people implemented it" — that's the actual
  answer. A second independent implementation and a written spec is the bar,
  and the TS binding deliberately reads the same generated data rather than
  being a second derivation, so it does *not* count.
