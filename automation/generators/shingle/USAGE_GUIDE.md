# Shingle Generator v4.0.0 Usage Guide

## Installation

1. **Download files to your FreeCAD macro directory:**
   - `shingle_geometry.py` — Pure geometry library (required)
   - `shingle_generator_v4.FCMacro` — Updated macro (required)
   - `test_shingle_geometry.py` — Tests (optional, for development)

   On macOS: `~/Library/Application\ Support/FreeCAD/Macro/`
   On Linux: `~/.FreeCAD/Macro/`
   On Windows: `%APPDATA%\FreeCAD\Macro\`

2. **Both files must be in the same directory** (macro imports geometry library)

## Usage

### Step 1: Prepare Your Model
- Create a roof surface or extrude a face to make it 3D
- The face must be planar (no twisted or warped surfaces)

### Step 2: Select Roof Face(s)
In FreeCAD 3D view:
1. Click on a roof surface to select it
2. Hold **Ctrl** and click additional faces to select multiple roof surfaces
3. (Optional) Set shingle parameters in a Spreadsheet

### Step 3: Run the Macro
1. Macro menu → Recent macros → **shingle_generator_v4.FCMacro**
   OR
2. Macro menu → Execute macro → browse to `shingle_generator_v4.FCMacro`

### Step 4: Monitor Progress
The macro will:
1. Validate all parameters
2. Validate each selected face
3. Generate shingles
4. Fuse them into a single solid
5. Trim to face boundaries
6. Create a new object named `ShingledRoof_YourObjectName`

## Parameters

### Default Values (HO Scale - Currently Too Large)
```
shingleWidth:           10.0 mm   (currently too large for HO)
shingleHeight:          20.0 mm   (currently too large for HO)
materialThickness:      0.5 mm    (reasonable)
shingleExposure:        15.0 mm   (overlap pattern)
shingleStaggerPattern:  "half"    (half, third, or none)
```

### Recommended HO Scale Parameters
```
shingleWidth:           4.0 mm    (realistic for HO scale)
shingleHeight:          2.5 mm    (realistic for HO scale)
materialThickness:      0.3 mm    (thin plastic for 3D printing)
shingleExposure:        2.0 mm    (80% exposed, 20% overlap)
shingleStaggerPattern:  "half"    (standard roofing pattern)
```

### Setting Parameters via Spreadsheet
Create a spreadsheet object named "Spreadsheet" with these cells:

| Cell | Value |
|------|-------|
| shingleWidth | 4.0 |
| shingleHeight | 2.5 |
| materialThickness | 0.3 |
| shingleExposure | 2.0 |
| shingleStaggerPattern | half |

The macro will automatically read from the spreadsheet if it exists.

## Parameter Details

### shingleWidth
The width of each individual shingle (in the direction along the roof ridge).

HO Scale Reference:
- Real shingle: ~350mm wide
- HO scale (1:87): 350 ÷ 87 ≈ 4mm

### shingleHeight
The full height/length of each shingle (in the direction of the roof slope).

HO Scale Reference:
- Real shingle: ~200mm long
- HO scale (1:87): 200 ÷ 87 ≈ 2.3mm

### materialThickness
How thick the shingle material is. This affects both the exposed surface and the overlap.

- For 3D printing: 0.3-0.5mm
- For laser cutting: depends on material (0.5-1.5mm typical)

### shingleExposure
The visible height of each course (how much shows before the next course overlaps it).

Typical: 75-80% of shingle height
- If height is 2.5mm, exposure should be ~2.0mm
- Overlap = height - exposure = 2.5 - 2.0 = 0.5mm

### shingleStaggerPattern
How courses offset horizontally to create a realistic brick/shingle pattern:

- **"half"** — Each row offset by 50% of width. Most realistic.
- **"third"** — Each row offset by 33% of width. Creates 3-row repeat pattern.
- **"none"** — No offset. Vertical courses line up (less realistic).

## Stagger Pattern Examples

### "half" pattern (recommended)
```
Row 0:  [====][====][====]
Row 1:    [====][====][====]
Row 2:  [====][====][====]
Row 3:    [====][====][====]
```

### "third" pattern
```
Row 0:  [====][====][====]
Row 1:     [====][====][====]
Row 2:       [====][====][====]
Row 3:  [====][====][====]
```

### "none" pattern
```
Row 0:  [====][====][====]
Row 1:  [====][====][====]
Row 2:  [====][====][====]
```

## Output

Each run creates a new object:
- Name: `ShingledRoof_YourRoofObjectName`
- Type: `Part::Feature` (solid body)
- Properties: Includes metadata (generator name, version, source object)

You can:
- **Delete and regenerate** — If parameters change, delete the result and re-run
- **Fuse with structural wall** — `Part → Boolean → Fuse` to merge with base roof
- **Export for 3D printing** — Select object, File → Export → STL
- **Export for laser cutting** — File → Export → DXF/SVG (requires flattening)

## Troubleshooting

### "ERROR: Could not import shingle_geometry.py"
- Make sure `shingle_geometry.py` is in the same directory as the macro
- Check that both files are in your FreeCAD Macro directory

### "ERROR: No faces selected!"
- Select specific faces by Ctrl+clicking on roof surfaces
- Don't just select the object; select the face(s)

### "ERROR: Invalid parameters"
- Check that shingle dimensions make sense:
  - width > 0
  - height > 0
  - thickness > 0
  - exposure > 0
  - exposure ≤ height
  - thickness ≤ height

### "Warning: Face is not planar"
- Your face is twisted or warped
- For complex roof geometry, break it into smaller planar faces
- Or extrude your wall sketch into a planar roof face

### Macro runs but produces no shingles
- Check the Console output for error messages
- Verify face is actually selected (check 3D view feedback)
- Try with a simple rectangular face first to test

### Boolean operations are slow
- That's normal for hundreds of shingles being fused
- Progress prints every 50 shingles
- Large roofs can take 1-2 minutes depending on your computer

## Design Notes

### Geometry Strategy
- **Row 0** (bottom course): Rectangular prism, thickness = materialThickness
- **Rows 1+** (upper courses): Triangular wedge profile
  - Tapers from full thickness at bottom to thin at top
  - Creates realistic 3D appearance when lit

### Batch Fusion
Shingles are fused in batches of 10 to avoid massive memory overhead. Batches are then fused together. This balances speed and memory usage.

### Trimming
A "collar" approach cuts away excess shingles beyond the face boundary:
1. Creates a picture-frame border around the face
2. Extrudes it through the shingles
3. Cuts away the overhang

## Version History

### v4.0.0 (Current)
- Extract geometry logic to `shingle_geometry.py` (pure Python, no FreeCAD)
- Face-based selection (match clapboard v5.2.0 pattern)
- Comprehensive parameter and face validation
- Improved error messages
- 55 automated tests in `test_shingle_geometry.py`

### v3.6.3 (Previous)
- All geometry logic inline in macro
- Object-based workflow (select whole roof)
- Limited validation

## Development

### Running Tests
```bash
cd ~/Library/Application\ Support/FreeCAD/Macro/
python -m pytest test_shingle_geometry.py -v
```

All 55 tests pass in ~0.11 seconds without requiring FreeCAD.

### Adding New Features
1. Add pure Python function to `shingle_geometry.py`
2. Add test cases to `test_shingle_geometry.py`
3. Run tests to validate
4. Update `shingle_generator_v4.FCMacro` to use new function
5. Test in FreeCAD

## Performance Expectations

On an M4 Max with typical parameters:
- Face validation: < 1 second
- Shingle generation: < 1 second per 200 shingles
- Fusing: 30-60 seconds for 500+ shingles
- Trimming: 10-30 seconds
- **Total: 1-3 minutes for a typical roof**

## Future Improvements

Planned:
- [ ] Optimize fusion algorithm (spatial hashing?)
- [ ] Add different shingle profiles (flat, curved, beveled)
- [ ] Support for hip/gable roofs (non-rectangular)
- [ ] Texture mapping for realistic appearance
- [ ] Parametric integration (update shingles when roof changes)
- [ ] Reduce default parameters to realistic HO scale
- [ ] Export to STL with proper orientation for 3D printing

## Support

Issues or questions:
1. Check the Troubleshooting section above
2. Check the Console output (View → Panels → Python console)
3. Verify `shingle_geometry.py` is in the same directory
4. Try with a simple test face first
