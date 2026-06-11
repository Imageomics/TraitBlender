from __future__ import annotations

import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
import pandas as pd
import os
from io import StringIO
import warnings

from ..morphospaces import (
    get_trait_parameters_with_defaults_for_morphospace,
)
from ..morphospaces._module_loader import load_morphospace_module


def sync_sample_to_active_object(context=None):
    """
    If enabled, sync dataset.sample to the active object name when it exactly matches a row name.
    Returns True if sample changed, else False.
    """
    try:
        ctx = context or bpy.context
        scene = ctx.scene
        dataset = getattr(scene, "traitblender_dataset", None)
        if dataset is None:
            return False
        if not getattr(dataset, "sync_sample_with_active_object", True):
            return False

        view_layer = getattr(ctx, "view_layer", None) or bpy.context.view_layer
        active_obj = getattr(view_layer.objects, "active", None) if view_layer else None
        if active_obj is None:
            return False

        obj_name = active_obj.name
        rownames = dataset.rownames
        if obj_name in rownames and dataset.sample != obj_name:
            dataset.sample = obj_name
            return True
    except Exception:
        # Never break UI interaction if sync fails.
        return False
    return False


def _normalize_dataset_path(path: str) -> str:
    """Normalize dataset paths so local Windows paths are read as files, not URLs."""
    if not path:
        return path
    return os.path.normpath(path)


_SPECIES_COLUMN_NAMES = frozenset(
    {
        "species",
        "label",
        "tips",
        "tip",
        "sample",
        "samples",
        "name",
        "names",
        "id",
        "ids",
    }
)


def _norm_dataset_col(s: str) -> str:
    return str(s).lower().strip().replace(" ", "_")


def _find_species_column(df: pd.DataFrame):
    """First column whose normalized name is a species id, else first column."""
    for col in df.columns:
        if _norm_dataset_col(col) in _SPECIES_COLUMN_NAMES:
            return col
    return df.columns[0]


def _resync_dataframe_trait_columns(df: pd.DataFrame, traits_expected: dict) -> pd.DataFrame | None:
    """
    Rebuild trait columns to match traits_expected (order + names). Preserve values where
    column names match case-insensitively. Returns None if already aligned.
    """
    if df.empty or len(df.columns) == 0:
        return None
    species_col = _find_species_column(df)
    expected_order = list(traits_expected.keys())
    trait_cols_old = [c for c in df.columns if c != species_col]
    if [_norm_dataset_col(c) for c in trait_cols_old] == [
        _norm_dataset_col(c) for c in expected_order
    ]:
        return None
    out = pd.DataFrame()
    out[species_col] = df[species_col]
    lookup = {_norm_dataset_col(c): c for c in df.columns}
    for tname, default in traits_expected.items():
        nk = _norm_dataset_col(tname)
        if nk in lookup:
            out[tname] = df[lookup[nk]]
        else:
            out[tname] = default
    return out[[species_col] + expected_order]


def reset_sample_on_csv_change(self, context):
    """Reset sample selection when CSV data changes."""
    # Reset sample to first item when CSV changes
    if hasattr(self, 'sample'):
        try:
            # Get the current sample items to see what's available
            items = self._get_sample_items()
            if items and len(items) > 0:
                # Set to the first available item
                self.sample = items[0][0]  # Use the identifier (first element of tuple)
            else:
                self.sample = 0
        except Exception as e:
            print(f"TraitBlender: Error updating sample selection: {e}")
            self.sample = 0

def update_filepath(self, context):
    """Automatically import dataset when filepath changes"""
    if not self.filepath:
        # Clear CSV data if no file is selected
        self.csv = ""
        return
    
    dataset_path = _normalize_dataset_path(self.filepath)

    # Check if file exists
    if not os.path.exists(dataset_path):
        warnings.warn(
            f"TraitBlender: Dataset file not found: {dataset_path}. Regenerating default dataset.",
            UserWarning,
        )
        self.csv = self.get_csv_for_editing()
        return
    
    # Infer file type from extension
    file_ext = os.path.splitext(dataset_path)[1].lower()
    
    # Check if extension is supported
    if file_ext not in ['.csv', '.tsv', '.xlsx', '.xls']:
        warnings.warn(
            f"TraitBlender: Unsupported dataset file type '{file_ext}'. Expected CSV/TSV/XLSX.",
            UserWarning,
        )
        self.csv = self.get_csv_for_editing()
        return
    
    try:
        # Load the dataset based on the file extension
        if file_ext == '.csv':
            df = pd.read_csv(dataset_path)
        elif file_ext == '.tsv':
            df = pd.read_csv(dataset_path, sep='\t')
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(dataset_path)
        
        # Apply column reordering (same logic as _get_dataframe)
        if not df.empty and len(df.columns) > 0:
            # Define possible species/label column names (case-insensitive)
            species_column_names = ['species', 'label', 'tips', 'tip', 'sample', 'samples', 'name', 'names', 'id', 'ids']
            
            # Check if first column is already a species column
            first_col_lower = df.columns[0].lower().strip()
            if first_col_lower not in species_column_names:
                # Look for species columns in the dataset
                species_columns = []
                for col in df.columns:
                    col_lower = col.lower().strip()
                    if col_lower in species_column_names:
                        species_columns.append(col)
                
                if species_columns:
                    # Sort alphabetically and pick the first one
                    species_columns.sort()
                    species_col = species_columns[0]
                    
                    # Move the species column to the first position
                    cols = list(df.columns)
                    species_idx = cols.index(species_col)
                    
                    # Reorder columns: species column first, then the rest
                    new_cols = [species_col] + [col for i, col in enumerate(cols) if i != species_idx]
                    df = df[new_cols]
                    
                    print(f"TraitBlender: Moved '{species_col}' column to first position for species identification")
        
        # Validate columns against active morphospace:
        # - Missing trait columns are allowed (sample() will use defaults).
        # - Unknown columns are not allowed.
        # - Provided trait columns that are entirely empty are not allowed.
        morphospace_name = bpy.context.scene.traitblender_setup.available_morphospaces

        def _norm_col(s: str) -> str:
            return str(s).lower().strip().replace(" ", "_")

        species_column_names = {'species', 'label', 'tips', 'tip', 'sample', 'samples', 'name', 'names', 'id', 'ids'}
        trait_defaults = get_trait_parameters_with_defaults_for_morphospace(
            morphospace_name, context=bpy.context
        )
        allowed_traits = {_norm_col(t) for t in trait_defaults.keys()}

        unknown_columns = []
        empty_trait_columns = []
        for col in df.columns:
            norm = _norm_col(col)
            if norm in species_column_names:
                continue
            if norm not in allowed_traits:
                unknown_columns.append(col)
                continue
            # Treat blank strings as empty values too.
            cleaned = df[col].replace(r'^\s*$', pd.NA, regex=True)
            if cleaned.isna().all():
                empty_trait_columns.append(col)

        if unknown_columns:
            warnings.warn(
                "TraitBlender: Dataset contains columns not recognized by the selected morphospace.\n"
                f"  Unknown columns: {unknown_columns}\n"
                f"  Using morphospace default dataset instead of '{self.filepath}'.",
                UserWarning,
            )
            self.csv = self.get_csv_for_editing()
            return

        if empty_trait_columns:
            warnings.warn(
                "TraitBlender: Dataset contains trait columns with no values.\n"
                f"  Empty columns: {empty_trait_columns}\n"
                f"  Using morphospace default dataset instead of '{self.filepath}'.",
                UserWarning,
            )
            self.csv = self.get_csv_for_editing()
            return

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()
        
        # Store the CSV string in the dataset property
        self.csv = csv_string
        
        # Print success message
        rows, cols = df.shape
        print(f"TraitBlender: Dataset imported successfully: {rows} rows, {cols} columns")
        
    except Exception as e:
        warnings.warn(
            f"TraitBlender: Failed to import dataset from '{dataset_path}'. Regenerating default dataset. Error: {e}",
            UserWarning,
        )
        self.csv = self.get_csv_for_editing()
        return

# This naming convention is different than the one for the TraitBlenderConfig, because it is a PropertyGroup and follows standard bpy naming convention for that.
class TRAITBLENDER_PG_dataset(bpy.types.PropertyGroup):
    """Property group for TraitBlender dataset management."""
    
    csv: StringProperty(
        name="CSV Data",
        description="CSV dataset content as string",
        default="",
        update=reset_sample_on_csv_change
    )
    
    filepath: StringProperty(
        name="Dataset File",
        description="Path to the dataset file (automatically imports when selected)",
        default="",
        subtype='FILE_PATH',
        update=update_filepath
    )
    
    sample: EnumProperty(
        name="Sample",
        description="Select a sample from the dataset",
        items=lambda self, context: self._get_sample_items(),
        default=0
    )

    sync_sample_with_active_object: BoolProperty(
        name="Sync Sample to Active Object",
        description="Automatically set Sample when active object name matches a specimen name",
        default=True,
    )
    
    def _get_sample_items(self):
        """Get sample items for the enum property (includes default 't1' when no file imported)."""
        try:
            rownames = self.rownames
            if not rownames:
                return [("NONE", "No samples", "")]
            
            # Create items with proper tuple format
            items = []
            for i, name in enumerate(rownames):
                items.append((name, name, f"Sample {i+1}"))
            
            return items
        except Exception as e:
            print(f"TraitBlender: Error getting sample items: {e}")
            return [("NONE", "No samples", "")]
    
    def _get_default_dataframe(self):
        """Get default DataFrame when no file imported: one row 't1' with trait columns from active morphospace."""
        try:
            morphospace_name = bpy.context.scene.traitblender_setup.available_morphospaces
        except Exception:
            morphospace_name = ""
        traits = get_trait_parameters_with_defaults_for_morphospace(
            morphospace_name, context=bpy.context
        )
        columns = ["species"] + list(traits.keys())
        default_values = list(traits.values())
        df = pd.DataFrame([["t1"] + default_values], columns=columns)
        return df.set_index("species")

    def _ensure_virtual_dataset_traits_synced(self) -> None:
        """
        No filepath: in-memory CSV. Morphospaces with ``get_trait_parameters_with_defaults``
        (e.g. ATLAS ``n_components``) may change expected trait columns — rewrite CSV to match
        so the editor and ``loc()`` stay consistent.
        """
        if self.filepath:
            return
        try:
            morphospace_name = bpy.context.scene.traitblender_setup.available_morphospaces
        except Exception:
            return
        module = load_morphospace_module(morphospace_name)
        if module is None or not callable(
            getattr(module, "get_trait_parameters_with_defaults", None)
        ):
            return
        if not self.csv:
            return
        traits = get_trait_parameters_with_defaults_for_morphospace(
            morphospace_name, context=bpy.context
        )
        try:
            df = pd.read_csv(StringIO(self.csv))
            new_df = _resync_dataframe_trait_columns(df, traits)
            if new_df is None:
                return
            buf = StringIO()
            new_df.to_csv(buf, index=False)
            new_s = buf.getvalue()
            if new_s != self.csv:
                self.csv = new_s
        except Exception as e:
            print(f"TraitBlender: Could not sync virtual dataset trait columns: {e}")

    def reset_to_morphospace_default(self):
        """Clear imported/edited dataset and regenerate the default single-row CSV for the active morphospace."""
        self.filepath = ""
        self.csv = ""
        self.csv = self.get_csv_for_editing()

    def get_csv_for_editing(self):
        """Return CSV string for the editor: from csv property, or serialized default when no file imported."""
        if self.filepath:
            return self.csv if self.csv else ""
        self._ensure_virtual_dataset_traits_synced()
        if self.csv:
            return self.csv
        if not self.filepath:
            df = self._get_default_dataframe()
            csv_buffer = StringIO()
            df.reset_index().to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue()
        return ""

    def _get_dataframe(self):
        """Get DataFrame from CSV string, or default (one row 't1') when no file imported."""
        if not self.csv and not self.filepath:
            return self._get_default_dataframe()
        if self.csv and not self.filepath:
            self._ensure_virtual_dataset_traits_synced()
        if not self.csv:
            return pd.DataFrame()
        try:
            df = pd.read_csv(StringIO(self.csv))
            if df.empty or len(df.columns) == 0:
                return df
            
            # Define possible species/label column names (case-insensitive)
            species_column_names = ['species', 'label', 'tips', 'tip', 'sample', 'samples', 'name', 'names', 'id', 'ids']
            
            # Check if first column is already a species column
            first_col_lower = df.columns[0].lower().strip()
            if first_col_lower in species_column_names:
                # First column is already a species column, use it as index
                df = df.set_index(df.columns[0])
                return df
            
            # Look for species columns in the dataset
            species_columns = []
            for col in df.columns:
                col_lower = col.lower().strip()
                if col_lower in species_column_names:
                    species_columns.append(col)
            
            if species_columns:
                # Sort alphabetically and pick the first one
                species_columns.sort()
                species_col = species_columns[0]
                
                # Move the species column to the first position
                cols = list(df.columns)
                species_idx = cols.index(species_col)
                
                # Reorder columns: species column first, then the rest
                new_cols = [species_col] + [col for i, col in enumerate(cols) if i != species_idx]
                df = df[new_cols]
                
                print(f"TraitBlender: Moved '{species_col}' column to first position for species identification")
            
            # Use the first column as the index
            df = df.set_index(df.columns[0])
            return df
            
        except Exception as e:
            print(f"TraitBlender: Error parsing CSV data: {e}")
            return pd.DataFrame()
    
    def __str__(self):
        """Return pretty formatted DataFrame"""
        df = self._get_dataframe()
        if df.empty:
            return "No dataset loaded"
        return str(df)
    
    def head(self, n=5):
        """Return first n rows of the dataset"""
        df = self._get_dataframe()
        return df.head(n)
    
    def tail(self, n=5):
        """Return last n rows of the dataset"""
        df = self._get_dataframe()
        return df.tail(n)
    
    @property
    def colnames(self):
        """Return column names"""
        df = self._get_dataframe()
        return df.columns.tolist()
    
    @property
    def rownames(self):
        """Return row names/indices"""
        df = self._get_dataframe()
        return df.index.tolist()
    
    def __iter__(self):
        """Iterate over column names"""
        df = self._get_dataframe()
        return iter(df.columns)
    
    def __len__(self):
        """Return number of rows in the dataset"""
        df = self._get_dataframe()
        return len(df)
    
    @property
    def shape(self):
        """Return shape of the dataset (rows, columns)"""
        df = self._get_dataframe()
        return df.shape
    
    def loc(self, *args, **kwargs):
        """Access a group of rows and columns by label(s) or a boolean array."""
        df = self._get_dataframe()
        if len(args) == 1:
            return df.loc[args[0]]
        elif len(args) == 2:
            return df.loc[args[0], args[1]]
        elif kwargs:
            return df.loc[kwargs]
        return df.loc
    
    def iloc(self, *args, **kwargs):
        """Purely integer-location based indexing for selection by position."""
        df = self._get_dataframe()
        if len(args) == 1:
            return df.iloc[args[0]]
        elif len(args) == 2:
            return df.iloc[args[0], args[1]]
        elif kwargs:
            return df.iloc[kwargs]
        return df.iloc 