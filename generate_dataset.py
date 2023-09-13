
import bpy
import json

## read in mesh function and trait csv
make_mesh_function_path = "D://TraitBlender/TraitBlender/Examples/Functions/make_snail.py"
csv_file_path = "D://TraitBlender/TraitBlender/Examples/Data/snails.csv"
json_file_path = "C://Users/caleb/Downloads/traitblender_settings.json"
use_suns = True
use_cameras = True
#use_model_export = True
use_3d_export = True

def load_settings_from_json(json_path):
    with open(json_path, 'r') as f:
        settings = json.load(f)
    return settings


# Path to the JSON file containing the settings
settings = load_settings_from_json(json_file_path)

# Extracting variables from the loaded settings
wc_red, wc_green, wc_blue, wc_alpha = settings["World Background Controls"]["wc_colors"]

## background variable extraction    
background_plane_distance = settings["Background Controls"]["background_plane_distance"]
bg_scale_x, bg_scale_y, bg_scale_z = settings["Background Controls"]["bg_scales"]
sun_strength = settings["Lights"]["sun_strength"]
place_cameras_distance = settings["Camera Controls"]["place_cameras_distance"]
camera_width, camera_height = settings["Camera Controls"]["camera_width_height"]
focal_length = settings["Camera Controls"]["focal_length"]
render_output_directory = settings["Camera Controls"]["render_output_directory"]
obj_export_directory = settings["obj_export_directory"]
export_format = settings["export_format"]
cameras_to_render = settings["Camera Controls"]["Cameras to Render"]

## Defining the scene
scene = bpy.data.scenes["Scene"]

## Import the function
scene.make_mesh_function_path = make_mesh_function_path

## setting mesh function and trait data related properties
scene.csv_file_path = csv_file_path
scene.make_mesh_function_path = make_mesh_function_path

## set world color properties
scene.world_background_controls.red = wc_red
scene.world_background_controls.green = wc_green
scene.world_background_controls.blue = wc_blue
scene.world_background_controls.alpha = wc_alpha

## set background plane/image properties
scene.background_plane_distance = background_plane_distance
scene.background_controls.plane_scale_x = bg_scale_x
scene.background_controls.plane_scale_y = bg_scale_y
scene.background_controls.plane_scale_z = bg_scale_z

## set the strength of the suns
scene.sun_strength = sun_strength

## set the camera related properties
scene.place_cameras_distance = place_cameras_distance
scene.camera_controls.camera_width = camera_width
scene.camera_controls.camera_height = camera_height
scene.camera_controls.focal_length = focal_length
scene.render_output_directory = render_output_directory

## set 3D object export properties
scene.export_format = export_format
scene.export_directory = obj_export_directory






bpy.ops.object.import_csv()
tips = bpy.data.scenes['Scene']['tip_labels']
traits = bpy.data.scenes['Scene']['csv_data']
mesh_function = bpy.ops.object.execute_with_selected_csv_row

for index, label in enumerate(tips):
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Delete all objects, including hidden ones and lights in all collections
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj)
    
    
    index = str(index)
    scene.csv_label_props.csv_label_enum = index
    mesh_function()
    
    bpy.ops.scene.change_background_color()
    
    if settings["Background Controls"]["background_plane_image_path"] != "None":
        bpy.ops.traitblender.import_background_image(filepath=settings["Background Controls"]["background_plane_image_path"])
        bpy.ops.object.toggle_background_planes()
        bpy.ops.object.scale_background_planes()
        
    if use_suns:
        bpy.ops.object.toggle_suns()
        bpy.ops.object.update_sun_strength()
        
    if use_cameras:
        bpy.ops.object.toggle_cameras()
        bpy.ops.object.render_all_cameras(camera_names=cameras_to_render)
        
    if use_3d_export:
        bpy.ops.object.export_active_object()
    
print("Done!")