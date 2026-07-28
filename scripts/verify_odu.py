#!/usr/bin/env python3
"""Record that a figure's bit pattern was checked against a primary source.

    python3 scripts/verify_odu.py --status                 # what's still open
    python3 scripts/verify_odu.py ogbe \\
        --against "Bascom 1969, Table 1, p. 44" --by "Your Name"
    python3 scripts/verify_odu.py ika --dispute \\
        --against "Abimbola 1976, p. 27" --by "Your Name" \\
        --note "shows 0010, not 0100"

This exists because verification is the one part of the project that cannot be
automated or inferred — it needs a person with the book open. What *can* be
automated is tracking it, so the work is resumable and the current state is
always a fact rather than a memory.

Nothing here changes a bit pattern. Correcting one is a deliberate edit to
data/principal_odu.json followed by a spec bump, because it changes what every
byte value means.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "principal_odu.json"
sys.path.insert(0, str(ROOT / "src"))


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def save(payload: dict) -> None:
    DATA.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def show_status(payload: dict) -> int:
    entries = payload["odu"]
    width = max(len(o["name"]) for o in entries)
    counts: dict[str, int] = {}

    for o in entries:
        v = o.get("verification") or {}
        status = v.get("status", "unverified")
        counts[status] = counts.get(status, 0) + 1
        mark = {"verified": "✓", "disputed": "!", "unverified": "·"}.get(status, "?")
        detail = v.get("checkedAgainst") or ""
        if v.get("note"):
            detail = f"{detail} — {v['note']}" if detail else v["note"]
        print(f"  {mark} {o['name']:<{width}}  {o['nibble']:04b}  {detail}")

    print()
    total = len(entries)
    verified = counts.get("verified", 0)
    print(f"  {verified} of {total} verified", end="")
    if counts.get("disputed"):
        print(f", {counts['disputed']} disputed", end="")
    print(f", {counts.get('unverified', 0)} still to check.")

    if verified < total:
        print("\n  Accepted sources:")
        for src in payload.get("verification", {}).get("acceptedSources", []):
            print(f"    - {src}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("slug", nargs="?", help="which figure, e.g. ogbe")
    parser.add_argument("--status", action="store_true", help="show progress and exit")
    parser.add_argument("--against", help="the source and page consulted")
    parser.add_argument("--by", help="who checked it")
    parser.add_argument("--note", help="anything worth recording")
    parser.add_argument("--dispute", action="store_true",
                        help="mark as disputed rather than verified")
    parser.add_argument("--reset", action="store_true", help="return it to unverified")
    args = parser.parse_args()

    payload = load()
    if args.status or not args.slug:
        return show_status(payload)

    entry = next((o for o in payload["odu"] if o["slug"] == args.slug), None)
    if entry is None:
        slugs = ", ".join(o["slug"] for o in payload["odu"])
        print(f"no figure with slug {args.slug!r}. One of: {slugs}", file=sys.stderr)
        return 1

    if args.reset:
        entry["verification"] = {
            "status": "unverified", "checkedAgainst": None,
            "checkedOn": None, "checkedBy": None, "note": None,
        }
        save(payload)
        print(f"reset {entry['name']} to unverified")
        return 0

    # A verification without a citation is just an assertion, which is the
    # thing this whole project is built to avoid.
    if not args.against or not args.by:
        print("--against and --by are both required: a verification without a "
              "source and a name records nothing checkable", file=sys.stderr)
        return 1

    entry["verification"] = {
        "status": "disputed" if args.dispute else "verified",
        "checkedAgainst": args.against,
        "checkedOn": date.today().isoformat(),
        "checkedBy": args.by,
        "note": args.note,
    }
    save(payload)

    verb = "disputed" if args.dispute else "verified"
    print(f"{entry['name']} ({entry['nibble']:>2}, {entry['nibble']:04b}) marked {verb}")
    print(f"  against  {args.against}")
    print(f"  by       {args.by}")
    print("\nRegenerate derived files:  make build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
