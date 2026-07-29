"""
MorphoWeave morphospace sample generation (TraitBlender wrapper around morphoweave_core).
"""

from __future__ import annotations

from pathlib import Path

import bpy
import numpy as np

from .morphoweave_core import build_deformed_mesh_arrays, load_ssm, resolve_database_paths
from .morphoweave_morphospace_sample import MorphoWeaveMorphospaceSample


def resolve_n_modes_for_hyperparams(hyperparameters: dict | None) -> int | None:
    """Return mode count from the configured DATABASE SSM, or None if not yet resolvable."""
    hp = dict(hyperparameters or {})
    db_raw = (hp.get("database_dir") or hp.get("database_path") or "").strip()
    if not db_raw:
        return None
    try:
        db_root = Path(bpy.path.abspath(db_raw))
    except Exception:
        db_root = Path(db_raw).expanduser().resolve()
    if not db_root.is_dir():
        return None
    try:
        paths = resolve_database_paths(db_root)
        ssm = load_ssm(paths)
        n_modes = int(ssm["n_modes"])
        return n_modes if n_modes > 0 else None
    except Exception:
        return None


def pc_values_from_trait_kwargs(traits: dict) -> list[float]:
    """Collect pc1, pc2, … from keyword traits in numeric order."""
    indexed: list[tuple[int, float]] = []
    for key, value in traits.items():
        if not key.startswith("pc") or len(key) <= 2:
            continue
        suffix = key[2:]
        if not suffix.isdigit():
            continue
        indexed.append((int(suffix), float(value)))
    indexed.sort(key=lambda item: item[0])
    return [v for _, v in indexed]


def _log(msg: str) -> None:
    print(f"[MorphoWeave] {msg}")


def generate_morphoweave_sample(
    name: str,
    hyperparameters: dict | None,
    pc_values: list[float],
) -> MorphoWeaveMorphospaceSample:
    hp = dict(hyperparameters or {})
    db_raw = (hp.get("database_dir") or hp.get("database_path") or "").strip()
    if not db_raw:
        raise ValueError(
            "MorphoWeave morphospace: set hyperparameter 'database_dir' to your "
            "MorphoWeave Model Library / DATABASE folder "
            "(manifest + template model + dense correspondences + ssm_model.npz)."
        )
    db_root = Path(bpy.path.abspath(db_raw))
    if not db_root.is_dir():
        raise ValueError(f"MorphoWeave database_dir is not a directory: {db_root}")

    n_comp_cfg = max(0, int(hp.get("n_components", 10)))
    scale = float(hp.get("scale", 1.0))

    if scale <= 0.0:
        raise ValueError("MorphoWeave hyperparameter 'scale' must be positive")

    paths = resolve_database_paths(db_root)
    ssm = load_ssm(paths)
    n_modes = int(ssm["n_modes"])
    if n_modes < 1:
        raise ValueError("SSM has no modes in ssm_model.npz")

    if n_comp_cfg > n_modes:
        _log(
            f"  n_components={n_comp_cfg} exceeds SSM modes ({n_modes}); using {n_modes} modes"
        )
        n_comp_cfg = n_modes

    _log(f"sample {name!r}: database_dir={db_root}")
    _log(f"  n_components={n_comp_cfg}, n_modes={n_modes}, scale={scale}")
    _log(
        "  files — "
        f"model={paths['model'].name}, dense={paths['dense'].name}, ssm={paths['ssm'].name}"
    )

    sigma = np.zeros(n_modes, dtype=np.float64)
    n_use = min(n_comp_cfg, n_modes, len(pc_values))
    sigma[:n_use] = np.asarray(pc_values[:n_use], dtype=np.float64)

    active = [i for i in range(n_use) if abs(sigma[i]) > 1e-12]
    if active:
        desc = ", ".join(f"PC{i + 1}={sigma[i]:.4g}σ" for i in active[:8])
        more = f" … (+{len(active) - 8} more)" if len(active) > 8 else ""
        _log(f"  active PCs: {desc}{more}")
    else:
        _log("  active PCs: none (template dense shape)")

    vertices, faces = build_deformed_mesh_arrays(
        paths,
        sigma,
        mesh_from_lps=True,
    )

    if scale != 1.0:
        _log(f"  uniform scale={scale}")
        vertices = vertices * scale

    _log(f"  mesh: {vertices.shape[0]} verts, {len(faces)} faces")
    verts = [tuple(map(float, row)) for row in vertices]
    return MorphoWeaveMorphospaceSample(name, verts, faces)
