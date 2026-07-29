"""
TraitBlender Core Helpers

Utility functions and helpers for the TraitBlender add-on.
"""

from .material_helpers import apply_material, get_texture_info, VALID_TEXTURES, set_textures
from .object_helpers import (
    ObjectNotFoundError,
    must_exist,
    check_object_exists,
)   
from .property_getset import get_property, set_property
from .addon_helpers import get_addon_root, get_asset_path, get_user_data_dir, init_user_dirs
from .config_helpers import (
    COMPONENT_TO_INDEX,
    get_config_path_info,
    list_config_properties,
    parse_component_path,
    resolve_config_path,
    validate_config_path,
)
from .get_property_type import get_property_type, VALID_PROPERTY_TYPES
from .transform_property_helper import (
    get_available_sections,
    get_properties_for_section,
    build_property_path,
    parse_property_path,
    get_available_samplers,
    get_available_samplers_for_property,
)
from .transform_sampler_helper import (
    get_sampler_signature,
    validate_parameter_value,
    format_parameter_value,
)
from .clear_scene import clear_scene
from .orientation_helpers import (
    bake_rotation_to_mesh,
    make_euler_orientation,
    is_valid_custom_orientation_name,
    custom_orientation_name_error,
    unique_custom_orientation_name,
)
# Import table location functions
try:
    from ..ui.properties.tb_location import _get_tb_location, _set_tb_location
    from ..positioning.get_tb_location import z_dist_to_lowest
except ImportError:
    # Fallback if modules are not available
    z_dist_to_lowest = None
    _get_tb_location = None
    _set_tb_location = None

__all__ = [
    "get_asset_path",
    "get_addon_root",
    "get_user_data_dir",
    "init_user_dirs",
    "apply_material",
    "get_texture_info",
    "VALID_TEXTURES",
    "set_textures",
    # Object validation utilities
    "ObjectNotFoundError",
    "must_exist",
    "check_object_exists",
    # Property getter/setter
    "get_property",
    "set_property",
    # Config validator functions
    "validate_config_path",
    "get_config_path_info",
    "list_config_properties",
    # Config path helpers
    "resolve_config_path",
    "parse_component_path",
    "COMPONENT_TO_INDEX",
    # Transform property/sampler helpers (for DPG transforms editor)
    "get_available_sections",
    "get_properties_for_section",
    "build_property_path",
    "parse_property_path",
    "get_available_samplers",
    "get_available_samplers_for_property",
    "get_sampler_signature",
    "validate_parameter_value",
    "format_parameter_value",
    # Property type
    "get_property_type",
    "VALID_PROPERTY_TYPES",
    # Clear scene
    "clear_scene",
    # Orientation
    "bake_rotation_to_mesh",
    "make_euler_orientation",
    "is_valid_custom_orientation_name",
    "custom_orientation_name_error",
    "unique_custom_orientation_name",
    # Table location functions
    "z_dist_to_lowest",
    "_get_tb_location",
    "_set_tb_location",
] 