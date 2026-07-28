/**
 * Types for the Odù dataset.
 *
 * An Odù figure is two legs of four lines each, and every line carries either
 * one mark or two. That is four bits per leg, eight bits per figure, and
 * exactly 256 figures — a bijection with the byte.
 */

/** A single line of a leg. `I` is one mark, `II` is two marks. */
export type Mark = "I" | "II";

/** Whether a figure's bit pattern has been checked against a primary source. */
export type VerificationStatus = "unverified" | "verified" | "disputed";

/** One leg: which of the 16 principal Odù it is. */
export interface Leg {
  readonly slug: string;
  readonly name: string;
  /** The leg as a 4-bit integer, 0-15. Top line is the most significant bit. */
  readonly nibble: number;
}

/** One of the 256 full figures. */
export interface Odu {
  /** The figure as an integer, 0-255. The right leg is the high nibble. */
  readonly byte: number;
  /** Eight binary digits, right leg first. */
  readonly bits: string;
  readonly hex: string;
  readonly name: string;
  readonly slug: string;
  /**
   * A contracted traditional name where one is attested. `null` means none has
   * been sourced — these vary by lineage and are never generated.
   */
  readonly traditionalName: string | null;
  /** Where the traditional name came from. `null` whenever the name is. */
  readonly traditionalNameSource: string | null;
  readonly isMeji: boolean;
  /** Position in the traditional 256 ordering, 1-256. */
  readonly seniorityRank: number;
  readonly right: Leg;
  readonly left: Leg;
  readonly marks: { readonly right: Mark[]; readonly left: Mark[] };
}

/** The four choices that determine the byte mapping. */
export interface Convention {
  readonly singleMarkBit: number;
  readonly doubleMarkBit: number;
  readonly lineOrder: string;
  readonly mostSignificantLine: string;
  readonly legToNibble: string;
  readonly seniorityTradition: string;
  readonly note?: string;
}

/** How much of the canonical table rests on a checked source. */
export interface Verification {
  readonly verified: number;
  readonly unverified: number;
  readonly disputed: number;
  readonly total: number;
  readonly complete: boolean;
  readonly acceptedSources: string[];
  readonly note: string | null;
}

/** The shape of `data/odu_256.json`. */
export interface Dataset {
  readonly specVersion: string;
  readonly convention: Convention;
  readonly verification: Verification;
  readonly count: number;
  /** How many of the 256 have an attested traditional name. */
  readonly namesSourced: number;
  readonly odu: Odu[];
}
