#!/usr/bin/env python3
"""Build ``web/learn.html``: a flashcard quiz over the 16 verified principal Odù.

Scoped to `isMeji` figures only -- the 240 compound figures carry
`traditionalName: null` because their contracted forms aren't sourced yet,
and this tool only teaches what's been checked against Bascom (1969).

Embeds the data rather than fetching it, same as build_web.py, so the page
works offline and never re-derives the mapping for itself.

Names, the 1-16 seniority rank, and marks come from `data/principal_odu.json`
-- the actual single source of truth -- not from the derived
`data/odu_256.json`. Two reasons: `odu_256.json`'s `traditionalName` has gaps
for 4 of the 16 méjì entries that `principal_odu.json`'s own `mejiName` field
does not, and `odu_256.json`'s `seniorityRank` is the full 1-256 rank
interleaved with all 240 compound figures, not the 1-16 principal rank this
quiz teaches -- using it directly would have taught the wrong numbers. Byte
value comes from `odu_256.json`, since méjì bytes aren't stored in
`principal_odu.json` and re-deriving `nibble * 17` here would be exactly the
kind of second computation the project's docs warn drifts from the first.

    python3 scripts/build_learn.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "web" / "learn.template.html"
OUT = ROOT / "web" / "learn.html"
PRINCIPAL_SOURCE = ROOT / "data" / "principal_odu.json"
FULL_SOURCE = ROOT / "data" / "odu_256.json"
MARKER = "/*__PRINCIPAL_DATA__*/null"


def main() -> int:
    if not PRINCIPAL_SOURCE.exists() or not FULL_SOURCE.exists():
        print("run scripts/generate.py first", file=sys.stderr)
        return 1

    principal = json.loads(PRINCIPAL_SOURCE.read_text(encoding="utf-8"))["odu"]
    full = json.loads(FULL_SOURCE.read_text(encoding="utf-8"))["odu"]
    by_slug = {o["right"]["slug"]: o for o in full if o["isMeji"]}

    if len(principal) != 16:
        print(f"expected 16 principal Odù, found {len(principal)} -- "
              f"source data looks wrong", file=sys.stderr)
        return 1
    if any(o["mejiName"] is None or o["verification"]["status"] != "verified"
           for o in principal):
        print("a principal Odù is missing its verified name or verification "
              "status -- refusing to build a quiz on unverified data", file=sys.stderr)
        return 1
    missing = [o["slug"] for o in principal if o["slug"] not in by_slug]
    if missing:
        print(f"principal_odu.json and odu_256.json disagree on slugs: "
              f"{missing} not found as a méjì figure in odu_256.json", file=sys.stderr)
        return 1

    slim = [
        {
            "byte": by_slug[o["slug"]]["byte"], "bits": by_slug[o["slug"]]["bits"],
            "slug": o["slug"], "name": o["name"], "mejiName": o["mejiName"],
            "rank": o["rank"], "nibble": by_slug[o["slug"]]["right"]["nibble"],
            "marks": {"right": o["marks"], "left": o["marks"]},
        }
        for o in principal
    ]
    slim.sort(key=lambda o: o["rank"])

    template = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in template:
        print(f"template is missing the {MARKER} marker", file=sys.stderr)
        return 1

    payload = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")

    OUT.write_text(template.replace(MARKER, payload), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {OUT.stat().st_size:,} bytes, "
          f"16 principal figures embedded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
