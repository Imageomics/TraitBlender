"""
Operator: run a TraitBlender core unit test by name.
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

from ....core.unit_test import HELP_NAME, TESTS, run_test


class TRAITBLENDER_OT_run_unit_test(Operator):
    """Run a registered TraitBlender unit test and report mismatches"""

    bl_idname = "traitblender.run_unit_test"
    bl_label = "Run Unit Test"
    bl_description = (
        "Run a TraitBlender unit test by name "
        f'(test_name="{HELP_NAME}" lists all tests)'
    )
    bl_options = {'REGISTER'}

    test_name: StringProperty(
        name="Test Name",
        description=f'Key from core.unit_test.TESTS, or "{HELP_NAME}" to list tests',
        default=HELP_NAME,
    )

    def execute(self, context):
        name = (self.test_name or "").strip()
        if not name:
            self.report({'ERROR'}, "No test_name provided")
            return {'CANCELLED'}

        try:
            result = run_test(name, context)
        except KeyError as e:
            known = ", ".join(TESTS.keys()) or "(none)"
            self.report({'ERROR'}, f"{e} Known tests: {known}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Unit test '{name}' crashed: {e}")
            print(f"TraitBlender: unit test '{name}' crashed: {e}")
            return {'CANCELLED'}

        message = result.get("message") or ""
        print(message)

        if result.get("help"):
            self.report({'INFO'}, f"Listed {len(TESTS)} unit test(s) (see console)")
            return {'FINISHED'}

        passed = bool(result.get("passed"))
        mismatches = result.get("mismatches") or []
        print(f"TraitBlender unit test [{name}]: {'PASS' if passed else 'FAIL'}")
        if mismatches:
            for m in mismatches:
                print(
                    f"  mismatch {m.get('path')}: "
                    f"expected={m.get('expected')!r} actual={m.get('actual')!r} "
                    f"({m.get('reason')})"
                )

        short = message.splitlines()[0] if message else name
        if passed:
            self.report({'INFO'}, f"PASS {name}: {short}")
            return {'FINISHED'}

        self.report({'WARNING'}, f"FAIL {name}: {short}")
        return {'FINISHED'}
