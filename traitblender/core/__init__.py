"""
TraitBlender Core Module

Contains the core functionality including configuration, datasets, morphospaces, 
transforms, scene assets, and helper functions.

Import everything you need from here:
    from TraitBlender.core import get_asset_path, SceneAsset, etc.
"""

# Helper functions and utilities
from .helpers import (
    get_asset_path,
    apply_material,
    get_texture_info,
    VALID_TEXTURES,
    set_textures,
    ObjectNotFoundError,
    must_exist,
    check_object_exists,
    clear_scene,
)

# Positioning (currently empty)
# from .positioning import (
#     # No exports currently available
# )

# Transforms
from .transforms import (
    SAMPLERS,
)

from .positioning import (
    world_to_tb_location,
    get_depsgraph,
)

# Config
from .config import CONFIG, config_subsection_register, configs, config_register

# Datasets
from .datasets import launch_dataset_viewer_with_string

# Mesh exports
from .meshes import export_current_sample

# In-addon unit tests
from .unit_test import TESTS, list_tests, run_test, help_tests, test_config_matches_scene

__all__ = [
    # Helper functions
    "get_asset_path",
    "apply_material",
    "get_texture_info",
    "VALID_TEXTURES",
    "set_textures",
    "ObjectNotFoundError",
    "must_exist",
    "check_object_exists",
    "clear_scene",
    
    # Positioning
    "world_to_tb_location",
    "get_depsgraph",
    # Transforms
    "SAMPLERS",
    
    # Config
    "CONFIG",
    "config_subsection_register",
    "config_register",
    "configs",
    
    # Datasets
    "launch_dataset_viewer_with_string",

    # Meshes
    "export_current_sample",

    # Unit tests
    "TESTS",
    "list_tests",
    "help_tests",
    "run_test",
    "test_config_matches_scene",
]
