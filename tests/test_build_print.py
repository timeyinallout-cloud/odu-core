"""Checks the print-card build embeds real, byte-correct SVG figures.

Runs the real build against the real data (not a mock), same discipline as
test_build_learn.py -- a page that "builds fine" but embeds the wrong
figure's SVG for a given byte would show no build error, just a card with
the wrong drawing on it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER_RE = re.compile(r"const DATA = (\{.*\});\n\nasync function checksumByte", re.S)


def _build() -> dict:
    subprocess.run([sys.executable, "scripts/generate.py"], cwd=ROOT, check=True,
                    capture_output=True)
    result = subprocess.run([sys.executable, "scripts/build_print.py"], cwd=ROOT,
                             check=True, capture_output=True, text=True)
    assert "256 figures embedded" in result.stdout
    html = (ROOT / "web" / "print.html").read_text(encoding="utf-8")
    match = MARKER_RE.search(html)
    assert match, "could not find embedded DATA in web/print.html"
    return json.loads(match.group(1))


def test_embeds_all_256_figures_in_byte_order():
    data = _build()
    assert [o["byte"] for o in data["odu"]] == list(range(256))


def test_every_figure_carries_a_real_svg():
    data = _build()
    for o in data["odu"]:
        assert o["svg"].startswith("<svg"), o["slug"]
        assert o["svg"].endswith("</svg>"), o["slug"]


def test_svg_aria_label_matches_its_own_byte_and_name():
    # The strongest correctness check: each embedded SVG's own aria-label
    # (baked in server-side by to_svg) names the byte and figure it was
    # rendered for. If the build ever zipped names/bytes to the wrong SVGs,
    # this catches it without needing to re-implement figure drawing here.
    data = _build()
    for o in data["odu"]:
        assert f'byte {o["byte"]}' in o["svg"], (
            f"slug {o['slug']} (byte {o['byte']}) embeds an SVG whose own "
            f"aria-label doesn't name that byte -- {o['svg'][:200]}"
        )


def test_ogbe_meji_and_oyeku_meji_are_the_extreme_bytes():
    # This embeds all 256 (byte-indexed) figures, so the méjì slugs are the
    # compound form -- "ogbe-ogbe", not "ogbe" (that's the 16-figure leg
    # slug used by build_learn.py's separate, principal-only dataset).
    data = _build()
    by_slug = {o["slug"]: o for o in data["odu"]}
    assert by_slug["ogbe-ogbe"]["byte"] == 255
    assert by_slug["ogbe-ogbe"]["name"] == "Èjì Ogbè"
    assert by_slug["oyeku-oyeku"]["byte"] == 0
