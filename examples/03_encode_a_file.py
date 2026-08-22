#!/usr/bin/env python3
"""Encode a real file as Odù and back — the bijection at scale.

Run:  python3 examples/03_encode_a_file.py [path]
"""
import sys
from pathlib import Path
from odu_core import encode, decode

path = Path(sys.argv[1] if len(sys.argv) > 1 else __file__)
raw = path.read_bytes()

figures = encode(raw)
print(f"{path.name}: {len(raw)} bytes -> {len(figures)} figures")
print("first five:", ", ".join(o.name for o in figures[:5]))

assert decode(figures) == raw, "round-trip must be lossless"
print("round-trip: byte-identical")
