# Constraint Parser
# Parse and normalize terrain generation parameters from structured input.
# Phase 1: structured parameters only. Phase 3: natural language prompt parsing.

from typing import Dict, Any, Optional
from .geology_knowledge import GeologyKnowledge


# Default values for optional parameters
DEFAULTS = {
    "feature_type": "hillside",
    "dimensions": {
        "width_inches": 12.0,
        "length_inches": 12.0,
        "height_inches": 6.0,
        "material_depth_inches": 2.0,
    },
    "geometry": {
        "base_elevation": 0.0,
        "peak_elevation": 6.0,
        "slope_angle_dominant": 0.0,
        "slope_angle_variance": 5.0,
    },
    "geology": {
        "rock_type": "sandstone",
        "jointing_angle_primary": 60.0,
        "jointing_spacing": None,  # Derived from rock type if not set
        "jointing_spacing_variance": 0.2,
        "weathering_intensity": 0.3,
    },
    "material": "xps_foam",
    "cnc_constraints": {
        "max_tool_diameter": 0.25,
        "max_depth_per_pass": 0.25,
        "surface_finish": "detail",
    },
    "resolution": 0.05,
    "seed": None,
}


class ConstraintParser:
    """Parse and normalize terrain generation parameters.

    Takes a raw parameter dict (from user or API) and produces a
    fully-resolved specification with defaults filled in and
    rock-type-derived values computed.
    """

    @staticmethod
    def parse(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw input into a complete terrain specification.

        Args:
            raw: User-provided parameter dict (may be partial)

        Returns:
            Fully-resolved specification dict with all defaults filled in
        """
        spec = {}

        # Feature type
        spec["feature_type"] = raw.get("feature_type", DEFAULTS["feature_type"])

        # Dimensions
        raw_dims = raw.get("dimensions", {})
        spec["dimensions"] = {
            "width_inches": raw_dims.get("width_inches", DEFAULTS["dimensions"]["width_inches"]),
            "length_inches": raw_dims.get("length_inches", DEFAULTS["dimensions"]["length_inches"]),
            "height_inches": raw_dims.get("height_inches", DEFAULTS["dimensions"]["height_inches"]),
            "material_depth_inches": raw_dims.get("material_depth_inches", DEFAULTS["dimensions"]["material_depth_inches"]),
        }

        # Geometry
        raw_geom = raw.get("geometry", {})
        spec["geometry"] = {
            "base_elevation": raw_geom.get("base_elevation", DEFAULTS["geometry"]["base_elevation"]),
            "peak_elevation": raw_geom.get("peak_elevation",
                                           raw_geom.get("base_elevation", 0) + spec["dimensions"]["height_inches"]),
            "slope_angle_dominant": raw_geom.get("slope_angle_dominant", DEFAULTS["geometry"]["slope_angle_dominant"]),
            "slope_angle_variance": raw_geom.get("slope_angle_variance", DEFAULTS["geometry"]["slope_angle_variance"]),
        }

        # Geology — resolve rock type defaults
        raw_geo = raw.get("geology", {})
        rock_type_name = raw_geo.get("rock_type", DEFAULTS["geology"]["rock_type"])
        rock_type = GeologyKnowledge.get_rock_type(rock_type_name)

        # Derive jointing parameters from rock type if not explicitly set
        spacing_range = rock_type.jointing_spacing_ho_inches
        default_spacing = (spacing_range[0] + spacing_range[1]) / 2.0

        spec["geology"] = {
            "rock_type": rock_type_name,
            "jointing_angle_primary": raw_geo.get("jointing_angle_primary", rock_type.default_jointing_angle),
            "jointing_angle_secondary": raw_geo.get("jointing_angle_secondary", None),
            "jointing_spacing": raw_geo.get("jointing_spacing", default_spacing),
            "jointing_spacing_variance": raw_geo.get("jointing_spacing_variance",
                                                      DEFAULTS["geology"]["jointing_spacing_variance"]),
            "weathering_intensity": raw_geo.get("weathering_intensity",
                                                 DEFAULTS["geology"]["weathering_intensity"]),
            "erosion_features": raw_geo.get("erosion_features", []),
        }

        # If rock type has secondary jointing and user didn't specify
        if spec["geology"]["jointing_angle_secondary"] is None and rock_type.secondary_angle_range:
            mid = (rock_type.secondary_angle_range[0] + rock_type.secondary_angle_range[1]) / 2.0
            spec["geology"]["jointing_angle_secondary"] = mid

        # Material
        spec["material"] = raw.get("material", DEFAULTS["material"])

        # CNC constraints
        raw_cnc = raw.get("cnc_constraints", {})
        spec["cnc_constraints"] = {
            "max_tool_diameter": raw_cnc.get("max_tool_diameter",
                                              DEFAULTS["cnc_constraints"]["max_tool_diameter"]),
            "max_depth_per_pass": raw_cnc.get("max_depth_per_pass",
                                               DEFAULTS["cnc_constraints"]["max_depth_per_pass"]),
            "surface_finish": raw_cnc.get("surface_finish",
                                           DEFAULTS["cnc_constraints"]["surface_finish"]),
        }

        # Resolution
        spec["resolution"] = raw.get("resolution", DEFAULTS["resolution"])

        # Seed
        spec["seed"] = raw.get("seed", DEFAULTS["seed"])

        # Vegetation zones (pass through)
        spec["vegetation_zones"] = raw.get("vegetation_zones", [])

        # Reference photos (pass through)
        spec["reference_photos"] = raw.get("reference_photos", [])

        # CAD model integration (pass through)
        spec["cad_model"] = raw.get("cad_model", None)

        return spec
