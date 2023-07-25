
def get_setting(context, key):
    settings_string = context.scene.traitblender_settings
    settings_dict = json.loads(settings_string)
    return settings_dict.get(key, None)
  
def print_selected_vertices():
    # Get the active mesh
    obj = bpy.context.edit_object
    me = obj.data

    # Get a BMesh from the active mesh
    bm = bmesh.from_edit_mesh(me)

    # Get the selected vertices
    selected_verts = [v.index for v in bm.verts if v.select]

    # Convert to numpy array
    selected_verts_np = np.array(selected_verts)

    return selected_verts_np
    
