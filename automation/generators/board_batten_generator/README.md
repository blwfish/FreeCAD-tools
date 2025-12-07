# Board-and-Batten Siding Generator

Parametric FreeCAD macro for generating realistic board-and-batten siding for model railroading (HO/O/N scale).

## Features

- **Face-based selection**: Select specific faces in your 3D model to apply board-and-batten siding
- **Vertical boards**: Creates vertical boards with battens covering seams
- **Automatic gable trimming**: Boards are automatically trimmed flush to gable profiles
- **Hole cutting**: Automatically cuts holes for windows and doors
- **Spreadsheet integration**: Parameters can be read from a spreadsheet
- **Multi-face support**: Process multiple faces in a single operation
- **Pure geometry output**: Creates clean Part::Compound objects

## Usage

1. **Open your FreeCAD model** with wall faces you want to apply board-and-batten to
2. **Select faces**:
   - Click on the object in the 3D view
   - Ctrl+click on specific faces you want board-and-batten on
   - You can select multiple faces across different objects
3. **Run the macro**: `Macro > Macros > board_batten_generator.FCMacro > Execute`
4. The generator will create a new `BoardBattenWall_*` object with the siding

## Parameters

Default values (HO scale):
- **board_width**: 7.0mm - Width of each vertical board
- **batten_width**: 0.6mm - Width of batten strips covering seams
- **board_thickness**: 0.2mm - Thickness of board material
- **batten_projection**: 0.12mm - How far battens project from board surface

### Using Spreadsheet Parameters

Create a spreadsheet object named `params`, `BoardBattenParameters`, or `BuildingParameters` with cells:
- `board_width` - Board width in mm
- `batten_width` - Batten width in mm
- `board_thickness` - Board thickness in mm
- `batten_projection` - Batten projection in mm

The generator will automatically read these parameters if available.

## Examples

### Simple Wall
```
1. Select one or more flat wall faces
2. Run macro
3. Board-and-batten applied vertically
```

### Gable Wall
```
1. Select a face with gabled (peaked) top
2. Run macro
3. Boards are automatically trimmed to gable profile
```

### Multiple Faces
```
1. Select multiple faces (Ctrl+click)
2. Run macro
3. All faces processed into single compound object
```

## Architecture

The generator consists of:

- **board_batten_generator.FCMacro**: Main FreeCAD macro (FreeCAD-dependent)
- **board_batten_geometry.py**: Pure Python geometry functions (testable without FreeCAD)
- **tests/test_board_batten_geometry.py**: Pytest unit tests

## How It Works

1. **Face Detection**: Analyzes selected faces to determine orientation (YZ, XZ, or XY plane)
2. **Board Creation**: Creates vertical boards spanning the face height
3. **Batten Creation**: Places batten strips at board seams with slight projection
4. **Gable Trimming**: Uses face boundary intersection to trim boards flush with gables
5. **Hole Cutting**: Cuts holes for windows/doors from face wires
6. **Compounding**: Combines all siding into single Part::Compound

## Testing

Run the unit tests:
```bash
cd generators/board_batten_generator
env PYTHONPATH=. pytest tests/test_board_batten_geometry.py -v
```

## Version History

- **1.0.0** (2025-12-06): Initial release
  - Vertical board-and-batten siding generation
  - Face-based selection
  - Spreadsheet parameter support
  - Gable edge trimming
  - Multi-face compound output
  - Based on clapboard_generator v6.0.0 architecture

## Related Generators

- **clapboard_generator**: Horizontal overlapping clapboard siding
- **shingle_generator**: Roof shingles with staggered courses

## License

Generated for model railroading purposes. Use freely for hobby and commercial projects.
