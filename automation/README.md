# FreeCAD Automation Generators

Parametric generators for model railroading in FreeCAD. All generators create photorealistic architectural details optimized for 3D printing and laser cutting at HO scale (1:87).

## Quick Start

1. **Open Skeleton.FCStd** from `General Parts/` to access shared parameters
2. **Select a face** in your model (Ctrl+click on face)
3. **Run the appropriate macro** from Macro menu
4. **Adjust parameters** in the spreadsheet if needed

## Utilities

| Utility | Purpose |
|---------|---------|
| [lint_params.FCMacro](lint_params.FCMacro) | Validate parameters before export/printing |

### lint_params
Checks scaled parameters against `materialThickness` to catch unprintable dimensions:
```
1. Open any model with a 'params' spreadsheet
2. Run lint_params.FCMacro
3. Orange-highlighted cells indicate values below materialThickness
```

## Available Generators

| Generator | Purpose | Select | Output |
|-----------|---------|--------|--------|
| [brick_generator](generators/brick_generator/) | Masonry walls (4 bond patterns) | Face/Object | BrickedWall compound |
| [shingle](generators/shingle/) | Roof shingles | Face | Shingle compound |
| [clapboard_generator](generators/clapboard_generator/) | Horizontal siding | Face(s) | ClapboardWall compound |
| [board_batten_generator](generators/board_batten_generator/) | Vertical siding | Face(s) | BoardBattenWall compound |
| [bead_board_generator](generators/bead_board_generator/) | Interior bead board | Face | BeadBoard compound |
| [smart_trim](generators/smart_trim/) | Window/door trim | Face(s) | Trim compound |
| [station_sign](generators/station_sign/) | C&O station signs | Object (Label) | Sign compound |

## Installation

### Automated (Recommended)
Each generator includes an installer script:
```bash
cd generators/brick_generator
python3 freecad_installer.py
```

### Manual
Copy to your FreeCAD Macro directory:
- macOS: `~/Library/Application Support/FreeCAD/Macro/`
- Linux: `~/.FreeCAD/Macro/`
- Windows: `%APPDATA%\FreeCAD\Macro\`

Files needed per generator:
- `*_generator.FCMacro` - Main macro
- `*_geometry.py` - Geometry library (same directory)

## Parameters via Skeleton.FCStd

All generators read parameters from a spreadsheet. The master parameter file is `General Parts/Skeleton.FCStd`.

### Key Parameters

**Global:**
- `scale` (87) - Model scale factor
- `materialThickness` (0.2mm) - Thin relief for printing

**Clapboard:**
- `clapboard_height` (0.8mm) - Course height
- `clapboard_thickness` (0.2mm) - Material thickness
- `trim_width` (1.5mm) - Corner trim width

**Shingle:**
- `shingleWidth` (3.5mm) - Shingle width
- `shingleExposure` (1.5mm) - Exposed height
- `shingleStaggerPattern` (half) - Stagger pattern

**Bead Board:**
- `beadSpacing` (101.6mm) - Spacing between beads
- `beadDepth` (0.2mm) - Groove depth
- `beadGap` (0.2mm) - Groove width

See [STATUS.md](STATUS.md) for complete parameter reference.

## Generator Usage

### Brick Generator
```
1. Create wall with openings (windows/doors already cut)
2. Select the face or object
3. Run brick_generator_macro
4. Bricks generated with openings auto-punched
```
Bond patterns: stretcher, english, flemish, common

### Shingle Generator
```
1. Select roof face(s)
2. Run shingle_generator
3. Shingles follow roof pitch with proper overlap
```
Stagger patterns: half, third, none

### Clapboard Generator
```
1. Select wall face(s) - Ctrl+click for multiple
2. Run clapboard_generator
3. Clapboards align across all selected faces
```
Features global grid snapping for seamless alignment.

### Board-and-Batten Generator
```
1. Select wall face(s)
2. Run board_batten_generator
3. Vertical boards with battens covering seams
```
Automatically trims boards to gable profiles.

### Bead Board Generator
```
1. Select interior wall face
2. Run bead_board_generator
3. Vertical grooves at regular intervals
```
Creates recessed groove pattern typical of period interiors.

### Smart Trim Generator
```
1. Select face(s) where trim is needed
2. Run smart_trim_generator
3. Trim with auto-mitered corners
```
Detects external/internal corners and calculates miter angles.

### Station Sign Generator
```
1. Create object, set Label to station name
2. Select the object
3. Run station_sign_generator
4. Sign created with scaled text and border
```
C&O style raised-letter signs.

## Architecture

All generators follow a clean separation pattern:

```
generator/
├── *_generator.FCMacro    # FreeCAD UI/orchestration
├── *_geometry.py          # Pure Python geometry (no FreeCAD deps)
├── tests/
│   └── test_*.py          # Pytest tests (run without FreeCAD)
└── README.md
```

**Benefits:**
- Geometry testable without FreeCAD running
- Fast pytest execution (~0.1 sec for 50+ tests)
- Easy to debug and maintain
- Reusable geometry functions

## Testing

Run tests without FreeCAD:
```bash
cd generators/brick_generator
python -m pytest tests/ -v

cd generators/shingle
python -m pytest tests/ -v
```

## HO Scale Reference

Common prototype-to-model conversions at 1:87:

| Prototype | HO Scale |
|-----------|----------|
| 8" brick | 2.32mm |
| 2.25" brick height | 0.65mm |
| 3/8" mortar | 0.11mm |
| 3" clapboard | 0.87mm |
| 4" clapboard | 1.16mm |
| 3.5" shingle | 0.92mm |

Formula: `HO_mm = prototype_inches × 25.4 / 87`

## Version History

- **2025-12:** Bead board generator added, Skeleton parameters updated
- **2025-12:** Board-and-batten generator v1.0.0
- **2025-12:** Brick generator v4.0.0 (auto opening detection)
- **2025-12:** Clapboard generator v6.0.0 (global grid snapping)
- **2025-11:** Shingle generator v4.0.0 (geometry lib extraction)
- **2025-11:** Smart trim generator v1.2.0 (corner detection)

## Troubleshooting

**Macro won't load:**
- Ensure `*_geometry.py` is in same directory as macro
- Check FreeCAD Python Console for import errors

**No output generated:**
- Verify face is selected (not just object)
- Check that face is planar

**Parameters not applied:**
- Spreadsheet must be named: `params`, `Spreadsheet`, or `Skeleton`
- Cell aliases must match expected names exactly

**Performance slow:**
- Large walls (>100k bricks) take time for boolean ops
- Consider breaking into sections

## License

Generated for model railroading. Free to use and modify for personal and commercial projects.

## Related Files

- `General Parts/Skeleton.FCStd` - Master parameter spreadsheet
- `automation/STATUS.md` - Current status and detailed parameter reference

## FreeCAD MCP API Reference

These generators can be driven programmatically via the FreeCAD MCP (Model Context Protocol) server. For Claude Code integration, see the API guide:

**[CLAUDE_API_GUIDE.md](https://github.com/blwfish/freecad-mcp/blob/main/CLAUDE_API_GUIDE.md)**

Key tools for automation:
- `execute_python` - Run arbitrary Python in FreeCAD context
- `spreadsheet_operations` - Read/write spreadsheet parameters
- `view_control` - Document management, screenshots, selection
- `part_operations` - Create and manipulate solids
