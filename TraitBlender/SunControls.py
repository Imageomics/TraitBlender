import bpy
from mathutils import Matrix, Vector

class SunControls(bpy.types.PropertyGroup):
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0)
    diffuse: bpy.props.FloatProperty(name="Diffuse", default=1.0, min=0.0, max=1.0)
    specular: bpy.props.FloatProperty(name="Specular", default=1.0, min=0.0, max=1.0)
    volume: bpy.props.FloatProperty(name="Volume", default=1.0, min=0.0, max=1.0)
    angle: bpy.props.FloatProperty(name="Angle", default=0.0, min=0.0, max=180.0)

class ToggleSunsOperator(bpy.types.Operator):
    bl_idname = "object.toggle_suns"
    bl_label = "Toggle Suns"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=10.0)

    def execute(self, context):
        # Get and store the original active object
        original_active_obj = context.active_object
        if original_active_obj is None:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        # Calculate the sun locations and names
        locations_and_names = [
            ((0, 0, self.distance), "sun.top"),
            ((0, 0, -self.distance), "sun.bottom"),
            ((self.distance, 0, 0), "sun.right"),
            ((-self.distance, 0, 0), "sun.left"),
            ((0, self.distance, 0), "sun.back"),
            ((0, -self.distance, 0), "sun.front"),
        ]

        # Check if the suns already exist
        suns_exist = all(bpy.data.objects.get(name) is not None for _, name in locations_and_names)

        if suns_exist:
            # Remove the suns
            for _, name in locations_and_names:
                sun = bpy.data.objects.get(name)
                if sun is not None:
                    bpy.data.objects.remove(sun)
        else:
            # Create the suns
            for location, name in locations_and_names:
                # Add the location of the active object to the location of the sun
                location = original_active_obj.location + Vector(location)
                bpy.ops.object.light_add(type='SUN', location=location)
                sun = context.active_object

                # Set the sun name
                sun.name = name

                # Point the sun towards the active object
                direction = original_active_obj.location - sun.location
                sun.rotation_mode = 'QUATERNION'
                sun.rotation_quaternion = direction.to_track_quat('-Z', 'Y')

                # Deselect the new sun
                sun.select_set(False)

        # Restore the original active object
        context.view_layer.objects.active = original_active_obj

        return {'FINISHED'}




class HideSunsOperator(bpy.types.Operator):
    bl_idname = "object.hide_suns"
    bl_label = "Hide Suns"
    bl_options = {'REGISTER', 'UNDO'}

    sun_names: bpy.props.StringProperty(
        name="Sun Names",
        default="sun.top,sun.bottom,sun.right,sun.left,sun.front,sun.back"
    )

    def execute(self, context):
        # Split the sun names by comma
        sun_names_list = self.sun_names.split(',')

        # Check if the suns already exist and are visible
        suns_exist = all(bpy.data.objects.get(name) is not None for name in sun_names_list)
        suns_visible = all(not bpy.data.objects[name].hide_viewport for name in sun_names_list if bpy.data.objects.get(name) is not None)

        if suns_exist and suns_visible:
            # Hide the suns
            for name in sun_names_list:
                sun = bpy.data.objects.get(name)
                if sun is not None:
                    sun.hide_viewport = True
        elif suns_exist and not suns_visible:
            # Unhide the suns
            for name in sun_names_list:
                sun = bpy.data.objects.get(name)
                if sun is not None:
                    sun.hide_viewport = False

        return {'FINISHED'}

