import numpy as np
import bpy

def generate_and_mesh_snail(label='snail', W=7, T=1.5, r_c=0.006, y_0=0, radius=0.0025, 
                            n_points=500, n_circles=1000, n_rotations=8*np.pi, color1="#FFFFFF", 
                            color2="#000000", Fac=0.720):
    
    def translate_point(theta, r_0, y_0, W, T, n_points):
        r_theta = r_0 * (W ** (theta / (2 * np.pi)))
        y_theta = y_0 * (W ** (theta / (2 * np.pi))) + r_c * (T * (W ** (theta / (2 * np.pi)) - 1))
        theta = np.full(n_points, theta)
        return (theta, r_theta, y_theta)

    def generate_circle_points(r_c, radius, n):
        angle_increment = 2 * np.pi / n
        x_coords = np.zeros(n)
        y_coords = np.zeros(n)
        
        for i in range(n):
            theta = i * angle_increment
            x_coords[i] = r_c + radius * np.cos(theta)
            y_coords[i] = radius * np.sin(theta)
        
        return x_coords, y_coords

    def cylindrical_to_cartesian(cylindrical_matrices):
        cartesian_matrices = []
        
        for theta_values, r_values, y_values in cylindrical_matrices:
            x_values = r_values * np.cos(theta_values)
            y_values_cartesian = r_values * np.sin(theta_values)
            z_values = y_values  
            cartesian_matrix = np.array([x_values, y_values_cartesian, z_values])
            cartesian_matrices.append(cartesian_matrix)
        
        return np.array(cartesian_matrices)

    r_0s, y_0s = generate_circle_points(r_c, radius, n_points)

    points = np.array([translate_point(angle, r_0s, y_0s, W, T, n_points) 
                       for angle in np.linspace(0, n_rotations, num=n_circles)])

    cartesian_matrices = cylindrical_to_cartesian(points)

    # Clear mesh objects in the scene
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Initialize empty lists for vertices and faces
    vertices = []
    faces = []

    # Populate vertices list
    for circle in cartesian_matrices:
        for x, y, z in zip(circle[0], circle[1], circle[2]):
            vertices.append((x, y, z))

    # Populate faces list
    n = len(cartesian_matrices[0][0])

    for i in range(len(cartesian_matrices) - 1):
        for j in range(n):
            idx1 = i * n + j
            idx2 = i * n + (j + 1) % n
            idx3 = (i + 1) * n + (j + 1) % n
            idx4 = (i + 1) * n + j
            faces.append((idx1, idx2, idx3, idx4))

    # Create new mesh and link it to scene
    mesh = bpy.data.meshes.new(name=label + "_Mesh")
    obj = bpy.data.objects.new(label, mesh)

    col = bpy.data.collections.get("Collection")
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Construct the mesh
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)


    # Create a new material
    mat = bpy.data.materials.new(name=label+"_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    # Create a new material
    mat = bpy.data.materials.new(name=f"{label}_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear default nodes
    for node in nodes:
        nodes.remove(node)

    # Add Principled BSDF shader node
    shader_node = nodes.new('ShaderNodeBsdfPrincipled')

    # Add Material Output node
    material_output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(shader_node.outputs["BSDF"], material_output.inputs["Surface"])

    # Add Magic Texture node
    magic_texture = nodes.new('ShaderNodeTexMagic')

    # Add ColorRamp node
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.color_ramp.interpolation = 'LINEAR'
    color_ramp.color_ramp.elements[0].color = tuple(int(color1.lstrip('#')[i:i+2], 16) / 255 for i in (0, 2, 4)) + (1,)
    color_ramp.color_ramp.elements[1].color = tuple(int(color2.lstrip('#')[i:i+2], 16) / 255 for i in (0, 2, 4)) + (1,)
    color_ramp.inputs[0].default_value = Fac  # Default value for 'Fac'

    # Connect Magic Texture to ColorRamp
    mat.node_tree.links.new(magic_texture.outputs["Color"], color_ramp.inputs[0])

    # Connect ColorRamp to Principled BSDF
    mat.node_tree.links.new(color_ramp.outputs["Color"], shader_node.inputs["Base Color"])

    # Assign the material to the object
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

    # Make sure the object is active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Set the origin to the center of mass
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')

    # Rotate the object 180 degrees about its local X-axis
    obj.rotation_euler[0] = np.pi  # np.pi is 180 degrees in radians

    # Update the scene
    bpy.context.view_layer.update()


generate_and_mesh_snail(label='snail', W=2.5, T=0, r_c=0.06, y_0=0, radius=0.06, 
                            n_points=50, n_circles=1000, n_rotations=8*np.pi, color1="#000000",
                            color2="#000000", Fac=1)