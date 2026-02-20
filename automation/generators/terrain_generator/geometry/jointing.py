# Jointing Pattern Generation
# Overlays geological joint patterns onto heightmaps.

import numpy as np
from typing import Optional, Tuple


class JointingGenerator:
    """Generate and apply geological jointing patterns to heightmaps.

    Joints are fractures in rock that create the characteristic patterns
    visible on cliff faces and rock cuts. This generator creates geometric
    joint patterns at specified angles and spacings, then carves them
    into the heightmap as shallow grooves.
    """

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng()

    def apply_jointing(
        self,
        heightmap: np.ndarray,
        resolution: float,
        primary_angle: float,
        primary_spacing: float,
        primary_depth: float = 0.03,
        primary_width: float = 0.02,
        spacing_variance: float = 0.2,
        secondary_angle: Optional[float] = None,
        secondary_spacing: Optional[float] = None,
        secondary_depth: Optional[float] = None,
        secondary_width: Optional[float] = None,
    ) -> np.ndarray:
        """Apply jointing pattern to a heightmap.

        Args:
            heightmap: 2D elevation array (modified in place and returned)
            resolution: Grid spacing in inches
            primary_angle: Primary joint set angle in degrees (from horizontal)
            primary_spacing: Distance between joints in inches
            primary_depth: Depth of joint grooves in inches
            primary_width: Width of joint grooves in inches
            spacing_variance: Random variation in spacing (fraction, 0-1)
            secondary_angle: Optional second joint set angle
            secondary_spacing: Spacing for secondary joints
            secondary_depth: Depth for secondary joints (default: 0.7 * primary)
            secondary_width: Width for secondary joints (default: same as primary)

        Returns:
            Modified heightmap with joint grooves carved in
        """
        result = heightmap.copy()

        # Apply primary joint set
        self._carve_joint_set(
            result, resolution,
            angle=primary_angle,
            spacing=primary_spacing,
            depth=primary_depth,
            width=primary_width,
            spacing_variance=spacing_variance,
        )

        # Apply secondary joint set if specified
        if secondary_angle is not None:
            sec_spacing = secondary_spacing or primary_spacing * 1.5
            sec_depth = secondary_depth or primary_depth * 0.7
            sec_width = secondary_width or primary_width
            self._carve_joint_set(
                result, resolution,
                angle=secondary_angle,
                spacing=sec_spacing,
                depth=sec_depth,
                width=sec_width,
                spacing_variance=spacing_variance,
            )

        return result

    def _carve_joint_set(
        self,
        heightmap: np.ndarray,
        resolution: float,
        angle: float,
        spacing: float,
        depth: float,
        width: float,
        spacing_variance: float,
    ):
        """Carve a single set of parallel joints into the heightmap.

        Joints are parallel lines at the specified angle, spaced at
        the specified interval with random variance.
        """
        rows, cols = heightmap.shape
        height_inches = rows * resolution
        width_inches = cols * resolution

        # Direction perpendicular to joint lines (spacing direction)
        angle_rad = np.radians(angle)
        # Joint lines run at `angle` from horizontal (X axis)
        # Normal to joint lines:
        nx = np.cos(angle_rad)
        ny = np.sin(angle_rad)

        # Maximum extent along the normal direction
        max_extent = abs(nx) * width_inches + abs(ny) * height_inches

        # Width of joint groove in grid cells
        width_cells = max(1, int(width / resolution))
        half_width = width / 2.0

        # Generate joint positions along the normal direction
        pos = 0.0
        joint_positions = []
        while pos < max_extent:
            joint_positions.append(pos)
            variance = 1.0 + self.rng.uniform(-spacing_variance, spacing_variance)
            pos += spacing * max(variance, 0.3)

        # Create coordinate grids
        y_coords = np.arange(rows) * resolution
        x_coords = np.arange(cols) * resolution
        yy, xx = np.meshgrid(y_coords, x_coords, indexing='ij')

        # Project each pixel onto the joint normal direction
        proj = xx * nx + yy * ny

        # For each joint, carve a groove
        for jpos in joint_positions:
            # Distance from this joint line
            dist = np.abs(proj - jpos)

            # Groove profile: triangular falloff
            mask = dist < half_width
            if not np.any(mask):
                continue

            # Depth tapers linearly from center to edge
            groove_depth = depth * (1.0 - dist / half_width)
            groove_depth = np.where(mask, groove_depth, 0.0)

            # Add slight random depth variation per joint
            joint_depth_factor = self.rng.uniform(0.6, 1.0)
            groove_depth *= joint_depth_factor

            heightmap -= groove_depth

    def generate_weathering_roughness(
        self,
        heightmap: np.ndarray,
        resolution: float,
        intensity: float = 0.5,
        rng: Optional[np.random.Generator] = None,
    ) -> np.ndarray:
        """Add small-scale surface roughness to simulate weathering.

        Args:
            heightmap: 2D elevation array
            resolution: Grid spacing in inches
            intensity: 0.0 (fresh) to 1.0 (heavily weathered)
            rng: Random generator

        Returns:
            Modified heightmap with weathering roughness
        """
        if rng is None:
            rng = self.rng

        rows, cols = heightmap.shape
        result = heightmap.copy()

        # Small-scale noise for surface texture
        roughness = rng.normal(0, 1, (rows, cols))

        # Smooth slightly to avoid single-pixel spikes
        from scipy.ndimage import gaussian_filter
        roughness = gaussian_filter(roughness, sigma=1.5)

        # Scale: intensity 1.0 → ~0.01" roughness (visible at HO scale)
        max_roughness = 0.015 * intensity
        roughness = roughness / np.max(np.abs(roughness)) * max_roughness

        result += roughness
        return result
