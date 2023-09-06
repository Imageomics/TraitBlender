import bpy
import csv

def save_vertex_groups_to_csv(obj_name, csv_file_path):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"Object {obj_name} not found.")
        return
    
    with open(csv_file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write header
        csvwriter.writerow(["Vertex Index", "Group Name", "Weight"])
        
        for vert in obj.data.vertices:
            for group in vert.groups:
                group_name = obj.vertex_groups[group.group].name
                weight = group.weight
                csvwriter.writerow([vert.index, group_name, weight])

def load_vertex_groups_from_csv(obj_name, csv_file_path):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"Object {obj_name} not found.")
        return
    
    # Clear existing vertex groups
    obj.vertex_groups.clear()
    
    with open(csv_file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # Skip header
        next(csvreader)
        
        for row in csvreader:
            vert_index, group_name, weight = int(row[0]), row[1], float(row[2])
            
            # Create vertex group if it doesn't exist
            if group_name not in obj.vertex_groups:
                obj.vertex_groups.new(name=group_name)
            
            obj.vertex_groups[group_name].add([vert_index], weight, 'REPLACE')

def delete_all_and_create_suzanne(jowl_length=1.0, csv_file_path=None):
    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create a new Suzanne
    bpy.ops.mesh.primitive_monkey_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 1))
    suzanne = bpy.context.object
    
    # Rename the new object to "Suzanne"
    suzanne.name = "Suzanne"
    
    # Load vertex groups from CSV if provided
    if csv_file_path:
        load_vertex_groups_from_csv("Suzanne", csv_file_path)
    
    # Make sure Suzanne is the active object
    bpy.context.view_layer.objects.active = suzanne
    
    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Deselect all vertices
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Assuming "Jowls" vertex group exists, if not, you might want to create it
    bpy.ops.object.vertex_group_set_active(group="Jowls")
    bpy.ops.object.vertex_group_select()
    
    # Scale vertices by jowl_length
    bpy.ops.transform.resize(value=(jowl_length, jowl_length, jowl_length))
    
    # Exit edit mode
    bpy.ops.object.mode_set(mode='OBJECT')

# Example usage
delete_all_and_create_suzanne(csv_file_path="C://Users/caleb/Downloads/vertex_groups.csv")
