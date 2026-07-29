"""
MorphoWeave morphospace: template-centered PCA on dense correspondences + Local RBF warp.

Traits ``pc1`` … ``pcK`` are σ-multiples (MorphoWeave Model Library / SSM Explorer sliders).
Reconstruction: ``target = template_dense + Σ z_i √(λ_i) mode_i``, then Local RBF mesh warp
(LPS/RAS aware).
"""

from __future__ import annotations

from .morphospace import (
    generate_morphoweave_sample,
    pc_values_from_trait_kwargs,
    resolve_n_modes_for_hyperparams,
)
from .orientations import ORIENTATIONS

NAME = "MorphoWeave"

HYPERPARAMETERS = {
    "database_dir": "",
    "n_components": 10,
    # uniform scale applied to deformed vertices after warp
    "scale": 1.0,
}


def get_trait_parameters_with_defaults(merged_hyperparameters):
    """``pc1`` … ``pc{n}`` for dataset columns; ``n`` is limited by SSM mode count when known."""
    n = max(0, int(merged_hyperparameters.get("n_components", HYPERPARAMETERS["n_components"])))
    n_modes = resolve_n_modes_for_hyperparams(merged_hyperparameters)
    if n_modes is not None:
        n = min(n, n_modes)
    return {f"pc{i}": 0.0 for i in range(1, n + 1)}


def sample(name="MorphoWeave", hyperparameters=None, **traits):
    """Generate a specimen; PC coefficients are passed as pc1, pc2, … keyword traits."""
    return generate_morphoweave_sample(
        name,
        hyperparameters or {},
        pc_values_from_trait_kwargs(traits),
    )


__all__ = [
    "NAME",
    "sample",
    "HYPERPARAMETERS",
    "ORIENTATIONS",
    "get_trait_parameters_with_defaults",
    "generate_morphoweave_sample",
    "resolve_n_modes_for_hyperparams",
]
