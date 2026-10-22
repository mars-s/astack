# Scene D (film 9.97 to 13.30 s, 100 frames). On white: the Eunomia lockup builds on construction lines and
# flies apart. "What did we decide?" swings in from a tilt and sharpens while the sea resolves through a cyan pixel
# sweep. The recall bar types the question, then the camera dives into the send button.
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, '..', 'layers', 'out', 'D')
ART = os.path.join(HERE, '..', '..')
N = 100
s, cam = reset(N, world=hexc('#f3f6f9')[:3], samples=48)
compositor(bloom=0.3, threshold=1.2, size=6)
s.render.motion_blur_shutter = 0.5

# the lockup, building and then tracking apart
logo = seq_plane('logo', os.path.join(OUT, 'logo_build'), 1, N, 960, 540, w=1200, h=420)
visible(logo, [(1, True), (44, False)])
cam_at(cam, 1, 960, 540, 1.0, 'LINEAR'); cam_at(cam, 41, 960, 540, 1.06, 'SINE', 'EASE_IN')

# the sea, revealed by a pixel sweep moving right to left
SEA = os.path.join(ART, 'sea.jpg') if not os.path.exists(os.path.join(ART, 'footage', 'sea.mp4')) else os.path.join(ART, 'footage', 'sea.mp4')
sea = photo_plane('sea', SEA, z=-0.8, w=2200, h=1238, sweep=True)
visible(sea, [(1, False), (41, True)])
node_keys(sea, 'edge', 0, [(41, -0.35), (53, 1.35)], 'SINE', 'EASE_IN_OUT', output=True)  # sharp spreads left to right

# the heading swings in from a 3D tilt, out of focus near the lens, and lands sharp
head = plane('heading', os.path.join(OUT, 'heading.png'), 960, 402, z=0.0, w=1100, h=120)
visible(head, [(1, False), (42, True)])
hz, hy = head.location.z, head.location.y
for idx, v in ((0, math.radians(-38)), (1, math.radians(24)), (2, math.radians(-7))):
    key(head, 'rotation_euler', 42, v, 'EXPO', 'EASE_OUT', index=idx); key(head, 'rotation_euler', 50, 0.0, 'EXPO', 'EASE_OUT', index=idx)
key(head, 'location', 42, hz + 2.2, 'EXPO', 'EASE_OUT', index=2); key(head, 'location', 51, hz, 'EXPO', 'EASE_OUT', index=2)
key(head, 'location', 42, hy - 0.5, 'EXPO', 'EASE_OUT', index=1); key(head, 'location', 51, hy, 'EXPO', 'EASE_OUT', index=1)
opacity(head, [(42, 0.0), (45, 1.0)], 'LINEAR')

# the recall bar: rises in, types the question
bar = seq_plane('bar', os.path.join(OUT, 'bar'), 47, N, 960, 522, w=1040, h=110)
visible(bar, [(1, False), (45, True)])
opacity(bar, [(45, 0.0), (50, 1.0)], 'LINEAR')
by = bar.location.y
key(bar, 'location', 45, by - 0.09, 'EXPO', 'EASE_OUT', index=1); key(bar, 'location', 52, by, 'EXPO', 'EASE_OUT', index=1)

# camera: a resolve push on the heading, then the dive into the send button with a slight roll
cam_at(cam, 42, 960, 540, 1.0, 'CONSTANT')
cam_at(cam, 42.6, 960, 560, 0.96, 'SINE', 'EASE_OUT')
cam_at(cam, 74, 975, 540, 1.04, 'SINE', 'EASE_IN_OUT')
SEND = (440 + 987, 522 - 55 + 10 + 44)
cam_at(cam, 99, *SEND, 4.1, 'EXPO', 'EASE_IN_OUT')
cam_at(cam, 100, SEND[0] + 4, SEND[1], 4.15, 'LINEAR')
key(cam, 'rotation_euler', 74, 0.0, 'EXPO', 'EASE_IN_OUT', index=2); key(cam, 'rotation_euler', 99, math.radians(-4), 'EXPO', 'EASE_IN_OUT', index=2)
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 1.6

if __name__ == '__main__':
    a = argv()
    render(os.path.join(HERE, '..', 'frames', 'D'), [int(x) for x in a[0].split(',')] if a else None)
