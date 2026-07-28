/**
 * Checksummed mnemonic encoding: bytes to Odù names and back.
 *
 * A trailing checksum figure is appended, so a mistyped or transposed figure is
 * caught on decode rather than silently yielding different bytes.
 *
 * ## Read this before using it for key material
 *
 * The checksum detects accidental corruption. It is not authentication, it is
 * not encryption, and it adds no entropy — a phrase reveals exactly the bytes it
 * encodes to anyone holding it.
 *
 * Each figure carries 8 bits where a BIP-39 word carries 11. Matching a 256-bit
 * seed takes 32 figures plus the checksum. **If you are encoding a wallet seed,
 * use BIP-39** — it is specified, audited, and interoperable across wallets.
 * This module is built for memory, teaching, and art.
 */

import { createHash } from "node:crypto";
import { allOdu, find, fold, fromByte, fromLegs } from "./core.ts";
import type { Odu } from "./types.ts";

/** Figures appended for the checksum. One figure is one byte of SHA-256. */
export const CHECKSUM_FIGURES = 1;

export type Style = "slug" | "display" | "numbered";

export class PhraseError extends Error {
  override name = "PhraseError";
}

/** A phrase parsed cleanly but its checksum does not match its payload. */
export class ChecksumError extends Error {
  override name = "ChecksumError";
}

/** First byte of the SHA-256 of `data`. */
export function checksumByte(data: Uint8Array): number {
  return createHash("sha256").update(data).digest()[0]!;
}

/** Encode bytes as figures, with a checksum figure appended. */
export function toPhrase(data: Uint8Array | readonly number[]): Odu[] {
  const payload = Uint8Array.from(data);
  const withChecksum = Uint8Array.from([...payload, checksumByte(payload)]);
  return Array.from(withChecksum, (b) => fromByte(b));
}

/** Decode figures back to bytes, verifying the checksum. */
export function fromPhrase(phrase: string | readonly Odu[]): Uint8Array {
  const figures = typeof phrase === "string" ? parsePhrase(phrase) : [...phrase];

  // An empty payload is legitimate: it encodes to the checksum figure alone.
  if (figures.length < CHECKSUM_FIGURES) {
    throw new PhraseError(
      `a phrase needs at least ${CHECKSUM_FIGURES} figure (the checksum), ` +
        `got ${figures.length}`,
    );
  }

  const raw = Uint8Array.from(figures, (f) => f.byte);
  const payload = raw.slice(0, -CHECKSUM_FIGURES);
  const given = raw[raw.length - 1]!;
  const expected = checksumByte(payload);

  if (given !== expected) {
    const hex = (n: number) => `0x${n.toString(16).padStart(2, "0").toUpperCase()}`;
    throw new ChecksumError(
      `checksum mismatch: phrase ends with ${figures[figures.length - 1]!.name} ` +
        `(${hex(given)}) but its ${payload.length} payload figures require ` +
        `${hex(expected)}. Usually a mistyped or transposed figure.`,
    );
  }
  return payload;
}

/** Bits of payload carried by a phrase of `figureCount` figures. */
export function phraseBits(figureCount: number): number {
  return Math.max(0, figureCount - CHECKSUM_FIGURES) * 8;
}

/**
 * Render figures as text.
 *
 * `slug` is the canonical written form — ASCII, one token per figure, safe to
 * write down. `display` keeps full Yorùbá orthography with a separator, since
 * figure names are themselves two words. `numbered` is for reading aloud.
 */
export function formatPhrase(figures: readonly Odu[], style: Style = "slug"): string {
  switch (style) {
    case "slug":
      return figures.map((f) => f.slug).join(" ");
    case "display":
      return figures.map((f) => f.name).join(" · ");
    case "numbered": {
      const width = String(figures.length).length;
      return figures
        .map((f, i) => `${String(i + 1).padStart(width)}. ${f.name}`)
        .join("\n");
    }
    default:
      throw new Error(`unknown style ${JSON.stringify(style)}`);
  }
}

/** Parse any format {@link formatPhrase} produces back into figures. */
export function parsePhrase(text: string): Odu[] {
  const cleaned = text
    .replace(/[·•/,;|\n\r\t]+/g, " ")
    .replace(/\b\d{1,3}[.)]\s*/g, " ")
    .trim();
  if (!cleaned) {
    throw new PhraseError("phrase is empty");
  }

  const words = cleaned.split(/\s+/);
  let chunks: string[];
  if (words.some((w) => w.includes("-"))) {
    chunks = words;
  } else if (words.length % 2 === 0) {
    // Display form without separators: every figure name is two words.
    chunks = [];
    for (let i = 0; i < words.length; i += 2) {
      chunks.push(`${words[i]} ${words[i + 1]}`);
    }
  } else {
    throw new PhraseError(
      `cannot split ${words.length} words into figures — every figure name is ` +
        `two words. Use slug form (ogbe-oyeku) or separate figures with '·'.`,
    );
  }

  return chunks.map((chunk) => resolve(chunk));
}

function resolve(token: string): Odu {
  const hit = find(token);
  if (hit) return hit;

  const key = fold(token);
  const parts = key.includes("-") ? key.split("-") : key.split(" ");
  if (parts.length === 2) {
    try {
      return fromLegs(parts[0]!, parts[1]!);
    } catch {
      // fall through to the suggestion path
    }
  }
  throw new PhraseError(`${JSON.stringify(token)} is not a figure${suggest(key)}`);
}

function suggest(key: string): string {
  // Cheap prefix match — enough to catch a fat-fingered ending.
  const near = allOdu()
    .map((o) => o.slug)
    .filter((slug) => slug.slice(0, 4) === key.slice(0, 4))
    .slice(0, 2);
  return near.length ? `. Did you mean: ${near.join(", ")}?` : "";
}
