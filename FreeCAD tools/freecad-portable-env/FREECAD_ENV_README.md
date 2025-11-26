# FreeCAD Portable Environment Scripts

Tools for creating and restoring portable FreeCAD environments across machines.

## Overview

These scripts let you:
1. **Pack** your FreeCAD setup on one machine into a portable bundle
2. **Transfer** the bundle to another machine (USB drive, scp, etc.)
3. **Unpack** the environment on the target machine

All your macros, settings, preferences, and custom configurations are preserved.

## Scripts

### pack_freecad.sh
Creates a tarball of your FreeCAD environment.

**Usage:**
```bash
./pack_freecad.sh [output_directory]
```

**Examples:**
```bash
# Create tarball in current directory
./pack_freecad.sh .

# Create in Desktop
./pack_freecad.sh ~/Desktop

# Create in Downloads
./pack_freecad.sh ~/Downloads
```

**Output:**
Creates a file like: `freecad-env-20251126-v1.0.0.tar.gz`

**What it packs:**
- Macros and support files
- Workbench configurations
- User preferences (plist file)
- Custom templates
- Settings and configurations

**Size:**
Typically 50-500 MB depending on your setup.

### unpack_freecad.sh
Restores a FreeCAD environment from a tarball.

**Usage:**
```bash
./unpack_freecad.sh <tarball> [--backup]
```

**Examples:**
```bash
# Unpack (with confirmation prompt)
./unpack_freecad.sh freecad-env-20251126-v1.0.0.tar.gz

# Unpack with automatic backup
./unpack_freecad.sh freecad-env-20251126-v1.0.0.tar.gz --backup
```

**What it does:**
1. Extracts the tarball
2. Creates a backup of current FreeCAD configuration
3. Restores the new environment
4. Shows you where the backup is (in case you need to revert)

**Important:** Completely replaces your FreeCAD configuration. Always back up first!

## Workflow

### On Source Machine (Studio)
```bash
cd ~/Documents/FreeCAD-github
./pack_freecad.sh ~/Desktop

# Now you have: ~/Desktop/freecad-env-20251126-v1.0.0.tar.gz
```

### Transfer to Target Machine (Laptop)
```bash
# Option 1: USB drive
cp ~/Desktop/freecad-env-*.tar.gz /Volumes/USB-Drive/

# Option 2: scp over network
scp ~/Desktop/freecad-env-*.tar.gz user@laptop:~/

# Option 3: Cloud sync (Dropbox, iCloud Drive, etc.)
cp ~/Desktop/freecad-env-*.tar.gz ~/Dropbox/
```

### On Target Machine (Laptop)
```bash
# Get the scripts from GitHub
git clone https://github.com/blwfish/FreeCAD-tools.git
cd FreeCAD-tools

# Unpack the environment
./unpack_freecad.sh ~/freecad-env-20251126-v1.0.0.tar.gz

# Restart FreeCAD
```

## Backups

Each time you unpack, the script automatically backs up your current configuration to:
```
~/.freecad-backup-YYYYMMDD-HHMMSS/
```

If something goes wrong, you can restore:
```bash
# Remove the broken environment
rm -rf ~/Library/Application\ Support/FreeCAD

# Restore from backup
cp -r ~/.freecad-backup-YYYYMMDD-HHMMSS/FreeCAD \
      ~/Library/Application\ Support/
```

## What's NOT Included

These scripts do **NOT** include:
- Your .FCStd model files (keep those in git)
- Git repositories (clone fresh from GitHub/Gitea)
- Large binary caches
- Build artifacts

This keeps the portable bundle focused and size-manageable.

## Versioning

Both scripts include version numbers. Keep them in sync with your FreeCAD-tools version:

**Current versions:**
- pack_freecad.sh: 1.0.0
- unpack_freecad.sh: 1.0.0

Update the `SCRIPT_VERSION` variable in both scripts when you bump versions.

## Troubleshooting

### Tarball is huge (> 1 GB)
- You might have large cached files in your FreeCAD directory
- Consider clearing caches before packing:
  ```bash
  rm -rf ~/Library/Caches/FreeCAD
  ```

### Unpacking says "Permission denied"
- Make sure unpack_freecad.sh is executable:
  ```bash
  chmod +x unpack_freecad.sh
  ```

### My preferences didn't restore
- Preferences files are stored in `~/Library/Preferences/`
- They're read-only on some systems
- FreeCAD will recreate them on first launch

### Macros aren't showing up
- Restart FreeCAD completely (quit and reopen)
- Check the macro location in FreeCAD:
  - FreeCAD > Preferences > Python > Macro
  - Should show: `~/Library/Application Support/FreeCAD/Macro/`

## Notes

- **macOS only** (currently)
- Both scripts use bash with color output
- They're safe to run multiple times
- Always test unpacking on a non-critical machine first
- Keep multiple backups of your tarball

## Adding to Your Repo

Put these scripts in your FreeCAD-tools repository:

```bash
cp pack_freecad.sh /path/to/FreeCAD-tools/
cp unpack_freecad.sh /path/to/FreeCAD-tools/
git add pack_freecad.sh unpack_freecad.sh
git commit -m "Add FreeCAD portable environment scripts v1.0.0"
git push
```

Then anyone can restore your environment setup:
```bash
git clone https://github.com/blwfish/FreeCAD-tools.git
cd FreeCAD-tools
./unpack_freecad.sh ~/freecad-env-*.tar.gz
```
