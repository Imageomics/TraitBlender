"""
Blender version differences: Eevee render.engine enum id varies (BLENDER_EEVEE_NEXT vs BLENDER_EEVEE).

IMPORTANT (Blender 5.1+): ``RenderSettings.engine`` RNA ``enum_items`` often only
lists the *currently selected* engine (e.g. ``['BLENDER_EEVEE']``), not every
installed engine. Never use that list to decide that CYCLES is "invalid" — direct
assignment ``scene.render.engine = "CYCLES"`` still works.
"""

from __future__ import annotations

import bpy

# Stable EnumProperty numbers for get/set (not list indices).
ENGINE_NUM_CYCLES = 0
ENGINE_NUM_EEVEE = 1
ENGINE_NUM_WORKBENCH = 2

# Known engine identifiers (assignment targets). Not derived from incomplete RNA enums.
_KNOWN_ENGINES = (
    "CYCLES",
    "BLENDER_EEVEE",
    "BLENDER_EEVEE_NEXT",
    "BLENDER_WORKBENCH",
)

# Keep a hard reference to dynamic enum item strings (Blender requirement).
_RENDER_ENGINE_ITEMS_CACHE: list[tuple] = []


def _engine_enum_identifiers() -> list[str]:
    """
    Best-effort RNA identifiers for render.engine.

    May be incomplete on Blender 5.1+ (often only the active engine). Prefer
    ``_KNOWN_ENGINES`` / try-assign for apply paths.
    """
    ids: list[str] = []
    try:
        scene = bpy.context.scene
        prop = scene.render.bl_rna.properties["engine"]
        ids = [item.identifier for item in prop.enum_items]
    except Exception:
        pass
    if not ids:
        try:
            prop = bpy.types.RenderSettings.bl_rna.properties["engine"]
            ids = [item.identifier for item in prop.enum_items]
        except Exception:
            ids = []
    return ids


def get_eevee_engine_identifier() -> str:
    ids = set(_engine_enum_identifiers())
    # Prefer whatever RNA currently exposes; else Blender 5 name, then legacy.
    if "BLENDER_EEVEE" in ids:
        return "BLENDER_EEVEE"
    if "BLENDER_EEVEE_NEXT" in ids:
        return "BLENDER_EEVEE_NEXT"
    # Blender 5 UI label is EEVEE; identifier is typically BLENDER_EEVEE.
    return "BLENDER_EEVEE"


def render_engine_enum_items() -> list[tuple]:
    """
    Enum items with stable integer ids for get/set callbacks.

    Blender EnumProperty get/set must return/accept these numbers (4th tuple
    element), not list indices. Keep a module reference so dynamic callbacks
    do not crash Blender.
    """
    global _RENDER_ENGINE_ITEMS_CACHE
    eevee = get_eevee_engine_identifier()
    _RENDER_ENGINE_ITEMS_CACHE = [
        ("CYCLES", "Cycles", "Cycles", ENGINE_NUM_CYCLES),
        (eevee, "Eevee", "Eevee", ENGINE_NUM_EEVEE),
        ("BLENDER_WORKBENCH", "Workbench", "Workbench", ENGINE_NUM_WORKBENCH),
    ]
    return _RENDER_ENGINE_ITEMS_CACHE


def render_engine_options() -> list[str]:
    return [item[0] for item in render_engine_enum_items()]


def render_engine_number_for_identifier(identifier: str) -> int:
    ident = normalize_render_engine_value(identifier)
    for item in render_engine_enum_items():
        if item[0] == ident:
            return item[3]
    return ENGINE_NUM_CYCLES


def render_engine_identifier_for_number(number: int) -> str:
    for item in render_engine_enum_items():
        if item[3] == number:
            return item[0]
    return "CYCLES"


def normalize_render_engine_value(value) -> str:
    """
    Map a config/YAML engine value to a ``scene.render.engine`` identifier.

    Does **not** demote known engines (e.g. CYCLES) to Eevee when RNA
    ``enum_items`` is incomplete — that was breaking Configure Scene on 5.1.
    """
    eevee = get_eevee_engine_identifier()
    ordered = ["CYCLES", eevee, "BLENDER_WORKBENCH"]

    if isinstance(value, int):
        if 0 <= value < len(ordered):
            return ordered[value]
        return "CYCLES"

    s = str(value).strip()
    if not s:
        return "CYCLES"

    # Friendly aliases
    upper = s.upper()
    if upper in ("EEVEE", "EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        if s in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
            # Prefer the id this build actually uses when we can see it
            ids = set(_engine_enum_identifiers())
            if s in ids:
                return s
            if "BLENDER_EEVEE" in ids:
                return "BLENDER_EEVEE"
            if "BLENDER_EEVEE_NEXT" in ids:
                return "BLENDER_EEVEE_NEXT"
            return eevee
        return eevee
    if upper == "CYCLES":
        return "CYCLES"
    if upper in ("WORKBENCH", "BLENDER_WORKBENCH"):
        return "BLENDER_WORKBENCH"

    if s in _KNOWN_ENGINES:
        return s

    # Unknown string: keep as-is so assignment can succeed or fail loudly
    return s


def try_set_render_engine(scene, engine) -> str:
    """
    Assign ``scene.render.engine`` and return the value that stuck.

    Raises:
        Exception: If assignment fails.
    """
    wanted = normalize_render_engine_value(engine)
    scene.render.engine = wanted
    return scene.render.engine
