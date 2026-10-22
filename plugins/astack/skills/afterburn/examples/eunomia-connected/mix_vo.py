"""Cut the voice take into its ten lines, place each at its spot in the film, duck the music bed under it,
set the overall level, and mux onto the picture.   python3 -I mix_vo.py <v2 folder>
Line spans come from silencedetect on vo/takeA.mp3 (noise -38 dB, 0.18 s). Film starts are the beats in
voiceover-script.md, checked against the cut."""
import json, re, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1]); vo = root / 'vo'; out = root / 'out'
TAKE = vo / 'takeA.mp3'
# (take start, take end, film start, line)
LINES = [
    (0.00, 2.33, 0.30, 'Your AI agents forget everything.'),
    (2.83, 3.71, 2.80, 'Meet Eunomia.'),
    (4.03, 6.31, 4.10, 'One shared memory for all your agents.'),
    (6.68, 8.66, 10.60, 'Ask any agent what the team decided.'),
    (9.10, 11.09, 15.50, 'Your agent reaches for a client secret.'),
    (11.55, 13.96, 18.40, 'Eunomia remembers the team said no.'),
    (14.45, 16.19, 21.10, 'Every agent adds what it learns.'),
    (16.43, 18.43, 24.60, 'Nobody has to re-explain the project.'),
    (18.82, 21.19, 27.20, "It's open source, and you can host it yourself."),
    (21.50, 22.32, 30.90, 'Give it a try.'),
]
TARGET_LUFS = -21.0  # a touch under the old -19, as asked
run = lambda *a: subprocess.run(a, check=True, capture_output=True, text=True)
def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)[-1])
# 1. one clip per line, a little air either side, 10 ms fades so nothing clicks
ins, delays = [], []
for i, (a, b, at, _) in enumerate(LINES):
    a2, b2 = max(0.0, a - 0.04), b + 0.12
    clip = vo / f'line{i + 1:02d}.wav'
    run('ffmpeg', '-v', 'error', '-y', '-ss', f'{a2}', '-to', f'{b2}', '-i', str(TAKE), '-af', f'afade=t=in:d=0.01,afade=t=out:st={b2 - a2 - 0.03}:d=0.03', '-ar', '48000', '-ac', '2', str(clip))
    ins += ['-i', str(clip)]; delays.append(int((at - (a - a2)) * 1000))
# no two lines may overlap in the film
for (a, b, at, t), (a2, b2, at2, t2) in zip(LINES, LINES[1:]):
    assert at + (b - a) + 0.1 < at2, f'overlap: "{t}" runs into "{t2}"'
# 2. the voice track, 35 s long
f = ''.join(f'[{i}]adelay={d}|{d}[d{i}];' for i, d in enumerate(delays)) + ''.join(f'[d{i}]' for i in range(len(delays)))
f += f'amix=inputs={len(delays)}:normalize=0,apad=whole_dur=35,atrim=0:35,loudnorm=I=-17:TP=-2:LRA=7[vo]'
voice = vo / 'voice-track.wav'
run('ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f, '-map', '[vo]', '-ar', '48000', str(voice))
# 3. bed down 3 dB, ducked under the voice; then the two together, set to the target level
bed = out / 'eunomia-v2-soundtrack-notype.wav'
mix0 = vo / 'mix-pre.wav'
run('ffmpeg', '-v', 'error', '-y', '-i', str(bed), '-i', str(voice), '-filter_complex',
    '[0]volume=-3dB[b];[1]asplit[v1][v2];[b][v1]sidechaincompress=threshold=0.02:ratio=5:attack=15:release=350:makeup=1[d];'
    '[d][v2]amix=inputs=2:normalize=0[m]', '-map', '[m]', '-ar', '48000', str(mix0))
i0, _ = lufs(mix0)
mix = out / 'eunomia-v2-mix-vo.wav'
run('ffmpeg', '-v', 'error', '-y', '-i', str(mix0), '-af', f'volume={TARGET_LUFS - i0:.2f}dB,alimiter=limit=0.84:level=false', '-ar', '48000', str(mix))
i1, p1 = lufs(mix)
# 4. onto the picture (video copied, not re-encoded)
final = out / 'eunomia-connected-v2-vo.mp4'
run('ffmpeg', '-v', 'error', '-y', '-i', str(out / 'eunomia-connected-v2.mp4'), '-i', str(mix), '-map', '0:v', '-map', '1:a',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', str(final))
(vo / 'timing.json').write_text(json.dumps([{'line': t, 'film_start': at, 'film_end': round(at + b - a, 2), 'take_start': a, 'take_end': b} for a, b, at, t in LINES], indent=1))
print(f'mix {i1:.1f} LUFS, peak {p1:.1f} dBFS -> {final}')
for a, b, at, t in LINES: print(f'{at:5.2f}-{at + b - a:5.2f}  {t}')
