#!/usr/bin/env python3
"""Generate ``site/art.html`` — all 256 figures, drawn and playable.

    python3 scripts/build_art.py

The SVGs are rendered server-side from the canonical data, so the page is a
record of the figures rather than a program that reinvents them. The rhythm is
synthesised with the Web Audio API directly: a preservation artifact should not
stop working because a CDN went away.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from odu_core import all_odu, spec_version  # noqa: E402
from odu_core.generative import to_rhythm, to_svg  # noqa: E402

OUT = ROOT / "site" / "art.html"

PAGE = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The 256 figures — drawn and played</title>
<link rel="stylesheet" href="style.css">
<style>
  .sheet{{display:grid;gap:.5rem;grid-template-columns:repeat(auto-fill,minmax(7rem,1fr));
    margin-top:1rem}}
  .fig{{border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--card);
    cursor:pointer;text-align:center;padding-bottom:.4rem;transition:border-color .12s}}
  .fig:hover,.fig:focus-visible{{border-color:var(--accent);outline:none}}
  .fig.playing{{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent) inset}}
  .fig svg{{display:block;width:100%;height:auto}}
  .fig .nm{{font-size:.66rem;color:var(--dim);display:block;padding:.3rem .3rem 0;
    line-height:1.3;word-break:break-word}}
  .fig .bt{{font-family:var(--mono);font-size:.6rem;color:var(--dim)}}
  .bar{{display:flex;gap:.6rem;align-items:center;flex-wrap:wrap;margin:1rem 0 .25rem}}
  button{{background:var(--accent);color:var(--bg);border:0;border-radius:6px;
    padding:.45rem .85rem;font-size:.85rem;font-weight:600;cursor:pointer}}
  button.ghost{{background:transparent;color:var(--accent);border:1px solid var(--line)}}
  #now{{font-family:var(--mono);font-size:.82rem;color:var(--dim);min-height:1.3em}}
  input[type=range]{{accent-color:var(--accent)}}
</style>
</head><body><main>
<div class="crumb"><a href="index.html">← knowledge base</a></div>
<h1>The 256 figures</h1>
<p class="sub">Drawn from the canonical bit patterns, and played as drum strokes:
one mark, one strike; two marks, two.</p>

<div class="note">
  Both the image and the rhythm are pure functions of the eight bits — no
  randomness anywhere, so a figure sounds and looks the same on every machine.
  The mapping needed no invention: a line already carries one mark or two.
  <strong>Click any figure to hear it.</strong>
</div>

<div class="bar">
  <button id="playAll">Play in seniority order</button>
  <button id="stop" class="ghost">Stop</button>
  <label style="font-size:.82rem;color:var(--dim)">tempo
    <input id="bpm" type="range" min="60" max="200" value="112" style="vertical-align:middle">
    <span id="bpmv" class="bt">112</span></label>
</div>
<div id="now"></div>

<div class="sheet" id="sheet">{cells}</div>

<footer>
  Generated from <code>data/principal_odu.json</code>, spec {spec}. Audio is
  synthesised in the browser; nothing is loaded from anywhere.
  <br><br>Verified against Bascom (1969), <i>Ifa Divination</i>, Table 1 p. 4 and Table 3 col. B p. 48. Archived at <a href="https://doi.org/10.5281/zenodo.21743991" rel="noopener">doi:10.5281/zenodo.21743991</a> — please cite Bascom alongside it, as this dataset is a transcription rather than a discovery.
</footer>
</main>
<script>
const FIGURES = {data};
let ctx = null, timers = [], playing = null;

function audio() {{
  ctx ??= new (window.AudioContext || window.webkitAudioContext)();
  if (ctx.state === "suspended") ctx.resume();
  return ctx;
}}

// A short pitched thump — closer to a struck gourd than a sine beep.
function strike(at, accent) {{
  const c = audio();
  const osc = c.createOscillator(), gain = c.createGain();
  osc.type = "triangle";
  osc.frequency.setValueAtTime(accent ? 196 : 147, at);
  osc.frequency.exponentialRampToValueAtTime(accent ? 98 : 74, at + 0.11);
  gain.gain.setValueAtTime(0.0001, at);
  gain.gain.exponentialRampToValueAtTime(accent ? 0.5 : 0.32, at + 0.006);
  gain.gain.exponentialRampToValueAtTime(0.0001, at + 0.19);
  osc.connect(gain).connect(c.destination);
  osc.start(at); osc.stop(at + 0.2);
}}

function clearAll() {{
  timers.forEach(clearTimeout); timers = [];
  document.querySelectorAll(".fig.playing").forEach(el => el.classList.remove("playing"));
  playing = null;
  document.getElementById("now").textContent = "";
}}

function slotSeconds() {{
  const bpm = +document.getElementById("bpm").value;
  return 60 / bpm / 4;           // sixteenth notes
}}

function playFigure(byte, startAt, announce = true) {{
  const f = FIGURES[byte], c = audio(), slot = slotSeconds();
  const t0 = startAt ?? c.currentTime + 0.05;
  // The first stroke of each leg is accented, marking where the legs divide.
  f.onsets.forEach(i => strike(t0 + i * slot, i === 0 || i === 8));
  if (announce) {{
    const el = document.querySelector(`[data-byte="${{byte}}"]`);
    const delay = Math.max(0, (t0 - c.currentTime) * 1000);
    timers.push(setTimeout(() => {{
      document.querySelectorAll(".fig.playing").forEach(e => e.classList.remove("playing"));
      el?.classList.add("playing");
      el?.scrollIntoView({{block: "nearest", behavior: "smooth"}});
      document.getElementById("now").textContent =
        `${{f.name}} — byte ${{byte}}, ${{f.beats}} strokes  ${{f.pattern}}`;
    }}, delay));
  }}
  return 16 * slot;
}}

document.getElementById("sheet").addEventListener("click", ev => {{
  const el = ev.target.closest(".fig");
  if (!el) return;
  clearAll();
  playFigure(+el.dataset.byte);
}});

document.getElementById("playAll").onclick = () => {{
  clearAll();
  const c = audio(), slot = slotSeconds(), order = FIGURES.map((f, b) => [f.rank, b])
    .sort((a, b) => a[0] - b[0]).map(([, b]) => b);
  let t = c.currentTime + 0.1;
  order.forEach(byte => {{ playFigure(byte, t); t += 16 * slot + slot * 2; }});
}};

document.getElementById("stop").onclick = clearAll;
document.getElementById("bpm").oninput = e =>
  document.getElementById("bpmv").textContent = e.target.value;
</script>
</body></html>
"""


def main() -> int:
    if not OUT.parent.exists():
        print("run scripts/build_kb_site.py first — site/ does not exist", file=sys.stderr)
        return 1

    cells, data = [], []
    for odu in all_odu():
        rhythm = to_rhythm(odu)
        cells.append(
            f'<div class="fig" tabindex="0" data-byte="{odu.byte}" '
            f'title="{odu.name} — {rhythm.beats} strokes">'
            f'{to_svg(odu, size=140, show_name=False)}'
            f'<span class="nm" lang="yo">{odu.name}</span>'
            f'<span class="bt">{odu.byte} · {odu.bits}</span></div>'
        )
        data.append({
            "name": odu.name,
            "beats": rhythm.beats,
            "pattern": rhythm.pattern,
            "onsets": list(rhythm.onsets()),
            "rank": odu.seniority_rank,
        })

    OUT.write_text(
        PAGE.format(
            cells="".join(cells),
            data=json.dumps(data, ensure_ascii=False, separators=(",", ":")),
            spec=spec_version(),
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)} — 256 figures, {OUT.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
