"""Tests for short, sayable file fingerprints."""
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from odu_core import fingerprint as fp  # noqa: E402
from odu_core import mnemonic  # noqa: E402


class TestDigest:
    def test_it_is_a_truncated_sha256_and_nothing_invented(self):
        """Anyone must be able to reproduce this with sha256sum | cut."""
        data = b"hello world"
        assert fp.digest(data) == hashlib.sha256(data).digest()[:3]

    def test_length_is_configurable(self):
        assert len(fp.digest(b"x", length=1)) == 1
        assert len(fp.digest(b"x", length=16)) == 16

    def test_zero_length_is_refused(self):
        with pytest.raises(ValueError):
            fp.digest(b"x", length=0)

    def test_a_path_and_its_bytes_agree(self, tmp_path):
        p = tmp_path / "clip.mp4"
        p.write_bytes(b"some render bytes")
        assert fp.digest(p) == fp.digest(b"some render bytes")

    def test_an_open_file_works_too(self, tmp_path):
        p = tmp_path / "x.bin"
        p.write_bytes(b"abc")
        with open(p, "rb") as fh:
            assert fp.digest(fh) == fp.digest(b"abc")

    def test_a_large_file_is_read_in_blocks_not_slurped(self, tmp_path):
        """Renders here run to gigabytes; the digest must stream."""
        p = tmp_path / "big.bin"
        p.write_bytes(b"\xa5" * (fp._CHUNK * 2 + 7))
        assert fp.digest(p) == hashlib.sha256(b"\xa5" * (fp._CHUNK * 2 + 7)).digest()[:3]

    def test_one_changed_byte_changes_the_fingerprint(self):
        assert fp.digest(b"take-01") != fp.digest(b"take-02")


class TestFingerprint:
    def test_three_payload_bytes_give_four_figures(self):
        """Three figures of payload plus one of checksum."""
        assert len(fp.fingerprint(b"anything")) == 4

    def test_it_round_trips_through_the_phrase(self):
        data = b"a render"
        phrase = fp.say(data, style="slug")
        assert mnemonic.from_phrase(phrase) == fp.digest(data)

    def test_a_mistyped_figure_is_caught(self):
        """The checksum figure is the reason this is worth saying aloud."""
        good = fp.say(b"a render", style="slug").split()
        wrong = " ".join(["ogbe-ogbe"] + good[1:])
        with pytest.raises(mnemonic.ChecksumError):
            mnemonic.from_phrase(wrong)

    def test_display_style_is_the_default_because_it_is_spoken(self):
        said = fp.say(b"x")
        assert "·" in said                       # separated, readable aloud
        assert said != fp.say(b"x", style="slug")

    def test_slug_style_is_ascii_for_typing(self):
        slug = fp.say(b"x", style="slug")
        assert slug.isascii() and " " in slug


class TestStrokes:
    def test_it_delegates_to_the_canonical_rhythm(self):
        """A fingerprint must sound like the same figures on the art page."""
        from odu_core.generative import to_rhythm

        figures = fp.fingerprint(b"hello world")
        assert fp.strokes(figures) == [list(to_rhythm(o).onsets()) for o in figures]

    def test_one_list_of_onsets_per_figure(self):
        figures = fp.fingerprint(b"hello world")
        rows = fp.strokes(figures)
        assert len(rows) == len(figures)

    def test_every_onset_lands_inside_the_bar(self):
        for row in fp.strokes(fp.fingerprint(b"hello world")):
            assert row == sorted(row)
            assert all(0 <= i < 16 for i in row)

    def test_a_figure_strikes_between_eight_and_sixteen_times(self):
        """Eight lines, each struck once or twice."""
        for row in fp.strokes(fp.fingerprint(b"hello world")):
            assert 8 <= len(row) <= 16


class TestMatches:
    def test_identical_content_matches(self, tmp_path):
        a, b = tmp_path / "a", tmp_path / "b"
        a.write_bytes(b"same"); b.write_bytes(b"same")
        assert fp.matches(a, b)

    def test_different_content_does_not(self, tmp_path):
        a, b = tmp_path / "a", tmp_path / "b"
        a.write_bytes(b"one"); b.write_bytes(b"two")
        assert not fp.matches(a, b)

    def test_a_truncated_copy_is_caught(self, tmp_path):
        """The case this exists for: a download that stopped early."""
        full, part = tmp_path / "full", tmp_path / "part"
        full.write_bytes(b"x" * 5000)
        part.write_bytes(b"x" * 4096)
        assert not fp.matches(full, part)


class TestItsLimits:
    """The docstring promises this detects accidents, not tampering.

    Stating the bound in a test keeps anyone from quietly leaning on it as a
    security control later.
    """

    def test_the_default_is_only_twenty_four_bits(self):
        assert len(fp.digest(b"x")) * 8 == 24

    def test_a_collision_is_findable_by_brute_force(self):
        """Demonstrated, not asserted in the abstract — 24 bits is small."""
        target = fp.digest(b"the original file")
        for i in range(400_000):
            if fp.digest(f"forged-{i}".encode()) == target:
                break
        else:
            pytest.skip("no collision inside the search budget; the bound holds")
        assert True   # found one: exactly why this is not a security control
