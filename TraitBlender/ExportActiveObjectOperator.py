import bpy
import os

class ExportActiveObjectOperator(bpy.types.Operator):
    """
    This operator exports the active object in the Blender scene to a specified format.
    It can export to .obj and .fbx formats.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
    """
    bl_idname = "object.export_active_object"
    bl_label = "Export Active Object"

    @staticmethod
    def export_active_object(filepath, format=".obj"):
        """
        Exports the active object in the scene to the specified file path and format.
        
        Parameters:
            filepath (str): The directory where the exported file will be saved.
            format (str): The format to export the object. Supported formats are ".obj" and ".fbx".

        Returns:
            None
        """
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
        """
        Executes the operator, exporting the active object based on the scene's export directory and format.
        
        Parameters:
            context: Blender's context object.
        
        Returns:
            dict: A dictionary indicating the execution status.
        """
        export_dir = context.scene.export_directory
        export_format = context.scene.export_format
        if not export_dir:
            self.report({'ERROR'}, "Please select an export directory first.")
            return {'CANCELLED'}
        self.export_active_object(export_dir, export_format)
        return {'FINISHED'}
