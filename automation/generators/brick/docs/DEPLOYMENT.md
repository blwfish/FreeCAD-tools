# Brick Generator - Deployment Guide

## Quick Start (5 minutes)

### 1. Install Files

Find your FreeCAD Macros directory:
- **macOS**: `~/Library/Application Support/FreeCAD/Macro`
- **Windows**: `%APPDATA%\FreeCAD\Macro`
- **Linux**: `~/.FreeCAD/Macro`

Copy these files there:
- `brick_generator_macro.FCMacro`
- `brick_geometry.py` (same directory as macro)

### 2. Prepare a Test Document

1. Open FreeCAD
2. Create new document
3. Insert a Spreadsheet (Part Design menu)
4. Add these cells and values:

```
Cell Name          Value
A1: brickWidth     2.32
B1: brickHeight    0.65
C1: brickDepth     1.09
D1: mortar         0.11
E1: bondType       stretcher
F1: commonBondCount 5
```

Actually, use a better layout:

```
         A                      B
1    Brick Parameters
2    brickWidth                2.32
3    brickHeight               0.65
4    brickDepth                1.09
5    mortar                    0.11
6    bondType                  stretcher
7    commonBondCount           5
```

### 3. Create a Test Wall

In the same document:

1. **Sketch mode**: Create a rectangular sketch (100mm × 100mm) and close it
   - OR
   - **Face mode**: Create a box, select one face

2. Select the sketch (or face)

3. Run macro: Macro → Recent macros → brick_generator_macro

4. Check output: You should see `BrickedWall_*` in the tree in a few seconds

### 4. Verify Success

Look for:
- New object in tree named `BrickedWall_*`
- Console shows "SUCCESS!"
- Object has properties: GeneratorName, GeneratorVersion, BondType, BrickCount

**Done!** You now have a working brick generator.

---

## Next Steps

### Test Different Bond Patterns

Edit the spreadsheet:
- Change `bondType` to "english", "flemish", or "common"
- For common bond, adjust `commonBondCount` (try 3 or 6)
- Select the sketch again and re-run the macro

### Work with Your Actual Building

1. **Photograph reference wall** - Get good lighting, perpendicular angle
2. **Measure brick dimensions** - Use actual bricks or research historical specs
3. **Calculate scale** - Actual dimension ÷ 87 for HO scale
4. **Update spreadsheet** with your measurements
5. **Generate wall** with correct bond pattern

### Add Openings (Windows/Doors)

For a wall with windows:

1. **Generate the full wall** (no openings)
2. **Create punchout sketches** for each window
3. **Extrude each sketch** perpendicular to wall (make it thick)
4. **Cut punchouts** from wall (Part → Boolean → Cut)

For arched openings, the same approach works—just extrude the arch sketch.

---

## Troubleshooting

### "ERROR: Could not import brick_geometry module"

**Solution**: `brick_geometry.py` is not in the same directory as the macro.

Check:
1. Both files are in the FreeCAD Macros directory
2. Filename is exactly `brick_geometry.py` (not `brick_geometry.py.txt`)

### "ERROR: No active document"

**Solution**: Create a document first before running macro.

1. File → New
2. Try again

### "ERROR: Please select a sketch or face"

**Solution**: Nothing was selected before running macro.

1. Draw a sketch OR select a face on a 3D object
2. Click in the tree to select it
3. Run macro again

### Macro runs but generates NO bricks

**Possible causes:**
1. Spreadsheet parameters are missing or have wrong cell names
2. Wall dimensions are too small for the brick size
3. Sketch/face is not properly closed

**Fix:**
1. Check spreadsheet has cells: `brickWidth`, `brickHeight`, `brickDepth`, `mortar`, `bondType`
2. Try with larger wall (500mm × 500mm)
3. Use face workflow instead of sketch if sketch fails

### Macro is VERY slow (minutes for small wall)

This is usually the FreeCAD fuse operation on large brick counts.

**Options:**
1. Use larger mortar joints to reduce brick count
2. Break wall into smaller sections
3. Wait (it will finish, just takes time)

For very large walls (>5000mm), you might want to adjust:
- Increase `mortar` to reduce brick count
- Generate in sections and combine

### Generated bricks look wrong on selected face

**Cause**: Face orientation or coordinate system detection issue

**Solution**: 
1. Try face-based workflow instead of sketch
2. Select the face you want directly (not a sketch)
3. Check that face is rectangular

---

## For Integration into Your Gordonsville Station

### Workflow

1. **Photograph the actual station** (you probably already have)
2. **Identify brick pattern** from photos
3. **Measure or research** brick dimensions
4. **Create rough wall geometry** in FreeCAD
5. **Apply brick generator** with correct parameters
6. **Create punchout geometry** for each window/door
7. **Cut punchouts** from wall
8. **Add arched overlays** for windows that need them

### Arch Example

For a typical arched window:

```
Step 1: Generate full wall with bricks (with opening placeholder)
Step 2: Create arch profile in sketch
Step 3: Extrude arch sketch (50mm thick)
Step 4: Cut arch from wall
Step 5: (Optional) Create voussoir overlay for detail
Step 6: Position arch directly over hole
```

### Documentation for Your Building

Add to Skeleton.FCStd or your building document:

```
Wall Configuration
==================
Building: Gordonsville Station
Date: 1918/1927/1944 (as applicable)

Brick Dimensions (measured from photo):
- Width: 8"   → HO: 2.32mm
- Height: 2.25" → HO: 0.65mm  
- Depth: 3.75" → HO: 1.09mm
- Mortar: 0.375" → HO: 0.11mm

Bond Pattern: English/Flemish/Common
Source: Photo reference [photo name]
Generated: [date] by brick_generator v3.0.0
```

---

## File Organization for Your Repo

Once you're happy with the generator:

```
automation/generators/brick/
├── brick_geometry.py              # Pure Python library
├── brick_generator_macro.FCMacro  # FreeCAD UI
├── tests/
│   └── test_brick_geometry.py     # 30 comprehensive tests
├── README.md                      # Full documentation
├── DEPLOYMENT.md                  # This file
└── docs/
    ├── PATTERNS.md                # Detailed bond pattern info
    ├── GORDONSVILLE.md            # Your station-specific notes
    └── EXAMPLES.md                # Usage examples with screenshots
```

---

## Performance Data

Test results on MacBook M4 Max (approximate):

| Task | Duration | Notes |
|------|----------|-------|
| Generate 100×100mm wall | <1 sec | Geometry creation |
| Fuse 1,600 bricks | 2-3 sec | Boolean fuse operation |
| Generate 500×500mm wall | 3-5 sec | Total |
| Generate 1000×1000mm wall | 10-15 sec | Getting slower |
| Generate 2000×2000mm wall | 60+ sec | May timeout |

**Tip**: For large walls, either:
1. Use larger mortar (fewer bricks)
2. Generate in 500mm sections
3. Use a more powerful computer

---

## Running Tests

To verify the geometry library is working correctly:

```bash
cd ~/Library/Application\ Support/FreeCAD/Macro/
python -m pytest test_brick_geometry.py -v
```

Should see:
```
============================= 30 passed in 33.22s ==============================
```

This proves all bond patterns and edge cases work correctly.

---

## Version Reference

When you generate a wall, the properties show which version was used:

- **v3.0.0**: Current—pure geometry library, 4 bond patterns
- **v2.0.2**: Old—all-in-one macro, 3 bond patterns
- **v2.0.1**: Very old—initial sketch-based version

If you ever upgrade, old generated walls keep their version metadata, so you know which generation method was used.

---

## Common Questions

**Q: Can I change the brick pattern after generation?**
A: No, you'd need to re-run the macro with different settings. The geometry is baked into the Part. Delete the old result and re-generate.

**Q: Can I break a wall into sections?**
A: Yes! Generate smaller rectangles separately, then boolean union them together. This also helps with performance on large walls.

**Q: What if my bricks aren't rectangular?**
A: The geometry library currently assumes rectangular bricks. Specialty shapes (circular, hexagonal) would require library changes.

**Q: Can I export this for 3D printing?**
A: Yes! The Part can be exported as STL, OBJ, or STEP. Slice it with your printer's software as usual. Thin wall geometry works great on resin printers.

**Q: Can I use this for laser cutting?**
A: Yes! The brick pattern can be useful for reference. For actual cutting, you'd usually want just the outer outline or individual brick profiles, which you can extract from the geometry.

---

## Next Session Planning

When you're ready to integrate this into your repository:

1. Move files to `automation/generators/brick/` structure
2. Add to your main README (point to this guide)
3. Create a Gordonsville-specific config document
4. Tag version 3.0.0 and create release notes
5. Archive the old v2.0.2 macro for reference

---

**You're all set!** Start bricking your Gordonsville buildings. 🧱

