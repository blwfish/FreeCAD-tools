# Brick Bond Fiddling Architecture for Corner Clipping

## Overview

Corner clipping in brick patterns varies significantly in complexity depending on the bond type. This document describes the architectural approach for handling both simple patterns (Common, Stretcher) that require no fiddling, and complex patterns (Flemish, English) that require constraint-satisfaction solving before clipping can be applied.

## Pattern Categories

### No-Fiddling Case
- **Patterns**: Common Bond, Stretcher Bond
- **Characteristics**: Geometry is deterministic; corner clipping is orthogonal to pattern generation
- **Process**: Specify dimensions → Generate pattern → Apply clipping
- **Complexity**: Straightforward; clipping logic is independent of pattern rules

### Fiddling Case
- **Patterns**: Flemish Bond, English Bond
- **Characteristics**: Dimensions and sequences are interdependent; closing requires planning from the leading edge
- **Process**: Pre-fiddling → Constraint solving → Pattern generation → Post-fiddling → Clipping

## Fiddling Phase Architecture

The fiddling phase is a **constraint satisfaction problem** that must be solved *before* the pattern is generated. It is not simply about finding dimensions that work—it must determine the leading-edge configuration that permits a valid closing sequence at the trailing edge.

### Phase 1: Pre-Fiddling Analysis
- Validate input wall dimensions (width W, height H)
- Identify bond pattern rules and closure constraints
- Determine what leading-edge brick configurations are possible

### Phase 2: Constraint Solving
- **Goal**: Find a leading-edge configuration that allows the pattern to repeat/close such that valid closing bricks (quoins, headers, etc.) fit at the trailing edge
- **Input**: Target dimensions and bond rules
- **Output**: The leading-edge brick configuration (sequence, types, positions) that permits valid closure
- **Complexity**: Solution space varies by bond type; different patterns have different closure rules

### Phase 3: Pattern Generation
- With the leading-edge configuration determined, generate the full pattern
- The pattern is now constructed knowing how it must close

### Phase 4: Post-Fiddling (Trailing Edge Closure)
- Work backwards from the trailing edge
- Place closing bricks (quoins, headers, etc.) that fit the determined sequence
- Ensures the pattern closes properly given the leading-edge constraint

### Phase 5: Clipping
- Apply corner clipping to the resulting geometry
- Clipping logic is pattern-agnostic; it operates on a wall of known final dimensions
- Works identically for both fiddling and no-fiddling cases

## Key Insight: Subset Relationship

The no-fiddling case is a proper subset of the fiddling case, sandwiched between pre-fiddling and post-fiddling:

1. **Pre-fiddling**: Establish base parameters (both cases)
2. **Fiddling phase** (conditional): Constraint solving for complex bonds only
3. **Post-fiddling**: Apply pattern rules to generate geometry (both cases)
4. **Clipping**: Corner clipping, independent of bond type (both cases)

For no-fiddling patterns, the fiddling phase is null—you skip directly from pre-fiddling to post-fiddling.

## Next Steps

1. Define closure rules for each bond pattern (Flemish, English)
2. Specify the constraint-satisfaction algorithm for the fiddling phase
3. Document the leading-edge configuration space for each pattern
4. Implement the fiddling solver
5. Validate clipping logic with both fiddling and no-fiddling outputs
