# Adding f(x) Expression Support to Part Workbench Extrude Dialog

## Problem Statement

The PartDesign Pad dialog has f(x) buttons next to numeric fields (Length, Taper angle, etc.) that allow binding expressions from spreadsheets or other properties. The Part workbench Extrude dialog lacks this feature, forcing users to:

1. Enter a placeholder value in the dialog
2. Click OK to create the feature
3. Go back to the object's properties panel
4. Manually bind the expression there

## Root Cause Analysis

### Why PartDesign Pad Has f(x) Buttons

The expression button appears when a `Gui::QuantitySpinBox` widget is **bound** to a document object property. In PartDesign:

**File:** `src/Mod/PartDesign/Gui/TaskExtrudeParameters.cpp`

```cpp
// Line 214: Get pointer to feature's property
m_side1.Length = &extrude->Length;

// Line 144: Bind widget to property - THIS enables f(x) button
side.lengthEdit->bind(*side.Length);
```

The key is that the PartDesign Pad feature **already exists** before the dialog opens. The dialog edits an existing object, and widgets are bound directly to its properties.

### Why Part Extrude Lacks f(x) Buttons

The Part Extrude dialog works differently:

**File:** `src/Mod/Part/Gui/DlgExtrusion.cpp`

1. Dialog collects values from user (no feature exists yet)
2. On OK/Apply, creates the feature via Python command (line 540):
   ```cpp
   FCMD_OBJ_DOC_CMD(sourceObj, "addObject('Part::Extrusion','" << name << "')");
   ```
3. Writes values to feature via Python commands (line 868):
   ```cpp
   Gui::Command::doCommand(Gui::Command::Doc, "f.LengthFwd = %.15f", ui->spinLenFwd->value().getValue());
   ```

Since no feature exists when the dialog opens, there's nothing to bind the widgets to.

### Widget Comparison

Both dialogs use the same widget class:

| Dialog | Widget Class | Has f(x)? |
|--------|--------------|-----------|
| Part Extrude | `Gui::QuantitySpinBox` | No |
| PartDesign Pad | `Gui::PrefQuantitySpinBox` (extends QuantitySpinBox) | Yes |

The difference isn't the widget type - it's whether `.bind()` is called.

## Properties Available for Binding

**File:** `src/Mod/Part/App/FeatureExtrusion.cpp`

```cpp
ADD_PROPERTY_TYPE(LengthFwd, (0.0), "Extrude", App::Prop_None, ...);    // Line 119
ADD_PROPERTY_TYPE(LengthRev, (0.0), "Extrude", App::Prop_None, ...);    // Line 121
ADD_PROPERTY_TYPE(TaperAngle, (0.0), "Extrude", App::Prop_None, ...);   // Line 129
ADD_PROPERTY_TYPE(TaperAngleRev, (0.0), "Extrude", App::Prop_None, ...); // Line 131
```

These would bind to:
- `ui->spinLenFwd` → `LengthFwd`
- `ui->spinLenRev` → `LengthRev`
- `ui->spinTaperAngle` → `TaperAngle`
- `ui->spinTaperAngleRev` → `TaperAngleRev`

## Proposed Solution

### Required Changes

1. **Change command flow** - Create the `Part::Extrusion` feature BEFORE showing the dialog

2. **Store feature pointer** - Add member to `DlgExtrusion`:
   ```cpp
   Part::Extrusion* extrusion;
   ```

3. **Bind widgets in constructor** - After feature creation:
   ```cpp
   ui->spinLenFwd->bind(extrusion->LengthFwd);
   ui->spinLenRev->bind(extrusion->LengthRev);
   ui->spinTaperAngle->bind(extrusion->TaperAngle);
   ui->spinTaperAngleRev->bind(extrusion->TaperAngleRev);
   ```

4. **Handle cancel properly** - Delete the feature if user cancels (undo the creation)

5. **Refactor `writeParametersToFeature()`** - May no longer need Python command approach since properties are bound directly

### Complication: Multi-Object Extrusion

The current dialog supports extruding **multiple shapes** simultaneously (lines 516-552 loop over selected objects). Each creates a separate Extrusion feature.

This complicates the "create first, then edit" approach:
- Which feature do you bind to?
- How do you propagate expression bindings to all features?

**Possible approaches:**

A. **Single-object mode only** - Simplify to match PartDesign behavior. Only allow one shape when using expressions.

B. **Template feature** - Create one "template" feature for binding, clone settings to others on Apply.

C. **Hybrid mode** - Enable f(x) only when single object is selected; fall back to current behavior for multiple objects.

## Files to Modify

| File | Changes |
|------|---------|
| `src/Mod/Part/Gui/DlgExtrusion.h` | Add feature pointer member, modify constructor signature |
| `src/Mod/Part/Gui/DlgExtrusion.cpp` | Add bind() calls, refactor apply(), handle cancel/undo |
| `src/Mod/Part/Gui/Command.cpp` | Possibly modify command to pre-create feature |

## Effort Estimate

**Medium-sized refactor** - Not a one-liner, but well-defined scope:
- Core binding changes: ~2-4 hours
- Multi-object handling decision and implementation: ~2-4 hours  
- Testing and edge cases: ~2-4 hours
- Total: 1-2 days for experienced FreeCAD contributor

## Related Dialogs

Other Part workbench dialogs likely have the same issue:
- Part Revolve
- Part Loft
- Part Sweep
- Part Offset

The same pattern could be applied to add f(x) support to all of them.

## References

- FreeCAD source: https://github.com/FreeCAD/FreeCAD
- Key files examined:
  - `src/Mod/Part/Gui/DlgExtrusion.cpp` / `.h` / `.ui`
  - `src/Mod/PartDesign/Gui/TaskExtrudeParameters.cpp`
  - `src/Mod/PartDesign/Gui/TaskPadPocketParameters.ui`
  - `src/Mod/Part/App/FeatureExtrusion.cpp`

---

*Analysis performed: December 2024*
*FreeCAD version examined: 1.2-dev*
