"""Byte ↔ Odù conversion.

The mapping is a bijection, not an encoding scheme with padding or escapes:
every byte is exactly one Odù and every Odù is exactly one byte. The right leg
occupies the high nibble, following the order in which the legs are cast.
"""

from __future__ import annotations

from functools import cache
from typing import Iterable

from .data import principal_odu
from .orthography import normalize, to_ascii
from .types import Odu, PrincipalOdu

__all__ = [
    "from_byte",
    "to_byte",
    "from_legs",
    "from_bits",
    "all_odu",
    "principal",
    "encode",
    "decode",
]

LegRef = int | str | PrincipalOdu
"""Anything that identifies a leg: nibble, slug, name, or the object itself."""


@cache
def _by_nibble() -> dict[int, PrincipalOdu]:
    return {o.nibble: o for o in principal_odu()}


@cache
def _by_key() -> dict[str, PrincipalOdu]:
    """Lookup by slug and by name, both diacritic and ASCII-folded."""
    index: dict[str, PrincipalOdu] = {}
    for o in principal_odu():
        for key in (o.slug, to_ascii(o.name), to_ascii(o.meji_name)):
            index[key] = o
        for key in (o.name, o.meji_name):
            index[normalize(key)] = o
    return index


def principal(ref: LegRef) -> PrincipalOdu:
    """Resolve a leg from its nibble, slug, or name.

    Accepts ``3``, ``"owonrin"``, ``"Ọ̀wọ́nrín"``, or ``"Ọ̀wọ́nrín Méjì"``.
    """
    if isinstance(ref, PrincipalOdu):
        return ref
    if isinstance(ref, int):
        if not 0 <= ref <= 15:
            raise ValueError(f"a leg's nibble must be 0-15, got {ref}")
        return _by_nibble()[ref]
    found = _by_key().get(normalize(ref)) or _by_key().get(to_ascii(ref))
    if found is None:
        raise KeyError(f"no principal Odù matches {ref!r}")
    return found


def from_byte(value: int) -> Odu:
    """Build the Odù for a byte value, 0-255."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"expected an int, got {type(value).__name__}")
    if not 0 <= value <= 255:
        raise ValueError(f"a byte must be 0-255, got {value}")
    return _build(_by_nibble()[value >> 4], _by_nibble()[value & 0x0F])


def to_byte(odu: Odu) -> int:
    """Return the byte value of an Odù."""
    return odu.byte


def from_legs(right: LegRef, left: LegRef) -> Odu:
    """Build an Odù from its two legs, right first as it is cast."""
    return _build(principal(right), principal(left))


def from_bits(bits: str) -> Odu:
    """Build an Odù from an 8-character bit string, right leg first."""
    cleaned = bits.strip().replace(" ", "").replace("_", "")
    if len(cleaned) != 8 or set(cleaned) - {"0", "1"}:
        raise ValueError(f"expected 8 binary digits, got {bits!r}")
    return from_byte(int(cleaned, 2))


def _build(right: PrincipalOdu, left: PrincipalOdu) -> Odu:
    is_meji = right.slug == left.slug
    return Odu(
        byte=(right.nibble << 4) | left.nibble,
        right=right,
        left=left,
        # Méjì figures carry their own attested name. Compound figures get a
        # descriptive "right left" pair — the contracted traditional names vary
        # by lineage and are left for the sourced dataset to fill in.
        name=right.meji_name if is_meji else f"{right.name} {left.name}",
        slug=f"{right.slug}-{left.slug}",
        seniority_rank=(right.rank - 1) * 16 + left.rank,
        traditional_name=None,
    )


@cache
def all_odu() -> tuple[Odu, ...]:
    """All 256 Odù in byte order, index ``i`` being byte ``i``."""
    return tuple(from_byte(b) for b in range(256))


def encode(data: bytes | bytearray | Iterable[int]) -> tuple[Odu, ...]:
    """Convert bytes to Odù, one per byte, in order."""
    return tuple(from_byte(b) for b in bytes(data))


def decode(odu: Iterable[Odu]) -> bytes:
    """Convert Odù back to bytes. Inverse of :func:`encode`."""
    return bytes(o.byte for o in odu)
