"""
TraitBlender Orientation Properties

Temporary UI state for the selected orientation of the active morphospace.
Not part of scene configuration - just tracks which orientation to apply.
"""

import bpy
from bpy.props import EnumProperty
from ...core.morphospaces import get_orientations_for_morphospace


class TRAITBLENDER_PG_orientation(bpy.types.PropertyGroup):
    """Temporary state: which orientation to apply for the current morphospace."""

    orientation: EnumProperty(
        name="Orientation",
        description="Orientation function to apply to the specimen (from the selected morphospace)",
        items=lambda self, context: self._get_orientation_items(context),
        default=0,
    )

    def _get_orientation_items(self, context):
        """Get orientation options from the selected morphospace's ORIENTATIONS dict."""
        items = []
        try:
            setup = context.scene.traitblender_setup
            morphospace_name = setup.available_morphospaces
            orientations = get_orientations_for_morphospace(morphospace_name, context=context)
            for name, func in orientations.items():
                if callable(func):
                    items.append((name, name, f"Apply {name} orientation"))
            if not items:
                items = [("", "—", "No orientations defined")]
        except Exception as e:
            print(f"TraitBlender: Error getting orientation items: {e}")
            items = items or [("", "—", "No orientations defined")]
        return items
