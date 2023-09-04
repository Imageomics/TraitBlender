import bpy 
import json
import types

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
