# FreeCAD Dependency Analysis Project

## Context
This project emerged from frustration with FreeCAD's recompute behavior on large parametric models. Even semantically-irrelevant changes (like cell formatting) trigger full model recalculation cascades, severely impacting workflow on sophisticated designs. The core idea: build dependency tracking analogous to Rete pattern matching to enable smart, selective recomputation.

## Core Problem Statement
When a FreeCAD model becomes large and complex (particularly those driven by spreadsheet parameters and sketch dependencies), any modification—even one with no semantic impact on model geometry—triggers a cascading recalculation through the entire dependency chain. This creates a usability wall for serious parametric work.

**Specific use case:** Changing a spreadsheet cell from plain to bold formatting should not recompute the entire model, yet currently it does.

## Project Scope: Three Nested Levels

### Level 1: Spreadsheet Dependency Analysis (Entry Point)
**Focus:** Cell → Parameter → Sketch Constraint → Feature propagation

**Questions to answer:**
- How does FreeCAD currently track which cells' *values* affect which parameters?
- Does FC expose its dependency graph, or is it implicit in the recompute engine?
- Can we distinguish between changes that affect model geometry vs. cosmetic changes?
- What would be required to build an overlay dependency tracker (Rete-like) that FC could use?

**Why start here:**
- More constrained than sketch analysis (simpler pipeline)
- Still exposes the fundamental dependency infrastructure
- Might be tractable as a self-contained solution

### Level 2: Sketch Internal Dependencies
**Focus:** Constraints within sketches, sketch-to-feature relationships

**Expected complexity:** Higher than spreadsheet level due to tighter coupling and internal constraint interdependencies

**Hypothesis:** Fully understanding sketch dependencies might require solving spreadsheet dependencies anyway (since sketches reference spreadsheet cells), but spreadsheet analysis might be solvable independently

### Level 3: Full Model Dependency Graph
**Focus:** Cross-sketch references, feature interdependencies, recursive parameter chains

**Status:** Deferred pending findings from Levels 1-2

## Technical Approach

### Preliminary Analysis (Claude Code Session)
**Goal:** Map the actual complexity before committing to full implementation

**Strategy:**
1. **Shape mapping** (low token cost): Read generator scripts, Skeleton.FCStd structure, representative generators
2. **Chokepoint identification**: Trace where code actually interfaces with FC's spreadsheet/dependency engine
3. **Gap analysis**: Identify minimal set of FC source needed to understand mechanisms
4. **Decision point**: Is full FC source exploration necessary, or can API docs + usage patterns suffice?

**Key advantage:** Claude Code runs locally under user's process tree, eliminating web fetch restrictions that normally constrain exploration of large codebases

### Full Implementation (if feasible)
- Build Rete-like dependency tracker overlay
- Integrate with FC's recompute engine to enable selective recalculation
- Test against real parametric models (Brian's generator ecosystem)
- Potentially contribute back to FreeCAD community

## Why This Matters

### User Impact
- Eliminates recompute cascades from semantically-irrelevant changes
- Massively improves workflow on large parametric models
- Makes FreeCAD genuinely usable for sophisticated railroad structure modeling at scale

### Community Impact
- Solves a known pain point for *many* users doing complex parametric design
- "WHOPPER of a difference" for FreeCAD's professional usability tier
- Potential contribution to FreeCAD codebase itself

## Relationship to Model Railroading
While model railroading is Brian's lifetime passion, FreeCAD has become deeply embedded in that work (parametric generators for structures, laser cutting, 3D printing, CNC routing). FreeCAD's limitations directly constrain what's possible in the layout, making this a high-leverage area for investigation.

## Background Context
- Brian has deep experience with rule-based systems (CLIPS 4.3, Rete pattern matching)
- Extensive parametric generator ecosystem already built (shingle generator v4.0, clapboard generator, etc.)
- Access to advanced fabrication equipment (resin 3D printers, laser cutters, CNC router)
- Sufficient computational resources (M4 Max Studio, 128GB memory) for analysis and experimentation

## Next Steps
1. **Defer** until ready to commit to exploration
2. **Schedule Claude Code session** for preliminary analysis when appropriate
3. **Scope** actual implementation effort based on findings
4. **Decide** whether to pursue as a standalone utility or contribute to FreeCAD proper

## Notes
- This is NOT a lifetime passion project, but an instrumental one
- Timing depends on how deeply FreeCAD continues to embed itself in model railroad work
- The fact that serious investigation is *possible* (via Claude Code's local execution model) changes the calculus on whether to attempt it
