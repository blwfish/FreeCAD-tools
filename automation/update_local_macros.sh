#!/bin/bash
set -e

MACRO_DIR="$HOME/Library/Application Support/FreeCAD/v1-2/Macro"
REPO="blwfish/FreeCAD-tools"
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

echo "Cloning latest generators..."
PATH=/opt/homebrew/bin:$PATH gh repo clone "$REPO" "$TMP_DIR" -- --depth=1 --quiet

echo "Installing to: $MACRO_DIR"
echo ""

install_file() {
    cp "$1" "$MACRO_DIR/"
    echo "  $(basename $1)"
}

# Top-level macros
find "$TMP_DIR/automation" -maxdepth 1 -name "*.FCMacro" | while read f; do
    install_file "$f"
done

# Shared utilities
install_file "$TMP_DIR/automation/generators/_shared/freecad_utils.py"

# Per-generator: FCMacro and geometry .py files (skip tests, old installer scripts, __init__)
find "$TMP_DIR/automation/generators" -mindepth 2 -maxdepth 2 \( -name "*.FCMacro" -o -name "*.py" \) \
    ! -path "*/_shared/*" \
    ! -path "*/terrain_generator/*" \
    ! -name "__init__.py" \
    ! -name "test_*.py" \
    ! -name "freecad_installer.py" \
    ! -name "git_populate.py" \
    ! -name "clapboard_freecad_installer.py" \
    ! -name "clapboard_git_populate.py" \
    | while read f; do
    install_file "$f"
done

echo ""
echo "Done."
