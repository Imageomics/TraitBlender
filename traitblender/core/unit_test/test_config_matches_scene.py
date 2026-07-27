"""
Compare the YAML config file on disk to the live scene / TraitBlender config.

Reports paths where expected (file) and actual (scene) differ.
"""

from __future__ import annotations

import os
from typing import Any

import bpy
import yaml

from ..helpers.render_engine_compat import normalize_render_engine_value


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    try:
        return list(value)
    except Exception:
        return [value]


def _values_equal(expected: Any, actual: Any, *, rtol: float = 1e-5, atol: float = 1e-6) -> bool:
    """Loose equality for YAML vs Blender RNA values."""
    if expected is None and actual is None:
        return True

    if isinstance(expected, bool) or isinstance(actual, bool):
        return bool(expected) == bool(actual)

    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(expected) - float(actual)) <= (atol + rtol * abs(float(expected)))

    if isinstance(expected, (list, tuple)) or (
        actual is not None
        and hasattr(actual, "__iter__")
        and not isinstance(actual, (str, bytes, dict))
    ):
        exp_l = _as_list(expected)
        act_l = _as_list(actual)
        if len(exp_l) != len(act_l):
            return False
        return all(_values_equal(a, b, rtol=rtol, atol=atol) for a, b in zip(exp_l, act_l))

    if isinstance(expected, dict) and isinstance(actual, dict):
        if set(expected.keys()) != set(actual.keys()):
            return False
        return all(_values_equal(expected[k], actual[k], rtol=rtol, atol=atol) for k in expected)

    return str(expected).strip() == str(actual).strip()


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_fmt(v) for v in value) + "]"
    return repr(value)


def _normalize_actual(actual: Any) -> Any:
    if actual is None or isinstance(actual, (str, bool, int, float, dict)):
        return actual
    if hasattr(actual, "__iter__"):
        return _as_list(actual)
    return actual


def _live_imaging_snapshot(imaging) -> dict:
    customs = {}
    for item in imaging.custom_orientations:
        name = (item.name or "").strip()
        if not name:
            continue
        customs[name] = [
            float(item.rotation[0]),
            float(item.rotation[1]),
            float(item.rotation[2]),
        ]
    return {
        "include_images": bool(imaging.include_images),
        "orientation_names": [item.name for item in imaging.orientation_options if item.enabled],
        "images_per_orientation": int(imaging.images_per_orientation),
        "custom_orientations": customs,
    }


def _live_morphospace_snapshot(morphospace) -> dict:
    try:
        hyper = dict(morphospace._get_hyperparams_dict() or {})
    except Exception:
        hyper = {}
    return {
        "name": morphospace.name,
        "hyperparams": hyper,
    }


def _live_value(section, key: str, context):
    """Read one YAML-schema field from a live config section / scene."""
    cls_name = section.__class__.__name__

    if cls_name == "RenderConfig" and key == "engine":
        return normalize_render_engine_value(context.scene.render.engine)

    # Always compare Cycles/Eevee YAML keys to live scene RNA (not PropertyGroup getters).
    if cls_name == "CyclesRenderConfig":
        cycles = getattr(context.scene, "cycles", None)
        if cycles is not None and hasattr(cycles, key):
            return getattr(cycles, key)

    if cls_name == "EeveeRenderConfig":
        eevee = getattr(context.scene, "eevee", None)
        if eevee is not None and hasattr(eevee, key):
            return getattr(eevee, key)

    if cls_name == "ImagingConfig":
        snap = _live_imaging_snapshot(section)
        if key in snap:
            return snap[key]

    if cls_name == "MorphospaceConfig":
        snap = _live_morphospace_snapshot(section)
        if key in snap:
            return snap[key]

    return getattr(section, key)


def _add_mismatch(mismatches, path, expected, actual, reason):
    mismatches.append(
        {
            "path": path,
            "expected": expected,
            "actual": _normalize_actual(actual),
            "reason": reason,
        }
    )


def _compare_section(path: str, expected: dict, section, context, mismatches: list) -> None:
    """Compare a YAML mapping to one live config PropertyGroup section."""
    for key, exp_val in expected.items():
        if key == "show":
            continue
        child_path = f"{path}.{key}" if path else key

        if key == "hyperparams" and isinstance(exp_val, dict):
            actual = _live_morphospace_snapshot(section).get("hyperparams", {})
            for hk, hv in exp_val.items():
                hpath = f"{child_path}.{hk}"
                if hk not in actual:
                    _add_mismatch(mismatches, hpath, hv, None, "hyperparam missing in live config")
                elif not _values_equal(hv, actual[hk]):
                    _add_mismatch(mismatches, hpath, hv, actual[hk], "value mismatch")
            continue

        if key == "custom_orientations" and isinstance(exp_val, dict):
            actual_customs = _live_imaging_snapshot(section).get("custom_orientations", {})
            for name, rot in exp_val.items():
                cpath = f"{child_path}.{name}"
                if name not in actual_customs:
                    _add_mismatch(
                        mismatches, cpath, rot, None, "custom orientation missing in live config"
                    )
                elif not _values_equal(rot, actual_customs[name]):
                    _add_mismatch(mismatches, cpath, rot, actual_customs[name], "value mismatch")
            continue

        if key == "orientation_names":
            try:
                actual = _live_value(section, key, context)
            except Exception as e:
                _add_mismatch(mismatches, child_path, exp_val, None, f"failed to read: {e}")
                continue
            exp_set = set(exp_val) if isinstance(exp_val, list) else set()
            act_set = set(actual) if isinstance(actual, list) else set()
            if exp_set != act_set:
                _add_mismatch(
                    mismatches,
                    child_path,
                    sorted(exp_set),
                    sorted(act_set),
                    "enabled orientation set mismatch",
                )
            continue

        # Nested config subsection (e.g. render.cycles / render.eevee)
        if isinstance(exp_val, dict):
            # Prefer comparing Cycles/Eevee blocks straight to scene RNA.
            if path == "render" and key == "cycles":
                cycles = getattr(context.scene, "cycles", None)
                if cycles is None:
                    _add_mismatch(
                        mismatches, child_path, exp_val, None, "scene.cycles is missing"
                    )
                    continue
                for ck, cv in exp_val.items():
                    cpath = f"{child_path}.{ck}"
                    if not hasattr(cycles, ck):
                        _add_mismatch(
                            mismatches, cpath, cv, None, f"scene.cycles has no attribute {ck!r}"
                        )
                        continue
                    try:
                        actual = getattr(cycles, ck)
                    except Exception as e:
                        _add_mismatch(mismatches, cpath, cv, None, f"failed to read: {e}")
                        continue
                    if not _values_equal(cv, actual):
                        _add_mismatch(mismatches, cpath, cv, actual, "value mismatch")
                continue

            if path == "render" and key == "eevee":
                eevee = getattr(context.scene, "eevee", None)
                if eevee is None:
                    _add_mismatch(
                        mismatches, child_path, exp_val, None, "scene.eevee is missing"
                    )
                    continue
                for ek, ev in exp_val.items():
                    epath = f"{child_path}.{ek}"
                    if not hasattr(eevee, ek):
                        _add_mismatch(
                            mismatches, epath, ev, None, f"scene.eevee has no attribute {ek!r}"
                        )
                        continue
                    try:
                        actual = getattr(eevee, ek)
                    except Exception as e:
                        _add_mismatch(mismatches, epath, ev, None, f"failed to read: {e}")
                        continue
                    if not _values_equal(ev, actual):
                        _add_mismatch(mismatches, epath, ev, actual, "value mismatch")
                continue

            child = getattr(section, key, None)
            if child is not None and callable(getattr(child, "from_dict", None)):
                _compare_section(child_path, exp_val, child, context, mismatches)
                continue
            _add_mismatch(
                mismatches,
                child_path,
                exp_val,
                None,
                "nested mapping could not be compared (no matching subsection)",
            )
            continue

        try:
            actual = _live_value(section, key, context)
        except Exception as e:
            _add_mismatch(mismatches, child_path, exp_val, None, f"failed to read: {e}")
            continue

        if key == "engine" and section.__class__.__name__ == "RenderConfig":
            # already handled via _live_value
            pass

        if not _values_equal(exp_val, actual):
            reason = "value mismatch"
            if key == "engine" and section.__class__.__name__ == "RenderConfig":
                try:
                    rna_ids = sorted(
                        item.identifier
                        for item in context.scene.render.bl_rna.properties["engine"].enum_items
                    )
                except Exception:
                    rna_ids = []
                reason = (
                    "value mismatch (test only compares; it does not apply YAML — "
                    "run bpy.ops.traitblender.configure_scene() first). "
                    f"scene.render.engine={context.scene.render.engine!r}; "
                    f"RNA engines={rna_ids}"
                )
            _add_mismatch(mismatches, child_path, exp_val, actual, reason)


# Sections that are UI-only / not meaningful to compare from YAML.
# Bare ``sample:`` (null) or ``sample: {}`` must never count as a mismatch.
_SKIP_ROOT_KEYS = frozenset({"sample"})


def _compare_root(expected: dict, root, context, mismatches: list) -> None:
    annotations = getattr(root.__class__, "__annotations__", {}) or {}

    for key, exp_val in expected.items():
        if key in _SKIP_ROOT_KEYS:
            continue
        # Bare section keys like `sample:` → None, or empty `{}` — nothing to check
        if exp_val is None or exp_val == {}:
            continue

        if key not in annotations:
            _add_mismatch(
                mismatches, key, exp_val, None, "key not present on live TraitBlender config"
            )
            continue

        section = getattr(root, key, None)
        if section is None:
            _add_mismatch(mismatches, key, exp_val, None, "live section is None")
            continue

        if isinstance(exp_val, dict) and callable(getattr(section, "from_dict", None)):
            _compare_section(key, exp_val, section, context, mismatches)
            continue

        # Non-dict root fields (e.g. transforms list)
        try:
            actual = getattr(root, key)
        except Exception as e:
            _add_mismatch(mismatches, key, exp_val, None, f"failed to read: {e}")
            continue
        if not _values_equal(exp_val, actual):
            _add_mismatch(mismatches, key, exp_val, actual, "value mismatch")


def test_config_matches_scene(context=None) -> dict:
    """
    Load ``traitblender_setup.config_file`` and compare each YAML field to the
    live scene / TraitBlender config values.

    Returns:
        dict with keys: name, passed, mismatches, message, config_file
    """
    context = context or bpy.context
    setup = context.scene.traitblender_setup
    config_file = (setup.config_file or "").strip()
    result = {
        "name": "config_matches_scene",
        "passed": False,
        "mismatches": [],
        "message": "",
        "config_file": config_file,
    }

    if not config_file:
        result["message"] = "No config file set on traitblender_setup.config_file"
        return result
    if not os.path.isfile(config_file):
        result["message"] = f"Config file not found: {config_file}"
        return result

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            expected = yaml.safe_load(f)
    except Exception as e:
        result["message"] = f"Failed to read config YAML: {e}"
        return result

    if not isinstance(expected, dict):
        result["message"] = "Config YAML root must be a mapping"
        return result

    mismatches: list = []
    _compare_root(expected, context.scene.traitblender_config, context, mismatches)

    result["mismatches"] = mismatches
    result["passed"] = len(mismatches) == 0
    if result["passed"]:
        result["message"] = f"All checked fields match scene ({config_file})"
    else:
        lines = [f"{len(mismatches)} mismatch(es) vs {config_file}:"]
        for m in mismatches:
            lines.append(
                f"  - {m['path']}: expected {_fmt(m['expected'])}, "
                f"actual {_fmt(m['actual'])} ({m.get('reason', 'mismatch')})"
            )
        result["message"] = "\n".join(lines)
    return result
