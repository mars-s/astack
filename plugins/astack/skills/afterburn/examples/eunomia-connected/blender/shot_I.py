# Scene I+J (film 27.00 to 35.00 s, 240 frames). The meadow, its flowers swaying in a gentle wind, under a sky
# where "One place to" builds word by word and remember / recall / share swap in green. The Eunomia mark draws on
# and the name types under it. Then the Paperless end card, held to the end.
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from lib import _fcurves

HERE = os.path.dirname(__file__)
V2 = os.path.join(HERE, '..')
OUT = os.path.join(V2, 'layers', 'out', 'I')
N = 240
s, cam = reset(N, world=hexc('#7fb0e0')[:3], samples=32)
compositor(bloom=0.2, threshold=1.3, size=6)

MEADOW = os.path.join(V2, '..', 'footage', 'meadow.mp4') if os.path.exists(os.path.join(V2, '..', 'footage', 'meadow.mp4')) else os.path.join(V2, '..', 'meadow.jpg')
mead = photo_plane('meadow', MEADOW, z=-1.0, w=2050, h=1153)
if MEADOW.endswith('.jpg'):  # a still: give the flowers a wind that moves only the bottom of the frame
    nt = mead.active_material.node_tree; n = nt.nodes; L = nt.links
    mp = [x for x in n if x.type == 'MAPPING'][0]; tc = [x for x in n if x.type == 'TEX_COORD'][0]
    noise = n.new('ShaderNodeTexNoise'); noise.noise_dimensions = '4D'; noise.inputs['Scale'].default_value = 7.0
    noise.inputs['Detail'].default_value = 1.5
    L.new(tc.outputs['UV'], noise.inputs['Vector'])
    w = noise.inputs['W']
    w.default_value = 0.0; w.keyframe_insert('default_value', frame=1); w.default_value = 4.0; w.keyframe_insert('default_value', frame=N)
    for fc in _fcurves(nt.animation_data):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    sub = n.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.5, 0.5, 0.5)
    L.new(noise.outputs['Color'], sub.inputs[0])
    sep = n.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['UV'], sep.inputs[0])
    mask = n.new('ShaderNodeMapRange'); mask.interpolation_type = 'SMOOTHSTEP'
    mask.inputs['From Min'].default_value = 0.42; mask.inputs['From Max'].default_value = 0.2
    L.new(sep.outputs['Y'], mask.inputs['Value'])
    amp = n.new('ShaderNodeMath'); amp.operation = 'MULTIPLY'; amp.inputs[1].default_value = 0.012
    L.new(mask.outputs['Result'], amp.inputs[0])
    sc = n.new('ShaderNodeVectorMath'); sc.operation = 'SCALE'; L.new(sub.outputs[0], sc.inputs[0]); L.new(amp.outputs[0], sc.inputs['Scale'])
    add = n.new('ShaderNodeVectorMath'); add.operation = 'ADD'; L.new(tc.outputs['UV'], add.inputs[0]); L.new(sc.outputs[0], add.inputs[1])
    L.new(add.outputs[0], mp.inputs['Vector'])

words = seq_plane('oneplace', os.path.join(OUT, 'oneplace'), 1, N, 960, 470, z=0.0, w=1000, h=140)
visible(words, [(1, True), (110, False)])
logo = seq_plane('endlogo', os.path.join(OUT, 'endlogo'), 112, N, 960, 455, z=0.0, w=700, h=360)
visible(logo, [(1, False), (112, True), (166, False)])

card = plane('endcard', os.path.join(OUT, 'endcard.png'), 960, 540, z=0.0, w=1920, h=1080)
card.parent = cam; card.location = (0, 0, -3.0); card.scale = (1920 * U * 0.3 * 1.02, 1080 * U * 0.3 * 1.02, 1)
visible(card, [(1, False), (166, True)])
opacity(card, [(166, 0.0), (172, 1.0)], 'LINEAR')

cam_at(cam, 1, 960, 540, 1.0, 'LINEAR')
cam_at(cam, 165, 960, 530, 1.07, 'LINEAR')
cam.data.dof.use_dof = True
for f, v in ((1, 5.6), (165, 5.6), (166, 128.0)):  # deep focus for the end card
    cam.data.dof.aperture_fstop = v; cam.data.dof.keyframe_insert('aperture_fstop', frame=f)
for fc in _fcurves(cam.data.animation_data):
    if 'fstop' in fc.data_path:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

if __name__ == '__main__':
    a = argv()
    render(os.path.join(HERE, '..', 'frames', 'I'), [int(x) for x in a[0].split(',')] if a else None)
