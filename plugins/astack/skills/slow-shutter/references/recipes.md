# Prompt recipes

Replace the scene and crop with the user's request. Preserve their palette when given. These are visual interpretations of the supplied Wonderful.ai screenshots, not verified production settings.

## Selective motion

Suited to the team, banking and reception references. A person is readable while life passes around them. The anchor can be naturally soft; it need not look digitally sharpened.

```text
Original editorial photograph of [subject] in [place], [aspect ratio and crop].
Keep [anchor] recognisable with gently soft edges and natural skin texture. Mild optical diffusion and restrained microcontrast soften the stationary setting too, integrating it with the motion. Other people move past in the near foreground, leaving strong continuous trails along their direction of travel. Give the blur spatial depth: broad soft streaks close to the lens, shorter trails farther away. Preserve plausible bodies and avoid a row of duplicate faces.
Natural available light, fine irregular film grain across the whole photograph, visible at final display size, soft highlights, deep cool shadows and restrained warm details. Candid, lived-in, slightly imperfect framing. [Copy-space requirement if any]. Clean photograph, no typography, logos or interface elements.
```

## Panning

Suited to transport and road scenes. Choose whether the camera tracks a subject or observes a moving foreground. Do not demand incompatible sharpness from both.

```text
Original photograph of [tracked subject] moving through [place]. The camera follows the subject so [anchor] remains readable. Strong lateral movement stretches the background into long [direction] streaks. Near-lens shapes smear farther than distant structures. Keep the scene plausible and the horizon coherent.
Fine film grain remains visible over the blurred colour fields at final display size. Gently soften digital detail and local contrast across the image. Natural exposure, blue or green shadows, soft cream highlights and a restrained warm accent. [Aspect ratio and placement]. Clean photograph without words, logos or UI.
```

For a stationary anchor, replace the motion sentence: "The camera stays on [anchor] while [foreground element] sweeps across the frame with long directional trails."

## Abstract sweep

Suited to the heavily blurred strategy and careers backgrounds. Use this when the user says "the really blurred one", "no clear subject", or asks for an atmospheric background. Keep photographic colour, light and grain while dissolving recognisable objects. A moving-train viewpoint alone can leave distant scenery too detailed; specify camera sweep across all depths.

```text
Original photographic abstraction using the light and colours of [real setting, such as a garden seen from a moving train]. Strong [horizontal or diagonal] camera sweep smears EVERY depth plane, including distant scenery, into broad continuous directional streaks. Resolve the setting only as broad colour bands and light masses. Dissolve tree silhouettes, buildings and the horizon too. No identifiable objects, crisp edges or hero subject. Keep the irregular colour, exposure and layered light of a real photograph.
Large fields of [user palette, or muted blue and green] with a small [warm amber or cream] accent. Fine irregular film grain visible over the smooth streaks at final display size. Soft highlight roll-off, dark but open shadows, natural exposure. [Aspect ratio and quieter area for copy]. Edge-to-edge photograph, no words, logos, UI, black fade or synthetic gradient mesh.
```

## Rotational motion

Suited to the wind turbine reference. The blur belongs to moving parts, while structure remains legible.

```text
Original editorial photograph of [rotating subject] against [setting], [crop]. Keep the stationary [mast, housing or support] readable. The rotating [blades or wheel] create translucent curved trails around the hub, consistent with their real rotation. Preserve plausible geometry and the correct object count. Fine film grain, soft blue daylight, restrained warm highlights, gentle contrast. Clean photograph without text, logos or UI.
```

## Apply the look to a supplied image

```text
Edit image 1, the target photograph. [Image 2, if present, guides photographic treatment only.]
Preserve image 1's identity, facial features, pose, objects, their count and positions, architecture, crop and aspect ratio. Change the photographic treatment only.
Apply [treatment and strength]. [Keep the named anchor readable, or explicitly state there is no anchor for whole-image abstraction.] Blur [specified regions, moving elements or all depth planes for abstraction] into [direction and trail length], consistent with the scene's motion. Add fine irregular grain across the photograph, gently soften highlights and [keep source colours or requested grade]. Preserve natural skin tones and essential [product details or lettering].
Output a clean photograph. Do not import words, buttons, logos or layout from a style-reference screenshot. Do not invent additional people or objects.
```

If the target contains no moving elements, use a camera sweep for abstraction, or depth softness plus a restrained grade for a recognisable subject. Do not add a crowd solely to create blur. If the user requires exact pixel fidelity, explain the limitation of generative editing and use an explicitly requested deterministic editing method where available.

## Common corrections

| Observed result | Targeted change |
|---|---|
| Ordinary background bokeh | Name moving regions and ask for stretched contours along a direction. |
| Everything uniformly fuzzy | Reassert the anchor, or use a directional camera sweep for abstraction. |
| Large speckles or JPEG blocks | Ask for fine irregular film grain over colour fields, without block artefacts. |
| Abstract image still reads as a landscape | Sweep every depth plane, including the distance. Dissolve silhouettes and the horizon into broad colour bands. |
| Still regions look crisp or glossy | Gently diffuse detail and reduce local contrast across the image, while retaining a recognisable anchor. |
| Grey or muddy skin | Preserve the face's natural colour and exposure; put the cool grade in shadows. |
| Neon orange and cyan everywhere | Reduce saturation, localise the warm accent, use natural highlight roll-off. |
| Subject or layout changes in an edit | Return to the original target and repeat specific invariants before style. |
| Screenshot text or black footer appears | Reference guides photography only; request a clean edge-to-edge photograph. |
