# 3D Printing Pipeline Development Roadmap

## Overview
A systematic approach to streamlining 3D printing production for large model railroad structures (like Gordonsville station) that don't fit on the printer bed. This breaks the workflow into three distinct phases, each building on the previous one.

## Phase 1: Non-Destructive Chopping Tool

### Problem
Models that exceed printer bed dimensions (like Gordonsville station) require slicing. FreeCAD's built-in `slice_apart()` tool destructively modifies the original model, making it impossible to edit or re-slice with different parameters afterward.

### Solution
Create a macro/tool that:
- Clones the selected model (leaving original untouched)
- Slices the clone along user-defined planes
- Exports individual pieces as separate STL files
- Maintains the original for future edits or alternative slice configurations

### Implementation Details

**Cutting planes:** Defined as explicit objects in the FreeCAD model (using Part→Create Primitive→Plane). This makes them:
- Reproducible (same planes can be reused for multiple iterations)
- Persistent (documented as part of the model)
- Visible (you can see exactly where cuts will happen)

**Export workflow:** Each chopped piece exports as a separate STL with sensible naming for easy import into the slicer.

**Non-destructive:** The original model remains completely intact and parametric. You can edit it, generate new geometry, and re-chop at any time.

### Registration Studs

**Purpose:** Ensure chopped pieces can be reassembled accurately on the layout without requiring manual alignment or test-fitting.

**Specifications:**
- Diameter: 1mm (ship model convention, barely visible after painting)
- Depth: 1mm (defaults stored in Skeleton as `RegStudDiameter` and `RegStudDepth`)
- Design: One half of seam gets pins (raised cylinders), other half gets sockets (depressions)

**Placement system:**
- One stud placement sketch per cutting plane
- Sketch contains points marking exact stud locations
- Points can be parametrically positioned using Skeleton spreadsheet values
- Macro iterates through sketch points and creates cylinders/depressions on appropriate sides

**Sizing logic:** Smaller piece gets pins, larger piece gets sockets (minimizes support material needed during printing)

**Workflow:**
1. Create cutting plane as permanent model object
2. Create sketch on that plane with points marking stud locations
3. Run registration macro: iterates sketch points, creates studs
4. Run chopper macro: slices model, studs are included in exported pieces
5. Studs printed as part of geometry, enabling deterministic reassembly

---

## Phase 2: Print Preprocessing Pipeline

### Problem
Slicer auto-support generation is unreliable and generic. Manual support placement in the slicer is tedious. Orientation matters significantly for print success but lacks clear optimization rules.

### Solution
Create a preprocessing pipeline in FreeCAD that:
- Clones the model
- Orients it optimally for printing
- Generates custom supports and raft using your specific rules
- Exports the complete assembly (model + supports + raft) as a single STL
- Tells the slicer to print "this thing" as-is on the build plate (no modifications)

Once supports are included in the geometry, the slicer cannot second-guess your decisions.

### Key Insight
By generating supports *before* sending to the slicer, you:
- Enforce your specific support rules consistently
- Preview support placement before printing
- Avoid slicer's generic algorithms that don't understand your requirements
- Control quality across all prints

### Raft Design

**Pattern:** Perforated grid (like AnyCubic's standard raft)
- Reduces resin usage significantly
- Reduces weight
- Still provides mechanical strength to reliably lift model off FEP
- Grid holes designed for your standard models

**Support attachment:** Supports attach to raft (not directly to model), then model attaches to supports via ball joints (your standard approach).

**Mechanical requirements:** Support aggregate must be strong enough to peel the model off the FEP through 50-4000+ cycles depending on print height.

---

## Phase 3: Support Generation Rules

### Semantic Location Tagging
Supports are sized and placed based on whether they're in visible or hidden areas:

- **Hidden surfaces** (interior, back faces, etc.): Can use medium or large supports freely for structural support. High load-bearing capacity acceptable.
- **Visible surfaces** (architectural detail, windows, doors, etc.): Light supports only, positioned to minimize scarring.

### Feature-Specific Rules

**Windows and doors:**
- Medium supports at structural corners (connection to wall casing, high stress, usually hidden)
- Light supports along inside (hidden) edges of casing and trim
- **Critical:** NO supports on mullions (vertical/horizontal dividers)
  - At `params.materialThickness` (typically 1mm), mullions are too delicate
  - Support nubs and cleanup damage thin geometry
  - Instead: orient windows at angles where they don't need support, or use minimal point contact

**Thin walls (station clapboards, etc.):**
- Light supports, point contact preferred
- Orient to minimize peel force on thin geometry
- Avoid putting supports on delicate surface detail

**Structural geometry (piers, foundations, etc.):**
- Can use medium/large supports on interior faces
- More generous support density acceptable on hidden surfaces

### Orientation Optimization

**Challenge:** No single "magic angle" works for all geometries. Optimization factors include:

- **Peel force minimization** (primary metric)
- **Wall thickness variation** (thin walls behave differently than solid blocks)
- **Aspect ratio** (tall thin structures vs. blocky geometry)
- **Hollow vs. solid** (air trapped inside creates suction during peel)
- **Contact area** with FEP (larger contact = larger absolute force, but distributed)

**Current status:** Research needed. Industry sources don't agree on a universal formula because it depends heavily on specific model geometry and material characteristics.

**Approach:** Consult resin printing community research, then build a rule system or heuristic that captures what works for your common model types.

**Future enhancement:** As you print more pieces and gather data on which orientations work best for which geometry types, you can refine the orientation rules.

---

## Implementation Roadmap

### Now
- Continue working on test model (Charlottesville station or similar)
- Deploy clapboard generator 5.1.0 and testing infrastructure
- Iterate on shingle generator until it's production-ready

### Next: Phase 1 (Chopper Tool)
Once you have a complete model ready to print:
- Build the clone-and-chop macro
- Implement stud placement system
- Validate with actual test model (Gordonsville station or similar)
- Refine based on printing results

### After Phase 1: Phase 2 (Orientation & Support Generation)
- Research orientation optimization rules (peel force minimization literature)
- Build orientation selection logic
- Implement raft generation (perforated grid pattern)
- Build support generator with your specific rules
- Test with actual prints, gather feedback

### Ongoing: Phase 3 (Rule Refinement)
- Print pieces, evaluate support placement and orientation
- Iterate on rules based on real results
- Build up a library of "this geometry type + this orientation = good results"
- Refine material thickness awareness in support rules

---

## Design Philosophy

**Non-destructive workflow:** Preserve parametric models for iteration
**Systematic approach:** Encode your hard-won printing knowledge as reproducible rules
**Automation at the boundary:** FreeCAD handles geometry, slicer just slices

This is essentially **CI/CD for physical models**—a manufacturing pipeline that can scale from single prototypes to dozens of pieces flowing through consistently.

---

## Key Technical Decisions

- **Studs are 1mm:** Ship model convention, barely visible after painting, but effective for registration
- **Studs placed via sketch:** User-driven but parametric; clear visual feedback on placement
- **Supports pre-generated:** Removes slicer guesswork, ensures consistency
- **Raft pattern:** Grid design matches printer standard, reduces resin usage
- **Separate phases:** Each phase can be developed and tested independently

---

## Next Steps

1. Complete shingle generator and test model
2. Scope out chopper tool requirements in detail
3. Build chopper with registration stud system
4. Test on actual large model needing slicing
5. Once Phase 1 works reliably, begin Phase 2 research on orientation optimization
