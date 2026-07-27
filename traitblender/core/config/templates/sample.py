import bpy
from .. import config_subsection_register, TraitBlenderConfig
from ...helpers import get_property, set_property


def _sample_object_path(attr):
    """Return path_getter (self) -> str | None for sample object's attribute (tb_location, tb_rotation)."""

    def path_getter(self):
        try:
            name = bpy.context.scene.traitblender_dataset.sample
            if name and name in bpy.data.objects:
                return f"bpy.data.objects['{name}'].{attr}"
        except Exception:
            pass
        return None

    return path_getter


@config_subsection_register("sample")
class SampleConfig(TraitBlenderConfig):
    print_index = 8

    # This configuration should not appear in the config file
    # It's only for UI controls in the datasets panel

    tb_rotation: bpy.props.FloatVectorProperty(
        name="Sample Rotation",
        description="The rotation of the generated sample object",
        default=(0.0, 0.0, 0.0),
        subtype='EULER',
        get=get_property("", path_getter=_sample_object_path("tb_rotation"), default=(0.0, 0.0, 0.0)),
        set=set_property("", path_getter=_sample_object_path("tb_rotation"), fail_silently=True),
    )

    tb_location: bpy.props.FloatVectorProperty(
        name="Sample Position",
        description="Table location of the generated sample object",
        default=(0.0, 0.0, 0.0),
        subtype='TRANSLATION',
        size=3,
        get=get_property("", path_getter=_sample_object_path("tb_location"), default=(0.0, 0.0, 0.0)),
        set=set_property("", path_getter=_sample_object_path("tb_location"), fail_silently=True),
    )

    def _to_yaml(self, indent_level=0, parent_path=""):
        """Override to prevent this configuration from appearing in YAML output."""
        return ""

    def from_dict(self, data_dict):
        """UI-only section — ignore YAML (including bare ``sample:`` / null / {})."""
        return
