"""Discovery of available morphospaces."""

import os

from ..helpers import get_asset_path
from .get_orientations import get_orientations_for_morphospace

# GUI dropdown order (folder names under morphospace_modules/)
_MORPHOSPACE_ORDER = ("Shell", "CircleGrid", "MorphoWeave")


def list_morphospaces():
    """
    List all available morphospaces by scanning the assets/morphospace_modules directory.
    Only morphospaces with a required 'Default' orientation are listed.
    
    Returns:
        list: List of morphospace names (folder names)
    """
    morphospace_modules_path = get_asset_path("morphospace_modules")
    
    if not os.path.exists(morphospace_modules_path):
        return []
    
    morphospaces = []
    try:
        for item in os.listdir(morphospace_modules_path):
            item_path = os.path.join(morphospace_modules_path, item)
            # Check if it's a directory and has an __init__.py file
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
                # Require Default orientation
                orientations = get_orientations_for_morphospace(item)
                if 'Default' in orientations and callable(orientations.get('Default')):
                    morphospaces.append(item)
                else:
                    print(f"TraitBlender: Skipping morphospace '{item}' - missing required 'Default' in ORIENTATIONS")
    except Exception as e:
        print(f"Error listing morphospaces: {e}")
        return []
    
    order_rank = {name: i for i, name in enumerate(_MORPHOSPACE_ORDER)}
    return sorted(
        morphospaces,
        key=lambda folder: (order_rank.get(folder, len(order_rank)), folder),
    )
