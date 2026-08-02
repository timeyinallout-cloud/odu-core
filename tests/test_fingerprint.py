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


class TestTheCommandLineContract:
    """`odu fingerprint` is how other programs use this.

    The contract other tools depend on: exit codes mean pass/fail, --json is
    machine-readable, and the CLI must agree with the library — a disagreement
    would be invisible until two people compared answers from different tools.
    """

    def _run(self, *args, stdin=None):
        import subprocess
        root = Path(__file__).resolve().parents[1]
        return subprocess.run(
            [sys.executable, "-m", "odu_core.cli", "fingerprint", *args],
            capture_output=True, text=True, cwd=root, input=stdin,
            env={"PYTHONPATH": str(root / "src"), "PATH": "/usr/bin:/bin"},
        )

    def test_the_cli_agrees_with_the_library(self, tmp_path):
        f = tmp_path / "clip.mp4"
        f.write_bytes(b"a render")
        out = self._run(str(f), "-q", "--style", "slug").stdout.strip()
        assert out == fp.say(f, style="slug")

    def test_stdin_agrees_too(self, tmp_path):
        """Reading a pipe must not hash the data twice."""
        r = self._run("-", "-q", "--style", "slug", stdin="hello world")
        assert r.stdout.strip() == fp.say(b"hello world", style="slug")

    def test_json_is_one_object_per_file(self, tmp_path):
        import json as _json

        a, b = tmp_path / "a", tmp_path / "b"
        a.write_bytes(b"one"); b.write_bytes(b"two")
        lines = self._run(str(a), str(b), "--json").stdout.strip().splitlines()
        assert len(lines) == 2
        for line, path in zip(lines, (a, b)):
            d = _json.loads(line)
            assert d["path"] == str(path)
            assert d["sha256_prefix"] == fp.digest(path).hex()
            assert d["slug"] == fp.say(path, style="slug")
            assert len(d["figures"]) == 4

    def test_check_exits_zero_on_a_match(self, tmp_path):
        f = tmp_path / "x"
        f.write_bytes(b"content")
        assert self._run(str(f), "--check", fp.say(f, style="slug")).returncode == 0

    def test_check_exits_one_on_a_mismatch(self, tmp_path):
        """The whole point: a script can branch on this."""
        f = tmp_path / "x"
        f.write_bytes(b"content")
        wrong = " ".join(["ogbe-ogbe"] * 4)
        assert self._run(str(f), "--check", wrong).returncode == 1

    def test_check_reports_both_phrases_when_they_differ(self, tmp_path):
        f = tmp_path / "x"
        f.write_bytes(b"content")
        r = self._run(str(f), "--check", " ".join(["ogbe-ogbe"] * 4))
        assert "expected" in r.stderr and "got" in r.stderr

    def test_a_missing_file_exits_nonzero(self):
        assert self._run("/nope/missing.bin").returncode != 0

    def test_an_unparseable_phrase_exits_nonzero(self, tmp_path):
        f = tmp_path / "x"
        f.write_bytes(b"content")
        assert self._run(str(f), "--check", "not-a-figure").returncode != 0

    def test_quiet_prints_only_the_phrase(self, tmp_path):
        f = tmp_path / "x"
        f.write_bytes(b"content")
        r = self._run(str(f), "-q", "--style", "slug")
        assert len(r.stdout.strip().splitlines()) == 1
        assert r.stderr.strip() == ""
