#!/usr/bin/env python3
"""
FreeCAD Installer for Clapboard Generator v5.1.0

Installs the clapboard generator macro and geometry library to your FreeCAD
Macro directory.

Usage:
    python3 clapboard_freecad_installer.py

What it does:
    1. Detects your FreeCAD Macro directory (OS-aware)
    2. Copies clapboard_geometry.py to Macro/_lib directory
    3. Copies clapboard_generator.FCMacro to Macro directory
    4. Verifies imports work
    5. Reports installation status

Environment:
    Works on macOS, Linux, Windows
    Requires Python 3.8+
    No external dependencies
"""

import os
import sys
import shutil
import platform
from pathlib import Path


# Configuration
GENERATOR_NAME = "Clapboard Generator"
GENERATOR_VERSION = "5.1.0"

# Files to install
MACROS_TO_INSTALL = [
    "clapboard_generator.FCMacro",
]

LIBS_TO_INSTALL = [
    "clapboard_geometry.py",
]

# Optional test file (useful for development)
OPTIONAL_FILES = [
    "test_clapboard_geometry.py",
]


def get_freecad_macro_directory():
    """
    Detect FreeCAD Macro directory based on OS.
    
    Returns:
        Path object for FreeCAD Macro directory
        
    Raises:
        FileNotFoundError if directory cannot be found
    """
    system = platform.system()
    
    if system == "Darwin":
        # macOS
        macro_dir = Path.home() / "Library" / "Application Support" / "FreeCAD" / "Macro"
    elif system == "Linux":
        # Linux
        macro_dir = Path.home() / ".FreeCAD" / "Macro"
    elif system == "Windows":
        # Windows
        appdata = os.getenv("APPDATA")
        if appdata:
            macro_dir = Path(appdata) / "FreeCAD" / "Macro"
        else:
            raise FileNotFoundError("Could not determine Windows APPDATA directory")
    else:
        raise OSError(f"Unsupported OS: {system}")
    
    if not macro_dir.exists():
        raise FileNotFoundError(
            f"FreeCAD Macro directory not found: {macro_dir}\n"
            f"Please install FreeCAD first."
        )
    
    return macro_dir


def install_files(macro_dir):
    """
    Copy required files to FreeCAD Macro directory.
    
    Macros go to: macro_dir/
    Libraries go to: macro_dir/_lib/
    
    Args:
        macro_dir: Path object for FreeCAD Macro directory
        
    Returns:
        List of successfully installed file paths
    """
    installed = []
    
    print(f"\nInstalling to: {macro_dir}\n")
    
    # Create _lib subdirectory
    lib_dir = macro_dir / "_lib"
    try:
        lib_dir.mkdir(exist_ok=True)
    except Exception as e:
        print(f"✗ Could not create _lib directory: {e}")
        return None
    
    # Install macros to root
    for filename in MACROS_TO_INSTALL:
        source = Path(filename)
        dest = macro_dir / filename
        
        if not source.exists():
            print(f"✗ SKIP: {filename} (not found in current directory)")
            continue
        
        try:
            shutil.copy2(source, dest)
            print(f"✓ Installed: {filename}")
            installed.append(dest)
        except Exception as e:
            print(f"✗ FAILED: {filename} - {e}")
            return None
    
    # Install libraries to _lib subdirectory
    for filename in LIBS_TO_INSTALL:
        source = Path(filename)
        dest = lib_dir / filename
        
        if not source.exists():
            print(f"✗ SKIP: {filename} (not found in current directory)")
            continue
        
        try:
            shutil.copy2(source, dest)
            print(f"✓ Installed: {filename} → _lib/")
            installed.append(dest)
        except Exception as e:
            print(f"✗ FAILED: {filename} - {e}")
            return None
    
    # Try to install optional files to _lib (don't fail if missing)
    for filename in OPTIONAL_FILES:
        source = Path(filename)
        dest = lib_dir / filename
        
        if source.exists():
            try:
                shutil.copy2(source, dest)
                print(f"✓ Installed (optional): {filename} → _lib/")
                installed.append(dest)
            except Exception as e:
                print(f"⚠ Warning: Could not install optional {filename}: {e}")
    
    return installed


def verify_imports():
    """
    Verify that the installed modules can be imported.
    
    Returns:
        True if imports successful, False otherwise
    """
    print("\nVerifying imports...")
    
    # Add _lib to Python path for imports
    lib_path = Path.cwd() / "_lib"
    if lib_path.exists():
        sys.path.insert(0, str(lib_path))
    
    try:
        import clapboard_geometry
        print("✓ clapboard_geometry.py imports successfully")
    except ImportError as e:
        print(f"✗ clapboard_geometry.py import failed: {e}")
        return False
    
    # Try to import a function from the geometry library
    try:
        from clapboard_geometry import validate_parameters
        print("✓ clapboard_geometry functions are accessible")
    except ImportError as e:
        print(f"✗ Could not import functions from clapboard_geometry: {e}")
        return False
    
    return True


def main():
    """Main installation flow."""
    
    print("┌" + "="*70 + "┐")
    print("│" + f"  {GENERATOR_NAME} v{GENERATOR_VERSION} - FreeCAD Installer".center(70) + "│")
    print("└" + "="*70 + "┘")
    
    # Step 1: Find FreeCAD Macro directory
    print("\n[1/4] Locating FreeCAD Macro directory...")
    try:
        macro_dir = get_freecad_macro_directory()
        print(f"✓ Found: {macro_dir}")
    except (FileNotFoundError, OSError) as e:
        print(f"\n✗ ERROR: {e}")
        return False
    
    # Step 2: Install files
    print("\n[2/4] Installing files...")
    installed = install_files(macro_dir)
    if installed is None:
        print("\n✗ Installation failed!")
        return False
    
    if not installed:
        print("\n✗ No files were installed!")
        return False
    
    # Step 3: Verify imports
    print("\n[3/4] Verifying imports...")
    
    # Add macro directory to Python path so we can import
    sys.path.insert(0, str(macro_dir / "_lib"))
    
    if not verify_imports():
        print("\n✗ Import verification failed!")
        return False
    
    # Step 4: Summary
    print("\n[4/4] Installation complete!")
    
    print("\n" + "="*72)
    print("✓ SUCCESS!")
    print("="*72)
    print(f"\nInstalled {len(installed)} file(s) to:")
    print(f"  {macro_dir}/")
    print(f"  └─ _lib/ (geometry libraries)")
    print("\nYour FreeCAD is now ready to use the Clapboard Generator!")
    print("\nNext steps:")
    print("  1. Open FreeCAD")
    print("  2. Create or open a model with wall faces")
    print("  3. Select one or more wall faces (Ctrl+click in 3D view)")
    print("  4. Macro menu → Recent macros → clapboard_generator.FCMacro")
    print("  5. Watch the clapboards generate!")
    print("\nFor detailed instructions, see README.md")
    print("="*72 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
