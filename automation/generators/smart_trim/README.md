# Smart Trim Generator v1.0.9

Parametric trim generator for FreeCAD. Applies corner boards, eave trim, and gable trim to walls that have been decorated with clapboard or shingles.

## Recent Changes

**v1.0.9** - Fixed outward direction for source clapboards
- Clapboard geometry extends on BOTH sides of the wall face (mostly into wall, slightly outward)
- Now checks which direction the clapboard extends BEYOND the face position
- The side that protrudes past the face is the true outward direction
- Fixes all source (non-mirror) clapboards that had trim outside bounding box

**v1.0.8** - Fixed outward direction for all cases
- Now uses bounding box comparison between clapboard/mirror and source wall
- Detects which direction the clapboard actually protrudes from the wall
- Works correctly for both source clapboards and mirrors on any wall orientation
- Fixes trim appearing on wrong side, inside wall, or outside bounding box

**v1.0.6** - Fixed mirror normal direction
- Trim was appearing inside the wall (wrong side) on mirrored objects
- Now correctly flips normal before generating trim for mirrors
- After mirror transformation, trim is on the outside where it belongs

**v1.0.5** - Fixed two critical issues
- **Mirror transformation**: Trim now appears at the mirror's location, not the source wall
  - Applies `Shape.mirror()` transformation for `Part::Mirroring` objects
- **Notch edge detection**: Door openings that extend to floor (notches in outer wire) are now correctly skipped
  - Uses robust bbox perimeter check instead of fragile edge signature matching
  - Edges 5, 6, 7 (door jambs/headers) now correctly skipped

**v1.0.4** - Fixed mirror handling
- Properly resolves mirror objects to access clapboard properties
- Mirrors now work correctly with source wall face analysis

**v1.0.2** - Punchout hole detection
- Automatically detects and skips window/door holes created by boolean cuts
- Uses bounding box analysis to distinguish building perimeter from hole edges
- Detects punchout misalignments and warns user to fix geometry before proceeding
- Handles both sketch-based holes and boolean punchout holes

**v1.0.1** - Fixed mirror support
- Trim now correctly applies to mirrored clapboard/shingle objects  
- Fixed handling of Part::Mirroring objects (reads from Source property)
- Fixed handling of PartDesign::Mirrored objects
- Previously, selecting a mirror would incorrectly place trim on the source object

## Features

- **Automatic edge classification**: Detects vertical, horizontal, and diagonal (gable) edges
- **Smart skipping**: Automatically skips bottom edges and edges adjacent to doors/windows
- **Separate trim types**: Generates corner trim, eave trim, and gable trim as separate FreeCAD objects in a compound
- **Parametric**: Trim dimensions from spreadsheet parameters or HO scale defaults
- **Reusable**: Pure Python geometry library makes it testable and maintainable

## Installation

### Quick Start (FreeCAD)

1. Unzip `smart_trim_generator_v1.0.9.zip`
2. Run: `python3 smart_trim_freecad_installer.py`
3. Restart FreeCAD
4. Done! The macro is ready to use

### Manual Installation

If you prefer to install manually:

1. Copy `smart_trim_generator.FCMacro` to your FreeCAD Macro directory
   - **macOS**: `~/Library/Application Support/FreeCAD/Macro/`
   - **Linux**: `~/.FreeCAD/Macro/`
   - **Windows**: `%APPDATA%\FreeCAD\Macro\`

2. Create a `_lib` subdirectory in your Macro directory

3. Copy `smart_trim_geometry.py` to `Macro/_lib/`

## Usage

### Basic Workflow

1. Generate clapboard or shingles on a wall face using the clapboard or shingle generator
2. Select the generated clapboard or shingle object in the tree
3. **Macro menu** → **Recent macros** → **smart_trim_generator.FCMacro**
4. Smart trim generates corner, eave, and gable trim automatically

### Parameters

Trim dimensions come from your FreeCAD spreadsheet:

| Parameter | Cell | Default (HO scale) | Description |
|-----------|------|-------------------|-------------|
| `trim_width` | params.trim_width | 2.0 mm | Width of trim board profile |
| `trim_thickness` | params.trim_thickness | 1.0 mm | Thickness of trim material |

If no spreadsheet is found, HO scale defaults are used.

### Output

Smart trim creates a **compound object** with separate sub-objects:

```
SmartTrim_ClapboardWall_Extrude009_F009
├── SmartTrim_ClapboardWall_Extrude009_F009_Vertical   (corner boards)
├── SmartTrim_ClapboardWall_Extrude009_F009_Eave       (horizontal fascia)
└── SmartTrim_ClapboardWall_Extrude009_F009_Gable      (diagonal roof trim)
```

This structure lets you:
- Delete individual trim types if needed
- Apply different materials to different trim types
- Manually edit specific trim components

## Architecture

### Smart Trim Geometry Library (`smart_trim_geometry.py`)

Pure Python library with no FreeCAD dependencies. Provides:

- **Edge classification**: Distinguishes vertical, horizontal, and gable edges
- **Edge filtering**: Skips bottom edges and edges adjacent to features
- **Parameter validation**: Ensures trim dimensions are sensible
- **Vector utilities**: Cross-product, dot-product, angle calculations

The library is fully tested with pytest:

```bash
pytest test_smart_trim_geometry.py -v
```

### Smart Trim Generator Macro (`smart_trim_generator.FCMacro`)

FreeCAD macro that:

1. Gets user selection (clapboard or shingle object)
2. Parses object name to find source wall and face
3. Calls geometry library functions to classify edges
4. Creates trim geometry along each edge
5. Fuses trim parts by type into three sub-objects
6. Creates a compound for easy manipulation

## Edge Classification Rules

**Vertical edges** → Corner trim (corner boards)
- Parallel to the wall's vertical axis (within 5° tolerance)

**Horizontal edges** → Eave trim (fascia/soffit)
- Perpendicular to the wall's vertical axis (within 5° tolerance)
- Typically at top of wall where it meets roof

**Gable edges** → Gable trim
- Diagonal edges that are neither vertical nor horizontal
- Typical of sloped roofs or gable-end walls

**Skipped edges:**
- Bottom edge (foundation/sill level)
- Edges adjacent to doors or windows (future enhancement)

## Common Workflows

### Standard Rectangular Wall

1. Generate clapboard on all four faces of a wall
2. Run smart_trim on each clapboarded face
3. Get corner boards on all four vertical edges
4. Get eave trim on top edge
5. Result: Professional-looking framed wall

### Bay Window

Some buildings have bay windows where standard trim doesn't apply. Smart trim generates it anyway, giving you options:

- Delete the vertical trim on the bay
- Create custom trim for the curved corner
- Leave generated trim and adjust later

### Gable Roof

1. Generate clapboard on gable wall face
2. Run smart_trim
3. Get corner boards on vertical edges
4. Get gable trim on diagonal roof edges
5. Result: Complete gable-end wall trim

## Troubleshooting

### "Could not import smart_trim_geometry"

Make sure:
- `smart_trim_geometry.py` is in `FreeCAD/Macro/_lib/`
- The file is readable (check permissions)
- You're using FreeCAD 0.20 or later

### No trim generated

Check:
- Did you select a clapboard or shingle object? (Not the source wall)
- Does the object name match the expected pattern?
- Does the source wall still exist in the document?

### Trim geometry looks wrong

- Check that `trim_width` and `trim_thickness` are reasonable values
- HO scale typically uses 2-3mm trim boards
- Make sure the source wall geometry is valid (no degenerate faces)

## Development

### Running Tests

```bash
# From the smart_trim directory
pytest test_smart_trim_geometry.py -v

# Or with coverage
pytest --cov=smart_trim_geometry test_smart_trim_geometry.py
```

### Repository Integration

To add smart_trim to your FreeCAD-tools repository:

```bash
# Unzip the package
unzip smart_trim_generator_v1.0.0.zip

# Organize into git tree and stage
python3 smart_trim_git_populate.py

# Review and commit
git status
git diff --cached
git commit -m "Add smart trim generator v1.0.0"
```

The populate script expects to find your git repository at:
`/Users/blw/Documents/FreeCAD-github`

Edit the script if your path is different.

## Version History

### v1.0.0 (Initial Release)
- Edge classification (vertical, horizontal, gable)
- Edge filtering (skip bottom, skip holes)
- Three trim types: corner, eave, gable
- Compound output with separate sub-objects
- Parametric dimensions from spreadsheet
- Full test suite with 40+ tests

## Next Steps

Potential enhancements:

- **Shared trim geometry library**: Factor out common edge detection logic for use by shingle trim generator
- **Mitered corners**: Detect where corner and eave trim meet, create miter joints
- **Advanced edge filtering**: Detect and skip edges adjacent to doors/windows automatically
- **Trim profiles**: Support different trim profile shapes (Victorian, modern, etc.)
- **Material assignment**: Automatically assign materials to trim objects

## Author

Generated for model railroading with FreeCAD. Part of the COVA (Chesapeake & Ohio Virginia) layout project.

## License

Same as FreeCAD (LGPL v2+)
