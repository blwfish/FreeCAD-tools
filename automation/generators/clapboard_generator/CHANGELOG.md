# Clapboard Generator CHANGELOG

## v6.0.0 (2024-12-02)

### Added
- Global grid snapping for clapboard course alignment across all faces
- Single compound output from multiple selected faces
- Vertical position snapping to clapboard_height grid
- Automatic adjustment reporting shows grid snap distances

### Fixed
- **MAJOR**: Clapboard courses now align perfectly across coplanar faces
- Eliminates visible seams at face boundaries
- Courses maintain alignment even with multi-face selection

### Changed
- Multi-face workflow now creates ONE result object instead of multiple
- Output is single Part::Feature containing compound of all faces
- Simplified workflow: select faces, run macro, get one clean result
- Metadata includes all processed faces and parameters

### Technical Details
- `snap_to_global_grid()` function snaps each face's vertical starting position
- Grid spacing based on clapboard_height (reveal)
- Snapping rounds to nearest grid line in global vertical axis (Z or Y)
- Preserves per-face bay boundary detection
- All faces now share common clapboard course heights

### Why This Matters
When multiple faces are clad independently (e.g., arrayed bays), each face previously had its own starting position and generated clapboards from scratch. This caused misaligned courses at face boundaries - very noticeable with horizontal siding. Now all faces snap to a shared global grid, ensuring perfect alignment across the entire building.

### Compatibility
- Works with single and multi-face selection
- Compatible with bay boundary detection
- Compatible with gable edge detection
- Requires FreeCAD 1.0.x

## v5.4.0 (2024-12-01)

### Added
- Bay boundary detection for fused arrays with vertical gaps

### Fixed
- Clapboards now respect bay separations (fudgeFactor-sized gaps)

### Changed
- Segmented clapboard generation stops at detected boundaries

## v5.3.0

### Changed
- SourceObject now uses App::PropertyLink (TNP-safe object reference)
- Stores actual object reference instead of label string

## v5.2.0

### Changed
- Return skin-only geometry, use Part::Compound output

### Fixed
- Eliminate duplicate wall geometry in output

## v5.1.0

### Removed
- Trim logic (defer to smart_trim generator)
- trim_width and trim_thickness parameters

### Changed
- Fuse clapboards directly to source wall

## v5.0.1

### Added
- Sketch geometry validation - detect degenerate and duplicate edges

## v5.0.0

### Changed
- REWRITE - Face-based selection (not sketches)
