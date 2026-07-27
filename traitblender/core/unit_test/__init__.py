"""
TraitBlender in-addon unit tests.

Each module exposes a test callable ``test_*(context=None) -> dict``.
``TESTS`` maps stable names to those callables.

Pass ``test_name="help"`` to ``run_test`` / the operator to list all tests
and their docstrings.
"""

from .test_config_matches_scene import test_config_matches_scene

TESTS = {
    "config_matches_scene": test_config_matches_scene,
}

HELP_NAME = "help"


def list_tests():
    """Return registered test names."""
    return list(TESTS.keys())


def help_tests() -> str:
    """Return a printable catalog of test names and docstrings."""
    lines = ["TraitBlender unit tests:", ""]
    if not TESTS:
        lines.append("  (none registered)")
        return "\n".join(lines)

    for name in list_tests():
        fn = TESTS[name]
        doc = (getattr(fn, "__doc__", None) or "").strip() or "(no docstring)"
        doc_lines = [ln.rstrip() for ln in doc.splitlines()]
        lines.append(f"  {name}")
        for ln in doc_lines:
            lines.append(f"    {ln}" if ln else "")
        lines.append("")
    lines.append('Run: bpy.ops.traitblender.run_unit_test(test_name="<name>")')
    lines.append(f'Help: bpy.ops.traitblender.run_unit_test(test_name="{HELP_NAME}")')
    return "\n".join(lines).rstrip() + "\n"


def run_test(name, context=None):
    """
    Run a registered test by name.

    Args:
        name: Key in ``TESTS``, or ``\"help\"`` to list tests and docstrings.
        context: Optional Blender context.

    Returns:
        dict: Test result (at least ``passed`` and ``message``).
        For ``help``, ``passed`` is True and ``message`` is the catalog text.

    Raises:
        KeyError: Unknown test name.
    """
    key = (name or "").strip()
    if key.lower() == HELP_NAME:
        message = help_tests()
        return {
            "name": HELP_NAME,
            "passed": True,
            "mismatches": [],
            "message": message,
            "help": True,
        }
    if key not in TESTS:
        known = ", ".join(list_tests()) or "(none)"
        raise KeyError(
            f"Unknown unit test '{name}'. Known: {known}. "
            f'Use test_name="{HELP_NAME}" for details.'
        )
    return TESTS[key](context)


__all__ = [
    "TESTS",
    "HELP_NAME",
    "list_tests",
    "help_tests",
    "run_test",
    "test_config_matches_scene",
]
