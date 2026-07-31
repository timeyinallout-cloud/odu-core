#!/usr/bin/env python3
"""Rebuild ``kb/odu.db`` from the versioned content files in ``kb/content/``.

    python3 scripts/ingest.py            # rebuild the database
    python3 scripts/ingest.py --check    # validate only, write nothing

The content files are the corpus; the database is a derived index. This script
is the only thing that writes it, and it rebuilds from scratch every time, so
the database can never drift from the text or hold a record that no file
accounts for.

Every error is collected rather than raised on the first one — someone entering
a batch of verses should see everything wrong with it in one pass.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from odu_core.core import from_byte, principal  # noqa: E402
from odu_core.kb import (  # noqa: E402
    REPRODUCIBLE_RIGHTS,
    add_contributor,
    add_note,
    add_recording,
    add_source,
    add_translation,
    add_verse,
    open_kb,
    stats,
)

CONTENT = ROOT / "kb" / "content"
DB_PATH = ROOT / "kb" / "odu.db"


def show(path: Path) -> str:
    """Path relative to the repo when it is inside it, absolute otherwise."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


class Problems:
    """Collects validation failures so all of them surface in one run."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, where: Path | str, message: str) -> None:
        location = show(where) if isinstance(where, Path) else where
        self.items.append(f"{location}: {message}")

    def __bool__(self) -> bool:
        return bool(self.items)


def resolve_odu(ref: Any) -> int:
    """Turn a slug, byte, or name from a content file into a byte value.

    Resolving through odu-core rather than trusting the file means a typo fails
    the ingest instead of quietly attaching a verse to the wrong figure.
    """
    if isinstance(ref, bool):
        raise ValueError(f"{ref!r} is not a figure reference")
    if isinstance(ref, int):
        return from_byte(ref).byte
    if not isinstance(ref, str):
        raise ValueError(f"{ref!r} is not a figure reference")

    text = ref.strip()
    if text.isdigit():
        return from_byte(int(text)).byte

    parts = text.split("-") if "-" in text else text.split()
    if len(parts) != 2:
        raise ValueError(
            f"{ref!r} is not a figure — use a slug like 'ogbe-oyeku', a byte, "
            f"or a full name"
        )
    right, left = principal(parts[0]), principal(parts[1])
    return (right.nibble << 4) | left.nibble


def load_json(path: Path, problems: Problems) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        problems.add(path, f"invalid JSON — {exc}")
        return None


def ingest_contributors(db, problems: Problems) -> dict[str, int]:
    """Load contributors.json, returning slug -> database id."""
    path = CONTENT / "contributors.json"
    if not path.exists():
        return {}

    payload = load_json(path, problems)
    if payload is None:
        return {}

    ids: dict[str, int] = {}
    for entry in payload.get("contributors", []):
        slug = entry.get("slug")
        if not slug:
            problems.add(path, f"contributor {entry.get('name', '?')!r} has no slug")
            continue
        if slug in ids:
            problems.add(path, f"duplicate contributor slug {slug!r}")
            continue
        if "consentStatus" not in entry:
            problems.add(path, f"{slug}: consentStatus is required, never assumed")
            continue
        try:
            ids[slug] = add_contributor(
                db,
                name=entry["name"],
                consent_status=entry["consentStatus"],
                role=entry.get("role"),
                affiliation=entry.get("affiliation"),
                region=entry.get("region"),
                lineage=entry.get("lineage"),
                consent_terms=entry.get("consentTerms"),
                contact=entry.get("contact"),
                notes=entry.get("notes"),
            )
        except Exception as exc:  # noqa: BLE001 — reported, not swallowed
            problems.add(path, f"{slug}: {exc}")
    return ids


def ingest_source_file(db, path: Path, contributors: dict[str, int],
                       problems: Problems) -> None:
    payload = load_json(path, problems)
    if payload is None:
        return

    meta = payload.get("source")
    if not meta:
        problems.add(path, "no 'source' block — every file must name its source")
        return

    try:
        source_id = add_source(
            db,
            kind=meta["kind"],
            title=meta["title"],
            rights=meta["rights"],
            author=meta.get("author"),
            year=meta.get("year"),
            publisher=meta.get("publisher"),
            isbn=meta.get("isbn"),
            url=meta.get("url"),
            notes=meta.get("notes"),
        )
    except Exception as exc:  # noqa: BLE001
        problems.add(path, f"source: {exc}")
        return

    reproducible = meta["rights"] in REPRODUCIBLE_RIGHTS

    for i, verse in enumerate(payload.get("verses", [])):
        label = f"verses[{i}]"
        try:
            odu_byte = resolve_odu(verse.get("odu"))
        except (ValueError, KeyError) as exc:
            problems.add(path, f"{label}: {exc}")
            continue

        if verse.get("yorubaText") and not reproducible:
            problems.add(
                path,
                f"{label}: this source is {meta['rights']}, so its text cannot be "
                f"stored — use pageReference instead",
            )
            continue

        contributor_id = None
        if verse.get("contributor"):
            contributor_id = contributors.get(verse["contributor"])
            if contributor_id is None:
                problems.add(
                    path,
                    f"{label}: unknown contributor {verse['contributor']!r} — "
                    f"add them to contributors.json first",
                )
                continue

        try:
            verse_id = add_verse(
                db,
                odu_byte=odu_byte,
                source_id=source_id,
                yoruba_text=verse.get("yorubaText"),
                page_reference=verse.get("pageReference"),
                contributor_id=contributor_id,
                sequence=verse.get("sequence"),
                restricted=bool(verse.get("restricted", False)),
                status=verse.get("status", "draft"),
                notes=verse.get("notes"),
            )
        except Exception as exc:  # noqa: BLE001
            problems.add(path, f"{label}: {exc}")
            continue

        for j, tr in enumerate(verse.get("translations", [])):
            try:
                add_translation(
                    db,
                    verse_id=verse_id,
                    language=tr["language"],
                    text=tr["text"],
                    source_id=source_id,
                    translator=tr.get("translator"),
                    status=tr.get("status", "draft"),
                    notes=tr.get("notes"),
                )
            except Exception as exc:  # noqa: BLE001
                problems.add(path, f"{label}.translations[{j}]: {exc}")

    for i, rec in enumerate(payload.get("recordings", [])):
        label = f"recordings[{i}]"
        try:
            odu_byte = resolve_odu(rec.get("odu"))
            add_recording(
                db,
                path=rec["path"],
                source_id=source_id,
                odu_byte=odu_byte,
                duration_seconds=rec.get("durationSeconds"),
                recorded_on=rec.get("recordedOn"),
                location=rec.get("location"),
                restricted=bool(rec.get("restricted", False)),
                status=rec.get("status", "draft"),
                notes=rec.get("notes"),
            )
        except Exception as exc:  # noqa: BLE001
            problems.add(path, f"{label}: {exc}")

    for i, note in enumerate(payload.get("notes", [])):
        label = f"notes[{i}]"
        try:
            odu_byte = resolve_odu(note.get("odu"))
            add_note(
                db,
                odu_byte=odu_byte,
                kind=note["kind"],
                text=note["text"],
                source_id=source_id,
                language=note.get("language", "yo"),
                lineage=note.get("lineage"),
                region=note.get("region"),
                restricted=bool(note.get("restricted", False)),
                status=note.get("status", "draft"),
            )
        except Exception as exc:  # noqa: BLE001
            problems.add(path, f"{label}: {exc}")


def run(target: Path) -> tuple[Problems, dict[str, Any]]:
    problems = Problems()
    if not CONTENT.exists():
        problems.add("kb/content", "directory not found")
        return problems, {}

    if target.exists():
        target.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)

    db = open_kb(target)
    contributors = ingest_contributors(db, problems)

    source_files = sorted((CONTENT / "sources").glob("*.json"))
    if not source_files:
        problems.add("kb/content/sources", "no source files found")

    for path in source_files:
        ingest_source_file(db, path, contributors, problems)

    summary = stats(db)
    summary["source_files"] = len(source_files)
    db.close()
    return problems, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="validate the content files without writing the database")
    args = parser.parse_args()

    target = DB_PATH.with_suffix(".check.db") if args.check else DB_PATH
    problems, summary = run(target)

    if args.check and target.exists():
        target.unlink()

    if problems:
        print(f"{len(problems.items)} problem(s) found:\n", file=sys.stderr)
        for item in problems.items:
            print(f"  {item}", file=sys.stderr)
        return 1

    verb = "validated" if args.check else f"wrote {show(DB_PATH)}"
    print(f"{verb} — {summary['source_files']} source files, "
          f"{summary['sources']} sources, {summary['contributors']} contributors")
    print(f"  verses          {summary['verses']} "
          f"({summary['verses_publishable']} publishable)")
    print(f"  translations    {summary['translations']}")
    print(f"  notes           {summary['notes']}")
    print(f"  figures covered {summary['figures_covered']} of {summary['figures_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
