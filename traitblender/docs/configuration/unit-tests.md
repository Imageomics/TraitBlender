# Unit Tests

**This section is for TraitBlender developers.**

TraitBlender ships a small set of **in-addon unit tests** you can run from the Blender Python console (or headless scripts). They check that the live scene matches expectations after you configure it.

## Running tests

```python
# List registered tests and their docstrings
bpy.ops.traitblender.run_unit_test(test_name="help")

# Run a specific test
bpy.ops.traitblender.run_unit_test(test_name="config_matches_scene")
```

You can also call the registry directly:

```python
from bl_ext.user_default.traitblender.core.unit_test import run_test, list_tests, help_tests

print(help_tests())
result = run_test("config_matches_scene")
print(result["passed"], result["message"])
```

Results are printed to the Blender console. The operator reports `PASS` or `FAIL` in the status bar; full mismatch details go to the console.

## `config_matches_scene`

Compares the YAML at `bpy.context.scene.traitblender_setup.config_file` to the live scene and the TraitBlender config.

**Prerequisites**

1. Import the museum scene.
2. Load a config with **Configure Scene** (or set `traitblender_setup.config_file` yourself, then configure).
3. Run the test.

If you use **Configure Scene** with an empty Config File field, the file browser path is written back to `config_file` after a successful load so the UI and this test share the same path.

**What it checks**

- Nested config sections present in the YAML (world, camera, lamp, mat, render, output, metadata, ruler, imaging, meshes, morphospace, transforms, dataset, …).
- For `render.cycles` / `render.eevee`, values are compared against live Blender RNA (`scene.cycles` / `scene.eevee`), including final-render vs viewport sampling keys (`samples` vs `preview_samples`, etc.).
- `render.engine` is normalized the same way Configure Scene applies it.


**Return value**

```text
{
  "name": "config_matches_scene",
  "passed": True | False,
  "mismatches": [ {"path", "expected", "actual", "reason"}, ... ],
  "message": "...",
  "config_file": "..."
}
```

## Adding tests

Register new callables in `core/unit_test/__init__.py` under `TESTS`. Each test should accept an optional `context` and return a dict with at least `passed` and `message` (for developers).
