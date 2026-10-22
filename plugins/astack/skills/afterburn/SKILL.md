---
name: afterburn
description: The detail pass that turns a motion preview into a finished motion graphics film in Blender. Takes any preview as input (an html-video film, a hyperframes render, any MP4, a reference video, a storyboard) and rebuilds every beat with camera moves, transforms, depth, bloom and grain. Use when making a motion graphics film, promo, reel or explainer, when a preview or animatic needs a full motion pass, or when animating a title, transition or scene for one.
category: video
---

# Afterburn: the detail pass

A film is made twice. The **preview** is fast and flat: an `html-video` film, a hyperframes render, any clip. It settles the story, the copy, the timing and the sound. **Afterburn** is the second pass. It keeps the preview's timing and words, and rebuilds every beat as real motion graphics: each beat transforms into the next, the camera always moves, and depth of field, motion blur, bloom and grain sit on every frame.

The preview is the spec. Afterburn changes how a beat moves, never when it happens or what it says. When the story itself is wrong, go back and fix the preview first.

A finished film is a set of **scenes**. Each scene is one Blender Python script that builds the shot from **tactics** (reusable moves in `toolkit/blender/tactics.py`), renders frames headless, and gets joined with grain and sound. Text and flat UI are drawn in HTML and placed into the 3D scene as image planes. Every tactic reads its easing and feel from a **style** and an **energy**.

The worked example is the Eunomia launch film: `examples/eunomia-connected/` (beat table, every shot script, every layer file, sound, voiceover mix).

## Intake

Every input becomes one **handoff** folder: `beats.json` (one row per beat), `cues.json` (the sound cue sheet), `stills/` (one frame per beat), `stills.png` (all of them tiled), and `layers/` or `frames/`.

| Input | What to do |
|---|---|
| An `html-video` film (`index.html`) | `node <skill>/scripts/intake.mjs <film>/index.html [--format 16x9]`. Gives exact beats from `__beats`, the cue sheet from `__cues`, and a transparent PNG at 3x for every element marked `data-layer`. |
| Any video: a hyperframes render, another skill's MP4, a reference film | `node <skill>/scripts/intake.mjs <clip.mp4>`. Gives a beat per hard cut, a still per beat, and every frame at 10 fps in `frames/`. Fill `on_screen` and `motion` by looking at the frames. Pull 30 fps across each transition when copying a reference's style. |
| A hyperframes project or anything else that renders | Render it to MP4 with its own tool first, then take the video row. |
| A brief or a storyboard, no picture yet | Make the preview first with `html-video`. It is minutes of work and settles timing before any Blender time is spent. |

Run intake from a folder that has Playwright (or set `PW_FROM` to its `package.json`). It writes next to the input unless given `--out`.

Done when every row in `beats.json` has its time, what is on screen, and its motion, and you have looked at `stills.png`.

## Steps

1. **Intake**, above. Get the length, format and whether there is a voiceover from the preview or the owner.
2. **Style and energy.** Fill `style` (`techy`, `airy`, `paper`, `nature`, `glossy`) and `energy` (`big`, `smooth`) on every row, from [reference/styles.md](reference/styles.md). Scenes may differ: the example goes techy, then glossy, airy, paper and nature. Done when every row names both.
3. **Detail pass on paper.** For every row, read its preview `motion` and write the upgrade in `tactic`: the move from [reference/tactics.md](reference/tactics.md) that performs it. Then write `exit`: the tactic that carries this beat into the next. A preview fade or slide becomes a transform (a whip, a dive, a scatter, a swap). A preview with no camera gets a push. Done when every row has a named tactic and a named exit, and every exit is a transform.
4. **Set up the film folder.** Copy `toolkit/` into the project (for example `video/<film>/`), with the handoff beside it. Install Playwright once in a scratch folder (`npm i -D playwright && npx playwright install chromium`) and point `PW_FROM` at its `package.json`. Generate art and footage now: stills and posters with Codex `gpt-image-2` (the `headless-agent-cli` skill), video with Seedance or the full ElevenLabs connector (the `ai-video-generation` skill). Paint growth art and sprite sheets on plain white, then run `tools/grow_prep.py` and `tools/sprites_prep.py`.
5. **Layers.** Use the handoff's `layers/` first: it is the preview's own type and UI, already transparent. Write `layers/scenes/<scene>.js` from `_template.js` only for what the preview lacks, such as frame sequences (typing, bouncy letters, blur builds) and stacked states, then export with `node layers/export.mjs <scene>`. Look at every layer on a contrasting backdrop before using it. Done when every layer a scene needs exists and reads correctly.
6. **Build each scene.** Start a script from the nearest example shot: `reset(frames)`, `apply_style(style, energy)`, then tactics in beat order, camera last. Beat times come from `beats.json` (seconds times 30 is the frame). Render stills at a frame inside every beat (`Blender -b --factory-startup -P shot.py -- 12,40,77`), tile them, and put them beside the preview's `stills.png`. Done when every still lands the same words at the same moment as its preview still, does it with the row's tactic, and the pitfalls list in [reference/pitfalls.md](reference/pitfalls.md) is clean.
7. **Render.** One full scene at a time, in the background, under `nice -n 19` (the owner keeps fans quiet). About 0.3 to 0.8 s per frame.
8. **Sound.** Start from the handoff's `cues.json` and run `tools/soundtrack.mjs`. Sound names follow `tools/synth.mjs`; rename any the preview kit had that this one lacks (`whoosh`, `riser`, `hit`, `scan`), or drop them. The owner's mix: very quiet pad, no drums, subtle ticks; about -19 LUFS, -21 under a voiceover. Typing clicks are off unless asked.
9. **Assemble and check.** `tools/assemble.sh <dir> "<scene order>" <soundtrack> <out.mp4> <grain>`. Cut a contact sheet at 3 fps from the encoded MP4 and measure loudness. Done when the sheet shows every beat in order with nothing early, late, black or broken, the length matches the preview's within a frame, and loudness is within 1 LU of target.
10. **Voiceover**, when asked. Hand the script to a subagent that pulls frames from the cut and writes timed lines (the `eunomia-promo-video` skill has the house narration rules). Play free voice previews and let the owner pick (the `tts-voice-matching` skill) before any paid take. Voice the whole script in one take, find line spans with `silencedetect`, and place them with `tools/mix_vo.py`.

## Rules that save hours

- Every image plane needs its own depth: `plane()` nudges each new one. Re-seating an object by hand must keep that nudge.
- Change things at whole frames with `visible()`, never with a scale jump from 0, and cut the camera with `cut()`: anything that changes inside one frame smears into a blur.
- Focus follows the camera: move it with `cam_at()` or the camera tactics, which key focus too.
- Read a value before you key it (`y0 = ob.location.y`, then key `y0 - d` and `y0`).
- Full-frame overlays and end cards go on `screen_plate()`, held in front of the lens.
- Run `toolkit/blender/tactics_check.py` after editing `lib.py` or `tactics.py`; it exercises every tactic.
