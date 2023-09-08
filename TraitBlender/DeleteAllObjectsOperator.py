import bpy

class DeleteAllObjectsOperator(bpy.types.Operator):
    """
    This operator deletes all objects in the Blender scene.
    All objects are first made visible and selected before deletion.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        bl_options (set): Operator options.
    """
    bl_idname = "object.delete_all_objects"
    bl_label = "Delete All Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Executes the operator, making all objects visible, selecting them, and then deleting them.
        
        Parameters:
            context: Blender's context object.
        
        Returns:
            dict: A dictionary indicating the execution status.
        """
        # Switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Make all objects visible and select them
        for obj in bpy.data.objects:
            obj.hide_viewport = False  # Make object visible
            obj.hide_set(False)  # Unhide the object
            obj.select_set(True)  # Select the object
        
        # Delete the objects
        bpy.ops.object.delete()
        
        return {'FINISHED'}
