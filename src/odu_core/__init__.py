"""odu-core — the 256 Odù Ifá as a canonical byte mapping.

Each Odù figure is two legs of four lines; each line carries one mark or two.
That is four bits per leg, eight bits per figure, and exactly 256 figures — a
bijection with the byte that needs no padding and loses nothing.

    >>> from odu_core import from_byte
    >>> from_byte(255).name
    'Èjì Ogbè'

The canonical data lives in ``data/principal_odu.json``, not in this code. See
that file's ``convention`` block for the four choices that fix the mapping.
"""

from .core import (
    all_odu,
    decode,
    encode,
    from_bits,
    from_byte,
    from_legs,
    principal,
    to_byte,
)
from .data import DATA_PATH, convention, principal_odu, spec_version
from .orthography import is_normalized, normalize, to_ascii
from .seniority import TRADITION, by_seniority, senior_of, seniority_rank
from .types import Mark, Odu, PrincipalOdu

__version__ = "1.0.0"

__all__ = [
    "Mark",
    "Odu",
    "PrincipalOdu",
    "all_odu",
    "by_seniority",
    "convention",
    "decode",
    "encode",
    "from_bits",
    "from_byte",
    "from_legs",
    "is_normalized",
    "normalize",
    "principal",
    "principal_odu",
    "senior_of",
    "seniority_rank",
    "spec_version",
    "to_ascii",
    "to_byte",
    "DATA_PATH",
    "TRADITION",
    "__version__",
]
