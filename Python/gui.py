import bpy

class AddSegmentOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.add_segment_operator"
    bl_label = "+ Add Segment"
    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        print("Button pressed!")
        
        # Set the pressed property of the current button to True
        context.scene.segment_buttons[self.index].pressed = True

        # Store the index of the current button in the scene
        context.scene.current_button_index = self.index

        # Add a new button to the collection
        new_button = context.scene.segment_buttons.add()
        new_button.name = "+ Add Segment"

        return {'FINISHED'}

class DeleteSegmentOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.delete_segment_operator"
    bl_label = "Delete Segment"
    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        print("Button pressed!")
        
        # Remove the current button from the collection
        context.scene.segment_buttons.remove(self.index)

        return {'FINISHED'}

class ChangeNameOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.change_name_operator"
    bl_label = "Change Name"
    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        print("Button pressed!")
        
        # Change the name of the current button to the value of the text property
        context.scene.segment_buttons[self.index].name = context.scene.segment_buttons[self.index].text

        return {'FINISHED'}

class MyMenu(bpy.types.Menu):
    bl_label = "My Menu"
    bl_idname = "OBJECT_MT_my_menu"

    def draw(self, context):
        # Set the label of the menu to the name of the current button
        self.bl_label = context.scene.segment_buttons[context.scene.current_button_index].name

        layout = self.layout
        layout.prop(context.scene.segment_buttons[context.scene.current_button_index], "text", text="Segment Label")
        op = layout.operator("object.change_name_operator")
        op.index = context.scene.current_button_index
        op = layout.operator("object.delete_segment_operator")
        op.index = context.scene.current_button_index

class SegmentButtonList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if item.pressed:
            layout.menu("OBJECT_MT_my_menu")
        else:
            op = layout.operator("object.add_segment_operator")
            op.index = index

class SegmentMeshPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Segment Mesh"
    bl_idname = "OBJECT_PT_segment_mesh_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "TraitBlender"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.template_list("SegmentButtonList", "", context.scene, "segment_buttons", context.scene, "segment_button_index")

class SegmentButton(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    pressed: bpy.props.BoolProperty(default=False)
    text: bpy.props.StringProperty()

def register():
    bpy.utils.register_class(SegmentButton)
    bpy.utils.register_class(AddSegmentOperator)
    bpy.utils.register_class(DeleteSegmentOperator)
    bpy.utils.register_class(ChangeNameOperator)
    bpy.utils.register_class(MyMenu)
    bpy.utils.register_class(SegmentButtonList)
    bpy.utils.register_class(SegmentMeshPanel)
    
    bpy.types.Scene.segment_buttons = bpy.props.CollectionProperty(type=SegmentButton)
    bpy.types.Scene.segment_button_index = bpy.props.IntProperty()
    bpy.types.Scene.current_button_index = bpy.props.IntProperty()

    # Clear the collection of buttons
    bpy.context.scene.segment_buttons.clear()

    # Add an initial button to the collection
    initial_button = bpy.context.scene.segment_buttons.add()
    initial_button.name = "+ Add Segment"

def unregister():
    bpy.utils.unregister_class(SegmentButton)
    bpy.utils.unregister_class(AddSegmentOperator)
    bpy.utils.unregister_class(DeleteSegmentOperator)
    bpy.utils.unregister_class(ChangeNameOperator)
    bpy.utils.unregister_class(MyMenu)
    bpy.utils.unregister_class(SegmentButtonList)
    bpy.utils.unregister_class(SegmentMeshPanel)
    
    del bpy.types.Scene.segment_buttons
    del bpy.types.Scene.segment_button_index
    del bpy.types.Scene.current_button_index

if __name__ == "__main__":
    register()
