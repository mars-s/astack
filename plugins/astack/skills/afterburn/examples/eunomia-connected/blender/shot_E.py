# Scene E+F (film 13.33 to 15.73 s, 72 frames). The send button shrinks and its arrow sweeps round as twelve
# poster cards fire out of it one after another and swing clockwise into a pinwheel over pulsing water ripples.
# The pinwheel turns, then bursts outward to reveal soft sky where "Recalled." pops in letter by letter, and a
# three-frame glitch (selection block, white block, sliced words) hands over to the editor.
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, '..', 'layers', 'out', 'E')
LE = lambda n: os.path.join(OUT, n + '.png')
N = 72
s, cam = reset(N, world=hexc('#e9f4fb')[:3], samples=48)
compositor(bloom=0.25, threshold=1.3, size=6)
C = (960, 540)

# where scene D left off: its last frame as a plate, fading under the ripples
plate = plane('plate', os.path.join(HERE, '..', 'frames', 'D', 'f_0100.png'), 960, 540, z=-1.2, w=1920, h=1080)
opacity(plate, [(1, 1.0), (3, 1.0), (10, 0.0)], 'LINEAR')

# ripples: concentric soft bands moving outward, white at the centre (screen-space shader)
bpy.ops.mesh.primitive_plane_add(size=1); rip = bpy.context.active_object; rip.name = 'ripples'
rip.scale = (1920 * U * 1.25, 1080 * U * 1.25, 1); rip.location = (0, 0, -2.5)
m = bpy.data.materials.new('ripples'); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; Lk = nt.links
for q in list(n): n.remove(q)
out = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission')
tc = n.new('ShaderNodeTexCoord'); sep = n.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Window'], sep.inputs[0])
dx = n.new('ShaderNodeMath'); dx.operation = 'SUBTRACT'; dx.inputs[1].default_value = 0.5; Lk.new(sep.outputs['X'], dx.inputs[0])
dxs = n.new('ShaderNodeMath'); dxs.operation = 'MULTIPLY'; dxs.inputs[1].default_value = 16 / 9; Lk.new(dx.outputs[0], dxs.inputs[0])
dy = n.new('ShaderNodeMath'); dy.operation = 'SUBTRACT'; dy.inputs[1].default_value = 0.5; Lk.new(sep.outputs['Y'], dy.inputs[0])
cmb = n.new('ShaderNodeCombineXYZ'); Lk.new(dxs.outputs[0], cmb.inputs['X']); Lk.new(dy.outputs[0], cmb.inputs['Y'])
ln = n.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; Lk.new(cmb.outputs[0], ln.inputs[0])
fr = n.new('ShaderNodeMath'); fr.operation = 'MULTIPLY'; fr.inputs[1].default_value = 19.0; Lk.new(ln.outputs['Value'], fr.inputs[0])
ph = n.new('ShaderNodeValue'); ph.name = 'phase'
sub = n.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'; Lk.new(fr.outputs[0], sub.inputs[0]); Lk.new(ph.outputs[0], sub.inputs[1])
sn = n.new('ShaderNodeMath'); sn.operation = 'SINE'; Lk.new(sub.outputs[0], sn.inputs[0])
band = n.new('ShaderNodeMapRange'); band.inputs['From Min'].default_value = -1; band.inputs['From Max'].default_value = 1
band.interpolation_type = 'SMOOTHSTEP'; Lk.new(sn.outputs[0], band.inputs['Value'])
c1 = n.new('ShaderNodeMix'); c1.data_type = 'RGBA'; Lk.new(band.outputs['Result'], c1.inputs['Factor'])
c1.inputs['A'].default_value = hexc('#cfe9fa'); c1.inputs['B'].default_value = hexc('#86c8f0')
cw = n.new('ShaderNodeMapRange'); cw.interpolation_type = 'SMOOTHSTEP'
cw.inputs['From Min'].default_value = 0.3; cw.inputs['From Max'].default_value = 0.12; Lk.new(ln.outputs['Value'], cw.inputs['Value'])
c2 = n.new('ShaderNodeMix'); c2.data_type = 'RGBA'; Lk.new(cw.outputs['Result'], c2.inputs['Factor'])
Lk.new(c1.outputs['Result'], c2.inputs['A']); c2.inputs['B'].default_value = (1, 1, 1, 1)
on = n.new('ShaderNodeMix'); on.name = 'on'; on.data_type = 'RGBA'; on.inputs['A'].default_value = hexc('#e9f4fb')
Lk.new(c2.outputs['Result'], on.inputs['B']); Lk.new(on.outputs['Result'], em.inputs['Color']); Lk.new(em.outputs[0], out.inputs['Surface'])
rip.data.materials.append(m)
keys_socket(ph.outputs[0], nt, [(1, 0.0), (N, 26.0)], 'LINEAR')
keys_socket(on.inputs['Factor'], nt, [(1, 0.0), (6, 1.0), (40, 1.0), (49, 0.0)], 'LINEAR')

# the sky that the cards part to reveal
sky = plane('sky', LE('sky'), 960, 540, z=-1.0, w=1920, h=1080)
opacity(sky, [(1, 0.0), (41, 0.0), (49, 1.0)], 'LINEAR')

# hub: white glow, the button and its arrow
hub = plane('hubglow', LE('hubglow'), 960, 540, z=0.2, w=470)
opacity(hub, [(1, 0.0), (4, 0.0), (10, 1.0), (40, 1.0), (46, 0.0)], 'LINEAR')
btn = plane('btn', LE('btn'), 960, 540, z=0.5, w=260)
arw = plane('arrow', LE('arrow'), 960, 540, z=0.52, w=260)
for ob in (btn, arw):
    sx, sy = ob.scale.x, ob.scale.y
    for idx, v in ((0, sx), (1, sy)):
        key(ob, 'scale', 1, v, 'EXPO', 'EASE_OUT', index=idx); key(ob, 'scale', 12, v * 0.5, 'EXPO', 'EASE_OUT', index=idx)
    y0 = ob.location.y
    key(ob, 'location', 40, y0, 'EXPO', 'EASE_IN', index=1); key(ob, 'location', 47, y0 + 2.6, 'EXPO', 'EASE_IN', index=1)
key(arw, 'rotation_euler', 2, 0.0, 'SINE', 'EASE_IN_OUT', index=2); key(arw, 'rotation_euler', 30, -math.tau, 'SINE', 'EASE_IN_OUT', index=2)

# the cards: each fires from the hub and swings clockwise to its slot; the whole wheel turns, then bursts
wheel = bpy.data.objects.new('wheel', None); s.collection.objects.link(wheel); wheel.location = px(*C, 0.0)
R, NC = 430, 12
for i in range(NC):
    th = math.radians(90 - i * 30)
    cd = plane(f'card{i + 1:02d}', LE(f'card{i + 1:02d}'), 960, 540, z=0.02 + 0.012 * i, w=560, h=300)
    z0 = cd.location.z
    cd.parent = wheel; cd.location = (0, 0, z0)
    sx, sy = cd.scale.x, cd.scale.y
    L0 = 3 + 1.4 * i
    visible(cd, [(1, False), (int(L0), True)])
    for f in range(int(L0), int(L0) + 11):
        u = ease('out', (f - L0) / 9.0)
        a = th + math.radians(150) * (1 - u)
        r = (60 + (R - 60) * u) * U
        sc = 0.35 + 0.65 * u
        cd.location = (math.cos(a) * r, math.sin(a) * r, z0); cd.keyframe_insert('location', frame=f)
        cd.rotation_euler = (0, 0, a + math.radians(12) * u); cd.keyframe_insert('rotation_euler', frame=f)
        cd.scale = (sx * sc, sy * sc, 1); cd.keyframe_insert('scale', frame=f)
key(wheel, 'rotation_euler', 8, 0.0, 'SINE', 'EASE_OUT', index=2); key(wheel, 'rotation_euler', 46, math.radians(-16), 'SINE', 'EASE_OUT', index=2)
for idx in (0, 1):
    key(wheel, 'scale', 40, 1.0, 'EXPO', 'EASE_IN', index=idx); key(wheel, 'scale', 50, 3.4, 'EXPO', 'EASE_IN', index=idx)
    key(wheel, 'scale', 58, 7.0, 'SINE', 'EASE_OUT', index=idx)

# "Recalled." pops in, then the glitch frames
rec = seq_plane('recalled', os.path.join(OUT, 'recalled'), 47, N, 960, 540, z=0.8, w=900, h=200)
visible(rec, [(1, False), (47, True), (67, False)])
for nm, a, b in (('gl_sel', 67, 68), ('gl_white', 68, 69), ('gl_slice', 69, 71), ('gl_slice2', 71, 73)):
    g = plane(nm, LE(nm), 960, 540, z=0.9, w=900, h=200)
    visible(g, [(1, False), (a, True), (b, False)])

if __name__ == '__main__':
    a = argv()
    render(os.path.join(HERE, '..', 'frames', 'E'), [int(x) for x in a[0].split(',')] if a else None)
