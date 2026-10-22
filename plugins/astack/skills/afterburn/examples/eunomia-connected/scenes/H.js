// Scene H: the things Eunomia remembers, as labels on paper that a tree grows to meet.
// Label canvas 300x90: the dot centre sits at (16, 30), so Blender places the plane centre at tip + (134, 15).
const ENTITIES = [
  ['Ada Lovelace', 18, 1], ['Priya Shah', 11, 1], ['Sam Okafor', 7, 1], ['acme-api', 27, 1], ['auth.rs', 9, 1],
  ['billing', 13, -1], ['services/api', 8, 1], ['schema.sql', 10, 1], ['PKCE', 6, 1], ['Deploy freeze', 4, 1],
  ['Self-host first', 5, 1], ['Staging first', 3, 1], ['Feature flags', 12, 1], ['Claude Code', 41, 1], ['Codex', 33, 1],
  ['Cursor', 19, 1], ['Acme', 22, 1], ['Sydney', 3, -1], ['Q3 plan', 5, 1], ['Runbook', 8, -1],
];
window.ENTITIES = ENTITIES;
const arrow = (d) => d > 0 ? '<span style="color:#22a352">&#8593;</span>' : '<span style="color:#d84a3a">&#8595;</span>';
ENTITIES.forEach(([name, n, d], i) => {
  LAYERS['ent' + String(i).padStart(2, '0')] = { w: 300, h: 90, scale: 3, html: () => `<div style="position:absolute;inset:0">
    <div style="position:absolute;left:8px;top:22px;width:16px;height:16px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffc54a,#f29a12);box-shadow:0 1px 2px rgba(80,40,0,.35)"></div>
    <div style="position:absolute;left:32px;top:16px;font-size:23px;font-weight:500;letter-spacing:-0.01em;color:#1d1812;white-space:nowrap">${name}</div>
    <div style="position:absolute;left:34px;top:50px;display:inline-flex;gap:4px;align-items:center;padding:1px 8px;border-radius:7px;background:rgba(60,45,20,.06);border:1px solid rgba(60,45,20,.12);font-size:14px;font-weight:500;color:#3a3226">${n} ${arrow(d)}</div></div>` };
});
[['12', 1], ['22', 1], ['3', -1], ['48', 1], ['342', 1], ['7', 1]].forEach(([n, d], i) => {
  LAYERS['badge' + i] = { w: 120, h: 60, scale: 3, html: () => `<div style="position:absolute;inset:8px 10px;display:flex;align-items:center;justify-content:center;gap:5px;border-radius:12px;background:rgba(255,250,240,.7);border:1px solid rgba(60,45,20,.14);box-shadow:0 2px 6px rgba(60,45,20,.08);font-size:24px;font-weight:500;color:#2c251b">${n} ${arrow(d)}</div>` };
});
['#bfe6c2', '#f7c6d0', '#f6e69a', '#c9dcf5', '#f5c99a', '#d7ccf3', '#bfe6c2', '#f6e69a'].forEach((c, i) => {
  LAYERS['chip' + i] = { w: 140, h: 70, scale: 1, html: () => `<div style="position:absolute;inset:14px;border-radius:12px;background:${c}"></div>` };
});
LAYERS.trunk = { w: 420, h: 70, scale: 3, html: () => `<div style="position:absolute;inset:0;display:flex;align-items:center;gap:10px;padding:0 14px;background:repeating-linear-gradient(90deg, rgba(20,12,6,.88) 0 3px, rgba(20,12,6,0) 3px 7px, rgba(20,12,6,.88) 7px 8px, rgba(20,12,6,0) 8px 12px)">
  <div style="padding:6px 12px;background:#1a110a;font-family:Anton;font-size:30px;letter-spacing:.06em;color:#f3e3c4">SHARED MEMORY</div></div>` };
LAYERS.dotglow = { w: 120, h: 120, scale: 2, html: () => `<div style="position:absolute;inset:0;background:radial-gradient(circle, rgba(255,236,120,1) 0%, rgba(255,210,60,.75) 18%, rgba(255,200,40,0) 62%)"></div>` };
LAYERS.navy = { w: 1920, h: 1080, scale: 1, html: () => `<div style="position:absolute;inset:0;background:#0f1a2c"></div>` + ENTITIES.slice(0, 12).map(([n], i) => `<div style="position:absolute;left:${(i * 337) % 1700 + 90}px;top:${(i * 211) % 900 + 80}px;font-size:${12 + (i % 3) * 4}px;color:rgba(120,160,220,${0.25 + (i % 4) * 0.1})">${n}</div>`).join('') };
