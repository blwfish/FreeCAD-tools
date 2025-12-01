# Smart Trim Generator v1.1.0

**Parametric Trim Generator for FreeCAD**

Applies corner, eave, and gable trim to wall and roof faces decorated with clapboard or shingles.

## What's New in v1.1.0

**Major Improvement:** Full compatibility with new clapboard v5.3.0 and shingle v4.1.0!

- **Handles PropertyLink:** Works with new PropertyLink format (object references)
- **Backward Compatible:** Still works with old PropertyString format (label strings)
- **Auto-Detects:** Automatically detects which format is being used
- **More Robust:** PropertyLink-based objects survive renames seamlessly

## Installation

### Quick Start (FreeCAD Only)

```bash
tar -xzf smart-trim-generator-v1.1.0.tar.gz
cd smart-trim-generator-v1.1.0
python3 smart_trim_freecad_installer.py
```

### Complete Integration (FreeCAD + Git Repository)

```bash
tar -xzf smart-trim-generator-v1.1.0.tar.gz
cd smart-trim-generator-v1.1.0
python3 smart_trim_freecad_installer.py
python3 smart_trim_git_populate.py
```

## File Structure

```
smart-trim-generator-v1.1.0/
├── smart_trim_generator.FCMacro ........ Main macro (v1.1.0)
├── smart_trim_geometry.py ............. Pure Python geometry library
├── smart_trim_freecad_installer.py ... FreeCAD installer script
├── smart_trim_git_populate.py ......... Git repository organizer
└── README.md .......................... This file
```

## Usage in FreeCAD

1. **Select a clapboard or shingle object** that has been generated
2. **Run the macro:** Macro menu → Recent Macros → smart_trim_generator.FCMacro
3. **Results:**
   - `SmartTrim_*_Vertical` - Corner trim (vertical edges)
   - `SmartTrim_*_Eave` - Eave trim (horizontal edges)
   - `SmartTrim_*_Gable` - Gable trim (diagonal edges)
   - All grouped in a Part::Compound for easy management

## Parameters

Parameters are read from spreadsheet (default: "params" or "Spreadsheet"):

- `trim_width`: Width of trim profile (mm) — default 2.0mm
- `trim_thickness`: Thickness of trim material (mm) — default 1.0mm

## Key Features

✅ **Works with clapboard v5.3.0+** (PropertyLink enabled)
✅ **Works with shingle v4.1.0+** (PropertyLink enabled)
✅ **Backward compatible** with old objects (PropertyString)
✅ **Handles mirrors** (Part::Mirroring and PartDesign::Mirrored)
✅ **Detects holes** (windows/doors in wall faces)
✅ **Edge classification** (vertical/horizontal/gable)
✅ **Intelligent trim placement** (corner/eave/gable)

## v1.1.0 Technical Details

### What Changed

In the `get_source_object_and_face()` function, added automatic detection of SourceObject format:

```python
if isinstance(source_object_value, str):
    # OLD FORMAT: PropertyString (label lookup)
else:
    # NEW FORMAT: PropertyLink (direct reference)
```

### Why This Matters

**With PropertyLink (v5.3.0+):**
- Trim automatically finds source wall/roof even after renames
- More reliable object tracking
- Cleaner FreeCAD architecture

**With PropertyString (legacy):**
- Still works exactly as before
- No changes required to existing objects
- Graceful fallback

### Automatic Detection

No user configuration needed! The macro detects which format your objects use and handles accordingly.

## Testing

After installation, try this workflow:

1. Generate a clapboard or shingle object
2. Select it
3. Run smart_trim_generator
4. Verify trim appears correctly
5. Rename the source wall/roof
6. Verify trim object still finds the source (PropertyLink feature!)

## Backward Compatibility

✅ Works with clapboard v5.2.0 and earlier
✅ Works with shingle v4.0.0 and earlier
✅ Works with existing trim-decorated objects
✅ No migration needed

## Version History

```
v1.1.0 (NOW)    ← PropertyLink support, backward compat with PropertyString
  ↑
v1.0.9          ← Works with old PropertyString only
  ↑
v1.0.0          ← Initial release
```

## Troubleshooting

### "SourceObject property is None"
The clapboard/shingle object exists but its SourceObject reference is unset. This shouldn't happen with normal generation but could occur with corrupted objects. Regenerate the clapboard/shingle.

### "Source object not found"
For old PropertyString format: The source wall/roof was renamed after the clapboard was generated. Either rename it back or regenerate the clapboard.

For new PropertyLink format: Shouldn't happen (PropertyLink survives renames). If it does, check that the source object wasn't deleted.

### Trim on wrong side
Check the normal direction calculation. This is typically caused by unusual face orientation. Review the console output for "Outward direction" messages.

### No trim generated
Common causes:
- Face has no edges (degenerate geometry)
- All edges are at bottom of wall (bottom edges are skipped)
- Face is covered by holes/windows (no perimeter edges)

Check console output for edge classification details.

## System Requirements

- FreeCAD 0.20+ (tested with v1.0.x)
- Python 3.8+
- macOS, Linux, or Windows

## Integration with Clapboard & Shingle

Smart trim is designed to work seamlessly with:
- **Clapboard Generator v5.3.0+** (recommended) or v5.2.0 and earlier
- **Shingle Generator v4.1.0+** (recommended) or v4.0.0 and earlier

Typical workflow:
1. Generate walls with clapboards
2. Generate roofs with shingles
3. Apply smart trim to both
4. Final result: professional-looking detailed buildings

## Performance

Typical operation for a wall face:
- 10-50 edges: ~5 seconds
- 50-100 edges: ~10 seconds
- Fusing trim parts: ~2 seconds per 10 parts

---

**Production-ready trim generator. Works with modern and legacy generators.** ✅

Ready to deploy alongside clapboard v5.3.0 and shingle v4.1.0!
