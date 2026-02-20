# Terrain Generator - Main Entry Point
# Orchestrates constraint parsing, validation, mesh generation, and export.

import numpy as np
import time
from typing import Dict, Any, Optional

from .constraints.parser import ConstraintParser
from .constraints.validator import ConstraintValidator
from .constraints.geology_knowledge import GeologyKnowledge
from .geometry.noise_functions import NoiseGenerator
from .geometry.base_shapes import BaseShapeGenerator
from .geometry.jointing import JointingGenerator
from .geometry.erosion import ErosionGenerator
from .geometry.mesh_utils import MeshUtils
from .io.mesh_export import MeshExporter


class TerrainGenerator:
    """Main terrain generation engine.

    Orchestrates the full pipeline:
    1. Parse and validate constraints
    2. Generate base terrain shape
    3. Apply jointing patterns
    4. Add erosion features
    5. Apply weathering
    6. Convert to mesh
    7. Validate and export

    Usage:
        gen = TerrainGenerator(seed=42)
        result = gen.generate(params)
        # result contains heightmap, mesh data, and export info
    """

    def __init__(self, seed: Optional[int] = None):
        """Initialize the terrain generator.

        Args:
            seed: Random seed for reproducible output. If None, random.
        """
        self.seed = seed

    def generate(
        self,
        params: Dict[str, Any],
        export_path: Optional[str] = None,
        export_format: str = "stl",
    ) -> Dict[str, Any]:
        """Generate terrain from parameters.

        Args:
            params: Raw terrain parameters (see ConstraintParser for schema)
            export_path: If provided, export mesh to this path
            export_format: "stl" or "obj"

        Returns:
            Dict with:
            - spec: resolved specification
            - validation: constraint validation results
            - heightmap: 2D numpy array of elevations
            - resolution: grid spacing in inches
            - vertices: Nx3 mesh vertices
            - faces: Mx3 mesh face indices
            - mesh_stats: vertex/face counts, bounding box
            - export: export info (if export_path provided)
            - generation_time_sec: total generation time
        """
        start_time = time.time()

        # 1. Parse constraints
        try:
            spec = ConstraintParser.parse(params)
        except (ValueError, KeyError) as e:
            return {
                "spec": params,
                "validation": {"valid": False, "errors": [str(e)], "warnings": []},
                "error": f"Parameter error: {e}",
            }

        # Override seed if specified in params but not constructor
        seed = spec.get("seed") or self.seed
        if seed is not None:
            spec["seed"] = seed

        # 2. Validate
        validation = ConstraintValidator.validate(spec)
        if not validation["valid"]:
            return {
                "spec": spec,
                "validation": validation,
                "error": "Validation failed: " + "; ".join(validation["errors"]),
            }

        # 3. Initialize generators with seed
        rng = np.random.default_rng(seed)
        noise = NoiseGenerator(seed=seed)
        shapes = BaseShapeGenerator(noise)
        jointing = JointingGenerator(rng=rng)
        erosion_gen = ErosionGenerator(rng=rng)

        dims = spec["dimensions"]
        geom = spec["geometry"]
        geo = spec["geology"]
        resolution = spec["resolution"]

        # 4. Generate base shape
        feature_type = spec["feature_type"]
        heightmap = self._generate_base_shape(
            shapes, feature_type, dims, geom, resolution
        )

        # 5. Apply jointing
        sec_spacing = None
        if geo.get("jointing_angle_secondary") is not None:
            sec_spacing = geo["jointing_spacing"] * 1.5

        heightmap = jointing.apply_jointing(
            heightmap,
            resolution,
            primary_angle=geo["jointing_angle_primary"],
            primary_spacing=geo["jointing_spacing"],
            spacing_variance=geo["jointing_spacing_variance"],
            secondary_angle=geo.get("jointing_angle_secondary"),
            secondary_spacing=sec_spacing,
        )

        # 6. Apply erosion features
        erosion_features = geo.get("erosion_features", [])
        if "drainage_lines" in erosion_features:
            heightmap = erosion_gen.add_drainage_lines(
                heightmap, resolution, num_lines=3, depth=0.05
            )
        if "undercut_banks" in erosion_features:
            heightmap = erosion_gen.add_undercut(
                heightmap, resolution, side="left",
                undercut_depth=0.3, undercut_height=0.5,
            )

        # 7. Apply weathering roughness
        weathering = geo.get("weathering_intensity", 0.3)
        if weathering > 0:
            heightmap = jointing.generate_weathering_roughness(
                heightmap, resolution, intensity=weathering, rng=rng
            )

        # 8. Convert heightmap to mesh
        base_thickness = dims.get("material_depth_inches", 2.0) * 0.1  # 10% base
        base_thickness = max(base_thickness, 0.1)
        vertices, faces = MeshUtils.heightmap_to_mesh(
            heightmap, resolution, base_thickness=base_thickness, closed=True
        )

        # 9. Validate mesh
        mesh_stats = MeshUtils.validate_mesh(vertices, faces)

        # 10. Export if requested
        export_info = None
        if export_path:
            export_info = MeshExporter.export(
                vertices, faces, export_path, spec,
                format=export_format,
            )

        generation_time = time.time() - start_time

        return {
            "spec": spec,
            "validation": validation,
            "heightmap": heightmap,
            "resolution": resolution,
            "vertices": vertices,
            "faces": faces,
            "mesh_stats": mesh_stats,
            "export": export_info,
            "generation_time_sec": generation_time,
        }

    def _generate_base_shape(
        self,
        shapes: BaseShapeGenerator,
        feature_type: str,
        dims: Dict[str, Any],
        geom: Dict[str, Any],
        resolution: float,
    ) -> np.ndarray:
        """Dispatch to the appropriate base shape generator."""
        width = dims["width_inches"]
        length = dims["length_inches"]
        height = dims["height_inches"]
        base_elev = geom["base_elevation"]
        peak_elev = geom["peak_elevation"]

        if feature_type == "hillside":
            heightmap, _ = shapes.hillside(
                width_inches=width,
                length_inches=length,
                base_elevation=base_elev,
                peak_elevation=peak_elev,
                slope_direction=geom.get("slope_angle_dominant", 0),
                slope_variance=geom.get("slope_angle_variance", 5),
                resolution=resolution,
            )
        elif feature_type == "riverbank":
            heightmap, _ = shapes.riverbank(
                width_inches=width,
                height_inches=height,
                resolution=resolution,
            )
        elif feature_type == "cliff":
            heightmap, _ = shapes.cliff(
                width_inches=width,
                height_inches=height,
                cliff_angle=geom.get("slope_angle_dominant", 80),
                resolution=resolution,
            )
        elif feature_type == "valley":
            heightmap, _ = shapes.valley(
                width_inches=width,
                length_inches=length,
                depth_inches=height,
                resolution=resolution,
            )
        else:
            # Default to hillside
            heightmap, _ = shapes.hillside(
                width_inches=width,
                length_inches=length,
                base_elevation=base_elev,
                peak_elevation=peak_elev,
                resolution=resolution,
            )

        return heightmap

    def generate_preview(
        self,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate a quick low-resolution preview for iteration.

        Same as generate() but at 4x coarser resolution and no export.
        """
        preview_params = dict(params)
        current_res = preview_params.get("resolution", 0.05)
        preview_params["resolution"] = current_res * 4
        return self.generate(preview_params)
