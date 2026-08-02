#!/usr/bin/env python3
"""Generate ``site/verify/index.html`` — check two files match, by ear.

    python3 scripts/build_verify.py

Everything happens in the browser. The file is hashed with the Web Crypto API
and never leaves the machine, which matters because the files people want to
check are often the ones they would not upload to a stranger's site.

The drum is the same synthesis the art page uses, imported rather than copied,
so a fingerprint always sounds like the same figures there.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _drum import DRUM_JS  # noqa: E402
from odu_core import all_odu, spec_version  # noqa: E402
from odu_core.generative import to_rhythm, to_svg  # noqa: E402

OUT = ROOT / "site" / "verify" / "index.html"

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Do these two files match? — Odù</title>
<link rel="stylesheet" href="../style.css">
<style>
.drop{{display:block;border:2px dashed var(--line);border-radius:10px;
  padding:2rem 1rem;text-align:center;color:var(--dim);cursor:pointer;
  transition:.15s}}
.drop:hover,.drop.over{{border-color:var(--accent);color:var(--fg)}}
.drop input{{display:none}}
.slots{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:1rem 0}}
@media (max-width:640px){{.slots{{grid-template-columns:1fr}}}}
.slot h3{{margin:.2rem 0 .6rem;font-size:1rem}}
.fp{{font-family:var(--mono);font-size:.95rem;word-break:break-word;margin:.6rem 0}}
.figs{{display:flex;gap:.4rem;flex-wrap:wrap;margin:.6rem 0}}
.figs svg{{width:56px;height:auto;background:var(--card);border:1px solid var(--line);
  border-radius:6px;padding:3px}}
.verdict{{padding:.9rem 1rem;border-radius:8px;font-weight:600;margin:1rem 0}}
.same{{background:#1f3a28;color:#9fe6ad}}
.diff{{background:#3c2020;color:#ffb3b3}}
@media (prefers-color-scheme:light){{.same{{background:#e2f5e8;color:#1c6b34}}
  .diff{{background:#fbe4e4;color:#9a2626}}}}
button{{font:inherit;padding:.45rem .9rem;border-radius:7px;border:1px solid var(--line);
  background:var(--card);color:var(--fg);cursor:pointer}}
button:hover:not(:disabled){{border-color:var(--accent)}}
button:disabled{{opacity:.45;cursor:not-allowed}}
.hint{{color:var(--dim);font-size:.9rem}}
</style></head><body>
<main>
<p><a href="../">← knowledge base</a></p>
<h1>Do these two files match?</h1>
<p class="sub">Drop a file on each side. Each becomes four Odù — three from the
file, one a checksum. Play them and compare by ear, or read them down a phone.</p>

<div class="note">
  <strong>Everything stays on your machine.</strong> The file is hashed here in
  the browser and nothing is uploaded. Nothing is stored, either — reload and
  it is gone.
</div>

<div class="slots">
  <div class="slot">
    <h3>First file</h3>
    <label class="drop" id="dropA">
      <input type="file" id="fileA">
      <span id="labelA">Drop a file, or click to choose</span>
    </label>
    <div class="fp" id="fpA"></div>
    <div class="figs" id="figsA"></div>
    <button id="playA" disabled>▶ Play</button>
  </div>
  <div class="slot">
    <h3>Second file</h3>
    <label class="drop" id="dropB">
      <input type="file" id="fileB">
      <span id="labelB">Drop a file, or click to choose</span>
    </label>
    <div class="fp" id="fpB"></div>
    <div class="figs" id="figsB"></div>
    <button id="playB" disabled>▶ Play</button>
  </div>
</div>

<div id="verdict"></div>

<div class="note">
  <strong>What this catches, and what it does not.</strong> Three bytes is 24
  bits, so a computer can find two files with the same fingerprint in seconds.
  This tells you a download did not truncate, a file did not rot, and you sent
  the take you meant to. It is <em>not</em> a defence against someone who wants
  the fingerprints to match — for that, compare the whole SHA-256.
</div>
<p class="hint">Same thing at a terminal:
  <code>odu fingerprint FILE</code> — or
  <code>sha256sum FILE</code> and read the first six hex characters.</p>
</main>
<script>
const FIGURES = {data};

function audio() {{
  window._ctx ??= new (window.AudioContext || window.webkitAudioContext)();
  if (window._ctx.state === "suspended") window._ctx.resume();
  return window._ctx;
}}

{drum_js}

// A file becomes four figures: three bytes of SHA-256, then a checksum byte
// over those three. Identical to what odu_core.fingerprint does in Python.
async function fingerprint(file) {{
  const buf = await file.arrayBuffer();
  const full = new Uint8Array(await crypto.subtle.digest("SHA-256", buf));
  const payload = full.slice(0, 3);
  const check = new Uint8Array(await crypto.subtle.digest("SHA-256", payload))[0];
  return [...payload, check];
}}

function playBytes(bytes) {{
  const c = audio(), slot = 60 / 112 / 4;
  let t = c.currentTime + 0.06;
  bytes.forEach(b => {{
    FIGURES[b].onsets.forEach(i => strike(t + i * slot, i === 0 || i === 8));
    t += 16 * slot;
  }});
}}

const state = {{A: null, B: null}};

function render(side, bytes, name) {{
  state[side] = bytes;
  document.getElementById("label" + side).textContent = name;
  document.getElementById("fp" + side).textContent =
    bytes.map(b => FIGURES[b].name).join("  ·  ");
  document.getElementById("figs" + side).innerHTML =
    bytes.map(b => FIGURES[b].svg).join("");
  document.getElementById("play" + side).disabled = false;
  verdict();
}}

function verdict() {{
  const el = document.getElementById("verdict");
  if (!state.A || !state.B) {{ el.className = ""; el.textContent = ""; return; }}
  const same = state.A.every((v, i) => v === state.B[i]);
  el.className = "verdict " + (same ? "same" : "diff");
  el.textContent = same
    ? "✓ Same fingerprint — these are almost certainly the same file."
    : "✗ Different fingerprints — these are definitely not the same file.";
}}

for (const side of ["A", "B"]) {{
  const input = document.getElementById("file" + side);
  const drop = document.getElementById("drop" + side);
  input.addEventListener("change", async e => {{
    const f = e.target.files[0];
    if (f) render(side, await fingerprint(f), f.name);
  }});
  ["dragenter", "dragover"].forEach(ev => drop.addEventListener(ev, e => {{
    e.preventDefault(); drop.classList.add("over");
  }}));
  ["dragleave", "drop"].forEach(ev => drop.addEventListener(ev, e => {{
    e.preventDefault(); drop.classList.remove("over");
  }}));
  drop.addEventListener("drop", async e => {{
    const f = e.dataTransfer.files[0];
    if (f) render(side, await fingerprint(f), f.name);
  }});
  document.getElementById("play" + side)
    .addEventListener("click", () => state[side] && playBytes(state[side]));
}}
</script>
<footer class="foot">Spec {spec} · <a href="../">the 256 figures</a> ·
<a href="https://github.com/timeyinallout-cloud/odu-core">source</a></footer>
</body></html>
"""


def main() -> int:
    data = {}
    for odu in all_odu():
        data[odu.byte] = {
            "name": odu.name,
            "onsets": list(to_rhythm(odu).onsets()),
            # 80 is the library's legibility floor; CSS scales it down.
            "svg": to_svg(odu, size=80, show_name=False),
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        PAGE.format(
            data=json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            drum_js=DRUM_JS,
            spec=spec_version(),
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)} — {OUT.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
