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
  <li><code>imaging</code> – which orientations to render and how many images</li>
  <li><code>meshes</code> – mesh export options during simulation</li>
</ul>

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
  <li><code>engine</code>: <code>CYCLES</code> | Eevee (<code>BLENDER_EEVEE_NEXT</code> or <code>BLENDER_EEVEE</code>, depending on Blender version; YAML values are normalized on load) | <code>BLENDER_WORKBENCH</code></li>
  <li><code>eevee_use_raytracing</code>: boolean</li>
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
  <li><code>orientation_names</code>: list of strings (orientation names from the selected morphospace)</li>
  <li><code>images_per_orientation</code>: integer, ≥ 1</li>
</ul>

<p><strong>meshes</strong></p>
<ul>
  <li><code>save_meshes</code>: boolean</li>
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
  engine: BLENDER_EEVEE_NEXT  # or BLENDER_EEVEE on Blender 5.1+; both accepted in YAML
  eevee_use_raytracing: false

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

meshes:
  file_export_type: obj
  save_meshes: false
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
  eevee_use_raytracing: false
  engine: CYCLES

output:
  image_format: PNG
  images_per_view: 1
  rendering_directory: "/home/calebc22/projects/tbd/simulations/shell_test_1"
  output_type: image

imaging:
  include_images: true
  orientation_names: ['Default']
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

Use the GUI to export a YAML (recommended), then reuse it later by loading it back into the Configuration panel workflow.
