import bpy
import os
import math
from mathutils import Matrix, Vector

###Functions
def mesh_menu_func(self, context):
    self.layout.operator(CreateBackgroundImageMeshOperator.bl_idname, icon='MESH_PLANE')

def update_background_plane_distance(self, context):
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
    bl_idname = "object.call_update_background_plane_distance"
    bl_label = "Call Update Background Plane Distance"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Here, 'self' refers to the operator object, which doesn't have a 'background_plane_distance' attribute.
        # So, we pass 'context.scene' instead, which should have the 'background_plane_distance' attribute.
        update_background_plane_distance(context.scene, context)
        return {'FINISHED'}

class CreateBackgroundImageMeshOperator(bpy.types.Operator):
    bl_idname = "mesh.create_background_image"
    bl_label = "Background Image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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
    bl_idname = "object.hide_background_planes"
    bl_label = "Hide Background"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ScaleBackgroundPlanesOperator(bpy.types.Operator):
    bl_idname = "object.scale_background_planes"
    bl_label = "Scale Background Planes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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
    bl_idname = "object.toggle_background_planes"
    bl_label = "Toggle Background"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=10.0)

    def execute(self, context):
        # Store the original active object and its selection state
        
        image_name = context.scene.background_image_reference
        if not bpy.data.images.get(image_name):
            self.report({'WARNING'}, "Background image not set. Aborting operation.")
            return {'CANCELLED'}
        
        original_active_obj = context.active_object
        original_active_obj_selected = original_active_obj.select_get()

        # Calculate the plane locations and names
        locations_and_names = [
            ((0, 0, self.distance), "background_plane.top"),  # Top
            ((0, 0, -self.distance), "background_plane.bottom"),  # Bottom
            ((self.distance, 0, 0), "background_plane.right"),  # Right
            ((-self.distance, 0, 0), "background_plane.left"),  # Left
            ((0, self.distance, 0), "background_plane.back"),  # Front
            ((0, -self.distance, 0), "background_plane.front"),  # Back
        ]

        # Check if the planes already exist
        planes_exist = all(bpy.data.objects.get(name) is not None for _, name in locations_and_names)

        if planes_exist:
            # Remove the planes
            for _, name in locations_and_names:
                plane = bpy.data.objects.get(name)
                if plane is not None:
                    bpy.data.objects.remove(plane)
        else:
            # Create the planes
            for location, name in locations_and_names:
                # Add the location of the active object to the location of the plane
                location = original_active_obj.location + Vector(location)
                bpy.ops.mesh.primitive_plane_add(size=1, location=location)
                plane = context.active_object

                # Set the plane name
                plane.name = name

                # Point the plane towards the active object
                direction = original_active_obj.location - plane.location
                plane.rotation_mode = 'QUATERNION'
                plane.rotation_quaternion = direction.to_track_quat('Z', 'Y')

                # Assign the background image material to the plane
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

                # Deselect the new plane
                plane.select_set(False)

        # Restore the original active object and its selection state
        context.view_layer.objects.active = original_active_obj
        original_active_obj.select_set(True)

        # Deselect all other objects
        for obj in context.selected_objects:
            if obj != original_active_obj:
                obj.select_set(False)

        return {'FINISHED'}

    def invoke(self, context, event):
        self.distance = context.scene.background_plane_distance
        return self.execute(context)
    
###Panels




    








    




