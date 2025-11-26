# Ashlar Stone Generator Concept

## Overview
A new parametric FreeCAD generator for creating large, irregular ashlar masonry (like bridge piers and building foundations) with natural surface variation and weathering detail. This will be a separate generator (`ashlar_generator.py`) alongside existing brick and clapboard generators.

## Motivation
Ashlar masonry is a "killer detail"—when present, it's a real attention-getter in model railroad photography. Examples include:
- Bridge pier near Woolen Mills (roughly 18-24" stones in real world)
- Richmond Main Street Station ground-level facade (even larger stones with up to 14" surface variation)

These details are worth the computational investment because they're photographed at close range following O. Winston Link's approach.

## Technical Approach

### Core Concept
Rather than generating complex lofted surfaces for each stone, decompose each stone into a **brick-scale grid with randomized vertices and elevation displacement**:

1. Define overall stone boundaries (roughly rectangular courses—the stones naturally organize in regular rows)
2. Within each stone, generate a **randomized grid** of intersection points:
   - X-spacing varies (not uniform)—use Poisson or similar non-normal distribution for natural clustering
   - Y-spacing also varies
   - Optionally add skew/shear so grid isn't perfectly orthogonal
3. Assign each grid intersection a random Z elevation (displacement) to create surface undulation
4. Loft/patch the surface between displaced vertices to create the weathered stone face
5. Vertical faces (edges between stones) remain relatively planar—they're just structural boundaries

### Computational Complexity
- Order of magnitude similar to brick generation
- Fewer total geometry pieces than brick (fewer stones, but each more complex)
- Reuses proven machinery: vertex displacement, patching/lofting, boolean fusion
- Estimated CPU cost: ~1 hour for complex scenes is acceptable given the visual payoff

## Parametrization

Expected inputs:
- Wall sketch defining overall outline
- Stone course heights
- Average stone width/height (for Poisson distribution)
- Displacement range (controls surface roughness)
- Random seed (reproducible generation)
- Possibly: multiple scales of variation (fine weathering + larger erosion features)

## Design Principles

**Constraint-driven:** The "brick grid" overlay isn't a limitation—it's a deliberate constraint that keeps the solution tractable while still producing natural-looking results. You're not inventing new computational approaches; you're extending what already works.

**Geometry enables weathering:** The parametric generator creates geometric surface complexity (undulations, erosion pits, joint depth variation). Post-processing weathering techniques (rust streaking, lichen patterns, differential patina) then work with this geometry, making the final result look authentic and lived-in. The elevation map is the geometric foundation; your painting skills provide the character.

**Resin printing limitation:** The resin printer produces whatever color resin you pour (Henry Ford color scheme). This is fine—geometric detail and surface variation are what matters. Character comes from post-printing weathering and paint techniques.

## Integration with Existing Infrastructure

- Separate generator file: `ashlar_generator.py`
- Uses existing Skeleton template pattern with parametrized inputs
- Semantic versioning (v1.0.0 at release)
- Comprehensive test suite with pytest (same approach as clapboard/brick)
- Metadata properties for tracking
- GitHub/Gitea version control

## Timeline

**Way down the line.** Current priorities are finishing clapboard 5.1.0 testing infrastructure, smart_trim development, and other generators. But the concept is solid and ready for the hopper.

## Reference Examples

- **Bridge pier near Woolen Mills:** Stones roughly 18-24" in real world (~0.2-0.28" HO scale), relatively uniform course heights, clear rectangular organization
- **Richmond Main Street Station:** Much larger ground-level stones with dramatic weathering (up to 4mm variation in HO scale), organic irregular coursing
- **Upper facades:** May require separate parametrization or generator variant for smaller, more refined ashlar

## Next Steps (When Ready)

1. Prototype Poisson distribution grid generation
2. Implement displacement sampling and surface lofting
3. Build test suite with reference geometry validation
4. Create multiple parameter sets for different stone types/sizes
5. Document integration with Skeleton template workflow
