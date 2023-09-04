import bpy
import math
from mathutils import Matrix, Vector
import os

class ToggleCamerasOperator(bpy.types.Operator):
    bl_idname = "object.toggle_cameras"
    bl_label = "Toggle Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=10.0)

    def execute(self, context):
        # Get the active object
        active_obj = context.active_object
        if active_obj is None:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        # Store the original active object and its selection state
        original_active_obj = context.active_object
        original_active_obj_selected = original_active_obj.select_get()

        # Calculate the camera locations and names
        locations_and_names = [
            ((0, 0, self.distance), "camera.top"),  # Top
            ((0, 0, -self.distance), "camera.bottom"),  # Bottom
            ((self.distance, 0, 0), "camera.right"),  # Right
            ((-self.distance, 0, 0), "camera.left"),  # Left
            ((0, self.distance, 0), "camera.back"),  # Front
            ((0, -self.distance, 0), "camera.front"),  # Back
        ]

        # Check if the cameras already exist
        cameras_exist = all(bpy.data.objects.get(name) is not None for _, name in locations_and_names)

        if cameras_exist:
            # Remove the cameras
            for _, name in locations_and_names:
                camera = bpy.data.objects.get(name)
                if camera is not None:
                    bpy.data.objects.remove(camera)
        else:
            # Reset the camera properties to default values
            context.scene.place_cameras_distance = 10.0

            # Create the cameras
            for location, name in locations_and_names:
                # Add the location of the active object to the location of the camera
                location = active_obj.location + Vector(location)
                bpy.ops.object.camera_add(location=location)
                camera = context.active_object

                # Set the camera name
                camera.name = name

                # Point the camera towards the active object
                direction = active_obj.location - camera.location
                camera.rotation_mode = 'QUATERNION'
                camera.rotation_quaternion = direction.to_track_quat('-Z', 'Y')

                # Store a reference to the original mesh in the camera
                camera["original_mesh"] = active_obj.name

                # Store the original position of the camera
                camera["original_position"] = camera.location.copy()

                # Store the original direction of the camera
                camera["original_direction"] = direction.normalized()

                # Store the original rotation of the camera
                camera["original_rotation"] = camera.rotation_quaternion.copy()

                # Deselect the new camera
                camera.select_set(False)

        # Restore the original active object and its selection state
        context.view_layer.objects.active = original_active_obj
        original_active_obj.select_set(original_active_obj_selected)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.distance = context.scene.place_cameras_distance
        return self.execute(context)
    
class HideCamerasOperator(bpy.types.Operator):
    bl_idname = "object.hide_cameras"
    bl_label = "Hide Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the names of the cameras to hide/unhide
        camera_names = ["camera.top", "camera.bottom", "camera.right", "camera.left", "camera.front", "camera.back"]

        # Check if the cameras already exist and are visible
        cameras_exist = all(bpy.data.objects.get(name) is not None for name in camera_names)
        cameras_visible = all(not bpy.data.objects[name].hide_viewport for name in camera_names if bpy.data.objects.get(name) is not None)

        if cameras_exist and cameras_visible:
            # Hide the cameras
            for name in camera_names:
                camera = bpy.data.objects.get(name)
                if camera is not None:
                    camera.hide_viewport = True
            self.bl_label = "Show Cameras"
        elif cameras_exist and not cameras_visible:
            # Unhide the cameras
            for name in camera_names:
                camera = bpy.data.objects.get(name)
                if camera is not None:
                    camera.hide_viewport = False
            self.bl_label = "Hide Cameras"

        return {'FINISHED'}


def update_camera_aspect_ratio(self, context):
    # Get the scene
    scene = context.scene

    # List of camera names to update
    camera_names = ["camera.top", "camera.back", "camera.left", "camera.right", "camera.front", "camera.bottom"]

    # Desired width and height in pixels
    desired_width = scene.camera_controls.camera_width
    desired_height = scene.camera_controls.camera_height

    # Calculate the aspect ratio
    aspect_ratio = desired_width / desired_height

    # Loop through the camera names and update each one
    for name in camera_names:
        camera_obj = bpy.data.objects.get(name)
        if camera_obj and camera_obj.type == 'CAMERA':
            camera = camera_obj.data
            camera.sensor_fit = 'HORIZONTAL' if desired_width > desired_height else 'VERTICAL'
            camera.sensor_width = desired_width if desired_width > desired_height else desired_height
            camera.sensor_height = desired_height if desired_width > desired_height else desired_width

    # Set the render resolution to the desired size in pixels
    scene.render.resolution_x = desired_width
    scene.render.resolution_y = desired_height

    # Set the pixel aspect ratio to 1:1 to ensure the correct aspect ratio
    scene.render.pixel_aspect_x = 1
    scene.render.pixel_aspect_y = 1

def update_camera_focal_length(self, context):
    # Get the scene
    scene = context.scene

    # List of camera names to update
    camera_names = ["camera.top", "camera.back", "camera.left", "camera.right", "camera.front", "camera.bottom"]

    # Loop through the camera names and update each one
    for name in camera_names:
        camera_obj = bpy.data.objects.get(name)
        if camera_obj and camera_obj.type == 'CAMERA':
            camera = camera_obj.data
            camera.lens = scene.camera_controls.focal_length 

class CameraControls(bpy.types.PropertyGroup):
    expanded: bpy.props.BoolProperty(
        name="Camera",
        description="Expand or collapse the camera controls",
        default=False
    )
    camera_width: bpy.props.IntProperty(name="Camera Width", default=1920, min=1, max=4096, update=update_camera_aspect_ratio)
    camera_height: bpy.props.IntProperty(name="Camera Height", default=1080, min=1, max=2160, update=update_camera_aspect_ratio)
    focal_length: bpy.props.FloatProperty(
        name="Focal Length",
        default=50.0,
        min=1.0,
        max=10000.0,
        soft_min=1.0,
        soft_max=10000.0,
        step=1,
        precision=2,
        update=update_camera_focal_length
    )
    # New properties for selecting cameras to render
    render_camera_top: bpy.props.BoolProperty(name="Top", default=True)
    render_camera_bottom: bpy.props.BoolProperty(name="Bottom", default=True)
    render_camera_right: bpy.props.BoolProperty(name="Right", default=True)
    render_camera_left: bpy.props.BoolProperty(name="Left", default=True)
    render_camera_front: bpy.props.BoolProperty(name="Front", default=True)
    render_camera_back: bpy.props.BoolProperty(name="Back", default=True)
    
class RenderAllCamerasOperator(bpy.types.Operator):
    bl_idname = "object.render_all_cameras"
    bl_label = "Render All Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    camera_names: bpy.props.StringProperty(
        name="Camera Names",
        description="Comma-separated names of the cameras to render",
        default="camera.top,camera.bottom,camera.right,camera.left,camera.front,camera.back"
    )

    def execute(self, context):
        # Ensure the render directory is set
        if not context.scene.render_output_directory:
            self.report({'ERROR'}, "Please select a render directory first.")
            return {'CANCELLED'}

        # Split the camera names string into a list
        camera_names_list = self.camera_names.split(',')

        # Store the current active camera
        original_camera = bpy.context.scene.camera

        for name in camera_names_list:
            camera = bpy.data.objects.get(name)
            if camera:
                # Extract the angle from the camera name
                angle = name.split('.')[-1].capitalize()

                # Set the camera view using the SetCameraViewOperator
                bpy.ops.object.set_camera_view(angle=angle)

                # Set the render path with the camera name
                active_object_name = bpy.context.active_object.name if bpy.context.active_object else "NoActiveObject"
                bpy.context.scene.render.filepath = os.path.join(context.scene.render_output_directory, f"{active_object_name}_{angle}.png")


                bpy.context.scene.camera = camera
                bpy.ops.render.render(write_still=True)

        # Restore the original active camera
        bpy.context.scene.camera = original_camera

        # Report that all images have been rendered
        self.report({'INFO'}, "All images have been rendered and saved!")

        return {'FINISHED'}


class SetCameraViewOperator(bpy.types.Operator):
    bl_idname = "object.set_camera_view"
    bl_label = "Set Camera View"
    bl_options = {'REGISTER', 'UNDO'}

    angle: bpy.props.StringProperty(name="Angle")

    def execute(self, context):
        camera_name = f"camera.{self.angle.lower()}"
        camera_obj = bpy.data.objects.get(camera_name)
        if camera_obj and camera_obj.type == 'CAMERA':
            # Set the active camera
            context.scene.camera = camera_obj
            # Change the view to the camera view
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.spaces[0].region_3d.view_perspective = 'CAMERA'

            # Hide all backgrounds except the one opposite the camera
            opposite_background_name = f"background_plane.{self.get_opposite_angle().lower()}"
            for obj in bpy.data.objects:
                if "background_plane." in obj.name:
                    obj.hide_viewport = obj.name != opposite_background_name

            # Hide all suns except the one corresponding to the camera
            corresponding_sun_name = f"sun.{self.angle.lower()}"
            for obj in bpy.data.objects:
                if "sun." in obj.name:
                    obj.hide_viewport = obj.name != corresponding_sun_name
        else:
            self.report({'ERROR'}, f"No camera found with name {camera_name}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def get_opposite_angle(self):
        opposites = {
            "Front": "Back",
            "Back": "Front",
            "Left": "Right",
            "Right": "Left",
            "Top": "Bottom",
            "Bottom": "Top",
        }
        return opposites.get(self.angle, "")




    
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




@bpy.app.handlers.persistent
def delete_cameras_on_mesh_deletion(dummy):
    # Get the names of the cameras to delete
    camera_names = ["camera.top", "camera.bottom", "camera.right", "camera.left", "camera.front", "camera.back"]

    # Delete the cameras if the original mesh has been deleted
    for name in camera_names:
        camera = bpy.data.objects.get(name)
        if camera is not None and bpy.data.objects.get(camera["original_mesh"]) is None:
            bpy.data.objects.remove(camera)



class SelectRenderDirectoryOperator(bpy.types.Operator):
    bl_idname = "object.select_render_directory"
    bl_label = "Select Render Directory"
    bl_options = {'REGISTER', 'INTERNAL'}

    directory: bpy.props.StringProperty(
        name="Output Directory",
        description="Choose a directory to save the renders",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    def execute(self, context):
        context.scene.render_output_directory = self.directory
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
