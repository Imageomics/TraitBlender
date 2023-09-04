import bpy
import json
import bmesh
import numpy as np
import sys
import os
import math
import csv
import types
import inspect
import bpy_extras
from mathutils import Matrix, Vector

from .DeleteAllObjectsOperator import *
from .ExportActiveObjectOperator import *
from .Suns import *
from .TraitDataCSV import *
from .MeshGeneratingFunction import *
from .CamerasRendering import *
from .BackGroundPlanes import *
from .Segmentation import *

bl_info = {
    "name": "TraitBlender",
    "blender": (2, 80, 0),
    # ... other metadata
}

        


class WorldBackgroundControls(bpy.types.PropertyGroup):
    expanded: bpy.props.BoolProperty(
        name="Background",
        description="Expand the background controls",
        default=False
    )
    
    red: bpy.props.FloatProperty(
        name="Red",
        description="Red component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    green: bpy.props.FloatProperty(
        name="Green",
        description="Green component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    blue: bpy.props.FloatProperty(
        name="Blue",
        description="Blue component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    alpha: bpy.props.FloatProperty(
        name="Alpha",
        description="Alpha component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )

    world_color_expanded: bpy.props.BoolProperty(
        name="World Color Expanded",
        default=True
    )
    
    imported_backgrounds_expanded: bpy.props.BoolProperty(
        name="Imported Backgrounds Expanded",
        default=True
    )
    
    background_scale_expanded: bpy.props.BoolProperty(
        name="Background Scale Expanded",
        default=True
    )
    


class ChangeWorldBackgroundColor(bpy.types.Operator):
    bl_idname = "scene.change_background_color"
    bl_label = "Change World Background Color"
    
    def execute(self, context):
        # Access the active scene
        scene = context.scene

        # Access the world settings
        world = scene.world

        # Access the background_controls property group
        world_background_controls = context.scene.world_background_controls

        # Enable use_nodes to allow node-based modifications
        world.use_nodes = True

        # Access the node tree
        node_tree = world.node_tree

        # Find the "Background" node
        world_background_node = node_tree.nodes.get("Background")

        # Change the color of the background
        world_background_node.inputs[0].default_value = (
            world_background_controls.red, 
            world_background_controls.green, 
            world_background_controls.blue, 
            world_background_controls.alpha
        )
        
        return {'FINISHED'}

class ExportSettingsOperator(bpy.types.Operator):
    bl_idname = "object.export_settings"
    bl_label = "Export Settings"

    def execute(self, context):
        # Fetch the relevant settings from the Scene
        scene = context.scene

        # Fetch the relevant settings from the UI controls
        world_background_controls = scene.world_background_controls
        background_controls = scene.background_controls
        camera_controls = scene.camera_controls

        # Get the background image path
        image_name = scene.background_image_reference
        image_filepath = bpy.data.images.get(image_name).filepath if bpy.data.images.get(image_name) else "None"

        # Format these settings into a string
        settings_str = f"World Background Controls:\n"
        settings_str += f"    Red: {world_background_controls.red:.5f}\n"
        settings_str += f"    Green: {world_background_controls.green:.5f}\n"
        settings_str += f"    Blue: {world_background_controls.blue:.5f}\n"
        settings_str += f"    Alpha: {world_background_controls.alpha:.5f}\n"

        settings_str += f'\nBackground Controls:\n'
        settings_str += f'    Background Image Path: "{image_filepath}"\n'
        settings_str += f'    Background Plane Distance: {scene.background_plane_distance:.5f}\n'
        settings_str += f'    Background Plane Scale X: {background_controls.plane_scale_x:.5f}\n'
        settings_str += f'    Background Plane Scale Y: {background_controls.plane_scale_y:.5f}\n'
        settings_str += f'    Background Plane Scale Z: {background_controls.plane_scale_z:.5f}\n'

        settings_str += f"\nLights:\n"
        settings_str += f"    Sun Strength: {scene.sun_strength:.5f}\n"

        # Construct the string argument for the RenderAllCamerasOperator
        camera_names_list = []
        if camera_controls.render_camera_top:
            camera_names_list.append('camera.top')
        if camera_controls.render_camera_bottom:
            camera_names_list.append('camera.bottom')
        if camera_controls.render_camera_right:
            camera_names_list.append('camera.right')
        if camera_controls.render_camera_left:
            camera_names_list.append('camera.left')
        if camera_controls.render_camera_front:
            camera_names_list.append('camera.front')
        if camera_controls.render_camera_back:
            camera_names_list.append('camera.back')
        camera_names_str = ','.join(camera_names_list)

        settings_str += f'\nCamera Controls:\n'
        settings_str += f'    Cameras to Render: "{camera_names_str}"\n'
        settings_str += f'    Place Cameras Distance: {scene.place_cameras_distance:.5f}\n'
        settings_str += f'    Camera Width: {camera_controls.camera_width:.5f}\n'
        settings_str += f'    Camera Height: {camera_controls.camera_height:.5f}\n'
        settings_str += f'    Focal Length: {camera_controls.focal_length:.5f}\n'
        settings_str += f'    Render Output Directory: "{scene.render_output_directory}"\n'

        # Print the settings string to the console for verification
        print(settings_str)

        return {'FINISHED'}


class TraitBlenderPanel(bpy.types.Panel):
    bl_label = "TraitBlender"
    bl_idname = "VIEW3D_PT_traitblender"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TraitBlender"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        background_controls = context.scene.background_controls
        camera_controls = context.scene.camera_controls
        segmentation_controls_property = context.scene.segmentation_controls_property  # Get the property group from the scene
        world_background_controls = context.scene.world_background_controls 
        
        layout.prop(context.scene, "mesh_generation_controls", icon="TRIA_DOWN" if context.scene.mesh_generation_controls else "TRIA_RIGHT", emboss=False, text="Mesh Generation")
        if context.scene.mesh_generation_controls:
                row = layout.row()
                row.alignment = 'CENTER'
                row.label(text="Select Mesh Function File", icon='NONE')
                
                # File path selection
                row = layout.row(align=True)
                row.prop(context.scene, 'make_mesh_function_path', text="")
                row.operator("object.open_mesh_function_file_browser", icon='FILEBROWSER', text="")
                
                # Button to execute the function
                layout.operator("object.execute_stored_function", text="Run Function")
                layout.prop(context.scene, "csv_file_path", text="CSV File Path")
                layout.operator("object.import_csv", text="Import CSV")

                if 'csv_data' in context.scene:
                    layout.prop(context.scene.csv_label_props, "csv_label_enum", text="Select Label")
        
                layout.operator("object.execute_with_selected_csv_row", text="Run Function with Selected CSV Row")        
        
        layout.prop(world_background_controls, "expanded", icon="TRIA_DOWN" if world_background_controls.expanded else "TRIA_RIGHT", emboss=False)
        if world_background_controls.expanded:
            box = layout.box()
            
            # Center the text "World Color"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="World Color")
            
            # Add RGBA controls with letters inside the fields
            row = box.row()
            row.prop(world_background_controls, "red", text="R")
            row = box.row()
            row.prop(world_background_controls, "green", text="G")
            row = box.row()
            row.prop(world_background_controls, "blue", text="B")
            row = box.row()
            row.prop(world_background_controls, "alpha", text="A")
            
            box.operator("scene.change_background_color", text="Apply Background Color")

            # New box for Imported Backgrounds
            box = layout.box()

            # Center the text "Imported Backgrounds"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Imported Backgrounds")

            # Add existing controls for imported backgrounds
            box.operator("traitblender.import_background_image", text="Import Background Image")
            box.operator("object.toggle_background_planes", text="Toggle Background")
            box.operator("object.hide_background_planes", text="Hide Background")
            box.prop(context.scene, "background_plane_distance", text="Background Distance")

            # New box for Background Plane Scale
            box = layout.box()

            # Center the text "Background Plane Scale"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Background Plane Scale")

            # Add scale controls for the background planes
            row = box.row()
            row.prop(background_controls, "plane_scale_x", text="X")
            row = box.row()
            row.prop(background_controls, "plane_scale_y", text="Y")
            row = box.row()
            row.prop(background_controls, "plane_scale_z", text="Z")
            box.operator("object.scale_background_planes", text="Apply Scaling")









        layout.prop(context.scene, "lights_controls", icon="TRIA_DOWN" if context.scene.lights_controls else "TRIA_RIGHT", emboss=False, text="Lights")
        if context.scene.lights_controls:
            # Button to toggle all suns
            row = layout.row()
            row.operator("object.toggle_suns", text="Toggle All Suns")

            # Button to hide all suns
            row = layout.row()
            row.operator("object.hide_suns", text="Hide All Suns")

            # Checkboxes to toggle individual suns in three rows
            sun_pairs = [("Front", "Back"), ("Left", "Right"), ("Top", "Bottom")]
            for pair in sun_pairs:
                row = layout.row()
                row.operator("object.hide_suns", text=pair[0]).sun_names = f"sun.{pair[0].lower()}"
                row.operator("object.hide_suns", text=pair[1]).sun_names = f"sun.{pair[1].lower()}"
            layout = self.layout
            layout.prop(context.scene, "sun_strength", slider=True)
            layout.operator("object.update_sun_strength", text="Update Sun Strength")




        layout.prop(camera_controls, "expanded", icon="TRIA_DOWN" if camera_controls.expanded else "TRIA_RIGHT", emboss=False)
        if camera_controls.expanded:
            layout.operator("object.toggle_cameras", text="Toggle Cameras")
            layout.operator("object.hide_cameras", text="Hide Cameras")

            # Centered "View & Render Settings" text
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="View & Render Settings", icon='NONE')

            # Camera distance control
            row = layout.row()
            row.label(text="Distance:")
            row.prop(context.scene, "place_cameras_distance", text="")

            # Camera width and height controls
            row = layout.row()
            row.label(text="Width:")
            row.prop(camera_controls, "camera_width", text="")
            row = layout.row()
            row.label(text="Height:")
            row.prop(camera_controls, "camera_height", text="")

            # Focal length control
            row = layout.row()
            row.label(text="Focal Length:")
            row.prop(camera_controls, "focal_length", text="")
            
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Camera Preview", icon='NONE')
            # Buttons to set the view to different angles

            # Row for Front & Back buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Front").angle = "Front"
            row.operator("object.set_camera_view", text="Back").angle = "Back"

            # Row for Left & Right buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Left").angle = "Left"
            row.operator("object.set_camera_view", text="Right").angle = "Right"

            # Row for Top & Bottom buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Top").angle = "Top"
            row.operator("object.set_camera_view", text="Bottom").angle = "Bottom"

            # Create a 3x2 grid layout for cameras to render
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Cameras to Render", icon='NONE')
            grid = layout.grid_flow(row_major=True, columns=2, even_columns=True)
            grid.prop(camera_controls, "render_camera_top")
            grid.prop(camera_controls, "render_camera_bottom")
            grid.prop(camera_controls, "render_camera_right")
            grid.prop(camera_controls, "render_camera_left")
            grid.prop(camera_controls, "render_camera_front")
            grid.prop(camera_controls, "render_camera_back")

            # Construct the string argument for the RenderAllCamerasOperator
            camera_names_list = []
            if camera_controls.render_camera_top:
                camera_names_list.append('camera.top')
            if camera_controls.render_camera_bottom:
                camera_names_list.append('camera.bottom')
            if camera_controls.render_camera_right:
                camera_names_list.append('camera.right')
            if camera_controls.render_camera_left:
                camera_names_list.append('camera.left')
            if camera_controls.render_camera_front:
                camera_names_list.append('camera.front')
            if camera_controls.render_camera_back:
                camera_names_list.append('camera.back')
            camera_names_str = ','.join(camera_names_list)

            # Centered "Render Directory" text
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Render Directory", icon='NONE')

            # Render directory selection
            layout.prop(context.scene, "render_output_directory", text="")

            layout.operator("object.render_all_cameras", text="Render Selected Cameras").camera_names = camera_names_str


        export_controls_property = context.scene.export_controls_property  # Replace with the correct attribute name if needed
        layout.prop(export_controls_property, "export_controls", icon="TRIA_DOWN" if export_controls_property.export_controls else "TRIA_RIGHT", emboss=False, text="3D Export")
        if export_controls_property.export_controls:  # Use the property from the property group
            
            # Row for the user to specify the export directory
            row = layout.row()
            row.prop(context.scene, "export_directory", text="Export Directory")
            
            # Dropdown for selecting the export format
            row = layout.row()
            row.prop(context.scene, "export_format", text="File Format")
            
            # Button to trigger the export
            row = layout.row()
            row.operator("object.export_active_object", text="Export Active Object")



        layout.prop(segmentation_controls_property, "segmentation_controls", icon="TRIA_DOWN" if segmentation_controls_property.segmentation_controls else "TRIA_RIGHT", emboss=False, text="Segmentation / Vertex Groups")
        if segmentation_controls_property.segmentation_controls:  # Use the property from the property group
            row = layout.row()
            row.template_list("MESH_UL_vgroups", "", obj, "vertex_groups", obj.vertex_groups, "active_index", rows=2)

            col = row.column(align=True)
            col.operator("object.vertex_group_add", icon='ADD', text="")
            col.operator("object.vertex_group_remove", icon='REMOVE', text="").all = False
            col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")
            col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            row = layout.row()
            row.operator("object.vertex_group_assign", text="Assign")
            row.operator("object.vertex_group_remove_from", text="Remove")
            row = layout.row()
            row.operator("object.vertex_group_select", text="Select")
            row.operator("object.vertex_group_deselect", text="Deselect")
            
            # Add a button to save vertex groups to CSV
            row = layout.row()
            row.operator("object.save_vertex_groups_to_csv", text="Save Vertex Groups to CSV").csv_file_path = context.scene.csv_file_path_save
            
            # Add a row for the user to specify the CSV file path for saving vertex groups
            row = layout.row()
            row.prop(context.scene, "csv_file_path_save", text="")

            # Add a button to load vertex groups from CSV
            row = layout.row()
            row.operator("object.load_vertex_groups_from_csv", text="Load Vertex Groups from CSV").csv_file_path = context.scene.csv_file_path_load

            # Add a row for the user to specify the CSV file path for loading vertex groups
            row = layout.row()
            row.prop(context.scene, "csv_file_path_load", text="")

            layout = self.layout
            
        layout.operator("object.export_settings")
        layout.operator("object.delete_all_objects", text="Delete All Objects")


def register():
    
    bpy.utils.register_class(DeleteAllObjectsOperator)
    bpy.utils.register_class(ExportControlsPropertyGroup)
    bpy.types.Scene.export_controls_property = bpy.props.PointerProperty(type=ExportControlsPropertyGroup)
    bpy.utils.register_class(ExportActiveObjectOperator)
    bpy.types.Scene.export_directory = bpy.props.StringProperty(
        name="Export Directory",
        description="Directory to export the 3D object",
      default="",
        subtype='DIR_PATH'
    )

    bpy.types.Scene.export_format = bpy.props.EnumProperty(
        name="Export Format",
        items=[('.obj', '.OBJ', 'Wavefront OBJ file format'), 
               ('.fbx', '.FBX', 'Autodesk FBX file format')],
        default='.obj'
    )

    bpy.utils.register_class(ExecuteWithSelectedCSVRowOperator)
    bpy.utils.register_class(CSVLabelProperties)
    bpy.types.Scene.csv_label_props = bpy.props.PointerProperty(type=CSVLabelProperties)
    bpy.utils.register_class(ImportCSVOperator)
    bpy.types.Scene.csv_file_path = bpy.props.StringProperty(
        name="CSV File Path",
        description="Path to the CSV file",
        default="",
        subtype='FILE_PATH'
    )
    bpy.types.Scene.csv_labels = bpy.props.StringProperty(
        name="CSV Labels",
        description="Labels imported from CSV",
        update=lambda self, context: setattr(
            bpy.types.Scene,
            'csv_label_enum',
            bpy.props.EnumProperty(
                items=[(str(i), name, name) for i, name in enumerate(self['csv_labels'])],
                name="CSV Labels"
            )
        )
    )
    bpy.utils.register_class(OpenMeshFunctionFileBrowserOperator)
    bpy.utils.register_class(ImportMakeMeshFunctionPathOperator)
    bpy.utils.register_class(ExecuteStoredFunctionOperator)
    bpy.types.Scene.make_mesh_function_path = bpy.props.StringProperty(
        name="Make Mesh Function Path",
        description="File path for the make_mesh function",
        default="",
    )
    bpy.utils.register_class(ImportBackgroundImageOperator)
    bpy.utils.register_class(ExportSettingsOperator)
    bpy.utils.register_class(WorldBackgroundControls)
    bpy.types.Scene.world_background_controls = bpy.props.PointerProperty(type=WorldBackgroundControls)
    bpy.utils.register_class(ChangeWorldBackgroundColor)
    bpy.utils.register_class(ToggleCamerasOperator)
    bpy.utils.register_class(TraitBlenderPanel)
    bpy.utils.register_class(CameraControls)
    bpy.utils.register_class(HideCamerasOperator)
    bpy.utils.register_class(SelectRenderDirectoryOperator)
    bpy.utils.register_class(RenderAllCamerasOperator)
    bpy.utils.register_class(ToggleBackgroundPlanesOperator)
    bpy.utils.register_class(ScaleBackgroundPlanesOperator)
    bpy.utils.register_class(HideBackgroundPlanesOperator)
    bpy.utils.register_class(SegmentationControls)
    bpy.utils.register_class(SegmentationControlsProperty)
    bpy.utils.register_class(SaveVertexGroupsToCSVOperator)
    bpy.utils.register_class(LoadVertexGroupsFromCSVOperator)
    bpy.utils.register_class(ToggleSunsOperator)
    bpy.utils.register_class(HideSunsOperator)
    bpy.utils.register_class(SunControlsPanel)
    bpy.utils.register_class(SetCameraViewOperator)
    bpy.utils.register_class(BackgroundControls)
    bpy.types.Scene.background_controls = bpy.props.PointerProperty(type=BackgroundControls)
    bpy.utils.register_class(CallUpdateBackgroundPlaneDistanceOperator)
    bpy.types.Scene.segmentation_controls_property = bpy.props.PointerProperty(type=SegmentationControlsProperty)
    bpy.types.Scene.lights_controls = bpy.props.BoolProperty(default=False)
    bpy.utils.register_class(SunControls)
    bpy.types.Scene.sun_controls = bpy.props.PointerProperty(type=SunControls)
    bpy.types.Scene.sun_lamp_controls = bpy.props.BoolProperty(name="Sun Lamp Controls", default=False)
    bpy.utils.register_class(UpdateSunStrengthOperator)
    bpy.types.Scene.sun_strength = bpy.props.FloatProperty(
        name="Sun Strength",
        description="Strength of the sun lamps",
        default=1.0,
        min=0.0,
        max=10.0
    )
    bpy.types.Scene.csv_file_path_save = bpy.props.StringProperty(
        name="CSV File Path to Save",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.csv_file_path_load = bpy.props.StringProperty(
        name="CSV File Path to Load",
        subtype='FILE_PATH'
    )


    bpy.types.Scene.background_controls = bpy.props.PointerProperty(type=BackgroundControls)
    bpy.types.Scene.background_image_reference = bpy.props.StringProperty(default="")

    bpy.utils.register_class(CreateBackgroundImageMeshOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(mesh_menu_func)

    bpy.types.Scene.camera_controls = bpy.props.PointerProperty(type=CameraControls)
    bpy.types.Scene.place_cameras_distance = bpy.props.FloatProperty(
        name="Place Cameras Distance",
        default=10.0,
        update=update_camera_distance  # Add the update function here
    )

    #background plane distance
    bpy.types.Scene.background_plane_distance = bpy.props.FloatProperty(
        name="Background Plane Distance",
        default=10.0,
        description="Distance of the background planes from the active object",
        update=update_background_plane_distance  # This will call the function whenever the property changes
    )

    
    bpy.types.Scene.render_output_directory = bpy.props.StringProperty(
        name="Render Output Directory",
        description="Directory to save the renders",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    
    bpy.types.Scene.make_mesh_function_path = bpy.props.StringProperty(
        name="Make Mesh Function Path",
        description="Path to the Python file containing the mesh-making function",
        default="",
        subtype='DIR_PATH'
    )


    bpy.types.Scene.mesh_generation_controls = bpy.props.BoolProperty(
        name="Mesh Generation Controls",
        description="Expand/Collapse Mesh Generation Controls",
        default=False
    )


    
    bpy.app.handlers.depsgraph_update_post.append(delete_cameras_on_mesh_deletion)
    
def unregister():
    
    bpy.utils.unregister_class(DeleteAllObjectsOperator)
    del bpy.types.Scene.export_controls_property
    bpy.utils.unregister_class(ExportControlsPropertyGroup)
    bpy.utils.unregister_class(ExportActiveObjectOperator)
    del bpy.types.Scene.export_directory
    del bpy.types.Scene.export_format
    bpy.utils.unregister_class(ExecuteWithSelectedCSVRowOperator)
    bpy.utils.unregister_class(CSVLabelProperties)
    del bpy.types.Scene.csv_label_props
    bpy.utils.unregister_class(ImportCSVOperator)
    del bpy.types.Scene.csv_file_path
    del bpy.types.Scene.csv_labels
    if hasattr(bpy.types.Scene, 'csv_label_enum'):
        del bpy.types.Scene.csv_label_enum
    bpy.utils.unregister_class(OpenMeshFunctionFileBrowserOperator)
    bpy.utils.unregister_class(ExecuteStoredFunctionOperator)
    bpy.utils.unregister_class(ImportMakeMeshFunctionPathOperator)
    del bpy.types.Scene.make_mesh_function_path
    bpy.utils.unregister_class(ImportMakeMeshFunctionOperator)
    bpy.utils.unregister_class(ImportBackgroundImageOperator)
    bpy.utils.unregister_class(ExportSettingsOperator)
    bpy.utils.unregister_class(WorldBackgroundControls)
    del bpy.types.Scene.world_background_controls
    bpy.utils.unregister_class(ToggleCamerasOperator)
    bpy.utils.unregister_class(TraitBlenderPanel)
    bpy.utils.unregister_class(CameraControls)
    bpy.utils.unregister_class(HideCamerasOperator)
    bpy.utils.unregister_class(SelectRenderDirectoryOperator)
    bpy.utils.unregister_class(RenderAllCamerasOperator)
    bpy.utils.unregister_class(ToggleBackgroundPlanesOperator)
    bpy.utils.unregister_class(ScaleBackgroundPlanesOperator)
    bpy.utils.unregister_class(HideBackgroundPlanesOperator)
    bpy.utils.unregister_class(SegmentationControlsProperty)
    bpy.utils.unregister_class(ToggleSunsOperator)
    bpy.utils.unregister_class(HideSunsOperator)
    bpy.utils.unregister_class(SunControlsPanel)
    bpy.utils.unregister_class(LoadVertexGroupsFromCSVOperator)
    bpy.utils.unregister_class(SaveVertexGroupsToCSVOperator)
    bpy.utils.unregister_class(SetCameraViewOperator)
    bpy.utils.unregister_class(ChangeBackgroundColor)
    bpy.utils.unregister_class(BackgroundControls)
    del bpy.types.Scene.background_controls
    bpy.utils.unregister_class(CallUpdateBackgroundPlaneDistanceOperator)
    del bpy.types.Scene.segmentation_controls_property
    del bpy.types.Scene.lights_controls
    bpy.utils.unregister_class(SunControls)
    del bpy.types.Scene.sun_controls
    bpy.utils.unregister_class(UpdateSunStrengthOperator)
    del bpy.types.Scene.sun_strength


    bpy.utils.unregister_class(ImportBackgroundImageOperator)
    bpy.utils.unregister_class(BackgroundControls)
    del bpy.types.Scene.background_controls
    del bpy.types.Scene.background_image_reference
    
    bpy.utils.unregister_class(CreateBackgroundImageMeshOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(mesh_menu_func)
 
    del bpy.types.Scene.traitblender_settings
    del bpy.types.Scene.place_cameras_distance
    del bpy.types.Scene.camera_controls
    del bpy.types.Scene.render_output_directory

    
    
    bpy.app.handlers.depsgraph_update_post.remove(delete_cameras_on_mesh_deletion)

if __name__ == "__main__":
    register()
    
    # bpy.ops.object.select_all(action='SELECT')
    # bpy.ops.object.delete()

