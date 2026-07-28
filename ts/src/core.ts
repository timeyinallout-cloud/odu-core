/**
 * Byte ↔ Odù conversion.
 *
 * This module reads `data/odu_256.json` — the artifact the Python generator
 * produces — rather than re-deriving the mapping. Two implementations that each
 * compute the table can drift apart; one that computes and one that reads
 * cannot.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import type { Convention, Dataset, Odu, Verification } from "./types.ts";

const HERE = dirname(fileURLToPath(import.meta.url));

function locate(): string {
  // Works from a checkout (ts/dist -> ../../data) and from a package that
  // ships the JSON alongside its build output.
  const candidates = [
    join(HERE, "..", "..", "data", "odu_256.json"),
    join(HERE, "..", "data", "odu_256.json"),
    join(HERE, "data", "odu_256.json"),
  ];
  for (const path of candidates) {
    try {
      readFileSync(path);
      return path;
    } catch {
      continue;
    }
  }
  throw new Error(
    `could not find odu_256.json — looked in:\n  ${candidates.join("\n  ")}\n` +
      `Run 'python3 scripts/generate.py' from the repository root.`,
  );
}

const DATA: Dataset = JSON.parse(readFileSync(locate(), "utf-8")) as Dataset;

if (DATA.odu.length !== 256) {
  throw new Error(`dataset holds ${DATA.odu.length} figures, expected 256`);
}

const BY_SLUG = new Map<string, Odu>();
const BY_NAME = new Map<string, Odu>();
for (const o of DATA.odu) {
  BY_SLUG.set(o.slug, o);
  BY_NAME.set(fold(o.name), o);
}

/** Strip diacritics and lowercase, so ASCII input matches Yorùbá names. */
export function fold(text: string): string {
  return text
    .normalize("NFD")
    .replace(/\p{Mn}/gu, "")
    .toLowerCase()
    .trim();
}

/** The dataset's spec version. Encoded data is only meaningful against one. */
export function specVersion(): string {
  return DATA.specVersion;
}

/** The four choices that determine the mapping. */
export function convention(): Convention {
  return DATA.convention;
}

/** How much of the canonical table has been checked against a source. */
export function verification(): Verification {
  return DATA.verification;
}

/** All 256 figures in byte order — index `i` is byte `i`. */
export function allOdu(): readonly Odu[] {
  return DATA.odu;
}

/** The figure for a byte value, 0-255. */
export function fromByte(value: number): Odu {
  if (!Number.isInteger(value)) {
    throw new TypeError(`expected an integer, got ${String(value)}`);
  }
  if (value < 0 || value > 255) {
    throw new RangeError(`a byte must be 0-255, got ${value}`);
  }
  return DATA.odu[value]!;
}

/** Build a figure from its two legs, right first as it is cast. */
export function fromLegs(right: string | number, left: string | number): Odu {
  return fromByte((legNibble(right) << 4) | legNibble(left));
}

function legNibble(ref: string | number): number {
  if (typeof ref === "number") {
    if (!Number.isInteger(ref) || ref < 0 || ref > 15) {
      throw new RangeError(`a leg's nibble must be 0-15, got ${ref}`);
    }
    return ref;
  }
  const key = fold(ref);
  for (const o of DATA.odu) {
    if (fold(o.right.slug) === key || fold(o.right.name) === key) {
      return o.right.nibble;
    }
  }
  throw new Error(`no principal Odù matches ${JSON.stringify(ref)}`);
}

/** Build a figure from eight binary digits, right leg first. */
export function fromBits(bits: string): Odu {
  const cleaned = bits.trim().replace(/[\s_]/g, "");
  if (!/^[01]{8}$/.test(cleaned)) {
    throw new Error(`expected 8 binary digits, got ${JSON.stringify(bits)}`);
  }
  return fromByte(Number.parseInt(cleaned, 2));
}

/** Look a figure up by slug or name, with or without diacritics. */
export function find(ref: string): Odu | undefined {
  const key = fold(ref);
  return BY_SLUG.get(key) ?? BY_NAME.get(key);
}

/** Convert bytes to figures, one per byte, in order. */
export function encode(data: Uint8Array | readonly number[]): Odu[] {
  return Array.from(data, (b) => fromByte(b));
}

/** Convert figures back to bytes. Inverse of {@link encode}. */
export function decode(odu: readonly Odu[]): Uint8Array {
  return Uint8Array.from(odu, (o) => o.byte);
}

/** All 256 figures in traditional seniority order, most senior first. */
export function bySeniority(): Odu[] {
  return [...DATA.odu].sort((a, b) => a.seniorityRank - b.seniorityRank);
}

/** Whichever of two figures outranks the other. */
export function seniorOf(a: Odu, b: Odu): Odu {
  return a.seniorityRank <= b.seniorityRank ? a : b;
}

/** Render a figure as text, right leg in the left-hand column. */
export function drawFigure(odu: Odu): string {
  return odu.marks.right
    .map((r, i) => {
      const l = odu.marks.left[i]!;
      return `${r === "I" ? "  I" : "I I"}  ${l === "I" ? "I" : "I I"}`.trimEnd();
    })
    .join("\n");
}
