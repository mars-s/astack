# Canvas 2D in films

## Setup

```js
const DPR = RENDER ? 1 : Math.min(2, devicePixelRatio || 1);
canvas.width = W * DPR; canvas.height = H * DPR;
Object.assign(canvas.style, { width: W + 'px', height: H + 'px' });

function drawCanvas() {
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  ctx.clearRect(0, 0, W, H);
  // paint everything from state S; nothing carries over from the last frame
}
```

Call it from `draw()`. Set `ctx.font` on every draw, after fonts have loaded.

## Camera

Zoom about a point:

```js
ctx.save();
ctx.beginPath(); ctx.rect(0, clipY, W, H - clipY); ctx.clip();  // keeps a headline on clean ground while zoomed in
ctx.translate(cx, cy); ctx.scale(S.cam, S.cam); ctx.translate(-cx, -cy);
// draw the world in its own coordinates
ctx.restore();
```

Tweening `S.cam` from 9 to 1 pulls back from one item to the whole set. A DOM element can hand off into the canvas by shrinking towards the camera's centre while the canvas fades in underneath it.

## Grids and waffle charts

One square per unit makes a large number tangible. Keep it honest: one square is one stated unit, and the film says the unit on screen.

1. At load, give each cell its position and an order key: distance from the centre, weighted per axis to shape the wave (`hypot(dx * wx, dy * wy)`), times seeded jitter (`1 + 0.45 * rnd()`). Sort by key and store each cell's rank.
2. Each frame, `front = S.value / unit`. A cell is lit when `rank < front`, with its scale easing in over the first unit.
3. Colour by age (`front - rank`): just-lit cells near white, settling to the brand colour over about 30 cells, so the wave front glows.

Re-shape the grid per format (50×20 wide, 25×40 tall) instead of scaling one shape down.

## Particles

At load, give each particle a seeded velocity, size and life. With burst progress `p` tweened linearly from 0 to 1 over the burst:

```js
const t = S.burst * LENGTH;
for (const q of SPARKS) {
  const a = 1 - t / q.life;
  if (a <= 0) continue;
  ctx.globalAlpha = a;
  ctx.fillRect(ox + q.vx * t - q.size / 2, oy + q.vy * t + 0.5 * G * t * t - q.size / 2, q.size, q.size);
}
ctx.globalAlpha = 1;
```

## Pulses and rings

A ring of radius `R = progress * Rmax` brightens what it passes: `bump = exp(-(((d - R) / width) ** 2)) * (1 - progress)`. Add `bump` to scale and mix towards a light colour.

## Colour

Keep the palette as RGB arrays and mix per element: `a.map((v, i) => Math.round(v + (b[i] - v) * t))`. Cache CSS custom properties in variables once; `getComputedStyle` inside a draw loop is slow.

## Cost

Thousands of `fillRect` or `roundRect` calls per frame are fine. `shadowBlur` and `ctx.filter` are slow: fake a glow with a second, larger, translucent shape.
