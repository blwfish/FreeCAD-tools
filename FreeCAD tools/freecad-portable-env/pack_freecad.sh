#!/bin/bash

##############################################################################
# pack_freecad.sh - Pack FreeCAD environment into portable tarball
#
# Creates a portable FreeCAD environment bundle containing:
#   - Macros and support files
#   - FreeCAD preferences and settings
#   - Custom templates
#   - Workbench configurations
#
# Excludes: caches, temp files, Python bytecode
#
# Usage: ./pack_freecad.sh [output_directory]
#
# Example:
#   ./pack_freecad.sh ~/Desktop
#   # Creates: ~/Desktop/freecad-env-20251126-v1.0.0.tar.gz
#
# Version: 1.0.0
##############################################################################

set -e

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Script version
SCRIPT_VERSION="1.0.0"
TIMESTAMP=$(date +%Y%m%d)

# Determine output directory
OUTPUT_DIR="${1:-.}"

if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${RED}❌ Error: Output directory does not exist: $OUTPUT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}FreeCAD Environment Packer${NC}"
echo -e "${BLUE}Version: $SCRIPT_VERSION${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Define FreeCAD directories (macOS)
FC_APP_SUPPORT="$HOME/Library/Application Support/FreeCAD"

# Check if FreeCAD is installed
if [ ! -d "$FC_APP_SUPPORT" ]; then
    echo -e "${RED}❌ Error: FreeCAD not found at $FC_APP_SUPPORT${NC}"
    echo "Is FreeCAD installed? Check ~/Library/Application Support/"
    exit 1
fi

echo -e "${YELLOW}Source directory:${NC}"
echo "  $FC_APP_SUPPORT"
echo ""

# Create temporary working directory
WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

BUNDLE_DIR="$WORK_DIR/freecad-env"
mkdir -p "$BUNDLE_DIR"

echo -e "${YELLOW}Step 1: Copying FreeCAD configuration...${NC}"

# Copy Application Support directory, excluding caches and temp files
cp -r "$FC_APP_SUPPORT" "$BUNDLE_DIR/Application_Support"

# Remove unwanted directories from the copy
rm -rf "$BUNDLE_DIR/Application_Support/Caches" 2>/dev/null || true
rm -rf "$BUNDLE_DIR/Application_Support/__pycache__" 2>/dev/null || true
find "$BUNDLE_DIR/Application_Support" -name "*.pyc" -delete 2>/dev/null || true
find "$BUNDLE_DIR/Application_Support" -name ".DS_Store" -delete 2>/dev/null || true

echo -e "${GREEN}✓${NC} Copied Application Support (cleaned)"

echo ""
echo -e "${YELLOW}Step 2: Creating unpack script...${NC}"

# Create unpack script inside the bundle
UNPACK_SCRIPT="$BUNDLE_DIR/unpack_freecad.sh"
cat > "$UNPACK_SCRIPT" << 'UNPACK_EOF'
#!/bin/bash

##############################################################################
# Unpack FreeCAD Environment (macOS)
#
# Restores a portable FreeCAD environment tarball to the correct locations:
# - Macros → ~/Library/Application Support/FreeCAD/Macro/
# - Settings → ~/Library/Application Support/FreeCAD/
# - Preferences → ~/.plist files
#
# Backs up existing configuration with .backup suffix before restoring.
#
# Usage: ./unpack_freecad.sh
#        (Run this from inside the extracted freecad-env directory)
#
# Example:
#   tar -xzf freecad-env-20251126-v1.0.0.tar.gz
#   cd freecad-env
#   ./unpack_freecad.sh
#
##############################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}FreeCAD Environment Unpacker (macOS)${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check we're in the right directory
if [ ! -f "MANIFEST.txt" ]; then
    echo -e "${RED}❌ Error: MANIFEST.txt not found${NC}"
    echo "Make sure you're in the extracted freecad-env directory"
    echo ""
    echo "Usage:"
    echo "  tar -xzf freecad-env-*.tar.gz"
    echo "  cd freecad-env"
    echo "  ./unpack_freecad.sh"
    exit 1
fi

FREECAD_CONFIG_DIR="$HOME/Library/Application Support/FreeCAD"

# Confirmation prompt
echo -e "${YELLOW}⚠️  WARNING:${NC}"
echo "This will OVERWRITE your current FreeCAD configuration:"
echo "  - Macros"
echo "  - Settings"
echo "  - Workbenches"
echo "  - Preferences"
echo ""
echo "A backup will be created with .backup suffix"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Step 1: Creating backup of current configuration...${NC}"

if [ -d "$FREECAD_CONFIG_DIR" ]; then
    BACKUP_DIR="$FREECAD_CONFIG_DIR.backup-$(date +%Y%m%d-%H%M%S)"
    cp -r "$FREECAD_CONFIG_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓${NC} Backed up to: $BACKUP_DIR"
else
    echo -e "${YELLOW}ℹ${NC} No existing FreeCAD configuration to back up"
fi

echo ""
echo -e "${YELLOW}Step 2: Restoring FreeCAD environment...${NC}"

# Remove old configuration
if [ -d "$FREECAD_CONFIG_DIR" ]; then
    rm -rf "$FREECAD_CONFIG_DIR"
fi

# Copy new configuration
cp -r Application_Support "$FREECAD_CONFIG_DIR"
echo -e "${GREEN}✓${NC} Restored FreeCAD configuration"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Unpacking complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Quit FreeCAD (if running)"
echo "2. Restart FreeCAD"
echo "3. Verify macros are present:"
echo "   FreeCAD > Macro > Macros"
echo ""
if [ -n "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Your backup is at:${NC}"
    echo "  $BACKUP_DIR"
    echo ""
    echo "To restore if needed:"
    echo "  rm -rf \"$FREECAD_CONFIG_DIR\""
    echo "  cp -r \"$BACKUP_DIR\" \"$FREECAD_CONFIG_DIR\""
    echo ""
fi
UNPACK_EOF

chmod +x "$UNPACK_SCRIPT"
echo -e "${GREEN}✓${NC} Created unpack_freecad.sh"

echo ""
echo -e "${YELLOW}Step 3: Creating manifest...${NC}"

# Create manifest file
MANIFEST="$BUNDLE_DIR/MANIFEST.txt"
cat > "$MANIFEST" << 'MANIFEST_EOF'
FreeCAD Portable Environment Bundle
====================================

This is a complete, portable FreeCAD environment bundle.

Contents:
  Application_Support/     - FreeCAD application data
                           (Macro/, Mod/, User/, etc.)
  unpack_freecad.sh        - Script to restore this environment
  MANIFEST.txt             - This file

Installation:
  1. Extract the tarball:
     tar -xzf freecad-env-*.tar.gz

  2. Go into the directory:
     cd freecad-env

  3. Run the unpack script:
     ./unpack_freecad.sh

  4. Restart FreeCAD

The script will:
  - Backup your current FreeCAD configuration
  - Restore this environment
  - Show you where the backup is (in case you need to revert)

What's included:
  ✓ Macros and plugins
  ✓ Workbench configurations
  ✓ User preferences
  ✓ Custom templates
  ✓ Settings and configurations

What's excluded (for size):
  ✗ Caches (auto-recreated on launch)
  ✗ Python bytecode (auto-regenerated)
  ✗ Temp files (.DS_Store, etc.)

MANIFEST_EOF

echo -e "${GREEN}✓${NC} Created manifest"

echo ""
echo -e "${YELLOW}Step 4: Creating tarball...${NC}"

# Create tarball, excluding unneeded files
TARBALL_NAME="freecad-env-${TIMESTAMP}-v${SCRIPT_VERSION}.tar.gz"
TARBALL_PATH="$OUTPUT_DIR/$TARBALL_NAME"

cd "$WORK_DIR"
tar --exclude='Caches' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    -czf "$TARBALL_PATH" freecad-env/

echo -e "${GREEN}✓${NC} Created $TARBALL_NAME"
echo ""

# Show file size
SIZE=$(du -h "$TARBALL_PATH" | cut -f1)
echo -e "${YELLOW}File size: $SIZE${NC}"
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Packing complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Output:${NC}"
echo "  $TARBALL_PATH"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Transfer to another machine:"
echo "   scp $TARBALL_PATH user@laptop:~/"
echo "   # or copy to USB drive, cloud storage, etc."
echo ""
echo "2. On the target machine:"
echo "   tar -xzf $TARBALL_NAME"
echo "   cd freecad-env"
echo "   ./unpack_freecad.sh"
echo ""
echo "3. Restart FreeCAD on the target machine"
echo ""
echo -e "${YELLOW}Everything you need is in the tarball!${NC}"
echo ""
