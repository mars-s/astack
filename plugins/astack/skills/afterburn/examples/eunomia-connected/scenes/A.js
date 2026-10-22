// Scene A: "too many chats / agents / sessions", the glyphs, the code cloud and the glitch burst.
// Every line layer shares one 1400x160 canvas with the text centred, so Blender stacks them on one plane spot.
const LINE = { w: 1400, h: 160, scale: 3 };
const G = 'var(--green-text)';
const lineHtml = (word, { only, color, style = '', box } = {}) => {
  const vis = (part) => (only && only !== part ? 'color:transparent;' : '');
  const inner = `<span style="color:${color ?? G};${vis('tm')}">too${word === null ? '' : ' many'}</span>${word ? `&nbsp;<span style="color:${color ?? '#fff'};${vis('w')}">${word}</span>` : ''}`;
  const boxed = box ? `<span style="display:inline-block;padding:2px 14px;background:${box};transform:${box.skew ?? ''}">${inner}</span>` : inner;
  return `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:46px;font-weight:400;letter-spacing:-0.012em;white-space:nowrap;${style}">${boxed}</div>`;
};
Object.assign(LAYERS, {
  l_too: { ...LINE, html: () => lineHtml(null) },
  l_toomany: { ...LINE, html: () => lineHtml('') },
  fl_many: { ...LINE, html: () => `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:46px;letter-spacing:-0.012em"><span style="color:transparent">too </span><span style="color:${G}">many</span></div>` },
});
for (const w of ['chats', 'agents', 'sessions']) {
  LAYERS['l_' + w] = { ...LINE, html: () => lineHtml(w) };
  LAYERS['fl_' + w] = { ...LINE, html: () => lineHtml(w, { only: 'w' }) };
}
// glitch frames on the last line: each shows for one or two frames
const gl = (inner) => ({ ...LINE, html: () => `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:46px;letter-spacing:-0.012em;white-space:nowrap">${inner}</div>` });
Object.assign(LAYERS, {
  g_magenta: gl(`<span style="color:#ff2d8d">too many</span>&nbsp;<span style="color:#fff">sessions</span>`),
  g_cyan: gl(`<span style="background:#18c8e8;color:#c7ff3d;padding:0 10px">too many</span><span style="background:#18c8e8;color:#04140b;padding:0 10px 0 0">&nbsp;sessions</span>`),
  g_yellow: gl(`<span style="color:#ffd23f;font-style:italic;font-weight:500;letter-spacing:0.01em">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;sessions</span>`),
  g_pink: gl(`<span style="display:inline-block;background:#ff2d78;padding:2px 16px;transform:skewX(-14deg)"><span style="display:inline-block;transform:skewX(14deg)"><span style="color:#ffd0e2">too many</span>&nbsp;<span style="color:#fff">sessions</span></span></span>`),
  g_red: gl(`<span style="color:#ff3b3b">too many</span>&nbsp;<span style="color:#fff">sessions</span>`),
  g_green: gl(`<span style="color:${G};opacity:.35;filter:blur(1px)">too many</span>&nbsp;<span style="color:#9ff0c4">sessions</span>`),
});
// glyphs that orbit the title
const glyph = (ch, color = '#fff', size = 30) => ({ w: 60, h: 60, scale: 3, html: () => `<div style="position:absolute;inset:0;display:grid;place-items:center;font-family:var(--mono);font-size:${size}px;color:${color}">${ch}</div>` });
Object.assign(LAYERS, {
  gl_slash: glyph('/'), gl_lt: glyph('&lt;'), gl_gt: glyph('&gt;'), gl_star: glyph('*'), gl_dash: glyph('-'),
  gl_slash_g: glyph('/', '#52bd87'), gl_star_g: glyph('*', '#52bd87'), gl_brace: glyph('{'), gl_brace2: glyph('}'),
});
// code fragments for the cloud: what working with forgetful agents looks like
const SNIPS = [
  ['session.end()  // context lost', '#e8edf5'], ['memory = None', '#8fb3ff'], ['agent.forget(everything)', '#e8edf5'],
  ['retry(prompt, context="???")', '#7d93b8'], ['unread(47)', '#8fb3ff'], ['slack.thread("#auth-rollout")', '#e8edf5'],
  ['# TODO: remember this', '#7d93b8'], ['git log --since=yesterday', '#e8edf5'], ['ctx.window = 200_000', '#8fb3ff'],
  ['explain(project)  # again', '#e8edf5'], ['decision = "???"', '#7d93b8'], ['notes_final_v3.md', '#8fb3ff'],
  ['which_branch()', '#e8edf5'], ['{TABS++}', '#8fb3ff'], ['copy(); paste(); explain();', '#7d93b8'],
  ['who_decided(this)', '#e8edf5'], ['new_chat()', '#8fb3ff'], ['reload(history)  // 0 results', '#7d93b8'],
  ['inbox(99+)', '#e8edf5'], ['agents.map(a => a.ask(you))', '#7d93b8'], ['standup.notes = []', '#8fb3ff'],
  ['README.md  (outdated)', '#e8edf5'], ['context.reset()', '#8fb3ff'], ['why_did_we(...)', '#7d93b8'],
];
SNIPS.forEach(([t, c], i) => {
  LAYERS['s' + String(i).padStart(2, '0')] = { w: 640, h: 56, scale: 2, html: () => `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:24px;color:${c};white-space:nowrap">${t.replace(/</g, '&lt;')}</div>` };
});
// a soft round flare sprite
LAYERS.flare = { w: 200, h: 200, scale: 2, html: () => `<div style="position:absolute;inset:0;background:radial-gradient(circle, #fff 0%, rgba(255,255,255,.9) 6%, rgba(220,235,255,.35) 22%, rgba(200,220,255,0) 60%)"></div>` };
