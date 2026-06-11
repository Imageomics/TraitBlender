# Quick Start Guide (GUI)

Get up and running with TraitBlender's graphical interface in just a few minutes! This guide will walk you through creating your first museum-style specimen image using Blender's user interface.

## Prerequisites

Before starting, ensure you have:

- ✅ **Blender 5.1+** and **TraitBlender v2.3.0** ([supported versions](./installation.md#supported-versions))
- ✅ TraitBlender add-on installed ([Installation Guide](./installation.md))

??? note "Step 0: Enable TraitBlender"
    1. Open Blender
    2. Go to **Edit → Preferences → Add-ons**
    3. Search for "TraitBlender" 
    4. Enable the checkbox next to **TraitBlender**
    5. The TraitBlender panel should now appear in the **3D Viewport sidebar** (press `N` if hidden)

    If you want TraitBlender to be activated by default when opening Blender, you must save your preferences after activation with **Edit → ☰ → Save Preferences**.

??? note "Step 1: Open the Museum Scene"
    1. In the TraitBlender panel, find the **"1 Museum Setup"** panel
    2. Click the **"Import Museum"** button
    3. After a moment, the scene will load with a museum table, lighting, and camera setup
    4. Press `0` on your numpad (or `0` with Emulate Numpad enabled) to switch to Camera View
    5. You should now be looking through the camera at the empty mat lying on the table

    ### Add a Ruler

    If the ruler object is missing or you need another copy, click **Add Ruler** in the **Museum Setup** panel. Each click appends a ruler from the museum scene and applies the ruler settings from your configuration (location, rotation, visibility). Blender assigns duplicate names automatically (e.g. `Ruler.001`).

    !!! tip "Emulate Numpad"
        If you don't have a numpad, go to **Edit → Preferences → Input** and check **Emulate Numpad**. This allows you to use the number keys at the top of your keyboard as a numpad.

??? note "Step 2: Configure the Scene"
    Collapse the **Museum Setup** panel and expand the **"2 Configuration"** panel.

    The configuration system stores all scene settings (camera, lighting, world, materials, etc.) as a structured PropertyGroup at `bpy.context.scene.traitblender_config`. The Configuration Panel provides a visual interface for these settings.

    In this panel, you'll see several collapsible sections:

    - **World** - Background color and lighting strength
    - **Camera** - Position, rotation, focal length, resolution
    - **Lamp** - Lighting position, color, power, and properties
    - **Mat** - Specimen mat color, position, and scale
    - **Render** - Render engine settings
    - **Output** - Image output format and directory
    - **Metadata** - Information to include in rendered images
    - **Morphospace** - Selected morphospace and related settings
    - **Sample** - Controls for the current specimen in the scene
    - **Transforms** - The transform pipeline for simulation and augmentation
    - **Ruler** - Measurements and scale-related settings

    Click the arrow next to any section to expand it and adjust settings. Changes are immediately reflected in the scene.

    ### Viewing and Exporting Configuration

    - **Show Configuration**: Click this button to see all configuration values in a popup window
    - **Export Config as YAML**: Export your current configuration to a YAML file for reuse

    ### Importing Configuration

    1. In the **Museum Setup** panel, enter a path to a YAML config file in the **Config File** field
    2. Click **Configure Scene** to load the configuration

    !!! warning "Scene Requirements"
        Configuration import only works if the museum scene has been loaded (via **Import Museum**). If you encounter issues, click **Clear Scene** and re-import the museum scene.

??? note "Step 3: Select a Morphospace"
    Expand the **"3 Morphospaces"** panel.

    TraitBlender generates 3D specimens from mathematical models called **morphospaces**. The dropdown lists three built-in options (in order):

    - **Shell (Default)** — parametric mollusc shells ([Contreras-Figueroa & Aragón](https://www.mdpi.com/1424-2818/15/3/431); thickness from [Okabe & Yoshimura](https://doi.org/10.1038/srep42445))
    - **Circle Grid** — simple test morphospace (cube with a 4×4 grid of circles)
    - **ATLAS** — deform a template mesh from an [ATLAS DATABASE](https://github.com/agporto/ATLAS) export using PCA + local RBF ([details](../morphospaces/atlas.md))

    Select the morphospace that matches your dataset.

    For **ATLAS**, set **`database_dir`** under Configuration → morphospace hyperparameters before generating samples.

??? note "Step 4: Import and Manage Datasets"
    Expand the **"4 Datasets"** panel.

    ### Import a Dataset

    1. Click the folder icon next to **Dataset File**
    2. Select a CSV, TSV, or Excel (.xlsx, .xls) file containing your morphological data
    3. TraitBlender will automatically:
       - Detect the species/label column (looks for: species, label, tips, name, id, etc.)
       - Move the species column to the first position
       - Load the data into the system

    ### Dataset Format

    Your dataset should have:
    - **First column**: Species/specimen names (automatically detected)
    - **Remaining columns**: Morphological traits that map to morphospace parameters

    For Shell (Default), dataset trait columns include: `b`, `d`, `z`, `a`, `phi`, `psi`, `k`, `c_depth`, `c_n`, `n_depth`, `n`, `t`, `eps`, `h_0`, `S`. Mesh resolution and inner-surface options (`n_vertices_aperture`, `time_step`, `use_inner_surface`) are hyperparameters in the config file, not dataset columns—see the [Shell morphospace reference](../morphospaces/shell.md).

    ### Generate a Specimen

    1. After importing, select a specimen from the **Sample** dropdown
    2. Click **Generate Sample**
    3. A 3D shell will be generated and placed at the center of the table
    4. Use the **Sample Controls** section to adjust the specimen's position and rotation

    ### Sync Sample to Active

    Enable **Sync Sample to Active** (on by default) to keep the **Sample** dropdown aligned with your scene selection. When you select an object whose name exactly matches a specimen row in the dataset, TraitBlender updates **Sample** to that row automatically.

    ### Edit Dataset

    Click **Edit Dataset** to open the CSV viewer (DearPyGui). This allows you to:
    - View and filter your data
    - Sort by columns
    - Edit values
    - Export changes back to TraitBlender

    ### Export Dataset

    Click **Export Dataset** to save the current dataset to a CSV file.

??? note "Step 5: Orientations"
    Expand the **"5 Orientations"** panel.

    Each morphospace can define orientation functions in its `ORIENTATIONS` dictionary. Select an orientation from the dropdown and click **Apply** to orient the specimen. The selected orientation is also applied automatically when running the Imaging Pipeline.

??? note "Step 6: Transforms"
    Expand the **"6 Transforms"** panel.

    The transform pipeline lets you apply controlled variation to configuration values for simulation and augmentation. This is useful when you want to randomize scene settings between samples without changing the base configuration by hand.

    1. Use the transform controls to add items to the pipeline.
    2. Pick the property you want to vary and choose a sampler for it.
    3. Add more transforms if you want multiple properties randomized together.
    4. Use **Run Pipeline** to apply the transforms in order.
    5. Use **Undo** to revert the changes.


??? note "Step 7: Meshes"
    Expand the **"7 Meshes"** panel.

    1. Choose the mesh export type.
    2. Enable **Save Meshes** if you want the simulation pipeline to export meshes.
    3. You can also use **Export Mesh** to save the current sample manually.

??? note "Step 8: Imaging"
    Expand the **"8 Imaging"** panel.

    1. Use **Include Images** to control whether image files are rendered.
    2. Set the number of images per orientation if needed.
    3. Choose which orientations are included for the imaging run.

??? note "Step 9: Simulation"
    Use the separate **Simulation** section below the numbered panels.

    1. Set the **Simulation Directory**.
    2. Click **Simulate Dataset**.

    The simulation pipeline will:
    - Apply any configured transforms
    - Render from the current camera view
    - Save images when enabled
    - Export meshes when enabled
    - Include metadata if configured

## Next Steps

Congratulations! You've completed the basic workflow. Now you can:

- **Explore the API**: ([API Reference](../api/scene-assets.md))
- **Customize Configurations**: Create and save YAML configs for different imaging setups

For more detailed information, see:
- [API Reference](../api/scene-assets.md) - Complete API documentation
- [Configuration Files](../configuration/config-files.md) - Understanding YAML configs
- [Tutorials](../tutorials.md) - Step-by-step guides (in progress)



