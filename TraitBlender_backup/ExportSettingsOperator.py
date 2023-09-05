import bpy 
       
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
