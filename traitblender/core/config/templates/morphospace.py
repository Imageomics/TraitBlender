"""
Morphospace configuration.

name: Selected morphospace (syncs with traitblender_setup.available_morphospaces), default Shell (Default).
hyperparams: Flat hyperparameter overrides {param: value}. Defaults from morphospace module's HYPERPARAMETERS.
"""

from bpy.props import StringProperty
import yaml
from .. import config_subsection_register, TraitBlenderConfig
from ...helpers import get_property, set_property
from ...morphospaces import get_hyperparameters_for_morphospace, normalize_morphospace_name

_SET_AVAILABLE_MORPHOSPACE = set_property(
    "bpy.context.scene.traitblender_setup.available_morphospaces",
    object_dependencies=None,
    fail_silently=True,
)


def _set_morphospace_name(self, value):
    """Apply legacy aliases (e.g. ATLAS → MorphoWeave) before writing the enum."""
    if value:
        canonical = normalize_morphospace_name(value)
        if canonical != value:
            print(
                f"TraitBlender: morphospace '{value}' is now '{canonical}' "
                f"(legacy alias); update configs when convenient."
            )
            value = canonical
    _SET_AVAILABLE_MORPHOSPACE(self, value)


@config_subsection_register("morphospace")
class MorphospaceConfig(TraitBlenderConfig):
    """Stores morphospace selection and hyperparameter overrides."""

    print_index = -1  # Put near start of config

    name: StringProperty(
        name="Morphospace",
        description="Selected morphospace module (syncs with morphospaces panel)",
        default="Shell (Default)",
        get=get_property("bpy.context.scene.traitblender_setup.available_morphospaces", object_dependencies=None, default="Shell (Default)"),
        set=_set_morphospace_name,
    )

    hyperparams_state: StringProperty(
        name="Hyperparameters State",
        description="YAML: hyperparameter overrides {param: value}",
        default="",
    )

    def _get_hyperparams_dict(self):
        """Parse hyperparams_state to flat dict {param: value}."""
        if not self.hyperparams_state or not self.hyperparams_state.strip():
            return {}
        try:
            data = yaml.safe_load(self.hyperparams_state)
            return data if isinstance(data, dict) else {}
        except Exception as e:
            print(f"TraitBlender: Error parsing morphospace hyperparams: {e}")
            return {}

    def _set_hyperparams_dict(self, data):
        """Serialize flat dict to hyperparams_state."""
        if not data:
            self.hyperparams_state = ""
            return
        try:
            self.hyperparams_state = yaml.dump(data, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"TraitBlender: Error serializing morphospace hyperparams: {e}")

    def _scoped_hyperparam_overrides(self, morphospace_name):
        """Overrides in hyperparams_state that apply to this morphospace only."""
        module_keys = get_hyperparameters_for_morphospace(morphospace_name).keys()
        return {k: v for k, v in self._get_hyperparams_dict().items() if k in module_keys}

    def get_hyperparams_for(self, morphospace_name):
        """Get merged hyperparameters. Module defaults + config overrides for this morphospace only."""
        module_defaults = get_hyperparameters_for_morphospace(morphospace_name)
        return {**module_defaults, **self._scoped_hyperparam_overrides(morphospace_name)}

    def set_hyperparam(self, morphospace_name, key, value):
        """Set one hyperparameter."""
        data = self._get_hyperparams_dict()
        data[key] = value
        self._set_hyperparams_dict(data)

    def get_hyperparam(self, morphospace_name, key):
        """Get one hyperparameter (merged with module defaults)."""
        merged = self.get_hyperparams_for(morphospace_name)
        return merged.get(key)

    def _to_yaml(self, indent_level=0, parent_path=""):
        """Format morphospace section for YAML export (called as nested section)."""
        indent = "  " * indent_level
        result = []
        result.append(f"{indent}name: {self.name}")
        data = self._scoped_hyperparam_overrides(self.name)
        result.append(f"{indent}hyperparams:")
        if not data:
            result.append(f"{indent}  {{}}")
        else:
            for k, v in sorted(data.items()):
                if isinstance(v, bool):
                    result.append(f"{indent}  {k}: {str(v).lower()}")
                else:
                    result.append(f"{indent}  {k}: {v}")
        return "\n".join(result)

    def to_dict(self):
        """Return morphospace config for config export."""
        data = self._scoped_hyperparam_overrides(self.name)
        return {"name": self.name, "hyperparams": data if data else {}}

    def from_dict(self, data_dict):
        """Load morphospace config from dict (YAML import)."""
        if not data_dict or not isinstance(data_dict, dict):
            return
        if "name" in data_dict:
            import bpy

            setup = bpy.context.scene.traitblender_setup
            # Avoid morphospace-switch confirm popup mid Configure Scene (it reverts the enum).
            setup.suppress_morphospace_update = True
            try:
                self.name = data_dict["name"]
                setup.prev_morphospace = setup.available_morphospaces
                setup.pending_morphospace = ""
            finally:
                setup.suppress_morphospace_update = False
        hyperparams = data_dict.get("hyperparams")
        if isinstance(hyperparams, dict):
            module_keys = get_hyperparameters_for_morphospace(self.name).keys()
            scoped = {k: v for k, v in hyperparams.items() if k in module_keys}
            self._set_hyperparams_dict(scoped)
