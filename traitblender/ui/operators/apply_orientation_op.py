"""
TraitBlender Apply Orientation Operator

Applies a named orientation from the morphospace ORIENTATIONS merge (built-ins +
customs) via the shared core helper. Optional ``orientation`` property overrides
the UI enum so callers (e.g. imaging pipeline) never rely on enum state for naming.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ...core.morphospaces import apply_orientation_by_name


class TRAITBLENDER_OT_apply_orientation(Operator):
    """Apply the selected orientation function to the current sample"""

    bl_idname = "traitblender.apply_orientation"
    bl_label = "Apply Orientation"
    bl_description = "Apply the selected orientation function to the specimen"
    bl_options = {'REGISTER', 'UNDO'}

    orientation: StringProperty(
        name="Orientation",
        description="Orientation name to apply; empty uses the Orientations panel selection",
        default="",
    )

    def execute(self, context):
        explicit = (self.orientation or "").strip()
        orientation_key = explicit or context.scene.traitblender_orientation.orientation

        try:
            applied = apply_orientation_by_name(context, orientation_key)
        except ValueError as e:
            msg = str(e)
            # Quiet no-op only when relying on the UI enum (no explicit argument)
            if not explicit and (
                msg == "No orientation name provided"
                or (
                    msg.startswith("Orientation '")
                    and " not found for morphospace " in msg
                )
            ):
                return {'FINISHED'}
            self.report({'ERROR'}, msg)
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to apply orientation: {e}")
            return {'CANCELLED'}

        # Keep UI enum in sync when possible (best-effort; apply does not depend on it)
        try:
            context.scene.traitblender_orientation.orientation = applied
        except Exception:
            pass

        self.report({'INFO'}, f"Applied orientation: {applied}")
        return {'FINISHED'}
