import bpy
import random
import time
import json
import os

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
                    elif time.time() - self.first_selected_time >= 2.0:  # 2 seconds have passed
                        print([v.index for v in selected_vertices])  # Print the indices of the selected vertices
                        stretch_factor = random.uniform(0.95, 1.1)  # Random stretch factor between 1.1 and 1.5
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

        # Load the active mesh from the JSON file
        try:
            with open("../data/state/active_mesh.json", "r") as f:
                data = json.load(f)
                mesh_path = data["active_mesh"][0]
                bpy.ops.import_scene.obj(filepath=mesh_path)
        except Exception as e:
            print("Failed to load mesh from JSON file. Error:", e)
            # Fall back to adding a Suzanne monkey mesh
            bpy.ops.mesh.primitive_monkey_add()
            context.object.name = "Suzanne"

        context.window_manager.modal_handler_add(self)
        context.window_manager.event_timer_add(1.0, window=context.window)  # Change timer to 1 seconds
        return {'RUNNING_MODAL'}

bpy.utils.register_class(ModalOperator)
bpy.ops.object.modal_operator('INVOKE_DEFAULT')
