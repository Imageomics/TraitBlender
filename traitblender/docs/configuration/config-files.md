# Configuration Files

TraitBlender config files are **YAML** files that store the settings you see in the **Configuration** panel (camera, lighting, world, materials, output, etc.). You can export a YAML to reuse the same setup later.

<details>
<summary>Basic structure</summary>

<p>Config files are organized into top-level sections. Each section controls one part of the scene or pipeline:</p>

<ul>
  <li><code>morphospace</code> – which morphospace is active and its hyperparameters</li>
  <li><code>dataset</code> – the external dataset file path (CSV/TSV/XLSX)</li>
  <li><code>world</code> – background color and strength</li>
  <li><code>camera</code> – position, rotation, resolution, lens</li>
  <li><code>lamp</code> – light position, color, power, shadows</li>
  <li><code>mat</code> – specimen mat position, scale, color, roughness</li>
  <li><code>render</code> – render engine and Eevee ray tracing</li>
  <li><code>output</code> – where simulation results are written and in what format</li>
  <li><code>metadata</code> – stamp text in the rendered images</li>
  <li><code>ruler</code> – ruler location / visibility</li>
  <li><code>transforms</code> – optional random variation on config values</li>
  <li><code>imaging</code> – which orientations to render, custom Euler orientations, and how many images</li>
  <li><code>meshes</code> – mesh export options during simulation</li>
</ul>

<p>The Datasets panel <code>sample</code> controls (specimen location / rotation) are <strong>UI-only</strong>. A bare <code>sample:</code> key in YAML is ignored on load and is not written on export. See <a href="./unit-tests.md">Unit Tests</a> to verify a loaded file against the live scene.</p>

<p><strong>Allowed values and ranges (quick reference)</strong></p>

<p><strong>world</strong></p>
<ul>
  <li><code>color</code>: 4 floats (RGBA), each in 0.0–1.0</li>
  <li><code>strength</code>: float, ≥ 0.0</li>
</ul>

<p><strong>dataset</strong></p>
<ul>
  <li><code>filepath</code>: string path to a CSV/TSV/XLSX dataset file</li>
</ul>

<p><strong>camera</strong></p>
<ul>
  <li><code>location</code>, <code>rotation</code>: 3 floats each</li>
  <li><code>camera_type</code>: <code>PERSP</code> | <code>ORTHO</code> | <code>PANO</code></li>
  <li><code>focal_length</code>: float, ≥ 0.0</li>
  <li><code>resolution_x</code>, <code>resolution_y</code>: integers</li>
  <li><code>resolution_percentage</code>: integer in 0–100</li>
  <li><code>aspect_x</code>, <code>aspect_y</code>: floats</li>
  <li><code>shift_x</code>, <code>shift_y</code>: floats</li>
  <li><code>lens_unit</code>: <code>MILLIMETERS</code> | <code>FOV</code></li>
</ul>

<p><strong>lamp</strong></p>
<ul>
  <li><code>location</code>, <code>rotation</code>, <code>scale</code>: 3 floats each</li>
  <li><code>color</code>: 3 floats (RGB), each in 0.0–1.0</li>
  <li><code>power</code>: float, ≥ 0.0</li>
  <li><code>use_soft_falloff</code>, <code>shadow</code>: booleans</li>
  <li><code>beam_size</code>: float in 0.0–10.0</li>
  <li><code>beam_blend</code>: float, ≥ 0.0</li>
  <li><code>diffuse</code>: float, ≥ 0.0</li>
</ul>

<p><strong>mat</strong></p>
<ul>
  <li><code>tb_location</code>, <code>tb_rotation</code>, <code>scale</code>: 3 floats each</li>
  <li><code>color</code>: 4 floats (RGBA), each in 0.0–1.0</li>
  <li><code>roughness</code>: float in 0.0–1.0</li>
</ul>

<p><strong>render</strong></p>
<ul>
  <li><code>engine</code>: <code>CYCLES</code> | Eevee (<code>BLENDER_EEVEE</code> / <code>BLENDER_EEVEE_NEXT</code>; both accepted) | <code>BLENDER_WORKBENCH</code></li>
  <li><code>cycles</code> (used when <code>engine</code> is <code>CYCLES</code>; written on export only for Cycles):
    <ul>
      <li><code>use_adaptive_sampling</code>, <code>adaptive_threshold</code>, <code>samples</code>, <code>adaptive_min_samples</code>, <code>time_limit</code>, <code>use_denoising</code> — final render sampling</li>
      <li><code>use_preview_adaptive_sampling</code>, <code>preview_adaptive_threshold</code>, <code>preview_samples</code>, <code>preview_adaptive_min_samples</code>, <code>use_preview_denoising</code> — viewport sampling</li>
    </ul>
  </li>
  <li><code>eevee</code> (used when engine is Eevee; written on export only for Eevee):
    <ul>
      <li><code>use_raytracing</code>: boolean</li>
      <li><code>taa_render_samples</code>: integer (Samples)</li>
    </ul>
  </li>
  <li>Legacy flat <code>eevee_use_raytracing</code> is still accepted on load</li>
</ul>

<p><strong>output</strong></p>
<ul>
  <li><code>rendering_directory</code>, <code>output_directory</code>: directory paths (strings)</li>
  <li><code>output_type</code>: <code>image</code> | <code>video</code></li>
  <li><code>image_format</code>: <code>PNG</code> | <code>JPEG</code></li>
  <li><code>images_per_view</code>: integer, ≥ 1</li>
</ul>

<p><strong>metadata</strong></p>
<ul>
  <li>All <code>use_stamp_*</code>: booleans</li>
  <li><code>stamp_note_text</code>: string</li>
</ul>

<p><strong>ruler</strong></p>
<ul>
  <li><code>tb_location</code>, <code>tb_rotation</code>: 3 floats each</li>
  <li><code>hide</code>: boolean</li>
</ul>

<p><strong>imaging</strong></p>
<ul>
  <li><code>include_images</code>: boolean</li>
  <li><code>orientation_names</code>: list of strings (built-in and/or custom orientation names to include in the pipeline)</li>
  <li><code>custom_orientations</code>: optional map of name → <code>[rx, ry, rz]</code> Euler angles in <strong>radians</strong>. Each custom orientation runs the morphospace Default, then applies the Euler in the specimen's <strong>local</strong> frame (relative to the post-Default pose, before bake), then recenters at geometry bounds. Available for all morphospaces; names must not collide with built-ins. Use simple keys: letters, digits, <code>_</code>, and <code>-</code> only (no spaces, quotes, or backslashes) so YAML export round-trips reliably.</li>
  <li><code>images_per_orientation</code>: integer, ≥ 1</li>
</ul>

<p><strong>meshes</strong></p>
<ul>
  <li><code>save_meshes</code>: boolean</li>
  <li><code>orient_before_export</code>: boolean (default <code>true</code>). When saving meshes in the imaging pipeline, apply the morphospace <strong>Default</strong> orientation before export. Set to <code>false</code> to export the generated mesh as-is (recommended for ATLAS, where the SSM already provides a consistent PCA-aligned frame). Imaging orientations are still applied afterward for renders.</li>
  <li><code>file_export_type</code>: <code>obj</code> or <code>ply</code></li>
</ul>

<p><strong>morphospace</strong></p>
<ul>
  <li><code>name</code>: morphospace display name (e.g. <code>Shell (Default)</code>)</li>
  <li><code>hyperparams</code>: mapping of morphospace-specific keys to values (keys differ by morphospace)</li>
</ul>

<p><strong>transforms</strong></p>
<ul>
  <li><code>sampler_name</code>: currently <code>normal</code>
    <ul>
      <li><code>params.mu</code>: float</li>
      <li><code>params.sigma</code>: float (use &gt; 0 for meaningful variation)</li>
    </ul>
  </li>
  <li><code>property_path</code>: supported scalar paths such as:
    <ul>
      <li><code>world.color.r|g|b|a</code>, <code>world.strength</code></li>
      <li><code>camera.location.x|y|z</code>, <code>camera.rotation.x|y|z</code></li>
      <li><code>camera.focal_length</code>, <code>camera.shift_x</code>, <code>camera.shift_y</code></li>
      <li><code>lamp.location.x|y|z</code>, <code>lamp.rotation.x|y|z</code></li>
      <li><code>lamp.color.r|g|b</code>, <code>lamp.power</code></li>
      <li><code>mat.tb_location.x|y|z</code>, <code>mat.tb_rotation.x|y|z</code></li>
      <li><code>mat.color.r|g|b|a</code>, <code>mat.roughness</code></li>
      <li><code>sample.tb_location.x|y|z</code>, <code>sample.tb_rotation.x|y|z</code></li>
    </ul>
  </li>
</ul>

</details>

<details>
<summary>Example 1: Minimal “museum image” config</summary>

This is a good starting point if you want a stable, repeatable setup with no augmentation.

```yaml
morphospace:
  name: Shell (Default)
  hyperparams: {}

world:
  color: [0.0, 0.0, 0.0, 1.0]
  strength: 1.0

camera:
  location: [0.0, 0.0, 1.0]
  rotation: [0.0, 0.0, 0.0]
  camera_type: PERSP
  focal_length: 60.0
  resolution_x: 1920
  resolution_y: 1920
  resolution_percentage: 100
  aspect_x: 1.0
  aspect_y: 1.0
  shift_x: 0.0
  shift_y: 0.0
  lens_unit: MILLIMETERS

lamp:
  location: [0.0, 0.0, 1.0]
  rotation: [0.0, 0.0, 0.0]
  scale: [1.0, 1.0, 1.0]
  color: [1.0, 1.0, 1.0]
  power: 10.0
  use_soft_falloff: true
  beam_size: 1.0
  beam_blend: 0.0
  shadow: true
  diffuse: 1.0

mat:
  tb_location: [0.0, 0.0, 0.59]
  tb_rotation: [0.0, 0.0, 0.0]
  scale: [0.125, 0.125, 1.0]
  color: [0.0, 0.0, 0.0, 1.0]
  roughness: 1.0

render:
  engine: BLENDER_EEVEE  # or CYCLES / BLENDER_EEVEE_NEXT
  eevee:
    use_raytracing: false
    taa_render_samples: 64
  # When using Cycles, use a cycles: block instead, for example:
  # engine: CYCLES
  # cycles:
  #   use_adaptive_sampling: true
  #   adaptive_threshold: 0.01
  #   samples: 4096
  #   adaptive_min_samples: 0
  #   time_limit: 0.0

output:
  rendering_directory: ""   # The directory where simulation output will be written
  output_type: image
  image_format: PNG
  output_directory: ""
  images_per_view: 1

metadata:
  use_stamp_date: true
  use_stamp_time: true
  use_stamp_render_time: true
  use_stamp_frame: true
  use_stamp_frame_range: false
  use_stamp_memory: false
  use_stamp_hostname: false
  use_stamp_camera: true
  use_stamp_lens: false
  use_stamp_scene: true
  use_stamp_marker: false
  use_stamp_filename: true
  use_stamp_sequencer_strip: false
  use_stamp_note: false
  stamp_note_text: ""

ruler:
  tb_location: [0.0, -0.1, 0.0]
  tb_rotation: [0.0, 0.0, 0.0]
  hide: false

transforms: []

imaging:
  include_images: true
  orientation_names: []
  images_per_orientation: 1
  # Optional named Euler orientations (radians), usable by any morphospace:
  # custom_orientations:
  #   Side: [1.5708, 0.0, 0.0]
  #   Dorsal: [0.0, 1.5708, 0.0]

meshes:
  file_export_type: obj
  save_meshes: false
  orient_before_export: true
```

 </details>

<details>
<summary>Example 2: Simulation that saves meshes (and skips images)</summary>

If you only want meshes during simulation (no rendered images), these are the important toggles:

```yaml
output:
  rendering_directory: "C:/path/to/simulation-output"

imaging:
  include_images: false

meshes:
  file_export_type: obj
  save_meshes: true
  # ATLAS: keep SSM/PCA frame (skip Default table placement before export)
  # orient_before_export: false
```

 </details>

<details>
<summary>Example 3: Morphospace hyperparameters (non-empty)</summary>

Hyperparameters are **morphospace-specific** (they are not part of the dataset). Here is a real example for **Shell (Default)**:

```yaml
morphospace:
  name: Shell (Default)
  hyperparams:
    n_vertices_aperture: 24
    time_step: 0.03
    use_inner_surface: true
```

 </details>

<details>
<summary>Example 4: Transforms (non-empty)</summary>

Transforms apply **random variation** during rendering/simulation. Each transform has:

- `property_path`: which setting to change
- `sampler_name`: how to sample the change
- `params`: parameters for the sampler

```yaml
transforms:
  - property_path: lamp.power
    sampler_name: normal
    params:
      mu: 0.0
      sigma: 2.0

  - property_path: camera.location.z
    sampler_name: normal
    params:
      mu: 0.0
      sigma: 0.05

  - property_path: world.strength
    sampler_name: normal
    params:
      mu: 0.0
      sigma: 0.2
```

 </details>

<details>
<summary>Example 5: Modern “Circle Grid + CYCLES” config</summary>

This example shows a modern YAML config structure you can load via `Configure Scene`. Sections omitted from the YAML fall back to the current Blender default values for those settings. It renders the `Circle Grid` morphospace using `CYCLES`, with transforms empty.

```yaml
morphospace:
  name: Circle Grid
  hyperparams:
    {}

dataset:
  filepath: "/home/calebc22/projects/tbd/datasets/circle_grid_50sp_32tr_mu5sd1.csv"

world:
  color: [1.0, 1.0, 1.0, 1.0]
  strength: 1.0

camera:
  location: [0.0, 0.0, 1.1]
  aspect_x: 1.0
  aspect_y: 1.0
  camera_type: PERSP
  focal_length: 60.0
  lens_unit: MILLIMETERS
  resolution_percentage: 100
  resolution_x: 220
  resolution_y: 220
  rotation: [0.0, 0.0, 0.0]
  shift_x: 0.0
  shift_y: 0.0

lamp:
  location: [0.0, 0.0, 1.0]
  beam_blend: 0.0
  beam_size: 1.0
  color: [1.0, 1.0, 1.0]
  diffuse: 1.0
  power: 0.0
  rotation: [0.0, 0.0, 0.0]
  scale: [1.0, 1.0, 1.0]
  shadow: true
  use_soft_falloff: true

ruler:
  tb_location: [0.0, -0.1, 0.0]
  tb_rotation: [0.0, 0.0, 0.0]
  hide: true

mat:
  color: [0.0, 0.0, 0.0, 1.0]
  tb_location: [0.0, 0.0, 0.0]
  tb_rotation: [0.0, 0.0, 0.0]
  roughness: 1.0
  scale: [0.15, 0.15, 1.0]

render:
  engine: CYCLES
  cycles:
    use_adaptive_sampling: true
    adaptive_threshold: 0.01
    samples: 4096
    adaptive_min_samples: 0
    time_limit: 0.0

output:
  image_format: PNG
  images_per_view: 1
  rendering_directory: "/home/calebc22/projects/tbd/simulations/shell_test_1"
  output_type: image

imaging:
  include_images: true
  orientation_names: ['Default', 'Side']
  custom_orientations:
    Side: [1.5708, 0.0, 0.0]
  images_per_orientation: 1

metadata:
  stamp_note_text: ""
  use_stamp_camera: true
  use_stamp_date: true
  use_stamp_filename: true
  use_stamp_frame: true
  use_stamp_frame_range: false
  use_stamp_hostname: false
  use_stamp_lens: false
  use_stamp_marker: false
  use_stamp_memory: false
  use_stamp_note: false
  use_stamp_render_time: true
  use_stamp_scene: true
  use_stamp_sequencer_strip: false
  use_stamp_time: true

transforms: []
```

</details>

## Using config files

1. Export a YAML from the GUI (**Export Config as YAML**), or edit one by hand using the schema above.
2. In **Museum Setup**, set **Config File** (or leave it empty and pick a file when prompted) and click **Configure Scene**.
3. After a successful load, the chosen path is stored on `traitblender_setup.config_file` so the field and [unit tests](./unit-tests.md) stay in sync.

### Custom orientations in YAML

Under `imaging.custom_orientations`, map a unique name to Euler angles `[rx, ry, rz]` in **radians**. Built-in morphospace orientation names always win on collision. Customs are available for every morphospace: they run **Default**, apply the Euler in the specimen’s **local** frame (relative to the post-Default pose, before bake), then recenter at geometry bounds. List those names in `orientation_names` to include them in the imaging pipeline.

Names should be simple identifiers: letters, digits, underscores, and hyphens only (e.g. `Side`, `Left-view`). Avoid spaces, quotes, and backslashes—unusual characters can break YAML export/import round-trips.

### Mesh export in the imaging pipeline

When `meshes.save_meshes` is `true`, the simulation pipeline writes one mesh per specimen under `rendering_directory/meshes/<specimen>/` **before** imaging orientations and transform randomization run for that specimen’s renders.

`meshes.orient_before_export` (default `true`) controls the pose of that file:

| Value | Mesh file contents |
|-------|--------------------|
| `true` (default) | Morphospace **Default** applied first (table placement). Same behavior as earlier TraitBlender releases. |
| `false` | Export the mesh as generated, with no Default/table orientation. Prefer this for **ATLAS**, where the SSM already lives in a shared PCA-aligned frame. Imaging orientations still apply afterward for rendered images only. |

```yaml
meshes:
  file_export_type: obj   # or ply
  save_meshes: true
  orient_before_export: false
```

### Verifying a load

After Configure Scene, run `config_matches_scene` (see [Unit Tests](./unit-tests.md)) to confirm the YAML still matches the live scene—including Cycles/Eevee **render** vs **viewport** sampling keys.
