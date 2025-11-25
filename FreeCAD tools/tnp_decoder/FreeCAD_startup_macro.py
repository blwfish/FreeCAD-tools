"""
FreeCAD Startup Macro - Auto-load TNP Decoder

Place this file in your FreeCAD Macros folder so it runs at startup.
The TNP decoder will then be available in the Python console without manual import.

Name this file: 10_load_tnp_decoder.py (the 10_ prefix ensures early loading)

Location:
    macOS:   ~/Library/Application Support/FreeCAD/Macro/
    Linux:   ~/.FreeCAD/Macro/
    Windows: %APPDATA%\FreeCAD\Macro\

The macro will automatically detect the OS and look for tnp_decoder in standard locations.
After placing, restart FreeCAD and the TNP decoder will be available.
"""

import sys
import os
import platform

# Determine OS and build search paths
system = platform.system()
macro_dir = None

if system == "Darwin":  # macOS
    macro_dir = os.path.expanduser('~/Library/Application Support/FreeCAD/Macro')
elif system == "Linux":
    macro_dir = os.path.expanduser('~/.FreeCAD/Macro')
elif system == "Windows":
    # Windows uses %APPDATA%
    appdata = os.environ.get('APPDATA')
    if appdata:
        macro_dir = os.path.join(appdata, 'FreeCAD', 'Macro')

# Build list of candidate paths where tnp_decoder might be
tnp_decoder_paths = []

# Primary: same directory as this macro (tnp_decoder package)
if macro_dir:
    tnp_decoder_paths.append(macro_dir)

# Secondary: standard FreeCAD locations
if system == "Darwin":
    tnp_decoder_paths.extend([
        os.path.expanduser('~/Documents/FreeCAD-Tools'),
        os.path.expanduser('~/Documents/FreeCAD'),
        '/opt/freecad-tools',
    ])
elif system == "Linux":
    tnp_decoder_paths.extend([
        os.path.expanduser('~/freecad-tools'),
        os.path.expanduser('~/FreeCAD-Tools'),
        '/usr/local/share/freecad',
        '/opt/freecad-tools',
    ])
elif system == "Windows":
    tnp_decoder_paths.extend([
        os.path.expanduser('~/Documents/FreeCAD'),
        os.path.expanduser('~/Documents/FreeCAD-Tools'),
        os.path.join(os.environ.get('ProgramFiles', ''), 'FreeCAD'),
    ])

# Try to import the decoder
found = False
for path in tnp_decoder_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        found = True
        break

try:
    from tnp_decoder import decode_tnp, decode_tnp_batch, scan_document_for_tnp
    print("[FreeCAD Startup] TNP Decoder loaded successfully")
    print("[FreeCAD Startup] Available commands in Python console:")
    print("    decode_tnp(error_string)")
    print("    decode_tnp_batch(error_text)")
    print("    scan_document_for_tnp()")
except ImportError as e:
    print(f"[FreeCAD Startup] WARNING: Could not load TNP decoder: {e}")
    print("[FreeCAD Startup] Detected OS: {0}".format(system))
    print("[FreeCAD Startup] Macro directory: {0}".format(macro_dir))
    print("[FreeCAD Startup] Make sure tnp_decoder package is in one of these locations:")
    for path in tnp_decoder_paths:
        print(f"    {path}")
    print("[FreeCAD Startup] Expected structure: tnp_decoder/__init__.py with tools/ subdirectory")
