"""
Morphospace switch confirmation popup.

Switching morphospaces changes the expected dataset columns/parameters, so we warn
and clear the current dataset on confirmation.
"""

import bpy
from bpy.types import Operator


def _draw_morphospace_switch_popup(self, context):
    layout = self.layout
    setup = context.scene.traitblender_setup
    pending = getattr(setup, "pending_morphospace", "")

    layout.label(text="Are you sure you want to switch morphospaces?")
    if pending:
        layout.label(text=f"Switch to: {pending}")
    layout.separator()
    layout.label(text="Your current dataset will not be saved.")
    layout.separator()

    row = layout.row(align=True)
    row.operator("traitblender.morphospace_switch_yes", text="Yes")
    row.operator("traitblender.morphospace_switch_no", text="No")


class TRAITBLENDER_OT_morphospace_switch_popup(Operator):
    """Popup asking to confirm morphospace switch."""

    bl_idname = "traitblender.morphospace_switch_popup"
    bl_label = "Switch Morphospace?"

    def invoke(self, context, event):
        context.window_manager.popup_menu(
            _draw_morphospace_switch_popup,
            title="Switch Morphospace?",
            icon='QUESTION',
        )
        return {'FINISHED'}


class TRAITBLENDER_OT_morphospace_switch_yes(Operator):
    """Confirm morphospace switch and clear dataset."""

    bl_idname = "traitblender.morphospace_switch_yes"
    bl_label = "Yes"

    def execute(self, context):
        setup = context.scene.traitblender_setup
        pending = getattr(setup, "pending_morphospace", "")
        if not pending:
            return {'CANCELLED'}

        setup.suppress_morphospace_update = True
        try:
            setup.available_morphospaces = pending
            setup.prev_morphospace = pending
            setup.pending_morphospace = ""
        finally:
            setup.suppress_morphospace_update = False

        # Clear dataset so it regenerates defaults for the new morphospace.
        context.scene.traitblender_dataset.reset_to_morphospace_default()

        return {'FINISHED'}


class TRAITBLENDER_OT_morphospace_switch_no(Operator):
    """Cancel morphospace switch (keep previous selection)."""

    bl_idname = "traitblender.morphospace_switch_no"
    bl_label = "No"

    def execute(self, context):
        setup = context.scene.traitblender_setup
        setup.pending_morphospace = ""
        return {'FINISHED'}

