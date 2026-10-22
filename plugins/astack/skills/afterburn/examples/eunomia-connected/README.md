# Eunomia launch film (worked example)

The first film built this way: 35 s, 16:9, seven Blender scenes (A, B, D, E, G, H, I) plus HTML layers, a pad
soundtrack and an ElevenLabs voiceover. Read it to see tactics in context; `reel-breakdown.md` is the reference beat
table it was built from.

- `blender/shot_*.py` are the scene scripts. They predate `tactics.py` and inline the same moves (the tactics were
  lifted from them), so names map one to one: shot_A is `swap_layers` + `flash` + `glyph_orbit` + `depth_cloud` +
  `glitch_burst`; shot_B is `wave_line` to `ring_tunnel`; shot_D `tilt_in` + `pixel_sweep` + `dive`; shot_E
  `card_burst` + `ripple_bg`; shot_G `alarm_grade` + `voxel_shape` + `invert_frames`; shot_H `scatter_settle` +
  `grow_reveal` + `sprite_pop` + `drift`; shot_I `wind` + blur-build text + end card.
- `scenes/*.js` are the matching layer files (text, UI, posters, labels, typing sequences).
- `audio.mjs` is the cue sheet, `mix_vo.py` the voiceover placement, `assemble.sh` the join.
- Paths inside point at the original project (`video/eunomia-connected/v2/` in the Eunomia repo). Copy a shot into
  a new film folder next to `toolkit/blender/lib.py` and change its layer paths before running it.
