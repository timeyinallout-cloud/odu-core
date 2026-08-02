"""The dùndún synthesis, shared by every page that makes a sound.

Extracted so the art page and the verify page cannot drift apart. A fingerprint
that sounded different from the same figures on the art page would defeat the
whole point of comparing by ear. See docs/DECISIONS.md §5.

`DRUM_JS` is real JavaScript, and is passed to str.format as an ARGUMENT, not
pasted into a template. format only un-doubles braces in the template itself —
a substituted value is copied verbatim — so doubling these braces first would
leave them doubled in the output.
"""
from __future__ import annotations

DRUM_JS = r"""
// One output stage for everything, so the page can be loud without tearing
// when eight onsets land close together. The compressor is the reason the
// gain can sit this high — peaks get held down instead of clipping.
let bus = null;
function master() {
  const c = audio();
  if (bus) return bus;
  const comp = c.createDynamicsCompressor();
  comp.threshold.value = -14; comp.knee.value = 20;
  comp.ratio.value = 8; comp.attack.value = 0.003; comp.release.value = 0.18;
  bus = c.createGain();
  bus.gain.value = 1.6;
  bus.connect(comp).connect(c.destination);
  return bus;
}

// A dùndún — the Yorùbá talking drum. What makes one "talk" is not its timbre
// but its pitch: the player squeezes the tension cords against their body, so
// every stroke bends. A fixed sample cannot do that, which is why this is
// synthesised rather than recorded — and why the shape below matters more
// than the waveform.
//
// Three parts: a stick transient (noise, ~8 ms), the membrane tone with its
// bend up and release down, and a quiet second partial for body.
function strike(at, accent) {
  const c = audio(), out = master();

  // Stick on skin. Short, bright, and the thing that makes it read as struck.
  const nlen = Math.floor(c.sampleRate * 0.03);
  const buf = c.createBuffer(1, nlen, c.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < nlen; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / nlen) ** 3;
  const noise = c.createBufferSource(); noise.buffer = buf;
  const nf = c.createBiquadFilter();
  nf.type = "bandpass"; nf.frequency.value = accent ? 1900 : 1500; nf.Q.value = 0.8;
  const ng = c.createGain();
  ng.gain.setValueAtTime(accent ? 0.55 : 0.38, at);
  ng.gain.exponentialRampToValueAtTime(0.0001, at + 0.03);
  noise.connect(nf).connect(ng).connect(out);
  noise.start(at); noise.stop(at + 0.03);

  // The membrane. f0 is where the squeeze settles; the stroke arrives under
  // it, bends up through it, then releases below — the speech-like contour.
  const f0 = accent ? 232 : 174;
  const osc = c.createOscillator(), g = c.createGain();
  osc.type = "sine";
  osc.frequency.setValueAtTime(f0 * 0.78, at);
  osc.frequency.linearRampToValueAtTime(f0 * 1.22, at + 0.05);
  osc.frequency.exponentialRampToValueAtTime(f0 * 0.58, at + 0.30);
  g.gain.setValueAtTime(0.0001, at);
  g.gain.exponentialRampToValueAtTime(accent ? 0.95 : 0.66, at + 0.008);
  g.gain.exponentialRampToValueAtTime(0.0001, at + 0.34);
  osc.connect(g).connect(out);
  osc.start(at); osc.stop(at + 0.35);

  // A second partial, detuned and quieter — a drum head is not a sine.
  const o2 = c.createOscillator(), g2 = c.createGain();
  o2.type = "triangle";
  o2.frequency.setValueAtTime(f0 * 1.63, at);
  o2.frequency.exponentialRampToValueAtTime(f0 * 0.95, at + 0.16);
  g2.gain.setValueAtTime(0.0001, at);
  g2.gain.exponentialRampToValueAtTime(accent ? 0.26 : 0.17, at + 0.007);
  g2.gain.exponentialRampToValueAtTime(0.0001, at + 0.18);
  o2.connect(g2).connect(out);
  o2.start(at); o2.stop(at + 0.19);
}
"""
