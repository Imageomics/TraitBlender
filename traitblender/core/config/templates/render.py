import bpy
from .. import config_subsection_register, TraitBlenderConfig
from ...helpers import get_property, set_property
from ...helpers.render_engine_compat import (
    normalize_render_engine_value,
    render_engine_enum_items,
    render_engine_identifier_for_number,
    render_engine_number_for_identifier,
    try_set_render_engine,
)


def _render_engine_items(self, context):
    """Live enum items so Eevee id matches this Blender build."""
    return render_engine_enum_items()


def _get_render_engine(self):
    # EnumProperty get/set use item *numbers*, not list indices.
    try:
        return render_engine_number_for_identifier(bpy.context.scene.render.engine)
    except Exception:
        return 0


def _set_render_engine(self, value):
    try:
        if isinstance(value, int):
            engine = render_engine_identifier_for_number(value)
        else:
            engine = normalize_render_engine_value(value)
        bpy.context.scene.render.engine = engine
    except Exception as e:
        print(f"TraitBlender: Failed to set render.engine to '{value}': {e}")


@config_subsection_register("render")
class RenderConfig(TraitBlenderConfig):
    print_index = 5

    def from_dict(self, data_dict):
        if not isinstance(data_dict, dict):
            return
        data = dict(data_dict)
        if "engine" in data:
            # Apply directly — do not gate on RNA enum_items (incomplete on Blender 5.1).
            raw = data.pop("engine")
            engine = normalize_render_engine_value(raw)
            scene = bpy.context.scene
            try:
                actual = try_set_render_engine(scene, raw)
                print(
                    f"TraitBlender: render.engine from config "
                    f"raw={raw!r} normalized={engine!r} actual={actual!r}"
                )
                if actual != engine:
                    print(
                        "TraitBlender: WARNING scene.render.engine did not stick "
                        f"(wanted {engine!r}, got {actual!r})"
                    )
            except Exception as e:
                print(f"TraitBlender: Failed to apply render.engine '{engine}': {e}")
        super().from_dict(data)

    engine: bpy.props.EnumProperty(
        name="Engine",
        description="The engine to use",
        items=_render_engine_items,
        get=_get_render_engine,
        set=_set_render_engine,
    )

    eevee_use_raytracing: bpy.props.BoolProperty(
        name="Use Raytracing",
        description="Whether to use raytracing",
        default=False,
        get=get_property("bpy.context.scene.eevee.use_raytracing"),
        set=set_property("bpy.context.scene.eevee.use_raytracing"),
    )
