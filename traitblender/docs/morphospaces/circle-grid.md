# Circle Grid

The **Circle Grid** morphospace generates a white cube with a 4×4 grid of black circles on the top face.  
Each circle has two traits:

- **opacity** (how dark the circle is)
- **diameter** (relative size)

<div style="display: flex; justify-content: center; align-items: flex-end; gap: 1rem; flex-wrap: wrap; margin: 1rem 0;">
  <img src="../../images/Morphospace%20Samples/circle_grid-1.png" alt="Circle Grid morphospace sample 1" width="216" />
  <img src="../../images/Morphospace%20Samples/circle_grid-2.png" alt="Circle Grid morphospace sample 2" width="216" />
  <img src="../../images/Morphospace%20Samples/circle_grid-3.png" alt="Circle Grid morphospace sample 3" width="216" />
</div>

## Traits (dataset columns)

The traits are `opacity_0`–`opacity_15` and `diameter_0`–`diameter_15`, row-major over the 4×4 grid.

| Trait name pattern | Default | Description | Typical range / notes |
|--------------------|---------|-------------|------------------------|
| `opacity_0` … `opacity_15` | `1.0` | Per-circle darkness control. In the current implementation, circles are **opaque** (no BSDF transparency); `opacity=0` makes the circle white and `opacity=1` makes it black. | Use values between `0.0` and `1.0`. |
| `diameter_0` … `diameter_15` | `0.0` | Size trait for each circle. The physical size is scaled as \(2^{\text{diameter}}\). | `0` ≈ default size. `1` = 2×, `2` = 4× default diameter. Values in `(0, 0.01)` are treated as `0`. |

The traits are ordered as:

```text
opacity_0, opacity_1, ..., opacity_15
diameter_0, diameter_1, ..., diameter_15
```

## Hyperparameters

Circle Grid currently has **no extra hyperparameters** (`HYPERPARAMETERS = {}`), so you do not need a `hyperparams` block in the config for this morphospace.

## Orientations

Circle Grid includes built-in orientations (including **Default**). Custom Euler orientations from the Orientations panel / `imaging.custom_orientations` apply the same way as for other morphospaces — see [Morphospaces overview](overview.md#orientations).

