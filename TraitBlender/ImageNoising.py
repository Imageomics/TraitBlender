
import numpy as np
import bpy

class RandomCamerasRotationOperator(bpy.types.Operator):
    """Randomly rotate cameras within specified normal distribution"""
    bl_idname = "object.random_cameras_rotation"
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
