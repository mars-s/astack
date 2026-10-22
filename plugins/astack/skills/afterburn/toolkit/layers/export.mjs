// Renders the text and UI layers for one scene to transparent PNGs, for Blender to place on planes.
//   node export.mjs <scene> [name ...]
// A scene file (scenes/<scene>.js) registers layers on window.LAYERS: { name: { w, h, scale?, frames?, html(f) } }.
// A layer with frames renders a numbered sequence <name>/0001.png...; without, a single <name>.png.
import { createRequire } from 'node:module';
import { mkdirSync, existsSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(process.env.PW_FROM ?? join(here, 'package.json'));
const { chromium } = require('playwright');
const [scene, ...only] = process.argv.slice(2);
const outRoot = join(here, 'out', scene);
mkdirSync(outRoot, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage();
page.on('pageerror', (e) => console.error('page error:', e.message));
await page.goto(pathToFileURL(join(here, 'layers.html')).href + `?scene=${scene}`);
await page.evaluate(() => window.__ready);
const specs = await page.evaluate(() => Object.fromEntries(Object.entries(window.LAYERS).map(([k, v]) => [k, { w: v.w, h: v.h, scale: v.scale ?? 2, frames: v.frames ?? 0 }])));
let n = 0;
for (const [name, s] of Object.entries(specs)) {
  if (only.length && !only.includes(name)) continue;
  const ctx = await browser.newContext({ viewport: { width: s.w, height: s.h }, deviceScaleFactor: s.scale });
  const p = await ctx.newPage();
  p.on('pageerror', (e) => console.error(name, 'page error:', e.message));
  await p.goto(pathToFileURL(join(here, 'layers.html')).href + `?scene=${scene}`);
  await p.evaluate(() => window.__ready);
  const shoot = async (f, file) => {
    await p.evaluate(([nm, f]) => window.__show(nm, f), [name, f]);
    await p.screenshot({ path: file, omitBackground: true });
  };
  if (s.frames) {
    const dir = join(outRoot, name);
    if (existsSync(dir)) rmSync(dir, { recursive: true });
    mkdirSync(dir, { recursive: true });
    for (let f = 1; f <= s.frames; f++) await shoot(f, join(dir, String(f).padStart(4, '0') + '.png'));
  } else await shoot(0, join(outRoot, name + '.png'));
  await ctx.close();
  n++;
}
await browser.close();
console.log(`exported ${n} layers to ${outRoot}`);
