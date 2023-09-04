class DeleteAllObjectsOperator(bpy.types.Operator):
    bl_idname = "object.delete_all_objects"
    bl_label = "Delete All Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Make all objects visible and select them
        for obj in bpy.data.objects:
            obj.hide_viewport = False  # Make object visible
            obj.hide_set(False)  # Unhide the object
            obj.select_set(True)  # Select the object
        
        # Delete the objects
        bpy.ops.object.delete()
        
        return {'FINISHED'}