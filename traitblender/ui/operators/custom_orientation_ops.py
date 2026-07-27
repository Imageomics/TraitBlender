"""
Operators for adding/removing custom Euler orientations on imaging config.
"""

import bpy
from bpy.types import Operator
from bpy.props import IntProperty


def _unique_custom_name(imaging, base="Custom"):
    existing = {(item.name or "").strip() for item in imaging.custom_orientations}
    if base not in existing:
        return base
    i = 1
    while f"{base}.{i:03d}" in existing:
        i += 1
    return f"{base}.{i:03d}"


class TRAITBLENDER_OT_add_custom_orientation(Operator):
    """Add a named custom Euler orientation"""

    bl_idname = "traitblender.add_custom_orientation"
    bl_label = "Add Custom Orientation"
    bl_description = "Add a custom local Euler orientation (radians) available for all morphospaces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        imaging = context.scene.traitblender_config.imaging
        item = imaging.custom_orientations.add()
        item.name = _unique_custom_name(imaging)
        item.rotation = (0.0, 0.0, 0.0)
        self.report({'INFO'}, f"Added custom orientation: {item.name}")
        return {'FINISHED'}


class TRAITBLENDER_OT_remove_custom_orientation(Operator):
    """Remove a custom Euler orientation by index"""

    bl_idname = "traitblender.remove_custom_orientation"
    bl_label = "Remove Custom Orientation"
    bl_description = "Remove this custom orientation"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(name="Index", default=0, min=0)

    def execute(self, context):
        imaging = context.scene.traitblender_config.imaging
        if self.index < 0 or self.index >= len(imaging.custom_orientations):
            self.report({'ERROR'}, "Invalid custom orientation index")
            return {'CANCELLED'}
        name = imaging.custom_orientations[self.index].name
        imaging.custom_orientations.remove(self.index)
        # Drop pipeline checkbox entry if present
        for i, opt in enumerate(list(imaging.orientation_options)):
            if opt.name == name:
                imaging.orientation_options.remove(i)
                break
        self.report({'INFO'}, f"Removed custom orientation: {name}")
        return {'FINISHED'}
