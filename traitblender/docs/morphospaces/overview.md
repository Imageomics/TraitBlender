# Morphospaces

TraitBlender currently includes three morphospaces:

- **[Shell (Default)](shell.md)** – a 3D shell model based on Contreras-Figueroa & Aragón (2023)
- **[Circle Grid](circle-grid.md)** – a white cube with a 4×4 grid of black circles on top
- **[ATLAS](atlas.md)** – PCA + local RBF deformation of a template mesh from an ATLAS DATABASE export

Each morphospace has a **name** (e.g. "Shell (Default)", "Circle Grid", "ATLAS") used in the GUI and in config files, and:

- **traits** – columns in the dataset (per-specimen values)
- **hyperparameters** – extra settings that affect how the model is generated (set in the Configuration panel)
- **orientations** – named poses for the specimen on the table (built-in per morphospace, plus optional custom Eulers)

## Orientations

Built-in orientation functions live with each morphospace (always including **Default**). In the **Orientations** panel you can also add **custom orientations**: a name plus Euler `(rx, ry, rz)` in radians. For any morphospace, a custom orientation:

1. Runs **Default**
2. Applies the Euler in the specimen’s **local** frame (relative to the post-Default pose, before bake)
3. Recenters at geometry bounds

Customs show up in the Apply dropdown and Imaging checkboxes, and persist via YAML (`imaging.custom_orientations`). Built-in names win if a custom name collides. Prefer simple names (letters, digits, `_`, `-`); avoid spaces, quotes, and backslashes so configs round-trip cleanly. See the [configuration reference](../configuration/config-files.md) and [API](../api/scene-assets.md).

Follow the links above for the full list of parameters, default values, and ranges that make sense in practice.
