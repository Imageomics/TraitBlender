# TraitBlender  [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19140353.svg)](https://doi.org/10.5281/zenodo.14804133)

<p align="center">
  <img src="traitblender/docs/images/logo.svg" alt="TraitBlender logo" width="360"/>
</p>

TraitBlender is a Blender add-on for generating museum-style images and 3D meshes of specimens from theoretical morphospaces. **v2.3.0** targets **Blender 5.1+** (Python 3.13 wheels) on Windows, macOS, and Linux.

## Features

**Serializable scene configuration** — The entire scene (camera, lamp, world, morphospace hyperparameters, sample placement, render and output settings) is exposed as a single configuration that can be saved to and loaded from YAML files. This makes it easy to reproduce runs, share setups, and version-control pipeline settings.

**Morphospaces** — TraitBlender ships with three morphospaces:

- **Shell (Default)** — A 3D shell morphospace that combines the parametric coiling model of [Contreras-Figueroa & Aragón (2023)](https://doi.org/10.3390/d15030431) with thickness allometry from [Okabe & Yoshimura (2017)](https://doi.org/10.1038/srep42445). Traits control whorl expansion, aperture shape, ribbing, and scaling; hyperparameters tune mesh resolution and options.
- **Circle Grid** — A simple morphospace (e.g. for testing): a gridded plane of circles with configurable traits.
- **ATLAS** — Deforms a template mesh from an [ATLAS DATABASE](https://github.com/agporto/ATLAS) export using PCA on dense correspondences and local RBF interpolation (same workflow as the ATLAS DATABASE explorer).

**Dataset import, editing, and saving** — Specimen trait values are read from CSV, TSV, or Excel. The built-in dataset editor supports filtering, sorting, pagination, and saving changes back to file, so you can curate and tweak trait tables without leaving Blender.

**Built-in orientations** — Each morphospace defines named orientations (e.g. "Default", "Aperture view") that place specimens consistently on the table. The imaging pipeline can render multiple orientations per specimen so images are comparable across specimens and runs.

**Stochastic transform pipeline** — Scene properties (e.g. camera location, focal length, lamp power) can be driven by configurable transforms with normal or other samplers. This adds controlled variation to images (e.g. small camera jitter) for robustness or data augmentation while keeping the setup reproducible via the same config and seed.

**Export** — The pipeline can export meshes (e.g. OBJ) and multi-view images per specimen. Simulated trait values are simply read from your spreadsheet, so you can generate trait tables in R or Python, import them into TraitBlender, run the imaging pipeline, and then analyze the exported meshes in external tools.

**Integration with SlicerMorph** — Exported meshes can be imported and analyzed in [SlicerMorph](https://slicermorph.github.io/), an open platform for 3D morphology and morphometrics in 3D Slicer.

For installation, quick start, and full documentation, see the [docs](https://imageomics.github.io/TraitBlender/).

## Command-Line Installation (Optional)

You can also install a release zip from the command line:

`blender --command extension install-file -r user_default --enable traitblender-v2.3.0-linux.zip`

Use the zip that matches your OS (for example: `...-windows.zip`, `...-mac.zip`, or `...-linux.zip`, `...-linux-headless.zip`).
