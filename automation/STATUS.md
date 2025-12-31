# Automation Status Report

**Generated:** 2025-12-31
**Skeleton Version:** 1.0.0
**Scale:** HO (1:87)

## Utilities

| Utility | Version | Purpose |
|---------|---------|---------|
| lint_params.FCMacro | v1.2.0 | Validate parameters in models descended from Skeleton |

### lint_params.FCMacro
Validates spreadsheet parameters before export/printing. Checks:
- Scaled parameters smaller than `materialThickness` (highlights in orange)

Run on any model with a `params` spreadsheet to catch unprintable dimensions.

## Generator Inventory

| Generator | Version | Status | Tests | Architecture |
|-----------|---------|--------|-------|--------------|
| brick_generator | v4.0.0 | Production | 30 tests | geometry lib + macro |
| shingle | v4.0.0 | Production | 55 tests | geometry lib + macro |
| clapboard_generator | v6.0.0 | Production | Yes | geometry lib + macro |
| board_batten_generator | v1.0.0 | Production | Yes | geometry lib + macro |
| bead_board_generator | v1.0.0 | Production | Yes | geometry lib + macro |
| smart_trim | v1.2.0 | Production | Yes | geometry lib + macro |
| station_sign | v1.1.1 | Production | No | standalone macro |

## Skeleton.FCStd Parameters

Central parameter spreadsheet for all generators.

### Global Parameters
| Parameter | Alias | Value | Description |
|-----------|-------|-------|-------------|
| B3 | scale | 87 | Model scale (HO=87, N=160, O=48) |
| B4 | materialThickness | 0.2 mm | Thin relief for 3D printing/laser |

### Bead Board Parameters
| Parameter | Alias | Value | Description |
|-----------|-------|-------|-------------|
| B6 | beadSpacing | 101.6 mm | Spacing between bead centers |
| B7 | beadDepth | 0.2 mm | Gap extrusion depth |
| B8 | beadGap | 0.2 mm | Width of each gap |

### Clapboard Parameters
| Parameter | Alias | Value | Description |
|-----------|-------|-------|-------------|
| B62 | clapboard_height | 0.8 mm | Height of each course |
| B63 | clapboard_thickness | 0.2 mm | Material thickness |
| B64 | trim_width | 1.5 mm | Corner/edge trim width |
| B65 | trim_thickness | 0.2 mm | Trim material thickness |
| B66 | wall_thickness | 2 mm | Structural wall thickness |

### Shingle Parameters
| Parameter | Alias | Value | Description |
|-----------|-------|-------|-------------|
| B70 | shingleWidth | 3.5 mm | Width of each shingle |
| B71 | shingleHeight | 2 mm | Height of each shingle |
| B72 | shingleExposure | 1.5 mm | Exposed portion per course |
| B73 | shingleStaggerPattern | half | Pattern: half, third, or none |
| B74 | shingleWedgeThickness | 0.25 mm | Base thickness of wedges |

### Calculated Parameters
| Parameter | Alias | Value | Description |
|-----------|-------|-------|-------------|
| E14 | wheelSize | 9.63 mm | HO wheel size (calculated) |
| E15 | clapboardHeight | 2.5 mm | Legacy parameter |

## Generator Details

### Brick Generator v4.0.0
- **Purpose:** Parametric masonry walls with four bond patterns
- **Patterns:** Stretcher, English, Flemish, Common
- **Features:** Automatic opening detection, punchout, boolean cut
- **Files:** `brick_generator_macro.FCMacro`, `brick_geometry.py`
- **Tests:** 30 tests (all passing)

### Shingle Generator v4.0.0
- **Purpose:** Roof shingles with staggered courses
- **Features:** Face-based selection, multiple stagger patterns
- **Files:** `shingle_generator.FCMacro`, `shingle_geometry.py`
- **Tests:** 55 tests (all passing)

### Clapboard Generator v6.0.0
- **Purpose:** Horizontal overlapping clapboard siding
- **Features:** Global grid snapping, multi-face alignment, Part::Compound output
- **Files:** `clapboard_generator.FCMacro`, `clapboard_geometry.py`
- **Tests:** Comprehensive test suite

### Board-and-Batten Generator v1.0.0
- **Purpose:** Vertical board-and-batten siding
- **Features:** Face-based selection, automatic gable trimming, hole cutting
- **Files:** `board_batten_generator.FCMacro`, `board_batten_geometry.py`
- **Tests:** Unit tests included

### Bead Board Generator v1.0.0
- **Purpose:** Vertical bead board interior trim
- **Features:** Gap-based groove pattern, face orientation detection
- **Files:** `bead_board_generator.FCMacro`, `bead_board_geometry.py`
- **Tests:** Unit tests included

### Smart Trim Generator v1.2.0
- **Purpose:** Parametric trim for architectural models
- **Features:** Automatic corner detection, miter angle calculation
- **Files:** `smart_trim_generator.FCMacro`, `trim_geometry.py`
- **Tests:** Test suite included

### Station Sign Generator v1.1.1
- **Purpose:** C&O style station signs with parametric text
- **Features:** Text scaling, raised border frame
- **Files:** `station_sign_generator.FCMacro`
- **Tests:** None (manual testing only)

## Architecture Pattern

All generators follow a consistent architecture:

```
generator/
├── *_generator.FCMacro    # FreeCAD macro (UI layer)
├── *_geometry.py          # Pure Python geometry library
├── tests/
│   └── test_*_geometry.py # Pytest unit tests
├── README.md              # Documentation
└── scripts/               # Optional deployment scripts
    ├── *_freecad_installer.py
    └── *_git_populate.py
```

**Benefits:**
- Geometry logic testable without FreeCAD
- Clean separation of concerns
- Consistent API across generators
- Easy to maintain and extend

## Scale Reference (from Skeleton)

### HO Scale (1:87)
- 8" brick = 2.32mm
- 2.25" brick height = 0.65mm
- 3/8" mortar = 0.11mm
- 3" clapboard reveal = 0.87mm
- 4" clapboard reveal = 1.16mm
- 3.5" shingle width = 0.92mm
- 1.5" shingle exposure = 0.40mm

### Other Scales
- **N Scale (1:160):** All dimensions ~55% of HO
- **O Scale (1:48):** All dimensions ~180% of HO
- **S Scale (1:64):** All dimensions ~136% of HO

## Pending Work

1. **Station Sign Generator:** Add automated test suite
2. **Smart Trim:** Implement mitered corner pieces (v1.3.0)
3. **All Generators:** TNP-safe property links (App::PropertyLink)

## File Locations

- **Skeleton.FCStd:** `/General Parts/Skeleton.FCStd`
- **Generators:** `/automation/generators/`
- **FreeCAD Macros:** `~/Library/Application Support/FreeCAD/Macro/` (macOS)
