"""Tests for odu-core.

The mapping is small enough to test exhaustively — every assertion about the 256
figures checks all 256, so nothing here samples or spot-checks.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from odu_core import (  # noqa: E402
    all_odu,
    by_seniority,
    decode,
    encode,
    from_bits,
    from_byte,
    from_legs,
    principal,
    principal_odu,
    senior_of,
    to_ascii,
)


class TestPrincipalOdu:
    def test_there_are_sixteen(self):
        assert len(principal_odu()) == 16

    def test_legs_cover_every_nibble_exactly_once(self):
        # If two legs shared a bit pattern the byte mapping would not be a
        # bijection and some byte would decode to the wrong figure.
        assert sorted(o.nibble for o in principal_odu()) == list(range(16))

    def test_marks_agree_with_nibbles(self):
        for o in principal_odu():
            derived = int("".join("1" if m == "I" else "0" for m in o.marks), 2)
            assert derived == o.nibble, f"{o.name}: marks say {derived}, data says {o.nibble}"

    def test_ranks_are_one_to_sixteen(self):
        assert sorted(o.rank for o in principal_odu()) == list(range(1, 17))

    def test_ogbe_is_all_single_marks(self):
        ogbe = principal("ogbe")
        assert ogbe.marks == ("I", "I", "I", "I")
        assert ogbe.nibble == 15
        assert ogbe.rank == 1

    def test_oyeku_is_all_double_marks(self):
        oyeku = principal("oyeku")
        assert oyeku.marks == ("II", "II", "II", "II")
        assert oyeku.nibble == 0

    def test_seniority_pairs_are_complements_or_reversals(self):
        """Consecutive pairs in seniority order are structurally related.

        Each pair is either bitwise complementary or a bit-reversal of the
        other. This is a property of the traditional ordering, and it is the
        test most likely to catch a mis-transcribed figure — a wrong nibble
        breaks the relation for its pair while leaving every other check green.
        """
        odu = principal_odu()
        for i in range(0, 16, 2):
            a, b = odu[i], odu[i + 1]
            reversed_bits = int(f"{a.nibble:04b}"[::-1], 2)
            related = (a.nibble ^ 0b1111) == b.nibble or reversed_bits == b.nibble
            assert related, f"{a.name}/{b.name} are neither complements nor reversals"


class TestByteMapping:
    def test_round_trip_over_every_byte(self):
        for b in range(256):
            assert from_byte(b).byte == b

    def test_every_byte_gives_a_distinct_figure(self):
        assert len({o.slug for o in all_odu()}) == 256

    def test_right_leg_is_the_high_nibble(self):
        for o in all_odu():
            assert o.byte >> 4 == o.right.nibble
            assert o.byte & 0x0F == o.left.nibble

    def test_from_legs_matches_from_byte(self):
        for o in all_odu():
            assert from_legs(o.right.slug, o.left.slug) == o

    def test_from_bits_matches_from_byte(self):
        for b in range(256):
            assert from_bits(f"{b:08b}") == from_byte(b)

    def test_meji_figures_are_the_sixteen_doubles(self):
        meji = [o for o in all_odu() if o.is_meji]
        assert len(meji) == 16
        assert all(o.name.endswith("Méjì") or o.name.startswith("Èjì") for o in meji)

    def test_eji_ogbe_is_byte_255(self):
        assert from_byte(255).name == "Èjì Ogbè"

    def test_oyeku_meji_is_byte_zero(self):
        assert from_byte(0).name == "Ọ̀yẹ̀kú Méjì"

    @pytest.mark.parametrize("bad", [-1, 256, 1000])
    def test_out_of_range_bytes_rejected(self, bad):
        with pytest.raises(ValueError):
            from_byte(bad)

    def test_bools_rejected(self):
        # bool subclasses int; accepting it would silently encode True as 1.
        with pytest.raises(TypeError):
            from_byte(True)


class TestEncoding:
    def test_round_trips_arbitrary_bytes(self):
        payload = bytes(range(256)) + b"\x00\xff" * 8
        assert decode(encode(payload)) == payload

    def test_one_odu_per_byte(self):
        assert len(encode(b"hello world")) == 11

    def test_empty_input(self):
        assert encode(b"") == ()
        assert decode(()) == b""

    def test_thirty_two_byte_key(self):
        key = bytes(range(32))
        names = [o.name for o in encode(key)]
        assert len(names) == 32
        assert decode(encode(key)) == key


class TestSeniority:
    def test_covers_all_256_without_gaps(self):
        assert sorted(o.seniority_rank for o in all_odu()) == list(range(1, 257))

    def test_ogbe_meji_is_most_senior(self):
        assert by_seniority()[0].name == "Èjì Ogbè"

    def test_seniority_differs_from_numeric_order(self):
        # The whole reason the library indexes by bit pattern instead of rank.
        assert [o.byte for o in by_seniority()] != list(range(256))

    def test_senior_of_picks_the_higher_rank(self):
        ogbe, oyeku = from_byte(255), from_byte(0)
        assert senior_of(ogbe, oyeku) is ogbe
        assert senior_of(oyeku, ogbe) is ogbe


class TestOrthography:
    def test_canonical_names_are_nfc(self):
        for o in principal_odu():
            assert unicodedata.is_normalized("NFC", o.name)
            assert unicodedata.is_normalized("NFC", o.meji_name)

    def test_diacritics_are_preserved_in_canonical_data(self):
        # Guards against a well-meaning "cleanup" flattening the dataset.
        assert any(not o.name.isascii() for o in principal_odu())
        assert principal("oyeku").name != "Oyeku"

    def test_slugs_are_ascii_and_match_names(self):
        for o in principal_odu():
            assert o.slug.isascii()
            assert to_ascii(o.name) == o.slug

    def test_lookup_accepts_diacritic_and_ascii_forms(self):
        assert principal("Ọ̀yẹ̀kú") is principal("oyeku")
        assert principal("Ọ̀yẹ̀kú Méjì") is principal("oyeku")
        assert principal(0) is principal("oyeku")

    def test_to_ascii_strips_tone_and_subdots(self):
        assert to_ascii("Ọ̀wọ́nrín") == "owonrin"
        assert to_ascii("Òtúrúpọ̀n") == "oturupon"
        assert to_ascii("Ìrẹtẹ̀") == "irete"


class TestFigure:
    def test_renders_four_rows(self):
        assert len(from_byte(0).figure().splitlines()) == 4

    def test_single_and_double_marks_differ(self):
        assert from_byte(255).figure() != from_byte(0).figure()


class TestVerification:
    """The dataset's foundation is verified; these keep it honest."""

    def test_every_figure_is_verified(self):
        from odu_core.data import verification_summary

        s = verification_summary()
        assert s["complete"], f"{s['unverified']} figures still unverified"
        assert s["verified"] == 16

    def test_no_figure_claims_verification_without_a_source_and_checker(self):
        for o in principal_odu():
            if o.verification.status == "verified":
                assert o.verification.checked_against, f"{o.name}: no source"
                assert o.verification.checked_by, f"{o.name}: no checker"
                assert o.verification.checked_on, f"{o.name}: no date"

    def test_verified_against_a_named_accepted_source(self):
        from odu_core.data import verification_summary

        accepted = verification_summary()["accepted_sources"]
        assert accepted, "no accepted sources recorded"
        for o in principal_odu():
            if o.verification.status == "verified":
                assert any(
                    src.split(",")[0].split()[0] in o.verification.checked_against
                    for src in accepted
                ), f"{o.name} cites an unlisted source: {o.verification.checked_against}"


class TestTraditionalNames:
    """Attested compound names must reach the generated dataset, not just the KB."""

    def test_generated_dataset_carries_sourced_names(self):
        import json
        from odu_core.data import DATA_PATH

        generated = json.loads(
            (DATA_PATH.parent / "odu_256.json").read_text(encoding="utf-8")
        )
        named = [o for o in generated["odu"] if o["traditionalName"]]
        assert named, "no traditional names reached data/odu_256.json"
        assert len(named) == generated["namesSourced"]

    def test_every_name_carries_its_source(self):
        import json
        from odu_core.data import DATA_PATH

        generated = json.loads(
            (DATA_PATH.parent / "odu_256.json").read_text(encoding="utf-8")
        )
        for o in generated["odu"]:
            # A name without a citation is exactly what this project forbids.
            if o["traditionalName"]:
                assert o["traditionalNameSource"], f"{o['slug']}: name without source"
            else:
                assert o["traditionalNameSource"] is None

    def test_names_match_the_canonical_names_file(self):
        import json
        from odu_core.data import DATA_PATH

        names = json.loads(
            (DATA_PATH.parent / "compound_names.json").read_text(encoding="utf-8")
        )["names"]
        generated = json.loads(
            (DATA_PATH.parent / "odu_256.json").read_text(encoding="utf-8")
        )
        for o in generated["odu"]:
            expected = names.get(o["slug"], {}).get("traditionalName")
            assert o["traditionalName"] == expected, o["slug"]

    def test_attested_names_carry_tone_marks(self):
        """Yorùbá tone is meaningful; a tone-less name is a different word.

        The source (Bascom) omits tone marks, so these are composed: the
        naming is his, the tone comes from our own verified principal names.
        Losing it again would leave the corpus inconsistent with itself.
        """
        import json
        import unicodedata
        from odu_core.data import DATA_PATH

        names = json.loads(
            (DATA_PATH.parent / "compound_names.json").read_text(encoding="utf-8")
        )["names"]
        assert names, "no compound names recorded"
        for slug, entry in names.items():
            name = entry["traditionalName"]
            decomposed = unicodedata.normalize("NFD", name)
            assert any(unicodedata.combining(c) for c in decomposed), (
                f"{slug}: {name!r} has no tone marks"
            )
            assert unicodedata.is_normalized("NFC", name), f"{slug}: not NFC"

    def test_attested_name_starts_with_its_principal(self):
        """The head of an attested name is the first leg, unaltered."""
        import json
        from odu_core.data import DATA_PATH
        from odu_core import principal

        names = json.loads(
            (DATA_PATH.parent / "compound_names.json").read_text(encoding="utf-8")
        )["names"]
        for slug, entry in names.items():
            first = slug.split("-")[0]
            assert entry["traditionalName"].startswith(principal(first).name), (
                f"{slug}: {entry['traditionalName']!r} does not open with "
                f"{principal(first).name!r}"
            )

    def test_elided_form_is_a_variant_never_a_replacement(self):
        """Where a source marks elision, both forms are kept.

        The parenthesis in Bascom's ``Ogbe - (Ọ)yẹku`` marks a vowel that may
        drop in speech, not one missing from the name. Recording only the
        contraction would lose the name itself.
        """
        import json
        from odu_core.data import DATA_PATH

        names = json.loads(
            (DATA_PATH.parent / "compound_names.json").read_text(encoding="utf-8")
        )["names"]
        with_elision = {k: v for k, v in names.items() if v.get("elidedForm")}
        assert with_elision, "no elided variants recorded"
        for slug, entry in with_elision.items():
            full, elided = entry["traditionalName"], entry["elidedForm"]
            assert full != elided, f"{slug}: elided form duplicates the name"
            # The contraction is shorter precisely because a vowel dropped.
            assert len(elided) < len(full), f"{slug}: {elided!r} not shorter"
            head = full.split(" ")[0]
            assert elided.startswith(head), f"{slug}: heads differ"
