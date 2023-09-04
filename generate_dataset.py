import bpy
import types
import importlib
import csv
import inspect
import warnings
import os
import argparse

# Argument parsing with default values
parser = argparse.ArgumentParser(description='Generate dataset using Blender.')
parser.add_argument('--make_mesh_function_path', default="D://datapalooza/make_cube_cylinder.py", help='Path to the script containing the function.')
parser.add_argument('--traits_csv_path', default="C://Users/caleb/Downloads/squares/square_data_short.csv", help='Path to the traits CSV.')
parser.add_argument('--bg_path', default=None, help='Path to the background image.')
parser.add_argument('--world_bg_color', nargs=4, type=float, default=[1.0, 1.0, 1.0, 1.0], help='World background color in RGBA.')
parser.add_argument('--bg_distance', type=float, default=10.0, help='Background distance.')
parser.add_argument('--bg_x_scale', type=float, default=15, help='Background X scale.')
parser.add_argument('--bg_y_scale', type=float, default=15, help='Background Y scale.')
parser.add_argument('--bg_z_scale', type=float, default=15, help='Background Z scale.')
parser.add_argument('--suns_distance', type=float, default=10, help='Distance of the suns.')
parser.add_argument('--suns_strength', type=float, default=1, help='Strength of the suns.')
parser.add_argument('--cameras_distance', type=float, default=10, help='Distance of the cameras.')
parser.add_argument('--camera_pixel_width', type=int, default=1080, help='Camera pixel width.')
parser.add_argument('--camera_pixel_height', type=int, default=1080, help='Camera pixel height.')
parser.add_argument('--camera_focal_length', type=float, default=700, help='Camera focal length.')
parser.add_argument('--render_directory', default="C://Users/caleb/Downloads/squares/short_imgs2", help='Directory to save the renders.')
parser.add_argument('--camera_rendering_views', default="camera.front,camera.right", help='Camera rendering views.')

args = parser.parse_args()

# Use the arguments
make_mesh_function_path = args.make_mesh_function_path
traits_csv_path = args.traits_csv_path
background_path = args.bg_path  # Variable name unchanged
world_background_color = args.world_bg_color
background_distance = args.bg_distance  # Variable name unchanged
background_x_scale = args.bg_x_scale  # Variable name unchanged
background_y_scale = args.bg_y_scale  # Variable name unchanged
background_z_scale = args.bg_z_scale  # Variable name unchanged
suns_distance = args.suns_distance
suns_strength = args.suns_strength
cameras_distance = args.cameras_distance
camera_pixel_width = args.camera_pixel_width
camera_pixel_height = args.camera_pixel_height
camera_focal_length = args.camera_focal_length
render_directory = args.render_directory
camera_rendering_views = args.camera_rendering_views

print("Current Working Directory:", os.getcwd())
with open("D://datapalooza/traitblender_gui.py", "r") as file:
    exec(file.read())


# Read the script content
with open(make_mesh_function_path, 'r') as f:
    script_content = f.read()

# Extract import statements
import_statements = [line.strip() for line in script_content.split('\n') if line.startswith('import') or line.startswith('from')]

# Create an empty dictionary to store local variables
local_variable_dict = {}

# Create a dictionary to store global variables (including imported modules)
global_variable_dict = {}

# Dynamically import modules
for statement in import_statements:
    exec(statement, global_variable_dict)

# Execute the script content
exec(script_content, global_variable_dict, local_variable_dict)

# Find the first function in the local variables and rename it to 'make_mesh'
for func_name, func_object in local_variable_dict.items():
    if isinstance(func_object, types.FunctionType):
        make_mesh = func_object
        break  # Stop after finding the first function

parameter_names = list(inspect.signature(make_mesh).parameters.keys())
print("Parameter names:", parameter_names)

# Check if exactly one of the parameter names is "tip", "name", or "label" (case-insensitive)
matching_params = [param for param in parameter_names if param.lower() in ["tip", "name", "label"]]

if len(matching_params) != 1:
    raise ValueError('No more or less than one mesh-generating function parameter can be "tip", "name", or "label"')

print("Parameter names:", parameter_names)


def import_csv(csv_file_path):
    # Initialize an empty list to store the rows
    csv_data = []
    
    # Initialize an empty list to store the column names
    column_names = []
    
    # Read the CSV file
    with open(csv_file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        
        # Store the column names
        column_names = csvreader.fieldnames

        # Check if the first column name is one of the allowed names
        first_column_name = column_names[0].lower()  # Convert to lowercase for case-insensitive comparison
        allowed_first_column_names = ["tip", "name", "label"]
        
        if first_column_name not in allowed_first_column_names:
            raise ValueError('Column 1 Must be titled "tip", "name", or "label"!')
        
        # Loop through each row and append it to the list
        for row in csvreader:
            # Convert the types of the values in the row
            for key, value in row.items():
                try:
                    row[key] = float(value)  # Try converting to float
                except ValueError:
                    try:
                        row[key] = int(value)  # Try converting to int
                    except ValueError:
                        if value.lower() == 'true':
                            row[key] = True  # Convert to boolean True
                        elif value.lower() == 'false':
                            row[key] = False  # Convert to boolean False
                        else:
                            row[key] = value  # Keep as string
            
            csv_data.append(row)
            
    return csv_data, column_names

# Example usage
try:
    imported_data, trait_names = import_csv(traits_csv_path)
    print("Trait Names:", trait_names)
except ValueError as e:
    print(e)

    
    
# Remove the 'tip', 'name', or 'label' column from trait_names
filtered_trait_names = [name for name in trait_names if name.lower() not in ["tip", "name", "label"]]

# Remove the 'tip', 'name', or 'label' parameter from parameter_names
filtered_parameter_names = [name for name in parameter_names if name.lower() not in ["tip", "name", "label"]]

# Check if the filtered_trait_names are a subset of filtered_parameter_names
if not set(filtered_trait_names).issubset(set(filtered_parameter_names)):
    raise ValueError("The columns of the imported data must be a subset of the make_mesh parameters.")

# If the check passes, you can proceed with the rest of your code
# Find the name of the label/tip/name parameter in make_mesh
mesh_label_param = next(param for param in parameter_names if param.lower() in ["tip", "name", "label"])

# Find the name of the label/tip/name column in the dataset
dataset_label_column = next(col for col in trait_names if col.lower() in ["tip", "name", "label"])



def update_camera_distance(self, context):
    # Get the active object
    active_obj = context.active_object
    if active_obj is None:
        return

    # Get the names of the cameras to update
    camera_names = ["camera.top", "camera.bottom", "camera.right", "camera.left", "camera.front", "camera.back"]

    # Update the camera locations
    for name in camera_names:
        camera = bpy.data.objects.get(name)
        if camera is not None:
            current_direction = (active_obj.location - camera.location).normalized()
            new_location = active_obj.location - current_direction * self.place_cameras_distance
            camera.location = new_location

            # Point the camera towards the active object
            direction_to_active_obj = active_obj.location - new_location
            camera.rotation_mode = 'QUATERNION'
            camera.rotation_quaternion = direction_to_active_obj.to_track_quat('-Z', 'Y')


# Loop through each row in the imported data
for row in imported_data:
    
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    # Initialize an empty dictionary to store the arguments for make_mesh
    make_mesh_args = {}
    
    # Initialize a list to store the names of missing parameters
    missing_params = []
    
    # Loop through each parameter name for make_mesh
    for param in parameter_names:
        if param.lower() in ["tip", "name", "label"]:
            make_mesh_args[param] = row[dataset_label_column]
        elif param in row:
            make_mesh_args[param] = row[param]
        elif param.lower() in [col.lower() for col in row]:
            original_col_name = next(col for col in row if col.lower() == param.lower())
            make_mesh_args[param] = row[original_col_name]
        else:
            missing_params.append(param)

    if missing_params:
        warnings.warn(f"The following parameters are in the mesh-generating function but not in the dataset, so their defaults are being used: {', '.join(missing_params)}")

    # Run the make_mesh function with the arguments
    make_mesh(**make_mesh_args)

    # Set the active object to the one with the name from the "tip", "name", or "label" columns
    active_obj_name = make_mesh_args.get('tip') or make_mesh_args.get('name') or make_mesh_args.get('label')
    bpy.context.view_layer.objects.active = bpy.data.objects[active_obj_name]

    # Check if background_path exists and import the background
    if background_path:
        bpy.ops.traitblender.import_background_image(filepath=background_path)
        bpy.ops.mesh.create_background_image()

    bpy.ops.object.toggle_background_planes()
    
    if 'world_background_color' in locals() and len(world_background_color) == 4:
        if all(isinstance(x, (int, float)) for x in world_background_color):
            red, green, blue, alpha = world_background_color
            bpy.data.scenes["Scene"].world_background_controls.red = red
            bpy.data.scenes["Scene"].world_background_controls.green = green
            bpy.data.scenes["Scene"].world_background_controls.blue = blue
            bpy.data.scenes["Scene"].world_background_controls.alpha = alpha
            bpy.ops.scene.change_background_color()
        else:
            raise ValueError("All elements in world_background_color must be numbers.")
    else:
        raise ValueError("world_background_color either does not exist or is not of length 4.")


    # Update the background plane distance
    bpy.ops.object.call_update_background_plane_distance()

    # Update the background scale values
    bpy.context.scene.background_controls.plane_scale_x = background_x_scale
    bpy.context.scene.background_controls.plane_scale_y = background_y_scale
    bpy.context.scene.background_controls.plane_scale_z = background_z_scale

    # Explicitly call the operator to scale the background planes
    bpy.ops.object.scale_background_planes()

    bpy.ops.object.toggle_suns(distance=suns_distance)
    
    bpy.context.scene.sun_strength = suns_strength  # Assuming sun_strength is defined at the top of your script
    bpy.ops.object.update_sun_strength()
    
    bpy.data.objects[active_obj_name].select_set(True)   
    bpy.ops.object.toggle_cameras()
    
    # Update the camera distance
    bpy.data.scenes["Scene"].place_cameras_distance = cameras_distance  # Assuming cameras_distance is defined at the top of your script

    # Call the update function
    update_camera_distance(bpy.context.scene, bpy.context)

    # Update the camera pixel and focal lengths
    bpy.data.scenes["Scene"].camera_controls.camera_width = camera_pixel_width
    bpy.data.scenes["Scene"].camera_controls.camera_width = camera_pixel_height
    bpy.data.scenes["Scene"].camera_controls.focal_length = camera_focal_length
    
    # Set the rendering directory
    bpy.data.scenes["Scene"].render_output_directory = render_directory + "/" + active_obj_name
    bpy.ops.object.render_all_cameras(camera_names=camera_rendering_views)

    