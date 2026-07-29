"""
Mesh export configuration.
"""

import bpy
from bpy.props import BoolProperty, EnumProperty

from .. import config_subsection_register, TraitBlenderConfig
from ...meshes import export_type_items


@config_subsection_register("meshes")
class MeshesConfig(TraitBlenderConfig):
    """Configuration for mesh exports."""

    # Place after imaging/sample/transforms in YAML/UI ordering (not the panel ordering)
    print_index = 9

    file_export_type: EnumProperty(
        name="File Export Type",
        description="Mesh export file type for exporting the current sample",
        items=lambda self, context: export_type_items(),
        default=0,
    )

    save_meshes: BoolProperty(
        name="Save Meshes",
        description=(
            "If enabled, export a 3D model for each specimen during the imaging pipeline"
        ),
        default=False,
    )

    orient_before_export: BoolProperty(
        name="Orient Before Export",
        description=(
            "If enabled (default), apply the morphospace Default orientation before exporting "
            "meshes (table placement). Disable to export the generated mesh as-is—useful for "
            "ATLAS, where the SSM already provides a consistent PCA-aligned frame"
        ),
        default=True,
    )

