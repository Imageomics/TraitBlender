"""Orientation functions for morphospaces (built-in + config custom Eulers)."""

from ._module_loader import load_morphospace_module
from ..helpers.orientation_helpers import make_euler_orientation


def _custom_orientations_from_context(context):
    """
    Read imaging.custom_orientations from the scene config.

    Returns:
        dict: {name: (rx, ry, rz)} for non-empty names
    """
    if context is None:
        try:
            import bpy

            context = bpy.context
        except Exception:
            return {}
    try:
        imaging = context.scene.traitblender_config.imaging
    except Exception:
        return {}

    out = {}
    for item in getattr(imaging, "custom_orientations", []) or []:
        name = (getattr(item, "name", "") or "").strip()
        if not name:
            continue
        rot = getattr(item, "rotation", (0.0, 0.0, 0.0))
        out[name] = (float(rot[0]), float(rot[1]), float(rot[2]))
    return out


def get_builtin_orientation_names(morphospace_name):
    """
    Built-in ORIENTATIONS keys for a morphospace (no custom Eulers).

    Returns:
        list[str]: e.g. ['Default', ...], or empty if unavailable.
    """
    module = load_morphospace_module(morphospace_name)
    if module is None:
        return []
    base = getattr(module, "ORIENTATIONS", {}) or {}
    return list(base.keys()) if base else []


def get_orientations_for_morphospace(morphospace_name, context=None):
    """
    Get the ORIENTATIONS dictionary for a morphospace, merged with custom local Eulers
    from ``scene.traitblender_config.imaging.custom_orientations``.

    Morphospace modules must export ORIENTATIONS with at least "Default": callable.
    Each callable receives (sample_obj) and orients the object in place.

    Customs run Default, then compose ``(rx, ry, rz)`` in the object's local frame
    (relative to the post-Default pose, before bake). Custom names that collide with
    built-in orientation names are skipped (built-ins win).

    Args:
        morphospace_name: Morphospace folder id or display name.
        context: Optional Blender context (defaults to ``bpy.context``).

    Returns:
        dict: name -> callable, or empty dict if not defined/failed
    """
    module = load_morphospace_module(morphospace_name)
    if module is None:
        return {}

    base = dict(getattr(module, "ORIENTATIONS", {}) or {})
    if not base:
        return {}

    default_fn = base.get("Default")
    customs = _custom_orientations_from_context(context)
    for name, (rx, ry, rz) in customs.items():
        if name in base:
            print(
                f"TraitBlender: Custom orientation '{name}' skipped "
                f"(name already used by a built-in orientation)."
            )
            continue
        base[name] = make_euler_orientation(rx, ry, rz, default_fn=default_fn)

    return base


def get_orientation_names(morphospace_name, context=None):
    """
    Get list of orientation names for a morphospace (built-ins + customs).
    Returns e.g. ['Default', ..., 'Side'].
    """
    orientations = get_orientations_for_morphospace(morphospace_name, context=context)
    return list(orientations.keys()) if orientations else []
