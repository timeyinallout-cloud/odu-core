"""Deterministic art and rhythm derived from a figure's bit pattern.

Everything here is a pure function of the eight bits. No randomness, no seeds,
no hidden state — the same figure always yields the same output, on any machine,
forever. That matters more than it sounds: a generated image is only meaningful
as *this figure's* image if it cannot drift.

The mapping to rhythm is the one that needed no invention. A line carries one
mark or two, and a drum stroke is struck once or twice. Ifá figures are already
read aloud in rhythm; this only writes down what the marks say.

    >>> from odu_core import from_byte
    >>> from odu_core.generative import to_rhythm
    >>> to_rhythm(from_byte(255)).strokes
    (1, 1, 1, 1, 1, 1, 1, 1)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Literal

from .types import Odu

__all__ = [
    "Rhythm",
    "to_rhythm",
    "to_grid",
    "to_svg",
    "palette_for",
    "PALETTE",
]

# Earth pigments — the colours the figures are actually marked in. Iyerosun is
# the pale wood dust the diviner marks on; the darker tones are the board and
# the palm nuts. Deliberately not a spectrum: the figures are not data.
PALETTE: tuple[str, ...] = (
    "#e8dcc4",  # iyerosun, pale
    "#c9a227",  # ochre
    "#a8622d",  # burnt sienna
    "#7a4b1e",  # opon wood
    "#4a3520",  # dark board
    "#2b1d12",  # near-black
)


@dataclass(frozen=True, slots=True)
class Rhythm:
    """A figure expressed as drum strokes, right leg first."""

    strokes: tuple[int, ...]
    """One entry per line, top to bottom: 1 for a single mark, 2 for a double."""

    beats: int
    """Total strokes — between 8 and 16 depending on the figure."""

    @property
    def pattern(self) -> str:
        """A readable stroke pattern, legs separated by a bar."""
        right = " ".join("x" * n for n in self.strokes[:4])
        left = " ".join("x" * n for n in self.strokes[4:])
        return f"{right} | {left}"

    def onsets(self, subdivision: int = 2) -> tuple[int, ...]:
        """Onset positions on a fixed grid, for sequencing.

        Each line occupies ``subdivision`` slots. A single mark strikes on the
        first slot; a double strikes on both. With the default of 2 a figure
        fills 16 slots — one bar of semiquavers.
        """
        if subdivision < 2:
            raise ValueError("a double mark needs at least two slots per line")
        positions = []
        for i, n in enumerate(self.strokes):
            base = i * subdivision
            positions.append(base)
            if n == 2:
                positions.append(base + 1)
        return tuple(positions)


def to_rhythm(odu: Odu) -> Rhythm:
    """Convert a figure to drum strokes: one mark one strike, two marks two."""
    strokes = tuple(
        1 if mark == "I" else 2
        for leg in (odu.right.marks, odu.left.marks)
        for mark in leg
    )
    return Rhythm(strokes=strokes, beats=sum(strokes))


def to_grid(odu: Odu) -> tuple[tuple[bool, bool], ...]:
    """The figure as four rows of two legs, ``True`` where the mark is single.

    Right leg first in each row, matching how the figure is drawn.
    """
    return tuple(
        (odu.right.marks[i] == "I", odu.left.marks[i] == "I") for i in range(4)
    )


def palette_for(odu: Odu, size: int = 3) -> tuple[str, ...]:
    """Pick colours for a figure, deterministically from its byte.

    Spaced around the palette rather than taken consecutively, so adjacent byte
    values do not produce near-identical images.
    """
    if not 1 <= size <= len(PALETTE):
        raise ValueError(f"size must be 1-{len(PALETTE)}, got {size}")
    step = max(1, len(PALETTE) // size)
    return tuple(PALETTE[(odu.byte + i * step) % len(PALETTE)] for i in range(size))


def to_svg(odu: Odu, size: int = 320, show_name: bool = True) -> str:
    """Render the figure as a standalone SVG.

    Marks are drawn as the diviner draws them — strokes in two columns, right
    leg on the left of the page — rather than as an abstraction of the bits.
    """
    if size < 80:
        raise ValueError("size must be at least 80 for the marks to be legible")

    bg, ink, accent = palette_for(odu, 3)
    pad = size * 0.14
    inner = size - 2 * pad
    row_h = inner / 4
    col_w = inner / 2
    mark_w = col_w * 0.30
    mark_h = row_h * 0.16

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}" role="img" '
        f'aria-label="Odù {odu.name}, byte {odu.byte}">',
        f'<rect width="{size}" height="{size}" fill="{bg}"/>',
    ]

    for row, (right_single, left_single) in enumerate(to_grid(odu)):
        cy = pad + row * row_h + row_h / 2
        for col, single in enumerate((right_single, left_single)):
            cx = pad + col * col_w + col_w / 2
            # One mark sits centred; two sit apart, as they are drawn.
            offsets = (0.0,) if single else (-col_w * 0.17, col_w * 0.17)
            for dx in offsets:
                parts.append(
                    f'<rect x="{cx + dx - mark_w / 2:.2f}" y="{cy - mark_h / 2:.2f}" '
                    f'width="{mark_w:.2f}" height="{mark_h:.2f}" rx="{mark_h / 2:.2f}" '
                    f'fill="{ink}"/>'
                )

    if show_name:
        parts.append(
            f'<text x="{size / 2:.1f}" y="{size - pad * 0.35:.1f}" fill="{accent}" '
            f'font-family="system-ui, sans-serif" font-size="{size * 0.052:.1f}" '
            f'text-anchor="middle">{_escape(odu.name)}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def each_figure_svg(size: int = 160) -> Iterator[tuple[Odu, str]]:
    """Yield every figure with its SVG, for building contact sheets."""
    from .core import all_odu

    for odu in all_odu():
        yield odu, to_svg(odu, size=size, show_name=False)
