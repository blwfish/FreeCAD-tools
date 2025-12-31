# Station Sign Generator v1.1.1 Changes

## Changes from v1.1.0 → v1.1.1

### 1. Increased Border Gap (Based on Photo Reference)
**Change:** Increased default `borderGap` from 0.5mm to 1.0mm

**Rationale:** Analysis of the Gordonsville depot photo shows the gap between
the border and text is approximately 2x the border thickness, not equal to it.

**Before:** borderGap = 0.5mm (equal to borderThickness)
**After:** borderGap = 1.0mm (2x borderThickness)

This makes the sign larger overall while keeping border and text the same size,
matching the proportions visible in the historical photo.

### 2. Improved ShapeString Cleanup
**Change:** Hide ShapeString before removing it

**Code change:**
```python
# Before:
doc.removeObject(text_obj.Name)

# After:
text_obj.ViewObject.Visibility = False
doc.recompute()
doc.removeObject(text_obj.Name)
```

**Rationale:** Hiding the object before removal prevents potential display
artifacts and ensures the object is fully cleaned up from the view.

## Photo Analysis

From the Gordonsville depot 1970 photo:
- Border thickness: ~1/9 of letter height → 0.5mm in HO scale
- Gap (white space): ~2x border thickness → 1.0mm in HO scale
- This gives nice, readable spacing matching C&O standard practice

## Updated Sign Structure

```
Total width = (2 × 0.5mm border) + (2 × 1.0mm gap) + text_width
Total height = (2 × 0.5mm border) + (2 × 1.0mm gap) + text_height

[Background slab: 0.4mm thick (2 × materialThickness)]
  [Border frame: 0.2mm thick, 0.5mm wide]
    [Gap: 1.0mm on all sides]
      [Text: 0.2mm thick, centered]
```

## Files

- `station_sign_generator_v1.1.1.FCMacro` - Updated macro
- `STATION_SIGN_v1.1.1_CHANGES.md` - This file
