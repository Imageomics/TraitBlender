import bpy
import yaml
import os
from bpy.types import Operator
from bpy.props import StringProperty
from ...core.datasets.traitblender_dataset import update_filepath, _normalize_dataset_path
from ...core.helpers.render_engine_compat import (
    normalize_render_engine_value,
    try_set_render_engine,
)


def _apply_render_engine_from_config(context, config_data):
    """
    Force-apply render.engine from YAML after the rest of config load.

    Returns (wanted, actual) or None if YAML has no render.engine.
    """
    render = config_data.get("render")
    if not isinstance(render, dict) or "engine" not in render:
        return None

    raw = render["engine"]
    wanted = normalize_render_engine_value(raw)
    scene = context.scene
    try:
        actual = try_set_render_engine(scene, raw)
    except Exception as e:
        print(f"TraitBlender: Failed to set render.engine from YAML {raw!r}: {e}")
        return wanted, scene.render.engine

    context.view_layer.update()
    if hasattr(context, "window_manager"):
        for window in context.window_manager.windows:
            screen = window.screen
            if screen is None:
                continue
            for area in screen.areas:
                area.tag_redraw()

    actual = scene.render.engine
    print(
        f"TraitBlender: Configure Scene render.engine "
        f"yaml={raw!r} wanted={wanted!r} actual={actual!r}"
    )
    return wanted, actual


class TRAITBLENDER_OT_configure_scene(Operator):
    """Configure TraitBlender scene from YAML file"""
    
    bl_idname = "traitblender.configure_scene"
    bl_label = "Configure Scene"
    bl_description = "Load and apply configuration from YAML file"
    # No UNDO: a full YAML apply must not be partially reverted by the undo stack
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(
        name="Config File Path",
        description="Path to the YAML configuration file (optional - uses default if not provided)",
        default="",
        subtype='FILE_PATH'
    )
    
    def execute(self, context):
        """Execute the configure scene operation"""
        
        # Use provided filepath or default to the stored config file path
        config_file_path = self.filepath if self.filepath else context.scene.traitblender_setup.config_file
        
        if not config_file_path:
            self.report({'ERROR'}, "No configuration file specified")
            return {'CANCELLED'}
        
        if not os.path.exists(config_file_path):
            self.report({'ERROR'}, f"Configuration file not found: {config_file_path}")
            return {'CANCELLED'}
        
        try:
            # Read the YAML file
            with open(config_file_path, 'r') as file:
                config_data = yaml.safe_load(file)
            
            if not config_data:
                self.report({'ERROR'}, "Configuration file is empty or invalid")
                return {'CANCELLED'}
            
            # Apply the configuration using the from_dict method
            context.scene.traitblender_config.from_dict(config_data)

            # Force render.engine last so nothing else in from_dict can leave it stale.
            engine_result = _apply_render_engine_from_config(context, config_data)
            if engine_result is not None:
                wanted, actual = engine_result
                if actual != wanted:
                    self.report(
                        {'WARNING'},
                        f"Render engine YAML asked for {wanted} but scene is {actual}",
                    )

            # Final imaging sync after morphospace + customs are both loaded.
            # Default policy: only "Default" enabled unless YAML lists orientation_names.
            imaging = context.scene.traitblender_config.imaging
            enabled = {"Default"}
            if isinstance(config_data.get("imaging"), dict):
                names = config_data["imaging"].get("orientation_names")
                if isinstance(names, list):
                    enabled = {n for n in names if isinstance(n, str)}
            try:
                imaging.sync_orientation_options(context, enabled_names=enabled)
            except Exception as e:
                print(f"TraitBlender: Post-configure orientation sync failed: {e}")

            missing = [
                name
                for name in ("Camera", "Mat", "Lamp")
                if name not in bpy.data.objects
            ]
            if missing:
                self.report(
                    {'WARNING'},
                    "Museum objects missing ("
                    + ", ".join(missing)
                    + "); run Import Museum first so those settings can apply.",
                )

            # Force an explicit dataset import after config load.
            # Do not rely on property update callbacks here; they may not run when
            # the value is unchanged, and users expect Configure Scene to load data.
            dataset = context.scene.traitblender_dataset
            if dataset.filepath:
                p = _normalize_dataset_path(dataset.filepath)
                if not os.path.exists(p):
                    self.report({'WARNING'}, f"Dataset file not found: {p}")
                else:
                    update_filepath(dataset, context)
                    # Re-import can leave csv unchanged; only warn if we still have no data.
                    if not (dataset.csv or "").strip():
                        self.report({'WARNING'}, f"Dataset path set but CSV is empty after import: {p}")
            
            self.report(
                {'INFO'},
                f"Configuration loaded from {config_file_path}"
                + (
                    f" (render.engine={context.scene.render.engine})"
                    if engine_result is not None
                    else ""
                ),
            )
            return {'FINISHED'}
            
        except yaml.YAMLError as e:
            self.report({'ERROR'}, f"Invalid YAML format: {e}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error loading configuration: {e}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        """Invoke file browser if no filepath is provided and no stored config file"""
        # If no filepath provided and no stored config file, open file browser
        if not self.filepath and not context.scene.traitblender_setup.config_file:
            if getattr(bpy.app, "background", False):
                self.report(
                    {'ERROR'},
                    "No configuration file specified (file browser unavailable in background mode)",
                )
                return {'CANCELLED'}
            context.window_manager.fileselect_add(self)
            return {'RUNNING_MODAL'}
        else:
            return self.execute(context)


class TRAITBLENDER_OT_show_configuration(Operator):
    """Show current TraitBlender configuration in YAML format"""
    
    bl_idname = "traitblender.show_configuration"
    bl_label = "Show Configuration"
    bl_description = "Display current configuration in YAML format"
    bl_options = {'REGISTER', 'UNDO'}
    
    _old_mouse_pos = None

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if getattr(bpy.app, "background", False):
            # No dialogs in headless; dump YAML to stdout for logs / debugging.
            print(str(context.scene.traitblender_config))
            return {'FINISHED'}
        if not context.window_manager.windows:
            self.report({'WARNING'}, "No window available to show configuration dialog")
            return {'CANCELLED'}
        window = context.window_manager.windows[0]
        self._old_mouse_pos = (event.mouse_x, event.mouse_y)
        center_x = window.width // 2
        center_y = window.height // 2
        window.cursor_warp(center_x, center_y)
        # Restore mouse after popup appears
        def restore_mouse():
            window.cursor_warp(*self._old_mouse_pos)
            self._old_mouse_pos = None
            return None  # Only run once
        bpy.app.timers.register(restore_mouse, first_interval=0.01)
        return context.window_manager.invoke_props_dialog(self, width=600)
    
    def draw(self, context):
        layout = self.layout
        config_yaml = str(context.scene.traitblender_config)
        for line in config_yaml.splitlines():
            layout.label(text=line)


class TRAITBLENDER_OT_export_config(Operator):
    """Export current TraitBlender configuration to a YAML file"""
    
    bl_idname = "traitblender.export_config"
    bl_label = "Export Config as YAML"
    bl_description = "Export the current configuration to a YAML file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(
        name="File Path",
        description="Path to export YAML file",
        default="",
        subtype='FILE_PATH',
    )
    
    def execute(self, context):
        config_yaml = str(context.scene.traitblender_config)
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(config_yaml)
            self.report({'INFO'}, f"Configuration exported to {self.filepath}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to export configuration: {e}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        if self.filepath:
            return self.execute(context)
        if getattr(bpy.app, "background", False):
            self.report(
                {'ERROR'},
                "No export path specified (file browser unavailable in background mode)",
            )
            return {'CANCELLED'}
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
