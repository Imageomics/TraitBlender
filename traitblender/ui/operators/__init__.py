"""
TraitBlender UI Operators

Contains all operator classes for the TraitBlender add-on.
Operators handle user actions and commands.
"""

import bpy

from ...core.helpers.dependency_helpers import is_dearpygui_available

from . import (
    setup_scene_op,
    clear_scene_op,
    config_ops,
    import_dataset_op,
    export_dataset_op,
    clear_dataset_op,
    export_mesh_op,
    transforms_ops,
    confirm_switch_morphospace_op,
    generate_morphospace_sample_op,
    imaging_pipeline_op,
    apply_orientation_op,
    render_image_op,
)

_dpg_operator_classes = []
if is_dearpygui_available():
    # These operators depend on DearPyGui (GUI dataset/transform editors).
    from . import edit_dataset_op, edit_transforms_op

    _dpg_operator_classes = [
        edit_dataset_op.TRAITBLENDER_OT_edit_dataset,
        edit_transforms_op.TRAITBLENDER_OT_edit_transforms,
    ]

classes = [
    setup_scene_op.TRAITBLENDER_OT_setup_scene,
    setup_scene_op.TRAITBLENDER_OT_add_ruler,
    clear_scene_op.TRAITBLENDER_OT_clear_scene,
    config_ops.TRAITBLENDER_OT_configure_scene,
    config_ops.TRAITBLENDER_OT_show_configuration,
    config_ops.TRAITBLENDER_OT_export_config,
    import_dataset_op.TRAITBLENDER_OT_import_dataset,
    export_dataset_op.TRAITBLENDER_OT_export_dataset,
    clear_dataset_op.TRAITBLENDER_OT_clear_dataset,
    export_mesh_op.TRAITBLENDER_OT_export_mesh,
    transforms_ops.TRAITBLENDER_OT_run_pipeline,
    transforms_ops.TRAITBLENDER_OT_undo_pipeline,
    transforms_ops.TRAITBLENDER_OT_reset_pipeline,
    *(_dpg_operator_classes),
    confirm_switch_morphospace_op.TRAITBLENDER_OT_morphospace_switch_popup,
    confirm_switch_morphospace_op.TRAITBLENDER_OT_morphospace_switch_yes,
    confirm_switch_morphospace_op.TRAITBLENDER_OT_morphospace_switch_no,
    generate_morphospace_sample_op.TRAITBLENDER_OT_generate_morphospace_sample,
    imaging_pipeline_op.TRAITBLENDER_OT_imaging_pipeline,
    apply_orientation_op.TRAITBLENDER_OT_apply_orientation,
    render_image_op.TRAITBLENDER_OT_render_image,
]


def register():
    r_classes = classes
    for cls in r_classes:
        bpy.utils.register_class(cls)


def unregister():
    r_classes = classes
    for cls in r_classes:
        bpy.utils.unregister_class(cls)

__all__ = ["register", "unregister"] 