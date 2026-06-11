"""
Mesh export registry.

Defines supported export types and maps them to exporter functions.
"""

from .export_obj import export_obj
from .export_ply import export_ply

# Keys are used for UI dropdown + config values.
EXPORTERS = {
    "obj": export_obj,
    "ply": export_ply,
}


def export_type_items():
    """Return Blender EnumProperty items for available export types."""
    # (identifier, name, description)
    return [(k, k.upper(), f"Export as .{k}") for k in EXPORTERS.keys()]

