# GSAP for films

Since 3.13 every GSAP plugin is free and on cdnjs. Load what the film uses, then register the plugins:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/SplitText.min.js"></script>
<!-- same folder: DrawSVGPlugin, MorphSVGPlugin, CustomEase, MotionPathPlugin -->
<script>gsap.registerPlugin(SplitText);</script>
```

## The master timeline

- One `gsap.timeline({ paused: true, defaults: { ease: 'power3.out' } })` holds the whole film.
- Place every tween at an absolute time: `tl.to(el, { ... }, 12.3)`. The storyboard and the code then share one set of numbers, and moving a scene means editing its times.
- Repeated moves become helpers that take `(tl, t)` and place their own tweens, such as `capIn(tl, '#cap2', 6.0)`.
- Finish with `tl.set({}, {}, DURATION)` so the timeline is exactly the film's length, then `tl.seek(0); draw();`.
- A plain state object (`const S = { value: 0, cam: 9 }`) is a valid tween target. Tween it like an element and read it in `draw()`. Counters, cameras, shader uniforms and particle bursts all work this way.

## Initial state, entrances, exits

- Hide everything that enters later with one `gsap.set([...], { autoAlpha: 0 })` before building. `autoAlpha` fades and toggles `visibility` together.
- Entrances use `fromTo`, which writes its from-state at build time. Exits use `to`.
- A later `fromTo` on a property an earlier tween already owns takes `immediateRender: false`. Without it, the later from-state is written at build time and frame 0 renders wrong.
- State changes (Draft, Sent, Accepted; a button's label) stack every variant in one grid cell (`display: grid` on the parent, `grid-area: 1 / 1` on each child) and crossfade between them.

## Moves that read on video

- **Mask reveal.** Parent `overflow: hidden`, child `yPercent: 110` to `0`, `power4.out`, about 1s. Exit with `yPercent: -110`, `power3.in`.
- **Per-line or per-word reveal.** Split after fonts load: `const s = SplitText.create(el, { type: 'lines', mask: 'lines' }); tl.from(s.lines, { yPercent: 110, stagger: 0.08 }, t);`. The `mask` option wraps each line in its own clip.
- **Line drawing.** `tl.fromTo(path, { drawSVG: '0%' }, { drawSVG: '100%' }, t)` with DrawSVGPlugin, or the dasharray method in [svg.md](svg.md).
- **Morph.** `tl.to('#a', { morphSVG: '#b' }, t)` with MorphSVGPlugin.
- **Counters.** Tween a number on `S`, format it in `draw()`. Put `font-variant-numeric: tabular-nums` on the number alone: some fonts (Inter) widen hyphens under it, which spreads out file names and codes.
- **Landing a number.** `fromTo(el, { scale: 1.12 }, { scale: 1, duration: 0.6, immediateRender: false }, hit)`.
- **Clicks.** A `yoyo: true, repeat: 1` scale dip of about 0.09s each way on the cursor (`transformOrigin` at its tip) and on the target, plus a `click` cue.
- **Staggers from the middle.** `stagger: { each: 0.014, from: 'center' }`.
- **Signature curves.** `CustomEase.create('snap', 'M0,0 C0.2,0 0.1,1 1,1')`, then `ease: 'snap'`.
- **Cyclic motion** (pulses, idle drift) is computed in `draw()` from time, `Math.sin(S.t * 2)`, with `S.t` tweened linearly from 0 to `DURATION`. A `repeat: -1` tween would make the timeline infinite.

## Cue times from eases

`gsap.parseEase(name)` returns the ease function. Sample it to find when a tween crosses a value, for example a tick each time a counter passes another 2.5 million:

```js
const ease = gsap.parseEase('power2.in');
for (let k = 1; k * step < to; k++)
  for (let i = 0; i <= 700; i++)
    if (from + (to - from) * ease(i / 700) >= k * step) { cue(at + (dur * i) / 700, 'tick', 0.3); break; }
```

## Gotchas

- `seek()` suppresses callbacks (SKILL.md, Determinism).
- ScrollTrigger and Observer have nothing to watch in a render.
- `getTotalLength()`, `offsetLeft` and SplitText need the element laid out: `visibility: hidden` is fine, `display: none` is not.
