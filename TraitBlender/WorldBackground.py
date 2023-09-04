import bpy

class WorldBackgroundControls(bpy.types.PropertyGroup):
    expanded: bpy.props.BoolProperty(
        name="Background",
        description="Expand the background controls",
        default=False
    )
    
    red: bpy.props.FloatProperty(
        name="Red",
        description="Red component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    green: bpy.props.FloatProperty(
        name="Green",
        description="Green component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    blue: bpy.props.FloatProperty(
        name="Blue",
        description="Blue component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )
    
    alpha: bpy.props.FloatProperty(
        name="Alpha",
        description="Alpha component of the background color",
        default=1.0,
        min=0.0,
        max=1.0
    )

    world_color_expanded: bpy.props.BoolProperty(
        name="World Color Expanded",
        default=True
    )
    
    imported_backgrounds_expanded: bpy.props.BoolProperty(
        name="Imported Backgrounds Expanded",
        default=True
    )
    
    background_scale_expanded: bpy.props.BoolProperty(
        name="Background Scale Expanded",
        default=True
    )
    


class ChangeWorldBackgroundColor(bpy.types.Operator):
    bl_idname = "scene.change_background_color"
    bl_label = "Change World Background Color"
    
    def execute(self, context):
        # Access the active scene
        scene = context.scene

        # Access the world settings
        world = scene.world

        # Access the background_controls property group
        world_background_controls = context.scene.world_background_controls

        # Enable use_nodes to allow node-based modifications
        world.use_nodes = True

        # Access the node tree
        node_tree = world.node_tree

        # Find the "Background" node
        world_background_node = node_tree.nodes.get("Background")

        # Change the color of the background
        world_background_node.inputs[0].default_value = (
            world_background_controls.red, 
            world_background_controls.green, 
            world_background_controls.blue, 
            world_background_controls.alpha
        )
        
        return {'FINISHED'}
