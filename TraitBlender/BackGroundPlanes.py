import bpy
import os
import math
from math import radians
from mathutils import Matrix, Vector

###Functions
def mesh_menu_func(self, context):
    """
    Function to add the CreateBackgroundImageMeshOperator to the Blender mesh menu.
    
    This function extends the mesh menu in Blender's UI to include an option for
    creating a background image mesh. It adds an icon and the operator to the layout.
    
    Parameters:
        self: The current instance of the Blender layout.
        context: The current Blender context, containing references to the active object and scene.
    """
    
    self.layout.operator(CreateBackgroundImageMeshOperator.bl_idname, icon='MESH_PLANE')

def update_background_plane_distance(self, context):
    """
    Update the distance of background planes relative to the active object.
    
    This function adjusts the location of background planes to maintain a specified
    distance from the active object in the Blender scene. It also rotates the planes
    to face the active object.
    
    Parameters:
        self: The object that owns the function, typically an operator or a property group.
        context: The current Blender context, which contains references to the active object and scene.
        
    Returns:
        None
    """
    # Get the active object
    active_obj = context.active_object
    if active_obj is None:
        return

    # Get the names of the background planes to update
    plane_names = ["background_plane.top", "background_plane.bottom", "background_plane.right", "background_plane.left", "background_plane.front", "background_plane.back"]

    # Update the background plane locations
    for name in plane_names:
        plane = bpy.data.objects.get(name)
        if plane is not None:
            current_direction = (active_obj.location - plane.location).normalized()
            new_location = active_obj.location - current_direction * self.background_plane_distance
            plane.location = new_location

            # Point the plane towards the active object
            direction_to_active_obj = active_obj.location - new_location
            plane.rotation_mode = 'QUATERNION'
            plane.rotation_quaternion = direction_to_active_obj.to_track_quat('Z', 'Y')


###Property Groups
class BackgroundControls(bpy.types.PropertyGroup):
    """
    Blender Property Group for controlling background plane settings.
    
    This class defines properties related to the positioning and scaling 
    of background planes in Blender. It provides controls for expanding or 
    collapsing the background settings UI, setting the distance of the 
    background planes from the active object, and scaling the background 
    planes along the X, Y, and Z axes.
    
    Attributes:
        expanded (BoolProperty): Expand or collapse the background controls UI.
        plane_distance (FloatProperty): Distance of the background planes from the active object.
        plane_scale_x (FloatProperty): Scale of the background planes on the X axis.
        plane_scale_y (FloatProperty): Scale of the background planes on the Y axis.
        plane_scale_z (FloatProperty): Scale of the background planes on the Z axis.
    """
    expanded: bpy.props.BoolProperty(
        name="Background",
        description="Expand or collapse the background controls",
        default=False
    )
    plane_distance: bpy.props.FloatProperty(
        name="Plane Distance",
        default=10.0,
        description="Distance of the background planes from the active object"
    )
    plane_scale_x: bpy.props.FloatProperty(
        name="Scale X",
        default=1.0,
        description="Scale of the background planes on the X axis"
    )
    plane_scale_y: bpy.props.FloatProperty(
        name="Scale Y",
        default=1.0,
        description="Scale of the background planes on the Y axis"
    )
    plane_scale_z: bpy.props.FloatProperty(
        name="Scale Z",
        default=1.0,
        description="Scale of the background planes on the Z axis"
    )

    
###Operators
class CallUpdateBackgroundPlaneDistanceOperator(bpy.types.Operator):
    """
    Operator to trigger the update of background plane distances.
    
    This class defines an operator that, when executed, calls the 
    'update_background_plane_distance' function to adjust the location 
    and orientation of background planes based on the active object in Blender.
    
    Attributes:
        bl_idname (str): Blender identifier for the operator.
        bl_label (str): Label displayed in the Blender UI.
        bl_options (set): Operator options defining its behavior in Blender.
    """
    
    bl_idname = "object.call_update_background_plane_distance"
    bl_label = "Call Update Background Plane Distance"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Execute the operator.
        
        This method is called when the operator is run. It triggers the 
        'update_background_plane_distance' function to adjust background 
        plane locations.
        
        Parameters:
            context: The current Blender context, which contains references to the active object and scene.
        
        Returns:
            dict: A dictionary indicating the operator's status. In this case, always returns {'FINISHED'}.
        """
        # Here, 'self' refers to the operator object, which doesn't have a 'background_plane_distance' attribute.
        # So, we pass 'context.scene' instead, which should have the 'background_plane_distance' attribute.
        update_background_plane_distance(context.scene, context)
        return {'FINISHED'}


class CreateBackgroundImageMeshOperator(bpy.types.Operator):
    """
    Operator to create a background image mesh.
    
    This class defines an operator that, when executed, creates a plane mesh
    and assigns a specified background image as its texture. The plane's position
    and orientation are also adjusted based on the active object in the Blender scene.
    
    Attributes:
        bl_idname (str): Blender identifier for the operator.
        bl_label (str): Label displayed in the Blender UI.
        bl_options (set): Operator options defining its behavior in Blender.
    """
    
    bl_idname = "mesh.create_background_image"
    bl_label = "Background Image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Execute the operator.
        
        This method is called when the operator is run. It creates a plane and
        assigns a specified background image to it. The plane's position and orientation
        are adjusted based on the active object in the Blender scene.
        
        Parameters:
            context: The current Blender context, containing references to the active object and scene.
        
        Returns:
            dict: A dictionary indicating the operator's status. Returns {'FINISHED'} if successful, or {'CANCELLED'} if not.
        """
        # Check if the background image reference exists
        image_name = context.scene.background_image_reference
        if not image_name:
            self.report({'ERROR'}, "No background image reference found. Please import a background image first.")
            return {'CANCELLED'}
        
        image = bpy.data.images.get(image_name)
        if not image:
            self.report({'ERROR'}, "Background image not found in the data. Please re-import the image.")
            return {'CANCELLED'}
        
        # Create a plane and assign the image as its texture
        bpy.ops.mesh.primitive_plane_add(size=1)
        plane = context.active_object
        mat = bpy.data.materials.new(name="BackgroundImageMaterial")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex_image.image = image
        mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
        plane.data.materials.append(mat)

        # Adjust the position of the plane based on the background_plane_distance
        active_obj = context.active_object
        direction_to_plane = (plane.location - active_obj.location).normalized()
        plane.location = active_obj.location + direction_to_plane * context.scene.background_plane_distance

        # Point the plane towards the active object
        direction_to_active_obj = active_obj.location - plane.location
        plane.rotation_mode = 'QUATERNION'
        plane.rotation_quaternion = direction_to_active_obj.to_track_quat('Z', 'Y')

        return {'FINISHED'}

    
class HideBackgroundPlanesOperator(bpy.types.Operator):
    """
    Operator to toggle the visibility of background planes.
    
    This class defines an operator that, when executed, either hides or shows
    the background planes in the Blender scene depending on their current state.
    
    Attributes:
        bl_idname (str): Blender identifier for the operator.
        bl_label (str): Label displayed in the Blender UI.
        bl_options (set): Operator options defining its behavior in Blender.
    """
    
    bl_idname = "object.hide_background_planes"
    bl_label = "Hide Background"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Execute the operator.
        
        This method is called when the operator is run. It toggles the visibility
        of predefined background planes in the Blender scene.
        
        Parameters:
            context: The current Blender context, containing references to the active object and scene.
        
        Returns:
            dict: A dictionary indicating the operator's status. Always returns {'FINISHED'}.
        """
        # Get the names of the background planes to hide/unhide
        plane_names = ["background_plane.top", "background_plane.bottom", "background_plane.right", 
                       "background_plane.left", "background_plane.back", "background_plane.front"]

        # Check if the planes already exist and are visible
        planes_exist = all(bpy.data.objects.get(name) is not None for name in plane_names)
        planes_visible = all(not bpy.data.objects[name].hide_viewport for name in plane_names if bpy.data.objects.get(name) is not None)

        if planes_exist and planes_visible:
            # Hide the planes
            for name in plane_names:
                plane = bpy.data.objects.get(name)
                if plane is not None:
                    plane.hide_viewport = True
            self.bl_label = "Show Background"
        elif planes_exist and not planes_visible:
            # Unhide the planes
            for name in plane_names:
                plane = bpy.data.objects.get(name)
                if plane is not None:
                    plane.hide_viewport = False
            self.bl_label = "Hide Background"

        return {'FINISHED'}

    
class ImportBackgroundImageOperator(bpy.types.Operator):
    """
    Operator to import a background image into the Blender scene.
    
    This class defines an operator that, when executed, imports a background 
    image from a file and stores its reference in the scene properties for 
    future use.
    
    Attributes:
        bl_idname (str): Blender identifier for the operator.
        bl_label (str): Label displayed in the Blender UI.
        bl_options (set): Operator options defining its behavior in Blender.
        filepath (StringProperty): Filepath for the image to be imported.
    """
    
    bl_idname = "traitblender.import_background_image"
    bl_label = "Import Background Image"
    bl_options = {'REGISTER', 'INTERNAL'}

    filepath: bpy.props.StringProperty(
        name="Image Filepath",
        description="Choose an image to store as a reference",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )

    def execute(self, context):
        """
        Execute the operator.
        
        This method is called when the operator is run. It imports the background
        image from the given filepath and stores its reference in the Blender scene.
        
        Parameters:
            context: The current Blender context, containing references to the active object and scene.
        
        Returns:
            dict: A dictionary indicating the operator's status. Returns {'FINISHED'} if successful, or {'CANCELLED'} if not.
        """
        # Load the image and store its reference
        try:
            # Load the image
            image = bpy.data.images.load(self.filepath)
            
            # Store the image's name in the scene properties
            context.scene.background_image_reference = image.name

        except Exception as e:
            self.report({'ERROR'}, f"Failed to load background image. Error: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        """
        Invoke the file selection dialog.
        
        This method opens the file selection dialog for the user to choose an image.
        
        Parameters:
            context: The current Blender context.
            event: The event that triggered the operator.
        
        Returns:
            dict: A dictionary indicating the operator's status. Returns {'RUNNING_MODAL'}.
        """
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}



class ScaleBackgroundPlanesOperator(bpy.types.Operator):
    """
    Operator to scale the background planes in the Blender scene.
    
    This class defines an operator that, when executed, scales the background 
    planes based on the specified X, Y, and Z scaling factors stored in the 
    scene's background_controls property group.
    
    Attributes:
        bl_idname (str): Blender identifier for the operator.
        bl_label (str): Label displayed in the Blender UI.
        bl_options (set): Operator options defining its behavior in Blender.
    """
    
    bl_idname = "object.scale_background_planes"
    bl_label = "Scale Background Planes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Execute the operator.
        
        This method is called when the operator is run. It scales the background 
        planes based on the X, Y, and Z scaling factors specified in the scene's 
        background_controls property group.
        
        Parameters:
            context: The current Blender context, containing references to the active object and scene.
        
        Returns:
            dict: A dictionary indicating the operator's status. Returns {'FINISHED'} if successful, or {'CANCELLED'} if an error occurs.
        """
        try:
            background_controls = context.scene.background_controls
            print(f"Scaling planes with X: {background_controls.plane_scale_x}, Y: {background_controls.plane_scale_y}, Z: {background_controls.plane_scale_z}")

            plane_names = ["background_plane.top", "background_plane.bottom", "background_plane.right", 
                           "background_plane.left", "background_plane.back", "background_plane.front"]

            for name in plane_names:
                plane = bpy.data.objects.get(name)
                if plane:
                    print(f"Scaling {name}")
                    plane.scale.x = background_controls.plane_scale_x
                    plane.scale.y = background_controls.plane_scale_y
                    plane.scale.z = background_controls.plane_scale_z
                else:
                    print(f"{name} not found in the scene.")
            
            bpy.context.view_layer.update()
            return {'FINISHED'}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {'CANCELLED'}


class ToggleBackgroundPlanesOperator(bpy.types.Operator):
    """
    Operator to toggle the visibility of background planes in the Blender scene.
    
    This class defines an operator that, when executed, either creates or 
    removes background planes at specified distances from the active object. 
    These planes are textured with a background image if available.
    
    Attributes:
        bl_idname (str): Blender identifier for the operator.
        bl_label (str): Label displayed in the Blender UI.
        bl_options (set): Operator options defining its behavior in Blender.
        distance (FloatProperty): The distance from the active object at which 
                                  the background planes will be created or removed.
    """
    
    bl_idname = "object.toggle_background_planes"
    bl_label = "Toggle Background"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=10.0)

    def execute(self, context):
        image_name = context.scene.background_image_reference
        if not bpy.data.images.get(image_name):
            self.report({'WARNING'}, "Background image not set. Aborting operation.")
            return {'CANCELLED'}
        
        original_active_obj = context.active_object

        locations_and_names = [
            ((0, 0, self.distance), "background_plane.top"),
            ((0, 0, -self.distance), "background_plane.bottom"),
            ((self.distance, 0, 0), "background_plane.right"),
            ((-self.distance, 0, 0), "background_plane.left"),
            ((0, self.distance, 0), "background_plane.back"),
            ((0, -self.distance, 0), "background_plane.front"),
        ]

        planes_exist = all(bpy.data.objects.get(name) is not None for _, name in locations_and_names)

        if planes_exist:
            for _, name in locations_and_names:
                plane = bpy.data.objects.get(name)
                if plane is not None:
                    bpy.data.objects.remove(plane)
        else:
            for location, name in locations_and_names:
                location = original_active_obj.location + Vector(location)
                bpy.ops.mesh.primitive_plane_add(size=1, location=location)
                plane = context.active_object
                plane.name = name
                direction = original_active_obj.location - plane.location
                plane.rotation_mode = 'QUATERNION'
                plane.rotation_quaternion = direction.to_track_quat('Z', 'Y')

                image_name = context.scene.background_image_reference
                if image_name:
                    image = bpy.data.images.get(image_name)
                    if image:
                        mat = bpy.data.materials.new(name="BackgroundImageMaterial")
                        mat.use_nodes = True
                        bsdf = mat.node_tree.nodes["Principled BSDF"]
                        tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
                        tex_image.image = image
                        mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
                        plane.data.materials.append(mat)
                plane.select_set(False)

            # Store the current active object and its mode
            original_active_object = bpy.context.view_layer.objects.active
            original_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'

            # Set the target object as active and change mode to 'OBJECT'
            bpy.context.view_layer.objects.active = bpy.data.objects['background_plane.bottom']
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active.select_set(True)

            # Perform the rotation
            bpy.ops.transform.rotate(value=radians(180), orient_axis='Z')

            # Restore original active object and its mode
            bpy.context.view_layer.objects.active = original_active_object
            if original_active_object:
                bpy.ops.object.mode_set(mode=original_mode)


        context.view_layer.objects.active = original_active_obj
        original_active_obj.select_set(True)
        
        for obj in context.selected_objects:
            if obj != original_active_obj:
                obj.select_set(False)

        return {'FINISHED'}

    def invoke(self, context, event):
        """
        Invoke the operator.
        
        This method is called to initialize the operator. It sets the distance
        property based on the scene's background_plane_distance.
        
        Parameters:
            context: The current Blender context.
            event: The event that triggered the operator.
        
        Returns:
            dict: The status of the execute method.
        """
        self.distance = context.scene.background_plane_distance
        return self.execute(context)

    
###Panels




    








    




