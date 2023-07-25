import bpy
import random
import time

class ModalOperator(bpy.types.Operator):
    bl_idname = "object.modal_operator"
    bl_label = "Modal Operator"

    first_selected_time = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            obj = context.object
            if obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH':
                bpy.ops.object.mode_set(mode='OBJECT')
                selected_vertices = [v for v in obj.data.vertices if v.select]
                if selected_vertices:
                    if self.first_selected_time is None:
                        self.first_selected_time = time.time()
                    elif time.time() - self.first_selected_time >= 3.0:  # 3 seconds have passed
                        print([v.index for v in selected_vertices])  # Print the indices of the selected vertices
                        stretch_factor = random.uniform(1.1, 1.5)  # Random stretch factor between 1.1 and 1.5
                        for v in selected_vertices:
                            v.co *= stretch_factor  # Stretch the vertex
                else:
                    self.first_selected_time = None
                bpy.ops.object.mode_set(mode='EDIT')

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # Ensure we are in Object Mode
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Delete all objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # Add a Suzanne monkey mesh
        bpy.ops.mesh.primitive_monkey_add()
        context.object.name = "Suzanne"

        context.window_manager.modal_handler_add(self)
        context.window_manager.event_timer_add(5.0, window=context.window)  # Change timer to 5 seconds
        return {'RUNNING_MODAL'}

bpy.utils.register_class(ModalOperator)
bpy.ops.object.modal_operator('INVOKE_DEFAULT')
