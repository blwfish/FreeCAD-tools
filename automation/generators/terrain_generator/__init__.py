"""Terrain & Scenery Substrate Generator for HO Scale Model Railroads.

Parametric mesh generator that creates geologically-plausible scenery
substrates for CNC machining. Designed for hybrid workflows: procedural
terrain combined with hand-modeled structures.

Usage:
    from terrain_generator import TerrainGenerator

    gen = TerrainGenerator(seed=42)
    result = gen.generate({
        "feature_type": "hillside",
        "dimensions": {"width_inches": 12, "length_inches": 18, "height_inches": 6},
        "geology": {"rock_type": "sandstone", "jointing_angle_primary": 60},
    })
"""

__version__ = "0.1.0"

from .terrain_generator import TerrainGenerator
