# Photogrammetry-Based FreeCAD Geometry Generation
## Design & Handoff Document

**Project**: Automated measurement and modeling of prototype railroad structures (footers, bridges, buildings) from multi-image photogrammetry

**Status**: Phase 1 (Backend proof of concept) — Handoff point: manual VIA annotation

**Date**: December 5, 2025

---

## 1. Problem Statement

Currently, extracting precise structural dimensions from prototype photographs for HO-scale model generation is tedious manual work:
- Measure pixel positions in Lightroom manually
- Calculate scale factors by hand
- Convert to real-world dimensions
- Repeat for multiple images

**Goal**: Automate this measurement pipeline to accelerate the design-to-FreeCAD workflow while leveraging existing tools (Lightroom, VIA, exiftool, Python).

---

## 2. Proof-of-Concept: Bridge Footer Analysis

### 2.1 Test Case

**Images**: Two Nikon Z9 photographs of C&O railroad bridge footer structure
- `_BLW3129.jpg` (original NEF: `_BLW3129.nef`)
- `_BLW3138.jpg` (original NEF: `_BLW3138.nef`)

**Extracted Metadata**:

| Metric | Image 1 | Image 2 |
|--------|---------|---------|
| Focal Length | 200mm | 270mm |
| Focus Distance | 23.8m | 12.8m |
| Camera | Nikon Z9 | Nikon Z9 |
| GPS | Present | Present |
| Native Resolution | 8256 × 5504 px | 8256 × 5504 px |

### 2.2 Scale Factors (at native resolution)

Using Z9 sensor specs (36mm × 24mm, pixel pitch ≈ 0.004363mm):

**Image 1** (200mm @ 23.8m):
- Angular FOV: ~5.7°
- Ground sample distance: **1 pixel ≈ 0.52mm** in real world

**Image 2** (270mm @ 12.8m):
- Angular FOV: ~4.3°
- Ground sample distance: **1 pixel ≈ 0.21mm** in real world

These scale factors enable direct pixel-to-dimension conversion once triangulation is complete.

---

## 3. Technical Architecture

### 3.1 Workflow Phases

#### **Phase 1: Backend Proof of Concept (CURRENT)**

**Objective**: Validate the measurement pipeline with manual annotation

**Steps**:
1. ✅ Extract EXIF from NEF files (GPS, focal length, focus distance)
2. ⏳ **Manual annotation in VIA**: Click key features in cropped NEF regions
3. ⏳ **Triangulation solver** (Python script, runs locally on M4 Max)
4. ⏳ **3D output validation**: Verify dimensions match expectations

**Handoff Point**: After VIA annotation, developer provides CSV/JSON with:
```
image_name, feature_label, pixel_x, pixel_y, focal_length, focus_distance, gps_lat, gps_lon, gps_alt
```

#### **Phase 2: FreeCAD Geometry Generation**

**Objective**: Validate that 3D coordinates → FreeCAD sketch/geometry works reliably via MCP

**Steps**:
1. Process 3D coordinates from Phase 1 triangulation
2. Create FreeCAD sketch with points, circles (rivets), lines (edges, braces)
3. Use Part/Draft operations for additional geometry as needed
4. User manually selects/combines elements from object tree

**Output**: FreeCAD document with parametric sketch ready for further modeling

#### **Phase 3: Lightroom Plugin Integration**

**Objective**: Encapsulate the workflow in a Lightroom Classic plugin for production use

**Steps**:
1. Write Lua plugin to batch-process selected images from Lightroom
2. Auto-extract EXIF via exiftool
3. Launch VIA for user annotation
4. Collect annotations → generate standardized "wad" (JSON bundle)
5. Pass wad to Claude conversation for FreeCAD generation

**Note**: Lua syntax to be researched and implemented in Phase 3

---

### 3.2 Triangulation Solver (Phase 1)

**Input**:
- Metadata per image: GPS (lat, lon, alt), focal length, focus distance, sensor specs
- Annotated points from VIA: image name, feature label, pixel coordinates

**Math**:
For each image:
1. Convert GPS to local XYZ (choose first image as origin, or world coords)
2. Convert focal length + sensor specs → angular field of view
3. Convert pixel coordinates → angular offset from image center
4. Construct 3D ray from camera position through feature point

For each labeled feature appearing in multiple images:
1. Find 3D point that minimizes error across all rays
2. (Optional: use focus distance as constraint—feature lies at distance D from camera)

**Output**:
- CSV/JSON with 3D coordinates: `feature_label, x_mm, y_mm, z_mm`
- (Coordinate system: local XYZ relative to first image; axes chosen for FreeCAD convenience)

---

## 4. Key Design Decisions

### 4.1 Why Manual Annotation Instead of Auto Feature Detection?

- Reduces scope: avoids complex computer vision pipeline
- User retains control: decides which features matter for the model
- Faster iteration: minimal friction between image and FreeCAD
- Trades off: requires user interaction (acceptable for proof of concept)

### 4.2 Why VIA?

- Browser-based: no installation overhead
- Simple output format: JSON with pixel coordinates per image
- Supports multi-image annotation with feature correspondence tracking
- Lightweight and free

### 4.3 Coordinate System

- Origin: chosen for FreeCAD convenience (e.g., bottom-left of footer plate in local XYZ)
- Units: millimeters (matches model railroad scale expectations)
- Basis: first image as reference; other images triangulated relative to it

### 4.4 Perspective Distortion Tolerance

- Assumption: features lie approximately on a plane perpendicular to camera axis
- Tolerance: reasonable for architectural/structural details when cropped tightly
- Fallback: multiple images + triangulation self-corrects for moderate tilt/perspective

---

## 5. Validation Criteria

**Phase 1 output should pass**:
- ✓ Rivet spacing matches prototype photographic measurements (within ~0.5mm)
- ✓ Plate depth proportions align with visual inspection
- ✓ X-brace geometry (arm width, diagonal angles) matches structure
- ✓ Multiple-image triangulation shows consistency (same feature measured from 2+ views agrees)

---

## 6. Next Steps

### Immediate (Next Session)

1. **Manual annotation in VIA**:
   - Open cropped footer regions from both NEFs in VIA
   - Annotate key points:
     - Rivet centers (label: `rivet_1`, `rivet_2`, etc.)
     - Plate corners/edges (label: `plate_top_left`, `plate_bottom_right`, etc.)
     - X-brace endpoints (label: `brace_arm_left_top`, etc.)
   - Export VIA JSON

2. **Provide annotation data**:
   - Paste VIA JSON output into next conversation
   - Include list of which NEF files correspond to each annotated image

3. **Receive triangulation script**:
   - Claude provides Python script (EXIF extraction + triangulation)
   - Developer runs locally: `python3 triangulate.py --metadata exif.csv --annotations via_output.json --output footer_3d.csv`

### After Phase 1 Validation

4. **FreeCAD sketch generation** via MCP
5. **Iterate** on coordinate system/origin point as needed
6. **Plan Phase 3** (Lightroom plugin architecture)

---

## 7. Constraints & Assumptions

- ✅ Z9 metadata reliable: GPS present on 98% of images; focus distance recorded in MakerNote
- ✅ Multiple images (usually 2–6) available for feature triangulation
- ✓ Perspective distortion: manageable when features cropped tightly and roughly perpendicular
- ⚠ VIA output format: assumed JSON with `image_name: { features: { label: {x, y} } }`
- ⚠ Local coordinate system: will be refined after first triangulation output

---

## 8. References & Tools

**External**:
- VIA (Visual Geometry Group Image Annotator): http://www.robots.ox.ac.uk/~vgg/software/via/
- exiftool: https://exiftool.org
- Z9 EXIF specification: Nikon MakerNote includes focus distance (AF Distance)

**Local Environment**:
- Mac Studio M4 Max, 128GB RAM
- Python 3.x (numpy, scipy for triangulation math)
- FreeCAD (via MCP for sketch generation)

---

## 9. Open Questions / Future Refinement

1. **Coordinate system origin**: Should (0,0,0) be at bottom-left of plate, or center of footer? (Decide after first output)
2. **Thin geometry generation**: Once sketch is created, should follow same "skin" approach as brick_generator/clapboard_generator?
3. **Multiple footers/structures**: Can this scale to batches of 5–10 structures in one shoot? (Deferred to Phase 2)
4. **Metric precision**: What tolerance is acceptable for HO-scale modeling? (±0.5mm? ±1.0mm?)

---

**Document Version**: 1.0  
**Last Updated**: December 5, 2025  
**Next Review**: After Phase 1 completion (VIA annotation + triangulation validation)
