---
name: slow-shutter
description: Create grainy editorial photographs with expressive motion blur, or apply that look to an uploaded photo. Use for Wonderful.ai-inspired imagery, slow-shutter photography, panning blur, a clear subject among blurred people, or abstract photographic backgrounds for websites and campaigns.
---

# Slow shutter

Make original editorial photographs inspired by the photographic treatment on [Wonderful.ai](https://www.wonderful.ai/?scLang=en). The signature is directional motion, fine film grain visible at the final display size, gently diffused detail, soft highlights, deep green or blue shadows, and warm human details. A strong image has deliberate movement and a readable composition. Simply making everything unfocused misses the look.

## Choose the treatment

Use the user's requested treatment. When they only ask for this look, default to **strong selective motion**: one readable anchor surrounded by pronounced directional blur. For a background with no hero subject, use **abstract sweep**. Apply the sweep across every depth plane; merely photographing a moving foreground can leave the distance too recognisable. Keep the user's palette and scene when supplied.

| Treatment | What stays readable | What moves |
|---|---|---|
| Selective motion | One face, person, building or object | Passing people, foreground traffic or foliage. Trails follow their travel direction. |
| Panning | The tracked subject | Background and nearby foreground streak along the camera's travel. |
| Abstract sweep | Large colour masses and a suggestion of a place | Every depth plane, including distant scenery, dissolves into broad directional streaks. No recognisable silhouettes or crisp horizon. |
| Rotational motion | The hub, tower or stationary structure | Blades or wheels trace their actual curved path. |

These are visual instructions, not claims about how the reference photographs were made. Read [references/recipes.md](references/recipes.md) for a matching prompt or to diagnose a weak result.

## Inputs and execution

Accept a scene description, an image to edit, style references, or a target image plus separate references. Identify each image's role before calling a tool. An image supplied with "apply this look" is the edit target. A website screenshot supplied as inspiration is a style reference; its headings, buttons, gradients and logos are page design, not part of the photograph.

For an edit, inspect the target first. Preserve its subject, identity, pose, object count, layout and aspect ratio unless the user asks to change them. Describe which regions move and which stay readable. Reapply those invariants on every revision. Preserve essential product details or lettering; if the requested blur conflicts with their legibility, keep those regions readable and blur their surroundings. Generative editing can alter details, so inspect the result before claiming fidelity.

Use the available image generation/editing tool to produce the image, rather than stopping at a prompt. In Codex, use the built-in `image_gen` tool and the installed `imagegen` skill's execution guidance. Inspect local targets with `view_image`, then pass their paths through `referenced_image_paths` when the tool supports it. Use the recent-image mechanism only for inputs without local paths. Use one reference mechanism per call, include every necessary input, and describe each role in the prompt. For a new image with no visual inputs, omit both reference arguments.

In another host, use its available image tool with the same role mapping and invariants. If no image tool is available, provide the ready-to-run prompt and explain that rendering is unavailable. Do not claim an image was generated or silently move to a paid API. Tool availability takes priority over guessed commands, model names or credentials.

## Build the prompt

Specify the scene, crop and intended use. Then define:

- **Anchor:** the region that remains readable, or explicitly none for an abstract sweep. Readable means recognisable with gently soft edges, rather than tack-sharp digital detail. Apply mild optical diffusion and restrained microcontrast to stationary architecture too, so it belongs to the same photograph as the blur.
- **Motion:** what moves, its direction, the length of its trails and whether it crosses the foreground. Strong blur visibly stretches contours, rather than merely softening them.
- **Finish:** fine irregular film grain visible across the image at its intended display size, restrained saturation, soft highlight roll-off and natural lighting. Use cool blue or teal shadows and warm cream, amber or skin highlights where they suit the source. Retain believable skin tones.
- **Composition:** quiet space for page copy only where requested or implied by its placement. Keep photographic texture in that space.
- **Constraints:** the edit invariants, clean photographic output, and user requirements.

Default to a clean photograph without words, logos, buttons, frames or baked-in black fades. Website copy and readability overlays belong in the page unless the user requests a finished graphic. Reuse the photographic principles, not the site's exact people, scenes or brand assets. Keep external reference images out of the distributed skill unless their licence permits redistribution.

Translate strength into observable results: **subtle** leaves most contours readable with short trails; **strong** stretches moving contours while preserving the anchor; **abstract** dissolves most detail into directional colour fields. Avoid specifying shutter speed as a guaranteed recipe, because its effect depends on camera and subject motion.

## Inspect and improve

Inspect the generated pixels at full view and a useful detail crop or zoom. Check that the requested blur is obvious, the motion follows a coherent path, the grain looks fine rather than like compression, and the anchor and edit invariants survived. For an abstract image, judge the colour masses, photographic texture and usable composition instead of searching for a sharp face.

Correct the largest visible mismatch with a targeted revision. If the result only looks defocused, request longer directional trails. If an abstract sweep still reads as a landscape, dissolve recognisable silhouettes and the distant horizon into broad streaked colour masses. If the anchor is smeared, isolate the moving regions more clearly. If the image looks synthetic, reduce glow and saturation and ask for natural exposure and irregular grain. If the still regions look too crisp or glossy, soften local contrast and fine detail across the photo while keeping the anchor recognisable. Keep the user's untouched original as the fidelity reference. Use the latest accepted output as a revision target so accepted changes survive, and compare it against the original for drift. If the subject or layout drifts, return to the original and restate the accepted treatment. Keep framing and invariants unless the user asks for a new composition.

Save a new version beside the target or in the project's requested output folder. Preserve the original. Show the final image and report its path when saved, the treatment used, and any material fidelity limitation. Keep the final prompt with the deliverable when reproducibility is useful; a prompt is not a guarantee of identical pixels.
