"""
TraitBlenderConfig base class for all TraitBlender configuration property groups.
"""

import bpy
from ..helpers import get_property_type


class TraitBlenderConfig(bpy.types.PropertyGroup):
    """Base class for all TraitBlender configuration property groups."""

    show: bpy.props.BoolProperty(
        name="Show",
        description="Show this section in the UI",
        default=False
    )

    def __str__(self):
        """Recursively display all parameters and their values in YAML format."""
        return self._to_yaml()

    def _to_yaml(self, indent_level=0, parent_path=""):
        """Convert the configuration to YAML format with proper indentation."""
        result = []
        indent = "  " * indent_level
        missing_any = False

        if indent_level == 0:
            result.append('---')

        properties_to_sort = []

        for prop_name in self.__class__.__annotations__.keys():
            if prop_name == "show":
                continue
            try:
                prop_value = getattr(self, prop_name)
                print_index = getattr(prop_value, 'print_index', float('inf')) if hasattr(prop_value, 'print_index') else float('inf')
                properties_to_sort.append((print_index, prop_name, prop_value))
            except Exception:
                properties_to_sort.append((float('inf'), prop_name, None))

        properties_to_sort.sort(key=lambda x: (x[0], x[1]))

        for print_index, prop_name, prop_value in properties_to_sort:
            try:
                if prop_value is None:
                    result.append(f"{indent}{prop_name}: # missing required Blender objects")
                    missing_any = True
                    continue

                if isinstance(prop_value, TraitBlenderConfig):
                    current_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
                    nested_yaml = prop_value._to_yaml(indent_level + 1, current_path)
                    # Skip empty sections (e.g. sample is UI-only and returns "")
                    if not nested_yaml.strip():
                        continue
                    result.append(f"{indent}{prop_name}:")
                    result.append(nested_yaml)
                else:
                    current_path = f"{parent_path}.{prop_name}" if parent_path else prop_name
                    prop_type = get_property_type(current_path)
                    yaml_value = self._format_value_for_yaml(prop_value, prop_type)
                    result.append(f"{indent}{prop_name}: {yaml_value}")
            except Exception:
                result.append(f"{indent}{prop_name}: # missing required Blender objects")
                missing_any = True

        yaml_str = '\n'.join(result)
        if indent_level == 0 and missing_any:
            yaml_str += ("\n\n[TraitBlender] Some configuration values are missing. "
                         "To fix this, run the following in the Blender Python console to set up the scene:\n"
                         "    bpy.ops.traitblender.setup_scene()\n"
                         "This will create any required objects (such as Camera, World, etc.) that are missing.")
        return yaml_str

    def _format_value_for_yaml(self, value, prop_type=None):
        """Format a value appropriately for YAML output."""
        if value is None:
            return "null"

        if prop_type in ['FloatVectorProperty', 'IntVectorProperty', 'BoolVectorProperty']:
            try:
                items = [str(item) for item in value]
                return f"[{', '.join(items)}]"
            except Exception:
                return str(value)
        elif prop_type == 'EnumProperty':
            return str(value)
        elif prop_type in ['FloatProperty', 'IntProperty']:
            return str(value)
        elif prop_type == 'BoolProperty':
            return str(value).lower()
        elif prop_type == 'StringProperty':
            if isinstance(value, str) and ('/' in value or '\\' in value):
                value = value.replace('\\', '/')
            if not value or any(char in value for char in '":{}[]&*#?|-<>=!%@`\''):
                return f'"{value}"'
            return value
        else:
            return str(value)

    def from_dict(self, data_dict):
        """Load configuration values from a dictionary."""
        if not isinstance(data_dict, dict):
            raise ValueError("Input must be a dictionary")

        annotations = getattr(self.__class__, "__annotations__", {}) or {}
        for prop_name, value in data_dict.items():
            if prop_name not in annotations:
                continue
            # Bare YAML keys like `sample:` become None — never assign onto PointerProperties.
            if value is None:
                continue

            current_prop = getattr(self, prop_name, None)
            # Duck-type nested sections: isinstance(PropertyGroup, TraitBlenderConfig)
            # can fail across Blender register/reload boundaries.
            from_dict_fn = getattr(current_prop, "from_dict", None)
            if callable(from_dict_fn):
                if isinstance(value, (dict, list)):
                    from_dict_fn(value)
                # Nested section with a non-mapping value: ignore
                continue

            try:
                setattr(self, prop_name, value)
            except Exception as e:
                print(f"TraitBlender: Failed to set config '{prop_name}': {e}")

    def to_dict(self):
        """Convert the configuration to a dictionary."""
        result = {}

        for prop_name in self.__class__.__annotations__.keys():
            if prop_name == "show":
                continue
            prop_value = getattr(self, prop_name)
            if isinstance(prop_value, TraitBlenderConfig):
                result[prop_name] = prop_value.to_dict()
            else:
                if hasattr(prop_value, '__iter__') and not isinstance(prop_value, str):
                    try:
                        result[prop_name] = list(prop_value)
                    except Exception:
                        result[prop_name] = str(prop_value)
                else:
                    result[prop_name] = prop_value

        return result

    def get_config_sections(self):
        """Get all nested TraitBlenderConfig sections in this configuration."""
        sections = {}

        for prop_name in self.__class__.__annotations__.keys():
            try:
                prop_value = getattr(self, prop_name)
                if isinstance(prop_value, TraitBlenderConfig):
                    sections[prop_name] = prop_value
            except Exception:
                continue

        return sections
