"""Core types for the Odù dataset.

A single Odù figure is two legs of four lines each. Every line carries either one
mark or two marks, giving four bits per leg and eight bits — exactly one byte —
per full figure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Mark = Literal["I", "II"]
"""A single line of a leg. ``I`` is one mark, ``II`` is two marks."""


@dataclass(frozen=True, slots=True)
class PrincipalOdu:
    """One of the 16 principal Odù — a single four-line leg."""

    rank: int
    """Position in the traditional seniority order, 1-16."""

    name: str
    """Name in full Yorùbá orthography, NFC-normalized."""

    meji_name: str
    """Name of the doubled figure, e.g. ``Ọ̀yẹ̀kú Méjì``."""

    slug: str
    """ASCII-safe identifier, e.g. ``oyeku``."""

    marks: tuple[Mark, Mark, Mark, Mark]
    """The four lines, ordered top to bottom."""

    nibble: int
    """The leg as a 4-bit integer, 0-15. Top line is the most significant bit."""

    @property
    def bits(self) -> str:
        """The leg as a 4-character bit string, top line first."""
        return f"{self.nibble:04b}"


@dataclass(frozen=True, slots=True)
class Odu:
    """One of the 256 full Odù figures — two legs, one byte."""

    byte: int
    """The figure as an integer, 0-255. The right leg is the high nibble."""

    right: PrincipalOdu
    """The right leg. Cast first in divination; the high nibble here."""

    left: PrincipalOdu
    """The left leg. The low nibble."""

    name: str
    """Compound name, e.g. ``Ogbè Ọ̀yẹ̀kú``. Méjì figures use their méjì name."""

    slug: str
    """ASCII-safe identifier, e.g. ``ogbe-oyeku``."""

    seniority_rank: int
    """Position in the traditional 256 ordering, 1-256. See :mod:`seniority`."""

    traditional_name: str | None = None
    """Contracted traditional name where one is attested, e.g. ``Ogbè Yẹ̀kú``.

    ``None`` means no name has been sourced yet — these contractions vary by
    lineage and must come from a citable source, never from generation.
    """

    @property
    def is_meji(self) -> bool:
        """True when both legs are the same principal Odù."""
        return self.right.slug == self.left.slug

    @property
    def bits(self) -> str:
        """The figure as an 8-character bit string, right leg first."""
        return f"{self.byte:08b}"

    @property
    def marks(self) -> tuple[tuple[Mark, ...], tuple[Mark, ...]]:
        """The two legs' marks as ``(right, left)``, each top to bottom."""
        return (self.right.marks, self.left.marks)

    def figure(self) -> str:
        """Render the figure as text, right leg in the left-hand column."""
        rows = []
        for r, l in zip(self.right.marks, self.left.marks):
            rows.append(f"{_strokes(r):>3}  {_strokes(l):<3}".rstrip())
        return "\n".join(rows)


def _strokes(mark: Mark) -> str:
    return "I" if mark == "I" else "I I"
