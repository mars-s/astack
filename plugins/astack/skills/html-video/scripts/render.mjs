#!/usr/bin/env node
// Renders an HTML film (see ../SKILL.md, "The film contract") to MP4, then proves the result:
// a contact sheet cut from the encoded file and its loudness.
//
//   node render.mjs <film.html> [--format 9x16 | --all] [--stills 1,4.5,9] [--audio-only] [--silent] [--fps 30] [--swiftshader]
//
// Outputs land in <film folder>/out/. Playwright is resolved from the current folder (then the
// film's folder), so run this from inside the project that has it installed.
import { createRequire } from 'node:module';
import { spawn, spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const argv = process.argv.slice(2);
const flag = (name) => argv.includes(`--${name}`);
const opt = (name) => { const i = argv.indexOf(`--${name}`); return i >= 0 ? argv[i + 1] : undefined; };
const fail = (msg) => { console.error(msg); process.exit(1); };

const film = argv.find((a) => a.endsWith('.html'));
if (!film) fail('Usage: node render.mjs <film.html> [--format 9x16 | --all] [--stills 1,4.5,9] [--audio-only] [--silent] [--fps 30] [--swiftshader]');
const filmPath = resolve(film), filmDir = dirname(filmPath);
const stem = basename(filmPath, '.html');
const name = stem === 'index' ? basename(filmDir) : stem;
const fps = Number(opt('fps') ?? 30);
const stills = opt('stills')?.split(',').map(Number);
const outDir = join(filmDir, 'out');
mkdirSync(outDir, { recursive: true });

if (spawnSync('ffmpeg', ['-version']).status !== 0) fail('ffmpeg not found. Install it first (macOS: brew install ffmpeg).');
const chromium = loadChromium();
// --swiftshader forces software GL: use it only when a WebGL film gets no context (headless Linux, CI). It is ~3x slower.
const browser = await chromium.launch({ args: flag('swiftshader') ? ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] : [] });
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('page error:', e.message));
page.on('console', (m) => { if (m.type() === 'error') console.error('console error:', m.text()); });
const seek = (t) => page.evaluate((t) => window.__seek(t), t);

const first = await open(opt('format'));
const formats = flag('all') ? (first.formats.length ? first.formats : [first.format]) : [first.format];
for (const format of formats) {
  const info = format === first.format ? first : await open(format);
  const base = join(outDir, `${name}-${format}`);
  if (stills) await renderStills(info, base);
  else if (flag('audio-only')) { const wav = await soundtrack(info, base); console.log(`${wav}  ${loudness(wav)}`); }
  else await renderFilm(info, base);
}
await browser.close();

// Loads the film for one format and sizes the viewport to it. Loads twice when the size changes, so nothing
// in the page ever sees the wrong viewport.
async function open(format) {
  const url = pathToFileURL(filmPath).href + `?render${format ? `&format=${encodeURIComponent(format)}` : ''}`;
  const load = async () => {
    await page.goto(url);
    await page.evaluate(() => window.__ready);
    return page.evaluate(() => ({ size: window.__size, duration: window.__duration, cues: window.__cues ?? [],
      formats: window.__formats ?? [], format: window.__format, audio: window.__audio ?? {} }));
  };
  let info = await load();
  if (!info.size?.w || !info.size?.h || !info.duration || typeof info.format !== 'string')
    fail('The film must set window.__size, __duration and __format before __ready resolves (SKILL.md, The film contract).');
  if (format && info.format !== format) fail(`The film does not support format ${format}. It has: ${info.formats.join(', ')}`);
  const vp = page.viewportSize();
  if (vp?.width !== info.size.w || vp?.height !== info.size.h) {
    await page.setViewportSize({ width: info.size.w, height: info.size.h });
    info = await load();
  }
  return info;
}

async function renderStills(info, base) {
  const dir = `${base}-stills`;
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(dir, { recursive: true });
  for (const t of stills) {
    await seek(t);
    await page.screenshot({ path: join(dir, `t${t.toFixed(2).padStart(6, '0')}.png`) });
  }
  const sheet = `${base}-stills.png`;
  contactSheet(['-pattern_type', 'glob', '-i', join(dir, '*.png')], info.size, stills.length, sheet);
  console.log(`stills: ${dir}/  sheet: ${sheet}`);
}

async function renderFilm(info, base) {
  const mp4 = `${base}.mp4`;
  const wav = flag('silent') ? null : await soundtrack(info, base);
  const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-'];
  if (wav) args.push('-i', wav);
  args.push('-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p');
  if (wav) args.push('-c:a', 'aac', '-b:a', '192k', '-shortest');
  args.push('-movflags', '+faststart', mp4);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((r) => ff.on('close', r));
  const frames = Math.round(info.duration * fps);
  for (let i = 0; i < frames; i++) {
    await seek(i / fps);
    const png = await page.screenshot();
    if (!ff.stdin.write(png)) await new Promise((r) => ff.stdin.once('drain', r));
    if (i % (fps * 5) === 0) process.stdout.write(`\r${info.format}  frame ${i}/${frames}`);
  }
  ff.stdin.end();
  if ((await done) !== 0) fail(`ffmpeg failed on ${mp4}`);
  const sheet = `${base}-sheet.png`;
  contactSheet(['-i', mp4], info.size, 16, sheet, `fps=16/${info.duration}`);
  const mb = (statSync(mp4).size / 1e6).toFixed(1);
  console.log(`\r${mp4}  ${info.duration}s  ${info.size.w}x${info.size.h}  ${mb} MB  ${wav ? loudness(mp4) : 'silent'}\n  sheet from the encoded file: ${sheet}`);
}

// The film's own synth.mjs if it has one, else the kit next to this script.
async function soundtrack(info, base) {
  const local = join(filmDir, 'synth.mjs');
  const kit = existsSync(local) ? local : join(dirname(fileURLToPath(import.meta.url)), '..', 'scaffold', 'synth.mjs');
  const { soundtrack } = await import(pathToFileURL(kit).href);
  const wav = `${base}-soundtrack.wav`;
  writeFileSync(wav, await soundtrack(info.cues, info.duration, { ...info.audio, filmDir }));
  return wav;
}

function contactSheet(input, size, count, out, pick = null) {
  const cols = Math.min(count, size.w >= size.h ? 4 : 8);
  const rows = Math.ceil(count / cols);
  const tw = Math.round((size.w >= size.h ? 1920 : 2160) / cols);
  const vf = [pick, `scale=${tw}:-2`, `tile=${cols}x${rows}`].filter(Boolean).join(',');
  const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', ...input, '-vf', vf, '-frames:v', '1', out], { encoding: 'utf8' });
  if (r.status !== 0) console.error(r.stderr);
}

function loudness(file) {
  const r = spawnSync('ffmpeg', ['-hide_banner', '-nostats', '-i', file, '-af', 'ebur128=peak=true:framelog=quiet', '-f', 'null', '-'], { encoding: 'utf8' });
  const lufs = r.stderr.match(/I:\s+(-?[\d.]+) LUFS/)?.[1], peak = r.stderr.match(/Peak:\s+(-?[\d.]+) dBFS/)?.[1];
  return `${lufs} LUFS  peak ${peak} dBFS`;
}

function loadChromium() {
  for (const from of [process.cwd(), filmDir]) {
    const req = createRequire(join(from, 'noop.js'));
    for (const id of ['playwright', '@playwright/test', 'playwright-core']) {
      try { return req(id).chromium; } catch {}
    }
  }
  fail('Playwright not found. In the project folder run: npm i -D playwright && npx playwright install chromium');
}
