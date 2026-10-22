// Scene B: source labels that type on, the glowing dot sprite, "remembered." and the ray flash.
const ICON = {
  mail: '<rect x="2.5" y="5" width="19" height="14" rx="1"/><path d="M2.5 5.5l9.5 7.5 9.5-7.5"/>',
  chat: '<path d="M3.5 5h17v11h-9l-5 4v-4h-3z"/><path d="M7.5 9.5h9M7.5 12.5h6"/>',
  cal: '<rect x="3" y="5" width="18" height="16" rx="1.5"/><path d="M3 10h18M8 3v4M16 3v4M7 14h2M11 14h2M15 14h2M7 17.5h2M11 17.5h2"/>',
  doc: '<path d="M6 3h8.5L19 7.5V21H6z"/><path d="M14 3v5h5M9 12.5h7M9 16h7"/>',
  code: '<rect x="2.5" y="4" width="19" height="16" rx="1.5"/><path d="M9.5 9.5L7 12l2.5 2.5M14.5 9.5L17 12l-2.5 2.5M12.8 8.5l-1.6 7"/>',
  term: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.2"/>',
};
// [icon, name, sub]
const SOURCES = {
  mail: ['mail', 'Re: deploy freeze', 'from Priya · 2 new'],
  chat: ['chat', '#auth-rollout', '12 new messages'],
  cal: ['cal', 'standup at 9:30', 'tomorrow'],
  doc: ['doc', 'Q3 plan.md', 'edited 2h ago'],
  code: ['code', 'auth.rs', '3 unresolved comments'],
  term: ['term', 'Claude Code', 'session 41 ended'],
};
const NAME_FRAMES = 16, SUB_FRAMES = 10;
for (const [id, [ic, name, sub]] of Object.entries(SOURCES)) {
  LAYERS['lab_' + id] = {
    w: 760, h: 120, scale: 4, frames: 1 + NAME_FRAMES + SUB_FRAMES + 3,
    html: (f) => {
      const k = Math.max(0, f - 1);
      const nN = Math.min(name.length, Math.ceil((k / NAME_FRAMES) * name.length));
      const nS = Math.max(0, Math.min(sub.length, Math.ceil(((k - NAME_FRAMES) / SUB_FRAMES) * sub.length)));
      return `<div style="position:absolute;left:0;top:0;width:760px;height:120px;display:flex;align-items:center;gap:16px">
        <svg viewBox="0 0 24 24" style="width:64px;height:64px;flex:none;fill:none;stroke:#e9ecf1;stroke-width:1.1;stroke-linecap:round;stroke-linejoin:round">${ICON[ic]}</svg>
        <div style="white-space:nowrap"><div style="font-size:30px;font-weight:400;letter-spacing:-0.01em;color:#f2f4f7;height:38px">${typed(name, nN, 2, '#ffffff')}</div>
        <div style="font-size:17px;color:#7d838d;height:22px;margin-top:2px">${typed(sub, nS, 0)}</div></div></div>`;
    },
  };
}
LAYERS.glowdot = { w: 400, h: 400, scale: 1, html: () => `<div style="position:absolute;inset:0;background:radial-gradient(circle, rgba(170,255,210,1) 0%, rgba(82,189,135,.85) 3%, rgba(63,168,115,.42) 12%, rgba(40,130,85,.12) 34%, rgba(30,110,70,0) 62%)"></div>` };
LAYERS.dotcore = { w: 40, h: 40, scale: 3, html: () => `<div style="position:absolute;inset:8px;border-radius:50%;background:#f4fff8"></div>` };
const REM = 'remembered.';
LAYERS.rem_w = { w: 480, h: 90, scale: 3, frames: REM.length + 2, html: (f) => `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:400;letter-spacing:-0.01em;color:#fff">${typed(REM, f - 1, 0)}</div>` };
LAYERS.rem_k = { w: 480, h: 90, scale: 3, html: () => `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:34px;font-weight:400;letter-spacing:-0.01em;color:#0b0c0e">${REM}</div>` };
// grey flash with dark star-shaped rays leaking between the dashes
LAYERS.rays = { w: 1920, h: 1080, scale: 1, html: () => `<div style="position:absolute;inset:-200px;background:repeating-conic-gradient(from -9deg at 50% 50%, #000 0deg 18deg, transparent 18deg 60deg);filter:blur(34px);
  -webkit-mask:radial-gradient(circle at 50% 50%, transparent 14%, #000 30%)"></div>` };
