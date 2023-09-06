import bpy 
import json
import types

bpy.types.Scene.mesh_generation_controls = bpy.props.BoolProperty(name="Mesh Generation Controls", default=False)

###Functions

###Property Groups
class ExportControlsPropertyGroup(bpy.types.PropertyGroup):
    """
    This property group controls the visibility of the 3D Export options in the Blender UI.
    
    Attributes:
        export_controls (BoolProperty): A boolean property to toggle the visibility of export controls.
    """
    export_controls: bpy.props.BoolProperty(
        name="Show/Hide",
        description="Show or hide the 3D Export options",
        default=False
    )

###Operators
class ExecuteStoredFunctionOperator(bpy.types.Operator):
    """
    This operator executes a Python function stored in a file. The file path is fetched from the Blender scene properties.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        json_args (StringProperty): A JSON-formatted string that represents the arguments for the function to execute.
    """
    bl_idname = "object.execute_stored_function"
    bl_label = "Execute Stored Function"

    # A string property to accept JSON-formatted arguments
    json_args: bpy.props.StringProperty(name="JSON Arguments")

    def execute(self, context):
        """
        Executes the operator, running the stored function with the given arguments.
        
        Parameters:
            context: Blender's context object.
        
        Returns:
            dict: A dictionary indicating the execution status.
        """
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


class ImportMakeMeshFunctionPathOperator(bpy.types.Operator):
    """
    This operator imports the file path for the make_mesh function from the user.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        make_mesh_function_path (StringProperty): A property that stores the path to the make_mesh function.
    """
    bl_idname = "object.import_make_mesh_function_path"
    bl_label = "Import Make Mesh Function Path"

    make_mesh_function_path: bpy.props.StringProperty(name="Make Mesh Function Path", subtype="FILE_PATH")

    def execute(self, context):
        """
        Executes the operator, importing the make_mesh function path into the scene property.

        Parameters:
            context: Blender's context object.

        Returns:
            dict: A dictionary indicating the execution status.
        """
        context.scene.make_mesh_function_path = self.make_mesh_function_path
        return {'FINISHED'}
    

class OpenMeshFunctionFileBrowserOperator(bpy.types.Operator):
    """
    This operator opens a file browser for the user to select the make_mesh function file.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        filepath (StringProperty): A property that stores the selected filepath.
    """
    bl_idname = "object.open_mesh_function_file_browser"
    bl_label = "Invoke File Browser"
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        """
        Executes the operator, setting the selected filepath to the make_mesh function path in the scene property.

        Parameters:
            context: Blender's context object.

        Returns:
            dict: A dictionary indicating the execution status.
        """
        context.scene.make_mesh_function_path = self.filepath
        return {'FINISHED'}
    
    def invoke(self, context, event):
        """
        Invokes the file browser for filepath selection.

        Parameters:
            context: Blender's context object.
            event: Blender's event object.

        Returns:
            dict: A dictionary indicating the execution status.
        """
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    
###Panels








