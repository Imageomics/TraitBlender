# Shell (Default)

The **Shell (Default)** morphospace generates 3D shells from a parametric model of coiling geometry [Contreras-Figueroa & Aragón (2023)](https://doi.org/10.3390/d15030431), with thickness allometry following [Okabe & Yoshimura (2017)](https://doi.org/10.1038/srep42445).  

<div style="display: flex; justify-content: center; align-items: flex-end; gap: 1rem; flex-wrap: wrap; margin: 1rem 0;">
  <img src="../../images/Morphospace%20Samples/shell-1.png" alt="Shell morphospace sample 1" width="216" />
  <img src="../../images/Morphospace%20Samples/shell-2.png" alt="Shell morphospace sample 2" width="216" />
  <img src="../../images/Morphospace%20Samples/shell-3.png" alt="Shell morphospace sample 3" width="216" />
</div>

## Traits (dataset columns)

These correspond to arguments of `sample()` (excluding `name` and hyperparameters).  
In the paper, most of them control the **coiling geometry** and **aperture shape** along the growth axis.

| Trait name | Default | Description | Range (paper) |
|-----------|---------|-------------|----------------|
| `b` | `0.2` | **Whorl expansion rate.** How fast the spiral and generating curve of the shell expand. | 0 ≤ b < ∞. b = 0 → torus; b → ∞ → straight shell. |
| `d` | `1.65` | **Horizontal distance** from the spiral to the coiling axis. | 0 < d < ∞. d → ∞ → infinitely expanded shell. |
| `z` | `0` | **Vertical translation** of the spiral (vertical distance to the x–y plane). | −∞ < z < ∞. Dextral: z > 0; sinistral: z < 0; planispiral: z = 0. |
| `a` | `1` | **Ratio of major to minor axes** of the ellipse modeling the aperture. | 0 < a < ∞. Narrow: a < 1; circular: a = 1; wide: a > 1. |
| `phi` | `0` | **Initial tilt angle** of the aperture before it is placed in the Frenet frame. | 0 ≤ φ < π. |
| `psi` | `0` | **Rotation angle** around the binormal axis in the local Frenet frame. | 0 ≤ ψ < π/2 to avoid invagination. |
| `k` | `0` | **Aperture displacement** along the binormal in generating-curve units (Contreras §2.7.3). Shifts the whole generating curve before the ψ rotation. Positive = right valve; negative = left valve. | 0 for most coiled shells; valve-like forms often ≠ 0. |
| `c_depth` | `0` | **Axial ribbing amplitude** on the outer surface. Scales the generating curve by `1 + c_depth(1 + sin(c_n t))`; rib troughs sit on the unribbed outer profile, peaks extend outward. | 0 = no axial ribs. |
| `c_n` | `70` | **Axial ribbing frequency.** Number of axial rib cycles per 2π radians of growth (parameter `t`). | ≥ 0; e.g. 70 ≈ 70 rib cycles per full turn of the spiral. |
| `n_depth` | `0` | **Spiral ribbing amplitude** on the outer surface. Scales the generating curve by `1 + n_depth(1 + sin(n θ))`; rib troughs sit on the unribbed outer profile, peaks extend outward. | 0 = no spiral ribs. |
| `n` | `0` | **Spiral ribbing frequency.** Number of rib cycles around the aperture circumference (parameter θ). | ≥ 0; e.g. 0, 4, 8, 12. |
| `t` | `100` | **End of the growth interval** in the parametric curve (growth parameter in **radians**). | Positive; larger values = more whorls (one whorl ≈ 2π radians). |
| `eps` | `0.8` | **Thickness allometry exponent (ε).** Wall thickness scales as (aperture size)^eps. eps = 1 is isometric (thickness ∝ size); eps &lt; 1 is allometric (thickness grows more slowly than aperture size, as in many ammonoids). | 0 = constant thickness; 1 = isometric; &lt; 1 typical for real shells (e.g. ≈ 0.8). |
| `h_0` | `0.1` | **Reference thickness.** Scale factor in the thickness formula: thickness = (aperture size)^eps × h_0. | Small positive (e.g. 0.01–0.3). |
| `S` | `5.0` | **Target final aperture diameter** (cm) measured parallel to the local binormal direction; sets global physical scale from that axis. Based on the unribbed generating curve. | &gt; 0. |

**Note.** When global scaling by `S` is enabled, parameters estimated from Contreras-Figueroa & Aragón (2023) must be converted to TraitBlender units by dividing by

$$
s_f = \frac{S}{200\left(e^{bt}-\frac{1}{t+1}\right)\sqrt{(a\sin\phi)^{2}+\cos^{2}\phi}}
$$

The factor 200 combines the aperture-diameter factor of 2 with 100 to convert `S` from centimeters to meters (Blender's native length unit). Only `d`, `z`, `h_0`, and `k` require this correction; all other parameters are dimensionless and require none.

## Ribbing and wall thickness

Ribbing applies to the **outer surface only**. Axial and spiral rib factors multiply on the outer generating curve:

- Axial: `1 + c_depth(1 + sin(c_n t))`
- Spiral: `1 + n_depth(1 + sin(n θ))`

At each sine minimum (`sin = −1`), the rib factor is `1`, so the outer profile matches the unribbed shell. At sine maxima, the outer wall extends beyond that baseline. Setting a depth amplitude to `0` disables that rib type.

**Wall thickness** (Okabe & Yoshimura) is computed from the smooth, unribbed generating curve and is not modulated by ribbing; ribs add outward displacement on top of that baseline thickness.

**Global scaling (`S`)** is likewise based on the unribbed final aperture diameter in the binormal direction; rib peaks can exceed that target size.

## Hyperparameters (configuration)

These live under the `morphospace.hyperparams` section in the config file.

| Hyperparameter | Default | Description | Typical range / notes |
|----------------|---------|-------------|------------------------|
| `n_vertices_aperture` | `20` | Number of points around each aperture ring (mesh resolution). | Integers ~12–64. Higher = smoother but heavier. |
| `time_step` | `0.05` | Step size for the growth parameter `t`. | Positive; smaller = more segments (smoother shells). |
| `use_inner_surface` | `false` | Whether to generate an inner surface with wall thickness. | Enable when you need closed/thick shells for meshes. |

To change these hyperparameters, edit the YAML:

```yaml
morphospace:
  name: Shell (Default)
  hyperparams:
    n_vertices_aperture: 24
    time_step: 0.03
    use_inner_surface: true
```

## References

- Contreras-Figueroa, R. & Aragón, L. (2023). A mathematical model for mollusc shells based on parametric surfaces and the application to *Conus* shells. *Diversity* **15**, 431. [https://doi.org/10.3390/d15030431](https://doi.org/10.3390/d15030431)
- Okabe, T. & Yoshimura, J. (2017). Optimal designs of mollusk shells from bivalves to snails. *Scientific Reports* **7**, 42445. [https://doi.org/10.1038/srep42445](https://doi.org/10.1038/srep42445)
