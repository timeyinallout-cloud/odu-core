"""Guards the flashcard quiz's build script against exactly the mistake it
was written to catch: sourcing the wrong rank scale.

`data/odu_256.json`'s `seniorityRank` runs 1-256, interleaved across all
figures including the 240 compound ones. `data/principal_odu.json`'s `rank`
is the 1-16 principal-only scale the quiz actually teaches. Reading the
wrong one silently produces a page that looks fine but teaches wrong
numbers -- there is no build error, just incorrect content. So this test
runs the real build against the real data files and checks the *numbers*,
not just that a file got written.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER_RE = re.compile(r"const PRINCIPAL = (\[.*?\]);", re.S)


def _build() -> list[dict]:
    subprocess.run([sys.executable, "scripts/generate.py"], cwd=ROOT, check=True,
                    capture_output=True)
    result = subprocess.run([sys.executable, "scripts/build_learn.py"], cwd=ROOT,
                             check=True, capture_output=True, text=True)
    assert "16 principal figures embedded" in result.stdout
    html = (ROOT / "web" / "learn.html").read_text(encoding="utf-8")
    match = MARKER_RE.search(html)
    assert match, "could not find embedded PRINCIPAL data in web/learn.html"
    return json.loads(match.group(1))


def test_embeds_exactly_sixteen_figures():
    data = _build()
    assert len(data) == 16


def test_rank_is_the_one_to_sixteen_principal_scale_not_the_full_256_scale():
    data = _build()
    ranks = sorted(o["rank"] for o in data)
    assert ranks == list(range(1, 17)), (
        "ranks must be the 1-16 principal scale from principal_odu.json, "
        "not odu_256.json's interleaved 1-256 seniorityRank"
    )


def test_every_figure_has_a_verified_meji_name():
    data = _build()
    for o in data:
        assert o["mejiName"], f"{o['slug']} has no mejiName"
        assert "Méjì" in o["mejiName"] or o["slug"] == "ogbe", (
            f"{o['slug']}'s mejiName {o['mejiName']!r} doesn't look like a "
            f"méjì name"
        )


def test_byte_values_match_the_nibble_times_seventeen_convention():
    # Every méjì figure has identical legs, so byte = nibble * 17 (nibble
    # repeated in both the high and low nibble). This is the same check the
    # library's own tests run against odu_256.json -- reproduced here to
    # catch a bad join between principal_odu.json and odu_256.json specifically.
    data = _build()
    for o in data:
        assert o["byte"] == o["nibble"] * 17, o["slug"]


def test_ogbe_is_rank_one_and_byte_255():
    data = _build()
    ogbe = next(o for o in data if o["slug"] == "ogbe")
    assert ogbe["rank"] == 1
    assert ogbe["byte"] == 255
    assert ogbe["mejiName"] == "Èjì Ogbè"


def test_marks_are_present_for_both_legs():
    data = _build()
    for o in data:
        assert len(o["marks"]["right"]) == 4
        assert len(o["marks"]["left"]) == 4
        # méjì figures: legs are identical by definition
        assert o["marks"]["right"] == o["marks"]["left"], o["slug"]
