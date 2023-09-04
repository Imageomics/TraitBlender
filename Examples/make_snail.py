import bpy
import math

def make_snail(label="", coil_fatness=.99, face_height=0.25, degree_of_coiling=12):
    # Delete all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Add a circle mesh
    bpy.ops.mesh.primitive_circle_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    circle_object = bpy.context.active_object

    # Offset the circle by the given value in the X-axis
    circle_object.location.x = -1

    # Add an array modifier to the circle
    array_modifier = circle_object.modifiers.new(name="Array", type='ARRAY')
    array_modifier.count = 1000
    array_modifier.use_relative_offset = False
    array_modifier.use_constant_offset = True
    array_modifier.constant_offset_displace[0] = 0
    array_modifier.constant_offset_displace[2] = face_height

    # Add an Empty object with Plain Axes
    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(-0.96, 0, 0))
    empty_object = bpy.context.object
    empty_object.name = "Empty"
    empty_object.rotation_euler[0] = math.radians(degree_of_coiling)
    empty_object.scale = (0.99, coil_fatness, 0.99)

    # Update the array modifier to use the Empty object
    array_modifier.use_object_offset = True
    array_modifier.offset_object = empty_object

    # Make the circle the active object
    bpy.context.view_layer.objects.active = circle_object
    circle_object.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Array")

    # Enter edit mode, select all edges, and bridge edge loops
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bridge_edge_loops()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()

    # Set the origin to the center of mass
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
    
    # Move the center of the object to the global origin
    circle_object.location = (0, 0, 0)

    # Set the name to the label
    circle_object.name = label

    # Create a material and set its diffuse color
    material = bpy.data.materials.new(name="Snail_Material")
    material.diffuse_color = (0.761, 0.725, 0.098, 1)  # RGBA for #c7c26b
    circle_object.data.materials.append(material)

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Select and delete only the Empty object
    bpy.data.objects['Empty'].select_set(True)
    bpy.ops.object.delete()
