import bpy
import json
import csv

###Functions
def get_csv_labels(self, context):
    labels = context.scene.get('csv_data', [])
    column_name = context.scene.get('column_names', [])[0]
    if labels and column_name:
        return [(str(i), row.get(column_name, ""), row.get(column_name, "")) for i, row in enumerate(labels)]
    else:
        return []
    
###Property Groups
class CSVLabelProperties(bpy.types.PropertyGroup):
    csv_label_enum: bpy.props.EnumProperty(
        items=get_csv_labels,
        name="CSV Labels",
        description="Labels imported from CSV"
    )

###Operators
class ExecuteWithSelectedCSVRowOperator(bpy.types.Operator):
    bl_idname = "object.execute_with_selected_csv_row"
    bl_label = "Run Function with Selected CSV Row"

    def execute(self, context):
        selected_row = dict(context.scene['csv_data'][int(context.scene.csv_label_props.csv_label_enum)])
        json_args = json.dumps(selected_row)
        bpy.ops.object.execute_stored_function(json_args=json_args)
        return {'FINISHED'}

class ImportCSVOperator(bpy.types.Operator):
    bl_idname = "object.import_csv"
    bl_label = "Import CSV"
    
    # Property to store the path to the CSV file
    csv_file_path: bpy.props.StringProperty(
        name="CSV File Path",
        description="Path to the CSV file",
        default="",
        subtype='FILE_PATH'
    )
    
    @staticmethod
    def import_csv(csv_file_path):
        # Initialize an empty list to store the rows
        csv_data = []
        
        # Initialize an empty list to store the column names
        column_names = []
        
        # Read the CSV file
        with open(csv_file_path, 'r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            
            # Store the column names
            column_names = csvreader.fieldnames

            # Check if the first column name is one of the allowed names
            first_column_name = column_names[0].lower()
            allowed_first_column_names = ["tip", "name", "label"]
            
            if first_column_name not in allowed_first_column_names:
                raise ValueError('Column 1 Must be titled "tip", "name", or "label"!')
            
            # Loop through each row and append it to the list
            for row in csvreader:
                # Convert the types of the values in the row
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
        
        # Convert the list of dictionaries to a JSON object
        csv_json = json.dumps(csv_data)
        
        return csv_data, column_names

    def execute(self, context):
        try:
            csv_data, column_names = self.import_csv(bpy.data.scenes["Scene"].csv_file_path)
            context.scene['csv_data'] = csv_data
            context.scene['column_names'] = column_names

            # Update the csv_labels property
            labels = [row.get(column_names[0]) for row in csv_data]
            items = [(str(i), name, name) for i, name in enumerate(labels)]
            context.scene.csv_label_props.csv_label_enum = items

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

###Panels






