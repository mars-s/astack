# Scene B (film 2.60 to 9.97 s, 221 frames). The title whips off left, a green dot spits out a line with a
# travelling wobble, a second dot fans threads out to six sources, close-ups while the labels type on, a wide hold,
# then the threads pull back, the end dots fly into a spinning ring, smear into dashes, a grey ray flash, and the
# ring becomes a glossy 3D torus with "remembered." inside. The torus tilts, echoes outward and the frame goes white.
import sys, os, math, random
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
import lib
lib.COMP = False  # the camera travels far from the rest pose, so depth offsets must not move things sideways

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, '..', 'layers', 'out')
LA = lambda n: os.path.join(OUT, 'A', n + '.png')
LB = lambda n: os.path.join(OUT, 'B', n + '.png')
SEQ = lambda n: os.path.join(OUT, 'B', n, '0001.png')
SEQD = lambda n: os.path.join(OUT, 'B', n)
N = 221
s, cam = reset(N, world=hexc('#050608')[:3], samples=48)
ng, glare = compositor(bloom=0.45, threshold=1.25, size=7)
s.render.motion_blur_shutter = 0.35
rnd = random.Random(11)
s.eevee.use_shadows = True if hasattr(s.eevee, 'use_shadows') else None

WHITE = hexc('#eef1f5'); MINT = hexc('#d8ffe9')
line_mat = solid_emit('line', WHITE, 1.15)
D1 = (1190.0, 540.0)
D2 = (D1[0] + 1150, 540.0)

# --- the title, left where scene A ended
title = plane('title', LA('l_sessions'), 960, 540, z=0.0, w=1400)
opacity(title, [(1, 1.0), (9, 0.0)])

# --- glowing dots
def glow_dot(name, x, y, f_on, r=7, glow=360, glow_strength=2.2):
    core = disc(name, x, y, r, MINT, z=0.03, strength=2.0)
    core.data.materials[0] = solid_emit(name + '_s', MINT, 2.0)
    g = plane(name + '_glow', LB('glowdot'), x, y, z=-0.02, w=glow, strength=glow_strength)
    for ob in (core, g):
        sx, sy = ob.scale.x, ob.scale.y
        key(ob, 'scale', 1, 0.0, 'CONSTANT', index=0); key(ob, 'scale', 1, 0.0, 'CONSTANT', index=1)
        key(ob, 'scale', f_on - 1, 0.0, 'BACK', 'EASE_OUT', index=0); key(ob, 'scale', f_on - 1, 0.0, 'BACK', 'EASE_OUT', index=1)
        key(ob, 'scale', f_on + 5, sx, 'BACK', 'EASE_OUT', index=0); key(ob, 'scale', f_on + 5, sy, 'BACK', 'EASE_OUT', index=1)
    return core, g

glow_dot('d1', *D1, 3)
d2core, d2glow = glow_dot('d2', *D2, 24)

# --- the line with a travelling wobble packet, drawn on from D1 to D2
NP = 170
xs = [D1[0] + (D2[0] - D1[0]) * i / (NP - 1) for i in range(NP)]
wave = curve_obj('wave', [(x, 540) for x in xs], 2.2, line_mat, poly=True)
wave.data.bevel_factor_end = 0.0
tween(wave.data, 'bevel_factor_end', 4, 0.0, 25, 1.0, 'SINE', 'EASE_OUT')
def packet_y(x, f):
    c = D1[0] + 90 + 470 * ease('out', (f - 4) / 21)       # packet centre rides just behind the drawing head
    amp = 38 * min(1.0, (f - 3) / 4) * (1 - 0.3 * ease('inout', (f - 25) / 40))
    env = math.exp(-((x - c) / 210) ** 2)
    return 540 - amp * env * math.sin((x - c) / 112 * math.tau + min(f, 25) * 0.32)
sp = wave.data.splines[0]
for f in range(1, 70):
    for i, p in enumerate(sp.points):
        x, y, z = px(xs[i], packet_y(xs[i], f) if f >= 4 else 540)
        p.co = (x, y, z, 1); p.keyframe_insert('co', frame=f)

# --- the fan from D2: six labelled threads plus decor strands that run off frame
TARGETS = {'mail': (672, -684), 'chat': (1344, -414), 'cal': (2368, -450), 'doc': (608, 324), 'code': (1440, 486), 'term': (2560, 630)}
DECOR = [(3500, -1000), (3300, 160), (3050, 1050), (1900, 1150), (2700, -120), (900, -1100)]
fans = []
def fan(name, dx, dy, f0, width=2.0):
    tx, ty = D2[0] + dx, D2[1] + dy
    wob = rnd.uniform(-0.35, 0.35) * abs(dy) + rnd.uniform(-120, 120)
    h0 = ((D2[0] - 10, D2[1]), (D2[0] + dx * 0.32, D2[1] + wob))
    h1 = ((tx - dx * 0.38, ty - dy * 0.05), (tx + 10, ty))
    c = curve_obj(name, [D2, (tx, ty)], width, line_mat, z=-0.01, handles=[h0, h1])
    c.data.bevel_factor_end = 0.0
    tween(c.data, 'bevel_factor_end', f0, 0.0, f0 + 20, 1.0, 'SINE', 'EASE_IN_OUT')
    fans.append(c)
    return c, (tx, ty)
ends = {}
for i, (nm, (dx, dy)) in enumerate(TARGETS.items()):
    _, ends[nm] = fan('fan_' + nm, dx, dy, 27 + i * 2)
for i, (dx, dy) in enumerate(DECOR):
    fan(f'fan_x{i}', dx, dy, 26 + i * 2, 1.6)

# --- end dots and labels
tips = {}
for i, (nm, (tx, ty)) in enumerate(ends.items()):
    d = disc('tip_' + nm, tx, ty, 6, WHITE, z=0.02)
    d.data.materials[0] = solid_emit('tip_m' + nm, WHITE, 1.3)
    sx = d.scale.x
    key(d, 'scale', 1, 0.0, 'CONSTANT', index=0); key(d, 'scale', 1, 0.0, 'CONSTANT', index=1)
    for idx in (0, 1):
        key(d, 'scale', 44 + i, 0.0, 'BACK', 'EASE_OUT', index=idx); key(d, 'scale', 49 + i, sx, 'BACK', 'EASE_OUT', index=idx)
    tips[nm] = d
LABEL_T = {'mail': 57, 'chat': 64, 'doc': 86, 'code': 90, 'cal': 93, 'term': 96}  # when each starts typing
labels = []
for j, (nm, (tx, ty)) in enumerate(ends.items()):
    up = ty < 540
    icx, icy = tx - 8, ty - 54 if up else ty + 54
    lab = seq_plane('lab_' + nm, SEQD('lab_' + nm), LABEL_T[nm], N, icx + 348, icy, z=0.04 + 0.005 * j, w=760, h=120)
    opacity(lab, [(1, 0.0), (44 + j, 0.0), (52 + j, 1.0), (130 + j, 1.0), (135 + j, 0.0)], 'LINEAR')
    labels.append(lab)

# --- camera: whip after the dot, ride the line, pan to the fan, two close-ups (cuts), a wide hold
cam_at(cam, 1, 960, 540, 1.0)
cam_at(cam, 7, D1[0] + 640, 540, 1.0, 'EXPO', 'EASE_IN_OUT')
cam_at(cam, 25, D1[0] + 700, 540, 1.0, 'LINEAR')
cam_at(cam, 26, D1[0] + 700, 540, 1.0, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 46, D2[0] + 390, 540, 1.04, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 55, D2[0] + 470, 520, 1.08, 'CONSTANT')
cam_at(cam, 55.6, D2[0] + 1110, -70, 1.7, 'LINEAR')           # cut: close-up on mail and chat (cuts sit between frames)
cam_at(cam, 83, D2[0] + 1170, -76, 1.78, 'CONSTANT')
cam_at(cam, 83.6, D2[0] + 1070, 1000, 1.7, 'LINEAR')           # cut: close-up on doc and code
cam_at(cam, 99, D2[0] + 1120, 994, 1.78, 'CONSTANT')
WIDE = (D2[0] + 1344, 540)
cam_at(cam, 99.6, *WIDE, 0.6, 'LINEAR')               # cut: wide
cam_at(cam, 130, WIDE[0] + 20, 540, 0.63, 'SINE', 'EASE_IN_OUT')

# --- unravel: the threads pull back into D2, the end dots fly to a ring that spins faster and faster
for c in fans:
    key(c.data, 'bevel_factor_end', 131, 1.0, 'SINE', 'EASE_IN_OUT'); key(c.data, 'bevel_factor_end', 141, 0.0, 'SINE', 'EASE_IN_OUT')
RC = WIDE; R = 380.0
def spin(f):  # ring angle: slow drift, then a fast whip that smears the dots into dashes
    return 0.25 * (f - 133) / 30 + 2.6 * ease('in', (f - 147) / 11) + 0.9 * ease('out', (f - 158) / 14)
for i, (nm, d) in enumerate(tips.items()):
    a0 = math.radians(90 + 60 * i)
    start = ends[nm]
    for f in range(132, 160):
        k = ease('expoinout', (f - 133) / 13)
        a = a0 + spin(f)
        x = start[0] + (RC[0] + math.cos(a) * R - start[0]) * k
        y = start[1] + (RC[1] - math.sin(a) * R - start[1]) * k
        d.location = px(x, y, 0.02); d.keyframe_insert('location', frame=f)
        sc = (6 + 7 * k) / 6
        d.scale = (sc, sc, 1); d.keyframe_insert('scale', frame=f)
    visible(d, [(1, True), (153, False)])
cam_at(cam, 136, WIDE[0] + 20, 540, 0.63, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 160, *RC, 1.0, 'SINE', 'EASE_IN_OUT')

# dashes: six arcs that grow from dot-length to closing the ring while it spins
arc_mat = solid_emit('arc', hexc('#f4f6f8'), 1.25)
arcs = []
for i in range(6):
    cd = bpy.data.curves.new(f'arc{i}', 'CURVE'); cd.dimensions = '3D'
    cd.bevel_depth = 13 * U; cd.bevel_resolution = 4; cd.resolution_u = 64
    cd.bevel_factor_mapping_start = cd.bevel_factor_mapping_end = 'SPLINE'
    sp = cd.splines.new('POLY'); M = 96; sp.points.add(M - 1)
    for j, p in enumerate(sp.points):
        a = j / (M - 1) * math.tau
        p.co = (math.cos(a) * R * U, math.sin(a) * R * U, 0, 1)
    ob = bpy.data.objects.new(f'arc{i}', cd); s.collection.objects.link(ob); ob.data.materials.append(arc_mat)
    ob.location = px(*RC, 0.02)
    for f in range(150, 176):
        L_ = 0.012 + (1 / 6 - 0.012) * ease('inout', (f - 152) / 7)  # fraction of a full turn
        a = math.radians(90 + 60 * i) + spin(f)
        cd.bevel_factor_start = 0.0; cd.bevel_factor_end = L_
        cd.keyframe_insert('bevel_factor_end', frame=f)
        ob.rotation_euler = (0, 0, -a - L_ * math.pi); ob.keyframe_insert('rotation_euler', frame=f)
    visible(ob, [(1, False), (152, True), (162, False)])
    arcs.append(ob)

# grey flash with dark rays leaking through the gaps, then the room goes light
wbg = s.world.node_tree.nodes['Background'].inputs[0]
for f, c in ((1, '#050608'), (152, '#050608'), (154, '#55585d'), (157, '#b9bdc2'), (161, '#dfe2e6'), (200, '#e6e9ed'), (214, '#f4f7fa')):
    wbg.default_value = hexc(c); wbg.keyframe_insert('default_value', frame=f)
rays = plane('rays', LB('rays'), RC[0], RC[1], z=-0.6, w=2600, h=1460)
opacity(rays, [(1, 0.0), (152, 0.0), (154, 0.85), (158, 0.6), (163, 0.0)], 'LINEAR')
key(rays, 'rotation_euler', 152, 0.0, 'LINEAR', index=2); key(rays, 'rotation_euler', 163, -0.9, 'LINEAR', index=2)

# --- the glossy torus and its echoes
G = lambda h: hexc(h)
ring_mat = glossy_ring_mat('ring', [(0.0, G('#0b5b35')), (0.18, G('#1f9a5c')), (0.36, G('#9ff0c4')), (0.5, G('#2fae6c')),
                                    (0.72, G('#0e6b3f')), (0.88, G('#5fd39a')), (1.0, G('#0b5b35'))])
sweep = ring_mat.node_tree.nodes['sweep'].inputs['Rotation']
for f, a in ((150, 0.0), (221, -5.5)):
    sweep.default_value[2] = a; sweep.keyframe_insert('default_value', index=2, frame=f)
def torus(name, scale=1.0):
    bpy.ops.mesh.primitive_torus_add(major_radius=R * U, minor_radius=24 * U, major_segments=160, minor_segments=36)
    t = bpy.context.active_object; t.name = name
    bpy.ops.object.shade_smooth()
    t.data.materials.append(ring_mat); t.location = px(*RC, 0.0)
    return t
tor = torus('torus')
visible(tor, [(1, False), (160, True)])
for idx in (0, 1, 2):
    key(tor, 'scale', 160, 0.97, 'SINE', 'EASE_OUT', index=idx); key(tor, 'scale', 166, 1.0, 'SINE', 'EASE_OUT', index=idx)
for idx, v in ((0, math.radians(24)), (1, math.radians(-14))):
    key(tor, 'rotation_euler', 178, 0.0, 'EXPO', 'EASE_IN_OUT', index=idx); key(tor, 'rotation_euler', 192, v, 'EXPO', 'EASE_IN_OUT', index=idx)
    key(tor, 'rotation_euler', 205, v * 0.4, 'SINE', 'EASE_IN_OUT', index=idx)
for i, (f0, big) in enumerate(((181, 1.42), (184, 1.95), (187, 2.7), (190, 3.8))):
    e = torus(f'echo{i}')
    e.rotation_euler = (math.radians(24 - 4 * i), math.radians(-14 + 3 * i), 0)
    visible(e, [(1, False), (f0, True)])
    for idx in (0, 1, 2):
        key(e, 'scale', f0, 1.0, 'EXPO', 'EASE_OUT', index=idx); key(e, 'scale', f0 + 16, big, 'EXPO', 'EASE_OUT', index=idx)
        key(e, 'scale', 214, big * 1.6, 'SINE', 'EASE_IN', index=idx)
for idx in (0, 1, 2):
    key(tor, 'scale', 200, 1.0, 'SINE', 'EASE_IN', index=idx); key(tor, 'scale', 214, 2.2, 'SINE', 'EASE_IN', index=idx)

# inner disc: black, then fades through grey to white as we dive in
disc_m = solid_emit('inner', hexc('#030405'), 1.0)
bpy.ops.mesh.primitive_circle_add(vertices=128, radius=(R - 22) * U, fill_type='NGON')
inner = bpy.context.active_object; inner.name = 'inner'; inner.location = px(*RC, -0.03); inner.data.materials.append(disc_m)
for idx in (0, 1):
    key(inner, 'scale', 1, 0.0, 'CONSTANT', index=idx); key(inner, 'scale', 156, 0.0, 'BACK', 'EASE_OUT', index=idx)
    key(inner, 'scale', 162, 1.0, 'BACK', 'EASE_OUT', index=idx)
    key(inner, 'scale', 200, 1.0, 'SINE', 'EASE_IN', index=idx); key(inner, 'scale', 214, 2.2, 'SINE', 'EASE_IN', index=idx)
ic = disc_m.node_tree.nodes['Emission'].inputs['Color']
for f, c in ((186, '#030405'), (190, '#4a4d52'), (194, '#bfc3c8'), (198, '#f2f5f8')):
    ic.default_value = hexc(c); ic.keyframe_insert('default_value', frame=f)
key(inner, 'rotation_euler', 178, 0.0, 'EXPO', 'EASE_IN_OUT', index=0); key(inner, 'rotation_euler', 192, math.radians(24), 'EXPO', 'EASE_IN_OUT', index=0)
key(inner, 'rotation_euler', 205, math.radians(10), 'SINE', 'EASE_IN_OUT', index=0)

# backdrop that catches the torus shadow, and the lights
bpy.ops.mesh.primitive_plane_add(size=1); bd = bpy.context.active_object; bd.name = 'backdrop'
bd.scale = (60, 40, 1); bd.location = (px(*RC)[0], px(*RC)[1], -2.2)
bm = bpy.data.materials.new('backdrop'); bm.use_nodes = True
bsdf = bm.node_tree.nodes['Principled BSDF']; bsdf.inputs['Base Color'].default_value = hexc('#e9ecf0'); bsdf.inputs['Roughness'].default_value = 0.9
bd.data.materials.append(bm)
bd_on = bm.node_tree.nodes['Principled BSDF'].inputs['Alpha']
for f, v in ((1, 0.0), (155, 0.0), (160, 1.0)):
    bd_on.default_value = v; bd_on.keyframe_insert('default_value', frame=f)
if hasattr(bm, 'surface_render_method'): bm.surface_render_method = 'DITHERED'
def area(name, loc, energy, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = color
    lo = bpy.data.objects.new(name, ld); s.collection.objects.link(lo); lo.location = loc
    lo.rotation_euler = (0, 0, 0)
    tr = lo.constraints.new('TRACK_TO'); tr.target = tor; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    return lo
cx_, cy_, _ = px(*RC)
key_l = area('key', (cx_ - 2.5, cy_ + 3.0, 6.0), 300, 5.0)
rim_l = area('rim', (cx_ + 3.5, cy_ - 2.0, 3.0), 180, 3.0, (0.75, 1.0, 0.88))
for f, (dx, dy) in ((160, (-2.5, 3.0)), (221, (3.0, 2.5))):
    key_l.location = (cx_ + dx, cy_ + dy, 6.0); key_l.keyframe_insert('location', frame=f)
for ob in (key_l, rim_l):
    ob.data.energy = 0.0; ob.data.keyframe_insert('energy', frame=158)
key_l.data.energy = 300; key_l.data.keyframe_insert('energy', frame=160)
rim_l.data.energy = 180; rim_l.data.keyframe_insert('energy', frame=160)

# "remembered." types in the black disc, then turns dark on white; it rides with the camera
rem_w = seq_plane('rem_w', SEQD('rem_w'), 157, N, 960, 540, z=0.1, w=480, h=90)
rem_k = plane('rem_k', LB('rem_k'), 960, 540, z=0.105, w=480, h=90)
for ob in (rem_w, rem_k): parent_keep(ob, cam)
# parent_keep used the camera's frame-1 pose; re-seat both at the camera's pose when they appear
s.frame_set(160)
for d, ob in ((3.0, rem_w), (2.96, rem_k)):  # held d units in front of the lens, scaled to read as if at 10:
    ob.parent = None                           # nearer than anything the camera pushes toward, never the same depth
    ob.location = (cam.location.x, cam.location.y, cam.location.z - d)
    ob.scale = (480 * U * d / CAM_Z, 90 * U * d / CAM_Z, 1)
    parent_keep(ob, cam)
opacity(rem_w, [(1, 0.0), (156, 0.0), (157, 1.0), (190, 1.0), (194, 0.0)], 'LINEAR')
opacity(rem_k, [(1, 0.0), (189, 0.0), (194, 1.0), (214, 1.0), (220, 0.0)], 'LINEAR')

# the dive: a push that tilts with the torus
cam_at(cam, 178, *RC, 1.04, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 206, RC[0] + 30, RC[1] - 20, 1.55, 'EXPO', 'EASE_IN')
cam_at(cam, 221, RC[0] + 30, RC[1] - 20, 1.6, 'SINE', 'EASE_OUT')
dof(cam, CAM_Z, 2.8)
cam.data.dof.use_dof = False  # flat graphics until the 3D part; switched on for the dive
cam.data.dof.keyframe_insert('use_dof', frame=1) if hasattr(cam.data.dof, 'keyframe_insert') else None

if __name__ == '__main__':
    a = argv()
    render(os.path.join(HERE, '..', 'frames', 'B'), [int(x) for x in a[0].split(',')] if a else None)
