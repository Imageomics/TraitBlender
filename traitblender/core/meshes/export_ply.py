"""
PLY export backend.
"""

import os
import bpy


def export_ply(*, object_name: str, filepath: str, use_selection: bool = True) -> dict:
    """
    Export a single object as PLY using Blender's exporter.

    Returns:
        dict: { export_type, sample_name, files, warnings }
    """
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise RuntimeError(f"Sample object not found: '{object_name}'")

    path = filepath
    if not path.lower().endswith(".ply"):
        path = path + ".ply"

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    view_layer = bpy.context.view_layer
    prev_active = view_layer.objects.active
    prev_selected = [o for o in bpy.context.selected_objects]

    try:
        if use_selection:
            for o in prev_selected:
                o.select_set(False)
            obj.select_set(True)
            view_layer.objects.active = obj

        # Blender 4.0+ / 5.x PLY exporter (TraitBlender targets 5.1+)
        if hasattr(bpy.ops.wm, "ply_export"):
            bpy.ops.wm.ply_export(filepath=path, export_selected_objects=use_selection)
        else:
            bpy.ops.export_mesh.ply(filepath=path, use_selection=use_selection)

        return {
            "export_type": "ply",
            "sample_name": object_name,
            "files": [path],
            "warnings": [],
        }
    finally:
        for o in bpy.context.selected_objects:
            o.select_set(False)
        for o in prev_selected:
            if o and o.name in bpy.data.objects:
                o.select_set(True)
        if prev_active and prev_active.name in bpy.data.objects:
            view_layer.objects.active = prev_active
