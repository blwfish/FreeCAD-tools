# Radial Brick Generator

Generate running bond brick patterns on cylindrical and conical surfaces in FreeCAD.

**Version:** 1.0.0
**Date:** 2025-01-01

## Overview

The radial brick generator creates brick skin geometry on surfaces of revolution (cylinders and cones). It analyzes selected faces from existing FreeCAD solids and applies a running bond brick pattern that follows the curved surface.

**Primary use cases:** smokestacks, water towers, silos, grain elevators, and other industrial cylindrical structures.

## Installation

### Option 1: Run the Installer (Recommended)

1. Open FreeCAD
2. Go to Macro → Macros...
3. Navigate to this directory
4. Select `freecad_installer.py`
5. Click Execute

The macro and library will be installed to your FreeCAD macros directory.

### Option 2: Manual Installation

1. Copy `radial_brick_generator_macro.FCMacro` to your FreeCAD Macro directory
2. Create a subdirectory called `radial_brick/`
3. Copy `radial_brick_geometry.py` to the `radial_brick/` subdirectory

## Usage

1. **Create your base model:** Model the cylindrical or conical shape first (cylinder, tapered cone, etc.)

2. **Select faces:** Click on one or more cylindrical or conical faces. Use Ctrl+click to select multiple faces.

3. **Run the macro:** Go to Macro → Macros... → radial_brick_generator_macro

4. **Result:** A new object is created with the brick pattern applied

## Parameters

Parameters are read from a spreadsheet named "Spreadsheet" in the active document. The following aliases are recognized:

| Parameter | Aliases | Default (HO scale) | Description |
|-----------|---------|-------------------|-------------|
| brick_length | `brickWidth`, `brickLength` | 2.32 mm | Brick length along circumference |
| brick_height | `brickHeight` | 0.65 mm | Brick height (vertical) |
| brick_thickness | `brickDepth`, `brickThickness` | 1.09 mm | Full brick depth (for reference) |
| mortar_thickness | `mortar`, `mortarThickness` | 0.11 mm | Mortar joint thickness |
| material_thickness | `materialThickness` | 0.3 mm | Skin depth (radial brick projection) |

If no spreadsheet is found, HO scale defaults are used.

## Brick Placement

Bricks are centered on the selected surface:
- The original cylindrical/conical surface represents the mid-wall
- Bricks project outward by `materialThickness / 2`
- Bricks project inward by `materialThickness / 2`
- Mortar joints have depth equal to `materialThickness`

This means if you model a cylinder at your desired mid-wall radius, the finished brick surface will be centered on that form.

## Supported Surface Types

- **Cylinders** (`Part::GeomCylinder`) - constant radius
- **Cones** (`Part::GeomCone`) - linear taper

Outer (convex) surfaces are supported. Inner surfaces are not needed since the brick skin is centered on the form.

## Features

- **Running bond pattern:** Half-brick offset between alternate courses
- **Automatic taper handling:** Fewer bricks per course at smaller radii
- **Centered placement:** Bricks centered on surface using `materialThickness`
- **Multi-face selection:** Process multiple faces in one operation
- **Metadata tracking:** Generated objects include source info and brick count

## Limitations

- Axis must be approximately vertical (within 15° of Z-axis)
- Minimum 8 bricks per course (very small radii not supported)
- Running bond only (other patterns in future versions)

## File Structure

```
radial_brick/
├── radial_brick_geometry.py        # Pure Python geometry library
├── radial_brick_generator_macro.FCMacro  # FreeCAD macro
├── freecad_installer.py            # Installer script
├── tests/
│   └── test_radial_brick_geometry.py  # Unit tests
├── README.md                       # This file
└── CHANGELOG.md                    # Version history
```

## Testing

Run unit tests with pytest:

```bash
cd automation/generators/radial_brick
python -m pytest tests/test_radial_brick_geometry.py -v
```

Or run manually without pytest:

```bash
python -c "import tests.test_radial_brick_geometry"
```

## Architecture

The generator follows a two-layer architecture:

1. **Pure Python geometry library** (`radial_brick_geometry.py`)
   - No FreeCAD dependencies
   - Generates brick definitions with positions and dimensions
   - Fully testable with pytest

2. **FreeCAD macro** (`radial_brick_generator_macro.FCMacro`)
   - Face analysis (cylinder/cone detection)
   - FreeCAD geometry creation
   - User interface and error handling

## Version History

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Related Tools

- `brick_generator` - For flat/planar wall surfaces
- `clapboard_generator` - For clapboard siding
- `shingle_generator` - For roof shingles
