# Motion tactics: every move from the Eunomia film as a parameterised function, plus style presets.
# Import after lib:  from lib import *;  from tactics import *;  cfg = apply_style('techy', 'big')
# Positions are px on the z=0 plane (top-left origin, 1920x1080 frame at rest). Frames are scene frames (30 fps).
# Every tactic takes its timing as arguments and reads its easing and feel from the active style (CFG), so the
# same call reads "big" or "smooth" depending on apply_style. Catalogue with pictures in words: reference/tactics.md.
import math, random
import bpy
from lib import *
from lib import _fcurves

# ------------------------------------------------------------------ styles
STYLES = {
    # world colour, bloom (strength, threshold, size), shutter, default f-stop, grain for assemble, text/accent colours
    'techy':  dict(world='#050608', bloom=(0.5, 1.0, 7), shutter=0.5, fstop=1.2, grain=6, ink='#ededef', accent='#52bd87'),
    'airy':   dict(world='#f3f6f9', bloom=(0.3, 1.2, 6), shutter=0.5, fstop=1.6, grain=4, ink='#111214', accent='#2b9a62'),
    'paper':  dict(world='#efe6d3', bloom=(0.25, 1.3, 6), shutter=0.4, fstop=1.1, grain=5, ink='#1d1812', accent='#f29a12'),
    'nature': dict(world='#7fb0e0', bloom=(0.2, 1.3, 6), shutter=0.5, fstop=5.6, grain=4, ink='#ffffff', accent='#ffffff'),  # accent by weight, not hue: colour on sky is unreadable
    'glossy': dict(world='#e9ecf0', bloom=(0.45, 1.25, 7), shutter=0.35, fstop=2.8, grain=4, ink='#0b0c0e', accent='#3fa873'),
}
ENERGY = {
    # 'big': whips, hard cuts, overshoot pops, glitch frames, ~1.2 s beats. 'smooth': eased glides, soft pops, ~2 s beats.
    'big':    dict(move=('EXPO', 'EASE_IN_OUT'), enter=('EXPO', 'EASE_OUT'), exit=('EXPO', 'EASE_IN'), pop=('BACK', 'EASE_OUT'),
                   drift=('SINE', 'EASE_IN_OUT'), shutter_mult=1.0, glitch=True, beat=1.2, flash_peak=10.0),
    'smooth': dict(move=('SINE', 'EASE_IN_OUT'), enter=('QUART', 'EASE_OUT'), exit=('QUART', 'EASE_IN'), pop=('SINE', 'EASE_OUT'),
                   drift=('SINE', 'EASE_IN_OUT'), shutter_mult=0.6, glitch=False, beat=2.0, flash_peak=4.0),
}
CFG = dict(STYLES['techy'], **ENERGY['big'], style='techy', energy='big')


def apply_style(style='techy', energy='big', **overrides):
    """Set world colour, bloom, motion blur and the easing every tactic uses. Call right after reset().
    Any key can be overridden, e.g. apply_style('paper', 'smooth', accent='#d84a3a', shutter=0.3)."""
    CFG.clear(); CFG.update(STYLES[style]); CFG.update(ENERGY[energy]); CFG.update(style=style, energy=energy); CFG.update(overrides)
    s = bpy.context.scene
    s.world.node_tree.nodes['Background'].inputs[0].default_value = hexc(CFG['world'])
    s.render.motion_blur_shutter = CFG['shutter'] * CFG['shutter_mult']
    ng, glare = compositor(*CFG['bloom'])
    CFG['_comp'] = (ng, glare)
    return CFG


def _e(kind):
    return CFG[kind]


# ------------------------------------------------------------------ camera
def push(cam, f0, f1, x, y, k0, k1, kind='drift'):
    """A slow push (or pull with k1 < k0) on (x, y)."""
    cam_at(cam, f0, x, y, k0, *_e(kind)); cam_at(cam, f1, x, y, k1, *_e(kind))


def whip(cam, f0, f1, x0, y0, x1, y1, k=1.0):
    """A fast pan that smears everything with motion blur (title exits, follow a line)."""
    cam_at(cam, f0, x0, y0, k, *_e('move')); cam_at(cam, f1, x1, y1, k, *_e('move'))


def cut(cam, frame, x, y, k=1.0):
    """A hard cut to a new framing, landed between frames so motion blur never smears across it.
    The previous camera key before the cut is switched to CONSTANT."""
    t = frame - 0.4
    for owner in (cam, cam.data):
        for fc in _fcurves(owner.animation_data):
            prev = [kp for kp in fc.keyframe_points if kp.co[0] < t]
            if prev: max(prev, key=lambda kp: kp.co[0]).interpolation = 'CONSTANT'
    cam_at(cam, t, x, y, k, 'LINEAR')


def dive(cam, f0, f1, x, y, zoom, roll_deg=-4.0):
    """Dive into a point (a button, a word) with a slight roll; pair with motion blur for the reel's push."""
    cam_at(cam, f1, x, y, zoom, *_e('move'))
    key(cam, 'rotation_euler', f0, 0.0, *_e('move'), index=2); key(cam, 'rotation_euler', f1, math.radians(roll_deg), *_e('move'), index=2)


def rack_focus(cam, f0, f_peak, f1, depth=0.62):
    """Blur the whole frame and bring it back (a beat between two states of one scene)."""
    s = bpy.context.scene; s.frame_set(f0); fd = cam.data.dof.focus_distance
    cam.data.dof.use_dof = True
    for f, v in ((f0, fd), (f_peak, fd * depth), (f1, fd)):
        cam.data.dof.focus_distance = v; cam.data.dof.keyframe_insert('focus_distance', frame=f)


def lens(cam, fstop=None, frames=None):
    """Turn depth of field on at the style's f-stop, or key f-stops [(frame, fstop)] (CONSTANT, for cuts)."""
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = fstop or CFG['fstop']
    for f, v in (frames or []):
        cam.data.dof.aperture_fstop = v; cam.data.dof.keyframe_insert('aperture_fstop', frame=f)
    for fc in _fcurves(cam.data.animation_data):
        if 'fstop' in fc.data_path:
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'


# ------------------------------------------------------------------ text and layers
def swap_layers(paths, schedule, x=960, y=540, w=1400, h=None, z=0.0, parent=None, strengths=None):
    """Stacked layers that take turns: schedule = [(index, on_frame, off_frame)]. Word swaps, glitch states,
    state changes of one UI. Each layer gets its own depth (never two at one depth)."""
    obs = []
    for i, p in enumerate(paths):
        ob = plane(f'swap{i}', p, x, y, z=z + 0.004 * i, w=w, h=h, strength=(strengths or {}).get(i, 1.0))
        if parent: parent_keep(ob, parent)
        visible(ob, [(1, False)]); obs.append(ob)
    for i, a, b in schedule:
        visible(obs[i], [(a, True), (b, False)])
    return obs


def flash(path, frame, x=960, y=540, w=1400, h=None, z=0.03, peak=None, length=4, parent=None):
    """A bright copy of a new word, just in front of it, that dims back to normal and switches off: the bloom
    pop when a word lands. Make the layer show only the new word (others transparent) in the same layout."""
    ob = plane('flash', path, x, y, z=z, w=w, h=h)
    if parent: parent_keep(ob, parent)
    strength(ob, [(frame, peak or CFG['flash_peak']), (frame + length, 1.0)], 'QUAD', 'EASE_OUT')
    visible(ob, [(1, False), (frame, True), (frame + length, False)])
    return ob


def glitch_burst(paths, frame, x=960, y=540, w=1400, h=None, z=0.1, frames_each=(1, 2, 1, 2, 2), strengths=None, parent=None):
    """One or two frames per state (colour swaps, highlight boxes, italic, skew). Only fires when the energy
    allows glitches; otherwise returns []. Returns the frame after the burst."""
    if not CFG['glitch']: return frame
    sched, f = [], frame
    for i, n in enumerate(frames_each[:len(paths)]):
        sched.append((i, f, f + n)); f += n
    swap_layers(paths, sched, x, y, w, h, z, parent, strengths)
    return f


def type_on(seq_dir, start, total, x, y, w, h, z=0.0):
    """Text typed letter by letter: render the typing as an HTML sequence (layers.html typed()) and place it.
    Before `start` it holds frame 1, after its end it holds the last frame."""
    return seq_plane('typed', seq_dir, start, total, x, y, z=z, w=w, h=h)


def tilt_in(ob, f0, f1, rot=(-38, 24, -7), dz=2.2, dy=-0.5):
    """A heading swings in from a 3D tilt, near the lens (out of focus), and lands flat and sharp."""
    z0, y0 = ob.location.z, ob.location.y
    for idx, v in enumerate(rot):
        key(ob, 'rotation_euler', f0, math.radians(v), *_e('enter'), index=idx); key(ob, 'rotation_euler', f1, 0.0, *_e('enter'), index=idx)
    key(ob, 'location', f0, z0 + dz, *_e('enter'), index=2); key(ob, 'location', f1, z0, *_e('enter'), index=2)
    key(ob, 'location', f0, y0 + dy, *_e('enter'), index=1); key(ob, 'location', f1, y0, *_e('enter'), index=1)
    opacity(ob, [(f0, 0.0), (f0 + 3, 1.0)], 'LINEAR')


def rise_in(ob, f0, f1, dy_px=-760):
    """Slides up from below the frame (an editor, a card, a panel) and settles."""
    y0 = ob.location.y
    key(ob, 'location', f0, y0 + dy_px * U, *_e('enter'), index=1); key(ob, 'location', f1, y0, *_e('enter'), index=1)


def float_drift(ob, f0, f1, rot_deg=(5, -7), dy_px=16):
    """A gentle 3D float: small tilt and bob between two frames (editors, cards, panels in a wide)."""
    y0 = ob.location.y
    for f, sgn in ((f0, 1), ((f0 + f1) // 2, -0.4), (f1, -1)):
        key(ob, 'rotation_euler', f, math.radians(rot_deg[0] * sgn), *_e('drift'), index=0)
        key(ob, 'rotation_euler', f, math.radians(rot_deg[1] * sgn), *_e('drift'), index=1)
        key(ob, 'location', f, y0 + dy_px * U * (1 if sgn > 0 else 0), *_e('drift'), index=1)


# ------------------------------------------------------------------ glows, glyphs, clouds
def glow_mat(name, color, power=2.2, strength=2.0):
    """A soft round glow made by shader (no image): alpha falls off from the centre of the plane."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m.surface_render_method = 'DITHERED'
    nt = m.node_tree; n = nt.nodes; L = nt.links
    for q in list(n): n.remove(q)
    o = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission'); tr = n.new('ShaderNodeBsdfTransparent'); mx = n.new('ShaderNodeMixShader')
    tc = n.new('ShaderNodeTexCoord'); vm = n.new('ShaderNodeVectorMath'); vm.operation = 'LENGTH'; L.new(tc.outputs['Object'], vm.inputs[0])
    sc = n.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = 2.0; L.new(vm.outputs['Value'], sc.inputs[0])
    inv = n.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; L.new(sc.outputs[0], inv.inputs[1])
    cl = n.new('ShaderNodeMath'); cl.operation = 'MAXIMUM'; cl.inputs[1].default_value = 0.0; L.new(inv.outputs[0], cl.inputs[0])
    pw = n.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = power; L.new(cl.outputs[0], pw.inputs[0])
    op = n.new('ShaderNodeMath'); op.operation = 'MULTIPLY'; op.name = 'opacity'; op.inputs[1].default_value = 1.0; L.new(pw.outputs[0], op.inputs[0])
    em.inputs['Color'].default_value = color; em.inputs['Strength'].default_value = strength
    L.new(op.outputs[0], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs['Surface'])
    return m


def glow_dot(x, y, f_on, color=None, core_px=7, glow_px=360, z=0.0):
    """A glowing dot that pops in with overshoot: a bright core plus a soft shader glow (the line's origin)."""
    col = hexc(color or CFG['accent'])
    core = disc('dot', x, y, core_px, col, z=z + 0.03)
    core.data.materials[0] = solid_emit('dot_s', (*[min(1, c * 1.4 + 0.3) for c in col[:3]], 1), 2.0)
    bpy.ops.mesh.primitive_plane_add(size=1); g = bpy.context.active_object; g.name = 'dot_glow'
    g.scale = (glow_px * U, glow_px * U, 1); g.location = px(x, y, z - 0.02); g.data.materials.append(glow_mat('glow', col))
    for ob in (core, g):
        sx, sy = ob.scale.x, ob.scale.y
        for idx, v in ((0, sx), (1, sy)):
            key(ob, 'scale', f_on - 1, 0.0, *_e('pop'), index=idx); key(ob, 'scale', f_on + 5, v, *_e('pop'), index=idx)
        visible(ob, [(1, False), (f_on - 1, True)])
    return core, g


def glyph_orbit(paths, f_from, center=(960, 540), rx=470, ry=250, stagger=1, swirl=None, parent=None, seed=4):
    """Small glyphs (< > / * { }) pop in around a title one by one; optional swirl=(f0, f1, degrees, scale)
    spins them round with motion blur as they leave."""
    rnd = random.Random(seed)
    root = bpy.data.objects.new('orbit', None); bpy.context.scene.collection.objects.link(root); root.location = px(*center)
    obs = []
    for i, p in enumerate(paths):
        a = i / len(paths) * math.tau + rnd.uniform(-0.25, 0.25); r = rnd.uniform(0.75, 1.0)
        g = plane(f'glyph{i}', p, center[0] + math.cos(a) * rx * r, center[1] + math.sin(a) * ry * r, w=52)
        parent_keep(g, root)
        on = f_from + i * stagger
        visible(g, [(1, False), (on, True)])
        for idx in (0, 1):
            v = g.scale[idx]; key(g, 'scale', on, 0.2 * v, *_e('pop'), index=idx); key(g, 'scale', on + 4, v, *_e('pop'), index=idx)
        obs.append(g)
    if parent: parent_keep(root, parent)
    if swirl:
        f0, f1, deg, sc = swirl
        key(root, 'rotation_euler', f0, 0.0, 'EXPO', 'EASE_IN', index=2); key(root, 'rotation_euler', f1, math.radians(deg), 'EXPO', 'EASE_IN', index=2)
        for idx in (0, 1):
            key(root, 'scale', f0, 1.0, 'EXPO', 'EASE_IN', index=idx); key(root, 'scale', f1, sc, 'EXPO', 'EASE_IN', index=idx)
        for g in obs: opacity(g, [(f1 - 2, 1.0), (f1 + 2, 0.0)], 'LINEAR')
    return root, obs


def depth_cloud(paths, count, f_in, f_out, z_range=(-9.0, 5.8), avoid=(960, 540, 420, 90), w=640, tilt=(12, 35, 4), alpha=(0.55, 0.95), seed=4):
    """Fragments (code, labels, badges) on tilted planes scattered through depth; with depth of field and a camera
    push through them this is the reel's 'cloud'. f_in is (first, spread) frames; f_out the frame they vanish."""
    rnd = random.Random(seed); obs = []
    for i in range(count):
        z = rnd.uniform(*z_range)
        while True:
            x, y = rnd.uniform(-150, 2070), rnd.uniform(40, 1040)
            if not (abs(y - avoid[1]) < avoid[3] and abs(x - avoid[0]) < avoid[2]): break
        sn = plane(f'frag{i}', paths[i % len(paths)], x, y, z=z, w=w)
        sn.rotation_euler = tuple(math.radians(rnd.uniform(-t, t)) for t in tilt)
        t0 = f_in[0] + rnd.randint(0, f_in[1])
        opacity(sn, [(1, 0.0), (t0, 0.0), (t0 + 4, rnd.uniform(*alpha)), (f_out, 0.0)], 'LINEAR')
        obs.append(sn)
    return obs


# ------------------------------------------------------------------ lines, threads, rings
def wave_line(p0, p1, f_draw0, f_draw1, amp=38, wavelength=112, sigma=210, travel=470, width=2.2, color='#eef1f5', settle=0.3, n=170):
    """A line drawn on from p0 to p1 with a travelling wobble packet riding just behind the drawing head,
    settling after the draw. The reel's 'text becomes a line' beat starts here."""
    mat = solid_emit('line', hexc(color), 1.15)
    xs = [p0[0] + (p1[0] - p0[0]) * i / (n - 1) for i in range(n)]
    ob = curve_obj('wave', [(x, p0[1]) for x in xs], width, mat, poly=True)
    ob.data.bevel_factor_end = 0.0
    tween(ob.data, 'bevel_factor_end', f_draw0, 0.0, f_draw1, 1.0, 'SINE', 'EASE_OUT')
    span = f_draw1 - f_draw0
    def y(x, f):
        c = p0[0] + 90 + travel * ease('out', (f - f_draw0) / span)
        a = amp * min(1.0, (f - f_draw0 + 1) / 4) * (1 - settle * ease('inout', (f - f_draw1) / 40))
        return p0[1] - a * math.exp(-((x - c) / sigma) ** 2) * math.sin((x - c) / wavelength * math.tau + min(f, f_draw1) * 0.32)
    sp = ob.data.splines[0]
    for f in range(1, f_draw1 + 45):
        for i, p in enumerate(sp.points):
            X, Y, Z = px(xs[i], y(xs[i], f) if f >= f_draw0 else p0[1])
            p.co = (X, Y, Z, 1); p.keyframe_insert('co', frame=f)
    return ob


def fan_threads(origin, targets, f0, stagger=2, width=2.0, color='#eef1f5', retract=None, decor=(), seed=11):
    """Curves grow out of one point with organic S shapes to each target (and decor strands that run off frame).
    retract=(f_a, f_b) pulls them all back into the origin. Returns (curves, endpoints)."""
    rnd = random.Random(seed); mat = solid_emit('thread', hexc(color), 1.15)
    curves, ends = [], []
    for i, (dx, dy) in enumerate(list(targets) + list(decor)):
        tx, ty = origin[0] + dx, origin[1] + dy
        wob = rnd.uniform(-0.35, 0.35) * abs(dy) + rnd.uniform(-120, 120)
        h0 = ((origin[0] - 10, origin[1]), (origin[0] + dx * 0.32, origin[1] + wob))
        h1 = ((tx - dx * 0.38, ty - dy * 0.05), (tx + 10, ty))
        c = curve_obj(f'thread{i}', [origin, (tx, ty)], width * (0.8 if i >= len(targets) else 1), mat, z=-0.01, handles=[h0, h1])
        c.data.bevel_factor_end = 0.0
        tween(c.data, 'bevel_factor_end', f0 + i * stagger, 0.0, f0 + i * stagger + 20, 1.0, 'SINE', 'EASE_IN_OUT')
        if retract:
            key(c.data, 'bevel_factor_end', retract[0], 1.0, 'SINE', 'EASE_IN_OUT'); key(c.data, 'bevel_factor_end', retract[1], 0.0, 'SINE', 'EASE_IN_OUT')
        curves.append(c)
        if i < len(targets): ends.append((tx, ty))
    return curves, ends


def tip_dots(points, f_on, r=6, color='#eef1f5', stagger=1):
    dots = []
    for i, (x, y) in enumerate(points):
        d = disc(f'tip{i}', x, y, r, hexc(color), z=0.02); d.data.materials[0] = solid_emit(f'tip_m{i}', hexc(color), 1.3)
        visible(d, [(1, False), (f_on + i * stagger, True)])
        for idx in (0, 1):
            v = d.scale[idx]; key(d, 'scale', f_on + i * stagger, 0.0, *_e('pop'), index=idx); key(d, 'scale', f_on + i * stagger + 5, v, *_e('pop'), index=idx)
        dots.append(d)
    return dots


def dots_to_ring(dots, starts, center, radius, f0, arrive=13, whip_at=None, grow=(6, 13), f_hide=None):
    """Loose dots fly into a ring, drift-spin, then (whip_at) spin fast enough that motion blur smears them.
    Pair with dashes_close() to turn the smear into a closed ring."""
    whip_at = whip_at or f0 + 14
    def spin(f): return 0.25 * (f - f0) / 30 + 2.6 * ease('in', (f - whip_at) / 11)
    for i, (d, (sx, sy)) in enumerate(zip(dots, starts)):
        a0 = math.radians(90 + 360 / len(dots) * i)
        for f in range(f0 - 1, whip_at + 12):
            k = ease('expoinout', (f - f0) / arrive); a = a0 + spin(f)
            x = sx + (center[0] + math.cos(a) * radius - sx) * k; y = sy + (center[1] - math.sin(a) * radius - sy) * k
            d.location = px(x, y, 0.02); d.keyframe_insert('location', frame=f)
            sc = (grow[0] + (grow[1] - grow[0]) * k) / grow[0]; d.scale = (sc, sc, 1); d.keyframe_insert('scale', frame=f)
        if f_hide: visible(d, [(f_hide, False)])
    return spin


def dashes_close(center, radius, n, f_start, f_closed, spin, f_hide, thickness=26, color='#f4f6f8'):
    """Arcs that grow from dot-length to closing the ring while it spins (the reel's dashed-ring beat)."""
    mat = solid_emit('arc', hexc(color), 1.25); arcs = []
    for i in range(n):
        cd = bpy.data.curves.new(f'arc{i}', 'CURVE'); cd.dimensions = '3D'
        cd.bevel_depth = thickness / 2 * U; cd.bevel_resolution = 4; cd.bevel_factor_mapping_start = cd.bevel_factor_mapping_end = 'SPLINE'
        sp = cd.splines.new('POLY'); M = 96; sp.points.add(M - 1)
        for j, p in enumerate(sp.points):
            a = j / (M - 1) * math.tau; p.co = (math.cos(a) * radius * U, math.sin(a) * radius * U, 0, 1)
        ob = bpy.data.objects.new(f'arc{i}', cd); bpy.context.scene.collection.objects.link(ob); ob.data.materials.append(mat)
        ob.location = px(*center, 0.02)
        for f in range(f_start - 2, f_hide + 1):
            Lf = 0.012 + (1 / n - 0.012) * ease('inout', (f - f_start) / (f_closed - f_start))
            a = math.radians(90 + 360 / n * i) + spin(f)
            cd.bevel_factor_end = Lf; cd.keyframe_insert('bevel_factor_end', frame=f)
            ob.rotation_euler = (0, 0, -a - Lf * math.pi); ob.keyframe_insert('rotation_euler', frame=f)
        visible(ob, [(1, False), (f_start, True), (f_hide, False)]); arcs.append(ob)
    return arcs


def glossy_ring(center, radius, tube_px, stops, f_on, sweep=(0.0, -5.5), sweep_frames=None, lights=True, backdrop='#e9ecf0'):
    """A glossy 3D torus whose colour band sweeps round it, lit by a key and a tinted rim light, casting a soft
    shadow on a backdrop. stops = [(pos, '#hex'), ...] around the ring."""
    s = bpy.context.scene
    mat = glossy_ring_mat('ring', [(p, hexc(c)) for p, c in stops])
    sw = mat.node_tree.nodes['sweep'].inputs['Rotation']
    f_end = (sweep_frames or (f_on, s.frame_end))
    for f, a in zip(f_end, sweep):
        sw.default_value[2] = a; sw.keyframe_insert('default_value', index=2, frame=f)
    bpy.ops.mesh.primitive_torus_add(major_radius=radius * U, minor_radius=tube_px * U, major_segments=160, minor_segments=36)
    tor = bpy.context.active_object; tor.name = 'torus'; bpy.ops.object.shade_smooth()
    tor.data.materials.append(mat); tor.location = px(*center, 0.0)
    visible(tor, [(1, False), (f_on, True)])
    for idx in (0, 1, 2):
        key(tor, 'scale', f_on, 0.97, 'SINE', 'EASE_OUT', index=idx); key(tor, 'scale', f_on + 6, 1.0, 'SINE', 'EASE_OUT', index=idx)
    if lights:
        cx, cy, _ = px(*center)
        for name, loc, e, size, col in (('key', (cx - 2.5, cy + 3.0, 6.0), 300, 5.0, (1, 1, 1)), ('rim', (cx + 3.5, cy - 2.0, 3.0), 180, 3.0, (0.75, 1.0, 0.88))):
            ld = bpy.data.lights.new(name, 'AREA'); ld.energy = e; ld.size = size; ld.color = col
            lo = bpy.data.objects.new(name, ld); s.collection.objects.link(lo); lo.location = loc
            tr = lo.constraints.new('TRACK_TO'); tr.target = tor; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    if backdrop:
        bpy.ops.mesh.primitive_plane_add(size=1); bd = bpy.context.active_object; bd.name = 'backdrop'
        bd.scale = (60, 40, 1); bd.location = (px(*center)[0], px(*center)[1], -2.2)
        bm = bpy.data.materials.new('backdrop'); bm.use_nodes = True
        b = bm.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = hexc(backdrop); b.inputs['Roughness'].default_value = 0.9
        bd.data.materials.append(bm); visible(bd, [(1, False), (f_on, True)])
    return tor, mat


def ring_tunnel(tor, mat, center, f0, echoes=((3, 1.42), (6, 1.95), (9, 2.7), (12, 3.8)), tilt=(24, -14), end_scale=2.2, f_end=None):
    """The ring tilts in 3D and echoes outward: copies spawn and grow past the frame while the camera pushes in."""
    f_end = f_end or f0 + 36
    for idx, v in ((0, math.radians(tilt[0])), (1, math.radians(tilt[1]))):
        key(tor, 'rotation_euler', f0, 0.0, 'EXPO', 'EASE_IN_OUT', index=idx); key(tor, 'rotation_euler', f0 + 14, v, 'EXPO', 'EASE_IN_OUT', index=idx)
        key(tor, 'rotation_euler', f0 + 27, v * 0.4, 'SINE', 'EASE_IN_OUT', index=idx)
    for idx in (0, 1, 2):
        key(tor, 'scale', f_end - 14, 1.0, 'SINE', 'EASE_IN', index=idx); key(tor, 'scale', f_end, end_scale, 'SINE', 'EASE_IN', index=idx)
    out = []
    for i, (df, big) in enumerate(echoes):
        e = tor.copy(); e.data = tor.data; e.animation_data_clear(); bpy.context.scene.collection.objects.link(e)
        e.rotation_euler = (math.radians(tilt[0] - 4 * i), math.radians(tilt[1] + 3 * i), 0)
        visible(e, [(1, False), (f0 + df, True)])
        for idx in (0, 1, 2):
            key(e, 'scale', f0 + df, 1.0, 'EXPO', 'EASE_OUT', index=idx); key(e, 'scale', f0 + df + 16, big, 'EXPO', 'EASE_OUT', index=idx)
            key(e, 'scale', f_end, big * 1.6, 'SINE', 'EASE_IN', index=idx)
        out.append(e)
    return out


# ------------------------------------------------------------------ backgrounds and grades
def pixel_sweep(photo, f0, f1):
    """Reveal a photo_plane(..., sweep=True): white, then a band of tinted pixels, then the sharp photo, moving
    left to right. Tint and pixel size are photo_plane arguments."""
    node_keys(photo, 'edge', 0, [(f0, -0.35), (f1, 1.35)], 'SINE', 'EASE_IN_OUT', output=True)


def ripple_bg(f_on, f_off, freq=19.0, colors=('#cfe9fa', '#86c8f0'), centre='#ffffff', base='#e9f4fb', speed=26.0):
    """Concentric soft bands pulsing outward, white at the centre (screen-space shader): the water-ripple behind
    a burst. freq sets band count, speed how fast they travel."""
    s = bpy.context.scene
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
    fr = n.new('ShaderNodeMath'); fr.operation = 'MULTIPLY'; fr.inputs[1].default_value = freq; Lk.new(ln.outputs['Value'], fr.inputs[0])
    ph = n.new('ShaderNodeValue'); ph.name = 'phase'
    sub = n.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'; Lk.new(fr.outputs[0], sub.inputs[0]); Lk.new(ph.outputs[0], sub.inputs[1])
    sn = n.new('ShaderNodeMath'); sn.operation = 'SINE'; Lk.new(sub.outputs[0], sn.inputs[0])
    band = n.new('ShaderNodeMapRange'); band.inputs['From Min'].default_value = -1; band.inputs['From Max'].default_value = 1
    band.interpolation_type = 'SMOOTHSTEP'; Lk.new(sn.outputs[0], band.inputs['Value'])
    c1 = n.new('ShaderNodeMix'); c1.data_type = 'RGBA'; Lk.new(band.outputs['Result'], c1.inputs['Factor'])
    c1.inputs['A'].default_value = hexc(colors[0]); c1.inputs['B'].default_value = hexc(colors[1])
    cw = n.new('ShaderNodeMapRange'); cw.interpolation_type = 'SMOOTHSTEP'; cw.inputs['From Min'].default_value = 0.3; cw.inputs['From Max'].default_value = 0.12
    Lk.new(ln.outputs['Value'], cw.inputs['Value'])
    c2 = n.new('ShaderNodeMix'); c2.data_type = 'RGBA'; Lk.new(cw.outputs['Result'], c2.inputs['Factor'])
    Lk.new(c1.outputs['Result'], c2.inputs['A']); c2.inputs['B'].default_value = hexc(centre)
    on = n.new('ShaderNodeMix'); on.name = 'on'; on.data_type = 'RGBA'; on.inputs['A'].default_value = hexc(base)
    Lk.new(c2.outputs['Result'], on.inputs['B']); Lk.new(on.outputs['Result'], em.inputs['Color']); Lk.new(em.outputs[0], out.inputs['Surface'])
    rip.data.materials.append(m)
    keys_socket(ph.outputs[0], nt, [(1, 0.0), (s.frame_end, speed * s.frame_end / 72)], 'LINEAR')
    keys_socket(on.inputs['Factor'], nt, [(1, 0.0), (f_on, 0.0), (f_on + 5, 1.0), (f_off, 1.0), (f_off + 9, 0.0)], 'LINEAR')
    return rip


def alarm_grade(photo, f0, f1, color=(1, 0.08, 0.06, 1), level=0.88, flicker=(0.62, 0.9, 0.7, 0.9, 0.78, 0.92, 0.74, 0.9), every=4):
    """Flush a photo_plane a colour and flicker it while an error is on screen (the reel's red forest)."""
    node_keys(photo, 'grade', 'B', [(1, color)], 'CONSTANT')
    pairs = [(1, 0.0), (f0 - 1, 0.0), (f0, level)]
    f = f0 + 3
    for v in flicker:
        if f >= f1: break
        pairs.append((f, v)); f += every
    pairs.append((f1, 0.0))
    node_keys(photo, 'grade', 'Factor', pairs, 'CONSTANT')


def warm_grade(photo, f0, f1, color=(1.0, 0.86, 0.55, 1.0), level=0.3):
    node_keys(photo, 'grade', 'B', [(1, color)], 'CONSTANT')
    node_keys(photo, 'grade', 'Factor', [(1, 0.0), (f0, 0.0), (f1, level)], 'SINE', 'EASE_IN_OUT')


def wind(photo, amp=0.012, scale=7.0, bottom=(0.42, 0.2), speed=4.0):
    """Make a still photo breathe: noise-driven UV wobble in the lower part only (flowers, grass, water)."""
    s = bpy.context.scene; nt = photo.active_material.node_tree; n = nt.nodes; L = nt.links
    mp = [x for x in n if x.type == 'MAPPING'][0]; tc = [x for x in n if x.type == 'TEX_COORD'][0]
    noise = n.new('ShaderNodeTexNoise'); noise.noise_dimensions = '4D'; noise.inputs['Scale'].default_value = scale; noise.inputs['Detail'].default_value = 1.5
    L.new(tc.outputs['UV'], noise.inputs['Vector'])
    keys_socket(noise.inputs['W'], nt, [(1, 0.0), (s.frame_end, speed * s.frame_end / 240)], 'LINEAR')
    sub = n.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.5, 0.5, 0.5); L.new(noise.outputs['Color'], sub.inputs[0])
    sep = n.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['UV'], sep.inputs[0])
    mask = n.new('ShaderNodeMapRange'); mask.interpolation_type = 'SMOOTHSTEP'
    mask.inputs['From Min'].default_value, mask.inputs['From Max'].default_value = bottom; L.new(sep.outputs['Y'], mask.inputs['Value'])
    a = n.new('ShaderNodeMath'); a.operation = 'MULTIPLY'; a.inputs[1].default_value = amp; L.new(mask.outputs['Result'], a.inputs[0])
    sc = n.new('ShaderNodeVectorMath'); sc.operation = 'SCALE'; L.new(sub.outputs[0], sc.inputs[0]); L.new(a.outputs[0], sc.inputs['Scale'])
    add = n.new('ShaderNodeVectorMath'); add.operation = 'ADD'; L.new(tc.outputs['UV'], add.inputs[0]); L.new(sc.outputs[0], add.inputs[1])
    L.new(add.outputs[0], mp.inputs['Vector'])


def invert_frames(frames):
    """Colour-negative glitch frames at the given scene frames (a hand-over between worlds)."""
    ng, glare = CFG['_comp']
    n, Lk = ng.nodes, ng.links
    inv = n.new('CompositorNodeInvert')
    out = [x for x in n if x.bl_idname in ('NodeGroupOutput', 'CompositorNodeComposite')][0]
    Lk.new(glare.outputs['Image'], inv.inputs['Color']); Lk.new(inv.outputs[0], out.inputs[0])
    fac = inv.inputs['Factor']
    pairs = [(1, 0.0)] + [p for f in frames for p in ((f, 1.0), (f + 1, 0.0))]
    for f, v in pairs:
        fac.default_value = v; fac.keyframe_insert('default_value', frame=f)
    for fc in _fcurves(ng.animation_data):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'


# ------------------------------------------------------------------ bursts, scatters, growth
def card_burst(paths, f0, center=(960, 540), radius=430, interval=1.4, swing_deg=150, tilt_deg=12, spin=(8, 46, -16), burst=(40, 50, 3.4, 58, 7.0), w=560, h=300):
    """Cards fire one after another from a hub and swing clockwise into a pinwheel; the wheel turns, then
    bursts outward past the frame. burst=(f_from, f_out, scale_out, f_gone, scale_gone)."""
    s = bpy.context.scene
    wheel = bpy.data.objects.new('wheel', None); s.collection.objects.link(wheel); wheel.location = px(*center, 0.0)
    NC = len(paths); cards = []
    for i, p in enumerate(paths):
        th = math.radians(90 - i * 360 / NC)
        cd = plane(f'card{i}', p, center[0], center[1], z=0.02 + 0.012 * i, w=w, h=h); z0 = cd.location.z
        cd.parent = wheel; cd.location = (0, 0, z0); sx, sy = cd.scale.x, cd.scale.y
        L0 = f0 + interval * i
        visible(cd, [(1, False), (int(L0), True)])
        for f in range(int(L0), int(L0) + 11):
            u = ease('out', (f - L0) / 9.0); a = th + math.radians(swing_deg) * (1 - u); r = (60 + (radius - 60) * u) * U; sc = 0.35 + 0.65 * u
            cd.location = (math.cos(a) * r, math.sin(a) * r, z0); cd.keyframe_insert('location', frame=f)
            cd.rotation_euler = (0, 0, a + math.radians(tilt_deg) * u); cd.keyframe_insert('rotation_euler', frame=f)
            cd.scale = (sx * sc, sy * sc, 1); cd.keyframe_insert('scale', frame=f)
        cards.append(cd)
    key(wheel, 'rotation_euler', spin[0], 0.0, 'SINE', 'EASE_OUT', index=2); key(wheel, 'rotation_euler', spin[1], math.radians(spin[2]), 'SINE', 'EASE_OUT', index=2)
    if burst:
        a, b, sb, c, sc_ = burst
        for idx in (0, 1):
            key(wheel, 'scale', a, 1.0, 'EXPO', 'EASE_IN', index=idx); key(wheel, 'scale', b, sb, 'EXPO', 'EASE_IN', index=idx)
            key(wheel, 'scale', c, sc_, 'SINE', 'EASE_OUT', index=idx)
    return wheel, cards


def scatter_settle(items, f_go, region=(420, 1560, 160, 940), z_range=(-3.5, 2.8), f_in=(3, 16), dur=18, stagger=2, parent=None, seed=5):
    """Things (labels, badges) float at many depths while the camera trucks past, then fly to their final spots.
    items = [(path, final_x, final_y, w, h)] where final x, y is the plane centre."""
    rnd = random.Random(seed); obs = []
    for i, (p, fx, fy, w, h) in enumerate(items):
        lb = plane(f'scatter{i}', p, fx, fy, z=0.05, w=w, h=h); fin = tuple(lb.location)
        zs = rnd.uniform(*z_range); start = px(rnd.uniform(region[0], region[1]), rnd.uniform(region[2], region[3]), zs)
        t_in = f_in[0] + rnd.randint(0, f_in[1]); g = f_go + (i % 6) * stagger
        for idx in range(3):
            key(lb, 'location', 1, start[idx], *_e('move'), index=idx); key(lb, 'location', g, start[idx], *_e('move'), index=idx)
            key(lb, 'location', g + dur, fin[idx], *_e('move'), index=idx)
        opacity(lb, [(1, 0.0), (t_in, 0.0), (t_in + 6, 1.0)], 'LINEAR')
        if parent: parent_keep(lb, parent)
        obs.append(lb)
    return obs


def grow_reveal(image_path, grow_path, rect, f0, f1, t=(-0.02, 1.03), grade=None):
    """An illustration revealed along a growth map (grow_prep.py): branches, roots, rivers, cracks, ink spreading
    outward from a seed point. rect=(left, top, scale) in px. Returns (plane, frame_for(g))."""
    left, top, sc = rect
    img = bpy.data.images.load(image_path); gm = bpy.data.images.load(grow_path); gm.colorspace_settings.name = 'Non-Color'
    IW, IH = img.size
    bpy.ops.mesh.primitive_plane_add(size=1); ob = bpy.context.active_object; ob.name = 'grow'
    ob.scale = (IW * sc * U, IH * sc * U, 1); ob.location = px(left + IW * sc / 2, top + IH * sc / 2, 0.0)
    m = bpy.data.materials.new('grow'); m.use_nodes = True; m.surface_render_method = 'DITHERED'
    nt = m.node_tree; n = nt.nodes; Lk = nt.links
    for q in list(n): n.remove(q)
    o = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission'); tr = n.new('ShaderNodeBsdfTransparent'); mx = n.new('ShaderNodeMixShader')
    ti = n.new('ShaderNodeTexImage'); ti.image = img; ti.interpolation = 'Cubic'
    gi = n.new('ShaderNodeTexImage'); gi.image = gm
    T = n.new('ShaderNodeValue'); T.name = 'T'
    lo = n.new('ShaderNodeMath'); lo.operation = 'SUBTRACT'; lo.inputs[1].default_value = 0.012; Lk.new(T.outputs[0], lo.inputs[0])
    mr = n.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'
    Lk.new(gi.outputs['Color'], mr.inputs['Value']); Lk.new(lo.outputs[0], mr.inputs['From Min']); Lk.new(T.outputs[0], mr.inputs['From Max'])
    mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    al = n.new('ShaderNodeMath'); al.operation = 'MULTIPLY'; Lk.new(ti.outputs['Alpha'], al.inputs[0]); Lk.new(mr.outputs['Result'], al.inputs[1])
    gr = n.new('ShaderNodeMix'); gr.name = 'grade'; gr.data_type = 'RGBA'; gr.blend_type = 'MULTIPLY'; gr.inputs['B'].default_value = (1.0, 0.9, 0.7, 1)
    Lk.new(ti.outputs['Color'], gr.inputs['A']); Lk.new(gr.outputs['Result'], em.inputs['Color'])
    Lk.new(al.outputs[0], mx.inputs['Fac']); Lk.new(tr.outputs[0], mx.inputs[1]); Lk.new(em.outputs[0], mx.inputs[2]); Lk.new(mx.outputs[0], o.inputs['Surface'])
    ob.data.materials.append(m)
    keys_socket(T.outputs[0], nt, [(1, t[0]), (f0, t[0]), (f1, t[1])], 'QUAD', 'EASE_IN_OUT')
    if grade: keys_socket(gr.inputs['Factor'], nt, [(1, 0.0)] + list(grade), 'SINE', 'EASE_IN_OUT')
    def frame_for(g):
        for f10 in range(f0 * 10, f1 * 10 + 1):
            u = (f10 / 10 - f0) / (f1 - f0); e = 2 * u * u if u < 0.5 else 1 - (-2 * u + 2) ** 2 / 2
            if t[0] + (t[1] - t[0]) * e >= g: return f10 / 10
        return f1
    return ob, frame_for


def sprite_pop(sprites, points, frames, sizes=(44, 64), parent=None, seed=9):
    """Small sprites (blossoms, leaves, sparks, stickers) pop in with overshoot at given points and frames.
    sprites = list of image paths; points = [(x, y)]; frames = list of start frames."""
    rnd = random.Random(seed); out = []
    for j, ((x, y), f0) in enumerate(zip(points, frames)):
        sp = plane(f'sprite{j}', sprites[j % len(sprites)], x, y, z=0.12 + j * 0.002, w=rnd.uniform(*sizes))
        sp.rotation_euler = (0, 0, math.radians(rnd.uniform(-180, 180)))
        visible(sp, [(1, False), (int(f0), True)])
        for idx in (0, 1):
            v = sp.scale[idx]; key(sp, 'scale', int(f0), v * 0.1, *_e('pop'), index=idx); key(sp, 'scale', int(f0) + 6, v, *_e('pop'), index=idx)
        if parent: parent_keep(sp, parent)
        out.append(sp)
    return out


def drift(sprites, count, f_from, f_to, region=(500, 2000, -120, 500), fall=((1.0, 2.4), (1.2, 2.6)), size=(26, 40), tint=None, seed=6):
    """Things drifting across the frame (falling leaves, petals, dust, confetti) with a slow spin."""
    rnd = random.Random(seed); out = []
    for k in range(count):
        d = plane(f'drift{k}', sprites[k % len(sprites)], rnd.uniform(region[0], region[1]), rnd.uniform(region[2], region[3]),
                  z=rnd.uniform(0.3, 2.5), w=rnd.uniform(*size), tint=tint)
        f0 = f_from + rnd.randint(0, max(1, (f_to - f_from) // 2)); visible(d, [(1, False), (f0, True)])
        p0 = tuple(d.location); p1 = (p0[0] - rnd.uniform(*fall[0]), p0[1] - rnd.uniform(*fall[1]))
        for idx in range(2):
            key(d, 'location', f0, p0[idx], 'LINEAR', index=idx); key(d, 'location', f_to, p1[idx], 'LINEAR', index=idx)
        key(d, 'rotation_euler', f0, 0.0, 'LINEAR', index=2); key(d, 'rotation_euler', f_to, rnd.uniform(-5, 5), 'LINEAR', index=2)
        out.append(d)
    return out


def sway(pivot_xy, keys_deg):
    """An empty to parent things to, rocking gently: keys_deg = [(frame, degrees)]. Returns the empty."""
    e = bpy.data.objects.new('sway', None); bpy.context.scene.collection.objects.link(e); e.location = px(*pivot_xy)
    for f, a in keys_deg:
        key(e, 'rotation_euler', f, math.radians(a), 'SINE', 'EASE_IN_OUT', index=2)
    return e


def voxel_shape(center, f_on, n=9, cell_px=31, fill=0.74, stops=(('#0f6b3f', 0.0), ('#1fa86a', 0.35), ('#2fc0b4', 0.65), ('#8a5ad8', 1.0)),
                spin=(28, (20, 85)), z=0.45, light=True):
    """A cube built from small glowing voxels with a colour gradient across it, popping in and turning.
    spin = (x tilt degrees, (y start, y end) degrees over the shot)."""
    s = bpy.context.scene
    vm = bpy.data.materials.new('voxel'); vm.use_nodes = True
    vn = vm.node_tree.nodes; vl = vm.node_tree.links; bs = vn['Principled BSDF']; oi = vn.new('ShaderNodeObjectInfo')
    vl.new(oi.outputs['Color'], bs.inputs['Base Color']); vl.new(oi.outputs['Color'], bs.inputs['Emission Color'])
    bs.inputs['Emission Strength'].default_value = 0.85; bs.inputs['Roughness'].default_value = 0.35
    root = bpy.data.objects.new('voxroot', None); s.collection.objects.link(root); root.location = px(*center, z)
    bpy.ops.mesh.primitive_cube_add(size=1); proto = bpy.context.active_object; proto.name = 'vox_proto'
    proto.data.materials.append(vm); proto.hide_render = proto.hide_viewport = True
    cs = [(p, hexc(c)) for c, p in stops]; cell = cell_px * U
    def ramp(t):
        for (p0, c0), (p1, c1) in zip(cs, cs[1:]):
            if t <= p1:
                k = (t - p0) / (p1 - p0); return tuple(c0[i] + (c1[i] - c0[i]) * k for i in range(4))
        return cs[-1][1]
    c = (n - 1) / 2
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if 0 < i < n - 1 and 0 < j < n - 1 and 0 < k < n - 1: continue
                v = bpy.data.objects.new(f'vox_{i}_{j}_{k}', proto.data); s.collection.objects.link(v); v.parent = root
                v.location = ((i - c) * cell, (j - c) * cell, (k - c) * cell); v.scale = (cell * fill,) * 3
                v.color = ramp((i + j + (n - 1 - k)) / (3 * (n - 1))); visible(v, [(1, False), (f_on, True)])
    for idx in (0, 1, 2):
        key(root, 'scale', f_on, 0.05, *_e('enter'), index=idx); key(root, 'scale', f_on + 12, 1.0, *_e('enter'), index=idx)
    key(root, 'rotation_euler', f_on, math.radians(spin[0]), 'LINEAR', index=0)
    key(root, 'rotation_euler', f_on, math.radians(spin[1][0]), 'LINEAR', index=1); key(root, 'rotation_euler', s.frame_end, math.radians(spin[1][1]), 'LINEAR', index=1)
    if light:
        ld = bpy.data.lights.new('voxkey', 'AREA'); ld.energy = 120; ld.size = 3
        lo = bpy.data.objects.new('voxkey', ld); s.collection.objects.link(lo); lo.location = (root.location.x - 1.5, root.location.y + 2.5, 4.0)
        tr = lo.constraints.new('TRACK_TO'); tr.target = root; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    return root


def screen_plate(path, d=3.0, frames=None, cam=None):
    """A full-frame layer held d units in front of the lens (end cards, title cards, glitch frames, overlays):
    always in front of anything the camera pushes toward. frames = [(frame, visible)]."""
    cam = cam or bpy.context.scene.camera
    ob = plane('plate', path, 960, 540, w=1920, h=1080)
    ob.parent = cam; ob.matrix_parent_inverse.identity(); ob.location = (0, 0, -d)
    ob.scale = (1920 * U * d / CAM_Z * 1.02, 1080 * U * d / CAM_Z * 1.02, 1)
    if frames: visible(ob, frames)
    return ob
