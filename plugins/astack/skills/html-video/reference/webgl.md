# WebGL in films

Tested with Playwright's headless Chromium on macOS (October 2026): WebGL2 and Three.js render, the canvas is captured, and seeking to the same `t` gives identical pixels. Headless WebGL runs in software (SwiftShader), so shader cost lands on the CPU.

## Rules

- Create the context with `preserveDrawingBuffer: true`, and draw from `draw()`.
- Time comes from the timeline: tween `S.t` linearly from 0 to `DURATION` and pass it as a uniform, beside any other tweened uniforms. `requestAnimationFrame`, `setAnimationLoop` and `THREE.Clock` have no place in a film.
- Effects that build up across frames (feedback buffers, TAA, motion trails) break seeking. Compute them from `t`, or leave them out.
- Keep shaders cheap: a few octaves of noise, no long loops. When frames get slow, render the GL canvas at half size and scale it up with CSS; soft backgrounds hide the difference.
- If WebGL gives no context on a machine (headless Linux, CI), render with `--swiftshader`. It forces software GL for the whole page and runs about 3x slower.

## Full-screen shader

`scaffold/index.html` has a working layer, "WebGL layer": a full-screen triangle from `gl_VertexID` (no buffers), uniforms for resolution, time, a tweened intensity, and two brand colours read from CSS custom properties.

```glsl
#version 300 es
void main() { vec2 v = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2); gl_Position = vec4(v * 2. - 1., 0., 1.); }
```

Draw with `gl.drawArrays(gl.TRIANGLES, 0, 3)` after setting the uniforms.

## Three.js

```html
<script type="importmap">{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js" } }</script>
<script type="module">
  import * as THREE from 'three';
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H, false);
  // build scene, camera, meshes; then in draw():
  //   mesh.rotation.y = S.spin; camera.position.z = S.dolly; renderer.render(scene, camera);
</script>
```

- Module scripts run after classic ones. Build the timeline inside the module, or have the module resolve a promise that `__ready` awaits, so the renderer waits for three.js.
- `alpha: true` lets DOM text and the CSS background sit around the 3D layer.
- Load models (GLTFLoader) and textures before resolving `__ready`.
