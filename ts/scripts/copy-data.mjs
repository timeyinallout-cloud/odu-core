// Stage the canonical JSON inside the package before it is packed.
//
// WHY THIS EXISTS. `package.json` declares `files: ["dist", "data"]`, but npm
// resolves those against the package directory (`ts/`), and the canonical data
// lives at the REPO ROOT (`../data/`). So `data` matched nothing, the tarball
// shipped without it, and `core.ts` — which reads `data/odu_256.json` at
// runtime rather than re-deriving it — failed on first import:
//
//     could not find odu_256.json — looked in: .../node_modules/@odu/data/...
//
// Nothing caught this locally, because in a checkout the `../../data` fallback
// path resolves fine. It only breaks once installed, which is the worst place
// to find out and the hardest to undo: npm will not let a version be republished.
//
// Copying rather than symlinking: npm does not follow symlinks into tarballs.
// The copy is gitignored, and regenerated on every pack, so it cannot drift from
// the root data — that copy is the source of truth, this is a build artifact.
import { mkdirSync, copyFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PKG = join(HERE, "..");
const ROOT = join(PKG, "..");

const FILES = ["odu_256.json", "principal_odu.json"];

mkdirSync(join(PKG, "data"), { recursive: true });

let copied = 0;
for (const name of FILES) {
  const src = join(ROOT, "data", name);
  if (!existsSync(src)) {
    console.error(`copy-data: MISSING ${src}`);
    process.exit(1);        // fail the pack rather than ship a broken tarball
  }
  copyFileSync(src, join(PKG, "data", name));
  copied += 1;
}
console.log(`copy-data: staged ${copied} data file(s) for packing`);
