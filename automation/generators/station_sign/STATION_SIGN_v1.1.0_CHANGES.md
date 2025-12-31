# Station Sign Generator v1.1.0 Changes

## Fixed Issues

### 1. Border Gap (FIXED ✓)
**Problem:** Border and text were touching - no visible gap
**Solution:** Changed border calculation structure to: `[border][gap][text][gap][border]`
- Added explicit `borderGap` parameter (default 0.5mm)
- Border inner rectangle is now inset by `borderThickness` only
- Text is centered within the inner area, which already includes the gap
- Gap is now visible on all four sides between border and text

### 2. ShapeString Cleanup (FIXED ✓)
**Problem:** ShapeString object was only hidden, not removed
**Solution:** Changed line 317 from:
```python
text_obj.Visibility = False  # Hide the ShapeString
```
To:
```python
doc.removeObject(text_obj.Name)  # Remove the ShapeString properly
```

### 3. Text Centering (IMPROVED ✓)
**Problem:** Text positioning was close but not perfectly centered
**Solution:** Simplified calculation:
```python
# Center text in the available space (inner area minus border)
available_width = inner_w
available_height = inner_h

text_x = inner_x + (available_width - text_width) / 2
text_y = inner_y + (available_height - text_height_dim) / 2
```

### 4. Input Method (CHANGED ✓)
**Problem:** Dialog methods were failing unreliably
**Solution:** Changed to object-based input:
- User creates any object (box, sketch, etc.)
- Sets the object's `Label` property to the station name
- Selects the object
- Runs the macro
- Macro reads station name from `Gui.Selection.getSelection()[0].Label`

## New Parameters

Added to parameter system:
- `borderThickness`: 0.5mm (was hardcoded, now in params)
- `borderGap`: 0.5mm (new parameter for gap between border and text)

Removed:
- `borderPaddingHorizontal` (replaced by borderGap)
- `borderPaddingVertical` (replaced by borderGap)

## New Metadata Properties

Added to generated sign objects:
- `BorderThickness`: Records the border thickness used
- `BorderGap`: Records the gap size used

## Structure

Sign structure is now clearly:
```
[Background slab: 2*materialThickness]
  [Border frame: materialThickness height]
    [Gap: borderGap on all sides]
      [Text: materialThickness height, centered]
```

## Usage

```python
# 1. Create input marker
box = Part.makeBox(10, 10, 10)
marker = doc.addObject("Part::Feature", "Marker")
marker.Shape = box
marker.Label = "Gordonsville"  # ← Station name goes here

# 2. Select the marker in the GUI tree view

# 3. Run macro: Macro → Macros → station_sign_generator → Execute
```

## Files Provided

1. `station_sign_generator_v1.1.0.FCMacro` - The fixed macro
2. `test_sign_input.py` - Test script to create input object
3. This README

## Installation

Copy `station_sign_generator_v1.1.0.FCMacro` to:
- macOS: `~/Library/Application Support/FreeCAD/Macro/`
- Linux: `~/.FreeCAD/Macro/`
- Windows: `%APPDATA%\FreeCAD\Macro\`

Or use FreeCAD's Macro → Macros → Create to create a new macro and paste the contents.
