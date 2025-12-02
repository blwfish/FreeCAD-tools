# Brick Generator v4.0.0 - Deployment Instructions

## Quick Start

1. **Extract the archive:**
   ```bash
   tar -xzf brick_generator_v4.0.0.tar.gz
   cd brick_generator_v4.0.0
   ```

2. **Run the deployment script:**
   ```bash
   python3 git_populate.py
   ```

3. **Restart FreeCAD** (if it was running)

4. The macro will appear as `brick_generator_macro.FCMacro` in FreeCAD's Macro menu

## What Gets Installed

The deployment script installs:

- **Macro file:** `brick_generator_macro.FCMacro`
  - Location: `~/Library/Application Support/FreeCAD/Macro/` (macOS)
  - Location: `~/.config/FreeCAD/Macro/` (Linux)
  - Location: `%APPDATA%\FreeCAD\Macro\` (Windows)
  - This file appears in FreeCAD's Macro → Macros menu

- **Geometry library:** `brick_geometry.py`
  - Location: `brick/` subdirectory of the Macro directory
  - Contains pure Python geometry functions (no FreeCAD dependencies)
  - Used by the macro for brick pattern generation

## Manual Installation

If the script doesn't work, manually copy:

1. `brick_generator_macro.FCMacro` → FreeCAD Macro directory root
2. `brick_geometry.py` → FreeCAD Macro directory `brick/` subdirectory

Create the `brick/` subdirectory if it doesn't exist.

## Removing Old Versions

If you have an older brick generator installed, **delete the old macro file first**:

```bash
# macOS/Linux
rm ~/Library/Application\ Support/FreeCAD/Macro/brick_generator_macro.FCMacro

# Or check for old versions
ls -la ~/Library/Application\ Support/FreeCAD/Macro/brick*
```

The deployment script will not overwrite existing files unless you use `--force`:

```bash
python3 git_populate.py --force
```

## Verification

After installation:

1. Open FreeCAD
2. Go to Macro → Macros
3. You should see `brick_generator_macro.FCMacro` in the list
4. Select it and click "Execute"
5. Check the Report View for version information - should show "v4.0.0"

## Troubleshooting

**Macro doesn't appear in FreeCAD's menu:**
- Make sure FreeCAD was restarted after installation
- Check that the macro file is in the root of the Macro directory, not in a subdirectory
- Verify the file has `.FCMacro` extension

**Import errors when running:**
- Make sure `brick_geometry.py` is in the `brick/` subdirectory
- Check file permissions (files should be readable)

**"Old version" still running:**
- Delete any old brick generator macro files from the Macro directory
- Make sure you're running the correct macro from the menu
- Check the Report View for the version number when macro starts

## Platform-Specific Locations

The script automatically detects your platform and uses the correct directory:

- **macOS:** `~/Library/Application Support/FreeCAD/Macro/`
- **Linux:** `~/.config/FreeCAD/Macro/`
- **Windows:** `%APPDATA%\FreeCAD\Macro\`

## Support

See README.md for usage instructions and CHANGELOG for version history.
