/**
 * odu-core — the 256 Odù Ifá as a canonical byte mapping.
 *
 * The canonical data lives in `data/principal_odu.json`; this package reads the
 * generated `data/odu_256.json` rather than re-deriving the mapping.
 */

export * from "./types.js";
export {
  allOdu,
  bySeniority,
  convention,
  decode,
  drawFigure,
  encode,
  find,
  fold,
  fromBits,
  fromByte,
  fromLegs,
  seniorOf,
  specVersion,
  verification,
} from "./core.js";
export {
  CHECKSUM_FIGURES,
  ChecksumError,
  PhraseError,
  checksumByte,
  formatPhrase,
  fromPhrase,
  parsePhrase,
  phraseBits,
  toPhrase,
  type Style,
} from "./mnemonic.js";
