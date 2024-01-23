import bpy
import json
import os

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

        # Create a dictionary to store the settings
        settings_dict = {}

        # World Background Controls
        wc_colors = [world_background_controls.red, world_background_controls.green, world_background_controls.blue, world_background_controls.alpha]
        settings_dict["World Background Controls"] = {"wc_colors": wc_colors}

        # Background Controls
        settings_dict["Background Controls"] = {
            "background_plane_image_path": image_filepath,
            "background_plane_distance": scene.background_plane_distance,
            "bg_scales": [background_controls.plane_scale_x, background_controls.plane_scale_y, background_controls.plane_scale_z]
        }

        # Lights
        settings_dict["Lights"] = {"sun_strength": scene.sun_strength}

        # Camera Controls
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

        settings_dict["Camera Controls"] = {
            "Cameras to Render": ",".join(camera_names_list),
            "place_cameras_distance": scene.place_cameras_distance,
            "camera_width_height": [camera_controls.camera_width, camera_controls.camera_height],
            "focal_length": camera_controls.focal_length,
            "render_output_directory": scene.render_output_directory
        }

        # Image Randomization Controls
        image_randomization_controls = {
            "RandomCamerasRotation": {
                "x_mu": scene.x_mu,
                "x_sd": scene.x_sd,
                "y_mu": scene.y_mu,
                "y_sd": scene.y_sd,
                "z_mu": scene.z_mu,
                "z_sd": scene.z_sd,
            },
            "RandomCamerasDistance": {
                "camera_distance_mu": scene.camera_distance_mu,
                "camera_distance_sd": scene.camera_distance_sd,
            },
            "RandomWorldBackgroundColor": {
                "red_mu": scene.red_mu,
                "red_sd": scene.red_sd,
                "green_mu": scene.green_mu,
                "green_sd": scene.green_sd,
                "blue_mu": scene.blue_mu,
                "blue_sd": scene.blue_sd,
                "alpha_mu": scene.alpha_mu,
                "alpha_sd": scene.alpha_sd,
            }
        }

        settings_dict["Image Randomization Controls"] = image_randomization_controls


        # New variables
        settings_dict["obj_export_directory"] = scene.export_directory
        settings_dict["export_format"] = scene.export_format

        # Adding new properties
        settings_dict["Dataset Options"] = {
            "use_suns": scene.use_suns,
            "use_cameras": scene.use_cameras,
            "use_3d_export": scene.use_3d_export
        }

        # Convert the dictionary to a JSON-formatted string
        settings_json = json.dumps(settings_dict, indent=4)

        # Print the JSON-formatted string to the console
        print(settings_json)

        # Save the settings to a JSON file in the selected directory
        export_path = os.path.join(scene.export_settings_directory, "traitblender_settings.json")
        with open(export_path, 'w') as json_file:
            json_file.write(settings_json)

        return {'FINISHED'}
