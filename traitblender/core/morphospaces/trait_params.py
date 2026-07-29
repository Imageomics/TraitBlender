"""Trait parameter functions for morphospaces."""

import inspect

from ._module_loader import load_morphospace_module


def _merged_hyperparameters_for_traits(morphospace_name, context):
    """Module HYPERPARAMETERS merged with scene config overrides (when context is available)."""
    module = load_morphospace_module(morphospace_name)
    base = dict(getattr(module, "HYPERPARAMETERS", {})) if module else {}
    if context is None:
        try:
            import bpy

            context = bpy.context
        except Exception:
            return base
    try:
        return context.scene.traitblender_config.morphospace.get_hyperparams_for(morphospace_name)
    except Exception:
        return base


def get_trait_parameters_for_morphospace(morphospace_name, context=None):
    """
    Get trait parameter names and defaults for a morphospace (sample() params excluding name, hyperparameters).
    Used for default dataset columns when no file is imported.

    Returns:
        list: Ordered list of trait param names (e.g. ['b', 'd', 'z', 'a', 'phi', 'psi', ...])
    """
    traits = get_trait_parameters_with_defaults_for_morphospace(morphospace_name, context=context)
    return list(traits.keys())


def get_trait_parameters_with_defaults_for_morphospace(morphospace_name, context=None):
    """
    Get trait parameters and their default values for a morphospace.

    If the module defines ``get_trait_parameters_with_defaults(merged_hyperparameters)``, that
    return value is used (e.g. MorphoWeave: PC1..PCn from ``n_components``, capped by SSM mode count).
    Otherwise
    parameters are inferred from ``sample()``'s signature.

    Args:
        morphospace_name: Display name or folder id (same as ``load_morphospace_module``).
        context: Optional ``bpy.types.Context``; when provided, hyperparameters are read from
            ``traitblender_config.morphospace`` so trait columns match the UI.

    Returns:
        dict: {param_name: default_value} in order (for default dataset row)
    """
    module = load_morphospace_module(morphospace_name)
    if module is None:
        return {}

    dynamic = getattr(module, "get_trait_parameters_with_defaults", None)
    if callable(dynamic):
        merged = _merged_hyperparameters_for_traits(morphospace_name, context)
        try:
            out = dynamic(merged)
            if isinstance(out, dict) and out:
                return dict(out)
        except Exception as e:
            print(f"TraitBlender: morphospace '{morphospace_name}' get_trait_parameters_with_defaults failed: {e}")

    sample_func = getattr(module, "sample", None)
    if not callable(sample_func):
        return {}

    sig = inspect.signature(sample_func)
    hyperparams = set(getattr(module, "HYPERPARAMETERS", {}).keys()) | {"hyperparameters"}
    exclude = {"name"} | hyperparams

    result = {}
    for pname, param in sig.parameters.items():
        if pname in exclude:
            continue
        default = param.default
        if default is inspect.Parameter.empty:
            default = 0.0
        result[pname] = default
    return result
