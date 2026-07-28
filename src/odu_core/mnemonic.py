"""Checksummed mnemonic encoding: bytes to Odù names and back.

Each Odù carries exactly one byte, so a 32-byte value becomes 32 figures with no
padding. A trailing checksum figure is appended, which is what separates this
from a bare byte-to-name substitution: a single mistyped or transposed figure is
caught on decode instead of silently yielding different bytes.

    >>> phrase = to_phrase(b"hello")
    >>> from_phrase(phrase)
    b'hello'

Read this before using it for key material
------------------------------------------
The checksum detects accidental corruption. It is not authentication, it is not
encryption, and it adds no entropy — a phrase reveals exactly the bytes it
encodes to anyone holding it.

Each figure carries 8 bits, where a BIP-39 word carries 11. A 24-word BIP-39
seed phrase is 264 bits; 24 Odù are 192. Matching a 256-bit seed takes 32
figures plus the checksum. If you are encoding a wallet seed, use BIP-39 — it is
specified, audited, and interoperable across wallets. This module is built for
memory, teaching, and art, and a spec bug here costs real money there.
"""

from __future__ import annotations

import hashlib
import re
from difflib import get_close_matches
from functools import cache
from typing import Iterable, Literal, Sequence

from .core import all_odu, decode, encode, from_legs, principal
from .orthography import normalize, to_ascii
from .types import Odu

__all__ = [
    "to_phrase",
    "from_phrase",
    "format_phrase",
    "parse_phrase",
    "checksum_byte",
    "phrase_bits",
    "ChecksumError",
    "PhraseError",
    "Style",
]

Style = Literal["slug", "display", "numbered"]

CHECKSUM_FIGURES = 1
"""Figures appended for the checksum. One figure is one byte of SHA-256."""

_SEPARATORS = re.compile(r"[·•/,;|\n\r\t]+")


class PhraseError(ValueError):
    """A phrase could not be parsed into figures."""


class ChecksumError(ValueError):
    """A phrase parsed cleanly but its checksum does not match its payload.

    Almost always a transcription error — a swapped, dropped, or mistyped
    figure — rather than a bug.
    """


def checksum_byte(data: bytes) -> int:
    """First byte of the SHA-256 of ``data``.

    One byte gives a 1-in-256 chance of a corrupted phrase slipping through,
    the same order of protection BIP-39 gives a 12-word phrase.
    """
    return hashlib.sha256(data).digest()[0]


def to_phrase(data: bytes | bytearray | Iterable[int]) -> tuple[Odu, ...]:
    """Encode bytes as figures, with a checksum figure appended."""
    payload = bytes(data)
    return encode(payload + bytes([checksum_byte(payload)]))


def from_phrase(phrase: str | Sequence[Odu]) -> bytes:
    """Decode figures back to bytes, verifying the checksum.

    Accepts either parsed figures or any format :func:`format_phrase` produces.
    Raises :class:`ChecksumError` if the phrase is self-inconsistent.
    """
    figures = parse_phrase(phrase) if isinstance(phrase, str) else tuple(phrase)
    # An empty payload is legitimate: it encodes to the checksum figure alone.
    if len(figures) < CHECKSUM_FIGURES:
        raise PhraseError(
            f"a phrase needs at least {CHECKSUM_FIGURES} figure "
            f"(the checksum), got {len(figures)}"
        )

    raw = decode(figures)
    payload, given = raw[:-CHECKSUM_FIGURES], raw[-1]
    expected = checksum_byte(payload)
    if given != expected:
        raise ChecksumError(
            f"checksum mismatch: phrase ends with {figures[-1].name} "
            f"(0x{given:02X}) but its {len(payload)} payload figures require "
            f"0x{expected:02X}. Usually a mistyped or transposed figure."
        )
    return payload


def phrase_bits(figure_count: int) -> int:
    """Bits of payload carried by a phrase of ``figure_count`` figures."""
    return max(0, (figure_count - CHECKSUM_FIGURES)) * 8


def format_phrase(figures: Sequence[Odu], style: Style = "slug") -> str:
    """Render figures as text.

    ``slug`` is the canonical written form — ASCII, one token per figure, safe
    to write down or paste anywhere. ``display`` keeps full Yorùbá orthography
    with a separator, since figure names are themselves two words. ``numbered``
    is for reading aloud and checking position by position.
    """
    if style == "slug":
        return " ".join(f.slug for f in figures)
    if style == "display":
        return " · ".join(f.name for f in figures)
    if style == "numbered":
        width = len(str(len(figures)))
        return "\n".join(
            f"{i:>{width}}. {f.name}" for i, f in enumerate(figures, 1)
        )
    raise ValueError(f"unknown style {style!r}")


@cache
def _figure_index() -> dict[str, Odu]:
    """Every figure keyed by slug and by name, diacritic and ASCII-folded."""
    index: dict[str, Odu] = {}
    for o in all_odu():
        index[o.slug] = o
        index[normalize(o.name)] = o
        index[to_ascii(o.name)] = o
    return index


def parse_phrase(text: str) -> tuple[Odu, ...]:
    """Parse any format :func:`format_phrase` produces back into figures."""
    stripped = _SEPARATORS.sub(" ", text).strip()
    # Drop "1." / "12)" position markers so numbered phrases round-trip.
    stripped = re.sub(r"\b\d{1,3}[.)]\s*", "", stripped)
    if not stripped:
        raise PhraseError("phrase is empty")

    tokens = stripped.split()
    if any("-" in t for t in tokens):
        chunks = tokens
    elif len(tokens) % 2 == 0:
        # Display form without separators: every figure name is two words.
        chunks = [f"{a} {b}" for a, b in zip(tokens[::2], tokens[1::2])]
    else:
        raise PhraseError(
            f"cannot split {len(tokens)} words into figures — every figure name "
            "is two words. Use slug form (ogbe-oyeku) or separate figures with '·'."
        )

    return tuple(_resolve(c) for c in chunks)


def _resolve(token: str) -> Odu:
    """Resolve one figure from a slug, a full name, or a pair of leg names."""
    key = normalize(token.strip())
    for candidate in (key, to_ascii(key)):
        hit = _figure_index().get(candidate)
        if hit is not None:
            return hit

    parts = key.split("-") if "-" in key else key.split()
    if len(parts) == 2:
        try:
            return from_legs(principal(parts[0]), principal(parts[1]))
        except (KeyError, ValueError):
            pass

    raise PhraseError(f"{token!r} is not a figure{_suggest(token)}")


def _suggest(token: str) -> str:
    near = get_close_matches(to_ascii(token), list(_figure_index()), n=3, cutoff=0.6)
    ascii_only = [n for n in near if n.isascii()]
    return f". Did you mean: {', '.join(ascii_only[:2])}?" if ascii_only else ""
