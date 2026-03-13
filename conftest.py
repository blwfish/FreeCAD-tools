import sys
import os

# Add each generator directory to sys.path so tests can use bare-name imports
# (e.g. `from brick_geometry import BrickGeometry` instead of relative imports)
_root = os.path.dirname(__file__)
for _gen in [
    "automation/generators/bead_board_generator",
    "automation/generators/board_batten_generator",
    "automation/generators/brick_generator",
    "automation/generators/clapboard_generator",
    "automation/generators/radial_brick",
    "automation/generators/roof_seam_generator",
    "automation/generators/shingle",
    "automation/generators/smart_trim",
    "automation/generators/station_sign",
    "automation/generators/terrain_generator",
]:
    _path = os.path.join(_root, _gen)
    if _path not in sys.path:
        sys.path.insert(0, _path)
