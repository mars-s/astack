# Smoke test: every tactic in three throwaway scenes, one low-res frame each. Fails loudly on any error.
#   Blender -b --factory-startup -P tactics_check.py -- <scratch dir>
# Placeholder images are generated here, so it needs nothing from a project.
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import bpy
import lib
from lib import *
from tactics import *

OUT = argv()[0] if argv() else '/tmp/tactics_check'
os.makedirs(OUT, exist_ok=True)

def png(name, w, h, rgba, alpha_box=True):
    p = os.path.join(OUT, name + '.png')
    if os.path.exists(p): return p
    im = bpy.data.images.new(name, w, h, alpha=True)
    a = np.zeros((h, w, 4), np.float32)
    if alpha_box: a[h // 4:3 * h // 4, w // 8:7 * w // 8] = rgba
    else: a[:] = rgba
    im.pixels = a.ravel(); im.filepath_raw = p; im.file_format = 'PNG'; im.save()
    return p

TXT = png('txt', 1400, 160, (0.9, 0.9, 0.95, 1))
WORD = png('word', 1400, 160, (0.3, 0.8, 0.5, 1))
CARD = png('card', 560, 300, (0.9, 0.4, 0.3, 1))
PHOTO = png('photo', 768, 512, (0.4, 0.6, 0.9, 1), alpha_box=False)
SPR = png('sprite', 64, 64, (1, 0.7, 0.8, 1))
# a growth illustration and its map: a diagonal bar whose growth value rises along it
gi = np.zeros((256, 384, 4), np.float32); gm = np.ones((256, 384, 4), np.float32)
for x in range(384):
    y = int(220 - x * 0.5)
    gi[max(0, y - 6):y + 6, x] = (0.4, 0.25, 0.15, 1); gm[max(0, y - 8):y + 8, x, :3] = x / 384
for nm, arr in (('grow_rgba', gi), ('grow_map', gm)):
    im = bpy.data.images.new(nm, 384, 256, alpha=True); im.pixels = arr.ravel(); im.filepath_raw = os.path.join(OUT, nm + '.png'); im.file_format = 'PNG'; im.save()

def finish(tag, frame):
    s = bpy.context.scene; s.render.resolution_percentage = 25; s.eevee.taa_render_samples = 4
    s.frame_set(frame); s.render.filepath = os.path.join(OUT, f'{tag}.png'); bpy.ops.render.render(write_still=True)
    print('CHECK ok', tag)

# 1: techy, big: text, flash, glitch, glyphs, cloud, wave, fan, ring, tunnel, invert
s, cam = reset(60); lib.COMP = True; apply_style('techy', 'big')
swap_layers([TXT, WORD], [(0, 1, 10), (1, 10, 60)], parent=cam)
flash(WORD, 10, parent=cam); glitch_burst([TXT, WORD, TXT], 30, parent=cam)
glyph_orbit([SPR] * 8, 5, swirl=(20, 28, -75, 1.35)); depth_cloud([TXT], 10, (4, 6), 40, w=400)
glow_dot(400, 540, 3); wave_line((400, 540), (1500, 540), 4, 20, n=60)
curves, ends = fan_threads((1500, 540), [(300, -200), (500, 150)], 22, retract=(40, 50), decor=[(900, -500)])
dots = tip_dots(ends, 30)
spin = dots_to_ring(dots, ends, (960, 540), 300, 42, whip_at=50, f_hide=55)
dashes_close((960, 540), 300, 2, 52, 56, spin, 58)
tor, mat = glossy_ring((960, 540), 300, 22, [(0, '#0b5b35'), (0.4, '#9ff0c4'), (1, '#0b5b35')], 50)
ring_tunnel(tor, mat, (960, 540), 52, f_end=60)
invert_frames([59]); push(cam, 1, 60, 960, 540, 1.0, 1.1); lens(cam)
finish('scene1_f20', 20); finish('scene1_f57', 57)

# 2: airy, smooth: photo sweep, tilt-in, rise, float, dive, ripples, cards, alarm, voxels, cut, rack, plate
s, cam = reset(60); lib.COMP = True; apply_style('airy', 'smooth')
ph = photo_plane('photo', PHOTO, z=-0.8, w=2200, h=1238, sweep=True); pixel_sweep(ph, 2, 12)
h = plane('head', TXT, 960, 400, w=1100, h=120); tilt_in(h, 3, 10)
b = plane('bar', CARD, 960, 600, w=600); rise_in(b, 5, 14); float_drift(b, 14, 40)
ripple_bg(20, 50); card_burst([CARD] * 6, 20, interval=2, burst=(40, 48, 3.0, 55, 6.0))
alarm_grade(ph, 30, 45); voxel_shape((1400, 500), 25, n=4)
cut(cam, 30, 900, 500, 1.6); dive(cam, 40, 55, 1200, 600, 3.0); rack_focus(cam, 20, 23, 28)
screen_plate(TXT, frames=[(1, False), (58, True)])
finish('scene2_f26', 26); finish('scene2_f50', 50)

# 3: paper, smooth: scatter, growth, sprites, drift, sway, warm grade, wind
s, cam = reset(60); lib.COMP = True; apply_style('paper', 'smooth')
pp = photo_plane('paper', PHOTO, z=-0.4, w=2400, h=1350); warm_grade(pp, 40, 50); wind(pp)
sw = sway((200, 900), [(10, 0), (30, 0.5), (60, -0.3)])
scatter_settle([(SPR, 600 + 80 * i, 300 + 40 * i, 120, 60) for i in range(5)], 20, parent=sw)
g, frame_for = grow_reveal(os.path.join(OUT, 'grow_rgba.png'), os.path.join(OUT, 'grow_map.png'), (200, 300, 3.0), 25, 45)
assert 25 <= frame_for(0.5) <= 45
sprite_pop([SPR], [(700, 500), (900, 400)], [46, 48]); drift([SPR], 3, 40, 60)
finish('scene3_f35', 35); finish('scene3_f55', 55)
print('CHECK all tactics ran')
