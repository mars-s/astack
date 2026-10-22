# Shared Blender toolkit for the v2 film. Every shot script imports this.
# Units: the camera sits at z=10 with a 50mm lens on a 36mm sensor, so the z=0 plane shows exactly
# 1920x1080 "px" across 7.2 x 4.05 Blender units. px() converts reel-style pixel coords (origin top-left)
# to world coords, so layouts can be written in the same numbers as the HTML layers.
import bpy, math, os, sys

FPS = 30
W, H = 1920, 1080
CAM_Z = 10.0
U = 7.2 / W  # world units per px on the z=0 plane


COMP = True  # scale positions for depth so off-plane layers line up in the rest camera; off for travelling cameras


def px(x, y, z=0.0):
    """Pixel coords (top-left origin) on the plane at depth z, as seen from the rest camera."""
    k = (CAM_Z - z) / CAM_Z if COMP else 1.0  # nearer planes need smaller offsets to land on the same pixel
    return ((x - W / 2) * U * k, (H / 2 - y) * U * k, z)


_layer = [0]
def _bump():
    """Every image plane gets its own depth. EEVEE's dithered transparency lets an invisible plane paint over
    a visible one when they share a depth exactly, so no two planes ever do."""
    _layer[0] += 1
    return _layer[0] * 0.0012


def reset(frames, world=(0, 0, 0), samples=32):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _layer[0] = 0
    s = bpy.context.scene
    s.render.engine = 'BLENDER_EEVEE'
    s.render.fps = FPS
    s.frame_start, s.frame_end = 1, frames
    s.render.resolution_x, s.render.resolution_y = W, H
    s.render.resolution_percentage = 100
    s.render.use_motion_blur = True
    s.render.motion_blur_shutter = 0.5
    s.eevee.taa_render_samples = samples
    s.view_settings.view_transform = 'Standard'  # keep brand and UI colours exact
    s.view_settings.look = 'None'
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGB'
    wd = bpy.data.worlds.new('World'); s.world = wd
    wd.use_nodes = True
    bg = wd.node_tree.nodes['Background']
    bg.inputs[0].default_value = (*world, 1)
    bg.inputs[1].default_value = 1.0
    cam_data = bpy.data.cameras.new('Cam'); cam_data.lens = 50; cam_data.sensor_width = 36
    cam_data.clip_end = 1000
    cam = bpy.data.objects.new('Cam', cam_data); s.collection.objects.link(cam)
    cam.location = (0, 0, CAM_Z)
    s.camera = cam
    return s, cam


def lin(c):
    """sRGB 0..1 to linear, for colours typed from the design tokens."""
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


def hexc(h, a=1.0):
    h = h.lstrip('#')
    return (*lin(tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))), a)


def key(obj, path, frame, value, interp='BEZIER', easing='AUTO', index=-1):
    """Set a property at a frame and keyframe it with a named interpolation (EXPO, QUART, BACK, CONSTANT...)."""
    target, attr = obj, path
    if '.' in path:
        head, attr = path.rsplit('.', 1)
        target = obj.path_resolve(head)
    if index >= 0:
        getattr(target, attr)[index] = value
    else:
        setattr(target, attr, value)
    target.keyframe_insert(attr, frame=frame, index=index)
    ad = (obj.id_data if hasattr(obj, 'id_data') else obj).animation_data
    for fc in _fcurves(ad):
        for kp in fc.keyframe_points:
            if abs(kp.co[0] - frame) < 1e-4:
                kp.interpolation = interp
                if easing != 'AUTO':
                    kp.easing = easing


def _fcurves(ad):
    if ad is None or ad.action is None:
        return []
    act = ad.action
    if hasattr(act, 'fcurves') and len(getattr(act, 'fcurves', [])):
        return act.fcurves
    out = []  # Blender 4.4+ layered actions
    for layer in getattr(act, 'layers', []):
        for strip in layer.strips:
            for cb in strip.channelbags:
                out.extend(cb.fcurves)
    return out


def tween(obj, path, f0, v0, f1, v1, interp='EXPO', easing='EASE_OUT', index=-1):
    key(obj, path, f0, v0, interp, easing, index)
    key(obj, path, f1, v1, interp, easing, index)


def emissive_image_material(name, img, strength=1.0, tint=None, additive=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    if hasattr(m, 'surface_render_method'):  # dithered writes depth, so focus blur sees the plane where it is
        m.surface_render_method = 'BLENDED' if additive else 'DITHERED'
    nt = m.node_tree; n = nt.nodes; L = nt.links
    for x in list(n): n.remove(x)
    out = n.new('ShaderNodeOutputMaterial')
    tex = n.new('ShaderNodeTexImage'); tex.image = img; tex.interpolation = 'Cubic'; tex.extension = 'CLIP'
    em = n.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = strength
    tr = n.new('ShaderNodeBsdfTransparent')
    mix = n.new('ShaderNodeMixShader')
    fade = n.new('ShaderNodeMath'); fade.operation = 'MULTIPLY'; fade.inputs[1].default_value = 1.0
    fade.label = 'opacity'; fade.name = 'opacity'
    if tint:
        mul = n.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
        mul.inputs['Factor'].default_value = 1.0
        L.new(tex.outputs['Color'], mul.inputs['A']); mul.inputs['B'].default_value = tint
        L.new(mul.outputs['Result'], em.inputs['Color'])
    else:
        L.new(tex.outputs['Color'], em.inputs['Color'])
    L.new(tex.outputs['Alpha'], fade.inputs[0])
    if additive:  # light only adds: alpha x opacity scales the emission, nothing gets covered
        n.remove(mix)
        st = n.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = strength
        L.new(fade.outputs[0], st.inputs[0]); L.new(st.outputs[0], em.inputs['Strength'])
        em.name = 'add_em'; st.name = 'add_strength'
        add = n.new('ShaderNodeAddShader')
        L.new(tr.outputs[0], add.inputs[0]); L.new(em.outputs[0], add.inputs[1])
        L.new(add.outputs[0], out.inputs['Surface'])
        return m
    L.new(fade.outputs[0], mix.inputs['Fac'])
    L.new(tr.outputs[0], mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    return m


def load_image(path, sequence_frames=0):
    img = bpy.data.images.load(path, check_existing=True)
    if sequence_frames:
        img.source = 'SEQUENCE'
    return img


def plane(name, path, x, y, z=0.0, w=None, h=None, strength=1.0, seq=0, seq_offset=0, tint=None, additive=False):
    """An image (or PNG sequence) on a plane, sized in px at its depth, centred at pixel (x, y)."""
    img = load_image(path, seq)
    iw, ih = img.size if img.size[0] else (w, h)
    if w is None and h is None: w, h = iw / 2, ih / 2  # layers are rendered at 2x
    elif h is None: h = w * ih / iw
    elif w is None: w = h * iw / ih
    z += _bump()
    k = (CAM_Z - z) / CAM_Z
    bpy.ops.mesh.primitive_plane_add(size=1)
    ob = bpy.context.active_object; ob.name = name
    ob.scale = (w * U * k, h * U * k, 1)
    ob.location = px(x, y, z)
    m = emissive_image_material(name + '_m', img, strength, tint, additive)
    ob.data.materials.append(m)
    if seq:
        tex = [nd for nd in m.node_tree.nodes if nd.type == 'TEX_IMAGE'][0]
        tex.image_user.frame_duration = seq
        tex.image_user.frame_start = 1 + seq_offset
        tex.image_user.use_auto_refresh = True
    return ob


def opacity_node(ob):
    return ob.active_material.node_tree.nodes['opacity'].inputs[1]


def fade(ob, f0, f1, a0, a1, interp='SINE', easing='EASE_IN_OUT'):
    sock = opacity_node(ob)
    sock.default_value = a0; sock.keyframe_insert('default_value', frame=f0)
    sock.default_value = a1; sock.keyframe_insert('default_value', frame=f1)
    for fc in _fcurves(ob.active_material.node_tree.animation_data):
        for kp in fc.keyframe_points:
            kp.interpolation = interp; kp.easing = easing


def set_opacity_keys(ob, pairs, interp='LINEAR'):
    sock = opacity_node(ob)
    for f, a in pairs:
        sock.default_value = a; sock.keyframe_insert('default_value', frame=f)
    for fc in _fcurves(ob.active_material.node_tree.animation_data):
        for kp in fc.keyframe_points:
            kp.interpolation = interp


def dof(cam, focus, fstop, f=None):
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = focus
    cam.data.dof.aperture_fstop = fstop
    if f is not None:
        cam.data.dof.keyframe_insert('focus_distance', frame=f)
        cam.data.dof.keyframe_insert('aperture_fstop', frame=f)


def compositor(bloom=0.6, threshold=0.9, size=7, vignette=0.0):
    """Bloom on highlights. Grain and the final grade happen once over the whole cut in ffmpeg."""
    s = bpy.context.scene
    if hasattr(s, 'compositing_node_group'):  # Blender 5.x
        ng = bpy.data.node_groups.new('Comp', 'CompositorNodeTree')
        s.compositing_node_group = ng
        n, L = ng.nodes, ng.links
        rl = n.new('CompositorNodeRLayers')
        out = n.new('NodeGroupOutput')
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    else:
        s.use_nodes = True
        ng = s.node_tree; n, L = ng.nodes, ng.links
        for x in list(n): n.remove(x)
        rl = n.new('CompositorNodeRLayers'); out = n.new('CompositorNodeComposite')
    g = n.new('CompositorNodeGlare')
    _set(g, ['glare_type', 'Type'], 'BLOOM')
    _set(g, ['threshold', 'Threshold'], threshold)
    _set(g, ['size', 'Size'], size)
    _set(g, ['mix', 'Strength'], bloom)
    L.new(rl.outputs['Image'], g.inputs['Image'])
    L.new(g.outputs['Image'], out.inputs[0])
    return ng, g


def _set(node, names, value):
    for nm in names:
        if hasattr(node, nm.lower()) and not nm[0].isupper():
            try:
                setattr(node, nm, value); return
            except Exception:
                pass
        if nm in node.inputs:
            sock = node.inputs[nm]
            try:
                sock.default_value = value
            except TypeError:
                sock.default_value = str(value).title() if isinstance(value, str) else value
            return
    print('WARN: could not set', names, 'on', node.bl_idname, [i.name for i in node.inputs])


def render(out_dir, frames=None):
    s = bpy.context.scene
    os.makedirs(out_dir, exist_ok=True)
    s.render.filepath = os.path.join(out_dir, 'f_')
    if frames:  # render only these frames (stills check)
        for f in frames:
            s.frame_set(f); s.render.filepath = os.path.join(out_dir, f'f_{f:04d}')
            bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)


def argv():
    a = sys.argv
    return a[a.index('--') + 1:] if '--' in a else []


def keys_socket(sock, owner_tree, pairs, interp='LINEAR', easing='AUTO'):
    """Keyframe a shader socket (opacity or emission strength) through (frame, value) pairs."""
    for f, v in pairs:
        sock.default_value = v; sock.keyframe_insert('default_value', frame=f)
    path = sock.path_from_id('default_value')
    for fc in _fcurves(owner_tree.animation_data):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                kp.interpolation = interp
                if easing != 'AUTO': kp.easing = easing


def opacity(ob, pairs, interp='CONSTANT', easing='AUTO'):
    nt = ob.active_material.node_tree
    keys_socket(nt.nodes['opacity'].inputs[1], nt, pairs, interp, easing)


def strength(ob, pairs, interp='LINEAR', easing='AUTO'):
    nt = ob.active_material.node_tree
    if 'add_strength' in nt.nodes:
        keys_socket(nt.nodes['add_strength'].inputs[1], nt, pairs, interp, easing); return
    em = [n for n in nt.nodes if n.type == 'EMISSION'][0]
    keys_socket(em.inputs['Strength'], nt, pairs, interp, easing)


def parent_keep(ob, parent):
    ob.parent = parent
    ob.matrix_parent_inverse = parent.matrix_world.inverted()


def emit_mat(name, color, strength=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes
    for x in list(n): n.remove(x)
    out = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = color; em.inputs['Strength'].default_value = strength
    tr = n.new('ShaderNodeBsdfTransparent'); mix = n.new('ShaderNodeMixShader')
    fa = n.new('ShaderNodeMath'); fa.operation = 'MULTIPLY'; fa.inputs[0].default_value = 1; fa.inputs[1].default_value = 1; fa.name = 'opacity'
    nt.links.new(fa.outputs[0], mix.inputs['Fac']); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
    return m


def rect(name, x, y, w, h, color, z=0.0, strength=1.0):
    """A flat emissive rectangle in px (centre x, y)."""
    k = (CAM_Z - z) / CAM_Z
    bpy.ops.mesh.primitive_plane_add(size=1)
    ob = bpy.context.active_object; ob.name = name
    ob.scale = (w * U * k, h * U * k, 1); ob.location = px(x, y, z)
    ob.data.materials.append(emit_mat(name + '_m', color, strength))
    return ob


def disc(name, x, y, r, color, z=0.0, strength=1.0, verts=48):
    k = (CAM_Z - z) / CAM_Z
    bpy.ops.mesh.primitive_circle_add(vertices=verts, radius=r * U * k, fill_type='NGON')
    ob = bpy.context.active_object; ob.name = name; ob.location = px(x, y, z)
    ob.data.materials.append(emit_mat(name + '_m', color, strength))
    return ob


def solid_emit(name, color, strength=1.0):
    """Opaque emission: for lines and dots that never fade by alpha (no depth-order surprises)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes
    for x in list(n): n.remove(x)
    out = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = color; em.inputs['Strength'].default_value = strength
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    return m


def curve_obj(name, pts_px, width_px, mat, z=0.0, poly=False, handles=None):
    """A curve through pixel points. Bezier with explicit handles [(h_left, h_right)] per point, or a poly line.
    Draw it on or pull it back with bevel_factor_start / bevel_factor_end (mapped along the spline)."""
    cd = bpy.data.curves.new(name, 'CURVE'); cd.dimensions = '3D'
    cd.bevel_depth = width_px * U / 2; cd.bevel_resolution = 3; cd.resolution_u = 24
    cd.bevel_factor_mapping_start = 'SPLINE'; cd.bevel_factor_mapping_end = 'SPLINE'
    if hasattr(cd, 'use_fill_caps'): cd.use_fill_caps = True
    if poly:
        sp = cd.splines.new('POLY'); sp.points.add(len(pts_px) - 1)
        for p, (x, y) in zip(sp.points, pts_px):
            p.co = (*px(x, y, z), 1)
    else:
        sp = cd.splines.new('BEZIER'); sp.bezier_points.add(len(pts_px) - 1)
        for i, (bp, (x, y)) in enumerate(zip(sp.bezier_points, pts_px)):
            bp.co = px(x, y, z)
            hl, hr = handles[i] if handles else ((x, y), (x, y))
            bp.handle_left_type = bp.handle_right_type = 'FREE'
            bp.handle_left = px(*hl, z); bp.handle_right = px(*hr, z)
    ob = bpy.data.objects.new(name, cd); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def glossy_ring_mat(name, stops, emit=0.55, rough=0.16):
    """Glossy material whose colour sweeps around the ring (a radial gradient through a colour ramp).
    Rotate the 'sweep' mapping node's Z rotation to move the highlight band around."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; L = nt.links
    for x in list(n): n.remove(x)
    out = n.new('ShaderNodeOutputMaterial'); bs = n.new('ShaderNodeBsdfPrincipled')
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping'); mp.name = 'sweep'
    gr = n.new('ShaderNodeTexGradient'); gr.gradient_type = 'RADIAL'
    cr = n.new('ShaderNodeValToRGB')
    el = cr.color_ramp.elements
    el[0].position, el[0].color = stops[0]; el[1].position, el[1].color = stops[-1]
    for pos, col in stops[1:-1]:
        e = el.new(pos); e.color = col
    L.new(tc.outputs['Object'], mp.inputs['Vector']); L.new(mp.outputs['Vector'], gr.inputs['Vector'])
    L.new(gr.outputs['Fac'], cr.inputs['Fac'])
    L.new(cr.outputs['Color'], bs.inputs['Base Color'])
    L.new(cr.outputs['Color'], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = emit
    bs.inputs['Roughness'].default_value = rough
    if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value = 1.0
    L.new(bs.outputs[0], out.inputs['Surface'])
    return m


def cam_at(cam, f, cx, cy, k=1.0, interp='SINE', easing='EASE_IN_OUT'):
    """Keyframe the camera to look at pixel (cx, cy) on the z=0 plane with zoom k (1 = frame shows 1920 px)."""
    x, y, _ = px(cx, cy)
    key(cam, 'location', f, x, interp, easing, index=0)
    key(cam, 'location', f, y, interp, easing, index=1)
    key(cam, 'location', f, CAM_Z / k, interp, easing, index=2)
    cam.data.dof.focus_distance = CAM_Z / k  # focus stays on the z=0 plane wherever the camera goes
    cam.data.dof.keyframe_insert('focus_distance', frame=f)
    for fc in _fcurves(cam.data.animation_data):
        for kp in fc.keyframe_points:
            if abs(kp.co[0] - f) < 1e-4:
                kp.interpolation = interp
                if easing != 'AUTO': kp.easing = easing


def ease(kind, t):
    t = max(0.0, min(1.0, t))
    if kind == 'inout': return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
    if kind == 'out': return 1 - (1 - t) ** 3
    if kind == 'in': return t ** 3
    if kind == 'expoinout':
        if t in (0.0, 1.0): return t
        return 2 ** (20 * t - 10) / 2 if t < 0.5 else (2 - 2 ** (-20 * t + 10)) / 2
    return t


def retimed(src_dir, start, total):
    """Map a typed-text PNG sequence onto scene frames: before `start` it holds frame 1, after its end it holds
    the last frame. Builds a folder of symlinks named by scene frame, so Blender never asks for a missing file.
    Returns the first file, for plane(..., seq=total)."""
    files = sorted(f for f in os.listdir(src_dir) if f.endswith('.png'))
    out = src_dir.rstrip('/') + f'__t{start}_{total}'
    os.makedirs(out, exist_ok=True)
    for f in range(1, total + 1):
        k = max(1, min(len(files), f - start + 1))
        dst = os.path.join(out, f'{f:04d}.png')
        if os.path.lexists(dst): os.remove(dst)
        os.symlink(os.path.join(os.path.abspath(src_dir), files[k - 1]), dst)
    return os.path.join(out, '0001.png')


def seq_plane(name, src_dir, start, total, x, y, **kw):
    ob = plane(name, retimed(src_dir, start, total), x, y, seq=total, **kw)
    tex = [n for n in ob.active_material.node_tree.nodes if n.type == 'TEX_IMAGE'][0]
    tex.image_user.frame_start = 1; tex.image_user.frame_offset = 0; tex.image_user.use_cyclic = False
    return ob


def visible(ob, pairs):
    """Switch an object on and off for render at whole frames: [(frame, True/False)]. Unlike a scale pop,
    this never leaves a motion-blur smear."""
    for f, on in pairs:
        ob.hide_render = not on; ob.keyframe_insert('hide_render', frame=f)
        ob.hide_viewport = not on; ob.keyframe_insert('hide_viewport', frame=f)


def photo_plane(name, path, z=0.0, w=W, h=H, x=W / 2, y=H / 2, sweep=False, tint=(0.21, 0.84, 1.0, 1.0), cells=(64, 36)):
    """A photo (or movie) filling a w x h px rect with cover-crop. With sweep=True the material carries a
    reveal: ahead of the 'edge' value it is white, in a band behind the edge it is pixelated and tinted, behind
    that it is the sharp photo. Key the node named 'edge' (x in 0..1, moving right to left) to run it."""
    img = bpy.data.images.load(path, check_existing=True)
    if path.lower().endswith(('.mp4', '.mov')): img.source = 'MOVIE'
    iw, ih = img.size
    k = (CAM_Z - z) / CAM_Z
    bpy.ops.mesh.primitive_plane_add(size=1)
    ob = bpy.context.active_object; ob.name = name
    ob.scale = (w * U * k, h * U * k, 1); ob.location = px(x, y, z)
    m = bpy.data.materials.new(name + '_m'); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; L = nt.links
    for q in list(n): n.remove(q)
    out = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission')
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping')
    ra, rb = w / h, iw / ih
    # cover: shrink the UV range on the overflowing axis, centred
    if rb > ra: sx, sy = ra / rb, 1.0
    else: sx, sy = 1.0, rb / ra
    mp.inputs['Scale'].default_value = (sx, sy, 1); mp.inputs['Location'].default_value = ((1 - sx) / 2, (1 - sy) / 2, 0)
    L.new(tc.outputs['UV'], mp.inputs['Vector'])
    sharp = n.new('ShaderNodeTexImage'); sharp.image = img; sharp.extension = 'EXTEND'
    if img.source == 'MOVIE':
        sharp.image_user.frame_duration = 10000; sharp.image_user.use_auto_refresh = True
    L.new(mp.outputs['Vector'], sharp.inputs['Vector'])
    col = sharp.outputs['Color']
    if sweep:
        sep = n.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['UV'], sep.inputs[0])
        edge = n.new('ShaderNodeValue'); edge.name = 'edge'; edge.outputs[0].default_value = 1.3
        d = n.new('ShaderNodeMath'); d.operation = 'SUBTRACT'; L.new(sep.outputs['X'], d.inputs[0]); L.new(edge.outputs[0], d.inputs[1])
        cell = n.new('ShaderNodeVectorMath'); cell.operation = 'MULTIPLY'; cell.inputs[1].default_value = (*cells, 1)
        L.new(mp.outputs['Vector'], cell.inputs[0])
        fl = n.new('ShaderNodeVectorMath'); fl.operation = 'FLOOR'; L.new(cell.outputs[0], fl.inputs[0])
        dv = n.new('ShaderNodeVectorMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = (*cells, 1)
        L.new(fl.outputs[0], dv.inputs[0])
        pix = n.new('ShaderNodeTexImage'); pix.image = img; pix.interpolation = 'Closest'; pix.extension = 'EXTEND'
        if img.source == 'MOVIE':
            pix.image_user.frame_duration = 10000; pix.image_user.use_auto_refresh = True
        L.new(dv.outputs[0], pix.inputs['Vector'])
        tintn = n.new('ShaderNodeMix'); tintn.data_type = 'RGBA'; tintn.blend_type = 'SCREEN'; tintn.inputs['Factor'].default_value = 0.6
        L.new(pix.outputs['Color'], tintn.inputs['A']); tintn.inputs['B'].default_value = tint
        inband = n.new('ShaderNodeMath'); inband.operation = 'GREATER_THAN'; inband.inputs[1].default_value = 0.0
        L.new(d.outputs[0], inband.inputs[0])
        m1 = n.new('ShaderNodeMix'); m1.data_type = 'RGBA'
        L.new(inband.outputs[0], m1.inputs['Factor']); L.new(col, m1.inputs['A']); L.new(tintn.outputs['Result'], m1.inputs['B'])
        wf = n.new('ShaderNodeMapRange'); wf.interpolation_type = 'SMOOTHSTEP'
        wf.inputs['From Min'].default_value = 0.1; wf.inputs['From Max'].default_value = 0.3
        L.new(d.outputs[0], wf.inputs['Value'])
        m2 = n.new('ShaderNodeMix'); m2.data_type = 'RGBA'
        L.new(wf.outputs['Result'], m2.inputs['Factor']); L.new(m1.outputs['Result'], m2.inputs['A'])
        m2.inputs['B'].default_value = (1, 1, 1, 1)
        col = m2.outputs['Result']
    tintmul = n.new('ShaderNodeMix'); tintmul.name = 'grade'; tintmul.data_type = 'RGBA'; tintmul.blend_type = 'MULTIPLY'
    tintmul.inputs['Factor'].default_value = 0.0; tintmul.inputs['B'].default_value = (1, 0.08, 0.06, 1)
    L.new(col, tintmul.inputs['A']); L.new(tintmul.outputs['Result'], em.inputs['Color'])
    L.new(em.outputs[0], out.inputs['Surface'])
    ob.data.materials.append(m)
    return ob


def node_keys(ob, node, sock_index, pairs, interp='LINEAR', easing='AUTO', output=False):
    nt = ob.active_material.node_tree
    sock = nt.nodes[node].outputs[sock_index] if output else nt.nodes[node].inputs[sock_index]
    keys_socket(sock, nt, pairs, interp, easing)
