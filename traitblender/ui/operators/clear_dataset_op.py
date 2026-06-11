"""
TraitBlender Clear Dataset Operator

Resets the in-memory dataset to the default single-row CSV for the active morphospace.
"""

import bpy
from bpy.types import Operator


class TRAITBLENDER_OT_clear_dataset(Operator):
    """Clear the current dataset and restore morphospace defaults"""

    bl_idname = "traitblender.clear_dataset"
    bl_label = "Clear Dataset"
    bl_description = "Reset the dataset to the default row for the current morphospace"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        dataset = context.scene.traitblender_dataset
        try:
            dataset.reset_to_morphospace_default()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to clear dataset: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, "Dataset cleared (default row restored)")
        return {'FINISHED'}

    def invoke(self, context, event):
        if getattr(bpy.app, "background", False) or not context.window_manager.windows:
            return self.execute(context)
        return context.window_manager.invoke_confirm(self, event)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Are you sure you want to clear the dataset?")
        layout.label(text="Unsaved changes will be lost.")
        layout.separator()
        layout.label(text="Continue?", icon='QUESTION')
