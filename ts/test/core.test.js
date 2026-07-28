/**
 * Tests for the TypeScript binding.
 *
 * These run against the compiled output in dist/, so `npm run build` must have
 * run first. The mapping is small enough to test exhaustively — assertions
 * about the 256 figures check all 256.
 */

import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  ChecksumError,
  PhraseError,
  allOdu,
  bySeniority,
  checksumByte,
  decode,
  drawFigure,
  encode,
  find,
  fold,
  formatPhrase,
  fromBits,
  fromByte,
  fromLegs,
  fromPhrase,
  parsePhrase,
  phraseBits,
  seniorOf,
  specVersion,
  toPhrase,
  verification,
} from "../dist/index.js";

const HERE = dirname(fileURLToPath(import.meta.url));
const parity = JSON.parse(
  readFileSync(join(HERE, "fixtures", "parity.json"), "utf-8"),
);

test("dataset holds exactly 256 figures", () => {
  assert.equal(allOdu().length, 256);
});

test("every byte round-trips", () => {
  for (let b = 0; b < 256; b++) assert.equal(fromByte(b).byte, b);
});

test("every figure is distinct", () => {
  assert.equal(new Set(allOdu().map((o) => o.slug)).size, 256);
});

test("right leg is the high nibble", () => {
  for (const o of allOdu()) {
    assert.equal(o.byte >> 4, o.right.nibble);
    assert.equal(o.byte & 0x0f, o.left.nibble);
  }
});

test("out-of-range bytes are rejected", () => {
  for (const bad of [-1, 256, 1000]) {
    assert.throws(() => fromByte(bad), RangeError);
  }
  assert.throws(() => fromByte(1.5), TypeError);
});

test("fromLegs and fromBits agree with fromByte", () => {
  for (const o of allOdu()) {
    assert.equal(fromLegs(o.right.slug, o.left.slug).byte, o.byte);
    assert.equal(fromBits(o.bits).byte, o.byte);
  }
});

test("fromBits rejects anything that is not eight binary digits", () => {
  for (const bad of ["", "1010", "111111112", "abcdefgh"]) {
    assert.throws(() => fromBits(bad));
  }
});

test("sixteen figures are méjì", () => {
  assert.equal(allOdu().filter((o) => o.isMeji).length, 16);
});

test("seniority covers 1-256 and differs from numeric order", () => {
  const ranks = allOdu().map((o) => o.seniorityRank).sort((a, b) => a - b);
  assert.deepEqual(ranks, Array.from({ length: 256 }, (_, i) => i + 1));
  assert.notDeepEqual(bySeniority().map((o) => o.byte), [...Array(256).keys()]);
});

test("Èjì Ogbè is most senior and is byte 255", () => {
  assert.equal(bySeniority()[0].name, "Èjì Ogbè");
  assert.equal(fromByte(255).name, "Èjì Ogbè");
  assert.equal(seniorOf(fromByte(0), fromByte(255)).byte, 255);
});

test("lookup accepts diacritic and ASCII forms", () => {
  assert.equal(find("Ọ̀yẹ̀kú Méjì").byte, 0);
  assert.equal(find("oyeku-oyeku").byte, 0);
  assert.equal(fold("Òtúrúpọ̀n"), "oturupon");
});

test("figures render as four rows", () => {
  assert.equal(drawFigure(fromByte(44)).split("\n").length, 4);
});

test("encode and decode round-trip arbitrary bytes", () => {
  const payload = Uint8Array.from({ length: 256 }, (_, i) => i);
  assert.deepEqual(decode(encode(payload)), payload);
});

test("phrases round-trip in every format", () => {
  const payload = new TextEncoder().encode("heritage computing");
  for (const style of ["slug", "display", "numbered"]) {
    const text = formatPhrase(toPhrase(payload), style);
    assert.deepEqual(fromPhrase(text), payload);
  }
});

test("an empty payload is one checksum figure", () => {
  const phrase = toPhrase(new Uint8Array(0));
  assert.equal(phrase.length, 1);
  assert.deepEqual(fromPhrase(phrase), new Uint8Array(0));
});

test("a 32-byte key is 33 figures", () => {
  assert.equal(toPhrase(new Uint8Array(32)).length, 33);
  assert.equal(phraseBits(33), 256);
});

test("transposed figures fail the checksum", () => {
  const phrase = [...toPhrase(new TextEncoder().encode("abcdefgh"))];
  [phrase[0], phrase[1]] = [phrase[1], phrase[0]];
  assert.throws(() => fromPhrase(phrase), ChecksumError);
});

test("a substituted figure fails the checksum", () => {
  const phrase = [...toPhrase(new TextEncoder().encode("abcdefgh"))];
  phrase[2] = fromByte((phrase[2].byte + 1) % 256);
  assert.throws(() => fromPhrase(phrase), ChecksumError);
});

test("corruption is caught at roughly the expected rate", () => {
  // A one-byte checksum misses about 1 in 256 by design, so this asserts the
  // rate rather than demanding every trial be caught.
  let detected = 0;
  const trials = 500;
  for (let i = 0; i < trials; i++) {
    const payload = Uint8Array.from({ length: 8 }, (_, j) => (i * 31 + j * 7) % 256);
    const phrase = [...toPhrase(payload)];
    const at = i % phrase.length;
    phrase[at] = fromByte((phrase[at].byte + 1 + (i % 255)) % 256);
    try {
      fromPhrase(phrase);
    } catch (err) {
      if (err instanceof ChecksumError) detected++;
    }
  }
  assert.ok(detected / trials > 0.97, `detection rate ${detected / trials}`);
});

test("malformed phrases are rejected with guidance", () => {
  assert.throws(() => parsePhrase("   "), PhraseError);
  assert.throws(() => parsePhrase("Ogbè Ọ̀yẹ̀kú Ìwòrì"), /two words/);
  assert.throws(() => parsePhrase("notanodu-atall"), PhraseError);
});

test("checksum byte is deterministic and input-sensitive", () => {
  const a = new TextEncoder().encode("hello");
  const b = new TextEncoder().encode("hellp");
  assert.equal(checksumByte(a), checksumByte(a));
  assert.notEqual(checksumByte(a), checksumByte(b));
});

// --- cross-language parity -------------------------------------------------

test("spec version matches the Python fixture", () => {
  assert.equal(specVersion(), parity.specVersion);
});

test("named figures match Python", () => {
  for (const expected of parity.figures) {
    const actual = fromByte(expected.byte);
    assert.equal(actual.name, expected.name, `byte ${expected.byte} name`);
    assert.equal(actual.slug, expected.slug, `byte ${expected.byte} slug`);
    assert.equal(
      actual.seniorityRank,
      expected.seniorityRank,
      `byte ${expected.byte} seniority`,
    );
  }
});

test("seniority order matches Python", () => {
  assert.deepEqual(
    bySeniority().slice(0, 16).map((o) => o.byte),
    parity.seniorityOrder,
  );
});

test("phrases match Python byte for byte", () => {
  for (const [text, expected] of Object.entries(parity.phrases)) {
    const actual = formatPhrase(toPhrase(new TextEncoder().encode(text)), "slug");
    assert.equal(actual, expected, `phrase for ${JSON.stringify(text)}`);
  }
});

test("verification state is carried through from the canonical data", () => {
  const v = verification();
  assert.equal(v.total, 16);
  assert.equal(typeof v.complete, "boolean");
  assert.equal(v.verified + v.unverified + v.disputed, v.total);
});
