# CNC Turnout Manufacturing System - Ideas & Development Plan

## Project Overview

**Goal:** Use Genmitsu 4030 ProVerXL2 CNC router to automate precision machining of handlaid turnout components, particularly rail filing operations that currently take ~2 hours per turnout by hand.

**Philosophy:** "Even if the CNC time equals my manual time, it's not MY time" - automation wins!

**Timeline:** CNC arrives this week, development over coming months

**Scope:** ~70 turnouts total for COVA layout, batch in groups of ~5

---

## Current State (Baseline)

### What You Already Have Working

**Laser-Cut Components:**
- Wooden ties (cut from FreeCAD designs)
- Complete PDF templates for layout
- Proven workflow: FreeCAD → Laser → Physical parts

**Hand-Filing System:**
- Fast Tracks PointForm jigs (Code 70-109)
- Fast Tracks StockAid jigs (Medium 70-83)
- Fast Tracks assembly jigs (#6 frog shown in photo)
- ~2 hours per turnout currently

**Materials:**
- Code 83 nickel silver rail (18" lengths)
- PC board ties (for electrical isolation)
- #6 frog geometry (9.5° frog angle)

**Existing Skills:**
- FreeCAD parametric modeling ✓
- Laser cutting workflow ✓
- Hand filing/soldering ✓
- CNC: Zero experience (learning curve ahead)

---

## Hardware: Genmitsu 4030 ProVerXL2

### Specifications
- Work area: ~400mm × 300mm × 130mm (adequate for rail work)
- Stock spindle: Adequate to start
- Planned upgrade: DeWalt router (~1.5 HP, overkill but nice to have)
- 4th axis rotary: Available (future applications)

### Tooling Requirements

**Immediate Needs:**
- 1/16" (1.6mm) end mills - detail work on rail profiles
- 1mm end mills - very fine detail if needed
- 1/8" end mills - roughing/jig making
- V-bits (30° or 60°) - engraving PC board ties

**Later:**
- Engraving bits - fine marking
- Ball end mills - if doing curved surfaces
- Specialty cutters - TBD based on needs

**Tool life considerations:**
- Nickel silver can work-harden
- Sharp tools + light cuts = longer life
- Plan to stock consumables

### Workholding Strategy
- Design custom jigs for rail holding
- T-track or threaded inserts in spoilboard
- Cam clamps or screw clamps for rail
- Batch capability: 5 rails per setup ideal

---

## Development Phases

### Phase 0: CNC Learning (Weeks 1-4)

**Goal:** Get comfortable with machine, learn basics

**Simple Projects:**
1. Spoilboard surfacing
2. T-track installation in bed
3. Simple 2D pockets in wood
4. Basic engraving text/lines
5. First metal cuts (aluminum scrap)

**Skills to develop:**
- CAM workflow (FreeCAD Path workbench)
- G-code generation and posting
- Machine zeroing and work offsets
- Feed/speed calculations
- Tool changes
- Emergency stop reflexes!

**Resources:**
- Genmitsu documentation
- YouTube: Basic CNC tutorials
- Test materials: Scrap wood, aluminum, soft metals

### Phase 1: Jig Development (Weeks 5-8)

**Goal:** Design and cut jigs to hold rails for machining

**Jig 1: Point Rail Holder**
```
Design in FreeCAD:
- Cradle for Code 83 rail profile
- Clamps to hold rail secure
- Registration features for repeatable positioning
- Mounts to CNC bed via T-track or screws
- Batch capacity: 5 rails minimum
```

**Features to include:**
- Precise rail profile cutout (0.083" × rail base width)
- Overhang clearance for tool access
- Quick-release clamping
- Visual alignment marks
- Material: MDF, phenolic, or aluminum

**Design process:**
1. Measure Fast Tracks jigs carefully
2. Model in FreeCAD with parameters
3. Generate toolpaths (2.5D pocketing)
4. Cut from MDF for first prototype
5. Test fit with actual rail
6. Iterate as needed
7. Final version in more durable material

**Jig 2: Stock Rail Holder**
```
Similar to Jig 1 but:
- Straight rail (no curve issues)
- Position for notch cutting
- May be simpler than point rail jig
```

**Jig 3: PC Board Tie Engraving Fixture (Optional)**
```
- Holds PC board flat
- Registration for consistent spacing
- Quick swap for batch engraving
```

### Phase 2: Point Rail Machining (Weeks 9-12)

**Goal:** Machine point rail tapers on CNC

**What needs to happen:**
1. Point rail must be filed to thin taper
2. Taper starts ~1.5-2" from point end
3. Taper reduces rail height by ~50%
4. Must mate with stock rail at closure
5. Critical: must fit Fast Tracks assembly jig

**Current manual process:**
- Clamp in PointForm jig
- File by hand following jig profile
- Check fit frequently
- ~30-45 minutes per point rail

**CNC approach:**

**Step 1: Measure and model**
- Get exact point rail taper profile from PointForm jig
- Model as 3D sweep or loft in FreeCAD
- Account for rail already having some taper

**Step 2: CAM strategy**
- Roughing pass: 1/8" end mill, remove bulk
- Finishing pass: 1/16" end mill, final profile
- Light depth of cut: 0.010" per pass
- Conservative feeds: ~300mm/min to start

**Step 3: Material removal**
- Top of rail filed to taper
- Sides may need attention too
- Bottom usually untouched

**Step 4: Tool clearance**
- Rail held in jig
- Tool must clear jig walls
- May need to split into multiple setups

**Challenges:**
1. **Pre-bent rails:** Points need curve before machining
   - Solution: Bend by hand first, then machine
   - Or: Design curved holding jig
   - Or: Machine straight, bend after (risky)

2. **Work holding thin rail:** Nickel silver is springy
   - Need firm clamping without deforming
   - Multiple clamp points along length

3. **Chip evacuation:** Long chips can scratch
   - Air blast essential
   - Consider coolant/lubrication

**Test procedure:**
1. Use scrap Code 83 rail first
2. Machine one point rail
3. Test fit in Fast Tracks assembly jig
4. Measure with calipers/gauge
5. Iterate feeds/speeds/depth
6. Document successful parameters

### Phase 3: Stock Rail Machining (Weeks 13-16)

**Goal:** Machine notches in stock rails for point closure

**What needs to happen:**
1. Stock rail gets notch cut in inside face
2. Notch allows point rail to nestle against it
3. Notch depth ~0.040-0.060"
4. Notch length ~2"
5. Must maintain proper gauge

**Current manual process:**
- Clamp in StockAid jig
- File notch following guide
- Check gauge frequently
- ~20-30 minutes per stock rail

**CNC approach:**

**Step 1: Profile definition**
- Notch is essentially a pocket
- Rectangular with radiused corners
- Depth controlled precisely

**Step 2: CAM strategy**
- Simple 2.5D pocket operation
- 1/8" or 1/16" end mill
- Multiple depth passes
- Leave corner radius = tool radius

**Step 3: Advantages over manual**
- Perfect repeatability
- Exact depth every time
- Both rails identical (critical!)
- Faster than filing

**Test procedure:**
1. Scrap rail first
2. Measure notch dimensions
3. Test point rail fit
4. Check gauge with assembly jig
5. Document parameters

### Phase 4: PC Board Tie Engraving (Weeks 17-18)

**Goal:** Engrave alignment marks, centerlines, spike holes on PC board ties

**What needs to happen:**
1. PC board ties need precise markings
2. Tie spacing critical near frog
3. Centerlines for rail alignment
4. Possibly pilot marks for holes

**Current manual process:**
- Mark by hand or use printed template
- Accuracy issues near frog
- Time-consuming for precision

**CNC approach:**

**Advantages:**
- Perfect accuracy
- Consistent across all ties
- Can include complex markings
- Very fast operation (engraving is quick)

**Step 1: Layout generation**
- FreeCAD parametric tie spacing
- Account for frog geometry
- Export tie positions
- Generate engraving paths

**Step 2: CAM strategy**
- V-bit engraving (30° or 60°)
- Very shallow depth: 0.010-0.020"
- High feed rates possible
- Group all ties in one setup

**Step 3: Batch process**
- Fixture holds multiple PC boards
- Quick registration system
- Engrave 10-20 ties per setup

### Phase 5: Integration & Refinement (Weeks 19-24)

**Goal:** Complete turnout workflow, optimize, document

**Full workflow:**
```
For batch of 5 turnouts:

1. Cut wooden ties on laser (existing workflow)
2. Prepare PC board ties (already have or cut)
3. Engrave PC board ties on CNC (all 5 turnouts worth)
4. Prepare rail stock (cut to length, initial bending)
5. CNC machine point rails (10 pieces)
6. CNC machine stock rails (10 pieces)
7. Hand assembly using Fast Tracks jigs
8. Solder joints
9. Test electrical continuity
10. Install on layout
```

**Time estimate (per batch of 5):**
- Setup time: 1 hour
- CNC run time: 3-4 hours (unattended)
- Hand assembly: 2-3 hours (all 5 turnouts)
- **Total human time: ~4 hours for 5 turnouts**
- **vs. Current: ~10 hours for 5 turnouts**

**Optimization targets:**
- Reduce setup time with better jigs
- Increase batch size if confident
- Optimize feeds/speeds for time
- Document "recipes" for repeatability

---

## FreeCAD Parametric System

### Turnout Generator Design

**Input Parameters:**
```python
frog_number = 6  # or 7, 8, etc.
rail_code = 83
hand = "right"  # or "left"
length_available = 400  # mm
tie_spacing_tangent = 7.0  # mm
tie_spacing_frog = 3.5  # mm (tighter near frog)
```

**Generated Outputs:**

1. **Point Rail Profile**
   - Taper geometry (sweep along curve)
   - Bending template for pre-forming
   - CNC toolpath for filing

2. **Stock Rail Profile**
   - Notch position and depth
   - CNC toolpath for pocketing

3. **Frog Geometry**
   - Wing rails
   - Guard rails
   - Frog casting integration

4. **Tie Layout**
   - PC board tie positions
   - Wooden tie positions
   - Engraving marks for alignment

5. **Assembly Verification**
   - Check fit in Fast Tracks jig
   - Gauge verification
   - Clearance checks

6. **Documentation**
   - Cut list
   - Assembly sequence
   - G-code files
   - Setup sheets

### FreeCAD Workflow

**Step 1: Geometry Definition**
```
Spreadsheet:
- All parameters in one place
- Driven by frog number
- Rail code dependent dimensions

Sketches:
- Track centerline geometry
- Point rail taper profile
- Stock rail notch profile

Parts:
- Rail sweeps
- Jigs
- Fixtures
```

**Step 2: Path Workbench**
```
Jobs:
- Point rail machining
- Stock rail machining  
- PC board engraving
- Jig manufacturing

Operations:
- Pockets
- Profiles
- Engravings
- Finishing passes

Post-processor:
- Genmitsu-compatible G-code
- Tool change handling
- Safe heights
```

**Step 3: Export & Execute**
```
- G-code to CNC controller
- Setup sheets to print
- Part drawings if needed
```

---

## Technical Details

### Material Properties: Code 83 Nickel Silver

**Composition:** Copper-nickel-zinc alloy
**Hardness:** Softer than steel, harder than brass
**Machinability:** Good, but can work-harden

**Cutting Parameters (starting points):**

| Operation | Tool | RPM | Feed (mm/min) | DOC (mm) |
|-----------|------|-----|---------------|----------|
| Roughing | 1/8" end mill | 18,000 | 300 | 0.25 |
| Finishing | 1/16" end mill | 20,000 | 200 | 0.15 |
| Engraving | 60° V-bit | 15,000 | 400 | 0.05 |

**Notes:**
- Start conservative, increase if successful
- Sharp tools essential
- Air blast for chip clearing
- Light oil/WD-40 if needed

**Tool life:**
- Carbide preferred for nickel silver
- HSS acceptable for light duty
- Replace before dull (work hardening)

### Lubrication Strategy

**Dry cutting (preferred to start):**
- Air blast for chip evacuation
- Keep work area clean
- Less messy

**Wet cutting (if needed):**
- WD-40 as light lubricant
- Cutting oil for heavy cuts
- Flood coolant probably overkill

**When to add lubricant:**
- Tool showing wear quickly
- Chips welding to tool
- Poor surface finish
- Squealing sounds

### Dimensional Tolerances

**Critical dimensions:**
- Rail gauge: ±0.005" (0.127mm)
- Point taper profile: ±0.010" (0.25mm)
- Stock rail notch depth: ±0.005" (0.127mm)
- Tie spacing near frog: ±0.020" (0.5mm)

**Achievable with CNC:**
- Position accuracy: ±0.001" (0.025mm)
- Repeatability: ±0.0005" (0.013mm)
- Surface finish: Good with sharp tools

**Conclusion:** CNC is overkill for your tolerances (in a good way!)

---

## Risk Mitigation

### Potential Problems & Solutions

**Problem 1: Rails too thin/fragile after machining**
- Solution: Test on scrap first
- Solution: Adjust taper depth if needed
- Solution: Support rail fully during cutting

**Problem 2: Work holding fails, rail moves**
- Solution: Multiple clamp points
- Solution: Adhesive backing (carpet tape)
- Solution: Mechanical stops/keys

**Problem 3: Tool breaks during cut**
- Solution: Conservative speeds/feeds initially
- Solution: Climb vs. conventional milling tests
- Solution: Keep spare tools

**Problem 4: Part doesn't fit Fast Tracks jig**
- Solution: Careful measurement before cutting
- Solution: Test cuts on scrap
- Solution: Iterate design

**Problem 5: CNC learning curve frustration**
- Solution: Phase 0 simple projects first
- Solution: Online resources/community
- Solution: No pressure - learning is OK!

**Problem 6: Curved point rails hard to hold**
- Solution: Machine straight, bend after
- Solution: Custom curved jig
- Solution: Segmented approach

---

## Future Enhancements (Post-MVP)

### Once Core System Working

**Enhancement 1: Frog Manufacturing**
- CNC mill frog from solid brass/nickel silver
- Requires 3D profiling capability
- Would eliminate commercial frog castings
- Advanced project!

**Enhancement 2: Guard Rail Automation**
- CNC cut guard rail profiles
- Integrate into turnout generation

**Enhancement 3: Switch Machine Mounts**
- CNC cut custom mounting brackets
- Integrate with tie spacing

**Enhancement 4: Turnout Library**
- Database of common prototype turnouts
- C&O specific geometries
- One-click generation

**Enhancement 5: Track Planning Integration**
- Export from track planning software
- Generate complete trackwork
- Mass production mode

**Enhancement 6: 4th Axis Applications**
- Rotate rails for multi-face machining?
- Complex curved parts?
- Future investigation

**Enhancement 7: Quality Control Jigs**
- CNC-made gauge checking tools
- Go/no-go fixtures
- Automatic verification

---

## Documentation & Knowledge Management

### What to Document

**For each successful operation:**
1. Tool used (make, size, flutes)
2. Feeds and speeds that worked
3. Depth of cut
4. Any issues encountered
5. Surface finish quality
6. Time per piece
7. Photos of setup
8. Photos of results

**FreeCAD files:**
- Version control (git)
- Parametric models saved
- G-code archived with source
- Setup sheets generated

**Physical records:**
- Test pieces labeled and saved
- First article inspection data
- Failed attempts (learn from)

### Repository Structure

```
~/Projects/COVA/turnouts/cnc/
├── freecad/
│   ├── jigs/
│   │   ├── point_rail_holder_v1.FCStd
│   │   ├── stock_rail_holder_v1.FCStd
│   │   └── pcb_tie_fixture_v1.FCStd
│   ├── turnouts/
│   │   ├── number_6_template.FCStd
│   │   ├── number_7_template.FCStd
│   │   └── params.FCStd (spreadsheet)
│   └── tests/
├── gcode/
│   ├── point_rails/
│   ├── stock_rails/
│   ├── engraving/
│   └── jigs/
├── docs/
│   ├── setup_sheets/
│   ├── test_results/
│   ├── feeds_speeds_database.md
│   └── lessons_learned.md
├── photos/
└── README.md (this file)
```

---

## Success Metrics

### How to know it's working

**Phase 0 (Learning):**
- ✓ Comfortable with machine operation
- ✓ Successful 2D cuts in wood
- ✓ Successful test cuts in aluminum
- ✓ No crashes or damage

**Phase 1 (Jigs):**
- ✓ Rail fits securely in jig
- ✓ Repeatable positioning
- ✓ Can swap rails quickly
- ✓ Jig doesn't interfere with tool

**Phase 2 (Point Rails):**
- ✓ Point rail fits in Fast Tracks jig
- ✓ Profile matches hand-filed parts
- ✓ Gauge correct
- ✓ Time competitive with hand filing

**Phase 3 (Stock Rails):**
- ✓ Notch correct depth
- ✓ Point rail fits in notch
- ✓ Gauge correct
- ✓ Both rails identical

**Phase 4 (Engraving):**
- ✓ Marks visible and accurate
- ✓ Tie spacing correct near frog
- ✓ Time faster than manual marking

**Phase 5 (Full Workflow):**
- ✓ Complete turnout assembles correctly
- ✓ Electrical continuity good
- ✓ Trains run through smoothly
- ✓ Total time less than manual
- ✓ Quality equal or better than manual

### Ultimate Success

**Definition:** "I can load 10 pieces of rail into jigs, press start, walk away, come back to perfectly machined parts that assemble into working turnouts."

**Bonus:** "The setup takes less time than filing one point rail by hand."

---

## Questions for Future Research

### Technical Questions

1. What's the minimum practical depth of cut in nickel silver?
2. How many rails can one carbide end mill machine before dulling?
3. Can I machine curved rails, or must they be straight?
4. What's the best jig material - MDF, phenolic, aluminum?
5. Is air blast sufficient or is coolant needed?
6. Can I do roughing and finishing in one setup?

### Design Questions

1. Should point rails be bent before or after machining?
2. Can I do both sides of a rail without flipping?
3. Should I batch by operation or by turnout?
4. What's the optimal number of rails per jig?
5. How to handle left vs. right hand turnouts?

### Workflow Questions

1. Where does CNC fit in overall turnout assembly?
2. Should I stockpile machined parts or work just-in-time?
3. How to quality-check without manual fitting every piece?
4. Can any operations be parallelized?

### Process Questions

1. What's the learning curve really like?
2. How much iteration before success?
3. Should I expect failures? How many?
4. When to give up and go back to manual?

---

## Resources & References

### Fast Tracks (Current System)
- Fast-Tracks.net
- Assembly jig documentation
- Filing jig profiles
- Online community/forums

### CNC Learning
- Genmitsu support documentation
- YouTube: CNC basics
- Fusion 360 CAM tutorials (transferable concepts)
- FreeCAD Path Workbench documentation

### Model Railroad
- NMRA standards (gauge, clearances)
- Turnout geometry calculations
- Prototype references (C&O drawings)

### Machining Reference
- Feeds and speeds calculators
- Nickel silver properties
- Tool selection guides
- Workholding techniques

---

## Timeline Summary

**Week 0:** CNC arrives, unbox, assemble, initial setup

**Weeks 1-4:** Phase 0 - Learning basics on simple projects

**Weeks 5-8:** Phase 1 - Design and cut jigs

**Weeks 9-12:** Phase 2 - Point rail machining development

**Weeks 13-16:** Phase 3 - Stock rail machining development

**Weeks 17-18:** Phase 4 - PC board tie engraving

**Weeks 19-24:** Phase 5 - Integration, optimization, documentation

**Week 25+:** Production mode - Making turnouts for layout!

**Total development time:** ~6 months part-time

**Note:** This is GENEROUS timeline. You may progress faster. No pressure!

---

## Closing Thoughts

### Philosophy

This is a learning journey, not a race. The goal is:
1. Learn CNC machining
2. Improve turnout quality
3. Free up your time
4. Have fun!

Every failure is data. Every iteration is progress.

### The Big Win

Even if CNC time equals manual time, **it's not your time**. You can:
- Solder other turnouts while CNC runs
- Work on other layout tasks
- Do scenery
- Take photos
- Drink coffee and watch the machine work!

### Automation Philosophy

"Anything worth doing is worth overdoing" - Your motto applies here!

Build infrastructure once, reap benefits for all 70 turnouts.

The first turnout will take longest. The 70th will be trivial.

---

## Next Actions

**Before CNC arrives:**
- ✓ Read this document (you're doing it!)
- ☐ Measure Fast Tracks jigs carefully
- ☐ Photograph current process steps
- ☐ Organize workspace for CNC
- ☐ Order initial tooling (end mills, V-bits)

**When CNC arrives:**
- ☐ Assembly and setup
- ☐ Surfacing spoilboard
- ☐ First test cuts
- ☐ Begin Phase 0 learning projects

**This week:**
- ☐ Test clapboard generator v5.4.0
- ☐ Test brick generator v3.1.0
- ☐ Get comfortable with bay boundaries
- ☐ Prepare for CNC arrival

**Future sessions:**
- ☐ Design first jig in FreeCAD
- ☐ Generate test toolpaths
- ☐ Document Fast Tracks jig dimensions
- ☐ Create FreeCAD turnout template

---

**Document Version:** 1.0
**Date:** 2024-12-02
**Status:** Planning - CNC arriving this week
**Next Review:** After Phase 0 completion

---

*"The difference between good engineering and great engineering is documentation."*

*"Measure twice, cut once. But with CNC, cut once, repeat forever."*
