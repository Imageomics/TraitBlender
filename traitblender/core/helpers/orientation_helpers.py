"""
Orientation helpers: bake rotation into mesh, and build custom Euler orientations.
"""

import bpy
from mathutils import Euler


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
    (works for Shell aperture alignment, ATLAS table Default, etc.).

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
