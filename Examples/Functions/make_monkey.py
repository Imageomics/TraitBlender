import bpy
import mathutils

def make_monkey(label="Suzanne", Jowl_Size=0, Dome_Size=0, Overall_Size=1, vertex_group_csv=None, ear_color=0):
    # Check if any object is selected; if not, set to 'OBJECT' mode
    if bpy.context.selected_objects:
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Delete all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


    # Add Suzanne monkey
    bpy.ops.mesh.primitive_monkey_add()

    # Rename the monkey object
    monkey = bpy.context.active_object
    monkey.name = label

    # Load vertex groups from CSV if provided
    if vertex_group_csv:
        bpy.ops.object.load_vertex_groups_from_csv(csv_file_path=vertex_group_csv)

    # Create new materials
    brown_mat = bpy.data.materials.new(name="Monkey_Material")
    brown_mat.use_nodes = True
    brown_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.4765625, 0.3359375, 0.2734375, 1)
    
    red_mat = bpy.data.materials.new(name="Red_Ear")
    red_mat.use_nodes = True
    red_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.890625, 0.0527344, 0.388672, 1)

    blue_mat = bpy.data.materials.new(name="Blue_Ears")
    blue_mat.use_nodes = True
    blue_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0980392, 0.266667, 0.878431, 1)

    # Assign materials to monkey
    monkey.data.materials.append(brown_mat)
    monkey.data.materials.append(red_mat)
    monkey.data.materials.append(blue_mat)

    # Set brown material as default for all faces
    for poly in monkey.data.polygons:
        poly.material_index = 0
    
    # Assign ear color based on ear_color parameter
    if ear_color != 0:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group="Ears")
        bpy.ops.object.vertex_group_select()

        if ear_color == 1:
            monkey.active_material_index = 1
        elif ear_color == 2:
            monkey.active_material_index = 2

        bpy.ops.object.material_slot_assign()
    bpy.ops.object.mode_set(mode='OBJECT')
