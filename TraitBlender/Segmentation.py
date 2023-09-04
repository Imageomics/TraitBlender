import bpy
import csv

class SegmentationControls(bpy.types.Panel):
    bl_label = "Segmentation Controls"
    bl_idname = "OBJECT_PT_segmentation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_category = "TraitBlender"

    def draw(self, context):
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



class SegmentationControlsProperty(bpy.types.PropertyGroup):
    expanded: bpy.props.BoolProperty(default=False)
    segmentation_controls: bpy.props.BoolProperty(default=False)  # Add this line


class SaveVertexGroupsToCSVOperator(bpy.types.Operator):
    bl_idname = "object.save_vertex_groups_to_csv"
    bl_label = "Save Vertex Groups to CSV"
    bl_options = {'REGISTER', 'UNDO'}

    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        subtype='FILE_PATH'
    )

    def execute(self, context):
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

class LoadVertexGroupsFromCSVOperator(bpy.types.Operator):
    bl_idname = "object.load_vertex_groups_from_csv"
    bl_label = "Load Vertex Groups from CSV"
    bl_options = {'REGISTER', 'UNDO'}

    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        subtype='FILE_PATH'
    )

    def execute(self, context):
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