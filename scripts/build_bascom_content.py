#!/usr/bin/env python3
"""Build the Bascom content file from his table of contents.

    python3 scripts/build_bascom_content.py

Bascom's contents (pp. v-vi) list every Odù for which he published verses,
with the verse numbers he assigned and the pages they occupy. That gives two
things this project could not otherwise have honestly:

1. **Real page references.** Citation-only verse records — where the verse
   lives, without reproducing a word of copyrighted text.
2. **Attested names.** His notation ``Ogbe - (Ọ)yẹku`` marks a vowel that may
   be elided in speech; the name itself keeps it, and is *Ogbè Ọ̀yẹ̀kú*. These
   are the compound names the dataset carried as ``null`` precisely because
   they must be sourced rather than generated — and Bascom listing them under
   the same construction this dataset uses confirms the convention rather than
   merely repeating it.

Transcribed by eye from the Internet Archive scan on 2026-07-28. The raw
notation is preserved on every record so a later reader can check the
derivation rather than trust it.
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from odu_core import from_legs, principal  # noqa: E402

OUT = ROOT / "kb" / "content" / "sources" / "bascom-1969.json"
NAMES = ROOT / "data" / "compound_names.json"

# (first leg, second leg, Bascom's notation, verse count, page range)
#
# The parenthesised letter in the notation is the one elided in the contracted
# name: "Ogbe - (Ọ)yẹku" is spoken "Ogbe Yẹku". Where Bascom prints no dash and
# no parentheses the name is not contracted.
ENTRIES = [
    ("ogbe", "ogbe",        "Ogbe Meji (1-12)",           12, "140-162"),
    ("ogbe", "oyeku",       "Ogbe - (Ọ)yẹku (1-3)",        3, "164-170"),
    ("ogbe", "iwori",       "Ogbe - (I)wori (1-4)",        4, "170-180"),
    ("ogbe", "odi",         "Ogbe - (E)di (1-4)",          4, "180-184"),
    ("ogbe", "obara",       "Ogbe - (Ọ)bara (1-4)",        4, "184-190"),
    ("ogbe", "okanran",     "Ogbe - (Ọ)kanran (1-6)",      6, "190-202"),
    ("ogbe", "irosun",      "Ogbe - (I)rosun (1-5)",       5, "202-212"),
    ("ogbe", "ogunda",      "Ogbe - (O)gunda (1-3)",       3, "214-220"),
    ("ogbe", "ika",         "Ogbe - (I)ka (1-3)",          3, "220-228"),
    ("oyeku", "ogbe",       "Ọyẹku Ogbe (1-4)",            4, "230-232"),
    ("oyeku", "oyeku",      "Ọyẹku Meji (1-12)",          12, "232-258"),
    ("oyeku", "iwori",      "Ọyẹku - (I)wori (1-3)",       3, "258-262"),
    ("oyeku", "odi",        "Ọyẹku - (E)di (1-3)",         3, "262-264"),
    ("oyeku", "owonrin",    "Ọyẹku - (Ọ)wọnrin (1)",       1, "266-268"),
    ("iwori", "ogbe",       "Iwori Ogbe (1-6)",            6, "268-284"),
    ("iwori", "oyeku",      "Iwori - (Ọ)yẹku (1-2)",       2, "284-286"),
    ("iwori", "iwori",      "Iwori Meji (1-7)",            7, "288-308"),
    ("iwori", "ofun",       "Iwori Ofun (1)",              1, "310"),
    ("odi", "odi",          "Edi Meji (1-5)",              5, "310-318"),
    ("odi", "okanran",      "Edi - (Ọ)kanran (1-8)",       8, "318-336"),
    ("odi", "irosun",       "Edi - (I)rosun (1-2)",        2, "338-340"),
    ("okanran", "okanran",  "Ọkanran Meji (1-3)",          3, "340-344"),
    ("irosun", "obara",     "Irosun Ọbara (1)",            1, "346-350"),
    ("irosun", "irosun",    "Irosun Meji (1-2)",           2, "350-354"),
    ("irosun", "ose",       "Irosun Ọsẹ (1-2)",            2, "354-358"),
    ("owonrin", "owonrin",  "Ọwọnrin Meji (1-2)",          2, "360-362"),
    ("owonrin", "irete",    "Ọwọnrin - (I)rẹtẹ (1)",       1, "362-368"),
    ("ogunda", "iwori",     "Ogunda - (I)wori (1)",        1, "368-370"),
    ("ogunda", "ogunda",    "Ogunda Meji (1-2)",           2, "372-374"),
    ("osa", "ogunda",       "Ọsa - (O)gunda (1)",          1, "374-384"),
    ("osa", "osa",          "Ọsa Meji (1)",                1, "384-386"),
    ("ose", "otura",        "Ọsẹ - (O)tura (1)",           1, "466"),
    ("ose", "ose",          "Ọsẹ Meji (1-2)",              2, "468-470"),
    ("ofun", "ogbe",        "Ofun Ogbe (1-4)",             4, "470-476"),
    ("ofun", "iwori",       "Ofun (I)wori (1-4)",          4, "476-482"),
    ("ofun", "odi",         "Ofun - (E)di (1-2)",          2, "482-486"),
]

SOURCE = {
    "slug": "bascom-1969",
    "kind": "book",
    "title": "Ifa Divination: Communication Between Gods and Men in West Africa",
    "author": "William R. Bascom",
    "year": 1969,
    "publisher": "Indiana University Press",
    "rights": "all-rights-reserved",
    "notes": (
        "Verified 2026-07-28 via Internet Archive controlled lending "
        "(ifadivinationcom0000basc). Table 1 p. 4 and Table 3 col. B p. 48 "
        "verified all 16 principal figures. Verses occupy pp. 140-563; "
        "bibliography pp. 565-575. Bascom numbers his 256 figures by the Ifẹ "
        "order (Table 1), not the southwestern order used as this dataset's "
        "default, so his figure numbers do not match seniority_rank."
    ),
}

# The one assumption in this file, stated rather than buried: Bascom names a
# compound figure "<first> <second>", and that first name is taken to be the
# right leg — the one cast first, which is this dataset's high nibble. His
# contents give no drawn figures to check it against.
LEG_ORDER_NOTE = (
    "Mapped on the assumption that Bascom's first-named leg is the right leg "
    "(cast first, high nibble here). Not confirmed against a drawn compound "
    "figure in the source."
)


def drop_initial_vowel(name: str) -> str:
    """Remove a name's first vowel *and its tone mark*, keeping the rest intact.

    Yorùbá tone marks are combining characters, so the leading vowel of
    ``Ọ̀yẹ̀kú`` is two codepoints — the letter and its grave. Slicing by
    character would strip the letter and orphan the accent onto the next one.
    """
    decomposed = unicodedata.normalize("NFD", name)
    i = 1
    while i < len(decomposed) and unicodedata.combining(decomposed[i]):
        i += 1
    return unicodedata.normalize("NFC", decomposed[i:])


def attested_name(first: str, second: str) -> str:
    """The full name Bascom lists a figure under, in this dataset's orthography.

    Bascom prints the parenthesised letter in ``Ogbe - (Ọ)yẹku`` to mark it as
    *optional* — elided in speech — not absent from the name. The name is
    ``Ogbè Ọ̀yẹ̀kú``, with the vowel.

    An earlier version of this file read the parenthesis as deletion and
    recorded the elided form as primary. That was wrong, and it was an
    inference presented as a source reading. Corrected on the authority of a
    Yorùbá speaker, 2026-07-29.

    Note what this yields: for compound figures the attested name matches the
    name this dataset constructs by concatenation. That is not redundancy —
    it is Bascom confirming that the construction convention is correct, which
    is a different and stronger claim than the dataset making it up.
    """
    head = principal(first).name
    if first == second:
        # Bascom writes every doubled figure as "<Principal> Meji", including
        # Ogbe — where this dataset uses the traditional "Èjì Ogbè" instead.
        return f"{head} Méjì"
    return f"{head} {principal(second).name}"


def elided_form(first: str, second: str, notation: str) -> str | None:
    """The spoken contraction, where Bascom's parentheses mark one.

    Recorded as a variant beside the full name, never in place of it. Whether
    elision shifts the tone of the syllables that remain is unresolved.
    """
    if " - (" not in notation or first == second:
        return None
    tail = drop_initial_vowel(principal(second).name)
    if not tail:
        return None
    return f"{principal(first).name} {tail[0].upper()}{tail[1:]}"


def main() -> int:
    verses, notes, derived, elisions = [], [], 0, 0

    for first, second, notation, count, pages in ENTRIES:
        odu = from_legs(principal(first), principal(second))
        verses.append({
            "odu": odu.slug,
            "pageReference": f"Bascom 1969, pp. {pages} ({notation})",
            "sequence": None,
            "status": "published",
            "notes": (
                f"{count} verse(s) published for this figure. Text not "
                f"reproduced: source is under copyright. {LEG_ORDER_NOTE}"
            ),
        })

        derived += 1
        notes.append({
            "odu": odu.slug,
            "kind": "alternative-name",
            "text": attested_name(first, second),
            "language": "yo",
            "status": "published",
        })
        elided = elided_form(first, second, notation)
        if elided:
            elisions += 1
            notes.append({
                "odu": odu.slug,
                "kind": "alternative-name",
                "text": elided,
                "language": "yo",
                "status": "published",
            })

    payload = {
        "source": SOURCE,
        "transcription": {
            "from": "Table of contents, pp. v-vi",
            "on": "2026-07-28",
            "method": "read by eye from the Internet Archive scan",
            "note": (
                "Notation preserved verbatim in each pageReference so the "
                "derivation of contracted names can be checked, not trusted."
            ),
        },
        "verses": verses,
        "notes": notes,
    }

    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # The same transcription also feeds the canonical dataset, so a sourced
    # name reaches consumers of data/odu_256.json and not only the knowledge
    # base. One transcription, two outputs — never two transcriptions.
    names = {}
    for first, second, notation, _count, pages in ENTRIES:
        name = attested_name(first, second)
        if not name:
            continue
        odu = from_legs(principal(first), principal(second))
        names[odu.slug] = {
            "traditionalName": name,
            "elidedForm": elided_form(first, second, notation),
            "source": f"Bascom 1969, p. v-vi ({notation})",
            "note": (
                "Full attested name. Bascom's parenthesised letter marks a "
                "vowel that may be elided in speech, not one absent from the "
                "name — elidedForm records that variant where he marks one. "
                "Tone marks carried over from this dataset's principal names, "
                "themselves verified against his Table 1 p. 4 and Table 3 "
                "p. 48; Bascom omits tone throughout."
            ),
        }

    NAMES.write_text(
        json.dumps(
            {
                "note": (
                    "Sourced compound names. Generated by "
                    "scripts/build_bascom_content.py — do not edit by hand. "
                    "A figure absent here has no attested name yet and keeps "
                    "traditionalName: null, which is a statement about the "
                    "evidence, not a gap to be filled in."
                ),
                "count": len(names),
                "of": 256,
                "names": names,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  {len(verses)} citation-only verse records")
    print(f"  {derived} attested names")
    print(f"  {elisions} of them also record a spoken elision")
    print(f"wrote {NAMES.relative_to(ROOT)} — {len(names)} of 256 named")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
