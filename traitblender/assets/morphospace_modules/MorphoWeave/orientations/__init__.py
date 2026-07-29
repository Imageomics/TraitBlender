"""
MorphoWeave specimen orientations.

Default: table placement only (tb_location). Other views: rotate one axis by n·π/4
(n = 1..7), origin to bounds, tb_location reset — then apply_orientation bakes rotation.
"""

from __future__ import annotations

import math
from math import gcd

import bpy


def _orient_morphoweave_default(sample_obj):
    sample_obj.tb_location = (0.0, 0.0, 0.0)


def _pi_multiplier_label(n_quarters: int) -> str:
    num = n_quarters
    den = 4
    g = gcd(num, den)
    num //= g
    den //= g
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def _make_morphoweave_axis_rotation(axis: str, n_quarters: int):
    angle = (math.pi / 4.0) * n_quarters
    label = _pi_multiplier_label(n_quarters)
    name = f"{axis} {label} π Rotation"

    def orient(sample_obj):
        _orient_morphoweave_default(sample_obj)
        if axis == "X":
            sample_obj.tb_rotation = (angle, 0.0, 0.0)
        elif axis == "Y":
            sample_obj.tb_rotation = (0.0, angle, 0.0)
        else:
            sample_obj.tb_rotation = (0.0, 0.0, angle)

        bpy.context.view_layer.objects.active = sample_obj
        sample_obj.select_set(True)
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
        sample_obj.tb_location = (0.0, 0.0, 0.0)
        bpy.context.view_layer.update()

    orient.__name__ = f"_orient_morphoweave_{axis}_{n_quarters}q"
    return name, orient


def _build_orientations() -> dict:
    out: dict = {"Default": _orient_morphoweave_default}
    for axis in ("X", "Y", "Z"):
        for n in range(1, 8):
            key, fn = _make_morphoweave_axis_rotation(axis, n)
            out[key] = fn
    return out


ORIENTATIONS = _build_orientations()

__all__ = ["ORIENTATIONS"]
