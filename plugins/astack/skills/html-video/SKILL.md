---
name: html-video
description: Video made in code and rendered to MP4, and the fast preview stage of a motion film. Build a film as an HTML page animated with GSAP, CSS, SVG, Canvas or WebGL, capture it frame by frame with a synthesised or licensed soundtrack, at any aspect ratio. Use for launch videos, product demos, animated stats and social clips, to preview a film before the afterburn detail pass, or to cut an existing film to another aspect ratio.
---

# HTML video

A **film** is one HTML page that can draw any moment on demand. Every motion sits on one paused GSAP timeline. `scripts/render.mjs` seeks it frame by frame in headless Chromium, pipes the screenshots to ffmpeg, mixes a soundtrack from the film's sound cues, then proves the result: a contact sheet cut from the encoded MP4, and its loudness. One page renders every aspect ratio.

A film made here ships as is, or serves as the **preview** for the `afterburn` skill: a Blender detail pass that keeps this film's timing, copy, layers and cues and rebuilds every beat as full motion graphics. The preview is where story and timing get settled, because a re-cut here costs a minute and a re-cut in Blender costs hours.

This skill owns the machinery and the craft. Story, pacing, look and sound belong to the user and to you, decided film by film: bring options, ask, and let the brand drive colour and type (load the project's design-system skill when it has one).

## The film contract

`render.mjs` drives the page through these globals. Set them all before `__ready` resolves.

| Global | Meaning |
|---|---|
| `__ready` | Promise. Resolves once fonts are loaded, images decoded and the timeline built |
| `__seek(t)` | Draws the frame at `t` seconds, synchronously |
| `__duration` | Length in seconds |
| `__format`, `__formats` | The format this load is in (from `?format=`), and every format the film supports |
| `__size` | `{ w, h }` of the stage in this format |
| `__cues` | `[{ t, name, gain, len? }]` sound events; names are the `SOUNDS` in `scaffold/synth.mjs` |
| `__beats` | `[{ t, name, copy, motion }]` the storyboard, one row per beat, from `beat()` calls. `afterburn` reads it as its beat table |
| `__audio` | Optional `{ music: 'synth' \| false \| 'track.mp3', musicGain, drive }` |

`?render` in the URL means the renderer is driving: no autoplay, canvas at DPR 1, no fit-to-window.

Mark each piece of flat type or UI that a detail pass would lift into 3D with `data-layer="<name>"` and `data-at="<seconds>"`, a moment when it is fully on screen. `afterburn` exports each one alone as a transparent PNG.

## Workflow

1. **Brief.** Agree with the user on the one message, the claim or number it lands on, audience, platforms and formats, length, and sound (synth bed or a licensed track). Done when you can say the film in one sentence and every fact on screen has a named source: real figures come from the user or their data, demo data is invented. If the user wants topic ideas first, table them as Topic | Hook | What we show | Trust point | Why this one.
2. **Storyboard.** Write the scene list: start time, on-screen copy, the motion, and the sound cue for each beat. Done when the times add up to the duration and the copy is final, because copy changes force re-timing.
3. **Scaffold.** Copy `scaffold/index.html` into the film's folder (for example `video/<film>/index.html`) with its assets beside it, and swap the placeholder tokens for the brand's. Copy `scaffold/synth.mjs` there too only when the sound needs its own design; otherwise the renderer uses the kit.
4. **Build.** Name the data shapes first (scene table, rows, the `LAYOUT` table), then write the timeline at absolute times, keeping every frame a pure function of `t` (see Determinism). Place each `cue()` beside the tween it belongs to, and a `beat()` at the start of each storyboard row.
5. **Stills.** Run `node <skill>/scripts/render.mjs <film>/index.html --all --stills 1.5,4,9.2` with a time inside every scene, and read each `out/<film>-<format>-stills.png`. Done when you have looked at every scene's key frame in every format, and nothing clips, collides or reads too small.
6. **Render.** Run `node <skill>/scripts/render.mjs <film>/index.html --all`. Done when every `out/<film>-<format>-sheet.png` (cut from the encoded MP4, not the page) looks right and the printed loudness is within 1 LU of the target.
7. **Deliver.** Send the MP4s and a poster frame per format (`ffmpeg -ss <t> -i film.mp4 -frames:v 1 poster.png`). Say what is unverified: figures taken on trust, music rights, features behind a flag.
8. **Afterburn**, when the film needs the full motion pass (camera moves, transforms between beats, depth, bloom, grain), or the owner calls the render flat. Get the owner's yes on this cut's story and timing first, then hand the film's `index.html` to the `afterburn` skill as its input. Done when every beat in `__beats` has its copy and motion filled in, and every flat element has `data-layer` and `data-at`.

Run the renderer from inside the project. It needs Playwright there (`npm i -D playwright && npx playwright install chromium`) and ffmpeg on the path. A 40 second film renders in about 40 seconds per format.

## Determinism

The renderer seeks to arbitrary times, so each frame depends on `t` alone.

- Every change is a tween on the master timeline, or plain state that a tween moves and `draw()` reads. `__seek` calls `draw()`, which writes text, Canvas and WebGL from that state.
- `tl.seek()` skips callbacks: `onStart`, `onComplete`, `onUpdate` and `.call()` stay silent in a render. Swap text by crossfading stacked elements, or set it in `draw()` from a tweened number.
- Randomness comes from a seeded generator, built once. Particles move by closed-form maths (`x0 + vx·t + ½·g·t²`), never by stepping.
- Every font weight is loaded (`document.fonts.load`) and every image decoded before `__ready` resolves.
- Sizes inside the stage are px. `vw`, `vh` and media queries measure the browser window, which the renderer resizes.
- GSAP owns all timing: the film carries no CSS `transition` or `animation`, `requestAnimationFrame`, timers or `Date.now()`.

## Formats

One timeline serves every format. The stage carries the class `f-<format>` for CSS overrides, a `LAYOUT` table holds the numbers motion needs, and `pos()` aims motion at elements instead of hard-coded coordinates. Sizes, safe zones and re-shaping: [reference/formats.md](reference/formats.md).

## Technique reference

Read the file for the layer in front of you:

- [reference/gsap.md](reference/gsap.md): the master timeline, entrances and exits, text reveals, counters, the free 3.13 plugins (SplitText, DrawSVG, MorphSVG, CustomEase), cue times from eases.
- [reference/svg.md](reference/svg.md): line drawing, diagrams built from data, clip and mask reveals, icons.
- [reference/canvas.md](reference/canvas.md): state-driven drawing, camera moves, grids and waffle charts, particles.
- [reference/webgl.md](reference/webgl.md): shader backgrounds, Three.js scenes, headless rendering cost.
- [reference/audio.md](reference/audio.md): cue lists, the synth kit, licensed tracks, loudness.
- [reference/formats.md](reference/formats.md): sizes, safe zones, layout tables.

[example/index.html](example/index.html) is a finished 43 second launch film built this way (Build Paperless estimating, 16:9 and 9:16): an SVG floor plan built from a rooms table, a scan reveal, counters, a cursor, a Canvas camera pull-back over a 1,000-square grid, and cue-driven sound. Read it to see the pieces working together; its look belongs to that brand.

## Before publishing

- Every figure and claim on screen checks out against its source.
- The feature shown is live for everyone, or the film says otherwise.
- Third-party logos and interfaces follow their brand rules: show a simple mock rather than a copy of their app.
- Loudness sits at −16 LUFS for social feeds or −14 for YouTube, true peak under −1 dBFS.
