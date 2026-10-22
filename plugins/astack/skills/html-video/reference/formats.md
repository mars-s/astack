# Formats

| Key | Size | Where it plays |
|---|---|---|
| `16x9` | 1920×1080 | YouTube, LinkedIn, websites, slides |
| `9x16` | 1080×1920 | Reels, TikTok, Shorts, Stories |
| `1x1` | 1080×1080 | Feeds |
| `4x5` | 1080×1350 | Instagram and LinkedIn feeds |

## Safe zones for 9x16

Platform buttons and captions cover roughly the top 250px, the bottom 400px and the right 120px. Keep copy and key numbers inside y 250 to 1520 and x 80 to 960. Ads with a call-to-action bar need more room at the bottom, so check the platform's own guide for those. Feed grids can crop a tall video to its centre 1080×1350, so the line that matters sits inside that band.

## One timeline, many formats

- The stage carries the class `f-<format>`. CSS overrides under it handle position, size and type.
- A `LAYOUT` table, one entry per format, holds the numbers motion needs: entrance offsets (slide in from the side in 16x9, from below in 9x16), grid shape, camera centre, particle origin, clip regions.
- `pos(el)` adds `offsetLeft` and `offsetTop` up to the stage. Aim cursors and shrink-into-place moves with it, so they follow the layout in every format.
- Same cues, same soundtrack: every format shares the sound.

## Re-shape, don't shrink

- Wide layouts sit things side by side; tall ones stack them. Two-column panels become 2×2 tiles, and summary cards turn sideways.
- Re-shape charts and grids per format (50×20 wide, 25×40 tall).
- A 9x16 video plays at about a third of its size on a phone. Headlines run 110 to 170px and labels at least 20px. Titles that wrap get `text-wrap: balance`, so no word sits alone on a line.
