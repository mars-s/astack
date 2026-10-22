# Scene A (film 0.00 to 2.60 s, frames 1-78): hairlines, a travelling slash, a flare, "too many chats / agents /
# sessions" with a glow flash on every new word, orbiting glyphs that swirl, a 3D cloud of code the camera pushes
# through, then a one-or-two-frame-per-state glitch burst and a clean hold.
import sys, os, math, random
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

HERE = os.path.dirname(__file__)
L = lambda n: os.path.join(HERE, '..', 'layers', 'out', 'A', n + '.png')
s, cam = reset(78, world=hexc('#050608')[:3])
compositor(bloom=0.55, threshold=1.0, size=7)
rnd = random.Random(4)

def on_cam(ob):  # everything but the code cloud rides with the camera, so the title holds its size
    parent_keep(ob, cam)
    return ob

# hairlines: a double horizontal pair, then a double vertical pair drawn from the centre
GREY = hexc('#9aa3b2')
for i, y in enumerate((536, 545)):
    ln = on_cam(rect(f'h{i}', 960, y, 1920, 1.3, GREY, z=-0.03 - 0.004 * i))
    opacity(ln, [(1, 0.0), (3, 0.55), (28, 0.55), (40, 0.0)], 'LINEAR')
for i, x in enumerate((955, 965)):
    ln = on_cam(rect(f'v{i}', x, 540, 1.3, 1080, GREY, z=-0.05 - 0.004 * i))
    tween(ln, 'scale', 13, 0.0001, 21, ln.scale.y, 'EXPO', 'EASE_OUT', index=1)
    opacity(ln, [(1, 0.0), (13, 0.45), (28, 0.45), (40, 0.0)], 'LINEAR')

# the travelling slash splits in two and the halves drift apart, then out and away
for i, side in enumerate((-1, 1)):
    sl = on_cam(plane(f'slash{i}', L('gl_slash'), 960, 540, z=0.06 + 0.004 * i, w=60))
    sl.location.x += -0.9  # starts left of centre on the line
    x0 = sl.location.x
    tween(sl, 'location', 1, x0, 9, x0 + 0.9 + side * 0.035, 'QUART', 'EASE_OUT', index=0)
    tween(sl, 'location', 13, sl.location.x, 16, side * 0.42, 'EXPO', 'EASE_OUT', index=0)
    tween(sl, 'location', 16, side * 0.42, 40, side * 0.9, 'SINE', 'EASE_OUT', index=0)
    tween(sl, 'location', 16, sl.location.y, 40, sl.location.y - 0.35, 'SINE', 'EASE_OUT', index=1)
    opacity(sl, [(1, 1.0), (30, 1.0), (40, 0.0)], 'LINEAR')

# flare at the crossing
fl = on_cam(plane('flare', L('flare'), 960, 540, z=0.09, w=90))
strength(fl, [(13, 6.0), (15, 2.0), (18, 1.0)], 'LINEAR')
opacity(fl, [(1, 0.0), (12, 0.0), (13, 1.0), (15, 1.0), (18, 0.0)], 'LINEAR')

# the title: line layers swap, a flash layer spikes on each new word
lines = {}
for i, nm in enumerate(('l_too', 'l_toomany', 'l_chats', 'l_agents', 'l_sessions')):
    lines[nm] = on_cam(plane(nm, L(nm), 960, 540, z=0.004 * i, w=1400))  # stacked layers never share a depth
    opacity(lines[nm], [(1, 0.0)])
SWAPS = [('l_too', 13, 19), ('l_toomany', 19, 21), ('l_chats', 21, 38), ('l_agents', 38, 46), ('l_sessions', 46, 79)]
for nm, a, b in SWAPS:
    opacity(lines[nm], [(a, 1.0), (b, 0.0)])
strength(lines['l_too'], [(13, 6.0), (17, 1.0)], 'LINEAR')
for j, (nm, f, peak) in enumerate((('fl_many', 19, 14), ('fl_chats', 21, 10), ('fl_agents', 38, 10), ('fl_sessions', 46, 10))):
    fx = on_cam(plane(nm, L(nm), 960, 540, z=0.03 + 0.004 * j, w=1400))  # a brighter copy of the new word, just in front
    end = min(f + 4, next((a for _, a, _ in SWAPS if a > f), f + 4))  # a flash never outlives its line
    strength(fx, [(f, peak), (end, 1.0)], 'QUAD', 'EASE_OUT')
    opacity(fx, [(1, 0.0), (f, 1.0), (end, 0.0)])

# brackets push outward as the line grows, and leave when the glyphs swirl
for i, (g, side) in enumerate((('gl_lt', -1), ('gl_gt', 1))):
    br = on_cam(plane(f'br{i}', L(g), 960, 540, z=0.07 + 0.004 * i, w=60))
    for f, half in ((18, 70), (19, 135), (21, 205)):
        key(br, 'location', f, side * half * U, 'EXPO', 'EASE_OUT', index=0)
    opacity(br, [(1, 0.0), (18, 1.0), (38, 0.0)])

# glyphs pop in around the title, then swirl round it with motion blur
swirl = bpy.data.objects.new('swirl', None); s.collection.objects.link(swirl); swirl.location = (0, 0, 0)
NAMES = ['gl_lt', 'gl_gt', 'gl_slash', 'gl_star', 'gl_dash', 'gl_slash_g', 'gl_star_g', 'gl_brace', 'gl_brace2', 'gl_slash', 'gl_lt', 'gl_star']
for i, g in enumerate(NAMES):
    a = i / len(NAMES) * math.tau + rnd.uniform(-0.25, 0.25)
    r = rnd.uniform(0.75, 1.0)
    x, y = 960 + math.cos(a) * 470 * r, 540 + math.sin(a) * 250 * r
    gp = plane(f'g{i}', L(g), x, y, w=52)
    parent_keep(gp, swirl)
    on0 = 23 + i
    opacity(gp, [(1, 0.0), (on0, 1.0), (46, 1.0), (50, 0.0)])
    tween(gp, 'scale', on0, 0.2 * gp.scale.x, on0 + 4, gp.scale.x, 'BACK', 'EASE_OUT', index=0)
    tween(gp, 'scale', on0, 0.2 * gp.scale.y, on0 + 4, gp.scale.y, 'BACK', 'EASE_OUT', index=1)
on_cam(swirl)
tween(swirl, 'rotation_euler', 37, 0.0, 47, math.radians(-75), 'EXPO', 'EASE_IN', index=2)
tween(swirl, 'scale', 37, 1.0, 47, 1.35, 'EXPO', 'EASE_IN', index=0)
tween(swirl, 'scale', 37, 1.0, 47, 1.35, 'EXPO', 'EASE_IN', index=1)

# the code cloud: snippets on tilted planes through depth; the camera pushes in through them
for i in range(40):
    z = rnd.uniform(-9.0, 5.8)
    while True:
        x, y = rnd.uniform(-150, 2070), rnd.uniform(40, 1040)
        if not (abs(y - 540) < 90 and abs(x - 960) < 420): break
    sn = plane(f'snip{i}', L(f's{i % 24:02d}'), x, y, z=z, w=640)
    sn.rotation_euler = (math.radians(rnd.uniform(-12, 12)), math.radians(rnd.uniform(-35, 35)), math.radians(rnd.uniform(-4, 4)))
    t0 = 43 + rnd.randint(0, 6)
    opacity(sn, [(1, 0.0), (t0, 0.0), (t0 + 4, rnd.uniform(0.55, 0.95)), (61, 0.0)], 'LINEAR')

# glitch burst on "too many sessions": one or two frames per state
glitch = [('l_sessions', 61, 62, 9.0), ('g_magenta', 62, 63, 1.0), ('g_cyan', 63, 65, 1.0), ('g_yellow', 65, 66, 1.0),
          ('g_pink', 66, 68, 1.0), ('g_red', 68, 70, 7.0)]
opacity(lines['l_sessions'], [(46, 1.0), (61, 1.0), (62, 0.0), (70, 1.0)])
strength(lines['l_sessions'], [(60, 1.0), (61, 9.0), (62, 1.0)], 'CONSTANT')
for j, (nm, a, b, st) in enumerate(glitch[1:]):
    gp = on_cam(plane(nm, L(nm), 960, 540, z=0.1 + 0.004 * j, w=1400, strength=st))
    opacity(gp, [(1, 0.0), (a, 1.0), (b, 0.0)])
    opacity(lines['l_sessions'], [(a, 0.0)])

# camera: a slow push, a faster push through the code with a slight roll, then a settle
tween(cam, 'location', 1, 10.0, 44, 9.55, 'LINEAR', 'AUTO', index=2)
tween(cam, 'location', 44, 9.55, 62, 7.0, 'SINE', 'EASE_IN_OUT', index=2)
tween(cam, 'location', 62, 7.0, 78, 6.85, 'SINE', 'EASE_OUT', index=2)
tween(cam, 'rotation_euler', 44, 0.0, 62, math.radians(-2.2), 'SINE', 'EASE_IN_OUT', index=2)
dof(cam, 10.0, 0.5)  # title rides at 10 from the camera; the cloud goes soft in front and behind

if __name__ == '__main__':
    a = argv()
    render(os.path.join(HERE, '..', 'frames', 'A'), [int(x) for x in a[0].split(',')] if a else None)
