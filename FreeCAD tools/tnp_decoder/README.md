# FreeCAD TNP Error Decoder

**Decode FreeCAD's cryptic Topological Naming Problem (TNP) error messages into actionable, human-readable diagnostics.**

## The Problem

FreeCAD's report view outputs error messages like this:

```
17:19:45 <Sketch> SketchObject.cpp(9133): External geometry gville_passenger_station#Sketch004.e2 missing reference: Sketch003.;e7v2;SKT
17:19:45 <Sketch> SketchObject.cpp(9133): External geometry gville_passenger_station#Sketch006.e6 missing reference: Sketch003.;e7v2;SKT
```

These errors are **cryptic and non-actionable**:
- What does `e2` mean? What does `e7v2` mean?
- Which geometry is broken?
- What should I do about it?
- What was that sketch even referencing?

Even experienced FreeCAD users struggle to understand these messages.

## The Solution

This tool decodes the error format into human-readable output:

```
===============================================================================
TNP Error Decoded
===============================================================================

BROKEN REFERENCE in:
  Sketch: Sketch004 (Baggage wall openings)
  Geometry: e2

Was pointing to:
  Sketch: Sketch003 (Master XY)
  Geometry: edge 7 (Line)
      From (10.5, 20.3) to (15.2, 35.7)

EXPLANATION:
  The sketch 'Baggage wall openings' contains external geometry references to 'Master XY'.
  When 'Master XY' was edited, its geometry indices changed, breaking the reference.
  You need to either:
    1. Delete and re-create the external geometry references in 'Baggage wall openings'
    2. Avoid editing 'Master XY' - treat it as a locked master sketch

===============================================================================
```

## Installation

### Option 1: Manual Installation

1. Place the `tnp_decoder` package (with `tools/` subdirectory) somewhere accessible:
   ```
   ~/Documents/FreeCAD-Tools/tnp_decoder/
   ```

2. In FreeCAD's Python console, import it:
   ```python
   import sys
   sys.path.insert(0, '~/Documents/FreeCAD-Tools')
   from tnp_decoder import decode_tnp, decode_tnp_batch
   ```

### Option 2: Auto-Load on FreeCAD Startup (Recommended)

1. Create the directory structure in your FreeCAD Macro folder:
   ```
   macOS:   ~/Library/Application Support/FreeCAD/Macro/
   Linux:   ~/.FreeCAD/Macro/
   Windows: %APPDATA%\FreeCAD\Macro\
   ```

2. Place the `tnp_decoder` package there:
   ```
   macOS:   ~/Library/Application Support/FreeCAD/Macro/tnp_decoder/
   Linux:   ~/.FreeCAD/Macro/tnp_decoder/
   Windows: %APPDATA%\FreeCAD\Macro\tnp_decoder/
   ```

3. Copy `FreeCAD_startup_macro.py` to your Macros folder as `10_load_tnp_decoder.py`:
   ```
   macOS:   ~/Library/Application Support/FreeCAD/Macro/10_load_tnp_decoder.py
   Linux:   ~/.FreeCAD/Macro/10_load_tnp_decoder.py
   Windows: %APPDATA%\FreeCAD\Macro\10_load_tnp_decoder.py
   ```
   (The `10_` prefix ensures it loads early)

4. Restart FreeCAD

5. The functions will be automatically available in the Python console:
   ```python
   decode_tnp("Sketch004.e2 missing reference: Sketch003.;e7v2;SKT")
   ```

### Directory Structure

The package should be organized like this (supporting modules in `tools/` subdirectory):

```
tnp_decoder/
├── __init__.py
├── decode_tnp.py
├── tools/
│   ├── __init__.py
│   └── [utility modules here]
└── FreeCAD_startup_macro.py
```

The `tools/` subdirectory keeps utility modules out of the FreeCAD Macro panel UI while keeping them accessible to the main decoder module.

## Usage

### Decode a Single Error

Copy one error line from the report view and decode it:

```python
decode_tnp("Sketch004.e2 missing reference: Sketch003.;e7v2;SKT")
```

### Decode Multiple Errors at Once

Copy the entire error block and paste it:

```python
decode_tnp_batch("""
Sketch004.e2 missing reference: Sketch003.;e7v2;SKT
Sketch004.e3 missing reference: Sketch005.;e11;SKT
Sketch006.e1 missing reference: Sketch005.;e2v1;SKT
""")
```

### Scan Document for All TNP Issues

```python
errors = scan_document_for_tnp()
for error in errors:
    print(error.format_report())
```

## Understanding the Error Format

FreeCAD's internal error format is undocumented. This decoder interprets:

```
SketchXXX.eN missing reference: SketchYYY.;eNvM;SKT
```

Where:
- `SketchXXX` - The sketch with the broken reference
- `e` or `g` - Type of geometry (edge/general)
- `N` - Index number in the geometry list
- `SketchYYY` - The sketch being referenced
- `vM` - Optional vertex number (often not used)
- `SKT` - Sketch geometry type indicator

Examples:
- `e2` = edge #2
- `e7v2` = edge #7, vertex #2
- `g15v2` = general geometry #15, vertex #2

## Why Does This Happen?

**Root Cause:** When you edit a sketch that other sketches reference externally:
1. Editing reorders or removes geometry
2. FreeCAD renumbers the geometry indices
3. External references pointing to specific indices become stale
4. You get "missing reference" errors with no clear path to fix them

**Prevention:** Treat master sketches as locked templates. Once you've created external references to them, don't edit them. Create new master sketches if needed instead.

## Proposed Feature for FreeCAD Core

This tool demonstrates a capability that should be built into FreeCAD:

### Ideal Implementation
- **Location:** Report View context menu or Sketcher menu
- **Behavior:** Right-click TNP error → "Decode error" or "Show affected geometry"
- **Integration:** Display the human-readable description inline in the report view
- **Scope:** Automatically decode all TNP errors as they appear

### What It Should Do
1. Parse TNP error messages automatically
2. Look up sketch labels and geometry coordinates
3. Display human-readable explanations
4. Optional: Highlight affected geometry in the 3D view
5. Optional: Suggest fixes (recreate refs, lock sketches, etc.)

### Why FreeCAD Should Have This
- TNP is a fundamental limitation of FreeCAD's parametric modeling
- Users encounter it regularly but can't understand the error messages
- The error format is already well-defined internally; it just needs translation
- Clear diagnostics would reduce support burden and improve user experience

## Contributing

Found a bug? Have suggestions? Fork, modify, and submit a PR!

## License

MIT License - Use freely in your projects, modify as needed, contribute back if you like.

## Author

Generated for the FreeCAD model railroading community.
Contact: See your local FreeCAD forum or GitHub issues.

---

**Happy sketching!** And remember: master sketches are your friends once you lock them. 🚂
