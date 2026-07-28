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
from odu_core.data import _raw  # noqa: E402

OUT = ROOT / "data" / "odu_256.json"


def build() -> dict:
    return {
        "specVersion": spec_version(),
        "generatedBy": "scripts/generate.py",
        "source": "data/principal_odu.json",
        "warning": "DERIVED FILE — do not edit by hand. Regenerate instead.",
        "convention": convention(),
        "verificationStatus": _raw()["verificationStatus"],
        "count": 256,
        "odu": [
            {
                "byte": o.byte,
                "bits": o.bits,
                "hex": f"{o.byte:02X}",
                "name": o.name,
                "slug": o.slug,
                "traditionalName": o.traditional_name,
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
