# Styles and energy

`apply_style(style, energy, **overrides)` in `tactics.py` sets the world colour, bloom, motion blur and the easing every tactic uses. Override any key per scene: `apply_style('paper', 'smooth', accent='#d84a3a', shutter=0.3)`. The numbers live in `STYLES` and `ENERGY` at the top of `tactics.py`, the single source of truth; this page says when to use which.

## Styles

| Style | Looks like | Reach for it when | Pairs with |
|---|---|---|---|
| `techy` | Near-black room, thin white lines, glowing accent dots, mono code fragments, strong bloom, shallow focus | the problem, chaos, systems, data flowing | `glyph_orbit`, `depth_cloud`, `wave_line`, `fan_threads`, `glitch_burst` |
| `glossy` | Light grey studio, glossy 3D objects with sweeping colour, soft shadows | a hero object, the moment it clicks | `glossy_ring`, `ring_tunnel`, `voxel_shape` |
| `airy` | White to pale blue, product UI floating over a photo, clean type | the product in use, a question and an answer | `tilt_in`, `pixel_sweep`, `dive`, `card_burst`, `ripple_bg` |
| `paper` | Warm textured paper, painted illustration, small labels with dots and badges, warm grade | knowledge, structure, growth, a calmer explanation | `scatter_settle`, `grow_reveal`, `sprite_pop`, `drift`, `sway`, `rack_focus` |
| `nature` | Real footage or a photo of sky and plants, white type (key words bolder, never coloured), deep focus | the closing promise, the brand line | `wind`, word-by-word blur build, mark draw-on |

A dark editor over a forest (example scene G) is `techy` type over a `nature` background: set the world from one and the photo from the other.

## Energy

| | `big` | `smooth` |
|---|---|---|
| Moves | EXPO in-out: fast middles, hard stops | SINE in-out: even glides |
| Entrances | EXPO out | QUART out |
| Pops | BACK (overshoot) | SINE out (no overshoot) |
| Motion blur | full shutter | 0.6 of the shutter |
| Word flashes | strong bloom (peak 10) | soft (peak 4) |
| Glitch frames | on | off (`glitch_burst` does nothing) |
| Beat length | about 1.2 s | about 2 s |
| Between scenes | whips, hard cuts, dives, invert frames | pushes, rack focus, pixel sweeps, slow scatters |

## Picking for a film

- One message per film, one world per act. The example runs dark problem, glossy click, airy product, editor proof, paper structure, nature promise. Each world change is a transform (see the table at the end of tactics.md).
- A techy explainer: `techy` + `big` throughout, with `glossy` for the hero moment.
- A paper-drawn explainer: `paper` + `smooth` throughout. Paint every illustration on white so `grow_prep.py` can grow it, and drive beats with `scatter_settle`, `grow_reveal`, `sprite_pop` and `rack_focus`.
- A calm brand film: `nature` and `airy` with `smooth`. Use pushes and blur builds, no glitches.
- Big transitions in a smooth film: keep `smooth` for the scenes and spend `big` only on the one scene that turns the story.

## Brand

The style sets the room. The brand sets accent, type and logo: pass `accent=` and put brand fonts in the `<link>` of `layers/layers.html` (the one place fonts load). Eunomia's tokens are in the repo's `DESIGN.md` (felt green `#3fa873`, Geist).
