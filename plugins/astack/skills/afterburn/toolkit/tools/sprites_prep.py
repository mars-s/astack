"""Cut a sprite sheet painted on white (blossoms, leaves, stickers, icons, spaced apart) into RGBA PNGs.
  python3 -I sprites_prep.py <sheet.png> <out dir>
Writes <out dir>/s00.png... and index.json with each sprite's size and a colour kind (pink/red -> 'blossom', else 'leaf').
"""
import json, sys
from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image
out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
img = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32)
H, W, _ = img.shape
alpha = np.clip((246.0 - img.min(axis=2)) / 30.0, 0, 1)
m = alpha > 0.15
seen = np.zeros_like(m); idx = []
S = 4  # flood on a coarse grid, then crop at full res
mc = m[::S, ::S]; h, w = mc.shape; lab = -np.ones((h, w), int); k = 0
for y in range(h):
    for x in range(w):
        if mc[y, x] and lab[y, x] < 0:
            q = deque([(y, x)]); lab[y, x] = k; pts = []
            while q:
                cy, cx = q.popleft(); pts.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mc[ny, nx] and lab[ny, nx] < 0:
                            lab[ny, nx] = k; q.append((ny, nx))
            if len(pts) > 40:
                ys, xs = zip(*pts)
                y0, y1, x0, x1 = max(0, min(ys) * S - 6), min(H, max(ys) * S + S + 6), max(0, min(xs) * S - 6), min(W, max(xs) * S + S + 6)
                crop = img[y0:y1, x0:x1]; a = alpha[y0:y1, x0:x1][..., None]
                rgb = np.where(a > 0.02, (crop - (1 - a) * 255) / np.maximum(a, 0.02), 0)
                Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a[..., 0] * 255]).astype(np.uint8), 'RGBA').save(out / f's{len(idx):02d}.png')
                mean = (crop * a).sum((0, 1)) / max(a.sum(), 1)
                kind = 'blossom' if mean[0] > mean[1] + 20 else 'leaf'
                idx.append({'file': f's{len(idx):02d}.png', 'kind': kind, 'w': x1 - x0, 'h': y1 - y0})
            k += 1
(out / 'index.json').write_text(json.dumps(idx, indent=1))
print(len(idx), 'sprites', {kd: sum(1 for i in idx if i['kind'] == kd) for kd in ('blossom', 'leaf')})
