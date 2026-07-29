"""Shared loader for morphospace modules."""

import os
import types
import importlib.util
import sys

from ..helpers import get_asset_path
from ..helpers.constants import ADDON_PACKAGE

# Namespace under which morphospace modules are registered (avoids Blender "top-level module" warning)
_MORPHOSPACE_NAMESPACE = f"{ADDON_PACKAGE}._morphospace"


def _ensure_morphospace_namespace():
    """Ensure the _morphospace namespace exists in sys.modules so child modules are not top-level."""
    if _MORPHOSPACE_NAMESPACE not in sys.modules:
        ns = types.ModuleType(_MORPHOSPACE_NAMESPACE)
        ns.__path__ = []
        sys.modules[_MORPHOSPACE_NAMESPACE] = ns


def _load_by_folder(folder_name):
    """Load a morphospace module by folder name (internal). Registers under addon namespace to avoid top-level module warning."""
    if not folder_name:
        return None
    morphospace_modules_path = get_asset_path("morphospace_modules")
    morphospace_path = os.path.join(morphospace_modules_path, folder_name)
    if not os.path.exists(morphospace_path):
        return None
    _ensure_morphospace_namespace()
    # Use a dotted name under the addon so Blender does not treat it as a top-level module
    module_name = f"{_MORPHOSPACE_NAMESPACE}.{folder_name}"
    try:
        spec = importlib.util.spec_from_file_location(
            module_name,
            os.path.join(morphospace_path, "__init__.py"),
            submodule_search_locations=[morphospace_path]
        )
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"TraitBlender: Error loading morphospace '{folder_name}': {e}")
        return None


def resolve_morphospace_to_folder(identifier):
    """
    Resolve a morphospace identifier (NAME or folder) to the folder name for loading.
    - If identifier is a folder that exists, return it.
    - Else treat identifier as NAME and search for a module whose NAME matches.

    Returns:
        str: Folder name, or None if not found
    """
    if not identifier:
        return None
    morphospace_modules_path = get_asset_path("morphospace_modules")
    folder_path = os.path.join(morphospace_modules_path, identifier)
    if os.path.isdir(folder_path) and os.path.exists(os.path.join(folder_path, "__init__.py")):
        return identifier
    for item in os.listdir(morphospace_modules_path):
        item_path = os.path.join(morphospace_modules_path, item)
        if not os.path.isdir(item_path) or not os.path.exists(os.path.join(item_path, "__init__.py")):
            continue
        module = _load_by_folder(item)
        if module is not None and getattr(module, 'NAME', item) == identifier:
            return item
    return None


def load_morphospace_module(identifier):
    """
    Load a morphospace module by identifier (NAME or folder name).

    Returns:
        Module object or None if not found/failed
    """
    folder_name = resolve_morphospace_to_folder(identifier)
    if folder_name is None:
        return None
    return _load_by_folder(folder_name)
