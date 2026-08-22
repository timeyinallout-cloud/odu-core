#!/usr/bin/env python3
"""The bijection: every byte is an Odù, every Odù is a byte.

Run:  python3 examples/01_bytes_and_figures.py
"""
from odu_core import from_byte, to_byte, all_odu, encode, decode

# A byte in, a figure out. No padding, no loss, no leftover values.
for b in (0, 44, 255):
    odu = from_byte(b)
    print(f"{b:>3} -> {odu.name}")

# And back again.
assert to_byte(from_byte(200)) == 200

# There are exactly 256, which is the whole point.
figures = all_odu()
print(f"\n{len(figures)} figures, {len({o.name for o in figures})} distinct names")

# So arbitrary data round-trips through the corpus losslessly.
message = "Ẹ káàbọ̀".encode("utf-8")
assert decode(encode(message)) == message
print(f"round-trip of {len(message)} bytes: OK")
