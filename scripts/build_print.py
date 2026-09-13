#!/usr/bin/env python3
"""Build ``web/print.html`` — a print-ready fingerprint card/plaque.

Renders all 256 figures to SVG server-side (via `odu_core.generative.to_svg`)
and embeds them alongside the byte table, so the page never re-derives the
mapping or the drawing for itself — same discipline as build_web.py and
build_learn.py.

    python3 scripts/build_print.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "web" / "print.template.html"
OUT = ROOT / "web" / "print.html"
SOURCE = ROOT / "data" / "odu_256.json"
MARKER = "/*__PRINT_DATA__*/null"

SVG_SIZE = 220  # px -- legible at both screen size and the print card's scale


def main() -> int:
    if not SOURCE.exists():
        print("run scripts/generate.py first", file=sys.stderr)
        return 1

    sys.path.insert(0, str(ROOT / "src"))
    from odu_core import from_byte
    from odu_core.generative import to_svg

    full = json.loads(SOURCE.read_text(encoding="utf-8"))
    if [o["byte"] for o in full["odu"]] != list(range(256)):
        print("source is not in byte order — the page indexes by position", file=sys.stderr)
        return 1

    slim = []
    for o in full["odu"]:
        odu = from_byte(o["byte"])
        slim.append({
            "byte": o["byte"], "name": o["name"], "slug": o["slug"],
            "svg": to_svg(odu, size=SVG_SIZE, show_name=False),
        })

    template = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in template:
        print(f"template is missing the {MARKER} marker", file=sys.stderr)
        return 1

    payload = json.dumps({"specVersion": full["specVersion"], "odu": slim},
                          ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")

    OUT.write_text(template.replace(MARKER, payload), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {OUT.stat().st_size:,} bytes, "
          f"256 figures embedded, drawn at {SVG_SIZE}px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
