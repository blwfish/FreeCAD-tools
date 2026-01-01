# Changelog

All notable changes to the Radial Brick Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-01

### Added
- Initial release
- Pure Python geometry library (`radial_brick_geometry.py`)
  - `RadialBrickDef` NamedTuple for brick data
  - `RadialBrickGeometry` class for brick layout generation
  - Support for cylinders (constant radius)
  - Support for cones (linear taper)
  - Support for reverse taper (corbelling)
  - Running bond pattern with configurable offset
  - Vertex calculation for full 3D brick solids
  - Outer face vertex calculation for skin geometry
- FreeCAD macro (`radial_brick_generator_macro.FCMacro`)
  - Cylindrical face analysis
  - Conical face analysis
  - Automatic concave/convex detection
  - Multi-face selection support
  - Spreadsheet parameter reading
  - Metadata properties on output objects
- Installer script (`freecad_installer.py`)
- Comprehensive test suite (35+ tests)
- Full documentation

### Technical Details
- Minimum 8 bricks per course validation
- Axis orientation validation (15° tolerance from vertical)
- Automatic radius interpolation for tapered surfaces
- Bond offset between 0 and 1 (default 0.5 for running bond)

## Future Plans

### [1.1.0] - Planned
- Course range parameter for partial coverage
- Decorative banding support
- Non-vertical axis handling
- Alternative bond patterns (common bond, soldier courses)

### [2.0.0] - Planned
- Horizontal radial patterns (for circular platforms)
- Elliptical surface support
- Automatic multi-face detection
