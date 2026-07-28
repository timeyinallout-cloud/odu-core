"""Yorùbá orthography helpers.

Yorùbá names carry two independent diacritic systems: sub-dots that distinguish
vowels and consonants (ẹ, ọ, ṣ) and tone marks that carry pitch (à, á). Both are
meaningful — stripping either produces a different word, not a cosmetic variant.
Canonical data therefore always keeps full diacritics, and ASCII slugs exist only
as identifiers.
"""

from __future__ import annotations

import unicodedata

__all__ = ["normalize", "to_ascii", "is_normalized"]


def normalize(text: str) -> str:
    """Return ``text`` in NFC form.

    Yorùbá needs this: ``ọ̀`` has no precomposed codepoint, so it is always
    ``U+1ECD`` plus a combining grave. Two visually identical strings can hold
    different codepoint sequences unless normalized, which silently breaks
    equality checks, sorting, and database lookups.
    """
    return unicodedata.normalize("NFC", text)


def is_normalized(text: str) -> bool:
    """True when ``text`` is already NFC."""
    return unicodedata.is_normalized("NFC", text)


def to_ascii(text: str) -> str:
    """Reduce a Yorùbá name to a lowercase ASCII slug.

    ``Ọ̀yẹ̀kú`` becomes ``oyeku``. This is lossy and one-way — several distinct
    names can collapse to the same slug, so slugs identify records but never
    replace the diacritic form in display or storage.
    """
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return "".join(c for c in stripped.lower() if c.isascii() and (c.isalnum() or c == " ")).strip().replace(" ", "-")
