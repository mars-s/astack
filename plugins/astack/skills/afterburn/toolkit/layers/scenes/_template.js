// A scene's flat layers (text, UI, cards, labels) for Blender planes. Copy to scenes/<scene>.js, then:
//   PW_FROM=<dir with node_modules/playwright>/package.json node export.mjs <scene>
// Each layer: { w, h (css px), scale (pixel density, 2-4; use 4 for anything the camera dives into),
//   frames (omit for a still), html(f) }. Helpers from layers.html: typed(text, n, fresh, colour), ease.*, clamp01.
// Stacked states of one thing (word swaps, glitch states, flash copies) share one canvas size and layout,
// so Blender can stack them on one spot. A flash layer is the same layout with every other part transparent.
// Image paths are relative to layers.html; list them in window.PRELOAD so they decode before capture.
window.PRELOAD = [];
Object.assign(LAYERS, {
  title: { w: 1400, h: 160, scale: 3, html: () => `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:46px;color:#fff">Title</div>` },
  typing: { w: 900, h: 140, scale: 3, frames: 30, html: (f) => `<div style="position:absolute;inset:0;display:flex;align-items:center;font-size:40px;color:#fff">${typed('Typed letter by letter.', f - 1, 2, 'var(--green-text)')}</div>` },
});
