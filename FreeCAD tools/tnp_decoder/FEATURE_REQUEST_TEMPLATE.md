# Feature Request: Topological Naming Problem (TNP) Error Decoder

## Summary

Add built-in decoding of TNP error messages to provide actionable diagnostics instead of cryptic geometry indices.

## Problem Statement

FreeCAD's report view outputs error messages like:

```
External geometry gville_passenger_station#Sketch004.e2 missing reference: Sketch003.;e7v2;SKT
```

These are **non-actionable** for users:
- No explanation of what `e2` or `e7v2` mean
- No description of the actual geometry affected
- No guidance on how to fix it
- Even experienced users need external tools to understand them

## Current Workaround

A community member has created a working solution: [freecad-tnp-decoder](https://github.com/yourname/freecad-tnp-decoder)

This decoder translates cryptic messages to human-readable output:

```
BROKEN REFERENCE in:
  Sketch: Sketch004 (Baggage wall openings)
  Geometry: e2

Was pointing to:
  Sketch: Sketch003 (Master XY)
  Geometry: edge 7 (Line) from (10.5, 20.3) to (15.2, 35.7)

EXPLANATION:
  The sketch 'Baggage wall openings' contains external geometry references to 'Master XY'.
  When 'Master XY' was edited, its geometry indices changed, breaking the reference.
```

## Proposed Solution

Integrate TNP error decoding into FreeCAD core:

### Location
- Add to Report View context menu: "Decode TNP Error"
- Or add to Sketcher menu when a sketch is active
- Or both

### Implementation
1. Parse TNP error format (already reverse-engineered in community solution)
2. Look up sketch labels and geometry coordinates
3. Display human-readable description
4. Optional: Highlight affected geometry in 3D view
5. Optional: Suggest fixes

### User Experience

**Before:**
```
Sketch004.e2 missing reference: Sketch003.;e7v2;SKT
```
(User confused, searches forums, finds workaround)

**After:**
```
Right-click error → "Decode"

Broken reference in Sketch004 (Baggage wall openings), edge 2
Was pointing to Sketch003 (Master XY), edge 7
This geometry is a Line from (10.5, 20.3) to (15.2, 35.7)

Fix: Either recreate external references or avoid editing Sketch003
```

## Why This Matters

- TNP is a fundamental limitation of FreeCAD's parametric model
- Users encounter it regularly
- Current error messages are incomprehensible without external tools
- Clear diagnostics would reduce support burden
- The error format is already well-defined internally

## Reference Implementation

A working Python implementation is available at:
https://github.com/yourname/freecad-tnp-decoder

This demonstrates:
- The error format can be parsed reliably
- Geometry information can be extracted and displayed
- The solution is practical and performant

## Related Issues

- #[Issue number if there's an existing TNP discussion]
- TNP discussions on FreeCAD forum

## Acceptance Criteria

- [ ] TNP errors can be decoded to show sketch labels and geometry info
- [ ] User receives actionable explanation of what's broken
- [ ] Solution integrates with Report View or Sketcher UI
- [ ] Documentation explains TNP cause and prevention

## Testing

Can be validated against the reference implementation with sample documents containing TNP errors.

---

**Note:** If FreeCAD adopts this feature, the community reference implementation can serve as a starting point for the core implementation.
