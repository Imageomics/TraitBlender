import bpy

###Functions

###Property Groups

###Operators

###Panels
class TraitBlenderPanel(bpy.types.Panel):
    """
    This panel provides controls for various functionalities related to mesh generation,
    background settings, lighting, camera settings, exporting, and segmentation.

    Attributes:
        bl_label (str): The label for this panel.
        bl_idname (str): Blender's internal name for this panel.
        bl_space_type (str): The space where this panel appears.
        bl_region_type (str): The region where this panel appears.
        bl_category (str): The category where this panel appears.
    """

    bl_label = "TraitBlender"
    bl_idname = "VIEW3D_PT_traitblender"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TraitBlender"

    def draw(self, context):
        """
        Draws the UI elements for this panel.

        Parameters:
            context: Blender's context object.
        """
        layout = self.layout
        obj = context.object
        background_controls = context.scene.background_controls
        camera_controls = context.scene.camera_controls
        segmentation_controls_property = context.scene.segmentation_controls_property  # Get the property group from the scene
        world_background_controls = context.scene.world_background_controls 
        
        layout.prop(context.scene, "mesh_generation_controls", icon="TRIA_DOWN" if context.scene.mesh_generation_controls else "TRIA_RIGHT", emboss=False, text="Mesh Generation")
        if context.scene.mesh_generation_controls:
                row = layout.row()
                row.alignment = 'CENTER'
                row.label(text="Select Mesh Function File", icon='NONE')
                
                # File path selection
                row = layout.row(align=True)
                layout.prop(context.scene, 'make_mesh_function_path', text="Function Path")
                #row.operator("object.open_mesh_function_file_browser", icon='FILEBROWSER', text="")
                
                # Button to execute the function
                layout.operator("object.execute_stored_function", text="Run Function")

                #Button to import the csv
                layout.prop(context.scene, "csv_file_path", text="CSV Path")
                layout.operator("object.import_csv", text="Import CSV")

                if 'csv_data' in context.scene:
                    layout.prop(context.scene.csv_label_props, "csv_label_enum", text="Select Label")
        
                layout.operator("object.execute_with_selected_csv_row", text="Run Function with Selected CSV Row")        
        
        layout.prop(world_background_controls, "expanded", icon="TRIA_DOWN" if world_background_controls.expanded else "TRIA_RIGHT", emboss=False)
        if world_background_controls.expanded:
            box = layout.box()
            
            # Center the text "World Color"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="World Color")
            
            # Add RGBA controls with letters inside the fields
            row = box.row()
            row.prop(world_background_controls, "red", text="R")
            row = box.row()
            row.prop(world_background_controls, "green", text="G")
            row = box.row()
            row.prop(world_background_controls, "blue", text="B")
            row = box.row()
            row.prop(world_background_controls, "alpha", text="A")
            
            box.operator("scene.change_background_color", text="Apply Background Color")

            # New box for Imported Backgrounds
            box = layout.box()

            # Center the text "Imported Backgrounds"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Imported Backgrounds")

            # Add existing controls for imported backgrounds
            box.operator("traitblender.import_background_image", text="Import Background Image")
            box.operator("object.toggle_background_planes", text="Toggle Background")
            box.operator("object.hide_background_planes", text="Hide Background")
            box.prop(context.scene, "background_plane_distance", text="Background Distance")

            # New box for Background Plane Scale
            box = layout.box()

            # Center the text "Background Plane Scale"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Background Plane Scale")

            # Add scale controls for the background planes
            row = box.row()
            row.prop(background_controls, "plane_scale_x", text="X")
            row = box.row()
            row.prop(background_controls, "plane_scale_y", text="Y")
            row = box.row()
            row.prop(background_controls, "plane_scale_z", text="Z")
            box.operator("object.scale_background_planes", text="Apply Scaling")









        layout.prop(context.scene, "lights_controls", icon="TRIA_DOWN" if context.scene.lights_controls else "TRIA_RIGHT", emboss=False, text="Lights")
        if context.scene.lights_controls:
            # Button to toggle all suns
            row = layout.row()
            row.operator("object.toggle_suns", text="Toggle All Suns")

            # Button to hide all suns
            row = layout.row()
            row.operator("object.hide_suns", text="Hide All Suns")

            # Checkboxes to toggle individual suns in three rows
            sun_pairs = [("Front", "Back"), ("Left", "Right"), ("Top", "Bottom")]
            for pair in sun_pairs:
                row = layout.row()
                row.operator("object.hide_suns", text=pair[0]).sun_names = f"sun.{pair[0].lower()}"
                row.operator("object.hide_suns", text=pair[1]).sun_names = f"sun.{pair[1].lower()}"
            layout = self.layout
            layout.prop(context.scene, "sun_strength", slider=True)
            layout.operator("object.update_sun_strength", text="Update Sun Strength")




        layout.prop(camera_controls, "expanded", icon="TRIA_DOWN" if camera_controls.expanded else "TRIA_RIGHT", emboss=False)
        if camera_controls.expanded:
            layout.operator("object.toggle_cameras", text="Toggle Cameras")
            layout.operator("object.hide_cameras", text="Hide Cameras")

            # Centered "View & Render Settings" text
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="View & Render Settings", icon='NONE')

            # Camera width and height controls
            row = layout.row()
            row.label(text="Width:")
            row.prop(camera_controls, "camera_width", text="")
            row = layout.row()
            row.label(text="Height:")
            row.prop(camera_controls, "camera_height", text="")

            # Camera distance control
            row = layout.row()
            row.label(text="Distance:")
            row.prop(context.scene, "place_cameras_distance", text="")

            # Focal length control
            row = layout.row()
            row.label(text="Focal Length:")
            row.prop(camera_controls, "focal_length", text="")
            
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Camera Preview", icon='NONE')
            # Buttons to set the view to different angles

            # Row for Front & Back buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Front").angle = "Front"
            row.operator("object.set_camera_view", text="Back").angle = "Back"

            # Row for Left & Right buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Left").angle = "Left"
            row.operator("object.set_camera_view", text="Right").angle = "Right"

            # Row for Top & Bottom buttons
            row = layout.row(align=True)
            row.operator("object.set_camera_view", text="Top").angle = "Top"
            row.operator("object.set_camera_view", text="Bottom").angle = "Bottom"

            # Create a 3x2 grid layout for cameras to render
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Cameras to Render", icon='NONE')
            grid = layout.grid_flow(row_major=True, columns=2, even_columns=True)
            grid.prop(camera_controls, "render_camera_top")
            grid.prop(camera_controls, "render_camera_bottom")
            grid.prop(camera_controls, "render_camera_right")
            grid.prop(camera_controls, "render_camera_left")
            grid.prop(camera_controls, "render_camera_front")
            grid.prop(camera_controls, "render_camera_back")

            # Construct the string argument for the RenderAllCamerasOperator
            camera_names_list = []
            if camera_controls.render_camera_top:
                camera_names_list.append('camera.top')
            if camera_controls.render_camera_bottom:
                camera_names_list.append('camera.bottom')
            if camera_controls.render_camera_right:
                camera_names_list.append('camera.right')
            if camera_controls.render_camera_left:
                camera_names_list.append('camera.left')
            if camera_controls.render_camera_front:
                camera_names_list.append('camera.front')
            if camera_controls.render_camera_back:
                camera_names_list.append('camera.back')
            camera_names_str = ','.join(camera_names_list)

            # Centered "Render Directory" text
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Render Directory", icon='NONE')

            # Render directory selection
            layout.prop(context.scene, "render_output_directory", text="")

            layout.operator("object.render_all_cameras", text="Render Selected Cameras").camera_names = camera_names_str

        
        export_controls_property = context.scene.export_controls_property  # Replace with the correct attribute name if needed
        layout.prop(export_controls_property, "export_controls", icon="TRIA_DOWN" if export_controls_property.export_controls else "TRIA_RIGHT", emboss=False, text="3D Export")
        if export_controls_property.export_controls:  # Use the property from the property group
            
            # Row for the user to specify the export directory
            row = layout.row()
            row.prop(context.scene, "export_directory", text="Export Directory")
            
            # Dropdown for selecting the export format
            row = layout.row()
            row.prop(context.scene, "export_format", text="File Format")
            
            # Button to trigger the export
            row = layout.row()
            row.operator("object.export_active_object", text="Export Active Object")



        layout.prop(segmentation_controls_property, "segmentation_controls", icon="TRIA_DOWN" if segmentation_controls_property.segmentation_controls else "TRIA_RIGHT", emboss=False, text="Segmentation / Vertex Groups")
        if segmentation_controls_property.segmentation_controls:  # Use the property from the property group
            row = layout.row()
            row.template_list("MESH_UL_vgroups", "", obj, "vertex_groups", obj.vertex_groups, "active_index", rows=2)

            col = row.column(align=True)
            col.operator("object.vertex_group_add", icon='ADD', text="")
            col.operator("object.vertex_group_remove", icon='REMOVE', text="").all = False
            col.menu("MESH_MT_vertex_group_context_menu", icon='DOWNARROW_HLT', text="")
            col.operator("object.vertex_group_move", icon='TRIA_UP', text="").direction = 'UP'
            col.operator("object.vertex_group_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            row = layout.row()
            row.operator("object.vertex_group_assign", text="Assign")
            row.operator("object.vertex_group_remove_from", text="Remove")
            row = layout.row()
            row.operator("object.vertex_group_select", text="Select")
            row.operator("object.vertex_group_deselect", text="Deselect")
            
            # Add a button to save vertex groups to CSV
            row = layout.row()
            row.operator("object.save_vertex_groups_to_csv", text="Save Vertex Groups to CSV").csv_file_path = context.scene.csv_file_path_save
            
            # Add a row for the user to specify the CSV file path for saving vertex groups
            row = layout.row()
            row.prop(context.scene, "csv_file_path_save", text="")

            # Add a button to load vertex groups from CSV
            row = layout.row()
            row.operator("object.load_vertex_groups_from_csv", text="Load Vertex Groups from CSV").csv_file_path = context.scene.csv_file_path_load

            # Add a row for the user to specify the CSV file path for loading vertex groups
            row = layout.row()
            row.prop(context.scene, "csv_file_path_load", text="")

            layout = self.layout

        layout.prop(context.scene, "dataset_options", icon="TRIA_DOWN" if context.scene.dataset_options else "TRIA_RIGHT", emboss=False, text="Dataset Options")
        if context.scene.dataset_options:
            box = layout.box()
            col = box.column(align=True)
            col.scale_y = 1.5  # Adjust the vertical scaling as needed
            
            col.prop(context.scene, "use_suns", text="Use Suns")
            col.prop(context.scene, "use_cameras", text="Use Cameras")
            col.prop(context.scene, "use_3d_export", text="Use 3D Export")


            
        layout.prop(context.scene, "export_settings_directory", text="Export Directory")    
        layout.operator("object.export_settings")
        layout.operator("object.delete_all_objects", text="Delete All Objects")