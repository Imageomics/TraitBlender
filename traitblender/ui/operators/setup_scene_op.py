"""
TraitBlender Setup Scene Operator

Operator for setting up the scene for trait blending operations.
"""

import bpy
from bpy.types import Operator
import os
from ...core.helpers import get_asset_path, apply_material
from ...core.datasets.traitblender_dataset import update_filepath
from bpy.app.handlers import persistent
import yaml


def _append_object_from_museum_scene(object_name: str, context) -> bpy.types.Object | None:
    """Append a single object by name from museum_scene.blend and link it to the current scene."""
    museum_scene_path = get_asset_path("scenes", "museum_scene.blend")
    if not os.path.exists(museum_scene_path):
        raise FileNotFoundError(f"Museum scene not found at: {museum_scene_path}")

    with bpy.data.libraries.load(museum_scene_path) as (data_from, data_to):
        if object_name not in data_from.objects:
            raise RuntimeError(f"Object '{object_name}' not found in museum scene")
        data_to.objects = [object_name]

    appended = next((obj for obj in data_to.objects if obj is not None), None)
    if appended is None:
        raise RuntimeError(f"Failed to append object '{object_name}' from museum scene")

    # Link if not already linked to this scene collection.
    if appended.name not in context.scene.collection.objects:
        context.scene.collection.objects.link(appended)
    return appended

@persistent
def set_rendered_view(dummy):
    # Remove the handler so it only runs once
    if set_rendered_view in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(set_rendered_view)
    # Set all 3D viewports to rendered
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'RENDERED'

class TRAITBLENDER_OT_setup_scene(Operator):
    """Load the TraitBlender museum scene for morphological imaging"""
    
    bl_idname = "traitblender.setup_scene"
    bl_label = "Load Museum Scene"
    bl_description = "Load the pre-configured museum scene with lighting and camera setup"
    bl_options = {'REGISTER', 'UNDO'}
    
    _old_mouse_pos = None
    
    def execute(self, context):
        """Execute the setup scene operation"""
        
        # Get museum scene path using utility function
        museum_scene_path = get_asset_path("scenes", "museum_scene.blend")
        
        if os.path.exists(museum_scene_path):
            try:
                # Clear existing objects
                for obj in bpy.data.objects:
                    bpy.data.objects.remove(obj, do_unlink=True)
                
                # Set world to black
                if not context.scene.world:
                    context.scene.world = bpy.data.worlds.new("World")
                context.scene.world.use_nodes = True
                context.scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
                
                # Append objects and materials
                with bpy.data.libraries.load(museum_scene_path) as (data_from, data_to):
                    # Get all objects and materials
                    data_to.objects = data_from.objects
                    data_to.materials = data_from.materials
                
                # Link objects to scene
                for obj in data_to.objects:
                    if obj is not None:  # Skip None objects
                        bpy.context.scene.collection.objects.link(obj)

                # Ensure depsgraph/bounding boxes are up to date before table-relative placement (tb_location)
                bpy.context.view_layer.update()
                
                # Table: apply solid color (same pattern as Mat)
                if "Table" in bpy.data.objects:
                    apply_material("Table", hex_color="#432006", new_material_name="table_material")
                else:
                    self.report({'ERROR'}, "Initialization failed, table object not found in scene: Table")
                    return {'CANCELLED'}

                # Re-apply mat material using solid black color and name it 'mat_material'
                mat_name = "Mat"
                if mat_name in bpy.data.objects:
                    apply_material(mat_name, hex_color="#000000", new_material_name="mat_material")
                else:
                    self.report({'ERROR'}, f"Initialization failed, mat object not found in scene: {mat_name}")
                    return {'CANCELLED'}
                
                # Set rendered view
                set_rendered_view(None)
                
                # Load and apply default configuration from assets/configs/default.yaml
                default_yaml_path = get_asset_path("configs", "default.yaml")
                if os.path.exists(default_yaml_path):
                    with open(default_yaml_path, 'r') as file:
                        config_data = yaml.safe_load(file)
                    if config_data:
                        context.scene.traitblender_config.from_dict(config_data)
                        bpy.context.view_layer.update()
                        dataset = context.scene.traitblender_dataset
                        if dataset.filepath:
                            # Re-import from configured file after scene/config setup.
                            update_filepath(dataset, context)
                        else:
                            # Ensure dataset defaults are materialized so imaging has rows
                            # even when no external dataset has been imported yet.
                            dataset.csv = dataset.get_csv_for_editing()
                    else:
                        self.report({'WARNING'}, "Default configuration file is empty or invalid")
                else:
                    self.report({'WARNING'}, f"Default configuration file not found: {default_yaml_path}")
                
                self.report({'INFO'}, "Museum scene objects and materials appended successfully.")
            except Exception as e:
                self.report({'ERROR'}, f"Failed to append museum scene: {str(e)}")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, f"Museum scene not found at: {museum_scene_path}")
            self.report({'INFO'}, "Scene setup cancelled - museum scene file missing")
            return {'CANCELLED'}

        return {'FINISHED'}
    
    def invoke(self, context, event):
        """Called when the operator is invoked"""
        # Background / no WM: cannot show confirm dialog; run without prompting.
        if bpy.data.is_dirty and not getattr(bpy.app, "background", False) and context.window_manager.windows:
            window = context.window_manager.windows[0]
            center_x = window.width // 2
            center_y = window.height // 2
            window.cursor_warp(center_x, center_y)
            return context.window_manager.invoke_confirm(self, event)
        else:
            return self.execute(context)
    
    def draw(self, context):
        """Draw the confirmation dialog"""
        layout = self.layout
        layout.label(text="Loading the museum scene will replace your current work.")
        layout.label(text="Make sure to save any important changes first.")
        layout.separator()
        layout.label(text="Continue?", icon='QUESTION')


class TRAITBLENDER_OT_add_ruler(Operator):
    """Append a fresh Ruler object and apply current ruler config values."""

    bl_idname = "traitblender.add_ruler"
    bl_label = "Add Ruler"
    bl_description = "Append the Ruler object from the museum scene and apply ruler configuration"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            ruler_obj = _append_object_from_museum_scene("Ruler", context)
            if ruler_obj is None:
                self.report({'ERROR'}, "Failed to append Ruler object")
                return {'CANCELLED'}

            # Ensure transforms/depsgraph are fresh before applying table-relative placement.
            bpy.context.view_layer.update()

            # Apply current ruler config values to the newly appended object.
            config = getattr(context.scene, "traitblender_config", None)
            if config and hasattr(config, "ruler"):
                ruler_cfg = config.ruler
                ruler_obj.tb_location = tuple(ruler_cfg.tb_location)
                ruler_obj.tb_rotation = tuple(ruler_cfg.tb_rotation)
                hidden = bool(ruler_cfg.hide)
                ruler_obj.hide_viewport = hidden
                ruler_obj.hide_render = hidden

            bpy.context.view_layer.update()
            self.report({'INFO'}, f"Ruler added: {ruler_obj.name}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to add ruler: {e}")
            return {'CANCELLED'}
