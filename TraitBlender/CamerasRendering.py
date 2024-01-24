import bpy
import math
from mathutils import Matrix, Vector
import os

###Functions
@bpy.app.handlers.persistent
def delete_cameras_on_mesh_deletion(dummy):
    """
    Persistent handler to delete cameras when the associated mesh is deleted.

    This function is intended to be used as a Blender application handler.
    It checks if the original mesh associated with each camera is deleted,
    and if so, deletes the camera.

    Parameters:
        dummy: A dummy parameter required for Blender application handlers.

    Note:
        This function is marked as persistent so it will survive file reloads.
    """
    
    # Get the names of the cameras to delete
    camera_names = ["camera.top", "camera.bottom", "camera.right", "camera.left", "camera.front", "camera.back"]

    # Delete the cameras if the original mesh has been deleted
    for name in camera_names:
        camera = bpy.data.objects.get(name)
        if camera is not None and bpy.data.objects.get(camera["original_mesh"]) is None:
            bpy.data.objects.remove(camera)



def update_camera_aspect_ratio(self, context):
    """
    Update the aspect ratio of cameras in the Blender scene based on user-defined settings.

    This function adjusts the sensor size and fit method of each camera in the scene to match
    the desired width and height set in the scene's camera_controls. It also updates the render
    resolution and pixel aspect ratio to match the new camera settings.

    Parameters:
        self: The current instance of the Blender layout.
        context: The current Blender context, containing references to the active object and scene.
    """
    
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


def update_camera_distance(self, context):
    """
    Update the distance of cameras from the active object in the Blender scene.

    This function adjusts the location of each camera in the scene to maintain a specified distance
    from the active object. The cameras are also oriented to point towards the active object.

    Parameters:
        self: The current instance of the Blender layout.
        context: The current Blender context, containing references to the active object and scene.
    """
    
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
            #direction_to_active_obj = active_obj.location - new_location
            #camera.rotation_mode = 'QUATERNION'
            #camera.rotation_quaternion = direction_to_active_obj.to_track_quat('-Z', 'Y')


def update_camera_focal_length(self, context):
    """
    Update the focal length of cameras in the Blender scene based on user-defined settings.

    This function adjusts the lens (focal length) of each camera in the scene to match
    the desired focal length set in the scene's camera_controls.

    Parameters:
        self: The current instance of the Blender layout.
        context: The current Blender context, containing references to the active object and scene.
    """
    
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


###Property Groups
class CameraControls(bpy.types.PropertyGroup):
    """
    Define the properties and methods for controlling camera settings in the Blender scene.

    This class contains various properties to control camera settings like dimensions,
    focal length, and which cameras to render. It also has methods to update these settings.
    """
    
    expanded: bpy.props.BoolProperty(
        name="Camera",
        description="Expand or collapse the camera controls",
        default=False
    )
    camera_width: bpy.props.IntProperty(
        name="Camera Width",
        default=1920,
        min=1,
        max=4096,
        update=update_camera_aspect_ratio,
        description="Width of the camera in pixels"
    )
    camera_height: bpy.props.IntProperty(
        name="Camera Height",
        default=1080,
        min=1,
        max=2160,
        update=update_camera_aspect_ratio,
        description="Height of the camera in pixels"
    )
    focal_length: bpy.props.FloatProperty(
        name="Focal Length",
        default=50.0,
        min=1.0,
        max=10000.0,
        soft_min=1.0,
        soft_max=10000.0,
        step=1,
        precision=2,
        update=update_camera_focal_length,
        description="Focal length of the camera lens"
    )
    render_camera_top: bpy.props.BoolProperty(name="Top", default=True, description="Render the top camera view")
    render_camera_bottom: bpy.props.BoolProperty(name="Bottom", default=True, description="Render the bottom camera view")
    render_camera_right: bpy.props.BoolProperty(name="Right", default=True, description="Render the right camera view")
    render_camera_left: bpy.props.BoolProperty(name="Left", default=True, description="Render the left camera view")
    render_camera_front: bpy.props.BoolProperty(name="Front", default=True, description="Render the front camera view")
    render_camera_back: bpy.props.BoolProperty(name="Back", default=True, description="Render the back camera view")

###Operators
class HideCamerasOperator(bpy.types.Operator):
    """
    Define the operator to hide or unhide cameras in the Blender scene.

    This class contains the execute method that toggles the visibility of predefined cameras.
    """
    
    bl_idname = "object.hide_cameras"
    bl_label = "Hide Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Toggle the visibility of cameras in the Blender scene.

        This function checks the existing cameras in the scene and either hides or shows them
        based on their current visibility status.

        Parameters:
            context: The current Blender context, containing references to the active object and scene.

        Returns:
            {'FINISHED'} if successful, otherwise raises an error.
        """
        
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

class RenderAllCamerasOperator(bpy.types.Operator):
    """
    Define the operator for rendering scenes from multiple camera angles.

    This class contains the execute method to render the scene from the perspective of 
    different cameras specified by their names and save the rendered images.
    """
    
    bl_idname = "object.render_all_cameras"
    bl_label = "Render All Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    camera_names: bpy.props.StringProperty(
        name="Camera Names",
        description="Comma-separated names of the cameras to render",
        default="camera.top,camera.bottom,camera.right,camera.left,camera.front,camera.back"
    )

    def execute(self, context):
        """
        Render the scene from the perspective of different cameras and save the images.

        This function loops through the specified camera names, sets each one as the active
        camera, and renders the scene, saving the resulting image to the specified directory.

        Parameters:
            context: The current Blender context, containing references to the active object and scene.

        Returns:
            {'FINISHED'} if successful, otherwise raises an error.
        """
        
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

                # Set the camera as the active one for rendering
                bpy.context.scene.camera = camera
                
                # Perform the rendering
                bpy.ops.render.render(write_still=True)

        # Restore the original active camera
        bpy.context.scene.camera = original_camera

        # Report that all images have been rendered
        self.report({'INFO'}, "All images have been rendered and saved!")

        return {'FINISHED'}


class SelectRenderDirectoryOperator(bpy.types.Operator):
    """
    Operator for selecting the directory where rendered images will be saved.

    Allows the user to select a directory for storing rendered images through a file selector.
    """
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
        """Sets the selected directory as the output directory for rendered images."""
        context.scene.render_output_directory = self.directory
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the file selector."""
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SetCameraViewOperator(bpy.types.Operator):
    """
    Operator for setting the camera view based on a specified angle.

    Allows the user to set the active camera and view perspective to a specified angle,
    and also hides all other background planes and sun objects that do not correspond to the new camera angle.
    """
    bl_idname = "object.set_camera_view"
    bl_label = "Set Camera View"
    bl_options = {'REGISTER', 'UNDO'}

    angle: bpy.props.StringProperty(name="Angle")

    def execute(self, context):
        """Set the camera view and hide unrelated background planes and sun objects."""
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
            #corresponding_sun_name = f"sun.{self.angle.lower()}"
            #for obj in bpy.data.objects:
            #    if "sun." in obj.name:
            #        obj.hide_viewport = obj.name != corresponding_sun_name
        else:
            self.report({'ERROR'}, f"No camera found with name {camera_name}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def get_opposite_angle(self):
        """
        Get the opposite viewing angle of the current viewing angle.

        Returns:
            str: The opposite angle.
        """
        opposites = {
            "Front": "Back",
            "Back": "Front",
            "Left": "Right",
            "Right": "Left",
            "Top": "Bottom",
            "Bottom": "Top",
        }
        return opposites.get(self.angle, "")


class ToggleCamerasOperator(bpy.types.Operator):
    """
    This operator toggles the visibility and existence of cameras in the Blender scene.
    The cameras are positioned at a specified distance from an active object and are
    oriented to face towards the active object. If the cameras already exist, they are removed.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        bl_options (set): Operator options.
        distance (FloatProperty): The distance from the active object at which the cameras are placed.
    """
    bl_idname = "object.toggle_cameras"
    bl_label = "Toggle Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=10.0)

    def execute(self, context):
        """
        Executes the operator, either creating or removing cameras based on their existence.
        
        Parameters:
            context: Blender's context object
        
        Returns:
            dict: A dictionary indicating the execution status.
        """
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
        """
        Invokes the operator and sets the distance attribute from the scene.
        
        Parameters:
            context: Blender's context object
            event: Blender's event object
        
        Returns:
            dict: A dictionary indicating the execution status.
        """
        self.distance = context.scene.place_cameras_distance
        return self.execute(context)

class RenderHiddenObjectsOperator(bpy.types.Operator):
    """Allows enabling/disabling of hidden objects appearing in the render (including light sources)"""
    bl_idname = "object.render_hidden_objects"
    bl_label = "Render Hidden Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        old_object = context.view_layer.objects.active

        # Check the custom property and update hide_render accordingly
        if not scene.render_hidden_objects:
            for obj in bpy.data.objects:
                if obj.hide_viewport:
                    obj.hide_render = True
        else:
            for obj in bpy.data.objects:
                obj.hide_render = False

        context.view_layer.objects.active = old_object
        context.view_layer.update()

        self.report({'INFO'}, "Render visibility updated")
        return {'FINISHED'}


def update_render_hidden_objects(self, context):
    # Trigger the operator when the checkbox value changes
    bpy.ops.object.render_hidden_objects()






    





    








