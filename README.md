# astack

Avi's personal skills for Claude Code. Like [pstack](https://github.com/michael-denyer/pstack-claude) (poteto's stack, ported from [Cursor's plugins](https://github.com/cursor/plugins/tree/main/pstack)), it is one person's way of working, packaged so any agent can follow it.

## Skills

| Skill | What it does | Use it when |
|---|---|---|
| `astack:html-video` | Builds a film as one HTML page on a GSAP timeline and renders it frame by frame to MP4, with sound, in any aspect ratio. It ships finished clips, or a fast preview for afterburn. | Launch videos, product demos, animated stats, social clips, or a first cut of a bigger film |
| `astack:slow-shutter` | Creates grainy editorial photographs with directional motion blur, or applies the look to an uploaded image. | Wonderful.ai-inspired photos, a readable subject among blurred people, panning shots, or abstract photographic backgrounds |
| `astack:afterburn` | Takes any flat preview and rebuilds every beat as finished motion graphics in Blender. It keeps the preview's timing and words, and changes how each beat moves. | You have a draft, an animatic or a reference video, and it needs to look like a motion design studio made it |

## Install

```bash
claude plugin marketplace add mars-s/astack
```

```bash
claude plugin install astack@astack
```

Then ask Claude for a video or an editorial photo, or call a skill by name, such as `/astack:afterburn` or `/astack:slow-shutter`.

## Making a photograph

`slow-shutter` makes original images using the photographic principles seen on [Wonderful.ai](https://www.wonderful.ai/?scLang=en): directional blur, fine film grain, soft highlights and restrained colour. It accepts a scene description, a photo to edit, or a photo plus separate style references.

```text
/astack:slow-shutter Make a wide photo of a cyclist at dusk.
Track the cyclist, with strong sideways blur in the street behind them.
```

```text
/astack:slow-shutter Apply this look to my attached photo.
Keep the person recognisable and blur the passing people strongly.
```

```text
/astack:slow-shutter Make a heavily blurred photographic background.
Muted blue and green, a small warm accent, no clear subject, no text.
```

| Treatment | Result |
|---|---|
| Selective motion | A readable subject with blurred movement around it. The default. |
| Panning | A tracked subject with streaks through the background. |
| Abstract sweep | Broad directional colour fields with grain and hints of a real place. |
| Rotational motion | Blades or wheels blur along their curved path; the support stays readable. |

An image generation and editing tool must be available in the host. Codex uses its built-in image tool. Claude Code needs an available image tool or connected image service; this plugin does not bundle a renderer or credentials. If rendering is unavailable, the skill provides a ready-to-run prompt and says so. Generative edits can change small details, so the skill checks the output and saves a new version of the source.

The skill produces clean photographs by default. Add headings, buttons and readability overlays in your page. It includes original instructions and prompt recipes, with no copied Wonderful.ai images or logos. Repeatable test requests and inspection criteria are in [the behavioural checks](plugins/astack/skills/slow-shutter/evals/cases.md).

## Making a film

### Make it twice

A good film is made in two passes. The first is cheap, so you can change your mind. The second is expensive, so you only start it once the story is locked.

| | Pass one: `html-video` | Pass two: `afterburn` |
|---|---|---|
| Job | Settle the story, the words, the timing and the sound | Make every second look crafted |
| Made with | HTML, GSAP, SVG, Canvas, WebGL | Blender, driven by Python scripts |
| A re-cut costs | About a minute | Hours of rendering |
| Camera | Usually still | Always moving: pushes, whips, dives, rack focus |
| Between beats | Fades and slides | Transforms: one thing turns into the next |
| Finish | Clean and flat | Depth of field, motion blur, bloom and film grain on every frame |
| Ships alone? | Yes, for social clips and demos | Yes, from any preview |

The preview is the spec. Afterburn never changes when a beat happens or what it says. If the story is wrong, fix the preview and run afterburn again.

### Pass one: html-video

A film is one HTML page that can draw any moment on demand. The renderer jumps to each frame in headless Chromium, screenshots it, and pipes the frames to ffmpeg. Then it proves the result: a contact sheet cut from the final MP4, and its loudness.

| Step | What happens | Done when |
|---|---|---|
| Brief | Agree the one message, audience, formats, length and sound | The film fits in one sentence, and every fact on screen has a source |
| Storyboard | A row per beat: time, words, motion, sound cue | The times add up and the words are final |
| Scaffold | Copy the starter page and swap in the brand | The page opens and plays |
| Build | One paused timeline, every frame drawn from the time alone | Any frame can be drawn in any order |
| Stills | One frame from every scene, in every format | Nothing clips, collides or reads too small |
| Render | The full film per format, with sound | The contact sheet from the MP4 looks right and loudness is on target |
| Deliver | MP4s and a poster frame per format | Anything unverified is named |
| Afterburn | Optional: hand the page to the second pass | Every beat and every flat element is tagged |

The page talks to the renderer through a few globals:

| Global | Meaning |
|---|---|
| `__ready` | Resolves once fonts, images and the timeline are ready |
| `__seek(t)` | Draws the frame at `t` seconds |
| `__duration` | Length in seconds |
| `__format`, `__formats`, `__size` | The current aspect ratio, all supported ones, and the stage size |
| `__cues` | Sound events: time, sound name, volume |
| `__beats` | The storyboard, one row per beat. Afterburn reads it as its beat table |
| `data-layer`, `data-at` | Tags on flat text and UI, so afterburn can lift each one into 3D |

One page renders every format:

| Format | Size | Where it plays |
|---|---|---|
| `16x9` | 1920×1080 | YouTube, LinkedIn, websites, slides |
| `9x16` | 1080×1920 | Reels, TikTok, Shorts, Stories |
| `1x1` | 1080×1080 | Feeds |
| `4x5` | 1080×1350 | Instagram and LinkedIn feeds |

### Pass two: afterburn

Every input becomes one **handoff** folder, made by the intake script. Everything after that works the same, whatever the source was.

| Input | What intake pulls out | What you still do |
|---|---|---|
| An html-video film | Exact beat times, words and motion notes, the sound cues, and each tagged element as a see-through PNG at 3x size | Nothing. It is the richest input. |
| Any video: a hyperframes render, another tool's MP4, a reference film | One beat per hard cut, one still per beat, and every frame at 10 per second | Fill in what is on screen and how it moves, by looking at the frames |
| A project that renders to video | Render it to MP4 with its own tool, then treat it as a video | Same as a video |
| Just a brief | Nothing yet | Make an html-video preview first |

```bash
node plugins/astack/skills/afterburn/scripts/intake.mjs video/my-film/index.html
```

| Handoff file | What is in it |
|---|---|
| `beats.json` | One row per beat: start, end, words, preview motion, and blanks for style, energy, tactic and exit |
| `cues.json` | The sound cue list |
| `stills/`, `stills.png` | One frame from the middle of each beat, and all of them on one sheet |
| `layers/` | Each tagged element alone, transparent, ready for 3D (HTML input) |
| `frames/` | The whole video at 10 frames per second, to study (video input) |

Then the steps. Each has a clear finish line, so nothing gets called done early.

| # | Step | What happens | Done when |
|---|---|---|---|
| 1 | Intake | Any input becomes the handoff folder | Every beat has a time, its words and its motion |
| 2 | Style and energy | Each beat gets a look and a pace | Every row names both |
| 3 | Detail pass on paper | Each beat's flat motion gets a named upgrade, and a named move into the next beat | No beat exits on a plain fade |
| 4 | Set up | Copy the toolkit in, make any art or footage | The film folder is ready |
| 5 | Layers | Reuse the preview's layers, draw only what is missing | Every layer exists and reads clearly |
| 6 | Build each scene | One Blender script per scene, stills checked beside the preview's stills | Each still says the same thing at the same moment, with the new move |
| 7 | Render | One scene at a time, in the background, at low priority | All frames on disk |
| 8 | Sound | A soundtrack from the preview's cues | Mixed to the loudness target |
| 9 | Assemble and check | Join scenes, add grain and sound, cut a contact sheet from the final file | Every beat in order, same length as the preview, loudness within 1 LU |
| 10 | Voiceover | Optional: timed lines, a picked voice, one take, placed on the beats | Every line lands on its beat |

**Styles** set the room. Scenes in one film can mix them.

| Style | Looks like | Reach for it when |
|---|---|---|
| `techy` | Near-black room, thin white lines, glowing dots, code fragments, strong bloom | The problem, chaos, systems, data flowing |
| `glossy` | Light grey studio, shiny 3D objects with sweeping colour, soft shadows | A hero object, the moment it clicks |
| `airy` | White to pale blue, product UI floating over a photo | The product in use, a question and its answer |
| `paper` | Warm textured paper, painted illustration, small labels | Knowledge, structure, growth, a calmer explanation |
| `nature` | Real footage of sky and plants, white type, deep focus | The closing promise, the brand line |

**Energy** sets the pace.

| | `big` | `smooth` |
|---|---|---|
| Moves | Fast middles, hard stops | Even glides |
| Pops | Overshoot and settle | No overshoot |
| Glitch frames | On | Off |
| A beat lasts | About 1.2 seconds | About 2 seconds |
| Between scenes | Whips, hard cuts, dives, invert frames | Pushes, rack focus, pixel sweeps, slow scatters |

**Tactics** are reusable Blender moves. Each reads its easing from the style and energy. The full list is in [`reference/tactics.md`](plugins/astack/skills/afterburn/reference/tactics.md).

| Family | What they do | Examples |
|---|---|---|
| Camera | Keep every shot alive | `push`, `whip`, `cut`, `dive`, `rack_focus`, `lens` |
| Text and layers | Land words and UI with weight | `swap_layers`, `flash`, `glitch_burst`, `type_on`, `tilt_in`, `rise_in` |
| Glows, glyphs, clouds | Fill depth around a title | `glow_dot`, `glyph_orbit`, `depth_cloud`, `scatter_settle` |
| Lines, threads, rings | Turn text into lines, and lines into shapes | `wave_line`, `fan_threads`, `dots_to_ring`, `glossy_ring`, `ring_tunnel` |
| Backgrounds and grades | Set the world and shift its mood | `photo_plane`, `pixel_sweep`, `ripple_bg`, `alarm_grade`, `wind`, `invert_frames` |
| Bursts, growth, particles | Big reveals and living detail | `card_burst`, `grow_reveal`, `sprite_pop`, `drift`, `voxel_shape` |

**Transform, not fade.** The biggest jump in quality comes from each world turning into the next.

| From | Into | How |
|---|---|---|
| Title | Line | Whip off the title; a glowing dot starts a wavy line where the last word ended |
| Threads | Ring | Threads pull back while their end dots fly into a ring, then the ring closes |
| Logo | Heading | Letters fly apart, the heading tilts in, the background resolves through a pixel sweep |
| Button | Burst | Dive into the button, then cards burst out from that same point |
| Dark UI | Paper | A couple of colour-negative frames hand over to the paper world |
| Scatter | Structure | Floating labels land, then an illustration grows to meet them |

### Worked examples

| Example | Skill | What it shows |
|---|---|---|
| `html-video/example/` | html-video | A 43 second launch film in 16:9 and 9:16: a floor plan built from data, a scan reveal, counters, a camera pull-back over a 1,000-square grid, cue-driven sound |
| `afterburn/examples/eunomia-connected/` | afterburn | A 35 second launch film in seven Blender scenes: beat table, every scene script, layers, sound and voiceover mix |

## Needs

| Tool | Used by | Why |
|---|---|---|
| Image generation/editing tool | slow-shutter | Creates photos and edits uploaded images; supplied by the host |
| Node | both video skills | Runs the renderer, intake, layer export and soundtrack |
| Playwright with Chromium (`npm i -D playwright && npx playwright install chromium`) | both video skills | Draws HTML frames and layers |
| ffmpeg | both video skills | Encoding, contact sheets, loudness |
| Blender 5.1 | afterburn | Builds and renders every scene |

## License

MIT
