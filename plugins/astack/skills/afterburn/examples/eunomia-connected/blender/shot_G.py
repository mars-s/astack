# Scene G (film 15.73 to 21.00 s, 159 frames). Frosted glass over a misty forest turns into a code editor that
# writes itself in bursts while it floats. Cut to a tilted close-up: lines tick green, the client-secret line goes
# red and the whole forest flushes red and flickers, a block cursor scrambles the line and memory replaces it with
# the team's decision. Cut wide: the editor rises in with every line ticked and a voxel cube turning beside the
# code. One inverted frame hands over to the paper.
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, '..', 'layers', 'out', 'G')
ART = os.path.join(HERE, '..', '..')
N = 159
s, cam = reset(N, world=hexc('#1d2a22')[:3], samples=48)
ng, glare = compositor(bloom=0.3, threshold=1.25, size=6)

# one inverted frame at the end (compositor invert keyed on for a single frame)
n, Lk = ng.nodes, ng.links
inv = n.new('CompositorNodeInvert')
out = [x for x in n if x.bl_idname in ('NodeGroupOutput', 'CompositorNodeComposite')][0]
Lk.new(glare.outputs['Image'], inv.inputs['Color'])
Lk.new(inv.outputs[0], out.inputs[0])
fac = inv.inputs['Factor']
for f, v in ((1, 0.0), (157, 0.0), (158, 1.0), (159, 0.0)):
    fac.default_value = v; fac.keyframe_insert('default_value', frame=f)
from lib import _fcurves
for fc in _fcurves(ng.animation_data):
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# the forest, far back so focus softens it; it flushes red and flickers while the error is on screen
FOREST = os.path.join(ART, 'footage', 'forest.mp4') if os.path.exists(os.path.join(ART, 'footage', 'forest.mp4')) else os.path.join(ART, 'forest.jpg')
forest = photo_plane('forest', FOREST, z=-6.0, w=2500, h=1406)
red = [(1, 0.0), (63, 0.0), (64, 0.88), (67, 0.62), (69, 0.9), (73, 0.7), (76, 0.9), (82, 0.78), (88, 0.92), (95, 0.74), (101, 0.9), (104, 0.0)]
node_keys(forest, 'grade', 'Factor', red, 'CONSTANT')

# the editor: one sequence whose frame is the scene frame
ed = seq_plane('editor', os.path.join(OUT, 'editor'), 1, N, 960, 540, z=0.0, w=1240, h=720)
ex, ey, ez = ed.location
for f, rx, ry, dy in ((1, 5, -7, 0.0), (25, 1, -2, 0.06), (50, -2, 3, 0.0)):
    key(ed, 'rotation_euler', f, math.radians(rx), 'SINE', 'EASE_IN_OUT', index=0)
    key(ed, 'rotation_euler', f, math.radians(ry), 'SINE', 'EASE_IN_OUT', index=1)
    key(ed, 'location', f, ey + dy, 'SINE', 'EASE_IN_OUT', index=1)
# close-up: tilt for perspective
key(ed, 'rotation_euler', 50.6, math.radians(-4), 'CONSTANT', index=0); key(ed, 'rotation_euler', 50.6, math.radians(8), 'SINE', 'EASE_IN_OUT', index=1)
key(ed, 'rotation_euler', 116, math.radians(-2), 'CONSTANT', index=0); key(ed, 'rotation_euler', 116, math.radians(5), 'CONSTANT', index=1)
key(ed, 'location', 50.6, ey, 'CONSTANT', index=1); key(ed, 'location', 116, ey, 'CONSTANT', index=1)
# wide again: the editor rises in from below, then floats
key(ed, 'rotation_euler', 116.6, math.radians(6), 'EXPO', 'EASE_OUT', index=0); key(ed, 'rotation_euler', 116.6, math.radians(-4), 'EXPO', 'EASE_OUT', index=1)
key(ed, 'location', 116.6, ey - 2.9, 'EXPO', 'EASE_OUT', index=1)
key(ed, 'location', 129, ey, 'EXPO', 'EASE_OUT', index=1)
key(ed, 'rotation_euler', 130, math.radians(2), 'SINE', 'EASE_IN_OUT', index=0); key(ed, 'rotation_euler', 130, math.radians(-2), 'SINE', 'EASE_IN_OUT', index=1)
key(ed, 'rotation_euler', 159, math.radians(-1), 'SINE', 'EASE_IN_OUT', index=0); key(ed, 'rotation_euler', 159, math.radians(3), 'SINE', 'EASE_IN_OUT', index=1)
key(ed, 'location', 159, ey + 0.05, 'SINE', 'EASE_IN_OUT', index=1)

# camera: wide drift, cut to close-up, cut back wide
cam_at(cam, 1, 960, 540, 0.98, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 50, 960, 548, 1.05, 'CONSTANT')
cam_at(cam, 50.6, 790, 470, 1.72, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 116, 822, 482, 1.84, 'CONSTANT')
cam_at(cam, 116.6, 960, 540, 1.0, 'SINE', 'EASE_IN_OUT')
cam_at(cam, 159, 962, 540, 1.04, 'LINEAR')
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 2.4
cam.data.dof.keyframe_insert('aperture_fstop', frame=50)
cam.data.dof.aperture_fstop = 1.3; cam.data.dof.keyframe_insert('aperture_fstop', frame=50.6)
cam.data.dof.keyframe_insert('aperture_fstop', frame=116)
cam.data.dof.aperture_fstop = 2.4; cam.data.dof.keyframe_insert('aperture_fstop', frame=116.6)
for fc in _fcurves(cam.data.animation_data):
    if 'fstop' in fc.data_path:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# the voxel cube beside the code
vmat = bpy.data.materials.new('voxel'); vmat.use_nodes = True
vn = vmat.node_tree.nodes; vl = vmat.node_tree.links
bs = vn['Principled BSDF']; oi = vn.new('ShaderNodeObjectInfo')
vl.new(oi.outputs['Color'], bs.inputs['Base Color']); vl.new(oi.outputs['Color'], bs.inputs['Emission Color'])
bs.inputs['Emission Strength'].default_value = 0.85; bs.inputs['Roughness'].default_value = 0.35
root = bpy.data.objects.new('voxroot', None); s.collection.objects.link(root)
root.location = px(1330, 520, 0.45)
bpy.ops.mesh.primitive_cube_add(size=1); proto = bpy.context.active_object; proto.name = 'vox_proto'
proto.data.materials.append(vmat); proto.hide_render = True; proto.hide_viewport = True
NV, CELL = 9, 31 * U
stops = [(0.0, hexc('#0f6b3f')), (0.35, hexc('#1fa86a')), (0.65, hexc('#2fc0b4')), (1.0, hexc('#8a5ad8'))]
def ramp(t):
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            k = (t - p0) / (p1 - p0)
            return tuple(c0[i] + (c1[i] - c0[i]) * k for i in range(4))
    return stops[-1][1]
for i in range(NV):
    for j in range(NV):
        for k in range(NV):
            if 0 < i < NV - 1 and 0 < j < NV - 1 and 0 < k < NV - 1: continue
            v = bpy.data.objects.new(f'vox_{i}_{j}_{k}', proto.data); s.collection.objects.link(v)
            v.parent = root
            c = (NV - 1) / 2
            v.location = ((i - c) * CELL, (j - c) * CELL, (k - c) * CELL)
            v.scale = (CELL * 0.74,) * 3
            v.color = ramp((i + j + (NV - 1 - k)) / (3 * (NV - 1)))
visible(root, [(1, False), (118, True)])
for v in [o for o in s.objects if o.name.startswith('vox_') and o.name != 'vox_proto']:
    visible(v, [(1, False), (118, True)])
for idx in (0, 1, 2):
    key(root, 'scale', 118, 0.05, 'EXPO', 'EASE_OUT', index=idx); key(root, 'scale', 130, 1.0, 'EXPO', 'EASE_OUT', index=idx)
key(root, 'rotation_euler', 118, math.radians(28), 'LINEAR', index=0)
key(root, 'rotation_euler', 118, math.radians(20), 'LINEAR', index=1); key(root, 'rotation_euler', 159, math.radians(85), 'LINEAR', index=1)
ld = bpy.data.lights.new('voxkey', 'AREA'); ld.energy = 120; ld.size = 3
lo = bpy.data.objects.new('voxkey', ld); s.collection.objects.link(lo); lo.location = (root.location.x - 1.5, root.location.y + 2.5, 4.0)
tr = lo.constraints.new('TRACK_TO'); tr.target = root; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'

if __name__ == '__main__':
    a = argv()
    render(os.path.join(HERE, '..', 'frames', 'G'), [int(x) for x in a[0].split(',')] if a else None)
