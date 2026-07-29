"""
Render configuration: engine plus Cycles/Eevee sampling settings.

YAML shape (engine-specific blocks are optional; only the active engine's block
is written on export, but both are accepted on load):

  render:
    engine: CYCLES
    cycles:
      use_adaptive_sampling: true
      adaptive_threshold: 0.01
      samples: 32
      adaptive_min_samples: 0
      time_limit: 0.0
      use_denoising: true
      use_preview_adaptive_sampling: true
      preview_adaptive_threshold: 0.1
      preview_samples: 1024
      preview_adaptive_min_samples: 0
      use_preview_denoising: false
    eevee:
      use_raytracing: false
      taa_render_samples: 64

Legacy flat ``eevee_use_raytracing`` is still accepted on load.
"""

from __future__ import annotations

import bpy
from bpy.props import BoolProperty, FloatProperty, IntProperty, PointerProperty

from .. import config_subsection_register, TraitBlenderConfig
from ...helpers import get_property, set_property
from ...helpers.render_engine_compat import (
    normalize_render_engine_value,
    render_engine_enum_items,
    render_engine_identifier_for_number,
    render_engine_number_for_identifier,
    try_set_render_engine,
)

# Keys written to / read from scene.cycles (final render + viewport).
CYCLES_SCENE_KEYS = (
    "use_adaptive_sampling",
    "adaptive_threshold",
    "samples",
    "adaptive_min_samples",
    "time_limit",
    "use_denoising",
    "use_preview_adaptive_sampling",
    "preview_adaptive_threshold",
    "preview_samples",
    "preview_adaptive_min_samples",
    "use_preview_denoising",
)

EEVEE_SCENE_KEYS = (
    "use_raytracing",
    "taa_render_samples",
)


def _render_engine_items(self, context):
    return render_engine_enum_items()


def _get_render_engine(self):
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


def _is_eevee_engine(engine: str) -> bool:
    return "EEVEE" in (engine or "").upper()


def _is_cycles_engine(engine: str) -> bool:
    return (engine or "").upper() == "CYCLES"


def _apply_mapping_to_id(target, data: dict, allowed_keys: tuple) -> list[str]:
    """
    Apply YAML dict keys onto a Blender ID/RNA struct (scene.cycles / scene.eevee).

    Returns list of error strings (empty if all ok).
    """
    errors = []
    if target is None:
        return ["target RNA is None"]
    for key, value in data.items():
        if key not in allowed_keys:
            continue
        if not hasattr(target, key):
            errors.append(f"missing attribute {key!r}")
            continue
        try:
            setattr(target, key, value)
        except Exception as e:
            errors.append(f"{key}={value!r}: {e}")
    return errors


def _snapshot_mapping(target, allowed_keys: tuple) -> dict:
    """Read allowed keys from a Blender RNA struct into a plain dict."""
    out = {}
    if target is None:
        return out
    for key in allowed_keys:
        if hasattr(target, key):
            try:
                out[key] = getattr(target, key)
            except Exception:
                pass
    return out


class CyclesRenderConfig(TraitBlenderConfig):
    """Cycles sampling (mirrors ``scene.cycles`` for UI / export helpers)."""

    use_adaptive_sampling: BoolProperty(
        name="Noise Threshold",
        default=True,
        get=get_property("bpy.context.scene.cycles.use_adaptive_sampling"),
        set=set_property("bpy.context.scene.cycles.use_adaptive_sampling"),
    )
    adaptive_threshold: FloatProperty(
        name="Adaptive Threshold",
        default=0.01,
        min=0.0,
        max=1.0,
        get=get_property("bpy.context.scene.cycles.adaptive_threshold"),
        set=set_property("bpy.context.scene.cycles.adaptive_threshold"),
    )
    samples: IntProperty(
        name="Max Samples",
        default=4096,
        min=1,
        get=get_property("bpy.context.scene.cycles.samples"),
        set=set_property("bpy.context.scene.cycles.samples"),
    )
    adaptive_min_samples: IntProperty(
        name="Min Samples",
        default=0,
        min=0,
        get=get_property("bpy.context.scene.cycles.adaptive_min_samples"),
        set=set_property("bpy.context.scene.cycles.adaptive_min_samples"),
    )
    time_limit: FloatProperty(
        name="Time Limit",
        default=0.0,
        min=0.0,
        get=get_property("bpy.context.scene.cycles.time_limit"),
        set=set_property("bpy.context.scene.cycles.time_limit"),
    )
    use_denoising: BoolProperty(
        name="Denoise",
        default=False,
        get=get_property("bpy.context.scene.cycles.use_denoising"),
        set=set_property("bpy.context.scene.cycles.use_denoising"),
    )
    use_preview_adaptive_sampling: BoolProperty(
        name="Viewport Noise Threshold",
        default=True,
        get=get_property("bpy.context.scene.cycles.use_preview_adaptive_sampling"),
        set=set_property("bpy.context.scene.cycles.use_preview_adaptive_sampling"),
    )
    preview_adaptive_threshold: FloatProperty(
        name="Viewport Adaptive Threshold",
        default=0.1,
        min=0.0,
        max=1.0,
        get=get_property("bpy.context.scene.cycles.preview_adaptive_threshold"),
        set=set_property("bpy.context.scene.cycles.preview_adaptive_threshold"),
    )
    preview_samples: IntProperty(
        name="Viewport Max Samples",
        default=1024,
        min=1,
        get=get_property("bpy.context.scene.cycles.preview_samples"),
        set=set_property("bpy.context.scene.cycles.preview_samples"),
    )
    preview_adaptive_min_samples: IntProperty(
        name="Viewport Min Samples",
        default=0,
        min=0,
        get=get_property("bpy.context.scene.cycles.preview_adaptive_min_samples"),
        set=set_property("bpy.context.scene.cycles.preview_adaptive_min_samples"),
    )
    use_preview_denoising: BoolProperty(
        name="Viewport Denoise",
        default=False,
        get=get_property("bpy.context.scene.cycles.use_preview_denoising"),
        set=set_property("bpy.context.scene.cycles.use_preview_denoising"),
    )


class EeveeRenderConfig(TraitBlenderConfig):
    """Eevee settings (mirrors ``scene.eevee``)."""

    use_raytracing: BoolProperty(
        name="Use Raytracing",
        default=False,
        get=get_property("bpy.context.scene.eevee.use_raytracing"),
        set=set_property("bpy.context.scene.eevee.use_raytracing"),
    )
    taa_render_samples: IntProperty(
        name="Samples",
        default=64,
        min=1,
        get=get_property("bpy.context.scene.eevee.taa_render_samples"),
        set=set_property("bpy.context.scene.eevee.taa_render_samples"),
    )


bpy.utils.register_class(CyclesRenderConfig)
bpy.utils.register_class(EeveeRenderConfig)


@config_subsection_register("render")
class RenderConfig(TraitBlenderConfig):
    print_index = 5

    engine: bpy.props.EnumProperty(
        name="Engine",
        description="The engine to use",
        items=_render_engine_items,
        get=_get_render_engine,
        set=_set_render_engine,
    )

    cycles: PointerProperty(type=CyclesRenderConfig, name="Cycles")
    eevee: PointerProperty(type=EeveeRenderConfig, name="Eevee")

    eevee_use_raytracing: BoolProperty(
        name="Use Raytracing (legacy)",
        description="Deprecated: use render.eevee.use_raytracing",
        default=False,
        get=get_property("bpy.context.scene.eevee.use_raytracing"),
        set=set_property("bpy.context.scene.eevee.use_raytracing"),
        options={'HIDDEN'},
    )

    def _to_yaml(self, indent_level=0, parent_path=""):
        """Export engine + only the active engine's settings from live scene RNA."""
        indent = "  " * indent_level
        child = "  " * (indent_level + 1)
        scene = bpy.context.scene
        engine = normalize_render_engine_value(scene.render.engine)
        lines = [f"{indent}engine: {engine}"]

        if _is_cycles_engine(engine):
            snap = _snapshot_mapping(getattr(scene, "cycles", None), CYCLES_SCENE_KEYS)
            lines.append(f"{indent}cycles:")
            for key in CYCLES_SCENE_KEYS:
                if key not in snap:
                    continue
                val = snap[key]
                if isinstance(val, bool):
                    lines.append(f"{child}{key}: {str(val).lower()}")
                else:
                    lines.append(f"{child}{key}: {val}")
        elif _is_eevee_engine(engine):
            snap = _snapshot_mapping(getattr(scene, "eevee", None), EEVEE_SCENE_KEYS)
            lines.append(f"{indent}eevee:")
            for key in EEVEE_SCENE_KEYS:
                if key not in snap:
                    continue
                val = snap[key]
                if isinstance(val, bool):
                    lines.append(f"{child}{key}: {str(val).lower()}")
                else:
                    lines.append(f"{child}{key}: {val}")

        return "\n".join(lines)

    def from_dict(self, data_dict):
        if not isinstance(data_dict, dict):
            return
        data = dict(data_dict)
        scene = bpy.context.scene

        if "engine" in data:
            raw = data.pop("engine")
            engine = normalize_render_engine_value(raw)
            try:
                actual = try_set_render_engine(scene, raw)
                print(
                    f"TraitBlender: render.engine from config "
                    f"raw={raw!r} normalized={engine!r} actual={actual!r}"
                )
            except Exception as e:
                print(f"TraitBlender: Failed to apply render.engine '{engine}': {e}")

        cycles_data = data.pop("cycles", None)
        eevee_data = data.pop("eevee", None)

        if "eevee_use_raytracing" in data:
            legacy = data.pop("eevee_use_raytracing")
            if not isinstance(eevee_data, dict):
                eevee_data = {}
            eevee_data.setdefault("use_raytracing", legacy)

        # Write straight to scene RNA — nested PropertyGroup setters are unreliable here.
        if isinstance(cycles_data, dict):
            errs = _apply_mapping_to_id(
                getattr(scene, "cycles", None), cycles_data, CYCLES_SCENE_KEYS
            )
            for err in errs:
                print(f"TraitBlender: cycles config apply: {err}")
            applied = _snapshot_mapping(getattr(scene, "cycles", None), CYCLES_SCENE_KEYS)
            print(f"TraitBlender: cycles applied -> {applied}")

        if isinstance(eevee_data, dict):
            errs = _apply_mapping_to_id(
                getattr(scene, "eevee", None), eevee_data, EEVEE_SCENE_KEYS
            )
            for err in errs:
                print(f"TraitBlender: eevee config apply: {err}")
            applied = _snapshot_mapping(getattr(scene, "eevee", None), EEVEE_SCENE_KEYS)
            print(f"TraitBlender: eevee applied -> {applied}")

        if data:
            super().from_dict(data)
