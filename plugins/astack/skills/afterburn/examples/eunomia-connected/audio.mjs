// Soundtrack for the v2 cut: the quiet pad bed from ../synth.mjs plus soft ticks and key clicks on the picture.
// Mix rules (eunomia-promo-video skill): very quiet music, no drums, typing and tiny UI ticks only, no whooshes,
// about -19 LUFS. Times are film seconds; frame numbers below are film frames at 30 fps.
//   node audio.mjs out/eunomia-v2-soundtrack.wav
import { writeFileSync } from 'node:fs';
import { soundtrack } from '../synth.mjs';

const fr = (f) => f / 30;
const cues = [];
const cue = (t, name, gain) => cues.push({ t: +t.toFixed(3), name, gain });
// ponytail: typing clicks removed at the owner's request (2026-10-21); the calls stay so the cue sheet still reads like the picture
const typing = () => {};

// A: too many ...
cue(0.43, 'tick-lo', 0.22); cue(0.63, 'tick', 0.2); cue(0.7, 'tick', 0.22); cue(1.27, 'tick-lo', 0.22); cue(1.53, 'tick', 0.22);
for (const f of [61, 62, 63, 65, 66, 68]) cue(fr(f), 'click', 0.1);
// B: dots, typed labels, the ring
cue(fr(80), 'pop', 0.12); cue(fr(101), 'pop', 0.12);
typing(fr(78 + 57), 16, 1 / 30); typing(fr(78 + 64), 13, 1 / 30); typing(fr(78 + 86), 10, 1 / 30, 0.1); typing(fr(78 + 90), 8, 1 / 30, 0.1);
for (let i = 0; i < 6; i++) cue(fr(78 + 133 + i), i % 2 ? 'tick' : 'tick-lo', 0.1);
cue(fr(78 + 156), 'lift', 0); cue(fr(78 + 157), 'chime', 0.16); typing(fr(78 + 157), 11, 1 / 30, 0.12);
// D: the lockup types, the heading lands, the question types
typing(fr(299 + 8), 7, 1.6 / 30, 0.14); cue(fr(299 + 43), 'tick', 0.16);
typing(fr(299 + 48), 30, 0.8 / 30, 0.13);
// E/F: send, cards fire, Recalled., glitch
cue(fr(399 + 1), 'click', 0.28);
for (let i = 0; i < 12; i++) cue(fr(399 + 3 + 1.4 * i), i % 2 ? 'tick' : 'tick-lo', 0.09);
for (let i = 0; i < 9; i++) cue(fr(399 + 47 + 1.5 * i), 'tick', 0.1);
for (const f of [67, 68, 69, 71]) cue(fr(399 + f), 'click', 0.1);
// G: code bursts, green ticks, the error, the scramble, the fix, the cube
for (const b of [8, 13, 19, 26, 33, 40]) typing(fr(471 + b), 6, 1 / 30, 0.11);
for (const g of [52, 55, 58, 61]) cue(fr(471 + g), 'tick', 0.16);
cue(fr(471 + 64), 'tick-lo', 0.26); cue(fr(471 + 66), 'tick-lo', 0.2);
typing(fr(471 + 74), 24, 1 / 30, 0.1);
cue(fr(471 + 104), 'tick', 0.2); for (const g of [106, 108, 110]) cue(fr(471 + g), 'tick', 0.14);
cue(fr(471 + 118), 'pop', 0.12);
// H: labels arrive, dots glow as the tree reaches them, blossoms
for (let i = 0; i < 10; i++) cue(fr(630 + 4 + i * 3), i % 2 ? 'tick' : 'tick-lo', 0.06);
for (let i = 0; i < 12; i++) cue(fr(630 + 72 + i * 2.5), 'tick', 0.06);
for (let i = 0; i < 10; i++) cue(fr(630 + 112 + i * 4), 'tick-lo', 0.05);
// I: the words, the mark, the end card
for (const f of [4, 13, 31, 36, 64, 90]) cue(fr(810 + f), 'tick', 0.14);
cue(fr(810 + 112), 'chime', 0.18); typing(fr(810 + 116), 7, 1.7 / 30, 0.12);

const wav = await soundtrack(cues.sort((a, b) => a.t - b.t), 35, { music: 'synth', musicGain: 0.7, drive: 1.35 });
writeFileSync(process.argv[2], wav);
console.log(`${cues.length} cues -> ${process.argv[2]}`);
