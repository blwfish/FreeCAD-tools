# Smart Trim Generator v1.2.0

Parametric trim generation for FreeCAD architectural models with automatic corner detection and miter angle calculation.

## What's New in v1.2.0

- **Advanced corner detection** - Automatically detects and classifies all corners
- **Automatic miter angles** - Calculates proper miter cuts for any polygon shape
- **Multiple corner types** - Handles external (convex), internal (concave), and straight corners
- **Beveled profiles** - New beveled/chamfered trim profile option
- **Better geometry** - Uses `trim_geometry.py` shared library

## Features

- Apply trim to any planar face
- Parametric control via spreadsheet
- Multiple profile styles (rectangular, beveled)
- Works with clapboard, shingle, or brick walls
- Generates trim as separate compound (easy to edit)

## Installation

### Quick Install (Recommended)
```bash
python3 smart_trim_freecad_installer.py
```

### Manual Install
1. Copy `smart_trim_generator.FCMacro` to your FreeCAD Macros folder
2. Copy `trim_geometry.py` to the same directory
3. Restart FreeCAD or reload macros

## Usage

### Basic Workflow
1. **Select faces** - Select one or more faces where you want trim
2. **Run macro** - Execute `smart_trim_generator.FCMacro`
3. **Adjust parameters** - Modify values in the `Trim_Params` spreadsheet
4. **Recompute** - Press F5 or Document → Recompute

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| trim_width | 2.0 mm | How far trim extends from wall |
| trim_height | 5.0 mm | Height of trim molding |
| trim_style | rectangular | Profile style (rectangular/beveled) |
| bevel_size | 0.5 mm | Bevel size for beveled profile |

### Corner Detection

The generator automatically:
- Detects all corners in the face boundary
- Classifies them as external (convex) or internal (concave)
- Calculates exact interior angles
- Computes proper miter cut angles

Example output:
```
Processing face 1/1...
  Detected 4 corners:
    - 4 external (convex)
    - 0 internal (concave)
    Corner 1: external  90.0° (miter:  45.0°)
    Corner 2: external  90.0° (miter:  45.0°)
    Corner 3: external  90.0° (miter:  45.0°)
    Corner 4: external  90.0° (miter:  45.0°)
  ✓ Generated 4 trim segments
```

## Architecture

```
smart-trim-generator-v1.2.0/
├── smart_trim_generator.FCMacro  # Main macro
├── trim_geometry.py              # Geometry library
├── smart_trim_git_populate.py    # Git deployment
├── smart_trim_freecad_installer.py  # FreeCAD installation
├── test_trim_geometry.py         # Test suite
└── README.md                     # This file
```

### Library: trim_geometry.py

Core geometry library providing:
- `detect_corners(face)` - Find all corners in a face
- `analyze_face_for_trim(face)` - Complete corner analysis
- `create_simple_rectangular_profile(w, h)` - Rectangular profile
- `create_beveled_profile(w, h, bevel)` - Beveled profile
- `generate_trim_for_face(face, profile)` - Complete trim generation

Can be imported by other generators (clapboard, shingle, brick).

## Examples

### Simple Rectangle
```python
# 4 external 90° corners → 45° miters
Face: 100mm × 50mm rectangle
Result: 4 trim segments with perfect 45° corners
```

### L-Shaped Wall
```python
# 5 external + 1 internal corner
Face: L-shaped
Result: 6 trim segments
  - 5 external 90° corners (45° miters)
  - 1 internal 270° corner (135° miter)
```

### Hexagonal Building
```python
# 6 external 120° corners → 60° miters
Face: Regular hexagon
Result: 6 trim segments with 60° miters
```

## Current Limitations

### Not Yet Implemented
- **Mitered corner pieces** - Currently generates straight segments only
  - Corners will show gaps where miters should meet
  - This is the top priority for v1.3.0
- **Non-planar faces** - Only works on planar (flat) faces
- **Curved edges** - Only supports straight edges

### Workarounds
- For now, trim generates continuous segments
- You can manually edit corner joints if needed
- Future versions will include proper mitered corners

## Technical Details

### Corner Detection Algorithm
Uses vector mathematics to determine corner types:
```python
turn_angle = vec_in.getAngle(vec_out)  # 0-180°
cross = vec_in.cross(vec_out)          # Turn direction

if cross.z > 0:  # External corner
    interior_angle = 180° - turn_angle
else:  # Internal corner
    interior_angle = 180° + turn_angle
```

This works for any polygon shape and correctly handles both convex and concave corners.

### Integration with Other Generators

Other generators can import trim_geometry:
```python
import sys
from pathlib import Path

# Add smart_trim to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'smart_trim'))
import trim_geometry as tg

# Use it
profile = tg.create_simple_rectangular_profile(2.0, 5.0)
trim_pieces = tg.generate_trim_for_face(face, profile)
```

## Version History

### v1.2.0 (2024-12-01)
- Integrated `trim_geometry.py` library
- Automatic corner detection and classification
- Automatic miter angle calculation
- Beveled profile option
- Comprehensive corner analysis output

### v1.1.0
- Updated git populator with default path
- Improved deployment scripts

### v1.0.0
- Initial release
- Basic trim generation
- Rectangular profiles

## Requirements

- FreeCAD 0.21+ (tested with 1.0.1)
- Python 3.8+
- Part workbench
- Draft workbench (for utilities)

## Files

1. `smart_trim_generator.FCMacro` - Main macro (6.5 KB)
2. `trim_geometry.py` - Geometry library (13 KB)
3. `smart_trim_git_populate.py` - Git deployment script
4. `smart_trim_freecad_installer.py` - FreeCAD installer
5. `test_trim_geometry.py` - Test suite
6. `README.md` - This documentation

## Support

For issues or questions:
1. Check the integration guide: `TRIM_INTEGRATION_GUIDE.md`
2. Review test cases in `test_trim_geometry.py`
3. See example usage in `trim_generation_demo.FCMacro`

## License

MIT License - Free to use and modify

## Author

Brian White  
COVA Model Railroad Project  
Version 1.2.0 - December 2024
