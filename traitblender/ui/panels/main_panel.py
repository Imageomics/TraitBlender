import bpy
from bpy.types import Panel
from ..properties import morphospace_hyperparams
from ...core.helpers.dependency_helpers import is_dearpygui_available

# Deferred sync of imaging orientation_options (cannot modify ID in draw context)
_pending_orientation_sync = None  # (scene_name, [orientation_names]) or None


def _sync_imaging_orientations_timer():
    """One-shot timer: add missing orientation_options for the pending scene."""
    global _pending_orientation_sync
    if not _pending_orientation_sync:
        return None
    scene_name, orientation_names = _pending_orientation_sync
    _pending_orientation_sync = None
    scene = bpy.data.scenes.get(scene_name)
    if not scene or not hasattr(scene, "traitblender_config"):
        return None
    config = scene.traitblender_config
    if not hasattr(config, "imaging"):
        return None
    items = config.imaging.orientation_options
    for name in orientation_names:
        if next((x for x in items if x.name == name), None) is None:
            item = items.add()
            item.name = name
            item.enabled = True
    return None  # one-shot

class TRAITBLENDER_PT_main_panel(Panel):
    bl_label = "1 Museum Setup"
    bl_idname = "TRAITBLENDER_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        # Setup Museum Scene and Clear Scene buttons
        row = layout.row(align=True)
        row.operator("traitblender.setup_scene", text="Import Museum")
        row.operator("traitblender.clear_scene", text="Clear Scene", icon='TRASH')
        row = layout.row(align=True)
        row.operator("traitblender.add_ruler", text="Add Ruler", icon='EMPTY_AXIS')
        layout.separator()
        # Config file path row
        row = layout.row(align=True)
        row.prop(context.scene.traitblender_setup, "config_file", text="Config File")
        # Configure Scene button row
        row = layout.row(align=True)
        row.operator("traitblender.configure_scene", text="Configure Scene")

    # Helper methods for config panel
    def _draw_config_section(self, layout, section_name, section_obj):
        box = layout.box()
        row = box.row()
        has_show_prop = hasattr(section_obj, 'show')
        if has_show_prop:
            row.prop(section_obj, 'show', text="", icon='DISCLOSURE_TRI_DOWN' if section_obj.show else 'DISCLOSURE_TRI_RIGHT')
            row.label(text=section_name.replace('_', ' ').title())
            if section_obj.show:
                self._draw_section_content(box, section_obj)
        else:
            row.label(text=section_name.replace('_', ' ').title())
            self._draw_section_content(box, section_obj)

    def _draw_section_content(self, layout, section_obj):
        for prop_name in section_obj.__class__.__annotations__.keys():
            if prop_name == "show":
                continue
            try:
                prop_value = getattr(section_obj, prop_name)
                if isinstance(prop_value, type(section_obj)):
                    sub_box = layout.box()
                    sub_box.label(text=prop_name.replace('_', ' ').title())
                    self._draw_config_section(sub_box, prop_name, prop_value)
                else:
                    layout.prop(section_obj, prop_name)
            except Exception as e:
                prop_row = layout.row()
                prop_row.label(text=f"{prop_name.replace('_', ' ').title()}: # Error - {str(e)}")

class TRAITBLENDER_PT_config_panel(Panel):
    bl_label = "2 Configuration"
    bl_idname = "TRAITBLENDER_PT_config_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        config = context.scene.traitblender_config
        config_sections = config.get_config_sections()
        if config_sections:
            for section_name, section_obj in config_sections.items():
                if section_name in ["transforms", "sample", "morphospace"]:
                    continue
                self._draw_config_section(layout, section_name, section_obj)
        else:
            layout.label(text="No configuration sections found", icon='INFO')
        layout.separator()
        row = layout.row(align=True)
        row.operator("traitblender.show_configuration", text="Show Configuration")
        row.operator("traitblender.export_config", text="Export Config as YAML")

    def _draw_config_section(self, layout, section_name, section_obj):
        TRAITBLENDER_PT_main_panel._draw_config_section(self, layout, section_name, section_obj)

    def _draw_section_content(self, layout, section_obj):
        TRAITBLENDER_PT_main_panel._draw_section_content(self, layout, section_obj)

class TRAITBLENDER_PT_morphospaces_panel(Panel):
    bl_label = "3 Morphospaces"
    bl_idname = "TRAITBLENDER_PT_morphospaces_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        setup = context.scene.traitblender_setup

        # Morphospace selection dropdown
        row = layout.row(align=True)
        row.prop(setup, "available_morphospaces", text="Morphospace")

        # Hyperparameters (dynamically from morphospace's HYPERPARAMETERS)
        morphospace_name = setup.available_morphospaces
        editor = morphospace_hyperparams.get_hyperparam_editor_for(context, morphospace_name)
        if editor is not None:
            box = layout.box()
            box.label(text="Hyperparameters", icon='SETTINGS')
            for key in morphospace_hyperparams.get_hyperparam_keys_for(morphospace_name):
                box.prop(editor, key)

class TRAITBLENDER_PT_datasets_panel(Panel):
    bl_label = "4 Datasets"
    bl_idname = "TRAITBLENDER_PT_datasets_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        dataset = context.scene.traitblender_dataset
        setup = context.scene.traitblender_setup
        
        # Dataset file path row
        row = layout.row(align=True)
        row.prop(dataset, "filepath", text="Dataset File")
        
        # Edit + Export dataset buttons
        row = layout.row(align=True)
        if is_dearpygui_available():
            row.operator("traitblender.edit_dataset", text="Edit Dataset")
        row.operator("traitblender.export_dataset", text="Export Dataset")
        row.operator("traitblender.clear_dataset", text="Clear")
        
        # Sample selection dropdown
        row = layout.row(align=True)
        row.prop(dataset, "sample", text="Sample")

        # Auto-sync sample with active object by exact name match
        row = layout.row(align=True)
        row.prop(dataset, "sync_sample_with_active_object", text="Sync Sample to Active")
        
        # Generate sample button
        row = layout.row(align=True)
        row.operator("traitblender.generate_morphospace_sample", text="Generate Sample", icon='ADD')

class TRAITBLENDER_PT_orientations_panel(Panel):
    bl_label = "5 Orientations"
    bl_idname = "TRAITBLENDER_PT_orientations_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        orientation_state = context.scene.traitblender_orientation

        layout.label(text="Apply orientation from the selected morphospace:")
        row = layout.row(align=True)
        row.prop(orientation_state, "orientation", text="")
        row.operator("traitblender.apply_orientation", text="Apply", icon='ORIENTATION_VIEW')

class TRAITBLENDER_PT_transforms_panel(Panel):
    bl_label = "6 Transforms"
    bl_idname = "TRAITBLENDER_PT_transforms_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        config = context.scene.traitblender_config
        layout.separator()
        box = layout.box()
        transforms_config = config.transforms

        # Edit transforms button (DearPyGui GUI only)
        row = box.row(align=True)
        if is_dearpygui_available():
            row.operator(
                "traitblender.edit_transforms",
                text="Edit Transform Pipeline",
                icon='PREFERENCES',
            )
        
        # Pipeline control buttons
        row = box.row(align=True)
        row.operator("traitblender.run_pipeline", text="Run Pipeline", icon='PLAY')
        row.operator("traitblender.undo_pipeline", text="Undo", icon='LOOP_BACK')
        row.operator("traitblender.reset_pipeline", text="Reset", icon='RECOVER_LAST')

        # Transform count
        row = box.row(align=True)
        row.label(text=f"Transforms in pipeline: {len(transforms_config)}")

class TRAITBLENDER_PT_meshes_panel(Panel):
    bl_label = "7 Meshes"
    bl_idname = "TRAITBLENDER_PT_meshes_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        config = context.scene.traitblender_config

        box = layout.box()
        box.label(text="Export current sample mesh")

        row = box.row(align=True)
        row.prop(config.meshes, "file_export_type", text="Type")

        row = box.row(align=True)
        row.prop(config.meshes, "save_meshes", text="Save meshes in imaging pipeline")

        row = box.row(align=True)
        row.operator("traitblender.export_mesh", text="Export Mesh")


class TRAITBLENDER_PT_imaging_panel(Panel):
    bl_label = "8 Imaging"
    bl_idname = "TRAITBLENDER_PT_imaging_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        config = context.scene.traitblender_config
        setup = context.scene.traitblender_setup

        row = layout.row(align=True)
        row.prop(config.imaging, "include_images", text="Include Images")
        
        # Images per orientation
        row = layout.row(align=True)
        row.prop(config.imaging, "images_per_orientation", text="Images Per Orientation")
        
        # Orientations (from current morphospace): sync via timer (cannot write in draw), then draw checkboxes
        from ...core.morphospaces import get_orientation_names
        morphospace_name = setup.available_morphospaces
        orientation_names = get_orientation_names(morphospace_name) if morphospace_name else []
        if orientation_names:
            items = config.imaging.orientation_options
            missing = [n for n in orientation_names if next((x for x in items if x.name == n), None) is None]
            if missing:
                global _pending_orientation_sync
                if _pending_orientation_sync is None:
                    _pending_orientation_sync = (context.scene.name, list(orientation_names))
                    bpy.app.timers.register(_sync_imaging_orientations_timer, first_interval=0.01)
            box = layout.box()
            box.label(text="Orientations to render", icon='ORIENTATION_VIEW')
            for name in orientation_names:
                item = next((x for x in items if x.name == name), None)
                if item is None:
                    continue  # will appear after timer runs
                row = box.row()
                row.prop(item, "enabled", text=name)

class TRAITBLENDER_PT_simulation_panel(Panel):
    bl_label = "Simulation"
    bl_idname = "TRAITBLENDER_PT_simulation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TraitBlender'

    def draw(self, context):
        layout = self.layout
        config = context.scene.traitblender_config

        row = layout.row(align=True)
        row.prop(config.output, "rendering_directory", text="Simulation Directory")

        row = layout.row(align=True)
        row.operator("traitblender.imaging_pipeline", text="Simulate Dataset", icon='PLAY')