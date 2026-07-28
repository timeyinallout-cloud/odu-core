/**
 * Rewrite `.ts` import specifiers to `.js` in the emitted declaration files.
 *
 * Source files import with `.ts` extensions so Node can run `src/` directly
 * with native type stripping. TypeScript's `rewriteRelativeImportExtensions`
 * handles that for the JavaScript emit, but it does *not* rewrite declaration
 * files — `dist/*.d.ts` is left pointing at `./types.ts`, which does not exist
 * beside it. A TypeScript consumer of the package would fail to resolve types.
 *
 * This closes that gap. It runs after tsc and is verified by
 * `test/dist.test.js`, which fails the build if any `.ts` specifier survives.
 */

import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DIST = join(dirname(fileURLToPath(import.meta.url)), "..", "dist");

// Only relative specifiers — a bare package name ending in .ts is not ours.
const RELATIVE_TS = /(from\s+|import\s*\(\s*)(["'])(\.\.?\/[^"']+)\.ts\2/g;

let changed = 0;
for (const name of readdirSync(DIST)) {
  if (!name.endsWith(".d.ts")) continue;
  const path = join(DIST, name);
  const before = readFileSync(path, "utf-8");
  const after = before.replace(RELATIVE_TS, "$1$2$3.js$2");
  if (after !== before) {
    writeFileSync(path, after, "utf-8");
    changed++;
  }
}

console.log(`fixed import extensions in ${changed} declaration file(s)`);
