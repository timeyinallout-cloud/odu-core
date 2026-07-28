"""Knowledge base: sourced content keyed to the 256 figures.

Content is stored in SQLite against ``kb/schema.sql``. The schema does the
enforcing — ``source_id`` is NOT NULL on every content table, so an unattributed
verse cannot be inserted at all. This module adds the checks SQLite cannot
express: that a byte is a real figure, that consent is current, and that a
source permitting citation is not mistaken for one permitting republication.

    >>> db = open_kb(":memory:")
    >>> sid = add_source(db, kind="book", title="Ifa Divination",
    ...                  author="William Bascom", year=1969,
    ...                  rights="all-rights-reserved")
    >>> add_verse(db, odu_byte=255, source_id=sid, page_reference="p. 314")
    1

Note what that example does *not* do: it records where a verse lives without
reproducing it, because the source is under copyright.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from .core import from_byte
from .types import Odu

__all__ = [
    "open_kb",
    "add_source",
    "add_contributor",
    "add_verse",
    "add_translation",
    "add_note",
    "add_recording",
    "verses_for",
    "publishable_for",
    "coverage",
    "stats",
    "SCHEMA_PATH",
    "KbError",
]

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "kb" / "schema.sql"

REPRODUCIBLE_RIGHTS = {"public-domain", "cc-by", "cc-by-sa", "contributor-licensed"}
"""Rights values under which stored text may be republished."""


class KbError(ValueError):
    """A record was rejected before it reached the database."""


def open_kb(path: str | Path = "kb/odu.db") -> sqlite3.Connection:
    """Open (creating if needed) a knowledge base and apply the schema."""
    db = sqlite3.connect(str(path))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    if not SCHEMA_PATH.exists():
        raise KbError(f"schema not found at {SCHEMA_PATH}")
    db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    db.commit()
    return db


def _check_byte(odu_byte: int) -> Odu:
    try:
        return from_byte(odu_byte)
    except (ValueError, TypeError) as exc:
        raise KbError(f"not a valid figure: {exc}") from exc


def add_source(
    db: sqlite3.Connection,
    *,
    kind: str,
    title: str,
    rights: str,
    author: str | None = None,
    year: int | None = None,
    publisher: str | None = None,
    isbn: str | None = None,
    url: str | None = None,
    reproduction_allowed: bool | None = None,
    notes: str | None = None,
) -> int:
    """Record a source. Returns its id.

    ``reproduction_allowed`` defaults to whatever ``rights`` implies, so the
    permissive case has to be stated deliberately rather than reached by
    forgetting a keyword.
    """
    if not title.strip():
        raise KbError("a source needs a title")
    if reproduction_allowed is None:
        reproduction_allowed = rights in REPRODUCIBLE_RIGHTS
    if reproduction_allowed and rights not in REPRODUCIBLE_RIGHTS:
        raise KbError(
            f"rights={rights!r} does not permit reproduction — set it to one of "
            f"{sorted(REPRODUCIBLE_RIGHTS)} or leave reproduction_allowed unset"
        )

    cur = db.execute(
        """INSERT INTO source
           (kind, title, author, year, publisher, isbn, url, rights,
            reproduction_allowed, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (kind, title.strip(), author, year, publisher, isbn, url, rights,
         int(reproduction_allowed), notes),
    )
    db.commit()
    return int(cur.lastrowid)


def add_contributor(
    db: sqlite3.Connection,
    *,
    name: str,
    consent_status: str,
    role: str | None = None,
    affiliation: str | None = None,
    region: str | None = None,
    lineage: str | None = None,
    consent_terms: str | None = None,
    contact: str | None = None,
    notes: str | None = None,
) -> int:
    """Record a contributor. Consent status is required, never defaulted."""
    if not name.strip():
        raise KbError("a contributor needs a name")
    recorded = date.today().isoformat() if consent_status == "granted" else None
    cur = db.execute(
        """INSERT INTO contributor
           (name, role, affiliation, region, lineage, consent_status,
            consent_recorded_on, consent_terms, contact, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name.strip(), role, affiliation, region, lineage, consent_status,
         recorded, consent_terms, contact, notes),
    )
    db.commit()
    return int(cur.lastrowid)


def add_verse(
    db: sqlite3.Connection,
    *,
    odu_byte: int,
    source_id: int,
    yoruba_text: str | None = None,
    page_reference: str | None = None,
    contributor_id: int | None = None,
    sequence: int | None = None,
    restricted: bool = False,
    status: str = "draft",
    notes: str | None = None,
) -> int:
    """Record a verse, or a citation pointing at one. Returns its id."""
    _check_byte(odu_byte)
    if not yoruba_text and not page_reference:
        raise KbError(
            "a verse needs either its text or a page reference — a record with "
            "neither asserts nothing"
        )

    source = db.execute("SELECT * FROM source WHERE id = ?", (source_id,)).fetchone()
    if source is None:
        raise KbError(f"no source with id {source_id}")

    # Storing text from a source that forbids reproduction is the mistake this
    # project most needs to avoid, so it is refused rather than merely hidden.
    if yoruba_text and not source["reproduction_allowed"]:
        raise KbError(
            f"source {source_id} ({source['title']!r}, rights="
            f"{source['rights']}) does not permit reproduction. Store a "
            f"page_reference instead of the text."
        )

    cur = db.execute(
        """INSERT INTO verse
           (odu_byte, source_id, contributor_id, yoruba_text, page_reference,
            sequence, restricted, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (odu_byte, source_id, contributor_id, yoruba_text, page_reference,
         sequence, int(restricted), status, notes),
    )
    db.commit()
    return int(cur.lastrowid)


def add_translation(
    db: sqlite3.Connection,
    *,
    verse_id: int,
    language: str,
    text: str,
    source_id: int,
    translator: str | None = None,
    status: str = "draft",
    notes: str | None = None,
) -> int:
    """Record a translation of a verse."""
    if not text.strip():
        raise KbError("a translation needs text")
    if db.execute("SELECT 1 FROM verse WHERE id = ?", (verse_id,)).fetchone() is None:
        raise KbError(f"no verse with id {verse_id}")

    source = db.execute("SELECT * FROM source WHERE id = ?", (source_id,)).fetchone()
    if source is None:
        raise KbError(f"no source with id {source_id}")
    if not source["reproduction_allowed"]:
        raise KbError(
            f"source {source_id} ({source['title']!r}) does not permit "
            f"reproduction, so its translation cannot be stored"
        )

    cur = db.execute(
        """INSERT INTO translation
           (verse_id, language, text, translator, source_id, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (verse_id, language, text.strip(), translator, source_id, status, notes),
    )
    db.commit()
    return int(cur.lastrowid)


def add_note(
    db: sqlite3.Connection,
    *,
    odu_byte: int,
    kind: str,
    text: str,
    source_id: int,
    language: str = "yo",
    lineage: str | None = None,
    region: str | None = None,
    status: str = "draft",
) -> int:
    """Record commentary about a figure as a whole."""
    _check_byte(odu_byte)
    if not text.strip():
        raise KbError("a note needs text")
    if db.execute("SELECT 1 FROM source WHERE id = ?", (source_id,)).fetchone() is None:
        raise KbError(f"no source with id {source_id}")

    cur = db.execute(
        """INSERT INTO odu_note
           (odu_byte, kind, text, language, lineage, region, source_id, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (odu_byte, kind, text.strip(), language, lineage, region, source_id, status),
    )
    db.commit()
    return int(cur.lastrowid)


def add_recording(
    db: sqlite3.Connection,
    *,
    path: str,
    source_id: int,
    odu_byte: int | None = None,
    verse_id: int | None = None,
    duration_seconds: float | None = None,
    recorded_on: str | None = None,
    location: str | None = None,
    restricted: bool = False,
    status: str = "draft",
    notes: str | None = None,
) -> int:
    """Record where a recitation can be heard.

    ``path`` may be a local file or a URL. Storing a pointer to a public
    recording is a citation, not a reproduction — no audio is copied and no
    verse text is transcribed. That distinction is why this can hold material
    the corpus itself never could.
    """
    if not path.strip():
        raise KbError("a recording needs a path or URL")
    if odu_byte is None and verse_id is None:
        raise KbError("a recording must attach to a figure or a verse")
    if odu_byte is not None:
        _check_byte(odu_byte)
    if db.execute("SELECT 1 FROM source WHERE id = ?", (source_id,)).fetchone() is None:
        raise KbError(f"no source with id {source_id}")

    cur = db.execute(
        """INSERT INTO recording
           (verse_id, odu_byte, path, duration_seconds, recorded_on, location,
            source_id, restricted, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (verse_id, odu_byte, path.strip(), duration_seconds, recorded_on,
         location, source_id, int(restricted), status, notes),
    )
    db.commit()
    return int(cur.lastrowid)


def verses_for(db: sqlite3.Connection, odu_byte: int) -> list[sqlite3.Row]:
    """Every verse recorded for a figure, whatever its status."""
    _check_byte(odu_byte)
    return db.execute(
        "SELECT * FROM verse WHERE odu_byte = ? ORDER BY sequence, id", (odu_byte,)
    ).fetchall()


def publishable_for(db: sqlite3.Connection, odu_byte: int) -> list[sqlite3.Row]:
    """Only what may actually be shown publicly for a figure."""
    _check_byte(odu_byte)
    return db.execute(
        "SELECT * FROM publishable_verse WHERE odu_byte = ? ORDER BY sequence, id",
        (odu_byte,),
    ).fetchall()


def coverage(db: sqlite3.Connection) -> dict[int, int]:
    """Verse count per byte, for all 256 figures including the empty ones."""
    counts = {b: 0 for b in range(256)}
    for row in db.execute(
        "SELECT odu_byte, COUNT(*) AS n FROM verse GROUP BY odu_byte"
    ):
        counts[row["odu_byte"]] = row["n"]
    return counts


def stats(db: sqlite3.Connection) -> dict[str, Any]:
    """A summary of what the knowledge base currently holds."""
    def count(sql: str) -> int:
        return int(db.execute(sql).fetchone()[0])

    covered = sum(1 for n in coverage(db).values() if n)
    return {
        "sources": count("SELECT COUNT(*) FROM source"),
        "contributors": count("SELECT COUNT(*) FROM contributor"),
        "verses": count("SELECT COUNT(*) FROM verse"),
        "verses_publishable": count("SELECT COUNT(*) FROM publishable_verse"),
        "translations": count("SELECT COUNT(*) FROM translation"),
        "recordings": count("SELECT COUNT(*) FROM recording"),
        "notes": count("SELECT COUNT(*) FROM odu_note"),
        "figures_covered": covered,
        "figures_total": 256,
    }
