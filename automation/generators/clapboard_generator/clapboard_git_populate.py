#!/usr/bin/env python3
"""
git_populate.py v4.1.0 - Stage brick generator files to git repository

This script copies generator files to the git repository and stages them
for commit. You can then review and commit manually when ready.

Usage:
    python3 git_populate.py [--verbose]

Default git repo: /Users/blw/Documents/FreeCAD-github/
Override with: GIT_REPO_PATH environment variable
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Version must match clapboard_generator_macro.FCMacro VERSION header
GENERATOR_VERSION = "6.0.0"

# Default git repository path
DEFAULT_GIT_REPO = Path.home() / "Documents" / "FreeCAD-github"

# Generator subdirectory in repo
GENERATOR_SUBDIR = "automation/generators/clapboard_generator"


def find_git_repo():
    """Find the git repository path."""
    # Check environment variable first
    env_path = os.environ.get('GIT_REPO_PATH')
    if env_path:
        repo_path = Path(env_path)
        if repo_path.exists():
            return repo_path
        print(f"WARNING: GIT_REPO_PATH set but directory doesn't exist: {env_path}")
    
    # Use default
    if DEFAULT_GIT_REPO.exists():
        return DEFAULT_GIT_REPO
    
    return None


def populate_git_repo(verbose=False):
    """Copy generator files to git repo and stage them."""
    
    # Find git repository
    git_repo = find_git_repo()
    if not git_repo:
        print("ERROR: Could not find git repository")
        print(f"Expected: {DEFAULT_GIT_REPO}")
        print("Set GIT_REPO_PATH environment variable to override")
        return False
    
    if verbose:
        print(f"Git repository: {git_repo}")
    
    # Create generator directory in repo
    gen_dir = git_repo / GENERATOR_SUBDIR
    gen_dir.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        print(f"Generator directory: {gen_dir}")
    
    # Get the directory where this script is located (source)
    script_dir = Path(__file__).parent
    
    # Files to copy
    files_to_copy = [
        "clapboard_generator.FCMacro",
        "clapboard_geometry.py",
        "README.md",
        "CHANGELOG.md",
        "clapboard_git_populate.py",
        "clapboard_freecad_installer.py",
    ]
    
    # Copy files
    copied_files = []
    for filename in files_to_copy:
        src_path = script_dir / filename
        dest_path = gen_dir / filename
        
        if not src_path.exists():
            print(f"WARNING: Source file not found: {src_path}")
            continue
        
        try:
            shutil.copy2(src_path, dest_path)
            copied_files.append(filename)
            if verbose:
                print(f"Copied: {filename}")
        except Exception as e:
            print(f"ERROR: Could not copy {filename}: {e}")
            return False
    
    print(f"✓ Copied {len(copied_files)} files to git repository")
    print(f"  Location: {gen_dir}")
    
    # Stage files with git add
    try:
        # Change to git repo directory
        os.chdir(git_repo)
        
        # Build relative path for git add
        rel_path = GENERATOR_SUBDIR + "/*"
        
        if verbose:
            print(f"\nStaging files with: git add {rel_path}")
        
        # Run git add
        result = subprocess.run(
            ["git", "add", rel_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Files staged with git add")
        
        # Show git status for the generator directory
        if verbose:
            print("\nGit status:")
            status_result = subprocess.run(
                ["git", "status", GENERATOR_SUBDIR],
                capture_output=True,
                text=True
            )
            print(status_result.stdout)
        
        print(f"\nReady to commit! Review changes with:")
        print(f"  cd {git_repo}")
        print(f"  git status")
        print(f"  git diff --cached {GENERATOR_SUBDIR}")
        print(f"\nThen commit when ready:")
        print(f"  git commit -m 'Clapboard generator v{GENERATOR_VERSION}'")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERROR: git add failed: {e}")
        if e.stderr:
            print(f"  {e.stderr}")
        return False
    except FileNotFoundError:
        print("ERROR: git command not found")
        print("Make sure git is installed and in your PATH")
        return False


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    
    success = populate_git_repo(verbose=verbose)
    sys.exit(0 if success else 1)
