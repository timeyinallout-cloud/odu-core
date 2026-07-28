#!/usr/bin/env python3
"""Build the Bascom content file from his table of contents.

    python3 scripts/build_bascom_content.py

Bascom's contents (pp. v-vi) list every Odù for which he published verses,
with the verse numbers he assigned and the pages they occupy. That gives two
things this project could not otherwise have honestly:

1. **Real page references.** Citation-only verse records — where the verse
   lives, without reproducing a word of copyrighted text.
2. **Attested contracted names.** His notation ``Ogbe - (Ọ)yẹku`` marks the
   elision: the contracted form is *Ogbe Yẹku*. These are the traditional
   compound names the dataset has been carrying as ``null`` precisely because
   they must be sourced rather than generated.

Transcribed by eye from the Internet Archive scan on 2026-07-28. The raw
notation is preserved on every record so a later reader can check the
derivation rather than trust it.
"""

from __future__ import annotations

import json
import sys
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


def contracted(notation: str) -> str | None:
    """Derive the contracted name where the dash-and-parenthesis marks it.

    ``Ogbe - (Ọ)yẹku`` gives ``Ogbe Yẹku``. Entries without that exact pattern
    are left alone: guessing at an elision would manufacture a traditional name,
    which is the one thing this dataset must never do.
    """
    head = notation.split(" (")[0]
    if " - (" not in notation:
        return None
    left, rest = notation.split(" - (", 1)
    elided, tail = rest.split(")", 1)
    second = tail.split(" (")[0].strip()
    if not second or not elided:
        return None
    return f"{left.strip()} {second[0].upper()}{second[1:]}"


def main() -> int:
    verses, notes, derived = [], [], 0

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

        name = contracted(notation)
        if name:
            derived += 1
            notes.append({
                "odu": odu.slug,
                "kind": "alternative-name",
                "text": name,
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
        name = contracted(notation)
        if not name:
            continue
        odu = from_legs(principal(first), principal(second))
        names[odu.slug] = {
            "traditionalName": name,
            "source": f"Bascom 1969, p. v-vi ({notation})",
            "note": "contracted form; the parenthesised letter is elided",
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
    print(f"  {derived} contracted names derived from Bascom's elision notation")
    print(f"  {len(ENTRIES) - derived} entries carry no contraction in the source")
    print(f"wrote {NAMES.relative_to(ROOT)} — {len(names)} of 256 named")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
