#!/usr/bin/env python3
"""Seniority ordering and why the orthography is not decoration.

Run:  python3 examples/02_seniority_and_orthography.py
"""
from odu_core import (
    all_odu, by_seniority, principal_odu, senior_of, seniority_rank,
    to_ascii, is_normalized, TRADITION,
)

print(f"tradition: {TRADITION}\n")

# All 256 figures have a seniority order, and it is tradition-specific.
print("most senior five:")
for odu in by_seniority()[:5]:
    print(f"  {seniority_rank(odu):>3}. {odu.name}")

# senior_of() returns the figure that outranks the other — the question asked
# in divination, where two are cast and one governs the reading.
a, b = all_odu()[44], all_odu()[200]
print(f"\ncast {a.name} and {b.name}")
print(f"  -> {senior_of(a, b).name} governs")

# The 16 principal figures carry their own rank and their méjì name.
print("\nfirst three principal figures:")
for p in principal_odu()[:3]:
    print(f"  rank {p.rank}: {p.name}  (méjì: {p.meji_name})")

# Orthography carries meaning: tonal marks and subdots are load-bearing.
# to_ascii() exists for systems that genuinely cannot store them — a lossy
# escape hatch, not a storage format.
print("\northography:")
for p in principal_odu()[:3]:
    print(f"  {p.name:<14} ascii={to_ascii(p.name):<14} normalized={is_normalized(p.name)}")
