# Blender 5.1 pitfalls

Each one cost a re-render on the Eunomia film. Check a scene against all of them before its full render.

## Transparency and depth

- **Blended transparency darkens what is behind it** and writes no depth, so focus blur treats the plane as infinitely far. Every image plane uses DITHERED (`lib.emissive_image_material` does). Only a deliberate bloom-only sprite may use `additive=True`.
- **Two dithered planes at one depth fight**: an invisible plane paints black over a visible one. `plane()` gives each new plane its own depth (`_bump`). When you place or re-seat a plane by hand, give it a depth no other plane uses.
- **A camera-parented plane can fall behind the scene** when the camera pushes in. Hold overlays at a fixed small distance from the lens with `screen_plate()` (scaled by distance / 10).

## Time and motion blur

- **Anything that changes within one frame smears.** A scale jump from 0 to 1 renders as a filled blur, and a constant camera jump smears the whole frame. Use `visible()` for pops (and animate scale only from about 0.05 up), and `cut()` for camera cuts. It lands the jump at frame - 0.4, outside any frame's shutter.
- **Constant extrapolation holds the first key backwards.** A strength or opacity key at frame 20 rules frames 1 to 19 too. Key the "before" value at frame 1 (and just before the change).
- **Read before you key.** `key(ob, 'location', f, ob.location.y - d)` moves the object; reading `ob.location.y` for the next key then reads the moved value. Store `y0` first.

## Images and sequences

- **A sequence that asks for a missing frame goes magenta and never recovers.** `seq_plane()` / `retimed()` build a symlink folder with one file per scene frame (holding the first and last frames), so every frame exists.
- **HTML layers:** in an inline `style="..."` attribute, quote font names as `&quot;Archivo Black&quot;`. Double quotes end the attribute, and single quotes break a single-quoted JS string. Check fonts loaded by looking at the exported PNG.
- Render layers at scale 3 or 4 when the camera will dive into them (a 4x zoom on a scale-2 layer is soft).

## Camera and focus

- **Focus must follow the camera.** `cam_at()` keys `focus_distance = 10 / k` with the move; a hand-keyed camera z leaves the z=0 plane soft.
- `lib.COMP` scales positions by depth so off-plane layers line up in the rest view (good for a camera near rest, like a code cloud). Set `lib.COMP = False` when the camera travels far from rest, or depth offsets slide things sideways.

## Light and grade

- **Lights push white backdrops past 1.0 and bloom turns the whole frame grey.** Keep area lights around 300 W key / 180 W rim for a torus on a light backdrop, and the bloom threshold at about 1.25 in light scenes.
- The view transform is Standard (`reset()`), so brand colours stay exact. Use `hexc()` for every colour: it converts sRGB hex to linear.

## Blender 5.1 API

- The compositor is a node group: `scene.compositing_node_group = bpy.data.node_groups.new(..., 'CompositorNodeTree')` with a `NodeGroupOutput`. Glare and Invert settings are input sockets (`inputs['Type']`, `inputs['Strength']`, `inputs['Factor']`), not node attributes.
- The engine id is `BLENDER_EEVEE`; materials use `surface_render_method` ('DITHERED' / 'BLENDED').
- Actions are layered: get F-curves with `lib._fcurves(animation_data)`, not `action.fcurves`.
- `primitive_*_add` makes the new object active; name it immediately.

## Readability

- **Colour text on a photo fails.** The owner could not read brand-green words on a mid-blue sky. Over photos and footage, set text white (or the photo's darkest tone) and stress a key word with weight (600), not hue. Check every text still on its real background at full size.

## Process

- Look at stills of every beat before a full render, and at a contact sheet cut from the final MP4 after. Most faults are timing faults (a label before its branch, a stamp before its trunk).
- One render at a time, `nice -n 19`, in the background. A 200-frame scene takes about 2 minutes on this Mac.
