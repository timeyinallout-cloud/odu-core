#!/usr/bin/env python3
"""Generate ``data/odu_256.json`` from the canonical 16.

This artifact is derived, never edited by hand — it is the file other languages
and other surfaces import so that nothing re-derives the mapping for itself.
Run after any change to ``data/principal_odu.json``.

    python3 scripts/generate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from odu_core import all_odu, convention, spec_version  # noqa: E402
from odu_core.data import _raw, verification_summary  # noqa: E402

OUT = ROOT / "data" / "odu_256.json"
NAMES = ROOT / "data" / "compound_names.json"


def sourced_names() -> dict:
    """Attested compound names, keyed by slug.

    Absent entries stay ``null``. That null is a statement about the evidence —
    no source has been found for that figure's traditional name — and not a
    placeholder waiting to be filled by inference.
    """
    if not NAMES.exists():
        return {}
    return json.loads(NAMES.read_text(encoding="utf-8")).get("names", {})


def build() -> dict:
    summary = verification_summary()
    names = sourced_names()
    return {
        "specVersion": spec_version(),
        "generatedBy": "scripts/generate.py",
        "source": "data/principal_odu.json",
        "warning": "DERIVED FILE — do not edit by hand. Regenerate instead.",
        "convention": convention(),
        # Carried through so a consumer of this file alone can still tell how
        # much of the mapping rests on a checked source.
        "verification": {
            "verified": summary["verified"],
            "unverified": summary["unverified"],
            "disputed": summary["disputed"],
            "total": summary["total"],
            "complete": summary["complete"],
            "acceptedSources": summary["accepted_sources"],
            "note": _raw().get("verification", {}).get("note"),
        },
        "namesSourced": len(names),
        "count": 256,
        "odu": [
            {
                "byte": o.byte,
                "bits": o.bits,
                "hex": f"{o.byte:02X}",
                "name": o.name,
                "slug": o.slug,
                "traditionalName": (names.get(o.slug) or {}).get("traditionalName"),
                "traditionalNameSource": (names.get(o.slug) or {}).get("source"),
                "elidedForm": (names.get(o.slug) or {}).get("elidedForm"),
                "isMeji": o.is_meji,
                "seniorityRank": o.seniority_rank,
                "right": {"slug": o.right.slug, "name": o.right.name, "nibble": o.right.nibble},
                "left": {"slug": o.left.slug, "name": o.left.name, "nibble": o.left.nibble},
                "marks": {"right": list(o.right.marks), "left": list(o.left.marks)},
            }
            for o in all_odu()
        ],
    }


def main() -> int:
    payload = build()
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    size = OUT.stat().st_size
    print(f"wrote {OUT.relative_to(ROOT)} — {payload['count']} figures, {size:,} bytes")
    print(f"spec version {payload['specVersion']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
