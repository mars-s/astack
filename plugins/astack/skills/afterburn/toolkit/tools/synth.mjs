// Sound kit for HTML films. render.mjs calls soundtrack(cues, duration, options) and muxes the WAV it returns.
// Copy this file next to a film to change its sound: the renderer prefers a synth.mjs in the film's folder.
// options come from window.__audio in the film: { music: 'synth' | false | 'track.mp3', musicGain, drive }.
// ponytail: hand-rolled DSP is a stand-in. For a polished film, set music to a licensed track file.
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';

const SR = 48000;
const TAU = Math.PI * 2;
let seed = 7;
const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647) * 2 - 1;
const arr = (sec) => new Float64Array(Math.max(1, Math.ceil(sec * SR)));
const env = (t, a, d) => (t < a ? t / a : Math.exp(-(t - a) / d));
const lp = (x, fc) => { const a = 1 - Math.exp(-TAU * fc / SR); let y = 0; return x.map((v) => (y += a * (v - y))); };
const hp = (x, fc) => { const l = lp(x, fc); return x.map((v, i) => v - l[i]); };
const midi = (m) => 440 * 2 ** ((m - 69) / 12);

// ------------------------------------------------------------------ one-shot sounds (mono, or [L, R])
function tick(f) {
  const x = arr(0.12);
  for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] = Math.sin(TAU * f * t) * env(t, 0.0005, 0.018) * 0.7 + rnd() * env(t, 0.0003, 0.003) * 0.3; }
  return x;
}
function click() {
  const x = arr(0.08);
  for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] = rnd() * env(t, 0.0002, 0.002) * 0.8 + Math.sin(TAU * 3200 * t) * env(t, 0.0003, 0.01) * 0.5 + Math.sin(TAU * 900 * t) * env(t, 0.0005, 0.015) * 0.3; }
  return x;
}
function pop() {
  const x = arr(0.3);
  let ph = 0;
  for (let i = 0; i < x.length; i++) { const t = i / SR; ph += (300 + 900 * Math.exp(-t / 0.03)) / SR; x[i] = Math.sin(TAU * ph) * env(t, 0.002, 0.06); }
  return x;
}
function whoosh(sec = 0.8) {
  const n = arr(sec).map(rnd);
  const lo = lp(n, 1200), hi = lp(n, 4000);
  const L = arr(sec), R = arr(sec);
  for (let i = 0; i < L.length; i++) {
    const p = i / L.length, e = Math.sin(Math.PI * p) ** 2;
    const v = (lo[i] * (1 - p) + (hi[i] - lo[i]) * p) * e * 1.4;
    L[i] = v * (1 - p * 0.7); R[i] = v * (0.3 + p * 0.7);
  }
  return [L, R];
}
function thud() {
  const x = arr(0.5);
  const n = lp(x.map(rnd), 500);
  for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] = Math.sin(TAU * 70 * t) * env(t, 0.002, 0.08) + n[i] * env(t, 0.001, 0.05) * 3; }
  return x;
}
function scan(sec) {
  const x = arr(sec);
  let ph = 0;
  for (let i = 0; i < x.length; i++) {
    const t = i / SR, p = t / sec;
    ph += (220 + 440 * p * p) / SR;
    x[i] = (Math.sin(TAU * ph) + 0.4 * Math.sin(TAU * ph * 2.01) + 0.2 * rnd()) * Math.min(1, p * 4) * Math.min(1, (1 - p) * 10) * 0.35;
  }
  return lp(x, 3000);
}
function chime() {
  const x = arr(2.5);
  [587.33, 739.99, 880, 1318.5].forEach((f, k) => {
    for (let i = 0; i < x.length; i++) {
      const t = i / SR - k * 0.045;
      if (t < 0) continue;
      x[i] += (Math.sin(TAU * f * t) + 0.3 * Math.sin(TAU * f * 2.76 * t) * Math.exp(-t / 0.2)) * env(t, 0.002, 0.7) * 0.25;
    }
  });
  return x;
}
// noise through an opening filter plus a rising fifth, cut dead at its end
function riser(sec) {
  const x = arr(sec);
  let y = 0, ph = 0;
  for (let i = 0; i < x.length; i++) {
    const t = i / SR, p = t / sec;
    y += (1 - Math.exp(-TAU * (200 + 7000 * p ** 3) / SR)) * (rnd() - y);
    ph += (110 + 330 * p * p) / SR;
    x[i] = (y * 0.9 + Math.sin(TAU * ph) * 0.25 + Math.sin(TAU * ph * 1.5) * 0.12) * p ** 2.2;
  }
  return x;
}
// the big landing: pitched kick, sub boom, wide crash, chime on top
function hit() {
  const sec = 3.2, L = arr(sec), R = arr(sec);
  const crashL = hp(lp(arr(sec).map(rnd), 9000), 2500), crashR = hp(lp(arr(sec).map(rnd), 9000), 2500);
  const boom = lp(arr(sec).map(rnd), 160);
  const ch = chime();
  for (let i = 0; i < L.length; i++) {
    const t = i / SR;
    const kick = Math.sin(TAU * (42 * t + 7 * (1 - Math.exp(-t / 0.05)))) * env(t, 0.001, 0.35);
    const body = kick + boom[i] * env(t, 0.003, 0.5) * 5 + (ch[i] || 0) * 0.8;
    L[i] = body + crashL[i] * env(t, 0.002, 0.9) * 0.5;
    R[i] = body + crashR[i] * env(t, 0.002, 0.9) * 0.5;
  }
  return [L, R];
}

// Each sound gets its cue and the whole list. `len` on a cue sets the length of scan and riser;
// a riser with no len runs until the next 'hit' cue, so it always lands on it.
// a soft keyboard press: filtered noise click plus a low body
function key() {
  const x = arr(0.07);
  const n = lp(x.map(rnd), 3500);
  for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] = n[i] * env(t, 0.0004, 0.006) * 2.2 + Math.sin(TAU * 260 * t) * env(t, 0.001, 0.012) * 0.25; }
  return hp(x, 300);
}
const SFX = {
  key, lift: () => arr(0.01),
  tick: () => tick(2400),
  'tick-lo': () => tick(1600),
  click, pop, thud, chime, hit,
  whoosh: (c) => whoosh(c.len ?? 0.8),
  scan: (c) => scan(c.len ?? 3),
  riser: (c, cues) => riser(c.len ?? Math.max(0.5, (cues.find((h) => h.name === 'hit' && h.t > c.t)?.t ?? c.t + 4) - c.t)),
};
export const SOUNDS = Object.keys(SFX);

// ------------------------------------------------------------------ music bed
// Eunomia mix: very quiet, no drums. Slow pads (a chord every 4s) and a sparse bell every beat.
// Minor until liftAt (the "remembered." beat), major after it.
function synthBed(sec, { liftAt = Infinity } = {}) {
  const L = arr(sec), R = arr(sec);
  const add = (buf, start, f, g = 1) => { const s = Math.round(start * SR); for (let i = 0; i < f.length && s + i < buf.length; i++) buf[s + i] += f[i] * g; };
  const pad = (fs, d) => {
    const x = arr(d);
    for (let i = 0; i < x.length; i++) { const t = i / SR; const e = Math.min(1, t / 1.6) * Math.min(1, (d - t) / 1.6);
      fs.forEach((f) => (x[i] += (Math.sin(TAU * f * t) + 0.35 * Math.sin(TAU * f * 1.004 * t) + 0.15 * Math.sin(TAU * f * 2 * t)) * e * 0.05)); }
    return lp(x, 1400);
  };
  const bell = (f, a) => {
    const x = arr(2.2);
    for (let i = 0; i < x.length; i++) { const t = i / SR; x[i] = (Math.sin(TAU * f * t) + 0.25 * Math.sin(TAU * f * 3.01 * t) * Math.exp(-t / 0.15)) * env(t, 0.004, 0.7) * a; }
    return x;
  };
  const minor = [[50, 57, 60, 64], [46, 53, 57, 62], [48, 55, 59, 64], [45, 52, 55, 61]];
  const major = [[50, 57, 61, 64], [47, 54, 57, 62], [43, 50, 54, 59], [45, 52, 57, 61]];
  const tune = [3, 2, 1, 2, 3, 1, 2, 0];
  for (let b = 0; b * 4 < sec; b++) {
    const t0 = b * 4, lift = t0 >= liftAt;
    const ch = lift ? major[Math.round((t0 - liftAt) / 4) % 4] : minor[b % 4];
    const p = pad(ch.map(midi), 4.8);
    add(L, t0, p); add(R, t0 + 0.02, p);
    for (let k = 0; k < 4; k++) {
      if ((b + k) % 3 === 2) continue;  // leave gaps so it breathes
      const bl = bell(midi(ch[tune[(b * 4 + k) % 8]] + 24), lift ? 0.05 : 0.035);
      add(k % 2 ? R : L, t0 + k, bl); add(k % 2 ? L : R, t0 + k + 0.18, bl, 0.35);
    }
  }
  fadeOut(L, R, 3);
  return [L, R];
}

// Any audio file ffmpeg can read, as stereo at 48kHz, cut or padded to sec, with a 2s fade out.
export function readAudio(path, sec) {
  const r = spawnSync('ffmpeg', ['-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', String(SR), '-'], { maxBuffer: 1 << 30 });
  if (r.status !== 0) throw new Error(`could not read ${path}: ${r.stderr}`);
  const f = new Float32Array(r.stdout.buffer.slice(r.stdout.byteOffset, r.stdout.byteOffset + r.stdout.length));
  const L = arr(sec), R = arr(sec);
  for (let i = 0; i < L.length && 2 * i + 1 < f.length; i++) { L[i] = f[2 * i]; R[i] = f[2 * i + 1]; }
  fadeOut(L, R, 2);
  return [L, R];
}

function fadeOut(L, R, sec) {
  const n = Math.min(L.length, Math.round(sec * SR));
  for (let i = 0; i < n; i++) { L[L.length - 1 - i] *= i / n; R[R.length - 1 - i] *= i / n; }
}

// drive pushes the mix into a tanh soft clip: louder body, rounded peaks. 2.4 lands this kit near -16 LUFS;
// a mastered track wants about 1. The 0.8 ceiling leaves room for AAC overshoot (true peak stays under -1 dBFS).
// The renderer prints the result; tune drive until it reads your target.
function wav(L, R, drive) {
  const n = L.length;
  const buf = Buffer.alloc(44 + n * 4);
  buf.write('RIFF', 0); buf.writeUInt32LE(36 + n * 4, 4); buf.write('WAVE', 8);
  buf.write('fmt ', 12); buf.writeUInt32LE(16, 16); buf.writeUInt16LE(1, 20); buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24); buf.writeUInt32LE(SR * 4, 28); buf.writeUInt16LE(4, 32); buf.writeUInt16LE(16, 34);
  buf.write('data', 36); buf.writeUInt32LE(n * 4, 40);
  let peak = 1e-9;
  for (let i = 0; i < n; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
  const g = (drive * 0.9) / peak;
  for (let i = 0; i < n; i++) {
    buf.writeInt16LE(Math.round(Math.tanh(L[i] * g) * 0.8 * 32767), 44 + i * 4);
    buf.writeInt16LE(Math.round(Math.tanh(R[i] * g) * 0.8 * 32767), 46 + i * 4);
  }
  return buf;
}

export async function soundtrack(cues, duration, { music = 'synth', musicGain, drive, filmDir = '.' } = {}) {
  seed = 7;  // same cues, same sound, however many formats render in one run
  const hitAt = cues.find((c) => c.name === 'hit')?.t;
  let L = arr(duration), R = arr(duration);
  if (music === 'synth') [L, R] = synthBed(duration, { liftAt: cues.find((c) => c.name === 'lift')?.t ?? hitAt ?? Infinity });
  else if (music) [L, R] = readAudio(resolve(filmDir, music), duration);
  const mg = musicGain ?? (music === 'synth' ? 0.7 : 1);
  for (let i = 0; i < L.length; i++) { L[i] *= mg; R[i] *= mg; }
  const made = {};
  for (const c of cues) {
    if (!SFX[c.name]) throw new Error(`no sound called ${c.name}. The kit has: ${SOUNDS.join(', ')}`);
    const key = `${c.name}:${c.len ?? ''}:${c.name === 'riser' ? c.t : ''}`;
    const s = (made[key] ??= SFX[c.name](c, cues));
    const [a, b] = Array.isArray(s) ? s : [s, s];
    const o = Math.round(c.t * SR), g = c.gain ?? 1;
    for (let i = 0; i < a.length && o + i < L.length; i++) { L[o + i] += a[i] * g; R[o + i] += b[i] * g; }
  }
  return wav(L, R, drive ?? (music === 'synth' ? 2.4 : 1));
}
