"""Tests for the generative layer.

Determinism is the property that matters: a figure's image and rhythm must be
functions of its bits alone, so they mean the same thing on every machine and
in five years' time.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from odu_core import all_odu, from_byte  # noqa: E402
from odu_core.generative import (  # noqa: E402
    PALETTE,
    each_figure_svg,
    palette_for,
    to_grid,
    to_rhythm,
    to_svg,
)


class TestRhythm:
    def test_single_marks_strike_once_double_twice(self):
        assert to_rhythm(from_byte(255)).strokes == (1,) * 8   # Èjì Ogbè
        assert to_rhythm(from_byte(0)).strokes == (2,) * 8     # Ọ̀yẹ̀kú Méjì

    def test_every_figure_has_eight_lines(self):
        for o in all_odu():
            assert len(to_rhythm(o).strokes) == 8

    def test_beats_range_from_eight_to_sixteen(self):
        beats = {to_rhythm(o).beats for o in all_odu()}
        assert min(beats) == 8 and max(beats) == 16

    def test_beats_equal_the_sum_of_strokes(self):
        for o in all_odu():
            r = to_rhythm(o)
            assert r.beats == sum(r.strokes)

    def test_right_leg_comes_first(self):
        odu = from_byte(0b1111_0000)  # all single right, all double left
        assert to_rhythm(odu).strokes == (1, 1, 1, 1, 2, 2, 2, 2)

    def test_pattern_separates_the_legs(self):
        assert to_rhythm(from_byte(255)).pattern == "x x x x | x x x x"
        assert to_rhythm(from_byte(0)).pattern == "xx xx xx xx | xx xx xx xx"

    def test_onsets_fill_a_sixteen_slot_bar(self):
        onsets = to_rhythm(from_byte(0)).onsets()
        assert len(onsets) == 16
        assert max(onsets) < 16

    def test_onsets_are_strictly_increasing(self):
        for o in all_odu():
            onsets = to_rhythm(o).onsets()
            assert list(onsets) == sorted(onsets)
            assert len(set(onsets)) == len(onsets)

    def test_single_mark_figure_has_the_fewest_onsets(self):
        assert len(to_rhythm(from_byte(255)).onsets()) == 8

    def test_subdivision_below_two_rejected(self):
        # A double mark needs two slots; one slot would silently drop a stroke.
        with pytest.raises(ValueError):
            to_rhythm(from_byte(0)).onsets(subdivision=1)

    def test_distinct_figures_give_distinct_rhythms(self):
        assert len({to_rhythm(o).strokes for o in all_odu()}) == 256


class TestGrid:
    def test_four_rows_of_two_legs(self):
        grid = to_grid(from_byte(44))
        assert len(grid) == 4
        assert all(len(row) == 2 for row in grid)

    def test_grid_matches_the_marks(self):
        for o in all_odu():
            for i, (right, left) in enumerate(to_grid(o)):
                assert right == (o.right.marks[i] == "I")
                assert left == (o.left.marks[i] == "I")


class TestPalette:
    def test_colours_come_from_the_palette(self):
        for o in all_odu():
            assert all(c in PALETTE for c in palette_for(o))

    def test_deterministic(self):
        assert palette_for(from_byte(44)) == palette_for(from_byte(44))

    def test_adjacent_bytes_differ(self):
        assert palette_for(from_byte(44)) != palette_for(from_byte(45))

    def test_requested_size_is_honoured(self):
        for n in range(1, len(PALETTE) + 1):
            assert len(palette_for(from_byte(7), n)) == n

    @pytest.mark.parametrize("bad", [0, -1, len(PALETTE) + 1])
    def test_invalid_size_rejected(self, bad):
        with pytest.raises(ValueError):
            palette_for(from_byte(0), bad)


class TestSvg:
    def test_every_figure_renders(self):
        for o in all_odu():
            svg = to_svg(o)
            assert svg.startswith("<svg") and svg.endswith("</svg>")

    def test_deterministic(self):
        assert to_svg(from_byte(44)) == to_svg(from_byte(44))

    def test_distinct_figures_render_differently(self):
        assert len({to_svg(o, show_name=False) for o in all_odu()}) == 256

    def test_mark_count_matches_the_figure(self):
        for byte in (0, 44, 255):
            o = from_byte(byte)
            expected = to_rhythm(o).beats
            # One <rect> per stroke, plus one for the background.
            assert to_svg(o, show_name=False).count("<rect") == expected + 1

    def test_name_is_escaped_and_optional(self):
        assert "Èjì Ogbè" in to_svg(from_byte(255))
        assert "<text" not in to_svg(from_byte(255), show_name=False)

    def test_has_an_accessible_label(self):
        svg = to_svg(from_byte(44))
        assert 'role="img"' in svg
        assert 'aria-label="Odù Òtúrúpọ̀n Ìrosùn, byte 44"' in svg

    def test_viewbox_matches_requested_size(self):
        svg = to_svg(from_byte(1), size=500)
        assert 'viewBox="0 0 500 500"' in svg

    def test_illegibly_small_rejected(self):
        with pytest.raises(ValueError):
            to_svg(from_byte(0), size=40)

    def test_no_raw_angle_brackets_from_names(self):
        for o in all_odu():
            body = re.sub(r"<[^>]+>", "", to_svg(o))
            assert "<" not in body and ">" not in body


class TestContactSheet:
    def test_yields_all_256(self):
        pairs = list(each_figure_svg())
        assert len(pairs) == 256
        assert [o.byte for o, _ in pairs] == list(range(256))
