// Scene I/J: "One place to remember / recall / share." over the meadow, the mark drawing on, and the end card.
const WORD_C = '#ffffff';  // white: green has too little contrast on sky blue
// [text, in, out] frames; words blur in over 5 frames and out over 4
const WORDS = [['One', 4, 104], ['place', 13, 104], ['to', 31, 104]];
const SWAPS = [['remember.', 36, 60], ['recall.', 64, 86], ['share.', 90, 104]];
const blurIn = (f, a, b) => { const kIn = clamp01((f - a) / 5), kOut = clamp01((f - b) / 4); return { op: kIn * (1 - kOut), blur: 10 * (1 - kIn) + 10 * kOut, y: 8 * (1 - ease.out(kIn)) - 6 * kOut }; };
LAYERS.oneplace = { w: 1000, h: 140, scale: 2, frames: 111, html: (f) => {
  const fixed = WORDS.filter(([, a]) => f >= a).map(([t, a, b]) => { const s = blurIn(f, a, b); return `<span style="display:inline-block;opacity:${s.op};filter:blur(${s.blur}px);transform:translateY(${s.y}px);margin-right:.26em">${t}</span>`; }).join('');
  const sw = SWAPS.find(([, a, b]) => f >= a && f < b + 4);
  const word = sw ? (() => { const s = blurIn(f, sw[1], sw[2]); return `<span style="display:inline-block;color:${WORD_C};font-weight:600;opacity:${s.op};filter:blur(${s.blur}px);transform:translateY(${s.y}px)">${sw[0]}</span>`; })() : '';
  // the line is centred on the words that are fully in, like the reel's line that re-centres as it grows
  return `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:42px;font-weight:400;letter-spacing:-0.015em;color:#fff;text-shadow:0 1px 18px rgba(20,60,110,.25);white-space:nowrap">${fixed}${word}</div>`;
} };
LAYERS.endlogo = { w: 700, h: 360, scale: 2, frames: 54, html: (f) => {
  const draw = clamp01((f - 1) / 12), fill = clamp01((f - 11) / 6), nodes = clamp01((f - 8) / 6);
  const nL = Math.max(0, Math.min(7, Math.floor((f - 16) / 1.7)));
  const per = 4 * 70;  // rounded-square outline length, near enough
  return `<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px">
    <svg viewBox="-2 -2 28 28" width="112" height="112" style="overflow:visible">
      <rect x="0" y="0" width="24" height="24" rx="6" fill="rgba(255,255,255,${0.95 * fill})" stroke="#fff" stroke-width="1.1" style="stroke-dasharray:${per};stroke-dashoffset:${per * (1 - draw)}"/>
      <g stroke="${fill > 0.5 ? '#1a7a49' : '#fff'}" stroke-width="1.5" stroke-linecap="round" opacity="${0.55 * nodes}"><line x1="12.5" y1="12.5" x2="6.5" y2="7"/><line x1="12.5" y1="12.5" x2="18" y2="8.5"/><line x1="12.5" y1="12.5" x2="9" y2="18.5"/></g>
      <g fill="${fill > 0.5 ? '#1a7a49' : '#fff'}"><circle cx="6.5" cy="7" r="${1.6 * nodes}" opacity=".7"/><circle cx="18" cy="8.5" r="${1.3 * nodes}" opacity=".7"/><circle cx="9" cy="18.5" r="${1.8 * nodes}" opacity=".7"/><circle cx="12.5" cy="12.5" r="${2.9 * ease.back(nodes)}"/></g></svg>
    <div style="font-size:52px;font-weight:600;letter-spacing:-0.03em;color:#fff;height:62px;text-shadow:0 1px 18px rgba(20,60,110,.25)">${'Eunomia'.slice(0, nL)}</div></div>`;
} };
LAYERS.endcard = { w: 1920, h: 1080, scale: 1, html: () => `<div style="position:absolute;inset:0;background:#000;display:flex;flex-direction:column;align-items:center;justify-content:center">
  <img src="../../paperless-white.png" style="height:96px">
  <div style="margin-top:40px;font-size:34px;color:#ededef">developers@buildpaperless.com.au</div>
  <div style="margin-top:14px;font-size:23px;color:#80858e;font-family:var(--mono)">github.com/Cashara-io/eunomia</div></div>` };
window.PRELOAD = ['../../paperless-white.png'];
