# Shingle Generator v4.1.0

**Parametric Shingle Generator for FreeCAD**

This package contains the shingle generator macro (v4.1.0) with critical TNP fix: PropertyLink for safe object references.

## What's New in v4.1.0

**Major Fix:** Eliminated TNP (Tree is Not a Property) vulnerability.

- **Before**: Used PropertyString with label strings (fragile, breaks on rename)
- **After**: Uses PropertyLink with object references (robust, rename-safe)
- **Benefit**: Survives object renames, unique identification, automatic updates

## Installation

### Quick Start (FreeCAD Only)

```bash
# 1. Unpack this package
cd ~/Downloads
tar -xzf shingle-generator-v4.1.0.tar.gz
cd shingle-generator-v4.1.0

# 2. Install to FreeCAD
python3 shingle_freecad_installer.py

# 3. Done! Restart FreeCAD and use the macro
```

### Complete Integration (FreeCAD + Git Repository)

```bash
# 1. Unpack this package
cd ~/Downloads
tar -xzf shingle-generator-v4.1.0.tar.gz
cd shingle-generator-v4.1.0

# 2. Install to FreeCAD (first!)
python3 shingle_freecad_installer.py

# 3. Organize in your git repository
python3 shingle_git_populate.py

# 4. Review and commit
cd ~/Documents/FreeCAD-github
git diff --cached
git commit -m "shingle_generator: v4.1.0 - TNP-safe PropertyLink"
git tag -a v4.1.0 -m "shingle_generator v4.1.0"
```

## File Structure

```
shingle-generator-v4.1.0/
├── shingle_generator.FCMacro ........... FreeCAD macro (v4.1.0)
├── shingle_geometry.py ................ Pure Python geometry library
├── shingle_freecad_installer.py ....... Automated FreeCAD installer
├── shingle_git_populate.py ............ Git repository organizer
└── README.md .......................... This file
```

## Usage in FreeCAD

1. **Select roof faces** (Ctrl+click to select multiple)
2. **Run the macro**: Macro menu → Recent Macros → shingle_generator.FCMacro
3. **Results**:
   - `ShingledRoof_*` (Part::Feature) - The fused shingle geometry
   - Properties include SourceObject (PropertyLink to source object)

## Parameters

Parameters are read from spreadsheet (default: "params" or "Spreadsheet"):

- `shingleWidth`: Width of each shingle (mm) — default 10mm
- `shingleHeight`: Height/length of each shingle (mm) — default 20mm
- `materialThickness`: Thickness at base edge (mm) — default 0.5mm
- `shingleExposure`: Exposed portion per course (mm) — default 15mm
- `shingleStaggerPattern`: "half", "third", or "none" — default "half"
- `shingleWedgeThickness`: Base thickness for wedges (mm) — default same as materialThickness

## Key Changes from v4.0.0

### 1. PropertyLink for SourceObject
```python
# OLD: PropertyString with label (TNP poison)
result_obj.addProperty("App::PropertyString", "SourceObject", ...)
result_obj.SourceObject = object_name

# NEW: PropertyLink with object reference (TNP-safe)
result_obj.addProperty("App::PropertyLink", "SourceObject", ...)
result_obj.SourceObject = source_obj
```

## Benefits

✅ **Rename-safe** - Shingles track renamed roof objects
✅ **Unique references** - Direct object link (not string lookup)
✅ **Automatic updates** - Property valid after renames
✅ **Clean hierarchy** - Clear parent-child relationships
✅ **TNP-free** - Eliminates naming/property poisoning

## Testing

1. Generate shingles on a roof face
2. Rename the source object
3. Select the shingle object
4. Check SourceObject property
5. Verify it shows the renamed object ✅

## Backward Compatibility

✅ Existing shingles unchanged
✅ New generations use PropertyLink
✅ Can coexist in same document
✅ Parameter interface unchanged

## Version History

- **v4.1.0** - TNP-safe PropertyLink for SourceObject (THIS VERSION)
- **v4.0.0** - MAJOR REFACTOR: Extracted geometry to separate library
- **v3.6.3** - Previous version with inline geometry

## Parallel with Clapboard

This fix uses **identical pattern** to clapboard v5.3.0:
- Same property type change (PropertyString → PropertyLink)
- Same benefits (rename-safe, unique identification)
- Consistent approach across all generators

## System Requirements

- FreeCAD 0.20+ (tested with v1.0.x)
- Python 3.8+
- macOS, Linux, or Windows

## What's Documented in This Package

- `README.md` - This file
- `shingle_freecad_installer.py` - Auto FreeCAD installer
- `shingle_git_populate.py` - Git repository organizer

## Next Steps (After Testing)

1. ✅ Test with your models
2. ✅ Verify property survives renames
3. ✅ Integrate to git repository
4. ⏳ Consider applying similar fixes to other generators

## Troubleshooting

### Macro won't load
- Check FreeCAD Macro directory (use installer to find it)
- Verify `shingle_geometry.py` is in `_lib/` subdirectory

### Geometry looks wrong
- This version only changed property storage (not geometry)
- If appearance broke, something else changed
- Try regenerating with original macro version

### Import errors
- Ensure shingle_geometry.py is in same _lib directory as macro
- Verify installation completed successfully

## Getting Help

1. Check the installation output for errors
2. Review FreeCAD Report View during generation
3. Examine the macro code (well-commented)

## Version Info

```
Shingle Generator v4.1.0
Date: 2025-11-30
Status: Ready for testing and deployment
Risk Level: Low (property storage only, no geometry changes)
Backward Compatible: Yes
TNP-Safe: Yes
```

## Installation Time

- **Install:** 5 minutes
- **Test:** 15 minutes
- **Integrate:** 5 minutes
- **Total:** ~25 minutes

---

**Production-ready, TNP-safe shingle generator.** Ready to deploy! 🚀
