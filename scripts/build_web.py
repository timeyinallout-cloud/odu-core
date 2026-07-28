#!/usr/bin/env python3
"""Build ``web/index.html`` by injecting the canonical table into the template.

The demo embeds its data rather than fetching it, so the page is a single file
that works offline. The data is injected from ``data/odu_256.json`` at build
time — the page never re-derives the mapping for itself.

    python3 scripts/build_web.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "web" / "index.template.html"
OUT = ROOT / "web" / "index.html"
SOURCE = ROOT / "data" / "odu_256.json"
MARKER = "/*__ODU_DATA__*/null"


def main() -> int:
    if not SOURCE.exists():
        print("run scripts/generate.py first", file=sys.stderr)
        return 1

    full = json.loads(SOURCE.read_text(encoding="utf-8"))

    # Only the fields the page actually uses — keeps the payload small enough
    # to inline without turning the file into a megabyte.
    slim = {
        "specVersion": full["specVersion"],
        "odu": [
            {"byte": o["byte"], "name": o["name"], "slug": o["slug"], "marks": o["marks"]}
            for o in full["odu"]
        ],
    }
    if [o["byte"] for o in slim["odu"]] != list(range(256)):
        print("source is not in byte order — the page indexes by position", file=sys.stderr)
        return 1

    template = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in template:
        print(f"template is missing the {MARKER} marker", file=sys.stderr)
        return 1

    payload = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
    # Guard against the embedded JSON terminating the surrounding <script>.
    payload = payload.replace("</", "<\\/")

    OUT.write_text(template.replace(MARKER, payload), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {OUT.stat().st_size:,} bytes, 256 figures embedded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
