import bpy
from mathutils import Matrix, Vector


###Functions

###Property Groups

class SunControls(bpy.types.PropertyGroup):
    """
    Property group for controlling sun related attributes in Blender.

    Attributes:
        strength (FloatProperty): The strength of the sun light.
    """
    strength: bpy.props.FloatProperty(name="Strength", default=1.0, min=0.0)

### Operators

class HideSunsOperator(bpy.types.Operator):
    """
    This operator hides or unhides sun objects in the Blender scene.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        bl_options (set): Options for this operator.
        sun_names (StringProperty): Comma-separated names of sun objects to be hidden or unhidden.
    """
    bl_idname = "object.hide_suns"
    bl_label = "Hide Suns"
    bl_options = {'REGISTER', 'UNDO'}

    sun_names: bpy.props.StringProperty(
        name="Sun Names",
        default="sun.top,sun.bottom,sun.right,sun.left,sun.front,sun.back"
    )

    def execute(self, context):
        """
        Executes the operator, hiding or unhiding specified sun objects.

        Parameters:
            context: Blender's context object.

        Returns:
            dict: A dictionary indicating the execution status.
        """
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



class ToggleSunsOperator(bpy.types.Operator):
    """
    This operator toggles the presence of sun objects in the Blender scene.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        bl_options (set): Options for this operator.
        distance (FloatProperty): Distance from the active object to place the suns.
    """
    bl_idname = "object.toggle_suns"
    bl_label = "Toggle Suns"
    bl_options = {'REGISTER', 'UNDO'}

    distance: bpy.props.FloatProperty(name="Distance", default=10.0)

    def execute(self, context):
        """
        Executes the operator, either adding or removing specified sun objects.

        Parameters:
            context: Blender's context object.

        Returns:
            dict: A dictionary indicating the execution status.
        """
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


class UpdateSunStrengthOperator(bpy.types.Operator):
    """
    This operator updates the strength of sun objects in the Blender scene.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        bl_options (set): Options for this operator.
    """
    bl_idname = "object.update_sun_strength"
    bl_label = "Update Sun Strength"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Executes the operator, updating the strength of specified sun objects.

        Parameters:
            context: Blender's context object.

        Returns:
            dict: A dictionary indicating the execution status.
        """
        sun_names = ["sun.top", "sun.bottom", "sun.right", "sun.left", "sun.front", "sun.back"]

        for name in sun_names:
            sun = bpy.data.objects.get(name)
            if sun and sun.type == 'LIGHT':
                sun.data.energy = context.scene.sun_strength

        self.report({'INFO'}, "Sun strength updated successfully!")
        return {'FINISHED'}

###Panels
class SunControlsPanel(bpy.types.Panel):
    """
    This panel provides controls for managing sun objects in Blender's UI.

    Attributes:
        bl_label (str): The label for this panel.
        bl_idname (str): Blender's internal name for this panel.
        bl_space_type (str): The space where this panel appears.
        bl_region_type (str): The region where this panel appears.
        bl_category (str): The category where this panel appears.
        bl_context (str): The context in which this panel appears.
        bl_options (set): Options for this panel.
    """
    bl_label = "Lights"
    bl_idname = "OBJECT_PT_sun_controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'  
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        """
        Draws the UI elements for this panel.

        Parameters:
            context: Blender's context object.
        """
        layout = self.layout

        # Toggle Suns Button
        row = layout.row()
        row.operator("object.toggle_suns", text="Toggle Suns")

        # Hide/Unhide Suns Button
        row = layout.row()
        row.operator("object.hide_suns", text="Hide/Unhide Suns")


