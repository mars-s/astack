# SVG in films

## Build from data

Generate geometry in JS (`document.createElementNS`) from a table: rooms, rows, nodes, steps. The same table feeds the numbers on screen, so labels and drawings always agree. The example film builds a floor plan from a rooms table and derives every area, wall length and total from it.

Keep coordinates in px. Font sizes go in CSS px (`font: 600 17px var(--font)`); a viewBox in tiny units with tiny font sizes renders text at the wrong size.

## Drawing lines

```js
const L = el.getTotalLength();
el.style.strokeDasharray = L;
el.style.strokeDashoffset = L;
tl.to(el, { strokeDashoffset: 0, duration: 0.5, ease: 'power1.inOut' }, t);
```

This works for `path`, `line`, `rect`, `circle` and `polyline`. Many short segments with a small stagger read as something being drawn by hand. DrawSVGPlugin does the same in one property ([gsap.md](gsap.md)).

## Reveals

- **Scan or wipe.** Put a second copy of the art (in its highlight colour) in a group clipped by a `<clipPath>` rect, and set the rect's width from state in `draw()`. A thin line plus a translucent band at the rect's edge sells it as a scan.
- **Things appearing as the scan passes.** Give each shape its own tween, timed from where the scan crosses it: `t = start + dur * (shape.cx - x0) / span`.
- **HTML wipes** (a logo, a card): tween `clipPath` from `'inset(0% 100% 0% 0%)'` to `'inset(0% 0% 0% 0%)'`.
- **Masks** (`<mask>` with a white shape) reveal through any shape you can tween.

## Layer order

Fills, then fixtures, strokes, highlight copies (clipped), labels, dimension lines, and the scan on top. Each layer is a `<g>`, so one selector tweens the whole layer.

## Shapes

- Arcs such as door swings and gauges: `M h L o A r r 0 0 sweep c`. Derive `sweep` from the turn between the two radii (`(a1 - a0 + 2π) % 2π < π ? 1 : 0`).
- Icons: inline the paths (Lucide, or the project's own set) with `stroke="currentColor"`, so CSS colours them.

## Cost

SVG filters (blur, drop shadow, turbulence) re-render every frame and slow capture. Use CSS `box-shadow` on HTML elements, or a pre-made image.
