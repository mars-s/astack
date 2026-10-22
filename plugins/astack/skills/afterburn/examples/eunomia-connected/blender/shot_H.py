# Scene H (film 21.00 to 27.00 s, 180 frames). A navy glitch frame, then warm paper where the things Eunomia
# remembers float as labels at many depths while the camera trucks past (focus picks out a few). The camera pulls
# back as the labels settle onto the tips of a tree that is not there yet; the painted tree grows out from the
# trunk to meet them and each dot glows as its branch arrives. A rack focus, the paper warms, leaves and blossoms
# pop along the branches outward, yellow leaves drift down and the tree sways.
import sys, os, math, json, random
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from lib import _fcurves
import numpy as np

HERE = os.path.dirname(__file__)
V2 = os.path.join(HERE, '..')
OUT = os.path.join(V2, 'layers', 'out', 'H')
LH = lambda n: os.path.join(OUT, n + '.png')
N = 180
s, cam = reset(N, world=hexc('#efe6d3')[:3], samples=48)
compositor(bloom=0.25, threshold=1.3, size=6)
rnd = random.Random(5)

# --- tree placement: image px -> screen px
TS, TX, TY = 1.1, -40, 40
tip_data = json.load(open(os.path.join(V2, 'tree_tips.json')))
IW, IH = tip_data['w'], tip_data['h']
scr = lambda x, y: (TX + x * TS, TY + y * TS)

# paper, with a warm grade that comes in after the rack focus
paper = photo_plane('paper', os.path.join(V2, '..', 'paper.jpg'), z=-0.4, w=2400, h=1350)
node_keys(paper, 'grade', 'B', [(1, (1.0, 0.86, 0.55, 1.0))], 'CONSTANT')
node_keys(paper, 'grade', 'Factor', [(1, 0.0), (106, 0.0), (116, 0.3)], 'SINE', 'EASE_IN_OUT')

sway = bpy.data.objects.new('sway', None); s.collection.objects.link(sway); sway.location = px(*scr(80, 1010))

# --- the tree, revealed by its growth map
tree_img = bpy.data.images.load(os.path.join(V2, 'tree_rgba.png'))
grow_img = bpy.data.images.load(os.path.join(V2, 'tree_grow.png')); grow_img.colorspace_settings.name = 'Non-Color'
bpy.ops.mesh.primitive_plane_add(size=1); tree = bpy.context.active_object; tree.name = 'tree'
cx, cy = scr(IW / 2, IH / 2)
tree.scale = (IW * TS * U, IH * TS * U, 1); tree.location = px(cx, cy, 0.0)
m = bpy.data.materials.new('tree'); m.use_nodes = True; m.surface_render_method = 'DITHERED'
nt = m.node_tree; n = nt.nodes; Lk = nt.links
for q in list(n): n.remove(q)
o = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission'); tr = n.new('ShaderNodeBsdfTransparent'); mx = n.new('ShaderNodeMixShader')
ti = n.new('ShaderNodeTexImage'); ti.image = tree_img; ti.interpolation = 'Cubic'
gi = n.new('ShaderNodeTexImage'); gi.image = grow_img; gi.interpolation = 'Linear'
T = n.new('ShaderNodeValue'); T.name = 'T'
lo_ = n.new('ShaderNodeMath'); lo_.operation = 'SUBTRACT'; lo_.inputs[1].default_value = 0.012; Lk.new(T.outputs[0], lo_.inputs[0])
mr = n.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'
Lk.new(gi.outputs['Color'], mr.inputs['Value']); Lk.new(lo_.outputs[0], mr.inputs['From Min']); Lk.new(T.outputs[0], mr.inputs['From Max'])
mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
al = n.new('ShaderNodeMath'); al.operation = 'MULTIPLY'; Lk.new(ti.outputs['Alpha'], al.inputs[0]); Lk.new(mr.outputs['Result'], al.inputs[1])
gr = n.new('ShaderNodeMix'); gr.name = 'grade'; gr.data_type = 'RGBA'; gr.blend_type = 'MULTIPLY'; gr.inputs['B'].default_value = (1.0, 0.9, 0.7, 1)
Lk.new(ti.outputs['Color'], gr.inputs['A']); Lk.new(gr.outputs['Result'], em.inputs['Color'])
Lk.new(al.outputs[0], mx.inputs['Fac']); Lk.new(tr.outputs[0], mx.inputs[1]); Lk.new(em.outputs[0], mx.inputs[2]); Lk.new(mx.outputs[0], o.inputs['Surface'])
tree.data.materials.append(m)
G0, G1, T0, T1 = 70, 101, -0.02, 1.03
keys_socket(T.outputs[0], nt, [(1, T0), (G0, T0), (G1, T1)], 'QUAD', 'EASE_IN_OUT')
keys_socket(gr.inputs['Factor'], nt, [(1, 0.0), (106, 0.0), (116, 0.25)], 'SINE', 'EASE_IN_OUT')
parent_keep(tree, sway)
def frame_for(g):  # when the growth front passes value g
    for f10 in range(G0 * 10, G1 * 10 + 1):
        t = (f10 / 10 - G0) / (G1 - G0)
        e = 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2
        if T0 + (T1 - T0) * e >= g: return f10 / 10
    return G1

trunk = plane('trunk', LH('trunk'), *scr(232, 792), z=0.06, w=330, h=55)
trunk.rotation_euler = (0, 0, math.radians(58.7))
opacity(trunk, [(1, 0.0), (80, 0.0), (86, 1.0)], 'LINEAR')  # after the trunk has grown under it
parent_keep(trunk, sway)

# --- pick label tips: spread out, boxes not overlapping, inside the frame
tips = sorted(tip_data['tips'], key=lambda t: -t['g'])
chosen = []
for t in tips:
    x, y = scr(t['x'], t['y'])
    box = (x - 10, y - 24, x + 205, y + 50)
    if box[0] < 20 or box[2] > 1900 or box[1] < 20 or box[3] > 1060: continue
    if any(not (box[2] < b[0] or b[2] < box[0] or box[3] < b[1] or b[3] < box[1]) for _, _, _, b in chosen): continue
    chosen.append((x, y, t['g'], box))
    if len(chosen) == 20: break
print('LABELS', len(chosen))

for i, (x, y, g, _) in enumerate(chosen):
    lb = plane(f'ent{i:02d}', LH(f'ent{i:02d}'), x + 134, y + 15, z=0.05, w=300, h=90)
    fin = tuple(lb.location)
    # scatter: somewhere in depth, then settle onto the tip
    zs = rnd.uniform(-3.5, 2.8)
    sx_, sy_ = rnd.uniform(420, 1560), rnd.uniform(160, 940)  # inside the trucking camera's path
    sc = (CAM_Z - zs) / CAM_Z
    start = px(sx_, sy_, zs)
    f_in = 3 + rnd.randint(0, 16)
    f_go = 46 + (i % 6) * 2
    for idx in range(3):
        key(lb, 'location', 1, start[idx], 'EXPO', 'EASE_IN_OUT', index=idx)
        key(lb, 'location', f_go, start[idx], 'EXPO', 'EASE_IN_OUT', index=idx)
        key(lb, 'location', f_go + 18, fin[idx], 'EXPO', 'EASE_IN_OUT', index=idx)
    for idx, v in ((0, lb.scale.x), (1, lb.scale.y)):
        key(lb, 'scale', f_go, v * (1.0 + 0.4 * max(0, zs) / 2.8), 'EXPO', 'EASE_IN_OUT', index=idx); key(lb, 'scale', f_go + 18, v, 'EXPO', 'EASE_IN_OUT', index=idx)
    opacity(lb, [(1, 0.0), (f_in, 0.0), (f_in + 6, 1.0)], 'LINEAR')
    parent_keep(lb, sway)
    # the dot glows as its branch arrives
    fg = frame_for(g)
    dg = plane(f'glow{i:02d}', LH('dotglow'), x, y, z=0.09, w=90)
    visible(dg, [(1, False), (int(fg), True), (int(fg) + 10, False)])
    for idx in (0, 1):
        v = dg.scale[idx]
        key(dg, 'scale', int(fg), v * 0.3, 'EXPO', 'EASE_OUT', index=idx); key(dg, 'scale', int(fg) + 9, v * 1.5, 'EXPO', 'EASE_OUT', index=idx)
    opacity(dg, [(int(fg), 1.0), (int(fg) + 9, 0.0)], 'LINEAR')
    parent_keep(dg, sway)

# floating badges and soft colour chips that only live in the scatter phase
for i in range(6):
    zs = rnd.uniform(-2.5, 3.2)
    b = plane(f'badge{i}', LH(f'badge{i}'), rnd.uniform(450, 1500), rnd.uniform(180, 900), z=zs, w=120, h=60)
    f_in = 4 + rnd.randint(0, 24)
    opacity(b, [(1, 0.0), (f_in, 0.0), (f_in + 6, 1.0), (44, 1.0), (52, 0.0)], 'LINEAR')
for i in range(8):
    zs = rnd.uniform(-6.0, -2.0) if i % 2 else rnd.uniform(4.0, 6.5)
    c = plane(f'chip{i}', LH(f'chip{i}'), rnd.uniform(0, 1920), rnd.uniform(0, 1080), z=zs, w=140, h=70)
    opacity(c, [(1, 0.0), (3, 0.0), (8, 0.8), (40, 0.8), (50, 0.0)], 'LINEAR')

# --- leaves and blossoms along the branches, popping outward after the rack focus
ta = np.array(tree_img.pixels[:], dtype=np.float32).reshape(IH, IW, 4)[::-1]  # image rows top-down
gg = np.array(grow_img.pixels[:], dtype=np.float32).reshape(IH, IW, 4)[::-1][..., 0]
cand = np.argwhere((ta[..., 3] > 0.95) & (gg > 0.35) & (gg < 0.97))
rs = np.random.default_rng(9)
cand = cand[rs.permutation(len(cand))]
spr = json.load(open(os.path.join(V2, 'sprites', 'index.json')))
blos = [x for x in spr if x['kind'] == 'blossom']; leaves = [x for x in spr if x['kind'] == 'leaf']
placed = []
for yx in cand:
    y, x = int(yx[0]), int(yx[1])
    if any((y - py) ** 2 + (x - px_) ** 2 < 46 ** 2 for py, px_ in placed): continue
    placed.append((y, x))
    if len(placed) >= 46: break
for j, (y, x) in enumerate(placed):
    kind = blos[j % len(blos)] if j % 3 == 0 else leaves[j % len(leaves)]
    sx_, sy_ = scr(x, y)
    size = rnd.uniform(44, 64) if kind['kind'] == 'blossom' else rnd.uniform(52, 76)
    sp = plane(f'spr{j:02d}', os.path.join(V2, 'sprites', kind['file']), sx_, sy_, z=0.12 + j * 0.002, w=size)
    sp.rotation_euler = (0, 0, math.radians(rnd.uniform(-180, 180)))
    f0 = int(110 + (gg[y, x] - 0.35) * 55 + rnd.randint(0, 8))
    visible(sp, [(1, False), (f0, True)])
    for idx in (0, 1):
        v = sp.scale[idx]
        key(sp, 'scale', f0, v * 0.1, 'BACK', 'EASE_OUT', index=idx); key(sp, 'scale', f0 + 6, v, 'BACK', 'EASE_OUT', index=idx)
    parent_keep(sp, sway)

# yellow leaves drifting across
for k in range(8):
    lf = leaves[k % len(leaves)]
    x0, y0 = rnd.uniform(500, 2000), rnd.uniform(-120, 500)
    d = plane(f'fall{k}', os.path.join(V2, 'sprites', lf['file']), x0, y0, z=rnd.uniform(0.3, 2.5), w=rnd.uniform(26, 40), tint=(1.0, 0.86, 0.25, 1.0))
    f0 = 108 + rnd.randint(0, 40)
    visible(d, [(1, False), (f0, True)])
    p0 = tuple(d.location)
    p1 = (p0[0] - rnd.uniform(1.0, 2.4), p0[1] - rnd.uniform(1.2, 2.6), p0[2])
    for idx in range(2):
        key(d, 'location', f0, p0[idx], 'LINEAR', index=idx); key(d, 'location', 180, p1[idx], 'LINEAR', index=idx)
    key(d, 'rotation_euler', f0, 0.0, 'LINEAR', index=2); key(d, 'rotation_euler', 180, rnd.uniform(-5, 5), 'LINEAR', index=2)

# sway
for f, a in ((110, 0.0), (135, 0.5), (160, -0.3), (180, 0.35)):
    key(sway, 'rotation_euler', f, math.radians(a), 'SINE', 'EASE_IN_OUT', index=2)

# glitch frames at the head: navy with faint labels, then a pale frame
navy = plane('navy', LH('navy'), 960, 540, z=6.9, w=1920, h=1080)
pale = rect('pale', 960, 540, 1920, 1080, hexc('#d9dce2'), z=6.95)
for ob in (navy, pale):
    ob.parent = cam
    ob.location = (0, 0, -(CAM_Z - (6.9 if ob is navy else 6.95)))
visible(navy, [(1, True), (2, False)]); visible(pale, [(1, False), (2, True), (3, False)])
opacity(pale, [(1, 0.6)])

# --- camera: truck past the scatter, pull back to the layout, slow push; rack focus out and back
cam_at(cam, 1, 760, 560, 1.35, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 44, 1180, 520, 1.42, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 68, 960, 540, 1.0, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 180, 975, 548, 1.07, 'SINE', 'EASE_IN_OUT')
cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 1.1
s.frame_set(103); fd = cam.data.dof.focus_distance
for f, v in ((103, fd), (106, fd * 0.62), (111, fd)):
    cam.data.dof.focus_distance = v; cam.data.dof.keyframe_insert('focus_distance', frame=f)
cam.data.dof.aperture_fstop = 1.1; cam.data.dof.keyframe_insert('aperture_fstop', frame=68)
cam.data.dof.aperture_fstop = 2.2; cam.data.dof.keyframe_insert('aperture_fstop', frame=100)

# navy/pale planes ride the camera; their size must cover the view at their distance
for ob, d in ((navy, CAM_Z - 6.9), (pale, CAM_Z - 6.95)):
    ob.scale = (1920 * U * d / CAM_Z * 1.4, 1080 * U * d / CAM_Z * 1.4, 1)

if __name__ == '__main__':
    a = argv()
    render(os.path.join(HERE, '..', 'frames', 'H'), [int(x) for x in a[0].split(',')] if a else None)
