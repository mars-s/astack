// Scene D: the logo building on construction lines and flying apart, the heading, and the recall bar typing.
const MARK = (tile = '#3fa873', fg = '#04140b') => `<svg viewBox="0 0 24 24" width="100%" height="100%"><rect width="24" height="24" rx="6" fill="${tile}"/>
  <g stroke="${fg}" stroke-width="1.5" stroke-linecap="round" opacity=".55"><line x1="12.5" y1="12.5" x2="6.5" y2="7"/><line x1="12.5" y1="12.5" x2="18" y2="8.5"/><line x1="12.5" y1="12.5" x2="9" y2="18.5"/></g>
  <g fill="${fg}"><circle cx="6.5" cy="7" r="1.6" opacity=".6"/><circle cx="18" cy="8.5" r="1.3" opacity=".6"/><circle cx="9" cy="18.5" r="1.8" opacity=".6"/><circle cx="12.5" cy="12.5" r="2.9"/></g></svg>`;
window.MARK = MARK;
const WORD = 'Eunomia';
// layout of the lockup inside a 1200x420 canvas (css px)
const LK = { w: 1200, h: 420, mark: 84, gap: 24, size: 78 };
LAYERS.logo_build = {
  w: LK.w, h: LK.h, scale: 2, frames: 42,
  html: (f) => {
    const k = (a, b) => clamp01((f - a) / (b - a));
    const lines = k(1, 7), markIn = ease.back(k(4, 10)), track = ease.inOut(k(35, 42));
    const nLetters = Math.min(WORD.length, Math.floor((f - 7) / 1.6));
    const guide = 0.9 - 0.6 * k(18, 30);
    const ls = -0.035 + 0.75 * track, blur = 9 * track, op = 1 - track;
    const letters = [...WORD].map((ch, i) => {
      const on = i < nLetters, fresh = on && i >= nLetters - 1 && f < 22;
      return `<span style="position:relative;display:inline-block;opacity:${on ? 1 : 0}">${ch}${fresh ? `<span style="position:absolute;inset:6px -2px 2px -2px;border:1px solid #9fb0c2"></span>` : ''}</span>`;
    }).join('');
    const dash = (len) => `stroke-dasharray:${len};stroke-dashoffset:${len * (1 - lines)}`;
    return `<div style="position:absolute;inset:0">
      <svg width="${LK.w}" height="${LK.h}" style="position:absolute;inset:0;opacity:${guide * op};fill:none;stroke:#c3cdd8;stroke-width:1">
        <line x1="40" y1="168" x2="1160" y2="168" style="${dash(1120)}"/><line x1="1160" y1="252" x2="40" y2="252" style="${dash(1120)}"/>
        <line x1="40" y1="210" x2="1160" y2="210" style="${dash(1120)};opacity:.6"/>
        <line x1="395" y1="40" x2="395" y2="380" style="${dash(340)}"/><line x1="479" y1="380" x2="479" y2="40" style="${dash(340)}"/>
        <line x1="503" y1="40" x2="503" y2="380" style="${dash(340)}"/><line x1="805" y1="380" x2="805" y2="40" style="${dash(340)}"/>
        <circle cx="437" cy="210" r="62" style="${dash(390)}"/><circle cx="439" cy="212" r="18" style="${dash(114)}"/>
        <rect x="395" y="168" width="84" height="84" rx="21" style="${dash(340)};opacity:.7"/>
      </svg>
      <div style="position:absolute;left:0;right:0;top:0;bottom:0;display:flex;align-items:center;justify-content:center;gap:${LK.gap}px;filter:blur(${blur}px);opacity:${op}">
        <div style="width:${LK.mark}px;height:${LK.mark}px;transform:scale(${0.82 + 0.18 * markIn});opacity:${clamp01(markIn * 1.4)}">${MARK()}</div>
        <div style="font-size:${LK.size}px;font-weight:600;letter-spacing:${ls}em;color:#0f1114;line-height:1;width:${302 + 900 * track}px;white-space:nowrap">${letters}</div>
      </div></div>`;
  },
};
LAYERS.heading = { w: 1100, h: 120, scale: 3, html: () => `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:66px;font-weight:500;letter-spacing:-0.025em;color:#152230">What did we decide?</div>` };
const Q = 'Why did we pick PKCE for sign-in?';
const T0 = 2, TN = 26;
LAYERS.bar = {
  w: 1040, h: 110, scale: 4, frames: 34,
  html: (f) => {
    const n = clamp01((f - T0) / (TN - T0)) * Q.length;
    const caret = f >= T0 && (f <= TN + 1 || Math.floor(f / 8) % 2 === 0);
    return `<div style="position:absolute;left:6px;right:6px;top:10px;height:88px;border-radius:44px;background:rgba(255,255,255,.88);
        box-shadow:0 14px 36px rgba(20,60,100,.14), inset 0 0 0 1px rgba(255,255,255,.95);display:flex;align-items:center;gap:20px;padding:0 18px 0 32px">
      <div style="font-size:34px;font-weight:300;color:#6b7682;width:22px">+</div>
      <div style="flex:1;font-size:23px;color:#2b3540;white-space:nowrap;overflow:hidden">${n < 0.5 ? '<span style="color:#9aa4ae">Ask your team&#39;s memory</span>' : typed(Q, n, 6, '#2b9a62')}${caret ? '<span style="display:inline-block;width:2px;height:28px;background:#2b9a62;vertical-align:-6px;margin-left:2px"></span>' : ''}</div>
      <div style="display:flex">${[['CC', '#f0815e'], ['CX', '#4fc1c7'], ['CU', '#b48cf0']].map(([t, c], i) => `<div style="width:34px;height:34px;border-radius:50%;background:${c};border:2.5px solid #fff;margin-left:${i ? -9 : 0}px;display:grid;place-items:center;font-size:11px;font-weight:700;color:#0b0c0e">${t}</div>`).join('')}</div>
      <div style="font-size:18px;color:#6b7682;display:flex;align-items:center;gap:6px">All vaults <svg width="14" height="14" viewBox="0 0 24 24" style="fill:none;stroke:#6b7682;stroke-width:2.4"><path d="M6 9l6 6 6-6"/></svg></div>
      <div style="width:58px;height:58px;border-radius:50%;background:radial-gradient(circle at 35% 30%, #63d69a, #2b9a62 70%);display:grid;place-items:center;box-shadow:0 6px 16px rgba(43,154,98,.4)">
        <svg width="28" height="28" viewBox="0 0 24 24" style="fill:none;stroke:#fff;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round"><path d="M12 19V5M5 12l7-7 7 7"/></svg></div>
    </div>`;
  },
};
