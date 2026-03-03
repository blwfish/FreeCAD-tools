#!/usr/bin/env python3
"""
FreeCAD Macro Installer for radial_brick_generator

Usage:
    python3 freecad_installer.py          # standalone
    Execute via Macro menu inside FreeCAD

Version: 1.0.2
"""

import os
import re
import sys
import shutil
import platform
from pathlib import Path

GENERATOR_VERSION = "1.0.2"


def get_macro_dir():
    """Return the active FreeCAD Macro directory, preferring versioned dirs."""
    try:
        import FreeCAD
        return Path(FreeCAD.getUserMacroDir())
    except ImportError:
        pass

    system = platform.system()
    if system == "Darwin":
        base_dir = Path.home() / "Library" / "Application Support" / "FreeCAD"
    elif system == "Windows":
        appdata = os.getenv("APPDATA")
        if not appdata:
            raise FileNotFoundError("Could not determine Windows APPDATA directory")
        base_dir = Path(appdata) / "FreeCAD"
    else:
        base_dir = Path.home() / ".FreeCAD"

    # Prefer highest versioned dir (v1-2 > v1-1 > unversioned)
    versioned = sorted(
        [d for d in base_dir.iterdir()
         if d.is_dir() and re.match(r'v\d+-\d+', d.name) and (d / "Macro").exists()],
        key=lambda d: [int(x) for x in d.name[1:].split('-')],
        reverse=True
    )
    if versioned:
        return versioned[0] / "Macro"

    macro_dir = base_dir / "Macro"
    if not macro_dir.exists():
        raise FileNotFoundError(f"FreeCAD Macro directory not found under {base_dir}")
    return macro_dir


def run():
    """Install radial brick generator."""
    try:
        macro_dir = get_macro_dir()
    except Exception as e:
        print(f"ERROR: {e}")
        return False

    if not macro_dir.exists():
        print(f"ERROR: FreeCAD macro directory not found: {macro_dir}")
        return False

    script_dir = Path(__file__).parent
    shared_dir = script_dir.parent / "_shared"
    lib_dir = macro_dir / "_lib"
    lib_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Macro to root
        shutil.copy2(script_dir / "radial_brick_generator_macro.FCMacro",
                     macro_dir / "radial_brick_generator_macro.FCMacro")
        # Geometry library to _lib/
        shutil.copy2(script_dir / "radial_brick_geometry.py",
                     lib_dir / "radial_brick_geometry.py")
        # Shared FreeCAD utilities to _lib/
        shared_utils = shared_dir / "freecad_utils.py"
        if shared_utils.exists():
            shutil.copy2(shared_utils, lib_dir / "freecad_utils.py")
        else:
            print(f"  WARNING: {shared_utils} not found — skipping freecad_utils")

        print(f"✓ Radial brick generator v{GENERATOR_VERSION} installed")
        print(f"  Location: {macro_dir}")
        print(f"  Macro: radial_brick_generator_macro.FCMacro")
        print(f"  Library: _lib/radial_brick_geometry.py")
        print(f"  Library: _lib/freecad_utils.py")
        return True

    except Exception as e:
        print(f"ERROR: Installation failed: {e}")
        return False


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
