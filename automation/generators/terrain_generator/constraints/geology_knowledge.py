# Geology Knowledge Base
# Rock type properties, jointing logic, and HO scale parameters.
# Data sourced from Appalachian/Virginia C&O corridor geology.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math

HO_SCALE = 87.1  # 1:87.1


@dataclass
class RockType:
    """Properties of a rock type at prototype and HO scale."""
    name: str
    # Jointing
    primary_jointing: str              # e.g. "bedding + vertical"
    jointing_angle_range: Tuple[float, float]  # degrees
    jointing_spacing_proto_ft: Tuple[float, float]  # prototype feet
    secondary_jointing: Optional[str] = None
    secondary_angle_range: Optional[Tuple[float, float]] = None
    # Weathering
    weathering_character: str = ""
    # CNC
    min_joint_depth_inches: float = 0.02  # minimum CNC-cuttable joint depth
    # Scale
    typical_compression: float = 2.0  # layout compression factor

    @property
    def jointing_spacing_ho_inches(self) -> Tuple[float, float]:
        """Jointing spacing converted to HO scale inches."""
        return (
            self.jointing_spacing_proto_ft[0] * 12.0 / HO_SCALE,
            self.jointing_spacing_proto_ft[1] * 12.0 / HO_SCALE,
        )

    @property
    def default_jointing_angle(self) -> float:
        """Middle of the jointing angle range."""
        return (self.jointing_angle_range[0] + self.jointing_angle_range[1]) / 2.0


# C&O Virginia corridor rock types
ROCK_TYPES: Dict[str, RockType] = {
    "sandstone": RockType(
        name="sandstone",
        primary_jointing="bedding + vertical",
        jointing_angle_range=(45.0, 75.0),
        jointing_spacing_proto_ft=(6.0, 18.0),
        weathering_character="Flaking, differential erosion",
    ),
    "shale": RockType(
        name="shale",
        primary_jointing="thin bedding",
        jointing_angle_range=(30.0, 60.0),
        jointing_spacing_proto_ft=(0.5, 3.0),
        weathering_character="Spalling, slope failures",
    ),
    "limestone": RockType(
        name="limestone",
        primary_jointing="vertical grid",
        jointing_angle_range=(60.0, 90.0),
        jointing_spacing_proto_ft=(3.0, 10.0),
        secondary_jointing="horizontal bedding",
        secondary_angle_range=(0.0, 15.0),
        weathering_character="Solution weathering, caves",
    ),
    "granite": RockType(
        name="granite",
        primary_jointing="orthogonal",
        jointing_angle_range=(70.0, 90.0),
        jointing_spacing_proto_ft=(10.0, 30.0),
        weathering_character="Rounding, corestones",
    ),
    "schist": RockType(
        name="schist",
        primary_jointing="foliation planes",
        jointing_angle_range=(20.0, 70.0),
        jointing_spacing_proto_ft=(1.0, 6.0),
        weathering_character="Platy fracture, differential erosion",
    ),
}

# CNC material properties
MATERIAL_PROPERTIES = {
    "xps_foam": {
        "name": "XPS Foam",
        "max_depth_per_pass_inches": 0.25,
        "min_tool_diameter_inches": 1.0 / 16.0,  # 1/16"
        "feed_rate_ipm": 40,
        "supports_engraving": True,
    },
    "mdf": {
        "name": "MDF",
        "max_depth_per_pass_inches": 0.125,
        "min_tool_diameter_inches": 1.0 / 16.0,
        "feed_rate_ipm": 20,
        "supports_engraving": True,
    },
    "plywood": {
        "name": "Plywood",
        "max_depth_per_pass_inches": 0.1,
        "min_tool_diameter_inches": 1.0 / 8.0,
        "feed_rate_ipm": 15,
        "supports_engraving": False,
    },
}


class GeologyKnowledge:
    """Domain knowledge about geology for terrain generation."""

    @staticmethod
    def get_rock_type(name: str) -> RockType:
        """Look up a rock type by name."""
        key = name.lower().strip()
        if key not in ROCK_TYPES:
            available = ", ".join(sorted(ROCK_TYPES.keys()))
            raise ValueError(f"Unknown rock type '{name}'. Available: {available}")
        return ROCK_TYPES[key]

    @staticmethod
    def list_rock_types() -> List[str]:
        return sorted(ROCK_TYPES.keys())

    @staticmethod
    def get_material(name: str) -> dict:
        key = name.lower().strip().replace(" ", "_")
        if key not in MATERIAL_PROPERTIES:
            available = ", ".join(sorted(MATERIAL_PROPERTIES.keys()))
            raise ValueError(f"Unknown material '{name}'. Available: {available}")
        return MATERIAL_PROPERTIES[key]

    @staticmethod
    def validate_jointing_angle(rock_type: str, angle: float) -> Optional[str]:
        """Check if a jointing angle is geologically plausible for the rock type.
        Returns warning string if implausible, None if OK."""
        rt = GeologyKnowledge.get_rock_type(rock_type)
        lo, hi = rt.jointing_angle_range
        if angle < lo - 10 or angle > hi + 10:
            return (f"Jointing angle {angle}° is outside plausible range "
                    f"({lo}°–{hi}°) for {rock_type}. Consider adjusting.")
        return None

    @staticmethod
    def proto_to_ho(proto_feet: float) -> float:
        """Convert prototype feet to HO scale inches."""
        return proto_feet * 12.0 / HO_SCALE

    @staticmethod
    def ho_to_proto(ho_inches: float) -> float:
        """Convert HO scale inches to prototype feet."""
        return ho_inches * HO_SCALE / 12.0
