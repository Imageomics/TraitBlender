
import bpy


make_mesh_function_path = ""
csv_file_path = ""

wc_red, wc_green, wc_blue, wc_alpha = [1.0, 1.0, 1.0, 1.0]
background_plane_image_path = ""
background_plane_distance = 10.00
bg_scale_x, bg_scale_y, bg_scale_z = [.5, 1.0, 1.0]
sun_strength = 1.0
place_cameras_distance = 10.00
camera_width, camera_height = [1080, 1080]
focal_length = 50.00
render_cameras = "camera.top,camera.bottom,camera.right,camera.left,camera.front,camera.back"
render_output_directory = ""

obj_export_format = ".obj"
obj_export_directory = ""



## Defining the scene
scene = bpy.data.scenes["Scene"]

## setting mesh function and trait data related properties
scene.csv_file_path = csv_file_path
scene.make_mesh_function_path = make_mesh_function_path

## set world color properties
scene.world_background_controls.red = wc_red
scene.world_background_controls.green = wc_green
scene.world_background_controls.blue = wc_blue
scene.world_background_controls.alpha = wc_alpha

## set background plane/image properties
if background_plane_image_path:
    bpy.ops.traitblender.import_background_image(filepath=background_plane_image_path)
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
scene.export_format = obj_export_format
scene.export_directory = obj_export_directory
