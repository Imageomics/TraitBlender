"""
TraitBlender Datasets Module

Contains dataset management functionality for TraitBlender.
"""

import bpy
from . import traitblender_dataset
try:
    # Only available when DearPyGui is installed (GUI editor).
    from .dpg_dataset_editor import launch_dataset_viewer_with_string
except Exception:
    launch_dataset_viewer_with_string = None

classes = [
    traitblender_dataset.TRAITBLENDER_PG_dataset,
]

_ACTIVE_OBJECT_MSG_OWNER = object()
_SYNC_SAMPLE_IN_PROGRESS = False


def _on_active_object_changed():
    global _SYNC_SAMPLE_IN_PROGRESS
    if _SYNC_SAMPLE_IN_PROGRESS:
        return
    _SYNC_SAMPLE_IN_PROGRESS = True
    try:
        traitblender_dataset.sync_sample_to_active_object()
    finally:
        _SYNC_SAMPLE_IN_PROGRESS = False


def _register_active_object_sync_msgbus():
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.LayerObjects, "active"),
        owner=_ACTIVE_OBJECT_MSG_OWNER,
        args=(),
        notify=_on_active_object_changed,
        options={"PERSISTENT"},
    )


def _unregister_active_object_sync_msgbus():
    bpy.msgbus.clear_by_owner(_ACTIVE_OBJECT_MSG_OWNER)


def register():
    r_classes = classes
    for cls in r_classes:
        bpy.utils.register_class(cls)
    
    # Create the scene property
    bpy.types.Scene.traitblender_dataset = bpy.props.PointerProperty(type=traitblender_dataset.TRAITBLENDER_PG_dataset)
    _register_active_object_sync_msgbus()


def unregister():
    _unregister_active_object_sync_msgbus()
    # Remove the scene property
    del bpy.types.Scene.traitblender_dataset
    
    r_classes = classes
    for cls in r_classes:
        bpy.utils.unregister_class(cls)


__all__ = ["register", "unregister", "launch_dataset_viewer_with_string"] 