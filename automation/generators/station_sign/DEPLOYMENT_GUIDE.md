# Station Sign Generator v1.2.0 - Deployment Guide

## Complete Bundle Contents

This is the full blw-standard deployment bundle for the station sign generator:

```
station_sign_generator/
├── station_sign_generator.FCMacro  # Main macro (no version in filename)
├── freecad_installer.py            # Automated installer script
├── git_populate.py                 # Git staging helper
├── README.md                       # Complete documentation
└── VERSION                         # Version tracking (1.2.0)
```

## Key Changes in v1.2.0

### Separate Horizontal and Vertical Gaps

Based on analysis of the Gordonsville depot 1970 photo:
- **Horizontal gap** (left/right): 1.5mm (more generous)
- **Vertical gap** (top/bottom): 0.75mm (tighter)

This matches C&O prototype practice where signs have more breathing room horizontally.

### Sign Sizing

The sign now auto-sizes based on:
```
Width  = (2 × 0.5mm border) + (2 × 1.5mm gap) + text_width
Height = (2 × 0.5mm border) + (2 × 0.75mm gap) + text_height
```

For "GORDONSVILLE" this creates a properly proportioned sign matching the historical photo.

## Installation Methods

### Method 1: Automated (Recommended)

```bash
cd station_sign_generator
python3 freecad_installer.py
```

The installer:
- Auto-detects your OS (macOS/Linux/Windows)
- Finds the correct FreeCAD macro directory
- Copies the macro
- Prompts before overwriting existing files

### Method 2: Manual

Copy `station_sign_generator.FCMacro` to:
- macOS: `~/Library/Application Support/FreeCAD/Macro/`
- Linux: `~/.FreeCAD/Macro/`
- Windows: `%APPDATA%\FreeCAD\Macro\`

## Usage Quick Start

1. Create/open FreeCAD document
2. Create a box: `Part.makeBox(10,10,10)`
3. Set its Label: `obj.Label = "Gordonsville"`
4. Select the object
5. Run: Macro → station_sign_generator

## Git Deployment

To add this to your git repository:

```bash
cd station_sign_generator
python3 git_populate.py
```

This stages all necessary files. Then:

```bash
git commit -m "Add station sign generator v1.2.0"
git push
```

## File Naming Convention (blw-standard)

Following your established pattern:
- ✅ Macro: `station_sign_generator.FCMacro` (NO version number)
- ✅ Version tracked in: VERSION file and code VERSION constant
- ✅ Installer: `freecad_installer.py` (consistent name)
- ✅ Git helper: `git_populate.py` (consistent name)

This matches your shingle generator structure.

## Parameter Spreadsheet Support

If using Skeleton.FCStd template, parameters read from:

| Cell | Parameter | Default |
|------|-----------|---------|
| B2 | materialThickness | 0.2mm |
| B3 | borderThickness | 0.5mm |
| B4 | borderGapHorizontal | 1.5mm |
| B5 | borderGapVertical | 0.75mm |

## Metadata Properties

Every generated sign includes:

**Generator group:**
- GeneratorName: "station_sign_generator"
- GeneratorVersion: "1.2.0"

**Parameters group:**
- StationName
- TextHeightHO
- SignWidth, SignHeight
- BorderThickness
- BorderGapHorizontal
- BorderGapVertical

## Directory Structure for Git

Suggested location in your repo:
```
automation/generators/station_sign_generator/
├── station_sign_generator.FCMacro
├── freecad_installer.py
├── git_populate.py
├── README.md
└── VERSION
```

This follows the pattern of your other generators (shingle, etc).

## Testing

After installation, test with:

```python
import FreeCAD as App
import Part

doc = App.activeDocument() or App.newDocument()
box = Part.makeBox(10, 10, 10)
marker = doc.addObject("Part::Feature", "Test")
marker.Shape = box
marker.Label = "Gordonsville"
doc.recompute()

# Select marker, run macro
```

## Next Steps

1. Install the macro: `python3 freecad_installer.py`
2. Test with "Gordonsville" 
3. Verify proportions match the reference photo
4. Add to git: `python3 git_populate.py`
5. Commit and push

Ready for production use!
