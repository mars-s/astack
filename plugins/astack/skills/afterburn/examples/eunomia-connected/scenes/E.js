// Scene E/F: poster cards (one remembered fact each), the hub button, "Recalled." with bouncy letters, glitch slices.
const ART = '../../art-raw/v2/';
window.PRELOAD = Array.from({ length: 12 }, (_, i) => `${ART}p${String(i + 1).padStart(2, '0')}.png`).concat(['../../sea.jpg']);
const CARD = { w: 560, h: 300, scale: 2 };
const meta = (who, c = 'rgba(255,255,255,.75)') => `<div style="position:absolute;left:24px;bottom:16px;font-family:var(--mono);font-size:11px;letter-spacing:.04em;color:${c}">REMEMBERED · ${who}</div>`;
const card = (n, inner, pos = 'center') => ({ ...CARD, html: () => `<div style="position:absolute;left:20px;top:20px;width:520px;height:260px;border-radius:22px;overflow:hidden;
  box-shadow:0 10px 26px rgba(10,30,60,.28);background:#111 url(${ART}p${n}.png) ${pos}/cover no-repeat">${inner}</div>` });
const T = (css, html) => `<div style="position:absolute;${css}">${html}</div>`;
Object.assign(LAYERS, {
  card01: card('01', T('right:26px;top:30px;text-align:right;font-family:Anton;font-size:56px;line-height:.92;color:#fff;letter-spacing:.01em', 'PKCE.<br>NO CLIENT<br>SECRETS.') + meta('CLAUDE CODE · ADA'), '30% center'),
  card02: card('02', T('left:26px;top:24px;font-family:&quot;Archivo Black&quot;;font-size:58px;line-height:.9;color:#15233a;letter-spacing:-.02em', 'DEPLOY<br>FREEZE') + T('left:28px;top:150px;font-family:var(--font);font-size:17px;font-weight:600;color:#15233a', 'Thursday, 5 pm. No merges.') + meta('CODEX · PRIYA', 'rgba(21,35,58,.75)')),
  card03: card('03', T('right:24px;top:26px;text-align:right;font-family:&quot;Bebas Neue&quot;;font-size:64px;line-height:.86;color:#ffd84a', 'TOKENS<br>REFRESH<br>60s EARLY') + meta('CURSOR · AUTH.RS', 'rgba(255,216,74,.8)'), '20% center'),
  card04: card('04', T('left:20px;bottom:36px;padding:8px 16px 10px;background:#f6eedf;font-family:&quot;DM Serif Display&quot;;font-size:50px;line-height:.95;color:#14204a', 'Priya owns<br><i>billing.</i>') + meta('YOU · ACME', 'rgba(20,32,74,.75)')),
  card05: card('05', T('left:28px;top:34px;font-family:&quot;Instrument Serif&quot;;font-style:italic;font-size:64px;line-height:.95;color:#fff', 'Async over<br>meetings.') + meta('CLAUDE CODE · ADA')),
  card06: card('06', T('right:26px;bottom:38px;text-align:right;font-family:Anton;font-size:60px;line-height:.9;color:#fff', 'SHIP BEHIND<br>A FLAG') + meta('CURSOR · WEB')),
  card07: card('07', T('left:26px;top:30px;font-family:Unbounded;font-weight:900;font-size:44px;line-height:1;color:#b9ffd9;letter-spacing:-.01em', 'SELF-HOST<br>FIRST.') + meta('YOU · ROADMAP')),
  card08: card('08', T('left:22px;top:44px;padding:6px 14px 2px;background:#fff;font-family:Anton;font-size:52px;line-height:1;color:#0d0d0d', 'NEVER LOG EMAILS') + T('left:22px;top:118px;padding:4px 10px;background:#0d0d0d;font-family:var(--mono);font-size:15px;color:#fff', 'redact(pii) before write()') + meta('CODEX · SECURITY')),
  card09: card('09', T('right:20px;top:22px;padding:10px 14px;text-align:right;background:#f3ead8;font-family:&quot;Archivo Black&quot;;font-size:44px;line-height:.95;color:#111', 'STAGING<br>FIRST.<br>ALWAYS.') + meta('CLAUDE CODE · OPS', 'rgba(17,17,17,.7)'), '0% center'),
  card10: card('10', T('left:26px;top:30px;font-family:&quot;Space Grotesk&quot;;font-weight:700;font-size:46px;line-height:1;color:#fff;letter-spacing:-.02em', 'Ada reviews<br>every schema.') + meta('CODEX · ADA')),
  card11: card('11', T('left:26px;bottom:38px;font-family:Anton;font-size:72px;line-height:.86;color:#fbe9d0', 'PIN RUST<br>1.84') + meta('CURSOR · CI', 'rgba(251,233,208,.8)')),
  card12: card('12', T('left:28px;top:28px;font-family:&quot;Bebas Neue&quot;;font-size:70px;line-height:.86;color:#fff', 'ONE<br>SHARED<br>MEMORY') + meta('EUNOMIA'), '80% center'),
});
LAYERS.hubglow = { w: 700, h: 700, scale: 1, html: () => `<div style="position:absolute;inset:0;background:radial-gradient(circle, #fff 0%, #fff 30%, rgba(255,255,255,.85) 42%, rgba(255,255,255,0) 70%)"></div>` };
LAYERS.btn = { w: 260, h: 260, scale: 2, html: () => `<div style="position:absolute;inset:10px;border-radius:50%;background:radial-gradient(circle at 35% 30%, #6be0a3, #2b9a62 68%, #1f7a4c);box-shadow:0 16px 40px rgba(31,122,76,.45)"></div>` };
LAYERS.arrow = { w: 260, h: 260, scale: 2, html: () => `<svg viewBox="0 0 24 24" style="position:absolute;inset:70px;fill:none;stroke:#fff;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>` };
LAYERS.sky = { w: 1920, h: 1080, scale: 1, html: () => `<div style="position:absolute;inset:-60px;background:url(../../sea.jpg) 50% 0%/2400px auto no-repeat;filter:blur(38px) brightness(1.18) saturate(.9)"></div>
  <div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 48%, rgba(255,255,255,.95) 0%, rgba(255,255,255,.6) 30%, rgba(255,255,255,0) 70%)"></div>` };
// "Recalled." with letters that pop in blue and settle to ink
const WORDR = 'Recalled.';
LAYERS.recalled = { w: 900, h: 200, scale: 3, frames: 26, html: (f) => {
  const letters = [...WORDR].map((ch, i) => {
    const t0 = 1 + i * 1.5, k = clamp01((f - t0) / 5);
    if (f < t0) return `<span style="display:inline-block;opacity:0">${ch}</span>`;
    const blue = f - t0 < 6 || ch === '.';
    const s = 0.55 + 0.45 * ease.back(k), y = 18 * (1 - ease.out(k));
    return `<span style="display:inline-block;transform:translateY(${y}px) scale(${s});transform-origin:50% 90%;color:${blue ? '#2f7fd8' : '#0f1418'}">${ch}</span>`;
  }).join('');
  return `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:84px;font-weight:500;letter-spacing:-0.03em">${letters}</div>`;
} };
const word = (style = '') => `<span style="${style}">Recalled.</span>`;
LAYERS.gl_sel = { w: 900, h: 200, scale: 2, html: () => `<div style="position:absolute;left:265px;top:52px;width:370px;height:96px;background:#2f7fd8"></div>` };
LAYERS.gl_white = { w: 900, h: 200, scale: 2, html: () => `<div style="position:absolute;left:265px;top:56px;width:370px;height:88px;background:#fff"></div>` };
LAYERS.gl_slice = { w: 900, h: 200, scale: 2, html: () => `<div style="position:absolute;left:250px;top:84px;font-size:56px;font-weight:500;letter-spacing:-.03em;background:#2f7fd8;color:#dfeaff;padding:0 8px">Reca</div>
  <div style="position:absolute;left:470px;top:36px;font-size:56px;font-weight:500;letter-spacing:-.03em;background:#2f7fd8;color:#dfeaff;padding:0 8px">lled.</div>` };
LAYERS.gl_slice2 = { w: 900, h: 200, scale: 2, html: () => `<div style="position:absolute;left:300px;top:96px;font-size:56px;font-weight:500;letter-spacing:-.03em;background:#ff5fb7;color:#fff;padding:0 8px">Reca</div>
  <div style="position:absolute;left:452px;top:60px;font-size:40px;font-weight:500;letter-spacing:-.03em;background:#2f7fd8;color:#dfeaff;padding:0 8px">lled.</div>` };
