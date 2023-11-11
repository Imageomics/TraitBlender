import numpy as np
import bpy

def make_contreras_snail(label="snail", 
                         b = .1, d = 5, z = 0, a = 1, phi = 0, psi = 0, 
                         c_depth=0.3, c_n = 12, n_depth = 0.5, n = 4, 
                         t = 20, time_step = .25/6, 
                         points_in_circle=20, length = 1, smooth=False,
                         color="#000000"):
    
    
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    
    t_values = np.arange(0, t, time_step)
    theta_values = np.arange(0, 2 * np.pi, np.pi / points_in_circle)
    
    
    # Define the gamma function
    def gamma(t, b, d, z):
        return np.array([d * np.sin(t), d * np.cos(t), z]) * np.exp(b * t)

    # Define the T function
    def T(t, b, d, z):
        numerator = np.array([d * (b * np.sin(t) + np.cos(t)), d * (b * np.cos(t) - np.sin(t)), -b * z])
        denominator = np.sqrt(((b**2) + 1) * (d**2) + (b**2) * (z**2))
        return numerator / denominator

    # Define the N function
    def N(t, b):
        numerator = np.array([b * np.cos(t) - np.sin(t), -b * np.sin(t) - np.cos(t), 0])
        denominator = np.sqrt((b**2) + 1)
        return numerator / denominator

    # Define the B function
    def B(t, b, d, z):
        numerator = np.array([b * z * (b * np.sin(t) + np.cos(t)), b * z * (b * np.cos(t) - np.sin(t)), d * ((b**2) + 1)])
        denominator = np.sqrt(((b**2) + 1) * (((b**2) + 1) * (d**2) + (b**2) * (z**2)))
        return numerator / denominator

    # Define the R_b function
    def R_b(psi):
        return np.array([[np.cos(psi), -np.sin(psi), 0],
                         [np.sin(psi), np.cos(psi), 0],
                         [0, 0, 1]])

    # Define the C function with the updated formula
    def C(t, theta, b, a, d, z, phi, psi, c_n, c_depth, n, n_depth):
        e_term = np.exp(b * t) - (1 / (t + 1))
        long_ribs = (1 + c_depth*np.sin(c_n * t))
        rotation_matrix = R_b(psi)
        modulation_n = (1 + (n_depth * np.sin(n * theta)))

        vector_N = ((a * np.sin(theta) * np.cos(phi)) + (np.cos(theta) * np.sin(phi))) * modulation_n * N(t, b)
        vector_B = ((a * np.sin(theta) * np.sin(phi)) - (np.cos(theta) * np.cos(phi))) * modulation_n * B(t, b, d, z)

        return long_ribs * e_term * np.dot(rotation_matrix, vector_N + vector_B)

    # Define the lambda function with the updated C function
    def lambda_(t, theta, b, d, z, a, phi, psi, c_n, c_depth, n, n_depth):
        return gamma(t, b, d, z) + C(t, theta, b, a, d, z, phi, psi, c_n, c_depth, n, n_depth)

    # the constant helps keep the float from overflowing when converting to blender
    points = np.array([[lambda_(t, theta, b, d, z, a, phi, psi, c_n, c_depth, n=n, n_depth=n_depth) for theta in theta_values] for t in t_values])

    # rescale the values to between 0 and 1 so it doesn't cause float overflow when converting to blender
    current_max = np.amax(points)
    current_min = np.amin(points)
    desired_max = 100
    desired_min = -100
    scale_factor = (desired_max - desired_min) / (current_max - current_min) if current_max != current_min else 1
    scaled_points = points * scale_factor
    translation = desired_min - np.amin(scaled_points)
    scaled_points += translation
    points = scaled_points
    new_max = np.amax(scaled_points)
    new_min = np.amin(scaled_points)



    print("Largest Value:", (current_max, new_max))
    print("Smallest Value:",(current_min, new_min))


    
    mesh = bpy.data.meshes.new(name="ShellMesh")
    obj = bpy.data.objects.new(label, mesh)

    # Link object to the scene
    bpy.context.collection.objects.link(obj)

    # Prepare mesh data
    vertices = points.reshape(-1, 3)  # Flatten the tensor to a list of vertices
    faces = []

    num_rings = len(points)
    points_per_ring = len(points[0])

    # Create faces
    for ring in range(num_rings - 1):
        for pt in range(points_per_ring):
            # Connect point 'pt' in ring 'ring' with the next point and the corresponding points in the next ring
            p1 = ring * points_per_ring + pt
            p2 = ring * points_per_ring + (pt + 1) % points_per_ring  # Wrap around to the first point
            p3 = (ring + 1) * points_per_ring + (pt + 1) % points_per_ring
            p4 = (ring + 1) * points_per_ring + pt

            faces.append((p1, p2, p3, p4))

    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    # Calculate the current max length along the x-axis
    x_coords = [vert.co.x for vert in mesh.vertices]
    x_length_current = max(x_coords) - min(x_coords)

    # Desired length along the x-axis (based on your 'length' parameter)
    length_desired = length

    # Calculate the scale factor
    scale_factor = length_desired / x_length_current if x_length_current != 0 else 1

    # Apply the scale to the mesh
    obj.scale.x *= scale_factor
    obj.scale.y *= scale_factor
    obj.scale.z *= scale_factor

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')

    # Move the object to the global origin
    obj.rotation_euler[1] = np.pi
    if smooth:
        # Set the object to be the active object
        bpy.context.view_layer.objects.active = obj

        # Select the object
        obj.select_set(True)

        # Apply smooth shading
        bpy.ops.object.shade_smooth()
        
    
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center="BOUNDS")
    obj.location = (0, 0, 0)
        
    color_hex = color.lstrip('#')
    color_rgb = tuple(int(color_hex[i:i+2], 16)/255 for i in (0, 2, 4))

    # Create a new material
    mat = bpy.data.materials.new(name="ShellMaterial")
    mat.diffuse_color = color_rgb + (1,)  # RGBA, A is the alpha (transparency)

    # Assign material to the object
    if obj.data.materials:
        # Object has materials, overwrite the first
        obj.data.materials[0] = mat
    else:
        # No materials on the object, append new
        obj.data.materials.append(mat)

    # Update the scene
    bpy.context.view_layer.update()

make_contreras_snail(label="snail", 
                         b = 5, d = 3, z = 2, a = 1, phi = 0, psi = 0, 
                         c_depth=0.3, c_n = 30, n_depth = 0.5, n = 0, 
                         t = 50, time_step = .25/5, 
                         points_in_circle=15, length = 1, smooth=True)