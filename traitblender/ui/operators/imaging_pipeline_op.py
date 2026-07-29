import bpy
from bpy.types import Operator
import os
import re
import csv
from datetime import datetime

from ...core.morphospaces import get_orientation_names, apply_orientation_by_name
from ...core.meshes import export_current_sample


def _sanitize_orientation_for_path(name):
    """Make orientation name safe for directory/file names."""
    s = name.replace(" ", "_").replace(",", "")
    return re.sub(r"[^\w\-]", "", s) or "orientation"


def _enabled_orientation_names(context, morphospace_name):
    """
    Build the imaging orientation list from one source of truth.

    Order and identity come from ``get_orientation_names`` (same dict used to apply).
    Enablement comes from imaging.orientation_options checkboxes keyed by that name.
    """
    names = get_orientation_names(morphospace_name, context) if morphospace_name else []
    if not names:
        return []
    options = context.scene.traitblender_config.imaging.orientation_options
    enabled = {item.name: bool(item.enabled) for item in options}
    return [n for n in names if enabled.get(n, False)]


class TRAITBLENDER_OT_imaging_pipeline(Operator):
    """Run the full imaging and simulation pipeline for the current dataset."""
    bl_idname = "traitblender.imaging_pipeline"
    bl_label = "Simulate Dataset"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    _specimen_idx = 0
    _orientation_idx = 0
    _img_idx = 0
    _specimens = []
    _orientations = []
    _total_specimens = 0
    _images_per_orientation = 1
    _include_images = True
    _render_dir = ""
    _save_meshes = False
    _orient_before_export = True
    _mesh_root = ""
    _exported_mesh_for_specimen = False
    _mesh_path = ""
    _last_applied_orientation = ""
    _log_file = None
    _csv_file = None
    _csv_writer = None

    def _imaging_step(self, context):
        """Run one imaging iteration. Returns True if the pipeline is finished (_finish called)."""
        dataset = context.scene.traitblender_dataset
        config = context.scene.traitblender_config

        # Treat implicit morphospace defaults as a valid dataset.
        if len(dataset.rownames) == 0 or self._specimen_idx >= self._total_specimens:
            self._finish(context)
            return True

        name = self._specimens[self._specimen_idx]
        row = dataset.loc(name)
        orientation_name = self._orientations[self._orientation_idx]

        # Generate new specimen only at start of each specimen (first orientation, first image)
        if self._orientation_idx == 0 and self._img_idx == 0:
            if self._specimen_idx > 0:
                prev_name = self._specimens[self._specimen_idx - 1]
                prev_obj = bpy.data.objects.get(prev_name)
                if prev_obj:
                    bpy.data.objects.remove(prev_obj, do_unlink=True)

            dataset.sample = name
            # When exporting unoriented meshes, skip Default on generate so the file
            # matches the morphospace/SSM frame (e.g. ATLAS PCA alignment).
            apply_default = (not self._save_meshes) or self._orient_before_export
            bpy.ops.traitblender.generate_morphospace_sample(
                apply_default_orientation=apply_default
            )
            self._exported_mesh_for_specimen = False
            self._mesh_path = ""
            self._last_applied_orientation = ""

            # Optional mesh export: once per specimen, before imaging orientations/transforms
            if self._save_meshes and not self._exported_mesh_for_specimen:
                try:
                    if self._orient_before_export:
                        apply_orientation_by_name(context, "Default", sample_name=name)
                        self._last_applied_orientation = "Default"
                    mesh_dir = os.path.join(self._mesh_root, name)
                    os.makedirs(mesh_dir, exist_ok=True)
                    self._mesh_path = os.path.join(mesh_dir, f"{name}")
                    export_current_sample(filepath=self._mesh_path, context=context)
                    self._exported_mesh_for_specimen = True
                    if self._csv_writer:
                        self._csv_writer.writerow([name, "MESH", 0, os.path.abspath(self._mesh_path), ""])
                        self._csv_file.flush()
                except Exception as e:
                    # Don't crash the imaging pipeline if mesh export fails
                    print(f"TraitBlender: Mesh export failed for '{name}': {e}")

        # Apply this orientation by name (same string used for folders / CSV / logs)
        if (
            self._img_idx == 0
            or self._last_applied_orientation != orientation_name
        ):
            apply_orientation_by_name(context, orientation_name, sample_name=name)
            self._last_applied_orientation = orientation_name
            # Best-effort UI sync only; not used for apply or paths
            try:
                context.scene.traitblender_orientation.orientation = orientation_name
            except Exception:
                pass

        # Reset and run pipeline for this image
        bpy.ops.traitblender.reset_pipeline()
        bpy.ops.traitblender.run_pipeline()

        # If images are disabled, skip rendering and just advance counters.
        if not self._include_images:
            self._img_idx += 1
            if self._img_idx >= self._images_per_orientation:
                self._img_idx = 0
                self._orientation_idx += 1
                if self._orientation_idx >= len(self._orientations):
                    self._orientation_idx = 0
                    self._specimen_idx += 1
            return False

        # Directory structure:
        # - Always: render_dir / images / specimen_name / orientation_sanitized /
        # - If save_meshes: render_dir / meshes / specimen_name /
        #   (Default-oriented if meshes.orient_before_export, else as generated)
        orient_subdir = _sanitize_orientation_for_path(orientation_name)
        images_dir = os.path.join(self._render_dir, "images", name, orient_subdir)
        # Keep configs under images when meshes are enabled so the dataset root splits into images/ + meshes/
        if self._save_meshes:
            configs_dir = images_dir
        else:
            configs_dir = os.path.join(self._render_dir, "configs", name, orient_subdir)
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(configs_dir, exist_ok=True)

        img_format = config.output.image_format.lower()
        config_filename = f"{name}_{self._img_idx}.yaml"
        config_path = os.path.join(configs_dir, config_filename)

        bpy.ops.traitblender.export_config(filepath=config_path)

        img_filename = f"{name}_{self._img_idx}.{img_format}"
        img_path = os.path.join(images_dir, img_filename)
        context.scene.render.filepath = img_path

        bpy.ops.traitblender.render_image()

        abs_img_path = os.path.abspath(img_path)
        abs_config_path = os.path.abspath(config_path)
        if self._csv_writer:
            self._csv_writer.writerow([name, orientation_name, self._img_idx, abs_img_path, abs_config_path])
            self._csv_file.flush()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = (
            f"[{timestamp}] [{self._specimen_idx + 1}/{self._total_specimens}] {name} "
            f"| {orientation_name} | image {self._img_idx + 1}/{self._images_per_orientation}: {dict(row)}\n"
        )
        print(log_msg.strip())
        if self._log_file:
            self._log_file.write(log_msg)
            self._log_file.flush()

        self._img_idx += 1
        if self._img_idx >= self._images_per_orientation:
            self._img_idx = 0
            self._orientation_idx += 1
            if self._orientation_idx >= len(self._orientations):
                self._orientation_idx = 0
                self._specimen_idx += 1

        return False

    def modal(self, context, event):
        if event.type == 'TIMER':
            if self._imaging_step(context):
                return {'FINISHED'}

        elif event.type == 'ESC':
            self._finish(context)
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        dataset = context.scene.traitblender_dataset
        config = context.scene.traitblender_config
        setup = context.scene.traitblender_setup

        if len(dataset.rownames) == 0:
            self.report({'WARNING'}, "No dataset loaded")
            return {'CANCELLED'}

        render_dir = config.output.rendering_directory
        if not render_dir:
            self.report({'ERROR'}, "No rendering directory specified")
            return {'CANCELLED'}

        morphospace_name = setup.available_morphospaces
        self._orientations = _enabled_orientation_names(context, morphospace_name)
        if not self._orientations:
            self.report({'ERROR'}, "No orientations selected for imaging. Enable at least one in the Imaging panel.")
            return {'CANCELLED'}

        try:
            os.makedirs(render_dir, exist_ok=True)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create rendering directory: {e}")
            return {'CANCELLED'}

        self._specimens = dataset.rownames
        self._total_specimens = len(self._specimens)
        self._include_images = bool(getattr(config.imaging, "include_images", True))
        self._images_per_orientation = config.imaging.images_per_orientation
        self._render_dir = render_dir
        self._save_meshes = bool(getattr(config.meshes, "save_meshes", False))
        self._orient_before_export = bool(
            getattr(config.meshes, "orient_before_export", True)
        )
        self._mesh_root = os.path.join(render_dir, "meshes")
        self._specimen_idx = 0
        self._orientation_idx = 0
        self._img_idx = 0
        self._exported_mesh_for_specimen = False

        if self._save_meshes:
            try:
                os.makedirs(self._mesh_root, exist_ok=True)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to create meshes directory: {e}")
                return {'CANCELLED'}

        log_path = os.path.join(render_dir, "rendering_log.txt")
        try:
            self._log_file = open(log_path, 'w')
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._log_file.write(f"TraitBlender Rendering Log - {timestamp}\n")
            self._log_file.write(f"{'='*60}\n\n")
        except Exception as e:
            self.report({'WARNING'}, f"Failed to open log file: {e}")
            self._log_file = None

        csv_path = os.path.join(render_dir, "rendering_log.csv")
        try:
            self._csv_file = open(csv_path, 'w', newline='')
            self._csv_writer = csv.writer(self._csv_file)
            self._csv_writer.writerow(['species', 'orientation', 'index', 'path', 'config_path'])
        except Exception as e:
            self.report({'WARNING'}, f"Failed to open CSV file: {e}")
            self._csv_file = None
            self._csv_writer = None

        total_imgs = self._total_specimens * len(self._orientations) * self._images_per_orientation
        print(f"Rendering {self._total_specimens} specimens × {len(self._orientations)} orientations × {self._images_per_orientation} images = {total_imgs} total to {render_dir}")

        # Modal + timer does not reliably run before Blender exits in --background mode.
        if getattr(bpy.app, "background", False):
            try:
                while not self._imaging_step(context):
                    pass
            except Exception:
                self._finish(context)
                raise
            return {'FINISHED'}

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _finish(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None

        if self._specimens and self._specimen_idx > 0:
            last_idx = min(self._specimen_idx - 1, len(self._specimens) - 1)
            if last_idx >= 0:
                last_name = self._specimens[last_idx]
                last_obj = bpy.data.objects.get(last_name)
                if last_obj:
                    bpy.data.objects.remove(last_obj, do_unlink=True)

        if self._csv_file:
            self._csv_file.close()
            self._csv_file = None
            self._csv_writer = None

        if self._log_file:
            if self._specimen_idx >= self._total_specimens:
                total_imgs = self._total_specimens * len(self._orientations) * self._images_per_orientation
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._log_file.write(f"\n{'='*60}\n")
                self._log_file.write(f"[{timestamp}] Rendering complete: {total_imgs} images rendered\n")
            self._log_file.close()
            self._log_file = None

        if self._specimen_idx >= self._total_specimens:
            total_imgs = self._total_specimens * len(self._orientations) * self._images_per_orientation
            print(f"Complete: rendered {total_imgs} images")
            self.report({'INFO'}, f"Rendered {total_imgs} images")
