#!/usr/bin/env python3
"""Create ``kb/odu.db`` and seed it with bibliographic records.

    python3 scripts/init_kb.py [--force]

What this seeds is *sources*, not content. A bibliographic record — that a book
exists, who wrote it, when — is a fact about the book and is safe to assert.
The verses inside those books are not, and none are inserted here.

The corpus therefore starts empty on purpose. Filling it means sitting with the
sources and entering records one at a time, with page references, which is the
slow part of the project and the part that cannot be automated or guessed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from odu_core.kb import add_source, open_kb, stats  # noqa: E402

DB_PATH = ROOT / "kb" / "odu.db"

# Both of these are in copyright. They are seeded as *citable* sources with
# reproduction_allowed = 0, which is exactly the case the schema exists to
# handle: a verse from either may be recorded as a page reference, never as
# reproduced text. Publication details should be checked against a physical
# copy before this database is treated as a bibliography.
SEED_SOURCES = [
    {
        "kind": "book",
        "title": "Ifa Divination: Communication Between Gods and Men in West Africa",
        "author": "William R. Bascom",
        "year": 1969,
        "publisher": "Indiana University Press",
        "rights": "all-rights-reserved",
        "notes": (
            "Primary reference for the figures and their ordering. Verify the "
            "bit patterns in data/principal_odu.json against this. Publication "
            "details unverified against a physical copy."
        ),
    },
    {
        "kind": "book",
        "title": "Ifá: An Exposition of Ifá Literary Corpus",
        "author": "Wande Abimbola",
        "year": 1976,
        "publisher": "Oxford University Press",
        "rights": "all-rights-reserved",
        "notes": (
            "Published ẹsẹ Ifá with translations. Cite by page; do not "
            "reproduce. Publication details unverified against a physical copy."
        ),
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="recreate even if the database exists"
    )
    args = parser.parse_args()

    if DB_PATH.exists() and not args.force:
        print(f"{DB_PATH.relative_to(ROOT)} already exists — use --force to recreate")
        return 1
    if DB_PATH.exists():
        DB_PATH.unlink()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = open_kb(DB_PATH)
    for source in SEED_SOURCES:
        add_source(db, **source)

    summary = stats(db)
    print(f"created {DB_PATH.relative_to(ROOT)}")
    print(f"  sources        {summary['sources']}")
    print(f"  verses         {summary['verses']}  (empty by design — see the docstring)")
    print(f"  figures covered {summary['figures_covered']} of {summary['figures_total']}")
    db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
