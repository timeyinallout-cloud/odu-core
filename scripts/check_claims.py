#!/usr/bin/env python3
"""Check that numbers stated in the documentation are still true.

    python3 scripts/check_claims.py

Documentation goes stale silently. The staleness gate in CI compares generated
files against their sources, but nothing catches a sentence that was true when
written and is not any more — a README claiming 129 tests, a roadmap counting
221 unnamed figures when there are 202, a release guide saying the project is
unpublished after it has been published.

Ten such claims were found by hand on 2026-08-01. This makes the checkable
subset automatic. It cannot judge prose, so `docs/audit.md` covers the rest.

Every claim below is a regex over the docs paired with a live value. A match
that disagrees fails the run; a claim with no match at all also fails, because
that means the sentence was reworded and the check is no longer watching
anything.
"""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def live_values() -> dict[str, int | str]:
    """Compute what is actually true right now."""
    from odu_core.data import verification_summary

    dataset = json.loads((ROOT / "data" / "odu_256.json").read_text(encoding="utf-8"))
    named = sum(1 for o in dataset["odu"] if o["traditionalName"])

    db = ROOT / "kb" / "odu.db"
    citations = sources = 0
    if db.exists():
        con = sqlite3.connect(db)
        citations = con.execute("SELECT COUNT(*) FROM verse").fetchone()[0]
        sources = con.execute("SELECT COUNT(*) FROM source").fetchone()[0]
        con.close()

    py = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--collect-only"],
        cwd=ROOT, capture_output=True, text=True,
    )
    n_py = re.search(r"(\d+) tests? collected", py.stdout)

    ts_dir = ROOT / "ts" / "test"
    n_ts = sum(
        len(re.findall(r"^test\(", f.read_text(encoding="utf-8"), re.M))
        for f in ts_dir.glob("*.test.js")
    ) if ts_dir.exists() else 0

    v = verification_summary()
    return {
        "python_tests": int(n_py.group(1)) if n_py else -1,
        "ts_tests": n_ts,
        "named": named,
        "unnamed": 256 - named,
        "citations": citations,
        "sources": sources,
        "verified": v["verified"],
        "spec": dataset["specVersion"],
    }


# (file, human label, regex capturing one number, key into live_values)
CLAIMS: list[tuple[str, str, str, str]] = [
    ("README.md",          "test counts",      r"make test\s+# Python \((\d+)\)", "python_tests"),
    ("README.md",          "verified figures", r"\*\*(\d+) of 16\*\*|`(\d+) of 16`", "verified"),
    ("CONTRIBUTING.md",    "test counts",      r"make test\s+# (\d+) Python",      "python_tests"),
    ("CONTRIBUTING.md",    "figures sourced",  r"—\s*(\d+) of 256\s*—",            "named"),
    ("RELEASING.md",       "test counts",      r"make test\s+# (\d+) Python",      "python_tests"),
    ("RELEASING.md",       "names sourced",    r"(\d+) of 256 traditional names",  "named"),
    ("ROADMAP.md",         "citations",        r"\| (\d+) sourced verse citations", "citations"),
    ("ROADMAP.md",         "unnamed figures",  r"remaining (\d+) compound names",  "unnamed"),
    ("docs/content-plan.md", "names sourced",  r"names, at (\d+) of 256",          "named"),
]

# Phrases that were true once and would be false now. Any hit is a failure.
FORBIDDEN: list[tuple[str, str]] = [
    (r"bit patterns are unverified", "verification is complete"),
    (r"repository is local-only",    "the repository is public"),
    (r"nothing here is published",   "v1.0.0 is released"),
    (r"no remote",                   "a remote is configured"),
]

# docs/audit.md quotes the forbidden phrases as examples of what went stale —
# a file documenting the audit has to be able to name what it caught. Scripts
# and the changelog are historical narrative by design.
SKIP = {
    "CHANGELOG.md", "docs/scripts", "docs/audit.md",
    "docs/release-notes-", "data/", "ts/dist", "node_modules",
}


def check_ci_page() -> list[str]:
    """The published CI explainer must match the workflow it describes.

    It is prose about a YAML file, so it goes stale the moment a gate is added.
    That happened once: a seventh gate landed and the page still said six. The
    ordinary/provenance split had also been wrong since the page was written —
    the total was checked, the breakdown never was.
    """
    page = ROOT / "docs" / "ci-explained.html"
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if not page.exists() or not workflow.exists():
        return []

    html = page.read_text(encoding="utf-8")
    yml = workflow.read_text(encoding="utf-8")

    # Steps that are actual gates, not environment setup.
    steps = re.findall(r"^\s+- name: (.+)$", yml, re.M)
    gates = [s for s in steps if s.strip() != "Install"]

    blocks = re.findall(r'<div class="gate( provenance)?">', html)
    ordinary = sum(1 for b in blocks if not b)
    provenance = sum(1 for b in blocks if b)

    words = {3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight"}
    out = []
    if len(blocks) != len(gates):
        out.append(
            f"docs/ci-explained.html: describes {len(blocks)} gates, the workflow "
            f"runs {len(gates)} ({', '.join(gates)})"
        )
    stated = re.search(
        r"(\w+) gates run in order.*?(\w+) are ordinary.*?(\w+) exist", html, re.S
    )
    if not stated:
        out.append("docs/ci-explained.html: gate summary sentence not found")
    else:
        total, ordn, prov = stated.groups()
        if (total, ordn, prov) != (words.get(len(blocks)), words.get(ordinary),
                                   words.get(provenance)):
            out.append(
                f"docs/ci-explained.html: says {total}/{ordn} ordinary/{prov} "
                f"provenance, body has {words.get(len(blocks))}/"
                f"{words.get(ordinary)}/{words.get(provenance)}"
            )
    return out


def main() -> int:
    live = live_values()
    problems: list[str] = []

    for filename, label, pattern, key in CLAIMS:
        path = ROOT / filename
        if not path.exists():
            problems.append(f"{filename}: missing, but a claim is registered for it")
            continue
        text = path.read_text(encoding="utf-8")
        found = [g for m in re.finditer(pattern, text) for g in m.groups() if g]
        if not found:
            problems.append(
                f"{filename}: no {label} claim found — the wording changed, so this "
                f"check is watching nothing. Update CLAIMS in check_claims.py."
            )
            continue
        expected = str(live[key])
        for got in found:
            if got != expected:
                problems.append(
                    f"{filename}: {label} says {got}, actual is {expected}"
                )

    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).as_posix()
        if any(s in rel for s in SKIP):
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern, why in FORBIDDEN:
            if re.search(pattern, text):
                problems.append(f"{rel}: contains {pattern!r} — {why}")

    problems.extend(check_ci_page())

    print("live values:", ", ".join(f"{k}={v}" for k, v in live.items()))
    print()
    if problems:
        print(f"{len(problems)} stale claim(s):\n", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        print(
            "\nFix the prose, or update CLAIMS if the wording legitimately changed.",
            file=sys.stderr,
        )
        return 1

    print(f"all {len(CLAIMS)} registered claims match, no forbidden phrases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
