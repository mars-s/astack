# astack

Motion film skills for Claude Code. The layout follows [pstack-claude](https://github.com/michael-denyer/pstack-claude), the Claude Code port of [Cursor's pstack](https://github.com/cursor/plugins/tree/main/pstack).

A film is made twice:

1. **`astack:html-video`** makes the preview. The film is one HTML page on a GSAP timeline, rendered frame by frame to MP4. Story, copy, timing and sound get settled here, where a re-cut takes a minute.
2. **`astack:afterburn`** does the detail pass. It takes any preview as input, keeps its timing and words, and rebuilds every beat in Blender: the camera always moves, each beat transforms into the next, with depth of field, motion blur, bloom and grain.

afterburn's intake script turns any preview into one handoff folder (beat table, sound cues, a still per beat, transparent layers):

```bash
node plugins/astack/skills/afterburn/scripts/intake.mjs video/my-film/index.html
```

It reads an html-video film exactly, and any MP4 (a hyperframes render, a reference film) by its cuts.

## Install

```bash
claude plugin marketplace add mars-s/astack
```

```bash
claude plugin install astack@astack
```

## Needs

- Node, with Playwright in the project (`npm i -D playwright && npx playwright install chromium`)
- ffmpeg on the path
- Blender 5.1 for afterburn

## License

MIT
