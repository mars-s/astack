// Cue sheet -> soundtrack: a quiet pad bed (synth.mjs) plus soft UI sounds on picture beats.
//   node soundtrack.mjs <out.wav> <seconds> <cues.json> [drive]
// cues.json: [[seconds, "tick" | "tick-lo" | "click" | "pop" | "chime" | "thud" | "key" | "lift", gain], ...]
// 'lift' (gain 0) switches the bed from minor to major at that moment (dark-to-light beats). Tune drive until the
// measured loudness hits the target: ffmpeg -i out.wav -af ebur128 -f null - 2>&1 | grep "I:"
import { readFileSync, writeFileSync } from 'node:fs';
import { soundtrack } from './synth.mjs';
const [out, secs, cuesPath, drive = '1.35'] = process.argv.slice(2);
const cues = JSON.parse(readFileSync(cuesPath, 'utf8')).map(([t, name, gain]) => ({ t, name, gain })).sort((a, b) => a.t - b.t);
writeFileSync(out, await soundtrack(cues, Number(secs), { music: 'synth', musicGain: 0.7, drive: Number(drive) }));
console.log(`${cues.length} cues -> ${out}`);
