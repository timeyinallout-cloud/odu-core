/**
 * Guards on the published build output.
 *
 * The package is consumed through `dist/`, so these check the artifact rather
 * than the source. The extension test in particular protects against a silent
 * packaging break: TypeScript rewrites `.ts` specifiers in the JavaScript emit
 * but not in declarations, and a stale `./types.ts` in a `.d.ts` only fails for
 * downstream users, never for us.
 */

import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DIST = join(dirname(fileURLToPath(import.meta.url)), "..", "dist");
const RELATIVE_TS = /(?:from\s+|import\s*\(\s*)["'](\.\.?\/[^"']+)\.ts["']/;

test("dist exists and carries declarations", () => {
  assert.ok(existsSync(DIST), "run `npm run build` first");
  const files = readdirSync(DIST);
  for (const expected of ["index.js", "index.d.ts", "core.js", "core.d.ts"]) {
    assert.ok(files.includes(expected), `dist/${expected} is missing`);
  }
});

test("no emitted file imports a .ts specifier", () => {
  for (const name of readdirSync(DIST)) {
    if (!name.endsWith(".js") && !name.endsWith(".d.ts")) continue;
    const text = readFileSync(join(DIST, name), "utf-8");
    const hit = RELATIVE_TS.exec(text);
    assert.equal(
      hit,
      null,
      `dist/${name} imports ${hit?.[1]}.ts — consumers cannot resolve that. ` +
        `Run scripts/fix-decl-extensions.mjs after tsc.`,
    );
  }
});

test("every relative import in dist resolves to a real file", () => {
  const specifier = /(?:from\s+|import\s*\(\s*)["'](\.\.?\/[^"']+)["']/g;
  for (const name of readdirSync(DIST)) {
    if (!name.endsWith(".js") && !name.endsWith(".d.ts")) continue;
    const text = readFileSync(join(DIST, name), "utf-8");
    for (const [, target] of text.matchAll(specifier)) {
      // A .d.ts referencing ./core.js is satisfied by core.d.ts beside it.
      const candidates = name.endsWith(".d.ts")
        ? [target, target.replace(/\.js$/, ".d.ts")]
        : [target];
      assert.ok(
        candidates.some((c) => existsSync(join(DIST, c))),
        `dist/${name} imports ${target}, which does not exist`,
      );
    }
  }
});
