
import numpy as np
import bpy

class RandomCamerasRotationOperator(bpy.types.Operator):
    """Randomly rotate cameras within specified normal distribution"""
    bl_idname = "object.randomize_camera_rotation"
    bl_label = "Random Cameras Rotation"
    bl_options = {'REGISTER', 'UNDO'}

    x_mu: bpy.props.FloatProperty(name="X Mean", default=0)
    x_sd: bpy.props.FloatProperty(name="X Std Dev", default=0)
    y_mu: bpy.props.FloatProperty(name="Y Mean", default=0)
    y_sd: bpy.props.FloatProperty(name="Y Std Dev", default=0)
    z_mu: bpy.props.FloatProperty(name="Z Mean", default=0)
    z_sd: bpy.props.FloatProperty(name="Z Std Dev", default=0)
    cameras: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)  # This should be populated with actual camera references

    def execute(self, context):
        scene = context.scene
        old_object = context.view_layer.objects.active

        all_objects = set(obj.name for obj in bpy.data.objects)
        camera_names = ("camera.front", "camera.back", "camera.top",
                        "camera.bottom", "camera.left", "camera.right")
        present_cameras = all_objects.intersection(camera_names)

        for camera_name in present_cameras:
            camera_object = bpy.data.objects[camera_name]
            camera_object.rotation_mode = "XYZ"
            
            x_rotation = np.random.normal(self.x_mu, self.x_sd)
            y_rotation = np.random.normal(self.y_mu, self.y_sd)
            z_rotation = np.random.normal(self.z_mu, self.z_sd)
            
            camera_object.rotation_euler[0] += x_rotation
            camera_object.rotation_euler[1] += y_rotation
            camera_object.rotation_euler[2] += z_rotation

        context.view_layer.objects.active = old_object
        context.view_layer.update()

        self.report({'INFO'}, "Random rotations applied to cameras.")
        return {'FINISHED'}


class RandomCamerasDistanceOperator(bpy.types.Operator):
    """Randomize Camera Distance"""
    bl_idname = "object.randomize_camera_distance"
    bl_label = "Randomize Camera Distance"
    bl_options = {'REGISTER', 'UNDO'}

    camera_distance_mu: bpy.props.FloatProperty(
        name="Mean Distance",
        description="Mean distance for the cameras",
        default=10.0
    )
    
    camera_distance_sd: bpy.props.FloatProperty(
        name="Std Dev Distance",
        description="Standard deviation of the distance for the cameras",
        default=0.0
    )

    def execute(self, context):
        # Calculate a random distance using a normal distribution
        random_distance = np.random.normal(self.camera_distance_mu, self.camera_distance_sd)
        
        # Set the calculated distance to the 'place_cameras_distance' property
        context.scene.place_cameras_distance = random_distance
        
        self.report({'INFO'}, f"Camera distance randomized to: {random_distance:.2f}")
        return {'FINISHED'}
    


class RandomWorldBackgroundColor(bpy.types.Operator):
    """Randomize World Background Color"""
    bl_idname = "object.randomize_world_background_color"
    bl_label = "Randomize World Background Color"
    
    red_mu: bpy.props.FloatProperty(name="Red Mean", default=1.0)
    red_sd: bpy.props.FloatProperty(name="Red Std Dev", default=0.0, min=0.0)
    green_mu: bpy.props.FloatProperty(name="Green Mean", default=1.0)
    green_sd: bpy.props.FloatProperty(name="Green Std Dev", default=0.0, min=0.0)
    blue_mu: bpy.props.FloatProperty(name="Blue Mean", default=1.0)
    blue_sd: bpy.props.FloatProperty(name="Blue Std Dev", default=0.0, min=0.0)
    alpha_mu: bpy.props.FloatProperty(name="Alpha Mean", default=1.0)
    alpha_sd: bpy.props.FloatProperty(name="Alpha Std Dev", default=0.0, min=0.0)

    def execute(self, context):
        # Access the background_controls property group
        world_background_controls = context.scene.world_background_controls
        
        # Generate random values from a normal distribution for each color component
        world_background_controls.red = np.clip(np.random.normal(self.red_mu, self.red_sd), 0, 1)
        world_background_controls.green = np.clip(np.random.normal(self.green_mu, self.green_sd), 0, 1)
        world_background_controls.blue = np.clip(np.random.normal(self.blue_mu, self.blue_sd), 0, 1)
        world_background_controls.alpha = np.clip(np.random.normal(self.alpha_mu, self.alpha_sd), 0, 1)
        
        # Call the function that updates the world background color
        bpy.ops.scene.change_background_color()
        
        return {'FINISHED'}