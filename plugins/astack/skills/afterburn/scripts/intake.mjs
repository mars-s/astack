#!/usr/bin/env node
// Turns a preview into the handoff the detail pass builds from (see ../SKILL.md, "Intake").
//
//   node intake.mjs <film.html | clip.mp4> [--format 16x9] [--out <dir>]
//
// An html-video film gives exact beats (__beats), the cue sheet (__cues) and transparent layers for every
// element marked data-layer. Any video (a hyperframes render, another skill's MP4, a reference film) gives
// its cut times, 10 fps frames and a still per cut; fill each beat's copy and motion by eye.
// Writes <out>/beats.json, cues.json, stills/, stills.png and layers/ (film) or frames/ (video).
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, extname, join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const argv = process.argv.slice(2);
const opt = (name) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : undefined; };
const fail = (msg) => { console.error(msg); process.exit(1); };

const input = argv[0] && resolve(argv[0]);
if (!input) fail('Usage: node intake.mjs <film.html | clip.mp4> [--format 16x9] [--out <dir>]');
if (spawnSync('ffmpeg', ['-version']).status !== 0) fail('ffmpeg not found. Install it first (macOS: brew install ffmpeg).');
const out = resolve(opt('out') ?? join(dirname(input), 'handoff'));
rmSync(out, { recursive: true, force: true });
mkdirSync(join(out, 'stills'), { recursive: true });

const beats = extname(input) === '.html' ? await fromFilm() : fromVideo();
writeFileSync(join(out, 'beats.json'), JSON.stringify(beats, null, 2));
const n = beats.length;
contactSheet(['-pattern_type', 'glob', '-i', join(out, 'stills', '*.png')], Math.min(n, 4), Math.ceil(n / 4), join(out, 'stills.png'));
console.log(`${n} beats -> ${out}/beats.json\n  stills: ${out}/stills.png`);

// A beat row: the preview's facts, plus the blanks the detail pass fills (style, energy, tactic, exit).
function row(i, t, end, b = {}) {
  return { beat: b.name ?? `b${String(i + 1).padStart(2, '0')}`, t, end: +end.toFixed(3), on_screen: b.copy ?? '', motion: b.motion ?? '',
    still: `stills/${String(i + 1).padStart(2, '0')}.png`, style: '', energy: '', tactic: '', exit: '' };
}

async function fromFilm() {
  const chromium = loadChromium();
  const browser = await chromium.launch();
  const url = pathToFileURL(input).href + `?render${opt('format') ? `&format=${opt('format')}` : ''}`;
  const probe = await browser.newPage();
  await probe.goto(url);
  await probe.evaluate(() => window.__ready);
  const { w, h } = await probe.evaluate(() => window.__size);
  // Scale 3 so a camera can push into a layer and stay sharp; stills are shot at css size.
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 3 });
  page.on('pageerror', (e) => console.error('page error:', e.message));
  await page.goto(url);
  await page.evaluate(() => window.__ready);
  const film = await page.evaluate(() => ({ duration: window.__duration, format: window.__format, cues: window.__cues ?? [], beats: window.__beats ?? [] }));
  if (!film.beats.length) fail('The film has no window.__beats. Add a beat() call per beat (html-video SKILL.md, The film contract).');
  const seek = (t) => page.evaluate((t) => window.__seek(t), t);

  const beats = film.beats.map((b, i) => row(i, b.t, film.beats[i + 1]?.t ?? film.duration, b));
  for (const b of beats) {
    await seek((b.t + b.end) / 2);
    await page.screenshot({ path: join(out, b.still), scale: 'css' });
  }

  // One transparent PNG per data-layer element, shot alone at its data-at time.
  mkdirSync(join(out, 'layers'), { recursive: true });
  const layers = await page.evaluate(() => [...document.querySelectorAll('[data-layer]')].map((el) => ({ name: el.dataset.layer, at: el.dataset.at })));
  for (const { name, at } of layers) {
    if (at === undefined) { console.error(`layer ${name}: no data-at, skipped`); continue; }
    await seek(Number(at));
    const box = await page.evaluate((name) => {
      const s = document.createElement('style');
      s.id = '__solo';
      s.textContent = `html, body { background: transparent !important } body * { visibility: hidden !important }
        [data-layer="${name}"], [data-layer="${name}"] * { visibility: visible !important }`;
      document.head.append(s);
      const r = document.querySelector(`[data-layer="${name}"]`).getBoundingClientRect();
      return { x: r.x, y: r.y, width: r.width, height: r.height };
    }, name);
    await page.screenshot({ path: join(out, 'layers', `${name}.png`), clip: box, omitBackground: true });
    await page.evaluate(() => document.getElementById('__solo').remove());
    const beat = beats.findLast((b) => b.t <= Number(at));
    if (beat) (beat.layers ??= []).push({ name, x: box.x, y: box.y, w: box.width, h: box.height });
  }
  await browser.close();

  // soundtrack.mjs reads [[seconds, name, gain]].
  writeFileSync(join(out, 'cues.json'), JSON.stringify(film.cues.map((c) => [c.t, c.name, c.gain ?? 1])));
  writeFileSync(join(out, 'film.json'), JSON.stringify({ source: input, duration: film.duration, format: film.format, size: { w, h } }, null, 2));
  console.log(`${layers.length} layers -> ${out}/layers/   ${film.cues.length} cues -> ${out}/cues.json`);
  return beats;
}

function fromVideo() {
  const probe = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:format=duration', '-of', 'json', input], { encoding: 'utf8' });
  if (probe.status !== 0) fail(`ffprobe could not read ${input}`);
  const info = JSON.parse(probe.stdout), duration = Number(info.format.duration), { width: w, height: h } = info.streams[0];
  // ponytail: a scene-change threshold finds hard cuts; transforms and pushes inside one shot need your eye on frames/.
  const scan = spawnSync('ffmpeg', ['-hide_banner', '-i', input, '-vf', "select='gt(scene,0.3)',showinfo", '-f', 'null', '-'], { encoding: 'utf8' });
  const cuts = [...scan.stderr.matchAll(/pts_time:([\d.]+)/g)].map((m) => Number(m[1])).filter((t) => t > 0.2 && t < duration - 0.2);
  const starts = [0, ...cuts];
  const beats = starts.map((t, i) => row(i, +t.toFixed(3), starts[i + 1] ?? duration));
  for (const b of beats) spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-ss', String((b.t + b.end) / 2), '-i', input, '-frames:v', '1', join(out, b.still)]);
  mkdirSync(join(out, 'frames'), { recursive: true });
  spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-i', input, '-vf', 'fps=10,scale=640:-2', join(out, 'frames', 'f_%04d.jpg')]);
  writeFileSync(join(out, 'cues.json'), '[]');
  writeFileSync(join(out, 'film.json'), JSON.stringify({ source: input, duration, size: { w, h } }, null, 2));
  console.log(`${cuts.length} cuts found; frames at 10 fps -> ${out}/frames/`);
  return beats;
}

function contactSheet(inputArgs, cols, rows, file) {
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', ...inputArgs, '-vf', `scale=480:-2,tile=${cols}x${rows}`, '-frames:v', '1', file], { encoding: 'utf8' });
  if (r.status !== 0) console.error(r.stderr);
}

function loadChromium() {
  for (const from of [process.cwd(), dirname(input), process.env.PW_FROM && dirname(process.env.PW_FROM)].filter(Boolean)) {
    const req = createRequire(join(from, 'noop.js'));
    for (const id of ['playwright', '@playwright/test', 'playwright-core']) {
      try { return req(id).chromium; } catch {}
    }
  }
  fail('Playwright not found. Run from a project that has it (npm i -D playwright && npx playwright install chromium), or set PW_FROM.');
}
