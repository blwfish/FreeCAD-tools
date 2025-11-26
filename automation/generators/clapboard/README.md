# Clapboard Generator v4.3.0 Restructuring

Reorganization of clapboard generator to match the production-ready structure used by shingle_generator v4.0.0.

## What Changed

**v4.3.0 Restructuring:**
- ✅ Extracted geometry library: `clapboard_geometry.py` (pure Python, testable)
- ✅ Created comprehensive test suite: `test_clapboard_geometry.py` (15+ test classes)
- ✅ Reorganized into standard structure: `automation/generators/clapboard/`
- ✅ Generated deployment scripts: `freecad_installer.py`, `git_populate.py`
- ✅ Maintained backward compatibility: existing macro `clapboard_generator.FCMacro` unchanged

## Directory Structure

```
automation/generators/clapboard/
├── clapboard_generator.FCMacro    (v4.3.0 - unchanged)
├── clapboard_geometry.py          (pure Python library)
├── README.md                      (this file)
└── tests/
    └── test_clapboard_geometry.py (15+ test classes, 50+ tests)
```

## Files in This Wad

- `clapboard_generator.FCMacro` — FreeCAD macro (v4.3.0)
- `clapboard_geometry.py` — Pure Python geometry functions
- `test_clapboard_geometry.py` — Comprehensive test suite
- `clapboard_freecad_installer.py` — Installs to FreeCAD Macro directory
- `clapboard_git_populate.py` — Organizes files in git tree + stages
- `CLAPBOARD_README.md` — This documentation

## Installation

### Quick Start

```bash
# 1. Unpack wad
cd ~/Downloads
tar -xzf clapboard-generator-v4.3.0.tar.gz
cd clapboard-generator-v4.3.0

# 2. Install to FreeCAD
python3 clapboard_freecad_installer.py

# 3. Organize in git
cd ~/Documents/FreeCAD-github
python3 ~/Downloads/clapboard-generator-v4.3.0/clapboard_git_populate.py

# 4. Review and commit
git status
git diff --cached
git commit -m "Reorganize clapboard generator to v4.3.0 structure"
```

## Usage in FreeCAD

1. Open your model
2. Create wall sketches (vertical planes: XZ or YZ)
3. Select one or more sketches (Ctrl+click)
4. Macro menu → Recent macros → `clapboard_generator.FCMacro`
5. Clapboards will generate with trim

## Parameters

Parameters are read from spreadsheet (default: "params" or "Spreadsheet"):

- `clapboard_height`: Reveal height (mm) — default 0.8mm (HO scale)
- `clapboard_thickness`: Thickness at bottom edge (mm) — default 0.2mm
- `trim_width`: Width of corner trim (mm) — default 1.5mm
- `trim_thickness`: Trim projection (mm) — default 0.2mm
- `wall_thickness`: Structural wall thickness (mm) — default 2.0mm

## Testing

### Run Test Suite

```bash
# From the wad directory
pytest test_clapboard_geometry.py -v

# Or run directly
python3 test_clapboard_geometry.py
```

### Test Coverage

- Edge validation (degenerate, duplicates)
- Wire geometry validation
- Face orientation detection (XY, XZ, YZ planes)
- Building corner detection
- Course calculations
- Parameter validation
- HO scale defaults

## Comparing with Shingle Generator

Both generators now follow the same patterns:

| Aspect | Shingle v4.0.0 | Clapboard v4.3.0 |
|--------|---|---|
| Geometry library | ✅ shingle_geometry.py | ✅ clapboard_geometry.py |
| Tests | ✅ 55 tests | ✅ 50+ tests |
| Pure Python | ✅ Fully testable | ✅ Fully testable |
| Deployment | ✅ Automated scripts | ✅ Automated scripts |
| Directory | ✅ automation/generators/shingle/ | ✅ automation/generators/clapboard/ |
| _lib structure | ✅ Macro files in root | ✅ Macro files in root |

---

**Generator v4.3.0 — Parametric clapboard siding for HO scale model railroads**
