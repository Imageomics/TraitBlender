import bpy
import math

def make_cube_cylinder(label="", width_x=10, width_y=1, width_z=10, cube_color_hex="#FFFFFF", cylinder_color_hex="#000000", cylinder_radius=2.5):
    # Clear all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create a cube
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cube = bpy.context.object
    cube.scale.x = width_x
    cube.scale.y = width_y
    cube.scale.z = width_z

    # Create a new material for the cube
    mat_cube = bpy.data.materials.new(name="Cube_Material")
    r, g, b = tuple(int(cube_color_hex.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    mat_cube.diffuse_color = (r, g, b, 1)

    # Assign the material to the cube
    if len(cube.data.materials) == 0:
        cube.data.materials.append(mat_cube)
    else:
        cube.data.materials[0] = mat_cube

    # Create a cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=cylinder_radius, depth=width_y, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    cylinder = bpy.context.object
    cylinder.rotation_euler.x = math.radians(90)  # Rotate 90 degrees on the X-axis to make it parallel to the cube's XZ face

    # Create a new material for the cylinder
    mat_cylinder = bpy.data.materials.new(name="Cylinder_Material")
    r, g, b = tuple(int(cylinder_color_hex.lstrip('#')[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    mat_cylinder.diffuse_color = (r, g, b, 1)

    # Assign the material to the cylinder
    if len(cylinder.data.materials) == 0:
        cylinder.data.materials.append(mat_cylinder)
    else:
        cylinder.data.materials[0] = mat_cylinder

    # Add a Boolean modifier to the cube
    bpy.context.view_layer.objects.active = cube  # Set the cube as the active object
    bpy.ops.object.modifier_add(type='BOOLEAN')
    mod = cube.modifiers[-1]  # Get the last added modifier
    mod.operation = 'DIFFERENCE'
    mod.use_self = False
    mod.object = cylinder  # Set the cylinder as the object to subtract

    # Apply the modifier
    bpy.ops.object.modifier_apply({"object": cube}, modifier=mod.name)

    # Join the cube and cylinder into a single object
    cube.select_set(True)
    cylinder.select_set(True)
    bpy.context.view_layer.objects.active = cube
    bpy.ops.object.join()
    
    cube.name = label
