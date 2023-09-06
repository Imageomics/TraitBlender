import bpy
import csv

###Functions

### Property Groups
class SegmentationControlsProperty(bpy.types.PropertyGroup):
    """
    Property group for controlling segmentation options in Blender.

    Attributes:
        expanded (BoolProperty): Whether the property group is expanded in the UI.
        segmentation_controls (BoolProperty): Placeholder for future segmentation controls.
    """
    expanded: bpy.props.BoolProperty(default=False)
    segmentation_controls: bpy.props.BoolProperty(default=False)


### Operators
class LoadVertexGroupsFromCSVOperator(bpy.types.Operator):
    """
    This operator loads vertex groups from a CSV file.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        bl_options (set): Options for this operator.
        csv_file_path (StringProperty): The path to the CSV file containing vertex group data.
    """
    bl_idname = "object.load_vertex_groups_from_csv"
    bl_label = "Load Vertex Groups from CSV"
    bl_options = {'REGISTER', 'UNDO'}

    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        subtype='FILE_PATH'
    )

    def execute(self, context):
        """
        Executes the operator, loading vertex groups from the specified CSV file.

        Parameters:
            context: Blender's context object.

        Returns:
            dict: A dictionary indicating the execution status.
        """
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object selected.")
            return {'CANCELLED'}
        
        obj.vertex_groups.clear()
        with open(self.csv_file_path, 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                vert_index, group_name, weight = int(row[0]), row[1], float(row[2])
                if group_name not in obj.vertex_groups:
                    obj.vertex_groups.new(name=group_name)
                obj.vertex_groups[group_name].add([vert_index], weight, 'REPLACE')

        return {'FINISHED'}


class SaveVertexGroupsToCSVOperator(bpy.types.Operator):
    """
    This operator saves vertex groups to a CSV file.

    Attributes:
        bl_idname (str): Blender's internal name for this operator.
        bl_label (str): The label for this operator.
        bl_options (set): Options for this operator.
        csv_file_path (StringProperty): The path to the CSV file for saving vertex group data.
    """
    bl_idname = "object.save_vertex_groups_to_csv"
    bl_label = "Save Vertex Groups to CSV"
    bl_options = {'REGISTER', 'UNDO'}

    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        subtype='FILE_PATH'
    )

    def execute(self, context):
        """
        Executes the operator, saving vertex groups to the specified CSV file.

        Parameters:
            context: Blender's context object.

        Returns:
            dict: A dictionary indicating the execution status.
        """
        obj = context.object
        if not obj:
            self.report({'ERROR'}, "No active object selected.")
            return {'CANCELLED'}
        
        with open(self.csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Vertex Index", "Group Name", "Weight"])
            for vert in obj.data.vertices:
                for group in vert.groups:
                    group_name = obj.vertex_groups[group.group].name
                    weight = group.weight
                    csvwriter.writerow([vert.index, group_name, weight])

        return {'FINISHED'}

### Panels
class SegmentationControls(bpy.types.Panel):
    """
    Panel for controlling segmentation options in Blender.

    Attributes:
        bl_label (str): The label for this panel.
        bl_idname (str): Blender's internal name for this panel.
        bl_space_type (str): The type of space where the panel appears.
        bl_region_type (str): The type of region where the panel appears.
        bl_context (str): The context in which the panel appears.
        bl_category (str): The category of the panel.
    """
    bl_label = "Segmentation Controls"
    bl_idname = "OBJECT_PT_segmentation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_category = "TraitBlender"

    def draw(self, context):
        """
        Draws the panel UI.

        Parameters:
            context: Blender's context object.
        """
        layout = self.layout
        obj = context.object

        # Draw the vertex group controls
        row = layout.row()
        row.template_list("MESH_UL_vgroups", "", obj, "vertex_groups", obj.vertex_groups, "active_index", rows=2)

        col = row.column(align=True)
        col.operator("object.vertex_group_add", icon='ADD', text="")
        col.operator("object.vertex_group_remove", icon='REMOVE', text="").all = False
        col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")
        col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        # Add the new operators
        layout.operator("object.save_vertex_groups_to_csv", text="Save Vertex Groups to CSV").csv_file_path = "path/to/save.csv"
        layout.operator("object.load_vertex_groups_from_csv", text="Load Vertex Groups from CSV").csv_file_path = "path/to/load.csv"

