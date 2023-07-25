import bpy
import json
import bmesh
import numpy as np
import sys
import os
from mathutils import Matrix, Vector

python_path = os.path.abspath("../Python")
sys.path.append(python_path)
from traitblender_helpers import *

class LoadObjectOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "traitblender.load_object_operator"
    bl_label = "Load Object"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        try: 
            active_mesh = get_setting(bpy.context, "active_mesh")[0]
            active_mesh_path = get_setting(bpy.context, "predefined_meshes")[active_mesh][0]
            bpy.ops.import_scene.obj(filepath=active_mesh_path)

            # Select the imported object
            imported_obj = bpy.context.selected_objects[0]
            bpy.context.view_layer.objects.active = imported_obj
            imported_obj.select_set(True)
        except Exception as e:
            print("Failed to import active object. Error:", e)
        return {'FINISHED'}
class ImportTraitBlenderSettings(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "traitblender.import_traitblender_settings"
    bl_label = "Import TraitBlender Settings"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        # Load the active mesh from the JSON file
        try:
            with open("../data/settings/settings.json", "r") as f:
                data = json.load(f)
                context.scene.traitblender_settings = json.dumps(data)
        except Exception as e:
            print("Failed to load mesh from JSON file. Error:", e)
            context.view_layer.objects.active = context.object

        return {'FINISHED'}


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
            context.scene.camera_rotation_x = 0.0
            context.scene.camera_rotation_y = 0.0
            context.scene.camera_rotation_z = 0.0

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
class RotateCamerasOperator(bpy.types.Operator):
    bl_idname = "object.rotate_cameras"
    bl_label = "Rotate Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    axis: bpy.props.StringProperty()
    angle: bpy.props.FloatProperty()

    def execute(self, context):
        # Get the names of the cameras to rotate
        camera_names = ["camera.top", "camera.bottom", "camera.right", "camera.left", "camera.front", "camera.back"]

        # Rotate the cameras
        for name in camera_names:
            camera = bpy.data.objects.get(name)
            if camera is not None:
                # Get the original mesh
                original_mesh = bpy.data.objects.get(camera["original_mesh"])
                if original_mesh is None:
                    self.report({'ERROR'}, "Original mesh has been deleted")
                    return {'CANCELLED'}

                # Reset the camera to its original rotation
                camera.rotation_quaternion = camera["original_rotation"]

                # Rotate the camera around the mesh
                pivot = original_mesh.location
                rotation_matrix = Matrix.Rotation(self.angle, 4, self.axis)
                camera.location = pivot + rotation_matrix @ (camera.location - pivot)

                # Point the camera towards the original mesh
                direction = original_mesh.location - camera.location
                camera.rotation_mode = 'QUATERNION'
                camera.rotation_quaternion = direction.to_track_quat('-Z', 'Y')

        return {'FINISHED'}
class CameraControls(bpy.types.PropertyGroup):
    expanded: bpy.props.BoolProperty(
        name="Camera",
        description="Expand or collapse the camera controls",
        default=False
    )
class RenderAllCamerasOperator(bpy.types.Operator):
    bl_idname = "object.render_all_cameras"
    bl_label = "Render All Cameras"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Ensure the render directory is set
        if not context.scene.render_output_directory:
            self.report({'ERROR'}, "Please select a render directory first.")
            return {'CANCELLED'}

        # Get the names of the cameras to render
        camera_names = ["camera.top", "camera.bottom", "camera.right", "camera.left", "camera.front", "camera.back"]

        # Store the current active camera
        original_camera = bpy.context.scene.camera

        for name in camera_names:
            camera = bpy.data.objects.get(name)
            if camera:
                # Set the render path with the camera name
                bpy.context.scene.render.filepath = os.path.join(context.scene.render_output_directory, name.split('.')[-1] + ".png")
                
                bpy.context.scene.camera = camera
                bpy.ops.render.render(write_still=True)
            

        # Restore the original active camera
        bpy.context.scene.camera = original_camera

        # Report that all images have been rendered
        self.report({'INFO'}, "All images have been rendered and saved!")

        return {'FINISHED'}
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
def update_camera_rotation_x(self, context):
    bpy.ops.object.rotate_cameras(axis='X', angle=np.radians(self.camera_rotation_x))
def update_camera_rotation_y(self, context):
    bpy.ops.object.rotate_cameras(axis='Y', angle=np.radians(self.camera_rotation_y))
def update_camera_rotation_z(self, context):
    bpy.ops.object.rotate_cameras(axis='Z', angle=np.radians(self.camera_rotation_z))
@bpy.app.handlers.persistent
def delete_cameras_on_mesh_deletion(dummy):
    # Get the names of the cameras to delete
    camera_names = ["camera.top", "camera.bottom", "camera.right", "camera.left", "camera.front", "camera.back"]

    # Delete the cameras if the original mesh has been deleted
    for name in camera_names:
        camera = bpy.data.objects.get(name)
        if camera is not None and bpy.data.objects.get(camera["original_mesh"]) is None:
            bpy.data.objects.remove(camera)

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

class ToggleBackgroundPlanesOperator(bpy.types.Operator):
    bl_idname = "object.toggle_background_planes"
    bl_label = "Toggle Background"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=10.0)

    def execute(self, context):
        # Store the original active object and its selection state
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
class ScaleBackgroundPlanesOperator(bpy.types.Operator):
    bl_idname = "object.scale_background_planes"
    bl_label = "Scale Background Planes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        background_controls = context.scene.background_controls
        plane_names = ["background_plane.top", "background_plane.bottom", "background_plane.right", 
                       "background_plane.left", "background_plane.back", "background_plane.front"]

        for name in plane_names:
            plane = bpy.data.objects.get(name)
            if plane:
                plane.scale.x = background_controls.plane_scale_x
                plane.scale.y = background_controls.plane_scale_y
                plane.scale.z = background_controls.plane_scale_z

        return {'FINISHED'}    
    
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
def mesh_menu_func(self, context):
    self.layout.operator(CreateBackgroundImageMeshOperator.bl_idname, icon='MESH_PLANE')

class TraitBlenderPanel(bpy.types.Panel):
    bl_label = "TraitBlender"
    bl_idname = "VIEW3D_PT_traitblender"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TraitBlender"

    def draw(self, context):
        layout = self.layout
        background_controls = context.scene.background_controls
        camera_controls = context.scene.camera_controls
        
        layout.prop(background_controls, "expanded", icon="TRIA_DOWN" if background_controls.expanded else "TRIA_RIGHT", emboss=False)
        if background_controls.expanded:
            layout.operator("traitblender.import_background_image", text="Import Background Image")
            layout.operator("object.toggle_background_planes", text="Toggle Background")
            layout.operator("object.hide_background_planes", text="Hide Background")
            layout.prop(context.scene, "background_plane_distance", text="Background Distance")
            
            # Add scale controls for the background planes
            layout.label(text="Background Plane Scale:")
            layout.prop(background_controls, "plane_scale_x", text="X")
            layout.prop(background_controls, "plane_scale_y", text="Y")
            layout.prop(background_controls, "plane_scale_z", text="Z")
            layout.operator("object.scale_background_planes", text="Apply Scaling")

        layout.prop(camera_controls, "expanded", icon="TRIA_DOWN" if camera_controls.expanded else "TRIA_RIGHT", emboss=False)
        if camera_controls.expanded:
            layout.operator("object.toggle_cameras", text="Toggle Cameras")
            layout.operator("object.hide_cameras", text="Hide Cameras")
            layout.prop(context.scene, "place_cameras_distance", text="Camera Distance")

            rotation_row_x = layout.row()
            rotation_row_x.label(text="Rotation X:")
            rotation_row_x.prop(context.scene, "camera_rotation_x", text="")
            rotation_row_y = layout.row()
            rotation_row_y.label(text="Y:")
            rotation_row_y.prop(context.scene, "camera_rotation_y", text="")
            rotation_row_z = layout.row()
            rotation_row_z.label(text="Z:")
            rotation_row_z.prop(context.scene, "camera_rotation_z", text="")
            
            layout.prop(context.scene, "render_output_directory", text="Render Directory")
            layout.operator("object.render_all_cameras", text="Render All Cameras")




def register():
    bpy.utils.register_class(ImportTraitBlenderSettings)
    bpy.utils.register_class(LoadObjectOperator)
    bpy.utils.register_class(ToggleCamerasOperator)
    bpy.utils.register_class(TraitBlenderPanel)
    bpy.utils.register_class(CameraControls)
    bpy.utils.register_class(HideCamerasOperator)
    bpy.utils.register_class(SelectRenderDirectoryOperator)
    bpy.utils.register_class(RenderAllCamerasOperator)
    bpy.utils.register_class(ToggleBackgroundPlanesOperator)
    bpy.utils.register_class(ScaleBackgroundPlanesOperator)
    bpy.utils.register_class(HideBackgroundPlanesOperator)

    bpy.utils.register_class(ImportBackgroundImageOperator)
    bpy.utils.register_class(BackgroundControls)
    bpy.types.Scene.background_controls = bpy.props.PointerProperty(type=BackgroundControls)
    bpy.types.Scene.background_image_reference = bpy.props.StringProperty(default="")

    bpy.utils.register_class(CreateBackgroundImageMeshOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(mesh_menu_func)

    bpy.types.Scene.camera_controls = bpy.props.PointerProperty(type=CameraControls)
    bpy.types.Scene.place_cameras_distance = bpy.props.FloatProperty(
        name="Place Cameras Distance",
        default=10.0,
        update=update_camera_distance  # Add the update function here
    )

    #background plane distance
    bpy.types.Scene.background_plane_distance = bpy.props.FloatProperty(
    name="Background Plane Distance",
    default=10.0,
    update=update_background_plane_distance
    )


    
    bpy.types.Scene.traitblender_settings = bpy.props.StringProperty(
        name="Active Mesh Data",
        description="JSON data for the active mesh",
        default="",
    )
    
    bpy.utils.register_class(RotateCamerasOperator)

    bpy.types.Scene.camera_rotation_x = bpy.props.FloatProperty(
        name="Camera Rotation X",
        default=0.0,
        update=update_camera_rotation_x
    )
    bpy.types.Scene.camera_rotation_y = bpy.props.FloatProperty(
        name="Camera Rotation Y",
        default=0.0,
        update=update_camera_rotation_y
    )
    bpy.types.Scene.camera_rotation_z = bpy.props.FloatProperty(
        name="Camera Rotation Z",
        default=0.0,
        update=update_camera_rotation_z
    )
    
    bpy.types.Scene.render_output_directory = bpy.props.StringProperty(
        name="Render Output Directory",
        description="Directory to save the renders",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    
    bpy.app.handlers.depsgraph_update_post.append(delete_cameras_on_mesh_deletion)
def unregister():
    bpy.utils.unregister_class(ImportTraitBlenderSettings)
    bpy.utils.unregister_class(LoadObjectOperator)
    bpy.utils.unregister_class(ToggleCamerasOperator)
    bpy.utils.unregister_class(TraitBlenderPanel)
    bpy.utils.unregister_class(CameraControls)
    bpy.utils.unregister_class(HideCamerasOperator)
    bpy.utils.unregister_class(SelectRenderDirectoryOperator)
    bpy.utils.unregister_class(RenderAllCamerasOperator)
    bpy.utils.unregister_class(ToggleBackgroundPlanesOperator)
    bpy.utils.unregister_class(ScaleBackgroundPlanesOperator)
    bpy.utils.unregister_class(HideBackgroundPlanesOperator)

    bpy.utils.unregister_class(ImportBackgroundImageOperator)
    bpy.utils.unregister_class(BackgroundControls)
    del bpy.types.Scene.background_controls
    del bpy.types.Scene.background_image_reference
    
    bpy.utils.unregister_class(CreateBackgroundImageMeshOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(mesh_menu_func)

    bpy.utils.unregister_class(RotateCamerasOperator)
    
    del bpy.types.Scene.camera_rotation_x
    del bpy.types.Scene.camera_rotation_y
    del bpy.types.Scene.camera_rotation_z    
    del bpy.types.Scene.traitblender_settings
    del bpy.types.Scene.place_cameras_distance
    del bpy.types.Scene.camera_controls
    del bpy.types.Scene.render_output_directory

    
    
    bpy.app.handlers.depsgraph_update_post.remove(delete_cameras_on_mesh_deletion)

if __name__ == "__main__":
    register()
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.traitblender.import_traitblender_settings()
    bpy.ops.traitblender.load_object_operator()

