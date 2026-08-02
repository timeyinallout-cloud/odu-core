# Releasing

The repository is public and v1.0.0 is released and archived at
[`10.5281/zenodo.21743991`](https://doi.org/10.5281/zenodo.21743991).
The package registries are still deliberately untouched; these are the
steps for when that changes, and the checks that must pass first.

## Version policy

**Package versions track the data spec**, not the code. `spec_version()` is
what downstream artifacts — encoded data, generated art, mnemonic phrases — are
meaningful against, so a consumer seeing `1.0.0` should get the same byte
mapping from the Python package, the TypeScript package, and the JSON.

Bump the **major** component whenever any of the four conventions changes
(which mark is 1, line order, which leg is the high nibble, seniority
tradition). Every byte value means something different after such a change, and
anything encoded under the old spec silently becomes wrong.

## Before releasing

```sh
make clean && make          # rebuild every derived artifact from source
make test                   # 220 Python + 29 TypeScript tests
odu verify                  # must report 16 of 16 and exit 0
python3 scripts/ingest.py --check
git status --short          # must be empty: no stale derived files
```

The pre-commit hook (`git config core.hooksPath .githooks`) runs most of this
already. CI in `.github/workflows/ci.yml` runs all of it plus a staleness check
on derived artifacts, and activates as soon as there is a remote.

## Python — PyPI

```sh
python3 -m pip install --quiet build twine
python3 -m build
python3 -m twine check dist/*
python3 -m twine upload dist/*     # not run yet
```

The canonical JSON ships inside the wheel via `force-include`, so an installed
copy reads the same bytes as a checkout.

## TypeScript — npm

```sh
cd ts && npm run build && npm pack --dry-run
npm publish                        # not run yet
```

`npm run build`, never bare `tsc` — a post-compile step fixes import extensions
in the declarations, and skipping it ships types no consumer can resolve.
`test/dist.test.js` fails the build if that step is missed.

## Before the first publish

- [ ] Decide the npm scope. `@odu/core` is currently a placeholder and may not
      be claimable.
- [ ] Confirm the PyPI name `odu-core` is free.
- [ ] Add a remote and let CI run green once.
- [ ] Consider whether the compound-name data is complete enough to publish —
      54 of 256 traditional names are sourced; the rest remain `null`.
