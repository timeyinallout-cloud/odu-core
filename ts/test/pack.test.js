// The canonical data must reach the published tarball.
//
// It did not, for the first attempted publish: package.json declares
// files: ["dist", "data"], but npm resolves that against ts/, while the data
// lives at the repo root. The tarball shipped 9 files, none of them JSON, and
// `import "odu-core"` failed on first use with "could not find odu_256.json".
//
// A checkout never sees this — core.ts has a ../../data fallback that resolves
// fine locally. Only an installed copy breaks, and npm will not let a version
// be republished, so this is worth a test rather than a memory.
import { test } from "node:test";
import assert from "node:assert";
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const PKG = join(dirname(fileURLToPath(import.meta.url)), "..");

test("package.json ships the data directory", () => {
  const pkg = JSON.parse(readFileSync(join(PKG, "package.json"), "utf8"));
  assert.ok(pkg.files.includes("data"),
    "files must include 'data' or the runtime JSON never ships");
  assert.strictEqual(pkg.scripts.prepack, "node scripts/copy-data.mjs",
    "prepack must stage the data; 'files' alone cannot reach outside the package");
});

test("prepack stages the canonical JSON inside the package", () => {
  rmSync(join(PKG, "data"), { recursive: true, force: true });
  execFileSync("node", ["scripts/copy-data.mjs"], { cwd: PKG });

  for (const name of ["odu_256.json", "principal_odu.json"]) {
    const staged = join(PKG, "data", name);
    assert.ok(existsSync(staged), `${name} was not staged for packing`);
    const copy = JSON.parse(readFileSync(staged, "utf8"));
    const source = JSON.parse(readFileSync(join(PKG, "..", "data", name), "utf8"));
    assert.deepStrictEqual(copy, source,
      `${name} staged copy differs from the root source of truth`);
  }
});
