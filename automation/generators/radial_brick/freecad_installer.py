#!/usr/bin/env python3
"""
FreeCAD Macro Installer for radial_brick_generator

This file provides a FreeCAD-native way to install the radial brick generator.

Usage in FreeCAD:
1. Open the Macro menu
2. Select "Execute macro..."
3. Choose this file (freecad_installer.py)
4. Run it

Version: 1.0.0
"""

import os
import sys
import shutil
from pathlib import Path

GENERATOR_VERSION = "1.0.0"


def run():
    """Install radial brick generator when executed as FreeCAD macro."""
    try:
        import FreeCAD
        freecad_available = True
    except ImportError:
        freecad_available = False

    if freecad_available:
        # We're running inside FreeCAD
        macro_dir = Path(FreeCAD.getUserMacroDir())
    else:
        # Fall back to platform detection
        import platform
        system = platform.system()

        if system == "Darwin":  # macOS
            base_dir = Path.home() / "Library" / "Application Support" / "FreeCAD"
        elif system == "Windows":
            base_dir = Path.home() / "AppData" / "Roaming" / "FreeCAD"
        else:  # Linux
            base_dir = Path.home() / ".config" / "FreeCAD"

        macro_dir = base_dir / "Macro"

    if not macro_dir.exists():
        print(f"ERROR: FreeCAD macro directory not found: {macro_dir}")
        return False

    # Get source directory (where this installer is)
    script_dir = Path(__file__).parent

    # Create radial_brick subdirectory for library
    lib_dir = macro_dir / "radial_brick"
    lib_dir.mkdir(parents=True, exist_ok=True)

    # Copy files
    try:
        # Copy macro to ROOT (so it appears in FreeCAD UI)
        macro_src = script_dir / "radial_brick_generator_macro.FCMacro"
        macro_dst = macro_dir / "radial_brick_generator_macro.FCMacro"
        if macro_src.exists():
            shutil.copy2(macro_src, macro_dst)

        # Copy geometry library to radial_brick/ subdirectory
        geom_src = script_dir / "radial_brick_geometry.py"
        geom_dst = lib_dir / "radial_brick_geometry.py"

        if geom_src.exists():
            shutil.copy2(geom_src, geom_dst)

        print(f"✓ Radial brick generator v{GENERATOR_VERSION} installed")
        print(f"  Location: {macro_dir}")
        print(f"  Macro: radial_brick_generator_macro.FCMacro")
        print(f"  Library: radial_brick/radial_brick_geometry.py")
        return True

    except Exception as e:
        print(f"ERROR: Installation failed: {e}")
        return False


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
