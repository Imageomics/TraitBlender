# Installation Guide

## Supported versions

| | |
|--|--|
| **TraitBlender** | **v2.3.0** |
| **Blender** | **5.1** and later |

??? note "System Requirements"
    ### Minimum Requirements
    - **Blender**: **5.1** or later
    - **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)

    ### Recommended Requirements
    - **Blender**: Latest **5.1+** release
    - **RAM**: 32GB for large datasets
    - **CPU**: Multi-core processor (8+ cores recommended)

## Installation

### Command-line install (optional)

You can install a downloaded release zip directly from the terminal:

`blender --command extension install-file -r user_default --enable traitblender-v2.3.0-linux.zip`

Use the zip that matches your OS:

- Linux: `traitblender-<tag>-linux.zip`
- Linux (headless): `traitblender-<tag>-linux-headless.zip`
- macOS: `traitblender-<tag>-mac.zip`
- Windows: `traitblender-<tag>-windows.zip`

## Command-line Uninstall (Optional)

To remove TraitBlender from the Blender extension directory:

```bash
blender --command extension remove [-h] [--no-prefs] PACKAGES
```

Replace `PACKAGES` with the installed extension package name(s) you want to remove (the exact identifier can vary by OS/tag).

After removing the extension, restart Blender. TraitBlender will no longer be available (the UI panel and `bpy.ops.traitblender.*` operators will not be registered).

**Step 1: Download TraitBlender**

- Download the latest release (**v2.3.0**) from [GitHub Releases](https://github.com/Imageomics/TraitBlender/releases)
- Save the `.zip` file to your computer

**Step 2: Install in Blender**

- Open Blender
- Go to `Edit > Preferences` (or `Blender > Preferences` on macOS)
- Navigate to the `Add-ons` tab
- Click `Install...` button
- Browse and select the downloaded TraitBlender `.zip` file
- Click `Install Add-on`

**Step 3: Enable the Add-on**

- In the Add-ons list, search for "TraitBlender"
- Check the box next to "TraitBlender" to enable it
- The add-on should now appear in the 3D Viewport sidebar (press `N` to show/hide)

## Verify Installation

To verify that TraitBlender is properly installed:

**Check the UI Panel**

- In the 3D Viewport, press `N` to open the sidebar
- Look for the "TraitBlender" tab

**If something is wrong**

- Use **Blender 5.1+** with **TraitBlender v2.3.0**
- Check that the add-on is enabled in Preferences
- Restart Blender completely

## Next Steps

After successful installation, proceed to the [Quick Start Tutorial](./quick-start.md) to begin using TraitBlender.
