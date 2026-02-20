# Terrain & Scenery Substrate Generator Specification

**Version**: 0.1.0 (Draft)  
**Date**: February 2026  
**Author**: Brian  
**Status**: Design Phase

---

## 1. Executive Summary

A parametric, prompt-driven mesh generator that creates geologically-plausible scenery substrates for HO scale model railroad layouts. The generator accepts dimensional constraints, geological parameters, and reference imagery, producing CNC-ready mesh geometry that serves as the foundation for detailed scenery work.

The system is designed for **hybrid workflows**: direct prototype extraction for iconic structures (tunnels, trestles) combined with procedurally-generated terrain that maintains geological realism at HO scale compression ratios.

---

## 2. Problem Statement

### 2.1 Hand-Sculpting Limitations

Model railroading scenery at HO scale presents a fundamental challenge: convincing terrain compression. Hand-carved scenery often looks either:
- **Too smooth and uniform** (lack of time/tools creates unrealistic surfaces)
- **Incorrectly proportioned** (jointing angles, weathering patterns that violate geology at scale)
- **Time-intensive** (hours of carving for features that could be generated in minutes)

### 2.2 Current Workflow Pain Points

- No systematic way to incorporate prototype geology into HO scale models
- Difficult to iterate on scenery designs before committing to CNC cuts
- Tedious manual mesh creation for complex terrain features
- Limited ability to ensure natural-looking compressed landscapes
- No integration with reference photography for geometry extraction

### 2.3 Opportunity

Modern CNC equipment (router, laser cutter) and procedural mesh generation enable a new approach: **procedurally-generated substrates that encode geological realism and allow artistic refinement on top**.

---

## 3. System Overview

### 3.1 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  User Input Layer                                               │
│  ├─ Prompt/Constraint Description                               │
│  ├─ Dimensional Parameters (width, height, depth)               │
│  ├─ Reference Photography (optional)                            │
│  └─ Geological/Feature Specifications                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│  Python Terrain Generation Engine                               │
│  ├─ Constraint Parser (interprets prompt/parameters)            │
│  ├─ Procedural Geometry Library                                 │
│  │  ├─ Base shape generation                                    │
│  │  ├─ Noise/displacement functions                             │
│  │  ├─ Jointing pattern generation                              │
│  │  └─ Feature insertion (undercuts, caves, etc.)               │
│  ├─ Mesh Validation & Optimization                              │
│  └─ Output Serialization (STL/OBJ)                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│  FreeCAD Integration Layer                                      │
│  ├─ Mesh Import & Validation                                    │
│  ├─ Tool Path Preparation                                       │
│  ├─ CNC Configuration                                           │
│  └─ Output to CAM Software                                      │
└────────────────┬────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────┐
│  Output                                                         │
│  ├─ CNC-Ready Geometry (G-code or CAM import)                   │
│  ├─ Painted/Detailed Substrate (post-processing)                │
│  └─ Integrated Layout Assembly                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Execution Flow

1. **User describes requirement** (prompt + dimensional constraints)
2. **Generator validates inputs** (dimensional feasibility, CNC constraints)
3. **Generate base mesh** (procedurally, using noise + constraints)
4. **Validate & optimize** (mesh quality, no impossible geometries, CNC-safe)
5. **Export to file** (STL or OBJ)
6. **Import to FreeCAD** (via Mesh workbench)
7. **Prepare for CNC** (add registration features, validate tool paths)
8. **Export to CAM** (G-code or CAM software import)

---

## 4. Use Cases

### 4.1 Primary Use Cases

#### UC1: Coal Operation Hillside
**Scenario**: Model a C&O coal trestle and loading facility. The hillside needs to look geologically plausible and accommodate the trestle's structural footprint.

**Input**:
- Footprint: 12" × 18"
- Trestle base elevation: 2"
- Peak elevation: 8"
- Rock type: Sandstone (60° jointing dominant angle)
- Reference: COHS photograph of similar facility
- Material: XPS foam, 2" thick

**Output**: Mesh substrate with natural slope, jointing pattern, and trestle foundation area. User paints on weathering and vegetation.

#### UC2: Riverbank Feature
**Scenario**: Model a Virginia creek with undercut banks and vegetation transition zones.

**Input**:
- Feature type: Riverbank
- Width: 12"
- Height: 8"
- Left side: Undercut bank (reeds zone)
- Right side: Slope up 2:1 to grass line at 10"
- Material: Mudstone/shale jointing
- Reference: On-site photography with dimensional markup

**Output**: Mesh with natural undercut erosion, jointing, and slope transitions. User adds vegetation, water, weathering.

#### UC3: Tunnel Portal Surround
**Scenario**: Hybrid approach: tunnel portal is extracted from reference photos/documentation, surrounding hillside is procedurally generated to integrate naturally.

**Input**:
- Tunnel model: Hand-modeled or extracted from reference
- Surround footprint: 18" × 12"
- Integration constraint: Portal sits at specific elevation
- Rock type: Similar to tunnel (ensures visual continuity)
- Reference: COHS tunnel photo + dimensional annotation

**Output**: Hillside substrate with portal interface points. User assembles portal + surround, paints as integrated feature.

#### UC4: Modular Layout Expansion
**Scenario**: Generate interconnected scenic sections that expand the layout without visible seams.

**Input**:
- Section grid: 12" × 12" modules (e.g., 3×3 grid = 36" × 36" total)
- Feature theme: Mixed hillside/valley
- Connector strategy: Matching edge geometry for seamless assembly
- Geological continuity: Same rock type, jointing angle across sections

**Output**: Multiple meshes with registered edges for modular assembly. Consistent geological character across the entire expansion.

---

## 5. Functional Requirements

### 5.1 Input Specification

#### 5.1.1 Constraint Definition
The system accepts constraints in two forms:

**A. Structured Parameters**
```
terrain_spec = {
    "feature_type": "hillside" | "riverbank" | "cliff" | "valley" | "coal_operation",
    "dimensions": {
        "width_inches": float,           # HO scale (actual layout dimensions)
        "length_inches": float,          # (Y direction)
        "height_inches": float,          # Maximum relief
        "material_depth_inches": float   # Thickness for CNC
    },
    "geometry": {
        "base_elevation": float,         # Lowest point (reference: 0)
        "peak_elevation": float,         # Highest point
        "slope_angle_dominant": float,   # Degrees, primary slope direction
        "slope_angle_variance": float    # +/- degrees for natural variation
    },
    "geology": {
        "rock_type": "granite" | "sandstone" | "shale" | "limestone" | "schist",
        "jointing_angle_primary": float, # Dominant joint orientation (degrees)
        "jointing_angle_secondary": float,  # Secondary joint set (if applicable)
        "jointing_spacing": float,       # Inches between visible joints
        "jointing_spacing_variance": float,  # Natural variation
        "weathering_intensity": 0.0-1.0,    # 0=fresh, 1=heavily weathered
        "erosion_features": ["undercut_banks", "cave_mouth", "drainage_lines"] # Optional
    },
    "vegetation_zones": [
        {
            "zone_name": "grass_slope",
            "elevation_range": [0, 4],
            "side": "all" | "left" | "right",
            "description": "Gentle slope with grass"
        },
        # ... additional zones
    ],
    "reference_photos": [
        {
            "path": "/path/to/photo.jpg",
            "type": "prototype" | "reference_only",
            "annotations": {
                "jointing_angles": [45, 60],
                "slope_profile": "marked",
                "vegetation_zones": "marked"
            }
        }
    ],
    "cad_model": {
        "type": "trestle" | "portal" | "structure",
        "path": "/path/to/model.FCStd",
        "placement": {
            "elevation": float,
            "orientation": float  # Degrees
        }
    },
    "material": "xps_foam" | "mdf" | "plywood" | "rigid_plastic",
    "cnc_constraints": {
        "max_tool_diameter": float,      # Inches
        "max_depth_per_pass": float,
        "surface_finish": "rough" | "detail"  # Controls engraving detail
    },
    "resolution": float,                 # Grid spacing in inches (default 0.05)
    "seed": int | null                   # Random seed for reproducible output
}
```

**B. Prompt-Based Input** (natural language)
```
"Coal operation hillside. 12" × 18" footprint. Trestle base at 2" height, 
rise naturally to 8" at back. Sandstone jointing (60° dominant). 
Reference: COHS-45503. Generate substrate that looks like active 
C&O coal facility, 1920-1944 era."
```

The system parses the prompt to extract parameters, uses reference photos for guidance, and applies domain knowledge about C&O operations.

#### 5.1.2 Reference Photography Integration
Optional but recommended: provide reference images with annotations.

**Extraction from Photos**:

*Phase 1-2: Manual annotation approach*
- User marks jointing angles/spacing on printed photo or in image editor
- Slope profiles drawn by hand on printout, measured with protractor
- System reads annotated values as structured parameters
- No automatic image analysis — user provides the geological interpretation

*Phase 3+: Assisted extraction (future)*
- Jointing angle/spacing (image analysis or manual markup)
- Slope profiles (sketch lines on printout → digitize)
- Weathering patterns (texture sampling)
- Vegetation zones (region identification)
- Scale reference (object of known size in frame)

**Usage in Generator**:
- Informs geological parameters
- Provides weathering texture hints
- Ensures regional/geological consistency
- Supplies color reference for painting guidance (Lightroom export)

#### 5.1.3 CAD Model Integration
If modeling around an existing structure (trestle, portal):

- Provide FreeCAD file or STL of the structure
- Specify placement (elevation, orientation, offset)
- Generator creates substrate that naturally integrates (edges, foundations, overhanging rock)

### 5.2 Processing Requirements

#### 5.2.1 Constraint Validation
Before mesh generation:
- Dimensional feasibility (width/height/depth reasonable for CNC)
- Geological realism (jointing angles don't violate physics)
- CNC feasibility (no impossible undercuts, tool access verified)
- Material compatibility (depth achievable in selected material)

**Action on Validation Failure**:
- Return detailed error message with suggested corrections
- Example: "Maximum jointing angle for 2" foam depth is ~65°. Your specification requests 85°. Reduce angle or increase material depth."

#### 5.2.2 Procedural Mesh Generation

**Core Algorithm**:

1. **Base Shape**: Create initial surface based on feature type
   - Hillside: sloped plane with variance
   - Riverbank: S-curve profile with undercut
   - Valley: U-shaped or V-shaped base
   - Cliff: vertical + overhang

2. **Noise Displacement**: Apply multi-scale noise
   - Perlin noise for broad topographic variation
   - Fractal Brownian motion for natural irregularity
   - Scaled to preserve dominant geological features (jointing angles, slope direction)

3. **Jointing Pattern**: Overlay geometric jointing
   - Primary and secondary joint sets (if applicable)
   - Angle, spacing, and variance per geology specification
   - Joint depth (surface detail vs. through-cut)

4. **Feature Insertion**: Add specific geological features
   - Undercut erosion (riverbank, cave mouth)
   - Drainage lines (water erosion patterns)
   - Natural platform features (benches, ledges)

5. **Vegetation Zone Constraints**: Mark regions for future artistry
   - Surface normal adjustments for vegetation placement
   - Optional: subtle surface detail cues (micro-texturing)

6. **Mesh Optimization**:
   - Reduce polygon count while preserving feature fidelity
   - Adaptive density: fine resolution near jointing lines (~0.01"), coarser elsewhere
   - Ensure manifold topology (no hanging edges, correct normals)
   - Verify no self-intersections or impossible geometries

#### 5.2.3 CNC Safety Checks
Before output:
- Verify no tool collisions (undercut depth achievable)
- Check that tool can access all surfaces
- Validate edge geometry (no sharp inside corners if rough cutting)
- Confirm material thickness accommodates design depth

#### 5.2.4 Scale Compression Handling

The generator actively encodes HO scale (1:87.1) geological realism:
- Jointing angles and spacing adjusted for visibility at scale
- Weathering depth parameterized for visual impact
- Surface feature scale calibrated to 1:87 human eye perspective
- Vegetation zone heights map to proto-scale expectations

Example: Real jointing spacing might be 6-18 feet; in HO scale that's 0.8-2.5 inches. Generator maintains this proportion while ensuring CNC cutability.

### 5.3 Output Specification

#### 5.3.1 Primary Output: Mesh File
**Format**: STL (ASCII or Binary) or OBJ
- **Precision**: 0.001" (sufficient for CNC accuracy)
- **Topology**: Manifold mesh, consistent face normals
- **Scale**: Output in inches (layout dimensions)
- **Origin**: (0, 0, 0) at one corner of footprint, Z+ up

**Metadata** (embedded in file comments or sidecar file):
```
{
  "generator_version": "0.1.0",
  "geometry_spec": { ... },  # Full input specification
  "generation_timestamp": "2026-02-18T14:30:00Z",
  "mesh_stats": {
    "vertex_count": 12480,
    "face_count": 6240,
    "bounding_box": [12.0, 18.0, 2.0],
    "surface_area_sqin": 425.3
  },
  "cad_integration": {
    "freecad_import_notes": "Import via Mesh workbench...",
    "cnc_notes": "Tool access verified for 0.25\" endmill..."
  }
}
```

#### 5.3.2 FreeCAD Integration
- Mesh imported into Mesh workbench
- Automatic material thickness validation
- Registration feature addition (mounting points, alignment keys)
- Tool path visualization (if CAM workbench available)

#### 5.3.3 CNC Output
- G-code generation (via CAM software or FreeCAD CAM workbench)
- Material-specific tool path (feed rate, spindle speed adjusted for foam/MDF/etc.)
- Optional: two-pass strategy (rough + detail finishing)

#### 5.3.4 Documentation Output
- Generation report (parameters used, validation results)
- Painting guide (geology-informed color suggestions, vegetation zones)
- Assembly notes (how to integrate with structures, terrain seams)
- Reference photo overlay (painted substrate against prototype)

---

## 6. Technical Architecture

### 6.1 Python Terrain Engine

**Location**: `/Volumes/Files/claude/freecad-mcp/terrain_generator/`

**Core Modules**:

```
terrain_generator/
├── __init__.py
├── terrain_generator.py          # Main entry point
├── geometry/
│   ├── __init__.py
│   ├── base_shapes.py             # Hillside, riverbank, cliff, etc.
│   ├── noise_functions.py         # Perlin, Voronoi, etc.
│   ├── jointing.py                # Joint pattern generation
│   ├── erosion.py                 # Undercuts, drainage, caves
│   └── mesh_utils.py              # Validation, optimization, export
├── constraints/
│   ├── __init__.py
│   ├── parser.py                  # Parse prompt + structured input
│   ├── validator.py               # Feasibility checks
│   └── geology_knowledge.py       # Rock type properties, jointing logic
├── io/
│   ├── __init__.py
│   ├── input_handler.py           # Prompt, params, photos
│   ├── photo_analyzer.py          # Extract geometry from reference photos
│   └── mesh_export.py             # STL, OBJ, metadata
├── tests/
│   ├── test_base_shapes.py
│   ├── test_jointing.py
│   ├── test_integration.py
│   └── test_geometry_validation.py
└── examples/
    ├── coal_trestle.py            # UC1 example
    ├── riverbank.py               # UC2 example
    └── tunnel_surround.py         # UC3 example
```

**Dependencies**:
- `numpy`: Numerical computation
- `scipy`: Advanced signal processing (noise generation)
- `trimesh`: Mesh manipulation, validation, export
- `Pillow`: Reference photo handling
- `opencv-python`: Optional, for advanced photo analysis (jointing angle extraction)

### 6.2 FreeCAD Integration

**Method 1: MCP Integration (Implemented)**
- `terrain_operations` MCP tool exposed via `AICopilot/handlers/terrain_ops.py`
- Operations: `generate_terrain`, `generate_preview`, `validate_params`, `list_rock_types`, `list_materials`
- Generates mesh → imports to FreeCAD → optional solid conversion for CAM
- Real-time parameter adjustment via Claude

**Method 2: Mesh Workbench (Manual Fallback)**
- Import STL/OBJ via Mesh workbench
- Manual validation
- Export to CAM software

**Registration/Mounting**:
- Auto-detect CAD model bounding box
- Create registration features (alignment dowels, mounting pads)
- Add interface geometry for terrain seaming

### 6.3 Data Flow: Prompt to CNC

```
Prompt: "Coal operation hillside..."
    ↓
Parser extracts: feature_type, dimensions, rock_type, etc.
    ↓
Photo analyzer (if provided): jointing angles, weathering level
    ↓
Constraint validator: checks feasibility
    ↓
Mesh generator: creates 3D geometry
    ↓
Mesh optimizer: reduces polygons, validates topology
    ↓
CNC feasibility check: undercuts, tool access
    ↓
Export to STL + metadata JSON
    ↓
User imports STL to FreeCAD
    ↓
FreeCAD: validate, add registration features
    ↓
Export to CAM software
    ↓
Generate G-code
    ↓
CNC execution
```

---

## 7. Implementation Phases

### Phase 1: MVP (Proof of Concept)
**Goal**: Demonstrate viability with a single feature type

**Deliverables**:
- Python library: Basic hillside generation (simple slope + noise)
- Jointing overlay (single angle, uniform spacing)
- STL export
- One test case: coal trestle hillside (UC1)

**Scope**:
- Structured parameter input only (no prompt parsing yet)
- Manual validation of outputs
- Simple mesh (thousands of faces, not optimized)

**Effort**: ~2-3 weeks

**Success Criteria**:
- Generated mesh can be CNC cut in foam
- Result looks geologically plausible
- User can iterate on parameters and regenerate

### Phase 2: Robustness & Multi-Feature
**Goal**: Expand to multiple feature types, add validation & optimization

**Deliverables**:
- Additional feature types (riverbank, valley, cliff)
- Constraint validation & error handling
- Mesh optimization (polygon reduction, normal smoothing)
- Photo analyzer: extract jointing angles, slope profiles
- Comprehensive test suite (55+ tests)

**Scope**:
- Still structured parameter input
- Photo analysis for geometry hints
- CNC feasibility checks
- Documentation and examples for UC2, UC3

**Effort**: ~3-4 weeks

**Success Criteria**:
- Multiple feature types tested in actual CNC cuts
- Generated meshes demonstrate geological variety
- Photo analysis provides useful constraints

### Phase 3: Prompt Interface & Refinement
**Goal**: Implement natural language prompt parsing, add workflow polish

**Deliverables**:
- Prompt parser (extract parameters from natural language)
- Interactive FreeCAD MCP integration (optional real-time preview)
- Painting guide generation (geology → color suggestions)
- Assembly/integration guide (how to compose terrain pieces)
- Gallery of examples

**Scope**:
- Prompt + photo → full mesh generation
- Domain knowledge encoded (C&O geology, vegetation zones, era-specific features)
- User-friendly error messages
- Export templates for painting reference

**Effort**: ~3-4 weeks

**Success Criteria**:
- User can describe terrain in natural language
- System reliably produces usable meshes
- Generated terrain integrates seamlessly with structures
- Painting guidance accelerates finishing work

### Phase 4: Advanced Features (Optional)
**Goal**: Expand capability and integration

**Potential Features**:
- Modular terrain with seamless edge matching
- Erosion simulation (water flow, differential weathering)
- Multi-material substrates (foam base + MDF detail layer)
- CAM software direct integration (avoid FreeCAD step)
- Library of parametric templates (common C&O features)

---

## 8. Testing Strategy

### 8.1 Unit Tests
- **Geometry**: Base shapes, noise functions, jointing patterns
- **Constraints**: Validation logic, parameter parsing
- **Mesh**: Manifold verification, normal calculation, optimization
- **I/O**: Photo analysis, export format correctness

**Target**: 55+ tests, organized by module

### 8.2 Integration Tests
- **End-to-end**: Prompt/params → STL → FreeCAD → CNC feasibility
- **Feature scenarios**: UC1, UC2, UC3 (actual use cases)
- **Real CNC tests**: Generated mesh → physical foam/MDF cut

### 8.3 Validation
- **Visual inspection**: Generated geometry matches intent
- **Geological plausibility**: Jointing/weathering realistic for compression
- **CNC feasibility**: Tool paths executable, no collisions
- **Aesthetic**: Result looks "right" in context of layout

---

## 9. Deliverables & Documentation

### 9.1 Code
- Python library (semantic versioning, deployment scripts)
- FreeCAD integration (Mesh workbench workflow documented)
- Example scripts (coal trestle, riverbank, tunnel surround)
- Test suite with CI/CD

### 9.2 Documentation
- **User Guide**: Prompt syntax, parameter reference, photo markup guide
- **Geologist's Guide**: Rock types, jointing patterns, weathering levels (HO scale context)
- **CNC Integration**: Material-specific settings, tool path optimization
- **Examples & Gallery**: Completed projects with before/after

### 9.3 Deployment
- Git repository with semantic versioning
- Automated installer script (Python dependencies, FreeCAD integration)
- Backup: Git + BackBlaze

---

## 10. Known Constraints & Assumptions

### 10.1 CNC Equipment
- **Router**: Genmitsu 4030 ProVerXL2 (constraints: tool access, depth limits)
- **4th Axis**: Optional rotary attachment available for undercut machining
  - Requires mesh splitting to fit within rotary axis parameters
  - Enables true undercuts (cave mouths, overhanging banks) via multi-setup
- **Materials**: XPS foam (primary), MDF, plywood (secondary)
- **Precision**: 0.01" typical, 0.001" achievable

### 10.2 Scale & Compression
- **Scale**: HO (1:87.1)
- **Compression factor**: ~1:2 typical (e.g., 40' cliff becomes 0.5" of visual relief)
- **Geological realism** at compression requires procedural approach (hand-carving fails)

### 10.3 Layout Integration
- **Modular approach**: Terrain fits on ~12" × 12-18" sections
- **Structures**: Trestle, portal, etc., provided separately (hand-modeled or extracted)
- **Finishing**: User responsible for painting, vegetation, weathering detail

### 10.4 Geology & Reference
- **Region**: Primarily Virginia C&O operations (1918-1944)
- **Rock types**: Sandstone, shale, limestone dominant; granite secondary
- **Reference material**: COHS archives, on-site photography, geological surveys

### 10.5 Not Included (Out of Scope)
- Direct CAM software integration (G-code generation) — handled separately
- Water feature modeling (rivers, streams, water surface) — separate system
- Vegetation modeling (trees, shrubs, grasses) — hand-placement on substrate
- Track/ballast integration — substrate is foundation only

---

## 11. Success Criteria

### 11.1 MVP Success
1. Generated coal trestle hillside substrate can be CNC cut in XPS foam
2. Result looks geologically plausible (jointing, weathering, slope)
3. User can iterate on 2-3 parameters and regenerate in < 2 minutes
4. Painted/finished result integrates convincingly with trestle model

### 11.2 Phase 2 Success
1. Multiple feature types (hillside, riverbank, cliff) demonstrated
2. Photo analysis successfully extracts 2-3 key parameters
3. Test suite at 55+ tests, all passing
4. Generated meshes in UC1-UC3 scenarios all physically cuttable

### 11.3 Phase 3 Success
1. User can describe terrain in natural language, system parses intent
2. Painting guide (colors, weathering patterns) derived from geology
3. Modular terrain sections integrate seamlessly (no visible seams)
4. Gallery demonstrates 3-5 completed scenic sections on layout

---

## 12. Future Directions

### 12.1 Machine Learning / Image Analysis
- Train model on C&O photos to extract geometry automatically
- Texture synthesis from prototype photos

### 12.2 Erosion Simulation
- Model water flow across terrain
- Predict realistic weathering patterns
- Simulate cave mouth formation

### 12.3 Multi-Material Layering
- Foam base + MDF detail layer for fine features
- Different material selection per elevation zone

### 12.4 Terrain Library
- Pre-parameterized common C&O features (coal operations, river curves, hillsides)
- Versioned templates with proven results

### 12.5 Layout Integration
- CAD layout file (benchwork dimensions, track positions) → auto-fit terrain to available space
- Conflict detection (terrain vs. structures)

---

## 13. References & Context

### 13.1 Related Work
- **Ashlar/Brick/Clapboard/Shingle Generators**: Precedent for parametric structure generation in FreeCAD
- **FreeCAD Mesh Workbench**: Native mesh import/manipulation capability
- **Procedural Terrain in Game Engines**: Perlin noise, Voronoi, erosion simulation (academic foundation)
- **Model Railroading Scenery References**: Tony Komlósi, Alex Stein, et al.

### 13.2 Key Publications
- "Procedural Modeling of Buildings" (Parish & Müller): Procedural generation principles
- "Fast Hydraulic Erosion Simulation and Visualization on GPU" (Mei et al.): Erosion algorithms
- "Terrains from Features" (Smelik et al.): Constraint-based terrain generation

### 13.3 COHS Resources
- COHS photo archive: 45503, 45523, and others documenting C&O Virginia operations
- Prototype documentation: Coal facilities, trestle designs, track configurations

---

## Appendix A: Prompt Examples

### Example 1: Coal Trestle Hillside
```
"Coal operation hillside. 12" × 18" footprint. Trestle base at 2" 
elevation, rise naturally to 8" at rear. Sandstone jointing with 
60° dominant angle. Reference photo provided (COHS-45503). Generate 
substrate for Chesapeake & Ohio coal facility, 1920-1944 era. 
Material: XPS foam, 2" thick."
```

### Example 2: Riverbank
```
"Riverbank, 12" wide, 8" tall. Left side: undercut bank with reed 
vegetation zone. Right side: 2:1 slope up to 10" grass line. 
Mudstone/shale jointing. Reference: on-site photo with profile lines 
marked. Material: foam or MDF."
```

### Example 3: Modular Expansion
```
"Generate 3×3 grid of 12" × 12" scenic sections. Mixed hillside/valley 
theme. Consistent rock type (sandstone, 60° jointing) across all 
sections. Connector strategy: matching edge geometry for seamless assembly. 
Total footprint: 36" × 36". Material: XPS foam."
```

---

## Appendix B: Geology Quick Reference (HO Scale)

| Rock Type | Primary Jointing | Typical Angle | Spacing (proto → HO) | Weathering Character | C&O Locations |
|-----------|------------------|---------------|----------------------|----------------------|---------------|
| Sandstone | Bedding + vertical | 45-75° | 6-18 ft → 0.8-2.5" | Flaking, differential erosion | Ridgetops, quarries |
| Shale | Thin bedding | 30-60° | 0.5-3 ft → 0.1-0.5" | Spalling, slope failures | River valleys, hillsides |
| Limestone | Vertical grid | 60-90° | 3-10 ft → 0.4-1.4" | Solution weathering, caves | Passages, gorges |
| Granite | Orthogonal | 70-90° | 10-30 ft → 1.4-4.2" | Rounding, corestones | Less common in C&O region |

---

## Appendix C: CNC Feasibility Matrix

| Feature | Material | Max Depth | Tool Dia | Achievable | Notes |
|---------|----------|-----------|----------|-----------|-------|
| Jointing lines | XPS foam | 0.5" | 1/16" | ✓ | Engraving pass |
| Undercut bank | XPS foam | 2" | 0.25" | ✓ | Requires careful tool path |
| Slope, 45° | MDF | 3" | 0.25" | ✓ | Two passes (rough + finish) |
| Deep cave | MDF | 6" | 0.5" | ✗ | Exceeds 4030 Z travel safely |
| Fine texture | XPS | 0.25" | 1/16" | ✓ | Detail pass, slower feed |

---

**End of Specification Document**
