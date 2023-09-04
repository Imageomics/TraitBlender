import bpy
import json
import bmesh
import numpy as np
import sys
import os
from mathutils import Matrix, Vector
import math
import csv
import types
import inspect
import bpy_extras
from DeleteAllObjectsOperator import *


class ExportActiveObjectOperator(bpy.types.Operator):
    bl_idname = "object.export_active_object"
    bl_label = "Export Active Object"

    @staticmethod
    def export_active_object(filepath, format=".obj"):
        # Store the current selection
        original_selection = bpy.context.selected_objects

        # Deselect all objects
        for obj in original_selection:
            obj.select_set(False)

        # Select only the active object
        active_object = bpy.context.view_layer.objects.active
        if active_object:
            active_object.select_set(True)
        else:
            print("No active object to export.")
            return

        # Determine the export function based on the format
        if format == ".obj":
            export_func = bpy.ops.export_scene.obj
        elif format == ".fbx":
            export_func = bpy.ops.export_scene.fbx
        else:
            print("Unsupported format.")
            return

        # Set the filepath
        full_filepath = os.path.join(filepath, active_object.name + format)

        # Execute the export function
        export_func(filepath=full_filepath, use_selection=True)

        # Restore the original selection
        for obj in original_selection:
            obj.select_set(True)

        print(f"Exported {active_object.name} to {full_filepath}.")

    def execute(self, context):
        export_dir = context.scene.export_directory
        export_format = context.scene.export_format
        if not export_dir:
            self.report({'ERROR'}, "Please select an export directory first.")
            return {'CANCELLED'}
        self.export_active_object(export_dir, export_format)
        return {'FINISHED'}

  

class ExecuteWithSelectedCSVRowOperator(bpy.types.Operator):
    bl_idname = "object.execute_with_selected_csv_row"
    bl_label = "Run Function with Selected CSV Row"

    def execute(self, context):
        selected_row = dict(context.scene['csv_data'][int(context.scene.csv_label_props.csv_label_enum)])
        json_args = json.dumps(selected_row)
        bpy.ops.object.execute_stored_function(json_args=json_args)
        return {'FINISHED'}


def get_csv_labels(self, context):
    labels = context.scene.get('csv_data', [])
    column_name = context.scene.get('column_names', [])[0]
    if labels and column_name:
        return [(str(i), row.get(column_name, ""), row.get(column_name, "")) for i, row in enumerate(labels)]
    else:
        return []

class CSVLabelProperties(bpy.types.PropertyGroup):
    csv_label_enum: bpy.props.EnumProperty(
        items=get_csv_labels,
        name="CSV Labels",
        description="Labels imported from CSV"
    )

class ImportCSVOperator(bpy.types.Operator):
    bl_idname = "object.import_csv"
    bl_label = "Import CSV"
    
    # Property to store the path to the CSV file
    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        description="Path to the CSV file",
        default="",
        subtype='FILE_PATH'
    )
    
    @staticmethod
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
            first_column_name = column_names[0].lower()
            allowed_first_column_names = ["tip", "name", "label"]
            
            if first_column_name not in allowed_first_column_names:
                raise ValueError('Column 1 Must be titled "tip", "name", or "label"!')
            
            # Loop through each row and append it to the list
            for row in csvreader:
                # Convert the types of the values in the row
                for key, value in row.items():
                    try:
                        row[key] = float(value)
                    except ValueError:
                        try:
                            row[key] = int(value)
                        except ValueError:
                            if value.lower() == 'true':
                                row[key] = True
                            elif value.lower() == 'false':
                                row[key] = False
                            else:
                                row[key] = value
            
                csv_data.append(row)
        
        # Convert the list of dictionaries to a JSON object
        csv_json = json.dumps(csv_data)
        
        return csv_data, column_names

    def execute(self, context):
        try:
            csv_data, column_names = self.import_csv(bpy.data.scenes["Scene"].csv_file_path)
            context.scene['csv_data'] = csv_data
            context.scene['column_names'] = column_names

            # Update the csv_labels property
            labels = [row.get(column_names[0]) for row in csv_data]
            items = [(str(i), name, name) for i, name in enumerate(labels)]
            context.scene.csv_label_props.csv_label_enum = items

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}


class ImportMakeMeshFunctionPathOperator(bpy.types.Operator):
    bl_idname = "object.import_make_mesh_function_path"
    bl_label = "Import Make Mesh Function Path"

    make_mesh_function_path: bpy.props.StringProperty(name="Make Mesh Function Path")

    def execute(self, context):
        context.scene.make_mesh_function_path = self.make_mesh_function_path
        return {'FINISHED'}


class ExecuteStoredFunctionOperator(bpy.types.Operator):
    bl_idname = "object.execute_stored_function"
    bl_label = "Execute Stored Function"

    # A string property to accept JSON-formatted arguments
    json_args: bpy.props.StringProperty(name="JSON Arguments")

    def execute(self, context):
        # Use the path stored in the scene property
        make_mesh_function_path = context.scene.make_mesh_function_path

        if not make_mesh_function_path:
            self.report({'WARNING'}, "No function path specified.")
            return {'CANCELLED'}

        with open(make_mesh_function_path, 'r') as f:
            script_content = f.read()

        import_statements = [line for line in script_content.split('\n') if line.startswith('import') or line.startswith('from')]

        local_variable_dict = {}
        global_variable_dict = {'bpy': bpy}

        # Dynamically import modules
        for statement in import_statements:
            exec(statement, global_variable_dict)

        exec(script_content, global_variable_dict, local_variable_dict)

        for func_name, func_object in local_variable_dict.items():
            if isinstance(func_object, types.FunctionType):
                make_mesh = func_object
                break

        if make_mesh is not None:
            args_dict = json.loads(self.json_args) if self.json_args else {}
            make_mesh(**args_dict)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "No function found in the imported script.")
            return {'CANCELLED'}

        
class SunControls(bpy.types.PropertyGroup):
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0)
    diffuse: bpy.props.FloatProperty(name="Diffuse", default=1.0, min=0.0, max=1.0)
    specular: bpy.props.FloatProperty(name="Specular", default=1.0, min=0.0, max=1.0)
    volume: bpy.props.FloatProperty(name="Volume", default=1.0, min=0.0, max=1.0)
    angle: bpy.props.FloatProperty(name="Angle", default=0.0, min=0.0, max=180.0)


class ToggleSunsOperator(bpy.types.Operator):
    bl_idname = "object.toggle_suns"
    bl_label = "Toggle Suns"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=10.0)

    def execute(self, context):
        # Get and store the original active object
        original_active_obj = context.active_object
        if original_active_obj is None:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        # Calculate the sun locations and names
        locations_and_names = [
            ((0, 0, self.distance), "sun.top"),
            ((0, 0, -self.distance), "sun.bottom"),
            ((self.distance, 0, 0), "sun.right"),
            ((-self.distance, 0, 0), "sun.left"),
            ((0, self.distance, 0), "sun.back"),
            ((0, -self.distance, 0), "sun.front"),
        ]

        # Check if the suns already exist
        suns_exist = all(bpy.data.objects.get(name) is not None for _, name in locations_and_names)

        if suns_exist:
            # Remove the suns
            for _, name in locations_and_names:
                sun = bpy.data.objects.get(name)
                if sun is not None:
                    bpy.data.objects.remove(sun)
        else:
            # Create the suns
            for location, name in locations_and_names:
                # Add the location of the active object to the location of the sun
                location = original_active_obj.location + Vector(location)
                bpy.ops.object.light_add(type='SUN', location=location)
                sun = context.active_object

                # Set the sun name
                sun.name = name

                # Point the sun towards the active object
                direction = original_active_obj.location - sun.location
                sun.rotation_mode = 'QUATERNION'
                sun.rotation_quaternion = direction.to_track_quat('-Z', 'Y')

                # Deselect the new sun
                sun.select_set(False)

        # Restore the original active object
        context.view_layer.objects.active = original_active_obj

        return {'FINISHED'}

class HideSunsOperator(bpy.types.Operator):
    bl_idname = "object.hide_suns"
    bl_label = "Hide Suns"
    bl_options = {'REGISTER', 'UNDO'}

    sun_names: bpy.props.StringProperty(
        name="Sun Names",
        default="sun.top,sun.bottom,sun.right,sun.left,sun.front,sun.back"
    )

    def execute(self, context):
        # Split the sun names by comma
        sun_names_list = self.sun_names.split(',')

        # Check if the suns already exist and are visible
        suns_exist = all(bpy.data.objects.get(name) is not None for name in sun_names_list)
        suns_visible = all(not bpy.data.objects[name].hide_viewport for name in sun_names_list if bpy.data.objects.get(name) is not None)

        if suns_exist and suns_visible:
            # Hide the suns
            for name in sun_names_list:
                sun = bpy.data.objects.get(name)
                if sun is not None:
                    sun.hide_viewport = True
        elif suns_exist and not suns_visible:
            # Unhide the suns
            for name in sun_names_list:
                sun = bpy.data.objects.get(name)
                if sun is not None:
                    sun.hide_viewport = False

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




class CallUpdateBackgroundPlaneDistanceOperator(bpy.types.Operator):
    bl_idname = "object.call_update_background_plane_distance"
    bl_label = "Call Update Background Plane Distance"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Here, 'self' refers to the operator object, which doesn't have a 'background_plane_distance' attribute.
        # So, we pass 'context.scene' instead, which should have the 'background_plane_distance' attribute.
        update_background_plane_distance(context.scene, context)
        return {'FINISHED'}


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
    
    
class SegmentationControls(bpy.types.Panel):
    bl_label = "Segmentation Controls"
    bl_idname = "OBJECT_PT_segmentation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_category = "TraitBlender"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        # Draw the vertex group controls
        row = layout.row()
        row.template_list("MESH_UL_vgroups", "", obj, "vertex_groups", obj.vertex_groups, "active_index", rows=2)

        col = row.column(align=True)
        col.operator("object.vertex_group_add", icon='ADD', text="")
        col.operator("object.vertex_group_remove", icon='REMOVE', text="").all = False
        col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")
        col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        # Add the new operators
        layout.operator("object.save_vertex_groups_to_csv", text="Save Vertex Groups to CSV").csv_file_path = "path/to/save.csv"
        layout.operator("object.load_vertex_groups_from_csv", text="Load Vertex Groups from CSV").csv_file_path = "path/to/load.csv"



class SegmentationControlsProperty(bpy.types.PropertyGroup):
    expanded: bpy.props.BoolProperty(default=False)
    segmentation_controls: bpy.props.BoolProperty(default=False)  # Add this line


class SunControlsPanel(bpy.types.Panel):
    bl_label = "Lights"
    bl_idname = "OBJECT_PT_sun_controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'  # Change this to the category where you want the panel to appear
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # Toggle Suns Button
        row = layout.row()
        row.operator("object.toggle_suns", text="Toggle Suns")

        # Hide/Unhide Suns Button
        row = layout.row()
        row.operator("object.hide_suns", text="Hide/Unhide Suns")


class UpdateSunStrengthOperator(bpy.types.Operator):
    bl_idname = "object.update_sun_strength"
    bl_label = "Update Sun Strength"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sun_names = ["sun.top", "sun.bottom", "sun.right", "sun.left", "sun.front", "sun.back"]

        for name in sun_names:
            sun = bpy.data.objects.get(name)
            if sun and sun.type == 'LIGHT':
                sun.data.energy = context.scene.sun_strength

        self.report({'INFO'}, "Sun strength updated successfully!")
        return {'FINISHED'}


class SaveVertexGroupsToCSVOperator(bpy.types.Operator):
    bl_idname = "object.save_vertex_groups_to_csv"
    bl_label = "Save Vertex Groups to CSV"
    bl_options = {'REGISTER', 'UNDO'}

    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        subtype='FILE_PATH'
    )

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object selected.")
            return {'CANCELLED'}
        
        with open(self.csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Vertex Index", "Group Name", "Weight"])
            for vert in obj.data.vertices:
                for group in vert.groups:
                    group_name = obj.vertex_groups[group.group].name
                    weight = group.weight
                    csvwriter.writerow([vert.index, group_name, weight])

        return {'FINISHED'}

class LoadVertexGroupsFromCSVOperator(bpy.types.Operator):
    bl_idname = "object.load_vertex_groups_from_csv"
    bl_label = "Load Vertex Groups from CSV"
    bl_options = {'REGISTER', 'UNDO'}

    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        subtype='FILE_PATH'
    )

    def execute(self, context):
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object selected.")
            return {'CANCELLED'}
        
        obj.vertex_groups.clear()
        with open(self.csv_file_path, 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                vert_index, group_name, weight = int(row[0]), row[1], float(row[2])
                if group_name not in obj.vertex_groups:
                    obj.vertex_groups.new(name=group_name)
                obj.vertex_groups[group_name].add([vert_index], weight, 'REPLACE')

        return {'FINISHED'}

class WorldBackgroundControls(bpy.types.PropertyGroup):
    expanded: bpy.props.BoolProperty(
        name="Background",
        description="Expand the background controls",
        default=False
    )
    
    red: bpy.props.FloatProperty(
        name="Red",
        description="Red component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    green: bpy.props.FloatProperty(
        name="Green",
        description="Green component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    blue: bpy.props.FloatProperty(
        name="Blue",
        description="Blue component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    alpha: bpy.props.FloatProperty(
        name="Alpha",
        description="Alpha component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )

    world_color_expanded: bpy.props.BoolProperty(
        name="World Color Expanded",
        default=True
    )
    
    imported_backgrounds_expanded: bpy.props.BoolProperty(
        name="Imported Backgrounds Expanded",
        default=True
    )
    
    background_scale_expanded: bpy.props.BoolProperty(
        name="Background Scale Expanded",
        default=True
    )
    


class ChangeWorldBackgroundColor(bpy.types.Operator):
    bl_idname = "scene.change_background_color"
    bl_label = "Change World Background Color"
    
    def execute(self, context):
        # Access the active scene
        scene = context.scene

        # Access the world settings
        world = scene.world

        # Access the background_controls property group
        world_background_controls = context.scene.world_background_controls

        # Enable use_nodes to allow node-based modifications
        world.use_nodes = True

        # Access the node tree
        node_tree = world.node_tree

        # Find the "Background" node
        world_background_node = node_tree.nodes.get("Background")

        # Change the color of the background
        world_background_node.inputs[0].default_value = (
            world_background_controls.red, 
            world_background_controls.green, 
            world_background_controls.blue, 
            world_background_controls.alpha
        )
        
        return {'FINISHED'}

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


bpy.types.Scene.mesh_generation_controls = bpy.props.BoolProperty(name="Mesh Generation Controls", default=False)

class OpenMeshFunctionFileBrowserOperator(bpy.types.Operator):
    bl_idname = "object.open_mesh_function_file_browser"
    bl_label = "Invoke File Browser"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        context.scene.make_mesh_function_path = self.filepath
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ExportControlsPropertyGroup(bpy.types.PropertyGroup):
    export_controls: bpy.props.BoolProperty(
        name="Show/Hide",
        description="Show or hide the 3D Export options",
        default=False
    )

class TraitBlenderPanel(bpy.types.Panel):
    bl_label = "TraitBlender"
    bl_idname = "VIEW3D_PT_traitblender"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TraitBlender"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        background_controls = context.scene.background_controls
        camera_controls = context.scene.camera_controls
        segmentation_controls_property = context.scene.segmentation_controls_property  # Get the property group from the scene
        world_background_controls = context.scene.world_background_controls 
        
        layout.prop(context.scene, "mesh_generation_controls", icon="TRIA_DOWN" if context.scene.mesh_generation_controls else "TRIA_RIGHT", emboss=False, text="Mesh Generation")
        if context.scene.mesh_generation_controls:
                row = layout.row()
                row.alignment = 'CENTER'
                row.label(text="Select Mesh Function File", icon='NONE')
                
                # File path selection
                row = layout.row(align=True)
                row.prop(context.scene, 'make_mesh_function_path', text="")
                row.operator("object.open_mesh_function_file_browser", icon='FILEBROWSER', text="")
                
                # Button to execute the function
                layout.operator("object.execute_stored_function", text="Run Function")
                layout.prop(context.scene, "csv_file_path", text="CSV File Path")
                layout.operator("object.import_csv", text="Import CSV")

                if 'csv_data' in context.scene:
                    layout.prop(context.scene.csv_label_props, "csv_label_enum", text="Select Label")
        
                layout.operator("object.execute_with_selected_csv_row", text="Run Function with Selected CSV Row")        
        
        layout.prop(world_background_controls, "expanded", icon="TRIA_DOWN" if world_background_controls.expanded else "TRIA_RIGHT", emboss=False)
        if world_background_controls.expanded:
            box = layout.box()
            
            # Center the text "World Color"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="World Color")
            
            # Add RGBA controls with letters inside the fields
            row = box.row()
            row.prop(world_background_controls, "red", text="R")
            row = box.row()
            row.prop(world_background_controls, "green", text="G")
            row = box.row()
            row.prop(world_background_controls, "blue", text="B")
            row = box.row()
            row.prop(world_background_controls, "alpha", text="A")
            
            box.operator("scene.change_background_color", text="Apply Background Color")

            # New box for Imported Backgrounds
            box = layout.box()

            # Center the text "Imported Backgrounds"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Imported Backgrounds")

            # Add existing controls for imported backgrounds
            box.operator("traitblender.import_background_image", text="Import Background Image")
            box.operator("object.toggle_background_planes", text="Toggle Background")
            box.operator("object.hide_background_planes", text="Hide Background")
            box.prop(context.scene, "background_plane_distance", text="Background Distance")

            # New box for Background Plane Scale
            box = layout.box()

            # Center the text "Background Plane Scale"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Background Plane Scale")

            # Add scale controls for the background planes
            row = box.row()
            row.prop(background_controls, "plane_scale_x", text="X")
            row = box.row()
            row.prop(background_controls, "plane_scale_y", text="Y")
            row = box.row()
            row.prop(background_controls, "plane_scale_z", text="Z")
            box.operator("object.scale_background_planes", text="Apply Scaling")









        layout.prop(context.scene, "lights_controls", icon="TRIA_DOWN" if context.scene.lights_controls else "TRIA_RIGHT", emboss=False, text="Lights")
        if context.scene.lights_controls:
            # Button to toggle all suns
            row = layout.row()
            row.operator("object.toggle_suns", text="Toggle All Suns")

            # Button to hide all suns
            row = layout.row()
            row.operator("object.hide_suns", text="Hide All Suns")

            # Checkboxes to toggle individual suns in three rows
            sun_pairs = [("Front", "Back"), ("Left", "Right"), ("Top", "Bottom")]
            for pair in sun_pairs:
                row = layout.row()
                row.operator("object.hide_suns", text=pair[0]).sun_names = f"sun.{pair[0].lower()}"
                row.operator("object.hide_suns", text=pair[1]).sun_names = f"sun.{pair[1].lower()}"
            layout = self.layout
            layout.prop(context.scene, "sun_strength", slider=True)
            layout.operator("object.update_sun_strength", text="Update Sun Strength")




        layout.prop(camera_controls, "expanded", icon="TRIA_DOWN" if camera_controls.expanded else "TRIA_RIGHT", emboss=False)
        if camera_controls.expanded:
            layout.operator("object.toggle_cameras", text="Toggle Cameras")
            layout.operator("object.hide_cameras", text="Hide Cameras")

            # Centered "View & Render Settings" text
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="View & Render Settings", icon='NONE')

            # Camera distance control
            row = layout.row()
            row.label(text="Distance:")
            row.prop(context.scene, "place_cameras_distance", text="")

            # Camera width and height controls
            row = layout.row()
            row.label(text="Width:")
            row.prop(camera_controls, "camera_width", text="")
            row = layout.row()
            row.label(text="Height:")
            row.prop(camera_controls, "camera_height", text="")

            # Focal length control
            row = layout.row()
            row.label(text="Focal Length:")
            row.prop(camera_controls, "focal_length", text="")
            
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Camera Preview", icon='NONE')
            # Buttons to set the view to different angles

            # Row for Front & Back buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Front").angle = "Front"
            row.operator("object.set_camera_view", text="Back").angle = "Back"

            # Row for Left & Right buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Left").angle = "Left"
            row.operator("object.set_camera_view", text="Right").angle = "Right"

            # Row for Top & Bottom buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Top").angle = "Top"
            row.operator("object.set_camera_view", text="Bottom").angle = "Bottom"

            # Create a 3x2 grid layout for cameras to render
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Cameras to Render", icon='NONE')
            grid = layout.grid_flow(row_major=True, columns=2, even_columns=True)
            grid.prop(camera_controls, "render_camera_top")
            grid.prop(camera_controls, "render_camera_bottom")
            grid.prop(camera_controls, "render_camera_right")
            grid.prop(camera_controls, "render_camera_left")
            grid.prop(camera_controls, "render_camera_front")
            grid.prop(camera_controls, "render_camera_back")

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

            # Centered "Render Directory" text
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Render Directory", icon='NONE')

            # Render directory selection
            layout.prop(context.scene, "render_output_directory", text="")

            layout.operator("object.render_all_cameras", text="Render Selected Cameras").camera_names = camera_names_str


        export_controls_property = context.scene.export_controls_property  # Replace with the correct attribute name if needed
        layout.prop(export_controls_property, "export_controls", icon="TRIA_DOWN" if export_controls_property.export_controls else "TRIA_RIGHT", emboss=False, text="3D Export")
        if export_controls_property.export_controls:  # Use the property from the property group
            
            # Row for the user to specify the export directory
            row = layout.row()
            row.prop(context.scene, "export_directory", text="Export Directory")
            
            # Dropdown for selecting the export format
            row = layout.row()
            row.prop(context.scene, "export_format", text="File Format")
            
            # Button to trigger the export
            row = layout.row()
            row.operator("object.export_active_object", text="Export Active Object")



        layout.prop(segmentation_controls_property, "segmentation_controls", icon="TRIA_DOWN" if segmentation_controls_property.segmentation_controls else "TRIA_RIGHT", emboss=False, text="Segmentation / Vertex Groups")
        if segmentation_controls_property.segmentation_controls:  # Use the property from the property group
            row = layout.row()
            row.template_list("MESH_UL_vgroups", "", obj, "vertex_groups", obj.vertex_groups, "active_index", rows=2)

            col = row.column(align=True)
            col.operator("object.vertex_group_add", icon='ADD', text="")
            col.operator("object.vertex_group_remove", icon='REMOVE', text="").all = False
            col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")
            col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            row = layout.row()
            row.operator("object.vertex_group_assign", text="Assign")
            row.operator("object.vertex_group_remove_from", text="Remove")
            row = layout.row()
            row.operator("object.vertex_group_select", text="Select")
            row.operator("object.vertex_group_deselect", text="Deselect")
            
            # Add a button to save vertex groups to CSV
            row = layout.row()
            row.operator("object.save_vertex_groups_to_csv", text="Save Vertex Groups to CSV").csv_file_path = context.scene.csv_file_path_save
            
            # Add a row for the user to specify the CSV file path for saving vertex groups
            row = layout.row()
            row.prop(context.scene, "csv_file_path_save", text="")

            # Add a button to load vertex groups from CSV
            row = layout.row()
            row.operator("object.load_vertex_groups_from_csv", text="Load Vertex Groups from CSV").csv_file_path = context.scene.csv_file_path_load

            # Add a row for the user to specify the CSV file path for loading vertex groups
            row = layout.row()
            row.prop(context.scene, "csv_file_path_load", text="")

            layout = self.layout
            
        layout.operator("object.export_settings")
        layout.operator("object.delete_all_objects", text="Delete All Objects")


def register():
    
    bpy.utils.register_class(DeleteAllObjectsOperator)
    bpy.utils.register_class(ExportControlsPropertyGroup)
    bpy.types.Scene.export_controls_property = bpy.props.PointerProperty(type=ExportControlsPropertyGroup)
    bpy.utils.register_class(ExportActiveObjectOperator)
    bpy.types.Scene.export_directory = bpy.props.StringProperty(
        name="Export Directory",
        description="Directory to export the 3D object",
      default="",
        subtype='DIR_PATH'
    )

    bpy.types.Scene.export_format = bpy.props.EnumProperty(
        name="Export Format",
        items=[('.obj', '.OBJ', 'Wavefront OBJ file format'), 
               ('.fbx', '.FBX', 'Autodesk FBX file format')],
        default='.obj'
    )

    bpy.utils.register_class(ExecuteWithSelectedCSVRowOperator)
    bpy.utils.register_class(CSVLabelProperties)
    bpy.types.Scene.csv_label_props = bpy.props.PointerProperty(type=CSVLabelProperties)
    bpy.utils.register_class(ImportCSVOperator)
    bpy.types.Scene.csv_file_path = bpy.props.StringProperty(
        name="CSV File Path",
        description="Path to the CSV file",
        default="",
        subtype='FILE_PATH'
    )
    bpy.types.Scene.csv_labels = bpy.props.StringProperty(
        name="CSV Labels",
        description="Labels imported from CSV",
        update=lambda self, context: setattr(
            bpy.types.Scene,
            'csv_label_enum',
            bpy.props.EnumProperty(
                items=[(str(i), name, name) for i, name in enumerate(self['csv_labels'])],
                name="CSV Labels"
            )
        )
    )
    bpy.utils.register_class(OpenMeshFunctionFileBrowserOperator)
    bpy.utils.register_class(ImportMakeMeshFunctionPathOperator)
    bpy.utils.register_class(ExecuteStoredFunctionOperator)
    bpy.types.Scene.make_mesh_function_path = bpy.props.StringProperty(
        name="Make Mesh Function Path",
        description="File path for the make_mesh function",
        default="",
    )
    bpy.utils.register_class(ImportBackgroundImageOperator)
    bpy.utils.register_class(ExportSettingsOperator)
    bpy.utils.register_class(WorldBackgroundControls)
    bpy.types.Scene.world_background_controls = bpy.props.PointerProperty(type=WorldBackgroundControls)
    bpy.utils.register_class(ChangeWorldBackgroundColor)
    bpy.utils.register_class(ToggleCamerasOperator)
    bpy.utils.register_class(TraitBlenderPanel)
    bpy.utils.register_class(CameraControls)
    bpy.utils.register_class(HideCamerasOperator)
    bpy.utils.register_class(SelectRenderDirectoryOperator)
    bpy.utils.register_class(RenderAllCamerasOperator)
    bpy.utils.register_class(ToggleBackgroundPlanesOperator)
    bpy.utils.register_class(ScaleBackgroundPlanesOperator)
    bpy.utils.register_class(HideBackgroundPlanesOperator)
    bpy.utils.register_class(SegmentationControls)
    bpy.utils.register_class(SegmentationControlsProperty)
    bpy.utils.register_class(SaveVertexGroupsToCSVOperator)
    bpy.utils.register_class(LoadVertexGroupsFromCSVOperator)
    bpy.utils.register_class(ToggleSunsOperator)
    bpy.utils.register_class(HideSunsOperator)
    bpy.utils.register_class(SunControlsPanel)
    bpy.utils.register_class(SetCameraViewOperator)
    bpy.utils.register_class(BackgroundControls)
    bpy.types.Scene.background_controls = bpy.props.PointerProperty(type=BackgroundControls)
    bpy.utils.register_class(CallUpdateBackgroundPlaneDistanceOperator)
    bpy.types.Scene.segmentation_controls_property = bpy.props.PointerProperty(type=SegmentationControlsProperty)
    bpy.types.Scene.lights_controls = bpy.props.BoolProperty(default=False)
    bpy.utils.register_class(SunControls)
    bpy.types.Scene.sun_controls = bpy.props.PointerProperty(type=SunControls)
    bpy.types.Scene.sun_lamp_controls = bpy.props.BoolProperty(name="Sun Lamp Controls", default=False)
    bpy.utils.register_class(UpdateSunStrengthOperator)
    bpy.types.Scene.sun_strength = bpy.props.FloatProperty(
        name="Sun Strength",
        description="Strength of the sun lamps",
        default=1.0,
        min=0.0,
        max=10.0
    )
    bpy.types.Scene.csv_file_path_save = bpy.props.StringProperty(
        name="CSV File Path to Save",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.csv_file_path_load = bpy.props.StringProperty(
        name="CSV File Path to Load",
        subtype='FILE_PATH'
    )


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
        description="Distance of the background planes from the active object",
        update=update_background_plane_distance  # This will call the function whenever the property changes
    )

    
    bpy.types.Scene.render_output_directory = bpy.props.StringProperty(
        name="Render Output Directory",
        description="Directory to save the renders",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
    )
    
    bpy.types.Scene.make_mesh_function_path = bpy.props.StringProperty(
        name="Make Mesh Function Path",
        description="Path to the Python file containing the mesh-making function",
        default="",
        subtype='DIR_PATH'
    )


    bpy.types.Scene.mesh_generation_controls = bpy.props.BoolProperty(
        name="Mesh Generation Controls",
        description="Expand/Collapse Mesh Generation Controls",
        default=False
    )


    
    bpy.app.handlers.depsgraph_update_post.append(delete_cameras_on_mesh_deletion)
    
def unregister():
    
    bpy.utils.unregister_class(DeleteAllObjectsOperator)
    del bpy.types.Scene.export_controls_property
    bpy.utils.unregister_class(ExportControlsPropertyGroup)
    bpy.utils.unregister_class(ExportActiveObjectOperator)
    del bpy.types.Scene.export_directory
    del bpy.types.Scene.export_format
    bpy.utils.unregister_class(ExecuteWithSelectedCSVRowOperator)
    bpy.utils.unregister_class(CSVLabelProperties)
    del bpy.types.Scene.csv_label_props
    bpy.utils.unregister_class(ImportCSVOperator)
    del bpy.types.Scene.csv_file_path
    del bpy.types.Scene.csv_labels
    if hasattr(bpy.types.Scene, 'csv_label_enum'):
        del bpy.types.Scene.csv_label_enum
    bpy.utils.unregister_class(OpenMeshFunctionFileBrowserOperator)
    bpy.utils.unregister_class(ExecuteStoredFunctionOperator)
    bpy.utils.unregister_class(ImportMakeMeshFunctionPathOperator)
    del bpy.types.Scene.make_mesh_function_path
    bpy.utils.unregister_class(ImportMakeMeshFunctionOperator)
    bpy.utils.unregister_class(ImportBackgroundImageOperator)
    bpy.utils.unregister_class(ExportSettingsOperator)
    bpy.utils.unregister_class(WorldBackgroundControls)
    del bpy.types.Scene.world_background_controls
    bpy.utils.unregister_class(ToggleCamerasOperator)
    bpy.utils.unregister_class(TraitBlenderPanel)
    bpy.utils.unregister_class(CameraControls)
    bpy.utils.unregister_class(HideCamerasOperator)
    bpy.utils.unregister_class(SelectRenderDirectoryOperator)
    bpy.utils.unregister_class(RenderAllCamerasOperator)
    bpy.utils.unregister_class(ToggleBackgroundPlanesOperator)
    bpy.utils.unregister_class(ScaleBackgroundPlanesOperator)
    bpy.utils.unregister_class(HideBackgroundPlanesOperator)
    bpy.utils.unregister_class(SegmentationControlsProperty)
    bpy.utils.unregister_class(ToggleSunsOperator)
    bpy.utils.unregister_class(HideSunsOperator)
    bpy.utils.unregister_class(SunControlsPanel)
    bpy.utils.unregister_class(LoadVertexGroupsFromCSVOperator)
    bpy.utils.unregister_class(SaveVertexGroupsToCSVOperator)
    bpy.utils.unregister_class(SetCameraViewOperator)
    bpy.utils.unregister_class(ChangeBackgroundColor)
    bpy.utils.unregister_class(BackgroundControls)
    del bpy.types.Scene.background_controls
    bpy.utils.unregister_class(CallUpdateBackgroundPlaneDistanceOperator)
    del bpy.types.Scene.segmentation_controls_property
    del bpy.types.Scene.lights_controls
    bpy.utils.unregister_class(SunControls)
    del bpy.types.Scene.sun_controls
    bpy.utils.unregister_class(UpdateSunStrengthOperator)
    del bpy.types.Scene.sun_strength


    bpy.utils.unregister_class(ImportBackgroundImageOperator)
    bpy.utils.unregister_class(BackgroundControls)
    del bpy.types.Scene.background_controls
    del bpy.types.Scene.background_image_reference
    
    bpy.utils.unregister_class(CreateBackgroundImageMeshOperator)
    bpy.types.VIEW3D_MT_mesh_add.remove(mesh_menu_func)
 
    del bpy.types.Scene.traitblender_settings
    del bpy.types.Scene.place_cameras_distance
    del bpy.types.Scene.camera_controls
    del bpy.types.Scene.render_output_directory

    
    
    bpy.app.handlers.depsgraph_update_post.remove(delete_cameras_on_mesh_deletion)

if __name__ == "__main__":
    register()
    
    # bpy.ops.object.select_all(action='SELECT')
    # bpy.ops.object.delete()

