"""Loader for the canonical dataset.

``data/principal_odu.json`` is the single source of truth for this project. The
16 principal Odù are hand-curated there; everything else in the library — all
256 figures, every byte mapping, every ordering — is derived from it at import
time. Nothing is duplicated in code.
"""

from __future__ import annotations

import json
from functools import cache
from importlib import resources
from pathlib import Path
from typing import Any

from .orthography import is_normalized
from .types import PrincipalOdu, Verification

__all__ = [
    "principal_odu",
    "convention",
    "spec_version",
    "verification_summary",
    "DATA_PATH",
]


def _locate() -> Path:
    """Find the canonical JSON, whether running from a checkout or installed."""
    try:
        packaged = resources.files("odu_core") / "data" / "principal_odu.json"
        if packaged.is_file():
            return Path(str(packaged))
    except (ModuleNotFoundError, FileNotFoundError):
        pass
    return Path(__file__).resolve().parents[2] / "data" / "principal_odu.json"


DATA_PATH = _locate()


@cache
def _raw() -> dict[str, Any]:
    with DATA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


@cache
def spec_version() -> str:
    """The dataset's spec version.

    Downstream work (encoded data, generated art, mnemonics) is only meaningful
    against a known version — a change to the bit conventions changes what every
    byte value means.
    """
    return _raw()["specVersion"]


@cache
def convention() -> dict[str, Any]:
    """The four choices that determine the byte mapping. See the JSON's notes."""
    return dict(_raw()["convention"])


@cache
def verification_summary() -> dict[str, Any]:
    """How much of the canonical table has been checked against a source.

    The count is what matters: a project whose value rests on provenance should
    be able to state, at any moment, exactly how much of its foundation is
    still taken on trust.
    """
    figures = principal_odu()
    by_status: dict[str, list[str]] = {}
    for o in figures:
        by_status.setdefault(o.verification.status, []).append(o.name)

    verified = len(by_status.get("verified", []))
    return {
        "verified": verified,
        "unverified": len(by_status.get("unverified", [])),
        "disputed": len(by_status.get("disputed", [])),
        "total": len(figures),
        "complete": verified == len(figures),
        "by_status": by_status,
        "accepted_sources": _raw().get("verification", {}).get("acceptedSources", []),
    }


@cache
def principal_odu() -> tuple[PrincipalOdu, ...]:
    """The 16 principal Odù in traditional seniority order.

    Raises on any inconsistency in the source data rather than loading a table
    that would silently mis-encode every byte downstream.
    """
    entries = _raw()["odu"]
    if len(entries) != 16:
        raise ValueError(f"expected 16 principal Odù, found {len(entries)}")

    result = []
    for entry in entries:
        marks = tuple(entry["marks"])
        if len(marks) != 4 or any(m not in ("I", "II") for m in marks):
            raise ValueError(f"{entry['name']}: marks must be four of 'I' or 'II'")

        # The nibble is stored explicitly for readability, but it is fully
        # determined by the marks. Disagreement means the data is corrupt.
        derived = int("".join("1" if m == "I" else "0" for m in marks), 2)
        if derived != entry["nibble"]:
            raise ValueError(
                f"{entry['name']}: marks give nibble {derived}, "
                f"but {entry['nibble']} is recorded"
            )

        for field in ("name", "mejiName"):
            if not is_normalized(entry[field]):
                raise ValueError(f"{entry['name']}: {field} is not NFC-normalized")

        v = entry.get("verification") or {}
        result.append(
            PrincipalOdu(
                rank=entry["rank"],
                name=entry["name"],
                meji_name=entry["mejiName"],
                slug=entry["slug"],
                marks=marks,  # type: ignore[arg-type]
                nibble=entry["nibble"],
                verification=Verification(
                    status=v.get("status", "unverified"),
                    checked_against=v.get("checkedAgainst"),
                    checked_on=v.get("checkedOn"),
                    checked_by=v.get("checkedBy"),
                    note=v.get("note"),
                ),
            )
        )

    ranks = sorted(o.rank for o in result)
    if ranks != list(range(1, 17)):
        raise ValueError(f"ranks must be 1-16 with no gaps or repeats, got {ranks}")

    nibbles = sorted(o.nibble for o in result)
    if nibbles != list(range(16)):
        raise ValueError(
            "the 16 legs must cover every 4-bit value exactly once, "
            f"got {nibbles}"
        )

    slugs = [o.slug for o in result]
    if len(set(slugs)) != 16:
        raise ValueError(f"slugs must be unique, got {slugs}")

    return tuple(sorted(result, key=lambda o: o.rank))
