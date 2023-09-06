import bpy
import json
import csv

### Functions
def get_csv_labels(self, context):
    """
    Function to retrieve the labels from the CSV data stored in the scene.

    Parameters:
        self: The self object.
        context (bpy.types.Context): The Blender context.

    Returns:
        list: A list of tuples for the EnumProperty items, each containing an index, label, and description.
    """
    labels = context.scene.get('csv_data', [])
    column_name = context.scene.get('column_names', [])[0]

    if labels and column_name:
        return [(str(i), row.get(column_name, ""), row.get(column_name, "")) for i, row in enumerate(labels)]
    else:
        return []


### Property Groups
class CSVLabelProperties(bpy.types.PropertyGroup):
    """
    Property Group to hold the CSV labels as an EnumProperty.

    Attributes:
        csv_label_enum (EnumProperty): The labels imported from the CSV file.
    """
    csv_label_enum: bpy.props.EnumProperty(
        items=get_csv_labels,
        name="CSV Labels",
        description="Labels imported from CSV"
    )


### Operators
class ExecuteWithSelectedCSVRowOperator(bpy.types.Operator):
    """
    Operator to execute a function using the selected row from the CSV data.

    Attributes:
        None
    """
    bl_idname = "object.execute_with_selected_csv_row"
    bl_label = "Run Function with Selected CSV Row"

    def execute(self, context):
        """
        Execute the operator. This is called when the operator is run.

        Parameters:
            context (bpy.types.Context): The context in which the operator is executed.

        Returns:
            set: A set containing {'FINISHED'} if completed successfully.
        """
        selected_row = dict(context.scene['csv_data'][int(context.scene.csv_label_props.csv_label_enum)])
        json_args = json.dumps(selected_row)
        bpy.ops.object.execute_stored_function(json_args=json_args)
        return {'FINISHED'}

class ImportCSVOperator(bpy.types.Operator):
    """
    Operator for importing CSV files into Blender.
    
    Attributes:
        csv_file_path (str): The path of the CSV file to be imported.
    """
    bl_idname = "object.import_csv"
    bl_label = "Import CSV"

    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        description="Path to the CSV file",
        default="",
        subtype='FILE_PATH'
    )

    @staticmethod
    def import_csv(csv_file_path):
        """
        Static method to read a CSV file and convert it to a list of dictionaries.

        Parameters:
            csv_file_path (str): The file path of the CSV file.

        Returns:
            list, list: A list of dictionaries containing the CSV data and a list of column names.
        """
        csv_data = []
        column_names = []
        with open(csv_file_path, 'r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            column_names = csvreader.fieldnames
            first_column_name = column_names[0].lower()
            allowed_first_column_names = ["tip", "name", "label"]
            if first_column_name not in allowed_first_column_names:
                raise ValueError('Column 1 Must be titled "tip", "name", or "label"!')
            for row in csvreader:
                for key, value in row.items():
                    try:
                        row[key] = float(value)
                    except ValueError:
                        try:
                            row[key] = int(value)
                        except ValueError:
                            if value.lower() == 'true':
                                row[key] = True
                            elif value.lower() == 'false':
                                row[key] = False
                            else:
                                row[key] = value
                csv_data.append(row)
        csv_json = json.dumps(csv_data)
        return csv_data, column_names

    def execute(self, context):
        """
        Execute the operator. This is called when the operator is run.

        Parameters:
            context (bpy.types.Context): The context in which the operator is executed.

        Returns:
            set: A set containing {'FINISHED'} if completed successfully, or {'CANCELLED'} otherwise.
        """
        scene_name = context.scene.name
        try:
            csv_data, column_names = self.import_csv(bpy.data.scenes[scene_name].csv_file_path)
            context.scene['csv_data'] = csv_data
            context.scene['column_names'] = column_names
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}



###Panels






