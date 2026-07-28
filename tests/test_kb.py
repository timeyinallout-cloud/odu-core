"""Tests for the knowledge base.

The schema's job is to make unsourced or unlicensed content impossible rather
than merely discouraged, so most of these assert that bad inserts are *refused*.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from odu_core.kb import (  # noqa: E402
    KbError,
    add_contributor,
    add_note,
    add_source,
    add_translation,
    add_verse,
    coverage,
    open_kb,
    publishable_for,
    stats,
    verses_for,
)


@pytest.fixture
def db():
    conn = open_kb(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def open_source(db):
    """A source whose text may be reproduced."""
    return add_source(
        db, kind="oral-contribution", title="Field notes", rights="contributor-licensed"
    )


@pytest.fixture
def closed_source(db):
    """A citable but copyrighted source."""
    return add_source(
        db, kind="book", title="Ifa Divination", author="William Bascom",
        year=1969, rights="all-rights-reserved",
    )


class TestSources:
    def test_copyright_blocks_reproduction_by_default(self, db, closed_source):
        row = db.execute("SELECT * FROM source WHERE id=?", (closed_source,)).fetchone()
        assert row["reproduction_allowed"] == 0

    def test_open_rights_allow_reproduction_by_default(self, db, open_source):
        row = db.execute("SELECT * FROM source WHERE id=?", (open_source,)).fetchone()
        assert row["reproduction_allowed"] == 1

    def test_cannot_claim_reproduction_against_restrictive_rights(self, db):
        with pytest.raises(KbError, match="does not permit reproduction"):
            add_source(
                db, kind="book", title="Something", rights="all-rights-reserved",
                reproduction_allowed=True,
            )

    def test_untitled_source_rejected(self, db):
        with pytest.raises(KbError):
            add_source(db, kind="book", title="   ", rights="public-domain")

    def test_unknown_rights_value_rejected(self, db):
        with pytest.raises(sqlite3.IntegrityError):
            add_source(db, kind="book", title="X", rights="whatever-i-like")


class TestVerses:
    def test_verse_requires_an_existing_source(self, db):
        with pytest.raises(KbError, match="no source"):
            add_verse(db, odu_byte=255, source_id=999, page_reference="p. 1")

    def test_verse_needs_text_or_a_citation(self, db, open_source):
        with pytest.raises(KbError, match="asserts nothing"):
            add_verse(db, odu_byte=255, source_id=open_source)

    def test_copyrighted_source_permits_citation(self, db, closed_source):
        vid = add_verse(
            db, odu_byte=255, source_id=closed_source, page_reference="p. 314"
        )
        assert vid > 0

    def test_copyrighted_source_refuses_reproduced_text(self, db, closed_source):
        with pytest.raises(KbError, match="does not permit reproduction"):
            add_verse(
                db, odu_byte=255, source_id=closed_source,
                yoruba_text="…", page_reference="p. 314",
            )

    def test_licensed_source_accepts_text(self, db, open_source):
        vid = add_verse(db, odu_byte=0, source_id=open_source, yoruba_text="…")
        assert vid > 0

    @pytest.mark.parametrize("bad", [-1, 256, 999])
    def test_byte_outside_the_256_rejected(self, db, open_source, bad):
        with pytest.raises(KbError, match="not a valid figure"):
            add_verse(db, odu_byte=bad, source_id=open_source, page_reference="p. 1")

    def test_source_cannot_be_deleted_out_from_under_a_verse(self, db, open_source):
        add_verse(db, odu_byte=1, source_id=open_source, yoruba_text="…")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("DELETE FROM source WHERE id=?", (open_source,))


class TestPublishing:
    def test_draft_verses_are_not_publishable(self, db, open_source):
        add_verse(db, odu_byte=5, source_id=open_source, yoruba_text="…")
        assert publishable_for(db, 5) == []

    def test_published_verse_appears(self, db, open_source):
        add_verse(
            db, odu_byte=5, source_id=open_source, yoruba_text="…", status="published"
        )
        assert len(publishable_for(db, 5)) == 1

    def test_restricted_material_never_publishes(self, db, open_source):
        add_verse(
            db, odu_byte=6, source_id=open_source, yoruba_text="…",
            status="published", restricted=True,
        )
        assert publishable_for(db, 6) == []
        assert len(verses_for(db, 6)) == 1  # retained for scholarship

    def test_citation_only_record_publishes_without_reproducing(self, db, closed_source):
        add_verse(
            db, odu_byte=7, source_id=closed_source,
            page_reference="p. 314", status="published",
        )
        rows = publishable_for(db, 7)
        assert len(rows) == 1
        assert rows[0]["yoruba_text"] is None

    def test_withdrawn_consent_retracts_published_content(self, db, open_source):
        cid = add_contributor(db, name="A. Contributor", consent_status="granted")
        add_verse(
            db, odu_byte=8, source_id=open_source, yoruba_text="…",
            contributor_id=cid, status="published",
        )
        assert len(publishable_for(db, 8)) == 1

        db.execute(
            "UPDATE contributor SET consent_status='withdrawn' WHERE id=?", (cid,)
        )
        assert publishable_for(db, 8) == []

    def test_pending_consent_does_not_publish(self, db, open_source):
        cid = add_contributor(db, name="B. Contributor", consent_status="pending")
        add_verse(
            db, odu_byte=9, source_id=open_source, yoruba_text="…",
            contributor_id=cid, status="published",
        )
        assert publishable_for(db, 9) == []


class TestTranslations:
    def test_translation_needs_a_real_verse(self, db, open_source):
        with pytest.raises(KbError, match="no verse"):
            add_translation(
                db, verse_id=42, language="en", text="…", source_id=open_source
            )

    def test_copyrighted_translation_refused(self, db, open_source, closed_source):
        vid = add_verse(db, odu_byte=2, source_id=open_source, yoruba_text="…")
        with pytest.raises(KbError, match="does not permit reproduction"):
            add_translation(
                db, verse_id=vid, language="en", text="…", source_id=closed_source
            )

    def test_translation_dies_with_its_verse(self, db, open_source):
        vid = add_verse(db, odu_byte=3, source_id=open_source, yoruba_text="…")
        add_translation(
            db, verse_id=vid, language="en", text="…", source_id=open_source
        )
        db.execute("DELETE FROM verse WHERE id=?", (vid,))
        assert db.execute("SELECT COUNT(*) FROM translation").fetchone()[0] == 0


class TestNotes:
    def test_note_requires_a_source(self, db):
        with pytest.raises(KbError, match="no source"):
            add_note(db, odu_byte=1, kind="commentary", text="…", source_id=999)

    def test_note_kind_is_constrained(self, db, open_source):
        with pytest.raises(sqlite3.IntegrityError):
            add_note(
                db, odu_byte=1, kind="vibes", text="…", source_id=open_source
            )


class TestReporting:
    def test_coverage_reports_all_256_figures(self, db):
        assert len(coverage(db)) == 256
        assert set(coverage(db).values()) == {0}

    def test_coverage_counts_entries(self, db, open_source):
        add_verse(db, odu_byte=100, source_id=open_source, yoruba_text="…")
        add_verse(db, odu_byte=100, source_id=open_source, yoruba_text="…")
        assert coverage(db)[100] == 2

    def test_stats_start_empty(self, db):
        s = stats(db)
        assert s["verses"] == 0
        assert s["figures_covered"] == 0
        assert s["figures_total"] == 256

    def test_stats_distinguish_stored_from_publishable(self, db, open_source):
        add_verse(db, odu_byte=11, source_id=open_source, yoruba_text="…")
        s = stats(db)
        assert s["verses"] == 1
        assert s["verses_publishable"] == 0


class TestNamesAreFactsNotExpression:
    """A proper name is not an expressive work; commentary is.

    The distinction matters because most published Ifá scholarship is in
    copyright. Being unable to record that a figure is *called* something would
    make the naming data unusable, while reproducing commentary from the same
    page would be a real infringement.
    """

    def test_attested_name_publishes_from_a_copyrighted_source(self, db, closed_source):
        add_note(
            db, odu_byte=240, kind="alternative-name", text="Ogbe Yẹku",
            source_id=closed_source, status="published",
        )
        rows = db.execute(
            "SELECT * FROM publishable_note WHERE odu_byte=240"
        ).fetchall()
        assert len(rows) == 1
        assert rows[0]["text"] == "Ogbe Yẹku"

    @pytest.mark.parametrize(
        "kind", ["commentary", "etymology", "taboo", "regional-variant", "association"]
    )
    def test_every_other_kind_stays_gated(self, db, closed_source, kind):
        add_note(
            db, odu_byte=241, kind=kind, text="…", source_id=closed_source,
            status="published",
        )
        assert db.execute(
            "SELECT COUNT(*) FROM publishable_note WHERE odu_byte=241"
        ).fetchone()[0] == 0

    def test_draft_names_still_do_not_publish(self, db, closed_source):
        add_note(
            db, odu_byte=242, kind="alternative-name", text="…",
            source_id=closed_source, status="draft",
        )
        assert db.execute(
            "SELECT COUNT(*) FROM publishable_note WHERE odu_byte=242"
        ).fetchone()[0] == 0


class TestRecordings:
    """A recording is a pointer, which is why it can exist where text cannot."""

    def test_recording_needs_a_source(self, db):
        from odu_core.kb import add_recording

        with pytest.raises(KbError, match="no source"):
            add_recording(db, path="https://example.com/v", source_id=999, odu_byte=255)

    def test_recording_must_attach_to_something(self, db, closed_source):
        from odu_core.kb import add_recording

        with pytest.raises(KbError, match="figure or a verse"):
            add_recording(db, path="https://example.com/v", source_id=closed_source)

    def test_recording_needs_a_path(self, db, closed_source):
        from odu_core.kb import add_recording

        with pytest.raises(KbError, match="path or URL"):
            add_recording(db, path="  ", source_id=closed_source, odu_byte=255)

    def test_pointer_stores_from_a_copyrighted_source(self, db, closed_source):
        from odu_core.kb import add_recording

        # Citing where a recitation can be heard reproduces nothing, so unlike
        # verse text this is allowed against a rights-reserved source.
        rid = add_recording(
            db, path="https://example.com/v", source_id=closed_source, odu_byte=255
        )
        assert rid > 0

    def test_draft_recordings_do_not_publish(self, db, closed_source):
        from odu_core.kb import add_recording

        add_recording(
            db, path="https://example.com/v", source_id=closed_source,
            odu_byte=255, status="draft",
        )
        assert db.execute(
            "SELECT COUNT(*) FROM publishable_recording"
        ).fetchone()[0] == 0

    def test_published_recording_still_gated_on_reproduction(self, db, closed_source):
        from odu_core.kb import add_recording

        add_recording(
            db, path="https://example.com/v", source_id=closed_source,
            odu_byte=255, status="published",
        )
        assert db.execute(
            "SELECT COUNT(*) FROM publishable_recording"
        ).fetchone()[0] == 0

    @pytest.mark.parametrize("bad", [-1, 256])
    def test_recording_byte_validated(self, db, closed_source, bad):
        from odu_core.kb import add_recording

        with pytest.raises(KbError, match="not a valid figure"):
            add_recording(db, path="https://x/v", source_id=closed_source, odu_byte=bad)
