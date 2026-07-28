"""Traditional ordering.

Seniority order and numeric order are different orderings of the same 256
figures, and neither is derivable from the other by arithmetic on the byte. Ogbè
is the most senior Odù but its leg is ``1111`` — byte 255, dead last numerically.

This is why the library indexes by bit pattern rather than by rank. The bit
pattern is structural and uncontested; seniority varies between lineages and
regions, so it lives here as an attribute that can hold more than one tradition.
"""

from __future__ import annotations

from functools import cache

from .core import all_odu
from .types import Odu

__all__ = ["seniority_rank", "by_seniority", "senior_of", "TRADITION"]

TRADITION = "southwestern-yoruba"
"""The seniority tradition this module implements.

Other traditions order the principal Odù differently — the Cuban Lucumí
sequence is not this sequence. Adding one means adding a rank field to the
canonical JSON, not rewriting this logic.
"""


def seniority_rank(odu: Odu) -> int:
    """Position in the traditional 256 ordering, 1-256.

    Figures are grouped by their right leg's seniority, then ordered by the
    left leg's within each group.
    """
    return odu.seniority_rank


@cache
def by_seniority() -> tuple[Odu, ...]:
    """All 256 Odù in traditional seniority order, most senior first."""
    return tuple(sorted(all_odu(), key=lambda o: o.seniority_rank))


def senior_of(a: Odu, b: Odu) -> Odu:
    """Return whichever of two figures outranks the other.

    In divination two figures are cast and the senior one is read; this is that
    comparison, not a numeric one.
    """
    return a if a.seniority_rank <= b.seniority_rank else b
