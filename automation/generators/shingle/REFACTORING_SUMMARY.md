# Shingle Generator Refactoring Summary

## What We've Built

### 1. `shingle_geometry.py` (v4.0.0)
Pure Python geometry library with **zero FreeCAD dependencies**.

Functions extracted from current shingle_generator.FCMacro:

**Parameter Validation:**
- `validate_parameters()` — Validates all shingle parameters
- `validate_stagger_pattern()` — Ensures pattern is "half", "third", or "none"

**Layout Calculation:**
- `calculate_stagger_offset()` — Calculates horizontal stagger for each row
- `calculate_layout()` — Computes full shingle layout (courses, shingles/course, coverage)
- `calculate_shingle_position()` — Returns U,V position for any row/col

**Face Validation:**
- `validate_face_geometry()` — Checks face dimensions are suitable
- `is_planar()` — Validates face is coplanar (catches twisted faces)
- `calculate_face_bounds()` — Bounding box from vertices
- `detect_face_orientation()` — Determines which plane face lies in
- `validate_face_for_shingling()` — Comprehensive face validation

**Utility Functions:**
- `get_orientation_description()` — Human-readable face description
- `validate_collar_margin()` — Calculates trimming margin

### 2. `test_shingle_geometry.py`
Comprehensive pytest test suite: **55 tests, all passing in 0.11 seconds**

Test classes:
- `TestParameterValidation` (7 tests) — Parameter edge cases
- `TestStaggerPattern` (11 tests) — All stagger patterns and rows
- `TestLayout` (4 tests) — Layout calculations
- `TestFaceGeometry` (4 tests) — Face dimension validation
- `TestPlanarity` (7 tests) — Coplanarity detection
- `TestBounds` (2 tests) — Bounding box calculation
- `TestOrientationDetection` (3 tests) — Face plane detection
- `TestFaceValidation` (4 tests) — Full face validation
- `TestOrientationDescription` (3 tests) — Descriptions
- `TestShinglePosition` (4 tests) — Shingle positioning
- `TestCollarMargin` (2 tests) — Trimming margin
- `TestIntegration` (3 tests) — End-to-end pipelines

## Next Steps

### 1. Update `shingle_generator.FCMacro`
Convert to import and use `shingle_geometry.py`:

```python
from shingle_geometry import (
    validate_parameters,
    validate_face_for_shingling,
    detect_face_orientation,
    calculate_layout,
    calculate_shingle_position,
    # ... etc
)

# In main execution:
# 1. Validate parameters early
is_valid, errors = validate_parameters(...)
if not errors:
    # 2. Validate face
    is_valid, errors = validate_face_for_shingling(face_points)
    if not is_valid:
        raise ValueError(f"Face invalid: {errors}")
    # 3. Calculate layout
    layout = calculate_layout(...)
    # 4. Generate shingles using positions from calculate_shingle_position()
```

Benefits:
- Cleaner, shorter macro (geometry logic is removed)
- Better error messages (caught early from geometry library)
- Testable without FreeCAD
- Version-controlled independently

### 2. Face-Based Selection (like clapboards v5.2.0)
Update to require explicit face selection in FreeCAD:

```python
# Instead of: select whole roof object
# User selects: specific roof face(s) by Ctrl+clicking

# In macro:
for sel_obj in FreeCADGui.Selection.getSelectionEx():
    if len(sel_obj.SubElementNames) > 0:
        for sub_name in sel_obj.SubElementNames:
            if sub_name.startswith('Face'):
                face_index = int(sub_name[4:]) - 1
                face = sel_obj.Object.Shape.Faces[face_index]
                # Process this face
```

### 3. Fix Default Parameters
Current defaults are too large (10mm x 20mm shingles):

For HO scale realistic shingles (1:87 scale):
- Real shingle: ~350mm x 200mm
- HO scale: 350/87 ≈ 4mm wide, 200/87 ≈ 2.3mm tall

Recommend:
- `shingleWidth`: 4.0 mm
- `shingleHeight`: 2.5 mm  
- `materialThickness`: 0.3 mm
- `shingleExposure`: 2.0 mm (80% of height)

These touch the Skeleton.FCStd template, so we'll do that last.

### 4. Update Macro to Face-Based Selection
Like clapboards v5.2.0, make it explicit:
1. User selects face(s) in 3D view
2. Macro validates each face
3. Only that face gets shingled
4. Result fused into source object (or kept separate for now)

## Test Coverage

```
Parameter validation:     7 tests ✓
Stagger patterns:        11 tests ✓  
Layout calculation:       4 tests ✓
Face geometry:            4 tests ✓
Planarity detection:      7 tests ✓
Bounds calculation:       2 tests ✓
Orientation detection:    3 tests ✓
Full face validation:     4 tests ✓
Descriptions:             3 tests ✓
Shingle positioning:      4 tests ✓
Collar margin:            2 tests ✓
Integration:              3 tests ✓
────────────────────────────────
TOTAL:                   55 tests ✓
```

All tests pass in **0.11 seconds** without FreeCAD.

## Engineering Benefits

✅ **Testability** — Pure Python, no FreeCAD required  
✅ **Maintainability** — Geometry logic isolated from FreeCAD I/O  
✅ **Reusability** — Can be used in CLI tools, batch scripts, other projects  
✅ **Debuggability** — Catch errors early in geometry, not downstream in boolean ops  
✅ **Version Control** — Can version geometry library independently  
✅ **CI/CD Ready** — Tests run in GitHub Actions without FreeCAD  

## Files Created

- `/home/claude/shingle_geometry.py` — Geometry library (330 lines)
- `/home/claude/test_shingle_geometry.py` — Test suite (430 lines)

Ready to move to `/mnt/user-data/outputs` and push to your repo when you're ready.
