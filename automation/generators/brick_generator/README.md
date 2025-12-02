# Brick Generator v4.0.0

Parametric brick wall generator for FreeCAD model railroad structures with automatic opening detection and punchout.

## Quick Start

### Installation
```bash
python3 git_populate.py
```

### Usage
1. Create wall geometry in FreeCAD with openings (holes in the face)
2. Select object or face
3. Run `brick_generator_macro.FCMacro` from Macros menu
4. Bricks are generated with holes automatically punched

## What's New in v4.0.0
- **Automatic opening detection** - finds holes in the face
- **Automatic punchout** - generates cutout geometry matching openings
- **Automatic boolean cut** - punches holes in bricks automatically
- **Single output** - fully finished wall (no separate punchout step needed)

## Features

- **4 Bond Patterns**: Stretcher, English, Flemish, Common
- **Automatic Opening Handling**: Detects and punches holes automatically
- **Parametric**: Configure via FreeCAD spreadsheet
- **Fast**: Compound generation (no fusing overhead)
- **Metadata**: Version tracking in generated objects
- **Works with arrays**: Seamlessly handles arrayed walls with holes

## Workflows

### Object-Based
Select entire object → Generator detects faces and bay boundaries

### Face-Based
Select specific face → Bricks applied to that face only

## Parameters

Create spreadsheet named `BrickParams` with these cells:
```
brick_width     2.32  (mm)
brick_height    0.65  (mm)
brick_depth     1.09  (mm)
mortar          0.11  (mm)
bond_type       stretcher
common_bond_count  5
```

## Bond Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| stretcher | Half-offset courses | Most common |
| english | Alternating stretchers/headers | Historic, strong |
| flemish | Alternating within courses | Decorative |
| common | N stretchers + 1 header | Economic |

## Openings (Windows/Doors)

Use the "punchout" method:
1. Generate full brick wall
2. Create opening geometry (solid box)
3. Boolean cut the opening from bricks

## Troubleshooting

- **Module not found**: Ensure `brick_geometry.py` in `_lib/` subdirectory
- **No bricks generated**: Check wall dimensions and brick size
- **Bricks missing at edges**: Expected - generator creates bricks spanning beyond wall
- **Bay boundaries detected unexpectedly**: Check for small gaps in geometry

## Version

- Macro: 3.1.0
- Geometry Library: 3.0.0
- Release: 2024-12-02

## See Also

- `DELIVERY_SUMMARY` - Comprehensive deployment documentation
- `CHANGELOG` - Complete version history
- `DEPLOYMENT_SUMMARY` - Technical implementation notes
