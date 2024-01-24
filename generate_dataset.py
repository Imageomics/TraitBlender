import bpy
import json
import sys
bpy.ops.preferences.addon_enable(module="TraitBlender")

# Function to get command-line arguments passed to Blender (skip the first two arguments which are blender related)
def get_args():
    args = sys.argv
    for i, arg in enumerate(args):
        if "--" == arg:
            custom_args = args[i + 1:]
            return custom_args
    return []

# Retrieve the paths and images_per_individual from command line arguments
argv = get_args()
make_mesh_function_path = argv[0] if len(argv) > 0 else None
csv_file_path = argv[1] if len(argv) > 1 else None
json_file_path = argv[2] if len(argv) > 2 else None
images_per_individual = int(argv[3]) if len(argv) > 3 else 1



def load_settings_from_json(json_path):
    with open(json_path, 'r') as f:
        settings = json.load(f)
    return settings


# Path to the JSON file containing the settings
settings = load_settings_from_json(json_file_path)

# Reading dataset options from JSON
use_suns = settings["Dataset Options"]["use_suns"]
use_cameras = settings["Dataset Options"]["use_cameras"]
use_3d_export = settings["Dataset Options"]["use_3d_export"]

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

# Image Randomization Controls
random_cam_rot = settings["Image Randomization Controls"]["RandomCamerasRotation"]
random_cam_dist = settings["Image Randomization Controls"]["RandomCamerasDistance"]
random_world_bg_color = settings["Image Randomization Controls"]["RandomWorldBackgroundColor"]
random_sun_intensity = settings["Image Randomization Controls"]["RandomSunIntensity"]

# Randomization Toggles
rand_toggles = settings["Randomization Toggles"]
random_world_bg_color_toggle = rand_toggles["random_world_bg_color"]
random_suns_hide_toggle = rand_toggles["random_suns_hide"]
random_suns_brightness_toggle = rand_toggles["random_suns_brightness"]
random_cameras_rotation_toggle = rand_toggles["random_cameras_rotation"]
random_cameras_distance_toggle = rand_toggles["random_cameras_distance"]

# Extract specific variables from Randomization Controls
# For example:
x_mu, x_sd = random_cam_rot["x_mu"], random_cam_rot["x_sd"]
y_mu, y_sd = random_cam_rot["y_mu"], random_cam_rot["y_sd"]


print(f"Dataset Options:")
print(f"  use_suns: {use_suns}")
print(f"  use_cameras: {use_cameras}")
print(f"  use_3d_export: {use_3d_export}\n")

print(f"World Background Controls:")
print(f"  wc_red: {wc_red}")
print(f"  wc_green: {wc_green}")
print(f"  wc_blue: {wc_blue}")
print(f"  wc_alpha: {wc_alpha}\n")

print(f"Background Controls:")
print(f"  background_plane_distance: {background_plane_distance}")
print(f"  bg_scale_x: {bg_scale_x}")
print(f"  bg_scale_y: {bg_scale_y}")
print(f"  bg_scale_z: {bg_scale_z}\n")

print(f"Lights:")
print(f"  sun_strength: {sun_strength}\n")

print(f"Camera Controls:")
print(f"  place_cameras_distance: {place_cameras_distance}")
print(f"  camera_width: {camera_width}")
print(f"  camera_height: {camera_height}")
print(f"  focal_length: {focal_length}")
print(f"  render_output_directory: {render_output_directory}")
print(f"  obj_export_directory: {obj_export_directory}")
print(f"  export_format: {export_format}")
print(f"  cameras_to_render: {cameras_to_render}\n")

print(f"Image Randomization Controls:")
print(f"  random_cam_rot: {random_cam_rot}")
print(f"  random_cam_dist: {random_cam_dist}")
print(f"  random_world_bg_color: {random_world_bg_color}")
print(f"  random_sun_intensity: {random_sun_intensity}\n")

print(f"Randomization Toggles:")
print(f"  random_world_bg_color_toggle: {random_world_bg_color_toggle}")
print(f"  random_suns_hide_toggle: {random_suns_hide_toggle}")
print(f"  random_suns_brightness_toggle: {random_suns_brightness_toggle}")
print(f"  random_cameras_rotation_toggle: {random_cameras_rotation_toggle}")
print(f"  random_cameras_distance_toggle: {random_cameras_distance_toggle}\n")

print(f"Randomization Controls - Camera Rotation:")
print(f"  x_mu: {x_mu}")
print(f"  x_sd: {x_sd}")
print(f"  y_mu: {y_mu}")
print(f"  y_sd: {y_sd}")



## Defining the scene
scene = bpy.data.scenes["Scene"]

## setting mesh function and trait data related properties
scene.csv_file_path = csv_file_path
scene.make_mesh_function_path = make_mesh_function_path

bpy.ops.object.import_csv()
tips = bpy.data.scenes['Scene']['tip_labels']
traits = bpy.data.scenes['Scene']['csv_data']
mesh_function = bpy.ops.object.execute_with_selected_csv_row

scene.render_output_directory = render_output_directory
scene.export_directory = obj_export_directory

for index, label in enumerate(tips):

    print("Starting New Individual!")

    scene = bpy.data.scenes["Scene"]

    for individual in range(images_per_individual):
        print("Starting New Image of Individual!")
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Delete all objects, including hidden ones and lights in all collections
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)
    
        index = str(index)
        scene.csv_label_props.csv_label_enum = index
        mesh_function()
        active_obj = bpy.context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        active_obj.select_set(True)

        ## set world color properties
        scene.world_background_controls.red = wc_red
        scene.world_background_controls.green = wc_green
        scene.world_background_controls.blue = wc_blue
        scene.world_background_controls.alpha = wc_alpha
        bpy.ops.scene.change_background_color()
    
        if settings["Background Controls"]["background_plane_image_path"] != "None":
            bpy.ops.traitblender.import_background_image(filepath=settings["Background Controls"]["background_plane_image_path"])
            bpy.ops.object.toggle_background_planes()
            ## set background plane/image properties
            scene.background_plane_distance = background_plane_distance
            scene.background_controls.plane_scale_x = bg_scale_x
            scene.background_controls.plane_scale_y = bg_scale_y
            scene.background_controls.plane_scale_z = bg_scale_z
            bpy.ops.object.scale_background_planes()
        
        if use_suns:
            bpy.ops.object.toggle_suns()
            ## set the strength of the suns
            scene.sun_strength = sun_strength
            bpy.ops.object.update_sun_strength()
        
        # Check and assign randomization properties based on JSON settings
        scene = bpy.data.scenes["Scene"]

        # Random World Background Color
        if random_world_bg_color_toggle:
            scene.red_mu = random_world_bg_color["red_mu"]
            scene.red_sd = random_world_bg_color["red_sd"]
            scene.green_mu = random_world_bg_color["green_mu"]
            scene.green_sd = random_world_bg_color["green_sd"]
            scene.blue_mu = random_world_bg_color["blue_mu"]
            scene.blue_sd = random_world_bg_color["blue_sd"]
            scene.alpha_mu = random_world_bg_color["alpha_mu"]
            scene.alpha_sd = random_world_bg_color["alpha_sd"]
            bpy.ops.object.randomize_world_background_color()

        # Random Suns Hide
        if random_suns_hide_toggle:
            bpy.ops.object.randomize_suns_hide()

        # Random Suns Brightness
        if random_suns_brightness_toggle:
            scene.sun_mu = random_sun_intensity["sun_mu"]
            scene.sun_sd = random_sun_intensity["sun_sd"]
            bpy.ops.object.randomize_suns_strength()


        if use_cameras:
            if render_output_directory == "":
                raise ValueError("You opted to export images, but didn't include a directory to export to!")
            bpy.ops.object.toggle_cameras()
            ## set the camera related properties
            scene.camera_controls.camera_width = camera_width
            scene.camera_controls.camera_height = camera_height
            scene.place_cameras_distance = place_cameras_distance
            scene.camera_controls.focal_length = focal_length

                    # Random Cameras Rotation
            if random_cameras_rotation_toggle:
                scene.x_mu = random_cam_rot["x_mu"]
                scene.x_sd = random_cam_rot["x_sd"]
                scene.y_mu = random_cam_rot["y_mu"]
                scene.y_sd = random_cam_rot["y_sd"]
                scene.z_mu = random_cam_rot["z_mu"]
                scene.z_sd = random_cam_rot["z_sd"]
                bpy.ops.object.randomize_camera_rotation()

                    # Random Cameras Distance
            if random_cameras_distance_toggle:
                scene.camera_distance_mu = random_cam_dist["camera_distance_mu"]
                scene.camera_distance_sd = random_cam_dist["camera_distance_sd"]
                bpy.ops.object.randomize_camera_distance()

            bpy.ops.object.render_all_cameras(camera_names=cameras_to_render)
        
    if use_3d_export:
        if obj_export_directory == "":
            raise ValueError("You opted to export the 3D object mesh, but didn't include a directory to export to!")

        ## set 3D object export properties
        scene.export_format = export_format
        bpy.ops.object.export_active_object()
    
print("Done!")
