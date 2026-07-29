# API Reference

This reference focuses on the user-facing operators and properties you will use in normal TraitBlender workflows.

<details>
<summary>1. Museum Setup</summary>

<p><code>bpy.ops.traitblender.setup_scene()</code></p>
<p>Load the pre-configured museum scene with the camera, lighting, and table objects needed for morphospace work.</p>

<hr>

<p><code>bpy.ops.traitblender.clear_scene()</code></p>
<p>Remove the current scene contents so you can start from a clean state.</p>

<hr>

<p><code>bpy.ops.traitblender.add_ruler()</code></p>
<p>Append a ruler object from the museum scene and apply ruler configuration (location, rotation, visibility). Each invocation adds another ruler; Blender handles duplicate naming.</p>

</details>

<details>
<summary>2. Configuration</summary>

<p><code>bpy.context.scene.traitblender_config</code></p>
<p>The main configuration <code>PropertyGroup</code> containing all scene settings.</p>

<hr>

<p><code>bpy.context.scene.traitblender_setup.config_file</code></p>
<p>Path to the YAML used by <strong>Configure Scene</strong> and by the <code>config_matches_scene</code> unit test. After a successful configure (including via the file browser), this property is updated to the absolute path that was loaded.</p>

<hr>

<p><code>bpy.ops.traitblender.configure_scene(filepath="")</code></p>
<p>Load a YAML config and apply it to the scene. If <code>filepath</code> is empty and <code>config_file</code> is unset, opens a file browser. Persists the chosen path on <code>traitblender_setup.config_file</code>.</p>

<hr>

<p><code>bpy.ops.traitblender.show_configuration()</code></p>
<p>Print the current configuration as YAML for inspection or copying.</p>

<hr>

<p><code>bpy.ops.traitblender.export_config(filepath="")</code></p>
<p>Export the current configuration to a YAML file.</p>

<hr>

<p><code>bpy.ops.traitblender.run_unit_test(test_name="help")</code></p>
<p>Run an in-addon unit test by name. Use <code>test_name="help"</code> to list tests. See <a href="../configuration/unit-tests.md">Unit Tests</a>.</p>

</details>

<details>
<summary>3. Morphospaces</summary>

<p><code>bpy.context.scene.traitblender_setup.available_morphospaces</code></p>
<p>Select the active morphospace. Changing it can alter the available parameters, orientations, and default dataset.</p>

<hr>

<p><code>bpy.context.scene.traitblender_dataset.sample</code></p>
<p>Select the current specimen or sample name from the active dataset.</p>

<hr>

<p><code>bpy.ops.traitblender.generate_morphospace_sample()</code></p>
<p>Generate a morphospace sample object using the selected sample and morphospace settings.</p>

<hr>

<p><code>bpy.ops.traitblender.apply_orientation(orientation="")</code></p>
<p>Apply a named orientation to the current sample by <strong>name</strong> (built-in or custom). Pass <code>orientation</code> explicitly (recommended for scripts/pipeline); if empty, uses the Orientations panel selection. Imaging folders and logs should use the same name string that was applied.</p>

<hr>

<p><code>bpy.context.scene.traitblender_config.imaging.custom_orientations</code></p>
<p>Named custom Euler orientations (<code>name</code>, <code>rotation</code> as <code>[rx, ry, rz]</code> radians). For every morphospace: run Default → apply Euler in the specimen's <strong>local</strong> frame (relative to the post-Default pose, before bake) → recenter at geometry bounds. Merged with built-ins for Apply and imaging; built-in names win on collision. YAML: <code>imaging.custom_orientations</code>.</p>

<hr>

<p><code>bpy.ops.traitblender.add_custom_orientation()</code> / <code>bpy.ops.traitblender.remove_custom_orientation()</code></p>
<p>Add or remove a custom orientation entry in the Orientations panel (also reflected in Imaging checkboxes and YAML export).</p>

</details>

<details>
<summary>4. Datasets</summary>

<p><code>bpy.context.scene.traitblender_dataset.filepath</code></p>
<p>Path to the dataset file on disk.</p>

<hr>

<p><code>bpy.context.scene.traitblender_dataset.sync_sample_with_active_object</code></p>
<p>When <code>True</code> (default), automatically set <code>sample</code> to match the active object name when that name is a row in the dataset.</p>

<hr>

<p><code>bpy.ops.traitblender.import_dataset()</code></p>
<p>Import CSV, TSV, or Excel data into the in-memory dataset.</p>

<hr>

<p><code>bpy.ops.traitblender.edit_dataset()</code></p>
<p>Open the dataset editor and modify the current dataset interactively.</p>

<hr>

<p><code>bpy.ops.traitblender.export_dataset()</code></p>
<p>Export the current dataset to a CSV file.</p>

</details>

<details>
<summary>5. Transforms</summary>

<p><code>bpy.context.scene.traitblender_config.transforms</code></p>
<p>Transform pipeline settings and state.</p>

<hr>

<p><code>bpy.ops.traitblender.run_pipeline()</code></p>
<p>Run the transform pipeline on the current specimen.</p>

<hr>

<p><code>bpy.ops.traitblender.undo_pipeline()</code></p>
<p>Undo the last transform step.</p>

<hr>

<p><code>bpy.ops.traitblender.reset_pipeline()</code></p>
<p>Reset the pipeline back to its initial state.</p>

</details>

<details>
<summary>6. Meshes</summary>

<p><code>bpy.context.scene.traitblender_config.meshes.file_export_type</code></p>
<p>Choose the mesh export format used by the mesh exporter and simulation pipeline.</p>

<hr>

<p><code>bpy.context.scene.traitblender_config.meshes.save_meshes</code></p>
<p>If enabled, save a mesh export during simulation.</p>

<hr>

<p><code>bpy.ops.traitblender.export_mesh()</code></p>
<p>Export the current sample as a mesh file using the selected format.</p>

</details>

<details>
<summary>7. Imaging and Simulation</summary>

<p><code>bpy.context.scene.traitblender_config.imaging</code></p>
<p>Controls for the imaging pipeline, including whether to render images during simulation.</p>

<hr>

<p><code>bpy.context.scene.traitblender_config.output.rendering_directory</code></p>
<p>Root directory used for simulation output.</p>

<hr>

<p><code>bpy.ops.traitblender.imaging_pipeline()</code></p>
<p>Run the full simulation pipeline for the current dataset.</p>

</details>

<details>
<summary>User-facing properties</summary>

<p><code>bpy.context.scene.traitblender_config</code></p>
<p>Main configuration object for all TraitBlender settings.</p>

<hr>

<p><code>bpy.context.scene.traitblender_setup</code></p>
<p>Setup state for morphospace selection, <code>config_file</code>, and related UI.</p>

<hr>

<p><code>bpy.context.scene.traitblender_dataset</code></p>
<p>The current dataset and its editable CSV contents.</p>

<hr>

<p><code>bpy.context.scene.traitblender_orientation</code></p>
<p>The currently selected orientation.</p>

<hr>

<p><code>bpy.context.scene.traitblender_sample</code></p>
<p>The current sample object.</p>

</details>

## Notes

- The [Python tooltip](../getting-started/blender-optimization.md#python-tooltips) in Blender is usually enough to discover the matching API call for a given button or property.
- TraitBlender assumes a **single active scene** (and view layer). Config, operators, imaging sync, and orientations all use that context—multi-scene setups are not supported.
- Custom orientation names should be simple identifiers (letters, digits, `_`, `-`) so YAML export/import round-trips; see [Configuration Files](../configuration/config-files.md#custom-orientations-in-yaml).