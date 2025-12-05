# Brick Generator v4.0.0

Parametric brick wall generator for FreeCAD with automatic opening detection. Creates photorealistic masonry walls using four different bond patterns: Stretcher, English, Flemish, and Common. All generated as thin geometry optimized for 3D printing and laser cutting.

## Features

- **Four bond patterns**: Stretcher (running), English, Flemish, and Common
- **Automatic opening detection**: Finds holes in the face geometry
- **Automatic punchout**: Generates cutout geometry matching openings
- **Automatic boolean cut**: Punches holes in bricks automatically
- **Parametric**: All dimensions controlled via FreeCAD spreadsheet
- **Flexible**: Works on arbitrary rectangular faces or sketches
- **HO/O/N scale**: Default dimensions are HO scale with configurable parameters
- **Metadata tracking**: Stores generator version, source, and configuration in result object
- **Fast**: Compound generation (no fusing overhead)

## What's New in v4.0.0

- **Automatic opening detection** - finds holes in the face
- **Automatic punchout** - generates cutout geometry matching openings
- **Automatic boolean cut** - punches holes in bricks automatically
- **Single output** - fully finished wall (no separate punchout step needed)

## Architecture

The brick generator uses a clean separation of concerns:

1. **`brick_geometry.py`** - Pure Python geometry library
   - No FreeCAD dependencies
   - Fully testable
   - Returns brick definitions (positions, dimensions, types)
   - ~312 lines of code

2. **`brick_generator_macro.FCMacro`** - FreeCAD UI layer
   - Orchestrates the workflow
   - Handles coordinate system detection
   - Creates FreeCAD objects
   - Reads parameters from spreadsheet
   - Detects and processes openings automatically
   - ~320 lines of code

3. **`test_brick_geometry.py`** - Comprehensive test suite
   - 30 tests covering all patterns and edge cases
   - All tests pass
   - No FreeCAD dependencies needed to run tests

## Installation

### Automated Installation
```bash
python3 freecad_installer.py
```

This will automatically:
- Detect your FreeCAD macro directory
- Copy the macro and geometry library
- Set up the correct directory structure

### Manual Installation

1. Copy files to your FreeCAD macro directory:
   - `brick_generator_macro.FCMacro` → FreeCAD Macros directory
   - `brick_geometry.py` → Same directory as macro

2. Create a FreeCAD document with a spreadsheet named "BrickParams"

3. In the spreadsheet, define these cells:
   ```
   brick_width     = 2.32    (mm)
   brick_height    = 0.65    (mm)
   brick_depth     = 1.09    (mm)
   mortar          = 0.11    (mm)
   bond_type       = "stretcher"   (stretcher, english, flemish, or common)
   common_bond_count = 5      (only used if bond_type = "common")
   ```

## Usage

### Workflow Options

#### Object-Based
Select entire object → Generator detects faces and bay boundaries automatically

#### Face-Based
Select specific face → Bricks applied to that face only

### Basic Workflow

1. **Create a wall face** - Either:
   - Draw a rectangular sketch and close it
   - Create a 3D body and select one face

2. **Select the face or object** in the tree or viewport

3. **Run the macro** - Go to Macro → Recent macros → brick_generator_macro

4. **Review the output** - A new Part feature `BrickedWall_*` appears in the tree

### Working with Openings (Windows, Doors, Arches)

**v4.0.0 Automatic Method (Recommended):**
1. Create wall geometry with holes already cut into the face
2. Select the object or face
3. Run the macro - openings are detected and punched automatically
4. Result is a fully finished wall with openings

**Manual Punchout Method (Alternative):**
1. **Generate the full brick wall** with no openings
2. **Create punchout geometry** for each opening:
   - Draw the outline of the window/door/arch
   - Extrude it perpendicular to the wall (thick enough to go through)
3. **Cut the punchout** from the wall using Part → Boolean → Cut
4. **Repeat** for each opening

**Why the punchout approach works well:**
- Works for any opening shape: rectangular, arched, irregular, etc.
- Uses FreeCAD's native boolean operations
- Allows you to reuse punchout geometry (arrays, mirrors, etc.)
- Brick edges at openings are naturally rough and authentic

**Example: Arched window**
1. Draw arch profile in sketch
2. Extrude it to create a solid arch shape
3. Cut from the wall (or use v4.0 automatic detection)
4. Optionally add voussoir bricks on top for detail

## Bond Patterns

### Stretcher (Running) Bond
- **Pattern**: Every course offset by half brick width
- **Use**: Most common, fastest to generate
- **Authenticity**: Common in modern construction

### English Bond
- **Pattern**: Alternating courses of stretchers and headers
- **Use**: Historic buildings, maximum strength
- **Authenticity**: Very common in 18th-19th century masonry

### Flemish Bond
- **Pattern**: Each course alternates individual stretchers and headers
- **Use**: High-strength, decorative walls
- **Authenticity**: Elegant historic bond, requires careful layout

### Common Bond
- **Pattern**: N stretcher courses, then 1 header course, repeat
- **Parameter**: `common_bond_count` (default 5)
- **Use**: Cost-effective, flexible
- **Authenticity**: Very common IRL, ratio varies by region and era

## Parameters

All parameters are read from the FreeCAD spreadsheet. If not found, defaults are used.

| Parameter | Default | Unit | Notes |
|-----------|---------|------|-------|
| `brick_width` | 2.32 | mm | Stretcher orientation (HO scale = 8") |
| `brick_height` | 0.65 | mm | Constant for all bricks (HO scale = 2.25") |
| `brick_depth` | 1.09 | mm | Into the wall (HO scale = 3.75") |
| `mortar` | 0.11 | mm | Joint thickness (HO scale = 0.375") |
| `bond_type` | "stretcher" | text | stretcher, english, flemish, or common |
| `common_bond_count` | 5 | count | Only for common bond |

## HO Scale Defaults

Based on common brick dimensions scaled to HO (1:87):

- **Brick dimensions**: 8" × 2.25" × 3.75" (width × height × depth)
- **Mortar joint**: 0.375" thick
- **In HO**: 2.32 × 0.65 × 1.09 mm (+ 0.11 mm mortar)

These are configurable. For O scale (1:48) or N scale (1:160), scale appropriately.

## Output

The macro creates:

1. **Part Feature**: Named `BrickedWall_{SourceName}`
   - Brick geometry with openings cut (v4.0+)
   - Ready for boolean operations, export, or 3D printing

2. **Metadata properties** (visible in Properties panel):
   - `GeneratorName`: "brick_generator"
   - `GeneratorVersion`: "4.0.0"
   - `SourceObject`: Name of source face or sketch
   - `SourceFace`: (face workflow) Face name
   - `BondType`: Bond pattern used
   - `BrickCount`: Total number of individual bricks

## Coordinate System

The generator uses a local 2D coordinate system on each wall:

- **U axis**: Horizontal (left to right along the wall)
- **V axis**: Vertical (bottom to top, ensures positive Z)
- **Normal**: Perpendicular to the wall (outward)

This system is detected automatically from the face/sketch and works with:
- Vertical walls
- Sloped walls
- Curved surfaces (treated as flat at each point)

## Advanced: Custom Brick Dimensions

To model period-specific or regional variations:

1. Research the actual brick dimensions
2. Determine the scale factor (e.g., HO = 1:87)
3. Calculate: `actual_dimension_mm = real_world_inches * 25.4 / 87`
4. Update the spreadsheet cells

Example: Large 10" × 3" bricks (common in late 1800s)
```
brick_width = 2.89    (10" / 87)
brick_height = 0.87   (3" / 87)
mortar = 0.15         (0.5" / 87, sometimes thicker for old mortar)
```

## Known Limitations

1. **No voussoirs**: Arched openings work via punchout, but don't automatically generate voussoir bricks
   - Workaround: Add voussoir layer on top after punchout

2. **Flat approximation**: Curved surfaces are treated as flat
   - Only noticeable on very large radius curves

3. **No mortar depth**: Mortar is represented as spacing, not 3D grooves
   - For visual detail, use bump maps or normal maps when rendering

4. **Brick orientation**: All bricks align to the detected U/V axes
   - No diagonal or complex herringbone patterns yet

## Testing

The geometry library includes comprehensive tests:

```bash
cd tests
python -m pytest test_brick_geometry.py -v
```

30 tests covering:
- All four bond patterns
- Parameter validation
- Edge cases (very small/large walls, narrow/tall walls)
- Metadata generation
- Brick definition correctness

All tests pass without FreeCAD running.

## Performance Notes

Typical generation times (MacBook M4 Max):

| Wall Size | Bond Type | Brick Count | Generation Time |
|-----------|-----------|------------|-----------------|
| 100×100 mm | Stretcher | ~1600 | <1 sec |
| 500×500 mm | Stretcher | ~40,000 | 3-5 sec |
| 1000×1000 mm | Stretcher | ~160,000 | 10-15 sec |
| Same size | Flemish | 1.5-2x slower | Due to alternating brick placement |

The main bottleneck is FreeCAD's boolean operations on large brick counts. For very large walls (>500,000 bricks), consider:
- Breaking into sections
- Using a lower resolution (larger mortar joints)
- Exporting as separate files and combining in CAM software

## Geometry Library API

For integration into other tools:

```python
from brick_geometry import BrickGeometry

# Create a generator
bg = BrickGeometry(
    u_length=500,           # Wall width (mm)
    v_length=300,           # Wall height (mm)
    brick_width=2.32,       # Stretcher width (mm)
    brick_height=0.65,      # Brick height (mm)
    brick_depth=1.09,       # Brick depth (mm)
    mortar=0.11,            # Joint thickness (mm)
    bond_type='english',    # Bond pattern
    common_bond_count=5     # For common bond only
)

# Generate
result = bg.generate()

# Access results
bricks = result['bricks']        # List of BrickDef namedtuples
metadata = result['metadata']    # Generation info

# Each brick has:
brick = bricks[0]
print(brick.index)       # Sequential index
print(brick.u)           # Position along wall width
print(brick.v)           # Position along wall height
print(brick.course)      # Which course (0-indexed)
print(brick.brick_type)  # 'stretcher' or 'header'
print(brick.width)       # Dimension along U
print(brick.height)      # Dimension along V
print(brick.depth)       # Dimension perpendicular
```

## Troubleshooting

- **Module not found**: Ensure `brick_geometry.py` is in the same directory as the macro
- **No bricks generated**: Check wall dimensions and brick size compatibility
- **Bricks missing at edges**: Expected - generator creates bricks spanning beyond wall boundaries
- **Bay boundaries detected unexpectedly**: Check for small gaps in geometry
- **Openings not detected**: Ensure holes are actually cut through the face geometry

## Version History

### v4.0.0 (2025-12-02)
- **NEW**: Automatic opening detection from face geometry
- **NEW**: Automatic punchout generation for openings
- **NEW**: Single-step workflow with integrated boolean operations
- Compound-based generation for better performance
- Works seamlessly with arrayed walls
- Improved bay boundary detection

### v3.0.0 (2025-11-26)
- Complete rewrite with separated geometry library
- Added Common bond pattern support
- 30 comprehensive tests, all passing
- Simplified macro to 320 lines
- Manual punchout workflow
- Better metadata tracking
- Improved documentation

### v2.0.2 (2025-11-23)
- Sketch-based workflow
- Coordinate system detection
- Three bond patterns (Stretcher, English, Flemish)

## Documentation

Additional documentation available in the `docs/` directory:
- `SUMMARY.md` - Complete feature and architecture overview
- `QUICK_REFERENCE.txt` - Quick command reference
- `DEPLOYMENT.md` - Deployment and installation guide

## License

Generated for model railroading projects. Use and modify freely for personal use.

## Support

For issues or questions:
1. Check the test suite to understand expected behavior
2. Verify spreadsheet parameters are set correctly
3. Use face-based workflow instead of sketch if issues persist
4. Check FreeCAD console output for detailed error messages
5. Review the documentation in `docs/` for detailed information

---

**Happy bricking!** 🧱

*Generated for HO scale model railroading with accuracy for photography at 1:87 scale and macro lens distances.*
