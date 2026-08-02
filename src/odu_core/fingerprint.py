"""Short file fingerprints you can say aloud or hear.

Two people holding what should be the same file want to know whether it is.
Comparing SHA-256 hex down a phone is miserable — sixty-four characters with no
rhythm, easy to lose your place in, and easy to agree on by accident because
neither of you is really reading. Four Odù names take a couple of seconds to
say, and the fourth is a checksum, so a mistranscription is caught rather than
silently accepted.

The same bytes drive a drum pattern on the web page, which is the point of the
exercise: you can compare two files by ear.

WHAT THIS IS NOT
================
A three-byte fingerprint is 24 bits. A collision can be found by chance in
about 4,000 tries and by brute force in 16 million — trivial for a computer.

So this detects **accidents**: a truncated download, the wrong take uploaded,
a file that silently changed on disk. It does **not** detect tampering, and
must never be used where someone might benefit from forging a match. For that,
compare the full digest.

The length is configurable, and `odu fingerprint --bytes 16` gives a 128-bit
fingerprint that is no longer forgeable by brute force — but it is seventeen
figures long and nobody is saying that down a phone. The short form is the
useful one precisely because it is short, and its limits come with that.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO, Iterable

from .mnemonic import Style, format_phrase, to_phrase
from .types import Odu

# Enough to be worth saying, short enough to be worth hearing. Three payload
# bytes plus the checksum figure is four figures.
DEFAULT_BYTES = 3

# Read in blocks so a multi-gigabyte render does not have to fit in memory.
_CHUNK = 1 << 20


def digest(source: str | Path | bytes | bytearray | BinaryIO,
           *, length: int = DEFAULT_BYTES) -> bytes:
    """The first `length` bytes of the SHA-256 of `source`.

    Accepts a path, raw bytes, or an open binary file. Truncating a standard
    digest rather than inventing one means anyone can reproduce this with
    `sha256sum | cut`, with no reference to this library.
    """
    if length < 1:
        raise ValueError("a fingerprint needs at least one byte")
    h = hashlib.sha256()
    if isinstance(source, (bytes, bytearray)):
        h.update(source)
    elif isinstance(source, (str, Path)):
        with open(source, "rb") as fh:
            for block in iter(lambda: fh.read(_CHUNK), b""):
                h.update(block)
    else:
        for block in iter(lambda: source.read(_CHUNK), b""):
            h.update(block)
    return h.digest()[:length]


def fingerprint(source: str | Path | bytes | bytearray | BinaryIO,
                *, length: int = DEFAULT_BYTES) -> tuple[Odu, ...]:
    """The figures for `source` — payload figures plus a checksum figure."""
    return to_phrase(digest(source, length=length))


def say(source: str | Path | bytes | bytearray | BinaryIO,
        *, length: int = DEFAULT_BYTES, style: Style = "display") -> str:
    """The fingerprint as text.

    Defaults to `display` — full Yorùbá orthography — because the whole point
    is reading it aloud. Use `slug` when it has to be typed or pasted.
    """
    return format_phrase(fingerprint(source, length=length), style)


def strokes(figures: Iterable[Odu]) -> list[list[int]]:
    """Drum onsets per figure, as sixteenth-note positions.

    Delegates to `generative.to_rhythm`, which is the one place the bit
    pattern becomes a rhythm — so a fingerprint always sounds exactly like the
    same figures on the art page, and stays that way if the mapping is ever
    revised. See docs/DECISIONS.md §5.
    """
    from .generative import to_rhythm
    return [list(to_rhythm(odu).onsets()) for odu in figures]


def matches(a: str | Path | bytes, b: str | Path | bytes,
            *, length: int = DEFAULT_BYTES) -> bool:
    """Whether two sources share a fingerprint.

    Convenience for scripts. A True here means "probably the same file"; for
    certainty compare the full digest.
    """
    return digest(a, length=length) == digest(b, length=length)
