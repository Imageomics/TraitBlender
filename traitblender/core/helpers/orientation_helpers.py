"""
Orientation helpers: bake rotation into mesh, and build custom Euler orientations.
"""

from __future__ import annotations

import re

import bpy
from mathutils import Euler

# Custom orientation names: YAML-safe identifiers (see docs).
CUSTOM_ORIENTATION_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")

_custom_name_update_guard: set[int] = set()


def is_valid_custom_orientation_name(name: str) -> bool:
    """True if name is non-empty and uses only letters, digits, underscores, hyphens."""
    return bool(name) and CUSTOM_ORIENTATION_NAME_RE.fullmatch(name) is not None


def custom_orientation_name_error(
    name: str,
    imaging,
    *,
    morphospace_name: str | None = None,
    exclude_index: int | None = None,
) -> str | None:
    """
    Return a user-facing error if ``name`` is invalid or conflicts; else None.

    Conflicts include other custom orientations and built-ins for ``morphospace_name``.
    """
    cleaned = (name or "").strip()
    if not cleaned:
        return "Custom orientation name cannot be empty"
    if not is_valid_custom_orientation_name(cleaned):
        return (
            "Custom orientation names may only use letters, digits, "
            "underscores, and hyphens (no spaces or special characters)"
        )
    for i, item in enumerate(getattr(imaging, "custom_orientations", []) or []):
        if exclude_index is not None and i == exclude_index:
            continue
        if (getattr(item, "name", "") or "").strip() == cleaned:
            return f"Custom orientation name '{cleaned}' is already used"
    if morphospace_name:
        from ..morphospaces.get_orientations import get_builtin_orientation_names

        builtins = set(get_builtin_orientation_names(morphospace_name) or [])
        if cleaned in builtins:
            return f"'{cleaned}' is already a built-in orientation name"
    return None


def unique_custom_orientation_name(
    imaging,
    base: str = "Custom",
    morphospace_name: str | None = None,
    exclude_index: int | None = None,
) -> str:
    """Allocate a valid custom name that does not collide with customs or built-ins."""
    base = base if is_valid_custom_orientation_name(base) else "Custom"
    candidate = base
    n = 0
    while custom_orientation_name_error(
        candidate,
        imaging,
        morphospace_name=morphospace_name,
        exclude_index=exclude_index,
    ):
        n += 1
        candidate = f"{base}_{n}"
        if n > 10000:
            return f"Custom_{n}"
    return candidate


def bake_rotation_to_mesh(object_name):
    """
    Apply the object's current rotation to its mesh data and set rotation to (0,0,0).
    The object keeps the same visual pose; later transforms use the applied orientation as base.

    Args:
        object_name: Name of the Blender object (str).

    Returns:
        bool: True if apply succeeded, False if object not found or apply failed.
    """
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return False
    if obj.type != 'MESH':
        return False
    try:
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(rotation=True)
        bpy.context.view_layer.update()
        return True
    except Exception:
        return False


def make_euler_orientation(rx, ry, rz, default_fn=None):
    """
    Build an orientation callable for any morphospace: run Default (if given), then apply
    Euler (rx, ry, rz) in the object's **local** frame (relative to the post-Default pose,
    before bake), then origin at geometry bounds and table center.

    Local composition uses ``R_obj @ R_local`` so axes follow the specimen after Default
    (works for Shell aperture alignment, MorphoWeave table Default, etc.).

    Args:
        rx, ry, rz: Local Euler rotation in radians (object rotation_euler order).
        default_fn: Optional morphospace Default orientation callable.

    Returns:
        callable: ``orient(sample_obj)``
    """
    rx_f, ry_f, rz_f = float(rx), float(ry), float(rz)

    def orient(sample_obj):
        if callable(default_fn):
            default_fn(sample_obj)
        else:
            sample_obj.tb_location = (0.0, 0.0, 0.0)

        order = sample_obj.rotation_euler.order
        R_obj = sample_obj.rotation_euler.to_matrix()
        R_local = Euler((rx_f, ry_f, rz_f), order).to_matrix()
        sample_obj.rotation_euler = (R_obj @ R_local).to_euler(order)

        bpy.context.view_layer.objects.active = sample_obj
        sample_obj.select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
        sample_obj.tb_location = (0.0, 0.0, 0.0)
        bpy.context.view_layer.update()

    orient.__name__ = f"_orient_custom_local_euler_{rx_f:.4f}_{ry_f:.4f}_{rz_f:.4f}"
    return orient
