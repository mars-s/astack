"""Prepare a painted illustration on white for tactics.grow_reveal (trees, roots, rivers, cracks, vines, ink).

  python3 -I grow_prep.py <image.png> [seed corner: bl|br|tl|tr|c, default bl]
Writes next to the image, with its stem as prefix:
  <stem>_rgba.png   cut out, edges un-blended from the white
  <stem>_grow.png   16-bit growth map: distance along the shape from the seed point (the shader reveals pixels below a
                    rising threshold, so it grows outward from the seed)
  <stem>_tips.json  tips (far ends) in image px with their growth value, for placing labels or sprites
  <stem>_debug.png  tips marked, for a visual check
"""
import json, sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

src = Path(sys.argv[1]); root = src.parent; stem = src.stem
seed = sys.argv[2] if len(sys.argv) > 2 else 'bl'
img = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
H, W, _ = img.shape
lo = img.min(axis=2)
alpha = np.clip((246.0 - lo) / 34.0, 0, 1)  # white paper -> 0, bark -> 1, soft edge between
a3 = alpha[..., None]
rgb = np.where(a3 > 0.02, (img - (1 - a3) * 255.0) / np.maximum(a3, 0.02), 0)  # un-blend the white fringe
rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
Image.fromarray(rgba, 'RGBA').save(root / f'{stem}_rgba.png')

# geodesic distance from the trunk base, on a half-size mask
S = 2
m = alpha[::S, ::S] > 0.5
h, w = m.shape
ys, xs = np.nonzero(m)
corner = {'bl': (0, h), 'br': (w, h), 'tl': (0, 0), 'tr': (w, 0), 'c': (w / 2, h / 2)}[seed]
base = np.argmin((xs - corner[0]) ** 2 + (ys - corner[1]) ** 2)  # the shape pixel nearest the seed corner
dist = np.full((h, w), np.inf, np.float32)
q = deque([(ys[base], xs[base])]); dist[ys[base], xs[base]] = 0
steps = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0), (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)]
while q:  # a BFS with diagonal costs is close enough to true geodesic distance for a reveal
    y, x = q.popleft(); d = dist[y, x]
    for dy, dx, c in steps:
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and d + c < dist[ny, nx] - 1e-3:
            dist[ny, nx] = d + c; q.append((ny, nx))
finite = np.isfinite(dist)
dmax = dist[finite].max()
# spread values a few pixels into the soft edge so anti-aliased fringes reveal with their branch
filled = np.where(finite, dist, np.inf)
for _ in range(4):
    p = np.pad(filled, 1, constant_values=np.inf)
    nb = np.min([p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] for dy in (-1, 0, 1) for dx in (-1, 0, 1)], axis=0)
    filled = np.where(np.isfinite(filled), filled, nb)
g = np.where(np.isfinite(filled), filled / dmax, 1.0)
g_full = np.kron(g, np.ones((S, S)))[:H, :W]
Image.fromarray((g_full * 65535).astype(np.uint16)).save(root / f'{stem}_grow.png')

# tips: pixels that are the farthest-grown within a window, well away from the trunk
R = 16
dd = np.where(finite, dist, -1)
def maxfilt(a, r, axis):
    p = np.pad(a, [(r, r) if i == axis else (0, 0) for i in range(2)], constant_values=-1)
    return np.max([np.take(p, range(k, k + a.shape[axis]), axis=axis) for k in range(2 * r + 1)], axis=0)
mx = maxfilt(maxfilt(dd, R, 0), R, 1)
cand = np.argwhere((dd >= mx) & (dd > 0.3 * dmax))
tips = []
for y, x in sorted(cand.tolist(), key=lambda p: -dd[p[0], p[1]]):
    if all((y - ty) ** 2 + (x - tx) ** 2 > (R * 1.2) ** 2 for ty, tx, _ in tips):
        tips.append((y, x, float(dd[y, x] / dmax)))
out = [{'x': int(x * S), 'y': int(y * S), 'g': round(gv, 4)} for y, x, gv in tips]
(root / f'{stem}_tips.json').write_text(json.dumps({'w': W, 'h': H, 'tips': out}, indent=1))
dbg = Image.fromarray(rgba, 'RGBA').convert('RGB'); dr = ImageDraw.Draw(dbg)
for t in out:
    dr.ellipse([t['x'] - 9, t['y'] - 9, t['x'] + 9, t['y'] + 9], outline=(255, 120, 0), width=4)
dbg.save(root / f'{stem}_debug.png')
print(f'{len(out)} tips, dmax {dmax:.0f}px (half-res)')
