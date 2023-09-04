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
from .WorldBackground import *
from .ExportSettingsOperator import *
from .TraitBlenderPanel import *



bl_info = {
    "name": "TraitBlender",
    "blender": (2, 80, 0),
    # ... other metadata
}

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

