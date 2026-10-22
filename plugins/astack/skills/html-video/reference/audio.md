# Sound for films

## Cues

Every sound is a cue placed beside the tween it belongs to: `cue(t, name, gain, len?)`. The film exposes them as `window.__cues`. `render.mjs` passes them to `soundtrack(cues, duration, options)` and muxes the WAV it returns. Re-time a scene and its sounds move with it.

## The kit

`scaffold/synth.mjs` is used unless the film's folder has its own `synth.mjs`.

| Sound | Use |
|---|---|
| `tick`, `tick-lo` | Light hits: an item landing, a counter passing a step. Alternate them in a run |
| `click` | A press |
| `pop` | A total or a toast landing |
| `whoosh` | A scene change; `len` sets its length (default 0.8s) |
| `thud` | Something heavy landing |
| `scan` | A sweep; `len` sets its length |
| `chime` | A success |
| `riser` | Builds until the next `hit` cue, or for `len` seconds |
| `hit` | The climax: pitched kick, sub boom, wide crash, chime |

The music bed runs at 120 bpm: a beat is 0.5s and a bar is 2s. Plucks play from the start, kick and hats from 3.5s, claps four bars later, and 16th notes for the four bars before the `hit`. The bed ducks for the half beat before the hit, sits in a minor key until it and a major key after, and plays a half-time kick in the outro before a 3s fade. Land the climax on a bar line (an even second) and put the `hit` cue there.

## A licensed track

Put the file next to the film and set `window.__audio = { music: 'track.mp3' }`. The kit decodes it with ffmpeg, cuts it to the film's length, fades the last 2s and mixes the cues on top. Time picture to the track: a beat lasts `60 / bpm` seconds; put scene changes on bar lines.

## Loudness

Aim for −16 LUFS integrated on social feeds and −14 on YouTube, with true peak under −1 dBFS. The renderer prints both for every MP4. Tune with `__audio.drive` (how hard the mix pushes into a tanh soft clip: the default 2.4 suits the synth, about 1 suits a mastered track) and with cue gains. Leave a one-pass ffmpeg `loudnorm` out: it rides the level up and down across the film.
