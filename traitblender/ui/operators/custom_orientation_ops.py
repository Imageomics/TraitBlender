"""
Operators for adding/removing custom Euler orientations on imaging config.
"""

import bpy
from bpy.types import Operator
from bpy.props import IntProperty

from ...core.helpers.orientation_helpers import unique_custom_orientation_name


class TRAITBLENDER_OT_add_custom_orientation(Operator):
    """Add a named custom Euler orientation"""

    bl_idname = "traitblender.add_custom_orientation"
    bl_label = "Add Custom Orientation"
    bl_description = (
        "Add a custom local Euler orientation (radians). "
        "Names must be unique and use only letters, digits, underscores, and hyphens"
    )
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        imaging = context.scene.traitblender_config.imaging
        morphospace_name = context.scene.traitblender_setup.available_morphospaces
        item = imaging.custom_orientations.add()
        idx = len(imaging.custom_orientations) - 1
        name = unique_custom_orientation_name(
            imaging,
            morphospace_name=morphospace_name,
            exclude_index=idx,
        )
        item.validated_name = name
        item.name = name
        item.rotation = (0.0, 0.0, 0.0)
        try:
            imaging.sync_orientation_options(context, enabled_names=None)
        except Exception as e:
            print(f"TraitBlender: Imaging orientation sync after add failed: {e}")
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
        try:
            imaging.sync_orientation_options(context, enabled_names=None)
        except Exception as e:
            print(f"TraitBlender: Imaging orientation sync after remove failed: {e}")
        self.report({'INFO'}, f"Removed custom orientation: {name}")
        return {'FINISHED'}
