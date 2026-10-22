"""Place a voiceover take line by line on a finished film, duck the music bed under it, set the level, mux.
  python3 -I mix_vo.py <config.json>
config.json:
  {"take": "vo/take.mp3", "bed": "out/soundtrack.wav", "film": "out/film.mp4", "out": "out/film-vo.mp4",
   "duration": 35.0, "target_lufs": -21, "bed_db": -3,
   "lines": [[take_start, take_end, film_start, "text"], ...]}
Find each line's take span with silencedetect (the gaps between sentences):
  ffmpeg -i take.mp3 -af silencedetect=noise=-38dB:d=0.18 -f null - 2>&1 | grep silence_
Film starts come from the script's beat table. The script refuses lines that overlap in the film.
Paths are relative to the config file."""
import json, re, subprocess, sys
from pathlib import Path
cfg_path = Path(sys.argv[1]); C = json.loads(cfg_path.read_text()); R = cfg_path.parent
P = lambda k: (R / C[k]).resolve()
work = P('out').parent / 'vo-work'; work.mkdir(parents=True, exist_ok=True)
run = lambda *a: subprocess.run(a, check=True, capture_output=True, text=True)
def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)[-1])
LINES, D = C['lines'], C.get('duration', 35.0)
for (a, b, at, t), (a2, b2, at2, t2) in zip(LINES, LINES[1:]):
    assert at + (b - a) + 0.1 < at2, f'overlap: "{t}" runs into "{t2}"'
ins, delays = [], []
for i, (a, b, at, _) in enumerate(LINES):  # a little air either side, 10 ms fades so nothing clicks
    a2, b2 = max(0.0, a - 0.04), b + 0.12
    clip = work / f'line{i + 1:02d}.wav'
    run('ffmpeg', '-v', 'error', '-y', '-ss', f'{a2}', '-to', f'{b2}', '-i', str(P('take')), '-af', f'afade=t=in:d=0.01,afade=t=out:st={b2 - a2 - 0.03}:d=0.03', '-ar', '48000', '-ac', '2', str(clip))
    ins += ['-i', str(clip)]; delays.append(int((at - (a - a2)) * 1000))
f = ''.join(f'[{i}]adelay={d}|{d}[d{i}];' for i, d in enumerate(delays)) + ''.join(f'[d{i}]' for i in range(len(delays)))
f += f'amix=inputs={len(delays)}:normalize=0,apad=whole_dur={D},atrim=0:{D},loudnorm=I=-17:TP=-2:LRA=7[vo]'
voice = work / 'voice-track.wav'
run('ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f, '-map', '[vo]', '-ar', '48000', str(voice))
mix0 = work / 'mix-pre.wav'
run('ffmpeg', '-v', 'error', '-y', '-i', str(P('bed')), '-i', str(voice), '-filter_complex',
    f"[0]volume={C.get('bed_db', -3)}dB[b];[1]asplit[v1][v2];[b][v1]sidechaincompress=threshold=0.02:ratio=5:attack=15:release=350:makeup=1[d];"
    '[d][v2]amix=inputs=2:normalize=0[m]', '-map', '[m]', '-ar', '48000', str(mix0))
i0, _ = lufs(mix0); target = C.get('target_lufs', -19)
mix = work / 'mix.wav'
run('ffmpeg', '-v', 'error', '-y', '-i', str(mix0), '-af', f'volume={target - i0:.2f}dB,alimiter=limit=0.84:level=false', '-ar', '48000', str(mix))
i1, p1 = lufs(mix)
run('ffmpeg', '-v', 'error', '-y', '-i', str(P('film')), '-i', str(mix), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
    '-shortest', '-movflags', '+faststart', str(P('out')))
print(f'mix {i1:.1f} LUFS, peak {p1:.1f} dBFS -> {P("out")}')
for a, b, at, t in LINES: print(f'{at:5.2f}-{at + b - a:5.2f}  {t}')
