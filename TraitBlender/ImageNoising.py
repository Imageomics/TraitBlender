
import numpy as np
import bpy
import random

class RandomCamerasRotationOperator(bpy.types.Operator):
    """Randomly rotate cameras within specified normal distribution"""
    bl_idname = "object.randomize_camera_rotation"
    bl_label = "Random Cameras Rotation"
    bl_options = {'REGISTER', 'UNDO'}

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
            
            x_rotation = np.random.normal(scene.x_mu, scene.x_sd)
            y_rotation = np.random.normal(scene.y_mu, scene.y_sd)
            z_rotation = np.random.normal(scene.z_mu, scene.z_sd)
            
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

    def execute(self, context):
        scene = context.scene
        random_distance = np.random.normal(scene.camera_distance_mu, scene.camera_distance_sd)
        scene.place_cameras_distance = random_distance
        self.report({'INFO'}, f"Camera distance randomized to: {random_distance:.2f}")
        return {'FINISHED'}
    


class RandomWorldBackgroundColor(bpy.types.Operator):
    """Randomize World Background Color"""
    bl_idname = "object.randomize_world_background_color"
    bl_label = "Randomize World Background Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        world_background_controls = scene.world_background_controls

        world_background_controls.red = np.clip(np.random.normal(scene.red_mu, scene.red_sd), 0, 1)
        world_background_controls.green = np.clip(np.random.normal(scene.green_mu, scene.green_sd), 0, 1)
        world_background_controls.blue = np.clip(np.random.normal(scene.blue_mu, scene.blue_sd), 0, 1)
        world_background_controls.alpha = np.clip(np.random.normal(scene.alpha_mu, scene.alpha_sd), 0, 1)

        bpy.ops.scene.change_background_color()
        
        return {'FINISHED'}
    

class RandomSunsHideOperator(bpy.types.Operator):
    """Hide a Random Number and Selection of Suns"""
    bl_idname = "object.randomize_suns_hide"
    bl_label = "Random Suns Hide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        old_object = context.view_layer.objects.active

        all_objects = set(obj.name for obj in bpy.data.objects)
        RandomSunsToggleOperator_names = ("sun.front", "sun.back", "sun.top",
                        "sun.bottom", "sun.left", "sun.right")
        
        present_suns = all_objects.intersection(RandomSunsToggleOperator_names)

        random_suns = random.sample(present_suns, np.random.randint(1, len(present_suns) + 1))
        random_suns_string = ",".join(random_suns)

        bpy.ops.object.hide_suns(sun_names=random_suns_string)

        context.view_layer.objects.active = old_object
        context.view_layer.update()

        self.report({'INFO'}, "Random hiding applied to suns.")
        return {'FINISHED'}


class RandomizationControls(bpy.types.PropertyGroup):
    expanded: bpy.props.BoolProperty(
        name="Expand Randomization Controls",
        description="Toggle the display of randomization controls",
        default=False
    )