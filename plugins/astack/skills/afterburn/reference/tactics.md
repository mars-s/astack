# Tactics

Every move from the Eunomia film, as a function in `toolkit/blender/tactics.py` (or `lib.py` where marked). Positions are px on the 1920x1080 frame at rest; frames are scene frames at 30 fps. Easing and feel come from the active style and energy unless a tactic says otherwise. "Example" points at the shot in `examples/eunomia-connected/blender/` that shows it in context.

## Camera

| Tactic | What it looks like | Key params | Example |
|---|---|---|---|
| `push(cam, f0, f1, x, y, k0, k1)` | A slow push or pull on a point. Every shot needs one. | `k` is zoom (1 = full frame, 2 = twice as close) | all |
| `whip(cam, f0, f1, ...)` | A fast pan that smears everything with motion blur. Use it to exit a title and follow a line. | distance, frames | B |
| `cut(cam, frame, x, y, k)` | A hard cut to a new framing (close-up, wide), landed between frames so it never smears. | framing | B, G |
| `dive(cam, f0, f1, x, y, zoom, roll)` | Dives into a button or word with a slight roll. It hands off to a burst from that point. | zoom 3 to 4.5, roll -3 to -6 degrees | D |
| `rack_focus(cam, f0, peak, f1, depth)` | The whole frame blurs, then comes back. It sits between two states of one scene. | depth 0.5 to 0.7 | H |
| `lens(cam, fstop, frames)` | Depth of field at the style's f-stop, or keyed f-stops for cuts. | f-stop 1.1 (dreamy) to 5.6 (crisp) | G |
| `cam_at(cam, f, x, y, k, interp, ease)` (lib) | Any camera key. Focus follows automatically. | | all |

## Text and layers

| Tactic | What it looks like | Key params | Example |
|---|---|---|---|
| `swap_layers(paths, schedule)` | Stacked states take turns: word swaps, UI states, glitch states. | `[(index, on, off)]` | A |
| `flash(path, frame)` | A new word lands with a bloom pop. A bright copy in front dims back to normal. | peak (big 10, smooth 4), length | A |
| `glitch_burst(paths, frame)` | 1 to 2 frames per state: colour swap, highlight box, italic, skew. Only fires at `big` energy. | `frames_each` | A, E |
| `type_on(seq_dir, start, total, ...)` | Letters type in, the newest few in a highlight colour. The HTML sequence uses `typed()` in layers.html. | start frame | B, D |
| bouncy letters (HTML sequence) | Each letter pops up scaled from 0.55 with overshoot, starts blue, settles to ink. | see `recalled` in example `scenes/E.js` | E |
| letters fly apart (HTML sequence) | Letter spacing explodes while blurring out. Use it as a logo exit into the next heading. | see `logo_build` in `scenes/D.js` | D |
| word-by-word blur build (HTML sequence) | Words blur in one at a time; the key word swaps with a blur out and in. | see `oneplace` in `scenes/I.js` | I |
| logo on construction lines (HTML sequence) | Guide lines draw, the mark pops, letters appear with a box flash. | see `logo_build` | D |
| mark draw-on (HTML sequence) | The mark's outline strokes on, nodes pop, then it fills; the name types under it. | see `endlogo` in `scenes/I.js` | I |
| `tilt_in(ob, f0, f1, rot, dz)` | A heading swings in from a 3D tilt, out of focus near the lens, and lands sharp. | rot degrees, dz toward lens | D |
| `rise_in(ob, f0, f1, dy_px)` | A panel slides up from below the frame and settles. | dy | G |
| `float_drift(ob, f0, f1)` | A gentle 3D float and bob for panels in a wide. | tilt degrees, bob px | G |
| `screen_plate(path, d, frames)` | A full-frame overlay or end card held in front of the lens. | | H, I |

## Glows, glyphs, clouds

| Tactic | What it looks like | Key params | Example |
|---|---|---|---|
| `glow_dot(x, y, f_on)` | A glowing dot pops in. It is the origin of lines and threads. | colour, core and glow size | B |
| `glyph_orbit(paths, f_from, swirl=)` | Small glyphs pop in around a title, then swirl round it with motion blur. | radius, stagger, swirl (frames, degrees, scale) | A |
| `depth_cloud(paths, count, f_in, f_out)` | Fragments float on tilted planes through depth. Push the camera through it with depth of field. | z range, count, tilt, avoid box | A |
| `scatter_settle(items, f_go)` | Labels float at many depths while the camera trucks past, then fly to their final spots. | region, z range, stagger | H |

## Lines, threads, rings

| Tactic | What it looks like | Key params | Example |
|---|---|---|---|
| `wave_line(p0, p1, f0, f1)` | A line draws on with a travelling wobble packet. This is "text becomes a line". | amp, wavelength, sigma, travel | B |
| `fan_threads(origin, targets, f0, retract=)` | Curves grow out of one point in S shapes to each target, then pull back in. | stagger, width, decor strands | B |
| `tip_dots(points, f_on)` | End dots pop in at thread tips. | radius, stagger | B |
| `dots_to_ring(dots, starts, center, r, f0)` | Loose dots fly into a ring, drift-spin, then whip fast. | arrive frames, whip_at | B |
| `dashes_close(center, r, n, f0, f1, spin, f_hide)` | The smeared dots become arcs that grow until the ring closes. | thickness, n | B |
| `glossy_ring(center, r, tube, stops, f_on)` | A glossy 3D torus with a colour band sweeping round it, a key and rim light, and a soft shadow. | colour stops, sweep, backdrop | B |
| `ring_tunnel(tor, mat, center, f0)` | The ring tilts in 3D and echoes outward past the frame while the camera pushes in. | echoes, tilt, end scale | B |

## Backgrounds and grades

| Tactic | What it looks like | Key params | Example |
|---|---|---|---|
| `photo_plane(name, path, sweep=)` (lib) | A photo or movie filling a rect with cover-crop. Accepts .mp4 footage too. | z, size, tint, cells | D, G, H, I |
| `pixel_sweep(photo, f0, f1)` | The scene resolves from white, through a band of tinted pixels, to the sharp photo. | photo_plane `tint`, `cells` | D |
| `ripple_bg(f_on, f_off)` | Soft concentric bands pulse outward with a white centre (water ripple behind a burst). | freq, colours, speed | E |
| `alarm_grade(photo, f0, f1)` | The background flushes a colour and flickers while an error is on screen. | colour, level, flicker pattern | G |
| `warm_grade(photo, f0, f1)` | The scene slowly warms (a mood shift after a rack focus). | colour, level | H |
| `wind(photo)` | A still photo breathes: a noise wobble in the lower part only (flowers, grass, water). | amp, scale, band | I |
| `invert_frames(frames)` | Colour-negative glitch frames hand over between worlds. | frames | G |
| world colour keys | The room flashes grey with dark rays through the gaps, then goes light. | see shot_B `wbg` and `rays` | B |

## Bursts, growth, particles, 3D

| Tactic | What it looks like | Key params | Example |
|---|---|---|---|
| `card_burst(paths, f0)` | Cards fire one after another from a hub, swing clockwise into a pinwheel, turn, then burst past the frame. | radius, interval, swing, burst scales | E |
| `grow_reveal(image, growmap, rect, f0, f1)` | An illustration grows outward from a seed (tree, roots, river, vine, crack, ink). Returns `frame_for(g)` to time things to the growth front. | rect, threshold range, grade | H |
| `sprite_pop(sprites, points, frames)` | Blossoms, leaves, sparks or stickers pop in with overshoot. | sizes | H |
| `drift(sprites, count, f_from, f_to)` | Falling leaves, petals, dust or confetti drift across with a slow spin. | region, fall, tint | H |
| `sway(pivot, keys)` | An empty that rocks gently; parent a whole illustration to it. | degrees per key | H |
| `voxel_shape(center, f_on)` | A cube of small glowing voxels with a colour gradient, popping in and turning. | n, cell, stops, spin | G |

## Transform, not fade

How the example hands each world to the next. Reach for a transform before any crossfade.

| From | Into | How |
|---|---|---|
| title | line | `whip` off the title, `glow_dot` + `wave_line` start where the last word ended |
| threads | ring | `fan_threads(retract=)` while the end dots run `dots_to_ring`, then `dashes_close` |
| ring | white world | `ring_tunnel` + world colour to light; the black centre greys to white |
| logo | heading | letters fly apart (HTML), `tilt_in` heading, `pixel_sweep` background |
| button | burst | `dive` into the button, then `card_burst` from the same screen point (use the last frame as a plate) |
| burst | word | wheel scales past the frame to reveal sky; bouncy letters type |
| word | panel | 1 to 2 frame glitch slices, then a frosted panel that darkens into the next UI |
| dark UI | paper | `invert_frames` + one navy frame with faint labels |
| scatter | structure | `scatter_settle` lands labels on tips, then `grow_reveal` grows to meet them |
| any | end card | `screen_plate` fade over the last scene |
