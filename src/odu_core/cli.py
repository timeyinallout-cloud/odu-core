"""Command line interface for odu-core.

    odu encode --text "hello"        bytes to a phrase
    odu decode "ika-ogbe iwori-ika"  a phrase back to bytes
    odu random --bytes 32            a fresh random phrase
    odu show 44                      one figure, drawn
    odu table                        the 16 principal Odù
"""

from __future__ import annotations

import argparse
import binascii
import os
import sys

from . import __version__
from .core import from_byte
from .data import convention, spec_version
from .mnemonic import (
    ChecksumError,
    PhraseError,
    format_phrase,
    from_phrase,
    phrase_bits,
    to_phrase,
)
from .seniority import TRADITION
from .types import Odu


def _emit(figures: tuple[Odu, ...], style: str, quiet: bool) -> None:
    print(format_phrase(figures, style))  # type: ignore[arg-type]
    if not quiet:
        bits = phrase_bits(len(figures))
        print(
            f"\n{len(figures)} figures — {bits} bits of payload "
            f"plus a checksum figure.",
            file=sys.stderr,
        )


def _read_input(args: argparse.Namespace) -> bytes:
    if args.text is not None:
        return args.text.encode("utf-8")
    if args.hex is not None:
        try:
            return bytes.fromhex(args.hex.replace(" ", "").replace("_", ""))
        except ValueError as exc:
            raise SystemExit(f"odu: not valid hex: {exc}")
    data = sys.stdin.buffer.read()
    if not data:
        raise SystemExit("odu: no input — pass --text, --hex, or pipe to stdin")
    return data


def cmd_encode(args: argparse.Namespace) -> int:
    _emit(to_phrase(_read_input(args)), args.style, args.quiet)
    return 0


def cmd_random(args: argparse.Namespace) -> int:
    if args.bytes < 1:
        raise SystemExit("odu: --bytes must be at least 1")
    data = os.urandom(args.bytes)
    _emit(to_phrase(data), args.style, args.quiet)
    if not args.quiet:
        print(f"hex: {data.hex()}", file=sys.stderr)
    return 0


def cmd_fingerprint(args: argparse.Namespace) -> int:
    from .fingerprint import digest, fingerprint

    exits = 0
    for path in args.paths:
        try:
            raw = digest(path, length=args.bytes)
            figures = fingerprint(path, length=args.bytes)
        except OSError as exc:
            print(f"odu: {exc}", file=sys.stderr)
            exits = 1
            continue
        if len(args.paths) > 1:
            print(f"{path}:")
        _emit(figures, args.style, args.quiet)
        if not args.quiet:
            print(f"sha256[:{args.bytes}]: {raw.hex()}", file=sys.stderr)
    return exits


def cmd_decode(args: argparse.Namespace) -> int:
    text = args.phrase if args.phrase else sys.stdin.read()
    try:
        payload = from_phrase(text)
    except ChecksumError as exc:
        print(f"odu: {exc}", file=sys.stderr)
        return 2
    except PhraseError as exc:
        print(f"odu: {exc}", file=sys.stderr)
        return 1

    if args.output == "hex":
        print(payload.hex())
    elif args.output == "text":
        try:
            print(payload.decode("utf-8"))
        except UnicodeDecodeError:
            print("odu: payload is not valid UTF-8; use --output hex", file=sys.stderr)
            return 1
    else:
        sys.stdout.buffer.write(payload)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    try:
        value = int(args.byte, 0)
        odu = from_byte(value)
    except ValueError as exc:
        raise SystemExit(f"odu: {exc}")

    print(f"{odu.name}")
    print(f"  byte        {odu.byte} (0x{odu.byte:02X}, {odu.bits})")
    print(f"  slug        {odu.slug}")
    print(f"  legs        right {odu.right.name}, left {odu.left.name}")
    print(f"  seniority   {odu.seniority_rank} of 256 ({TRADITION})")
    print(f"  méjì        {'yes' if odu.is_meji else 'no'}")
    print()
    for line in odu.figure().splitlines():
        print(f"  {line}")
    return 0


def cmd_table(args: argparse.Namespace) -> int:
    from .data import principal_odu

    print(f"{'rank':>4}  {'name':<12} {'bits':<6} {'nibble':>6}  slug")
    for o in principal_odu():
        print(f"{o.rank:>4}  {o.name:<12} {o.bits:<6} {o.nibble:>6}  {o.slug}")
    return 0


def cmd_spec(args: argparse.Namespace) -> int:
    print(f"odu-core {__version__}, data spec {spec_version()}")
    for key, value in convention().items():
        print(f"  {key:<20} {value}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Report how much of the canonical table rests on a primary source."""
    from .data import verification_summary

    s = verification_summary()
    print(f"{s['verified']} of {s['total']} figures verified against a source")
    if s["disputed"]:
        print(f"{s['disputed']} disputed")
    if s["unverified"]:
        print(f"{s['unverified']} still to check\n")
        for name in s["by_status"].get("unverified", []):
            print(f"  · {name}")
        print("\nRecord a check with: python3 scripts/verify_odu.py <slug> "
              "--against ... --by ...")
    # Non-zero while the foundation is still unverified, so CI can gate on it.
    return 0 if s["complete"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odu",
        description="The 256 Odù Ifá as a byte mapping.",
        epilog="Phrases carry a checksum, which catches transcription errors "
        "but is not encryption. For wallet seeds use BIP-39.",
    )
    parser.add_argument("--version", action="version", version=f"odu-core {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_style(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--style",
            choices=["slug", "display", "numbered"],
            default="slug",
            help="slug is ASCII and safe to write down (default)",
        )
        p.add_argument("-q", "--quiet", action="store_true", help="phrase only")

    enc = sub.add_parser("encode", help="encode bytes as a phrase")
    src = enc.add_mutually_exclusive_group()
    src.add_argument("--text", help="encode this UTF-8 string")
    src.add_argument("--hex", help="encode these hex bytes")
    add_style(enc)
    enc.set_defaults(func=cmd_encode)

    rnd = sub.add_parser("random", help="generate a random phrase")
    rnd.add_argument("--bytes", type=int, default=32, help="payload size (default 32)")
    add_style(rnd)
    rnd.set_defaults(func=cmd_random)

    dec = sub.add_parser("decode", help="decode a phrase back to bytes")
    dec.add_argument("phrase", nargs="?", help="the phrase; reads stdin if omitted")
    dec.add_argument(
        "--output", choices=["hex", "text", "raw"], default="hex", help="default hex"
    )
    dec.set_defaults(func=cmd_decode)

    shw = sub.add_parser("show", help="describe and draw one figure")
    shw.add_argument("byte", help="byte value, decimal or 0x hex")
    shw.set_defaults(func=cmd_show)

    tbl = sub.add_parser("table", help="list the 16 principal Odù")
    tbl.set_defaults(func=cmd_table)

    spc = sub.add_parser("spec", help="show the bit conventions in use")
    spc.set_defaults(func=cmd_spec)

    vfy = sub.add_parser(
        "verify", help="report verification coverage (exits 1 while incomplete)"
    )
    vfy.set_defaults(func=cmd_verify)

    fpr = sub.add_parser(
        "fingerprint",
        help="a short, sayable fingerprint for a file",
        description=(
            "Four figures you can read down a phone to check two people hold "
            "the same file. The last figure is a checksum, so a "
            "mistranscription is caught. This is a truncated SHA-256 — at the "
            "default three bytes it detects accidents, not tampering."
        ),
    )
    fpr.add_argument("paths", nargs="+", metavar="FILE")
    fpr.add_argument(
        "--bytes", type=int, default=3,
        help="payload bytes to keep (default 3; more is safer but unsayable)",
    )
    fpr.add_argument("--style", default="display",
                     choices=["display", "slug", "numbered"])
    fpr.add_argument("-q", "--quiet", action="store_true",
                     help="just the phrase, no hex on stderr")
    fpr.set_defaults(func=cmd_fingerprint)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        return 0
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
