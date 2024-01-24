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
from .ImageNoising import *

bl_info = {
    "name": "TraitBlender",
    "description": "Simulate raw image/mesh datasets under artificial models of biological evolution",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "Viewport > TraitBlender Tab",
    "warning": "",
    "doc_url": "in progress",
    "support": "TESTING",
    "category": "User Interface"
}

def register():
    
    ##Register Operators
    ###BackGroundPlanes
    bpy.utils.register_class(ImportBackgroundImageOperator)
    bpy.utils.register_class(CreateBackgroundImageMeshOperator)
    bpy.utils.register_class(ToggleBackgroundPlanesOperator)
    bpy.utils.register_class(HideBackgroundPlanesOperator)
    bpy.utils.register_class(BackgroundControls)
    bpy.utils.register_class(ScaleBackgroundPlanesOperator)
    bpy.utils.register_class(CallUpdateBackgroundPlaneDistanceOperator)

    ###CamerasRendering
    bpy.utils.register_class(ToggleCamerasOperator)
    bpy.utils.register_class(HideCamerasOperator)
    bpy.utils.register_class(CameraControls)
    bpy.utils.register_class(RenderAllCamerasOperator)
    bpy.utils.register_class(SetCameraViewOperator)
    bpy.utils.register_class(SelectRenderDirectoryOperator)

    ###DeleteAllObjecctsOperator
    bpy.utils.register_class(DeleteAllObjectsOperator)

    ###ExportActiveObjectOperator
    bpy.utils.register_class(ExportActiveObjectOperator)

    ###ExportSettingsOperator
    bpy.utils.register_class(ExportSettingsOperator)

    ###MeshGeneratingFunction
    bpy.utils.register_class(OpenMeshFunctionFileBrowserOperator)
    bpy.utils.register_class(ImportMakeMeshFunctionPathOperator)
    bpy.utils.register_class(ExecuteStoredFunctionOperator)

    ###Segmentation
    bpy.utils.register_class(SegmentationControls)
    bpy.utils.register_class(SegmentationControlsProperty)
    bpy.utils.register_class(SaveVertexGroupsToCSVOperator)
    bpy.utils.register_class(LoadVertexGroupsFromCSVOperator)

    ###Suns
    bpy.utils.register_class(SunControls)    
    bpy.utils.register_class(ToggleSunsOperator)
    bpy.utils.register_class(HideSunsOperator)
    bpy.utils.register_class(SunControlsPanel) 
    bpy.utils.register_class(UpdateSunStrengthOperator)

    ###TraitBlenderPanel
    bpy.utils.register_class(TraitBlenderPanel)

    ###TraitDataCSV
    bpy.utils.register_class(CSVLabelProperties) 
    bpy.utils.register_class(ImportCSVOperator)
    bpy.utils.register_class(ExecuteWithSelectedCSVRowOperator)

    ###WorldBackground
    bpy.utils.register_class(WorldBackgroundControls)
    bpy.utils.register_class(ChangeWorldBackgroundColor)
    bpy.utils.register_class(ExportControlsPropertyGroup)   

    ###Random Camera Effects
    bpy.utils.register_class(RandomCamerasRotationOperator)
    bpy.utils.register_class(RandomCamerasDistanceOperator)
    bpy.utils.register_class(RandomWorldBackgroundColor)
    bpy.utils.register_class(RandomSunsHideOperator)
    bpy.types.Scene.camera_distance_mu = bpy.props.FloatProperty(name="Mean Distance", default=10.0)
    bpy.types.Scene.camera_distance_sd = bpy.props.FloatProperty(name="Std Dev Distance", default=0.0)
    bpy.types.Scene.red_mu = bpy.props.FloatProperty(name="Red Mean", default=1.0, soft_min=0, soft_max=1)
    bpy.types.Scene.red_sd = bpy.props.FloatProperty(name="Red Std Dev", default=0.0, min=0.0, max=1)
    bpy.types.Scene.green_mu = bpy.props.FloatProperty(name="Green Mean", default=1.0, min=0, max=1)
    bpy.types.Scene.green_sd = bpy.props.FloatProperty(name="Green Std Dev", default=0.0, min=0.0, max=1)
    bpy.types.Scene.blue_mu = bpy.props.FloatProperty(name="Blue Mean", default=1.0, min=0, max=1)
    bpy.types.Scene.blue_sd = bpy.props.FloatProperty(name="Blue Std Dev", default=0.0, min=0.0, max=1)
    bpy.types.Scene.alpha_mu = bpy.props.FloatProperty(name="Alpha Mean", default=1.0, min=0, max=1)
    bpy.types.Scene.alpha_sd = bpy.props.FloatProperty(name="Alpha Std Dev", default=0.0, min=0.0, max=1)
    bpy.types.Scene.x_mu = bpy.props.FloatProperty(name="X Mean", default=0)
    bpy.types.Scene.x_sd = bpy.props.FloatProperty(name="X Std Dev", default=0)
    bpy.types.Scene.y_mu = bpy.props.FloatProperty(name="Y Mean", default=0)
    bpy.types.Scene.y_sd = bpy.props.FloatProperty(name="Y Std Dev", default=0)
    bpy.types.Scene.z_mu = bpy.props.FloatProperty(name="Z Mean", default=0)
    bpy.types.Scene.z_sd = bpy.props.FloatProperty(name="Z Std Dev", default=0)
    bpy.utils.register_class(RandomizationControls)
    bpy.types.Scene.randomization_controls = bpy.props.PointerProperty(type=RandomizationControls)


    
    #Register Properties

    bpy.types.Scene.export_settings_directory = bpy.props.StringProperty(
        name="Export Directory",
        description="Directory where the settings will be exported",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    bpy.types.Scene.export_controls_property = bpy.props.PointerProperty(type=ExportControlsPropertyGroup)
    
    bpy.types.Scene.random_noising_property = bpy.props.PointerProperty(type=ExportControlsPropertyGroup)

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

    bpy.types.Scene.csv_label_props = bpy.props.PointerProperty(type=CSVLabelProperties)

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

    bpy.types.Scene.mesh_generation_controls = bpy.props.BoolProperty(name="Mesh Generation Controls", default=False)

    bpy.types.Scene.make_mesh_function_path = bpy.props.StringProperty(
	    name="Make Mesh Function Path",
	    description="Path to the mesh function",
	    default="",
	    maxlen=1024,
	    subtype='FILE_PATH'
	)


    bpy.types.Scene.world_background_controls = bpy.props.PointerProperty(type=WorldBackgroundControls)

    bpy.types.Scene.background_controls = bpy.props.PointerProperty(type=BackgroundControls)

    bpy.types.Scene.segmentation_controls_property = bpy.props.PointerProperty(type=SegmentationControlsProperty)
    bpy.types.Scene.lights_controls = bpy.props.BoolProperty(default=False)

    bpy.types.Scene.sun_controls = bpy.props.PointerProperty(type=SunControls)
    bpy.types.Scene.sun_lamp_controls = bpy.props.BoolProperty(name="Sun Lamp Controls", default=False)

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


    bpy.types.VIEW3D_MT_mesh_add.append(mesh_menu_func)

    bpy.types.Scene.camera_controls = bpy.props.PointerProperty(type=CameraControls)
    bpy.types.Scene.place_cameras_distance = bpy.props.FloatProperty(
        name="Place Cameras Distance",
        default=10.0,
        min=0.001,
        update=update_camera_distance  # Add the update function here
    )

    #background plane distance
    bpy.types.Scene.background_plane_distance = bpy.props.FloatProperty(
        name="Background Plane Distance",
        default=10.0,
        min=0.001,
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
        subtype='FILE_PATH'
    )


    bpy.types.Scene.mesh_generation_controls = bpy.props.BoolProperty(
        name="Mesh Generation Controls",
        description="Expand/Collapse Mesh Generation Controls",
        default=False
    )

    bpy.types.Scene.use_suns = bpy.props.BoolProperty(
        name="Use Suns",
        description="Enable or disable the use of suns in the dataset",
        default=True
    )

    bpy.types.Scene.use_cameras = bpy.props.BoolProperty(
        name="Use Cameras",
        description="Enable or disable the use of cameras in the dataset",
        default=True
    )

    bpy.types.Scene.use_3d_export = bpy.props.BoolProperty(
        name="Use 3D Export",
        description="Enable or disable the use of 3D export in the dataset",
        default=True
    )

    bpy.types.Scene.dataset_options = bpy.props.BoolProperty(
        name="Dataset Options",
        description="Toggle to show or hide additional dataset options",
        default=False
    )



    bpy.app.handlers.depsgraph_update_post.append(delete_cameras_on_mesh_deletion)
    
def unregister():
    
    ##Unregister operators
    ###BackGroundPlanes
    bpy.utils.unregister_class(ImportBackgroundImageOperator)
    bpy.utils.unregister_class(CreateBackgroundImageMeshOperator)    
    bpy.utils.unregister_class(ToggleBackgroundPlanesOperator)    
    bpy.utils.unregister_class(HideBackgroundPlanesOperator)    
    bpy.utils.unregister_class(BackgroundControls)    
    bpy.utils.unregister_class(ScaleBackgroundPlanesOperator)    
    bpy.utils.unregister_class(CallUpdateBackgroundPlaneDistanceOperator)    
    
    ###CamerasRendering
    bpy.utils.unregister_class(ToggleCamerasOperator)    
    bpy.utils.unregister_class(HideCamerasOperator)
    bpy.utils.unregister_class(CameraControls)
    bpy.utils.unregister_class(RenderAllCamerasOperator)
    bpy.utils.unregister_class(SetCameraViewOperator)
    bpy.utils.unregister_class(SelectRenderDirectoryOperator)    
    
    ###DeleteAllObjectsOperator
    bpy.utils.unregister_class(DeleteAllObjectsOperator)
    
    ###ExportActiveObjectOperator
    bpy.utils.unregister_class(ExportActiveObjectOperator)
     
    ###ExportSettingsOperator 
    bpy.utils.unregister_class(ExportSettingsOperator)
    
    ###MeshGeneratingFunction
    bpy.utils.unregister_class(OpenMeshFunctionFileBrowserOperator)
    bpy.utils.unregister_class(ImportMakeMeshFunctionPathOperator)
    bpy.utils.unregister_class(ExecuteStoredFunctionOperator)    
    
    ###Segmentation
    bpy.utils.unregister_class(SegmentationControls)
    bpy.utils.unregister_class(SegmentationControlsProperty)    
    bpy.utils.unregister_class(SaveVertexGroupsToCSVOperator)    
    bpy.utils.unregister_class(LoadVertexGroupsFromCSVOperator)    
    
    ###Suns
    bpy.utils.unregister_class(SunControls)
    bpy.utils.unregister_class(ToggleSunsOperator)
    bpy.utils.unregister_class(HideSunsOperator)
    bpy.utils.unregister_class(SunControlsPanel)
    bpy.utils.unregister_class(UpdateSunStrengthOperator)    
    
    ###TraitBlenderPanel
    bpy.utils.unregister_class(TraitBlenderPanel)
    
    ###TraitDataCSV    
    bpy.utils.unregister_class(CSVLabelProperties)
    bpy.utils.unregister_class(ImportCSVOperator)    
    bpy.utils.unregister_class(ExecuteWithSelectedCSVRowOperator)    
    
    ###WorldBackground
    bpy.utils.unregister_class(WorldBackgroundControls)
    bpy.utils.unregister_class(ChangeWorldBackgroundColor)
    bpy.utils.unregister_class(ExportControlsPropertyGroup)

    ###Random Camera Effects
    bpy.utils.unregister_class(RandomCamerasRotationOperator)
    bpy.utils.unregister_class(RandomCamerasDistanceOperator)
    bpy.utils.unregister_class(RandomWorldBackgroundColor)
    bpy.utils.unregister_class(RandomSunsHideOperator)
    del bpy.types.Scene.camera_distance_mu
    del bpy.types.Scene.camera_distance_sd
    del bpy.types.Scene.red_mu
    del bpy.types.Scene.red_sd
    del bpy.types.Scene.green_mu
    del bpy.types.Scene.green_sd
    del bpy.types.Scene.blue_mu
    del bpy.types.Scene.blue_sd
    del bpy.types.Scene.alpha_mu
    del bpy.types.Scene.alpha_sd
    del bpy.types.Scene.randomization_controls
    bpy.utils.unregister_class(RandomizationControls)
    
    ###Dataset Options
    del bpy.types.Scene.use_suns
    del bpy.types.Scene.use_cameras
    del bpy.types.Scene.use_3d_export
    del bpy.types.Scene.dataset_options
    
    
    #unregister properties
    bpy.types.VIEW3D_MT_mesh_add.remove(mesh_menu_func)
    del bpy.types.Scene.world_background_controls 
    del bpy.types.Scene.make_mesh_function_path 
    del bpy.types.Scene.csv_label_props
    del bpy.types.Scene.export_controls_property
    del bpy.types.Scene.export_directory
    del bpy.types.Scene.export_format
    del bpy.types.Scene.sun_controls
    del bpy.types.Scene.segmentation_controls_property
    del bpy.types.Scene.lights_controls 
    del bpy.types.Scene.background_controls
    del bpy.types.Scene.sun_strength
    del bpy.types.Scene.background_image_reference
    #del bpy.types.Scene.traitblender_settings
    del bpy.types.Scene.place_cameras_distance
    del bpy.types.Scene.camera_controls
    del bpy.types.Scene.render_output_directory
    del bpy.types.Scene.csv_file_path
    del bpy.types.Scene.csv_labels
    del bpy.types.Scene.export_settings_directory
    if hasattr(bpy.types.Scene, 'csv_label_enum'):
        del bpy.types.Scene.csv_label_enum

    del bpy.types.Scene.x_mu
    del bpy.types.Scene.x_sd
    del bpy.types.Scene.y_mu
    del bpy.types.Scene.y_sd
    del bpy.types.Scene.z_mu
    del bpy.types.Scene.z_sd




    
    bpy.app.handlers.depsgraph_update_post.remove(delete_cameras_on_mesh_deletion)

if __name__ == "__main__":
    register()
    