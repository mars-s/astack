// Scene G: the code editor. One sequence (frame = scene frame) carries everything that happens inside the window.
window.PRELOAD = ['../../forest.jpg'];
const K = 'color:#e05cc8', F = 'color:#3fc6e8', S = 'color:#f2c46a', C = 'color:#8fe3ad';
// each line: [html, plain-text length]
const L = (parts) => [parts.map(([t, st]) => st ? `<span style="${st}">${t}</span>` : t).join(''), parts.reduce((n, [t]) => n + t.length, 0)];
const CODE = [
  L([['def', K], [' '], ['sign_in', F], ['(user):']]),
  L([['    notes = '], ['recall', F], ['('], ['"auth decisions"', S], [')']]),
  L([['    flow = '], ['start_pkce', F], ['(user)']]),
  L([['    verifier = flow.code_verifier']]),
  L([['']]),
  L([['    secret = CLIENT_SECRET']]),
  L([['']]),
  L([['    token = '], ['exchange', F], ['(flow, verifier)']]),
  L([['    token.refresh_at = token.expires - '], ['60', S]]),
  L([['    '], ['return', K], [' '], ['session', F], ['(token)']]),
];
const FIXED = L([['    # no client secret. PKCE only. (Ada, Tue)', C]]);
const BAD = '    secret = CLIENT_SECRET';
const GLYPH = '#%&@$/\\|<>{}=+*?!0123456789';
// typed reveal of a line's html: keep tags, reveal n visible characters
const reveal = (html, n) => { let out = '', seen = 0, i = 0; while (i < html.length && seen < n) { if (html[i] === '<') { const j = html.indexOf('>', i); out += html.slice(i, j + 1); i = j + 1; continue; } if (html[i] === '&') { const j = html.indexOf(';', i); out += html.slice(i, j + 1); i = j + 1; seen++; continue; } out += html[i++]; seen++; } const opens = (out.match(/<span/g) || []).length - (out.match(/<\/span>/g) || []).length; return out + '</span>'.repeat(Math.max(0, opens)); };
const BURSTS = [[8, [0, 1]], [13, [0, 1, 2, 3]], [19, [0, 1, 2, 3, 5]], [26, [0, 1, 2, 3, 5, 7]], [33, [0, 1, 2, 3, 5, 7, 8]], [40, [0, 1, 2, 3, 5, 7, 8, 9]]];
const GREEN_AT = { 0: 52, 1: 55, 2: 58, 3: 61, 7: 106, 8: 108, 9: 110 };
const RED_AT = 64, SCRUB0 = 74, SCRUB1 = 98, FIX_AT = 100, FIXGREEN = 104, WIDE = 117;
let seed = 3; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
const scramble = (f) => { seed = 7 + f * 13; return [...BAD].map((ch, i) => { const head = 4 + (BAD.length - 4) * clamp01((f - SCRUB0) / (SCRUB1 - SCRUB0)); if (i < 4) return ch; if (i < head - 1) return GLYPH[Math.floor(rnd() * GLYPH.length)]; if (i < head) return `<span style="background:#fff;color:#000">${GLYPH[Math.floor(rnd() * GLYPH.length)]}</span>`; return ch; }).join(''); };
LAYERS.editor = {
  w: 1240, h: 720, scale: 2, frames: 159,
  html: (f) => {
    const frost = 1 - clamp01((f - 1) / 8);
    const typedChars = (li) => { let n = 0; for (const [t, ls] of BURSTS) if (f >= t && ls.includes(li)) n = Math.max(n, Math.min(CODE[li][1], Math.round(CODE[li][1] * clamp01((f - t + 3) / 6)))); return f >= 46 ? CODE[li][1] : n; };
    const lines = CODE.map(([html, len], li) => {
      let body = reveal(html, typedChars(li)), bar = '', mark = '', note = '';
      const g = GREEN_AT[li];
      const barGreen = (k) => `<div style="position:absolute;left:64px;top:3px;bottom:3px;width:calc(${k} * (100% - 64px));background:linear-gradient(90deg,#19e04f 0%,#12b33c 30%,rgba(10,90,30,.55) 62%,rgba(10,60,20,0) 100%)"></div>`;
      const barRed = `<div style="position:absolute;left:64px;top:3px;bottom:3px;width:calc(100% - 64px);background:linear-gradient(90deg,#e3192a 0%,#b3101e 35%,rgba(120,10,20,.4) 65%,rgba(80,0,10,0) 100%)"></div>`;
      if (g && f >= g && f < WIDE) { bar = barGreen(clamp01((f - g + 1) / 3)); }
      if (g && f >= g + 1) mark = '<span style="color:#34e05a;font-weight:800;font-size:27px;margin-left:16px">&#10003;</span>';
      if (li === 5) {
        if (f >= RED_AT && f < FIXGREEN) { bar = barRed; mark = '<span style="color:#ff3030;font-weight:800;font-size:27px;margin-left:16px">&#10005;</span>'; body = `<span style="color:#ff6b6b">${BAD}</span>`; }
        if (f >= 70 && f < FIXGREEN) note = `<span style="margin-left:40px;font-family:var(--font);font-size:17px;color:rgba(255,255,255,.55)">recalling decision${'.'.repeat(1 + Math.floor(f / 4) % 3)}</span>`;
        if (f >= SCRUB0 && f < FIX_AT) body = `<span style="color:#ff8a8a">${scramble(f)}</span>`;
        if (f >= FIX_AT) body = reveal(FIXED[0], Math.round(FIXED[1] * clamp01((f - FIX_AT + 1) / 4)));
        if (f >= FIXGREEN && f < WIDE) bar = barGreen(clamp01((f - FIXGREEN + 1) / 3));
        if (f >= FIXGREEN + 1) mark = '<span style="color:#34e05a;font-weight:800;font-size:27px;margin-left:16px">&#10003;</span>';
        if (f >= FIXGREEN + 1 && f < WIDE) note = `<span style="margin-left:40px;font-family:var(--font);font-size:17px;color:rgba(160,255,200,.7)">recalled from Eunomia</span>`;
      }
      return `<div style="position:relative;height:40px;display:flex;align-items:center;white-space:pre">${bar}
        <span style="position:relative;width:64px;text-align:right;padding-right:26px;color:#5d636c">${li + 1}</span>
        <span style="position:relative">${body}</span>${mark ? `<span style="position:relative">${mark}</span>` : ''}${note ? `<span style="position:relative">${note}</span>` : ''}</div>`;
    }).join('');
    const glitch = f <= 6 ? `<div style="position:absolute;left:96px;top:96px;font-size:30px;font-weight:500;background:#ff5fb7;color:#fff;padding:0 6px;opacity:${1 - f / 7}">Reca</div><div style="position:absolute;left:190px;top:76px;font-size:22px;background:#2f7fd8;color:#dfeaff;padding:0 6px;opacity:${1 - f / 7}">lled.</div>` : '';
    return `<div style="position:absolute;inset:0;border-radius:18px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.14)">
      <div style="position:absolute;inset:-60px;background:url(../../forest.jpg) center/2200px auto;filter:blur(26px) brightness(1.35) saturate(.7);opacity:${frost}"></div>
      <div style="position:absolute;inset:0;background:rgba(9,11,14,${0.9 * (1 - frost) + 0.25 * frost})"></div>
      <div style="position:absolute;left:0;right:0;top:0;height:52px;display:flex;align-items:center;gap:28px;padding:0 22px;border-bottom:1px solid rgba(255,255,255,.07);font-size:16px;color:#c9ccd2;opacity:${1 - frost}">
        <div style="display:flex;gap:9px;margin-right:22px"><span style="width:14px;height:14px;border-radius:50%;background:#ff5f57"></span><span style="width:14px;height:14px;border-radius:50%;background:#febc2e"></span><span style="width:14px;height:14px;border-radius:50%;background:#28c840"></span></div>
        <span>File</span><span>Edit</span><span>View</span><span>Go</span><span>Run</span><span>Terminal</span><span>Window</span><span>Help</span></div>
      <div style="position:absolute;left:0;top:52px;bottom:30px;width:1px;left:64px;background:rgba(255,255,255,.06)"></div>
      <div style="position:absolute;left:0;right:0;top:78px;font-family:var(--mono);font-size:21px;color:#e8eaee;opacity:${1 - frost * 0.8}">${lines}</div>
      <div style="position:absolute;left:0;right:0;bottom:0;height:30px;border-top:1px solid rgba(255,255,255,.07);display:flex;align-items:center;gap:22px;padding:0 18px;font-size:12px;color:#8a9099;opacity:${1 - frost}">
        <span>main</span><span>Python 3.12</span><span style="margin-left:auto">Ln 6, Col 5</span><span>Spaces: 4</span><span>UTF-8</span></div>
      ${glitch}</div>`;
  },
};
