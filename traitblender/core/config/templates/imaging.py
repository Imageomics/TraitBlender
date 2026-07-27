"""
Imaging pipeline configuration: selected orientations and images per orientation.
"""

import bpy
from bpy.props import (
    BoolProperty,
    CollectionProperty,
    FloatVectorProperty,
    IntProperty,
    StringProperty,
)

from .. import config_subsection_register, TraitBlenderConfig


class ImagingOrientationItem(bpy.types.PropertyGroup):
    """One orientation option for the imaging pipeline (name + enabled checkbox)."""

    name: StringProperty(name="Orientation", default="")
    enabled: BoolProperty(
        name="Include",
        description="Include this orientation in the imaging pipeline",
        default=False,
    )


class ImagingCustomOrientationItem(bpy.types.PropertyGroup):
    """User-defined Euler orientation: name + (rx, ry, rz) in radians."""

    name: StringProperty(
        name="Name",
        description="Display name for this custom orientation (must be unique)",
        default="Custom",
    )
    rotation: FloatVectorProperty(
        name="Rotation",
        description=(
            "Local Euler rotation in radians (X, Y, Z) applied after Default, "
            "relative to the specimen's axes before bake"
        ),
        size=3,
        default=(0.0, 0.0, 0.0),
    )


# Register so ImagingConfig can use CollectionProperty types
bpy.utils.register_class(ImagingOrientationItem)
bpy.utils.register_class(ImagingCustomOrientationItem)


@config_subsection_register("imaging")
class ImagingConfig(TraitBlenderConfig):
    """Which orientations to run in the imaging pipeline and how many images per orientation."""

    print_index = 7

    include_images: BoolProperty(
        name="Include Images",
        description="If enabled, render images during the imaging pipeline",
        default=True,
    )

    orientation_options: CollectionProperty(
        type=ImagingOrientationItem,
        name="Orientations",
        description="Orientations from the selected morphospace; checked = include in pipeline",
    )
    custom_orientations: CollectionProperty(
        type=ImagingCustomOrientationItem,
        name="Custom Orientations",
        description=(
            "Named local Euler orientations (radians) applied after Default for all morphospaces"
        ),
    )
    images_per_orientation: IntProperty(
        name="Images Per Orientation",
        description="Number of images to render per orientation (transforms applied each time)",
        default=1,
        min=1,
    )

    def _to_yaml(self, indent_level=0, parent_path=""):
        """Export imaging section; orientation_options as orientation_names list."""
        indent = "  " * (indent_level + 1)
        names = [item.name for item in self.orientation_options if item.enabled]
        safe = [repr(n) for n in names]
        lines = [
            f"{indent}include_images: {str(self.include_images).lower()}",
            f'{indent}orientation_names: [{", ".join(safe)}]',
            f"{indent}images_per_orientation: {self.images_per_orientation}",
        ]

        customs = [
            item for item in self.custom_orientations if (item.name or "").strip()
        ]
        if customs:
            lines.append(f"{indent}custom_orientations:")
            for item in customs:
                name = item.name.strip()
                key = name if name.replace("_", "").replace("-", "").isalnum() else repr(name)
                rx, ry, rz = float(item.rotation[0]), float(item.rotation[1]), float(item.rotation[2])
                lines.append(f"{indent}  {key}: [{rx}, {ry}, {rz}]")

        return "\n".join(lines)

    def sync_orientation_options(self, context, enabled_names=None):
        """
        Rebuild orientation_options from the live morphospace + customs dict.

        Args:
            context: Blender context.
            enabled_names: Optional set/list of names that should be enabled.
                If None, preserve previous enabled flags; new names default to
                enabled only when the name is ``Default``.
        """
        from ...morphospaces import get_orientation_names

        morphospace_name = context.scene.traitblender_setup.available_morphospaces
        all_names = (
            get_orientation_names(morphospace_name, context) if morphospace_name else []
        )
        prev_enabled = {item.name: bool(item.enabled) for item in self.orientation_options}
        enabled_set = set(enabled_names) if enabled_names is not None else None

        self.orientation_options.clear()
        for name in all_names:
            item = self.orientation_options.add()
            item.name = name
            if enabled_set is not None:
                item.enabled = name in enabled_set
            else:
                item.enabled = prev_enabled.get(name, name == "Default")

    def from_dict(self, data_dict):
        """Load imaging section; restore orientation_options and custom_orientations."""
        if not isinstance(data_dict, dict):
            raise ValueError("Input must be a dictionary")
        if "include_images" in data_dict:
            self.include_images = bool(data_dict["include_images"])
        if "images_per_orientation" in data_dict:
            self.images_per_orientation = data_dict["images_per_orientation"]

        enabled_from_yaml = {"Default"}
        if "orientation_names" in data_dict:
            names = data_dict["orientation_names"]
            if isinstance(names, list):
                enabled_from_yaml = {n for n in names if isinstance(n, str)}

        if "custom_orientations" in data_dict:
            customs = data_dict["custom_orientations"]
            if isinstance(customs, dict):
                self.custom_orientations.clear()
                for name, rot in customs.items():
                    if not isinstance(name, str) or not name.strip():
                        continue
                    if not isinstance(rot, (list, tuple)) or len(rot) < 3:
                        print(
                            f"TraitBlender: Skipping custom orientation '{name}' "
                            f"(expected [rx, ry, rz])."
                        )
                        continue
                    item = self.custom_orientations.add()
                    item.name = name.strip()
                    item.rotation = (float(rot[0]), float(rot[1]), float(rot[2]))
            elif customs is not None:
                print(
                    "TraitBlender: custom_orientations must be a mapping of "
                    "name → [rx, ry, rz]; leaving existing customs unchanged."
                )

        # Sync checkboxes now if possible (morphospace may still load later in YAML;
        # configure_scene also syncs after the full from_dict).
        try:
            import bpy

            self.sync_orientation_options(bpy.context, enabled_names=enabled_from_yaml)
        except Exception as e:
            print(f"TraitBlender: Could not sync imaging orientation_options: {e}")
            if enabled_from_yaml is not None:
                self.orientation_options.clear()
                for n in enabled_from_yaml:
                    item = self.orientation_options.add()
                    item.name = n
                    item.enabled = True
