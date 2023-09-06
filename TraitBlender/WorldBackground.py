import bpy

###Functions
###Property Groups
class WorldBackgroundControls(bpy.types.PropertyGroup):
    """
    Property Group to hold controls for modifying the world background.
    
    Attributes:
        expanded (BoolProperty): Controls whether the background section is expanded in the UI.
        red (FloatProperty): The red component of the world background color.
        green (FloatProperty): The green component of the world background color.
        blue (FloatProperty): The blue component of the world background color.
        alpha (FloatProperty): The alpha component of the world background color.
        world_color_expanded (BoolProperty): Controls whether the world color section is expanded in the UI.
        imported_backgrounds_expanded (BoolProperty): Controls whether the imported backgrounds section is expanded in the UI.
        background_scale_expanded (BoolProperty): Controls whether the background scale section is expanded in the UI.
    """
    
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


###Operators
class ChangeWorldBackgroundColor(bpy.types.Operator):
    """
    Operator to change the world background color based on user input.
    
    Attributes:
        bl_idname (str): Blender internal name for this operator.
        bl_label (str): Human-readable label displayed in the UI.
    """
    
    bl_idname = "scene.change_background_color"
    bl_label = "Change World Background Color"
    
    def execute(self, context):
        """
        Execute the operator to change the world background color.
        
        Args:
            context (bpy.context): Blender context.
        
        Returns:
            set: A set with a string status {'FINISHED'}.
        """
        
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


###Panels


    


