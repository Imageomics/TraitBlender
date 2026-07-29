"""
Apply a named morphospace orientation to the current sample.

Single source of truth: look up the callable by ``orientation_name`` from
``get_orientations_for_morphospace``, apply it, and return that same name
for callers to use for folders / logs / CSV.
"""

from __future__ import annotations

import bpy
from mathutils import Euler

from .get_orientations import get_orientations_for_morphospace
from ..helpers import bake_rotation_to_mesh


def apply_orientation_by_name(context, orientation_name, sample_name=None, morphospace_name=None):
    """
    Reset the sample to rest, apply the named orientation, bake rotation.

    Args:
        context: Blender context.
        orientation_name: Exact key in the morphospace ORIENTATIONS merge
            (built-ins + customs). Used for both the lookup and as the return value.
        sample_name: Object name; defaults to ``scene.traitblender_dataset.sample``.
        morphospace_name: Morphospace id; defaults to setup selection.

    Returns:
        str: The ``orientation_name`` that was applied (same string passed in).

    Raises:
        ValueError: Missing sample, unknown orientation, or non-callable entry.
    """
    scene = context.scene
    dataset = scene.traitblender_dataset
    setup = scene.traitblender_setup

    if not orientation_name:
        raise ValueError("No orientation name provided")

    if sample_name is None:
        sample_name = dataset.sample
    if not sample_name:
        raise ValueError("No sample selected in dataset")
    if sample_name not in bpy.data.objects:
        raise ValueError(f"Sample object '{sample_name}' not found in scene")

    if morphospace_name is None:
        morphospace_name = setup.available_morphospaces
    if not morphospace_name:
        raise ValueError("No morphospace selected")

    orientations = get_orientations_for_morphospace(morphospace_name, context=context)
    if orientation_name not in orientations:
        raise ValueError(
            f"Orientation '{orientation_name}' not found for morphospace '{morphospace_name}'"
        )

    orient_func = orientations[orientation_name]
    if not callable(orient_func):
        raise ValueError(f"Orientation '{orientation_name}' is not callable")

    sample_obj = bpy.data.objects[sample_name]
    sample_data = scene.traitblender_sample

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    sample_obj.select_set(True)
    bpy.context.view_layer.objects.active = sample_obj

    last_baked = sample_data.last_baked_rotation
    if (last_baked[0], last_baked[1], last_baked[2]) != (0.0, 0.0, 0.0):
        eul = Euler(last_baked)
        inv_rot = eul.to_matrix().inverted()
        sample_obj.rotation_euler = inv_rot.to_euler(eul.order)
        bpy.ops.object.transform_apply(rotation=True)
        sample_data.last_baked_rotation = (0.0, 0.0, 0.0)

    sample_obj.rotation_euler = Euler(sample_data.rest_rotation)
    bpy.context.view_layer.update()

    orient_func(sample_obj)
    bpy.context.view_layer.update()

    sample_data.last_baked_rotation = tuple(sample_obj.rotation_euler)
    bake_rotation_to_mesh(sample_name)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    bpy.context.view_layer.update()

    return orientation_name
