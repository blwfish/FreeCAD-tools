#!/usr/bin/env python3
"""
Git Tree Populator for Smart Trim Generator v1.0.0

Organizes the smart trim generator files into the correct git repository structure
and stages them with 'git add' (without committing).

Usage:
    python3 smart_trim_git_populate.py

What it does:
    1. Verifies the git repository exists (defaults to /Users/blw/Documents/FreeCAD-github)
    2. Creates directory structure: automation/generators/smart_trim/
    3. Copies macro and geometry files to correct locations
    4. Copies test files to automation/generators/smart_trim/tests/
    5. Copies documentation to automation/generators/smart_trim/
    6. Runs 'git add' for all files (does NOT commit)
    7. Shows what will be committed

Environment:
    Requires: git, Python 3.8+
    Must be run from the unpacked wad directory
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


# Configuration
GENERATOR_NAME = "Smart Trim Generator"
GENERATOR_VERSION = "1.0.0"

# File organization map: (source_file, relative_dest_path)
FILE_MAP = [
    # Main generator files
    ("smart_trim_generator.FCMacro", "automation/generators/smart_trim/smart_trim_generator.FCMacro"),
    ("smart_trim_geometry.py", "automation/generators/smart_trim/smart_trim_geometry.py"),
    
    # Tests
    ("test_smart_trim_geometry.py", "automation/generators/smart_trim/tests/test_smart_trim_geometry.py"),
    
    # Documentation
    ("README.md", "automation/generators/smart_trim/README.md"),
    
    # Deployment scripts (put themselves into scripts/ subdirectory)
    ("smart_trim_git_populate.py", "automation/generators/smart_trim/scripts/smart_trim_git_populate.py"),
    ("smart_trim_freecad_installer.py", "automation/generators/smart_trim/scripts/smart_trim_freecad_installer.py"),
]

# Optional files (don't fail if missing)
OPTIONAL_FILES = [
]


def verify_git_repo(git_root):
    """
    Verify that the directory is a git repository.
    
    Args:
        git_root: Path object for git repository root
        
    Returns:
        True if valid git repo, False otherwise
    """
    git_dir = git_root / ".git"
    if not git_dir.exists():
        return False
    
    # Try to run git status to verify it's a valid repo
    try:
        result = subprocess.run(
            ["git", "status"],
            cwd=git_root,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def create_directories(git_root):
    """
    Create necessary directory structure.
    
    Args:
        git_root: Path object for git root
        
    Returns:
        List of created directories
    """
    created = []
    
    # Directories to create
    dirs = [
        git_root / "automation" / "generators" / "smart_trim",
        git_root / "automation" / "generators" / "smart_trim" / "tests",
    ]
    
    for dir_path in dirs:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {dir_path.relative_to(git_root)}")
            created.append(dir_path)
        else:
            print(f"  Directory exists: {dir_path.relative_to(git_root)}")
    
    return created


def copy_files(git_root):
    """
    Copy files to their destinations in the git tree.
    
    Args:
        git_root: Path object for git root
        
    Returns:
        List of successfully copied files (relative to git_root)
    """
    copied = []
    failed = []
    
    # Wad directory is the script's directory
    wad_dir = Path(__file__).parent
    
    all_files = FILE_MAP + OPTIONAL_FILES
    
    for source_name, dest_rel_path in all_files:
        source = wad_dir / source_name
        dest = git_root / dest_rel_path
        
        # Check if source exists
        if not source.exists():
            if (source_name, dest_rel_path) in FILE_MAP:
                # Required file
                print(f"✗ REQUIRED FILE NOT FOUND: {source_name}")
                failed.append(source_name)
            else:
                # Optional file
                print(f"⚠ Optional file not found: {source_name}")
            continue
        
        # Copy file
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            rel_dest = dest.relative_to(git_root)
            print(f"✓ Copied: {source_name} → {rel_dest}")
            copied.append(rel_dest)
        except Exception as e:
            print(f"✗ FAILED to copy {source_name}: {e}")
            failed.append(source_name)
    
    if failed:
        print(f"\n✗ {len(failed)} file(s) failed to copy!")
        return None
    
    return copied


def git_add_files(git_root, files):
    """
    Stage files with 'git add'.
    
    Args:
        git_root: Path object for git root
        files: List of Path objects (relative to git_root)
        
    Returns:
        True if successful, False otherwise
    """
    if not files:
        print("No files to add to git.")
        return True
    
    try:
        # Build git add command with all file paths
        file_paths = [str(f) for f in files]
        result = subprocess.run(
            ["git", "add"] + file_paths,
            cwd=git_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"✗ Git add failed: {result.stderr}")
            return False
        
        print(f"\n✓ Staged {len(files)} file(s) with 'git add'")
        return True
        
    except Exception as e:
        print(f"✗ Git add failed: {e}")
        return False


def show_git_status(git_root):
    """
    Show git status to confirm what will be committed.
    
    Args:
        git_root: Path object for git root
    """
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=git_root,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print("\nStaged changes (ready to commit):")
            print("=" * 72)
            # Show only lines starting with 'A' (added) or 'M' (modified)
            for line in result.stdout.split("\n"):
                if line and line[0] in ['A', 'M']:
                    print(line)
            print("=" * 72)
    except Exception as e:
        print(f"Could not show git status: {e}")


def main():
    """Main git population flow."""
    
    print("┌" + "="*70 + "┐")
    print("│" + f"  {GENERATOR_NAME} v{GENERATOR_VERSION} - Git Populator".center(70) + "│")
    print("└" + "="*70 + "┘")
    
    # Step 1: Find or verify git root
    print("\n[1/5] Locating git repository...")
    default_git_root = Path("/Users/blw/Documents/FreeCAD-github")
    
    if verify_git_repo(default_git_root):
        git_root = default_git_root
        print(f"✓ Using git root: {git_root}")
    else:
        print(f"\n✗ ERROR: Git repository not found at {default_git_root}")
        print("\nPlease ensure:")
        print("  1. /Users/blw/Documents/FreeCAD-github exists")
        print("  2. It is a valid git repository (.git directory present)")
        print("  3. You have read/write permissions")
        return False
    
    # Step 2: Create directories
    print("\n[2/5] Creating directory structure...")
    try:
        create_directories(git_root)
    except Exception as e:
        print(f"\n✗ ERROR creating directories: {e}")
        return False
    
    # Step 3: Copy files
    print("\n[3/5] Copying files...")
    copied = copy_files(git_root)
    if copied is None:
        print("\n✗ File copy failed!")
        return False
    
    if not copied:
        print("\n✗ No files were copied!")
        return False
    
    # Step 4: Stage with git add
    print("\n[4/5] Staging files with git add...")
    if not git_add_files(git_root, copied):
        print("\n✗ Git add failed!")
        return False
    
    # Step 5: Show status
    print("\n[5/5] Showing git status...")
    show_git_status(git_root)
    
    # Summary
    print("\n" + "="*72)
    print("✓ SUCCESS!")
    print("="*72)
    print(f"\nOrganized {len(copied)} file(s) into git tree:")
    print(f"  automation/generators/smart_trim/")
    print(f"    ├── smart_trim_generator.FCMacro")
    print(f"    ├── smart_trim_geometry.py")
    print(f"    ├── tests/")
    print(f"    ├── scripts/")
    print(f"    └── README.md")
    print("\nNext steps:")
    print("  1. Review the changes: git status")
    print("  2. Review the diff: git diff --cached")
    print("  3. Commit when ready: git commit -m 'Add smart trim generator v1.0.0'")
    print("\nYour files are now in the correct git structure and staged!")
    print("="*72 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
