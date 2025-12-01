# Clapboard Generator v5.2.0

**Parametric Clapboard Siding Generator for FreeCAD**

This package contains the clapboard generator macro (v5.2.0) with critical bug fix: duplicate wall geometry elimination through Part::Compound output structure.

## What's New in v5.2.0

**Major Fix:** Eliminated duplicate wall geometry in clapboard output.

- **Before**: Output contained fused geometry (wall + skin), duplicating wall
- **After**: Output is a Part::Compound referencing both wall and skin separately
- **Benefit**: Cleaner exports, proper separation, smart trim integration ready

## Installation

### Quick Start (FreeCAD Only)

```bash
# 1. Unpack this package
cd ~/Downloads
tar -xzf clapboard-generator-v5.2.0.tar.gz
cd clapboard-generator-v5.2.0

# 2. Install to FreeCAD
python3 clapboard_freecad_installer.py

# 3. Done! Restart FreeCAD and use the macro
```

### Complete Integration (FreeCAD + Git Repository)

```bash
# 1. Unpack this package
cd ~/Downloads
tar -xzf clapboard-generator-v5.2.0.tar.gz
cd clapboard-generator-v5.2.0

# 2. Install to FreeCAD (first!)
python3 clapboard_freecad_installer.py

# 3. Organize in your git repository
python3 clapboard_git_populate.py

# 4. Review and commit
cd ~/Documents/FreeCAD-github
git diff --cached
git commit -m "clapboard_generator: v5.2.0 - Compound output, no duplicate wall"
git tag -a v5.2.0 -m "clapboard_generator v5.2.0"
```

## File Structure

```
clapboard-generator-v5.2.0/
├── clapboard_generator.FCMacro ........... FreeCAD macro (v5.2.0)
├── clapboard_geometry.py ................ Pure Python geometry library
├── clapboard_freecad_installer.py ....... Automated FreeCAD installer
├── clapboard_git_populate.py ............ Git repository organizer
├── README.md ............................ This file
└── [documentation files from outputs]
```

## Usage in FreeCAD

1. **Select wall faces** (Ctrl+click to select multiple)
2. **Run the macro**: Macro menu → Recent Macros → clapboard_generator.FCMacro
3. **Results**:
   - `ClapboardWall_*_F*` (Part::Compound) - References wall + skin
   - `ClapboardWall_*_F*_skin` (Part::Feature) - Just the clapboard geometry

## Parameters

Parameters are read from spreadsheet (default: "params" or "Spreadsheet"):

- `clapboard_height`: Reveal height (mm) — default 0.8mm (HO scale)
- `clapboard_thickness`: Thickness at bottom edge (mm) — default 0.2mm

## Key Changes from v5.1.0

### 1. Return Skin Only
```python
# OLD: combined = source_object.Shape.fuse(final_clapboards); return combined
# NEW: return final_clapboards  (skin only, no wall fusion)
```

### 2. Use Part::Compound
```python
# OLD: wall_obj = doc.addObject("Part::Feature", ...)
#      wall_obj.Shape = wall_compound

# NEW: compound_obj = doc.addObject("Part::Compound", ...)
#      skin_obj = doc.addObject("Part::Feature", ... + "_skin")
#      compound_obj.Links = [source_obj, skin_obj]
```

## Benefits

✅ **No duplicate wall geometry** - Wall stored once, referenced twice
✅ **Clean exports** - Select `_skin` object to export just clapboards
✅ **Smart trim ready** - Separate geometry enables trivial direction detection
✅ **Cleaner hierarchy** - Compound structure obvious in document tree
✅ **Smaller files** - No redundant geometry storage

## Testing

See `CLAPBOARD_TEST_CHECKLIST.md` for comprehensive testing guide:

1. Install macro
2. Select wall face
3. Run generator
4. Verify compound + skin structure
5. Check volumes (no duplication)
6. Test exports
7. Test smart trim integration

## Backward Compatibility

✅ Existing clapboard objects unchanged
✅ Old objects remain with previous structure
✅ New generations use improved compound structure
✅ Can coexist in same document
✅ Parameter interface unchanged

## Smart Trim Integration

Once clapboards are fixed with this version, smart_trim_generator should:
- Detect outward direction trivially (bbox extends ~0.15mm only)
- Filter hole edges cleanly (separate skin geometry)
- Work without geometric ambiguity

Expected behavior: smart trim "just works" with this version.

## What's Documented in This Package

Included documentation files:

- `QUICK_REFERENCE.txt` - One-page overview
- `BEFORE_AFTER_VISUAL.md` - Visual architecture comparison
- `CLAPBOARD_FIX_SUMMARY.md` - Complete technical explanation
- `CLAPBOARD_TEST_CHECKLIST.md` - Testing guide (30 min)
- `INTEGRATION_INSTRUCTIONS.md` - Git integration guide
- `IMPLEMENTATION_NOTES.md` - Deep technical details
- `README_DELIVERABLES.md` - Complete manifest

## Version History

- **v5.2.0** - Part::Compound output, no wall duplication (THIS VERSION)
- **v5.1.1** - Bug fix: return skin-only (development version)
- **v5.1.0** - Removed trim logic, began fusing (problematic)
- **v5.0.1** - Added geometry validation
- **v5.0.0** - Face-based selection rewrite

## Next Steps (After Testing)

1. ✅ Test with your models
2. ✅ Verify smart trim works better
3. ⏳ Fix TNP property links (App::PropertyLink instead of string)
4. ⏳ Apply same pattern to shingle generator
5. ⏳ Address remaining TODOs (extrusion direction, gable cutting, etc.)

## Troubleshooting

### Macro won't load
- Check FreeCAD Macro directory (use installer to find it)
- Verify `clapboard_geometry.py` is in `_lib/` subdirectory

### Compound not created
- Check Report View for error messages
- Verify you're using v5.2.0 (should see "Clapboard siding complete" message)

### Geometry looks wrong
- This wasn't changed—if appearance broke, something else is wrong
- Try regenerating with original macro version

### Volumes don't match
- Make sure you're measuring the right objects
- Compound references wall (use compound's reference link)
- Skin is separate (use skin object volume)

## Getting Help

1. Check `CLAPBOARD_TEST_CHECKLIST.md` for systematic testing
2. Review `IMPLEMENTATION_NOTES.md` for code-level details
3. Examine Report View output during generation
4. Compare with expected behavior in documentation

## System Requirements

- FreeCAD 0.20+ (tested with 1.0.x)
- Python 3.8+
- macOS, Linux, or Windows

## License

Same as FreeCAD (LGPL)

## Version Info

```
Clapboard Generator v5.2.0
Date: 2025-11-30
Status: Ready for testing and deployment
Risk Level: Low (focused architecture fix)
Backward Compatible: Yes
TNP-Safe: Partial (object references by Label, fix pending)
```

## Files in This Package

| File | Purpose | Status |
|------|---------|--------|
| clapboard_generator.FCMacro | Main macro (v5.2.0) | ✅ Updated |
| clapboard_geometry.py | Geometry library (v5.1.0) | ✅ Included |
| clapboard_freecad_installer.py | Auto FreeCAD installer | ✅ Provided |
| clapboard_git_populate.py | Git repository organizer | ✅ Provided |
| README.md | This file | ✅ Current |

## Next Release (Planned)

**v5.3.0** (after TNP property fix):
- Change `SourceObject` to App::PropertyLink
- Handle backward compatibility
- Better metadata preservation

---

**Installation time:** ~5 minutes
**Testing time:** ~30 minutes
**Integration time:** ~5 minutes

**Total:** ~40 minutes for complete validation and deployment

Ready to test! 🚀
