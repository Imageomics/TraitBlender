import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
import inspect
from ...core.morphospaces import load_morphospace_module
import traceback


class TRAITBLENDER_OT_generate_morphospace_sample(Operator):
    """Generate a morphospace sample using the selected morphospace and dataset row"""

    bl_idname = "traitblender.generate_morphospace_sample"
    bl_label = "Generate Morphospace Sample"
    bl_description = "Generate a morphospace sample using selected morphospace and dataset row"
    bl_options = {'REGISTER', 'UNDO'}

    apply_default_orientation: BoolProperty(
        name="Apply Default Orientation",
        description=(
            "Apply the morphospace Default orientation after generation. "
            "Disable when the imaging pipeline will export an unoriented mesh first"
        ),
        default=True,
        options={'SKIP_SAVE'},
    )

    def execute(self, context):
        setup = context.scene.traitblender_setup
        dataset = context.scene.traitblender_dataset

        if not setup.available_morphospaces:
            self.report({'ERROR'}, "No morphospace selected")
            return {'CANCELLED'}
        if not dataset.sample:
            self.report({'ERROR'}, "No dataset sample selected")
            return {'CANCELLED'}
        try:
            morphospace_identifier = setup.available_morphospaces
            morphospace_module = load_morphospace_module(morphospace_identifier)
            if morphospace_module is None:
                self.report({'ERROR'}, f"Morphospace not found: {morphospace_identifier}")
                return {'CANCELLED'}

            sample_func = getattr(morphospace_module, 'sample', None)
            orientations = getattr(morphospace_module, 'ORIENTATIONS', {})
            if not callable(sample_func):
                self.report({'ERROR'}, f"Morphospace '{morphospace_identifier}' has no 'sample' function")
                return {'CANCELLED'}
            if 'Default' not in orientations or not callable(orientations.get('Default')):
                self.report({'ERROR'}, f"Morphospace '{morphospace_identifier}' must define ORIENTATIONS with a callable 'Default'")
                return {'CANCELLED'}

            selected_sample_name = dataset.sample
            row_data = dataset.loc(selected_sample_name)
            # Get the argument names for the sample function (excluding 'name')
            sig = inspect.signature(sample_func)
            accepts_var_keyword = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )
            valid_params = set(sig.parameters.keys()) - {'name'}
            
            # Get hyperparameters from config (merged with module defaults)
            hyperparameters = None
            module_hp_keys = set(getattr(morphospace_module, 'HYPERPARAMETERS', {}).keys())
            if module_hp_keys:
                morphospace_config = context.scene.traitblender_config.morphospace
                hyperparameters = morphospace_config.get_hyperparams_for(morphospace_identifier)
                # Remove hyperparameters from valid_params so they don't get mapped from dataset
                valid_params = valid_params - module_hp_keys - {'hyperparameters'}
            
            species_column_names = {
                'species', 'label', 'tips', 'tip', 'sample', 'samples', 'name', 'names', 'id', 'ids',
            }

            def _norm_col(s: str) -> str:
                return str(s).lower().strip().replace(' ', '_')

            # Map dataset columns to function parameters (excluding hyperparameters).
            # Case-insensitive match so e.g. dataset column "S" maps to param "S".
            # Morphospaces with **traits (e.g. MorphoWeave pc1..pcN) pass all non-species trait columns.
            params = {}
            for column_name, value in row_data.items():
                param_name = column_name.lower().replace(' ', '_')
                if _norm_col(column_name) in species_column_names:
                    continue
                if accepts_var_keyword:
                    params[param_name] = value
                    continue
                if param_name in valid_params:
                    params[param_name] = value
                else:
                    matched = next((p for p in valid_params if p.lower().replace(' ', '_') == param_name), None)
                    if matched is not None:
                        params[matched] = value

            # Add hyperparameters as a dict parameter if the function accepts it
            if hyperparameters is not None and module_hp_keys and 'hyperparameters' in sig.parameters:
                params['hyperparameters'] = hyperparameters
            
            # Debug: show what will be passed
            print(f"Calling {morphospace_identifier}.sample with name={selected_sample_name} and params={params}")
            try:
                sample_obj = sample_func(name=selected_sample_name, **params)
                sample_obj.to_blender()

                # Ensure the object is properly created and positioned
                bpy.context.view_layer.update()

                # Get the generated object
                generated_obj = bpy.data.objects.get(selected_sample_name)
                if generated_obj is None:
                    self.report({'ERROR'}, f"Failed to find generated object: {selected_sample_name}")
                    return {'CANCELLED'}

                # Ensure OBJECT mode (orientation needs to modify object transforms)
                if bpy.context.active_object and bpy.context.mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode='OBJECT')

                # Store rest state for this sample (before any orientation); used when resetting before apply.
                scene = context.scene
                scene.traitblender_sample.rest_rotation = tuple(generated_obj.rotation_euler)
                scene.traitblender_sample.last_baked_rotation = (0.0, 0.0, 0.0)

                if self.apply_default_orientation:
                    try:
                        bpy.context.scene.traitblender_orientation.orientation = 'Default'
                        print(f"Set orientation to: {bpy.context.scene.traitblender_orientation.orientation}")
                    except Exception as e:
                        traceback.print_exc()
                        self.report({'ERROR'}, f"Failed to set orientation: {e}")
                        return {'CANCELLED'}

                    try:
                        bpy.ops.traitblender.apply_orientation()
                        print(f"Successfully applied orientation: {bpy.context.scene.traitblender_orientation.orientation}")
                    except Exception as e:
                        traceback.print_exc()
                        self.report({'ERROR'}, f"Failed to apply orientation: {e}")
                        return {'CANCELLED'}

                    if "Table" not in bpy.data.objects:
                        self.report({'WARNING'}, "Table object missing - run Import Museum first for correct orientation")
              
                bpy.context.view_layer.update()

                # Make the generated sample the active and selected object
                generated_obj.select_set(True)
                bpy.context.view_layer.objects.active = generated_obj

                self.report({'INFO'}, f"Generated morphospace sample: {selected_sample_name}")
            except Exception as e:
                traceback.print_exc()
                self.report({'ERROR'}, f"Failed to generate morphospace sample: {str(e)}")
                return {'CANCELLED'}
        except Exception as e:
            traceback.print_exc()
            self.report({'ERROR'}, f"Failed to generate morphospace sample: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}
