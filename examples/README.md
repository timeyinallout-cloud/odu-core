# Examples

Runnable, in order. Each is standalone — no arguments needed unless noted.

```sh
pip install odu-core
python3 examples/01_bytes_and_figures.py
```

| File | Shows |
|---|---|
| `01_bytes_and_figures.py` | The bijection — byte to figure and back, and why there are exactly 256 |
| `02_seniority_and_orthography.py` | Seniority ordering, and why `to_ascii()` is an escape hatch rather than a format |
| `03_encode_a_file.py` | Encoding arbitrary bytes losslessly (takes an optional path) |
| `01_bytes_and_figures.mjs` | The same bijection in TypeScript/JavaScript |

The TypeScript example needs the npm package:

```sh
npm install odu-core
node examples/01_bytes_and_figures.mjs
```
