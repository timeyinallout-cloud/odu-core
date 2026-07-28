"""Tests for the mnemonic layer.

The checksum is the whole point of this layer, so most of these tests are about
corruption being caught rather than about happy-path round trips.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from odu_core.mnemonic import (  # noqa: E402
    ChecksumError,
    PhraseError,
    checksum_byte,
    format_phrase,
    from_phrase,
    parse_phrase,
    phrase_bits,
    to_phrase,
)


class TestRoundTrip:
    @pytest.mark.parametrize(
        "payload",
        [b"", b"\x00", b"\xff", b"hello world", bytes(range(256)), os.urandom(32)],
        ids=["empty", "zero", "max", "text", "all-bytes", "random-32"],
    )
    def test_bytes_survive_a_round_trip(self, payload):
        assert from_phrase(to_phrase(payload)) == payload

    def test_phrase_is_one_figure_longer_than_payload(self):
        assert len(to_phrase(b"abcd")) == 5

    def test_thirty_two_byte_key_is_thirty_three_figures(self):
        assert len(to_phrase(os.urandom(32))) == 33

    @pytest.mark.parametrize("style", ["slug", "display", "numbered"])
    def test_every_format_parses_back(self, style):
        payload = os.urandom(16)
        text = format_phrase(to_phrase(payload), style)
        assert from_phrase(text) == payload

    def test_round_trips_through_text_not_just_objects(self):
        payload = b"\xde\xad\xbe\xef"
        assert from_phrase(format_phrase(to_phrase(payload), "slug")) == payload


class TestChecksum:
    def test_dropped_figure_is_caught(self):
        figures = to_phrase(os.urandom(16))
        with pytest.raises(ChecksumError):
            from_phrase(figures[:-2] + figures[-1:])

    def test_transposed_figures_are_caught(self):
        figures = list(to_phrase(b"abcdefgh"))
        figures[0], figures[1] = figures[1], figures[0]
        with pytest.raises(ChecksumError):
            from_phrase(figures)

    def test_single_substituted_figure_is_caught(self):
        from odu_core import from_byte

        figures = list(to_phrase(b"abcdefgh"))
        figures[2] = from_byte((figures[2].byte + 1) % 256)
        with pytest.raises(ChecksumError):
            from_phrase(figures)

    def test_corruption_is_caught_across_many_random_trials(self):
        """Every single-figure corruption of a random phrase should be caught."""
        from odu_core import from_byte

        for _ in range(50):
            payload = os.urandom(8)
            figures = list(to_phrase(payload))
            i = os.urandom(1)[0] % len(figures)
            original = figures[i]
            figures[i] = from_byte((original.byte + 1 + os.urandom(1)[0] % 255) % 256)
            if figures[i].byte == original.byte:
                continue
            with pytest.raises(ChecksumError):
                from_phrase(figures)

    def test_checksum_is_deterministic(self):
        assert checksum_byte(b"hello") == checksum_byte(b"hello")

    def test_checksum_differs_for_different_payloads(self):
        assert checksum_byte(b"hello") != checksum_byte(b"hellp")

    def test_too_short_phrase_rejected(self):
        with pytest.raises(PhraseError):
            from_phrase([])


class TestParsing:
    def test_accepts_slug_form(self):
        payload = b"\x01\x02"
        assert from_phrase(format_phrase(to_phrase(payload), "slug")) == payload

    def test_accepts_display_form_with_separators(self):
        figures = to_phrase(b"\x01\x02")
        assert parse_phrase(format_phrase(figures, "display")) == figures

    def test_accepts_display_form_without_separators(self):
        figures = to_phrase(b"\x01\x02")
        plain = format_phrase(figures, "display").replace(" · ", " ")
        assert parse_phrase(plain) == figures

    def test_accepts_ascii_folded_names(self):
        figures = parse_phrase("Oyeku Meji Eji Ogbe")
        assert figures[0].byte == 0
        assert figures[1].byte == 255

    def test_accepts_meji_names(self):
        assert parse_phrase("Ọ̀yẹ̀kú Méjì")[0].byte == 0

    def test_tolerates_extra_whitespace_and_newlines(self):
        assert parse_phrase("  ogbe-ogbe \n\n oyeku-oyeku  ") == parse_phrase(
            "ogbe-ogbe oyeku-oyeku"
        )

    def test_numbered_form_strips_position_markers(self):
        figures = to_phrase(b"abc")
        assert parse_phrase(format_phrase(figures, "numbered")) == figures

    def test_empty_phrase_rejected(self):
        with pytest.raises(PhraseError):
            parse_phrase("   ")

    def test_unknown_figure_rejected(self):
        with pytest.raises(PhraseError):
            parse_phrase("notanodu-atall")

    def test_odd_word_count_rejected_with_guidance(self):
        with pytest.raises(PhraseError, match="two words"):
            parse_phrase("Ogbè Ọ̀yẹ̀kú Ìwòrì")

    def test_typo_gets_a_suggestion(self):
        with pytest.raises(PhraseError, match="Did you mean"):
            parse_phrase("ogbe-oyekk")


class TestReporting:
    def test_phrase_bits_excludes_the_checksum(self):
        assert phrase_bits(33) == 256
        assert phrase_bits(5) == 32

    def test_phrase_bits_never_negative(self):
        assert phrase_bits(0) == 0

    def test_slug_form_is_ascii(self):
        assert format_phrase(to_phrase(os.urandom(16)), "slug").isascii()

    def test_display_form_keeps_diacritics(self):
        assert not format_phrase(to_phrase(b"\x00"), "display").isascii()

    def test_numbered_form_has_one_line_per_figure(self):
        figures = to_phrase(os.urandom(10))
        assert len(format_phrase(figures, "numbered").splitlines()) == len(figures)

    def test_unknown_style_rejected(self):
        with pytest.raises(ValueError):
            format_phrase(to_phrase(b"x"), "hieroglyphs")  # type: ignore[arg-type]
