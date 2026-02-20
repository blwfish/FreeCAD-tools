# Base Shape Generation
# Creates initial heightmap surfaces for different terrain feature types.

import numpy as np
from typing import Optional, Tuple
from .noise_functions import NoiseGenerator


class BaseShapeGenerator:
    """Generate base heightmap surfaces for terrain features.

    All methods return 2D numpy arrays (heightmaps) with values in inches,
    at the specified grid resolution. The heightmap represents Z elevation
    at each (X, Y) grid point.
    """

    def __init__(self, noise: NoiseGenerator):
        self.noise = noise

    def hillside(
        self,
        width_inches: float,
        length_inches: float,
        base_elevation: float,
        peak_elevation: float,
        slope_direction: float = 0.0,
        slope_variance: float = 5.0,
        resolution: float = 0.05,
    ) -> Tuple[np.ndarray, float]:
        """Generate a hillside slope.

        Args:
            width_inches: X dimension (across slope)
            length_inches: Y dimension (along slope)
            base_elevation: Lowest Z value (inches)
            peak_elevation: Highest Z value (inches)
            slope_direction: Primary slope direction in degrees (0 = +Y)
            slope_variance: Random variation in slope angle (+/- degrees)
            resolution: Grid spacing in inches

        Returns:
            (heightmap, resolution) — 2D array of Z values, grid spacing
        """
        cols = max(4, int(width_inches / resolution))
        rows = max(4, int(length_inches / resolution))

        # Normalized grid [0, 1]
        y_norm = np.linspace(0, 1, rows)
        x_norm = np.linspace(0, 1, cols)
        yy, xx = np.meshgrid(y_norm, x_norm, indexing='ij')

        # Slope direction as unit vector
        angle_rad = np.radians(slope_direction)
        # Project grid onto slope direction
        slope_t = xx * np.sin(angle_rad) + yy * np.cos(angle_rad)

        # Base slope: linear ramp from base to peak
        relief = peak_elevation - base_elevation
        heightmap = base_elevation + slope_t * relief

        # Add broad topographic variation (fBm noise)
        noise_broad = self.noise.fractal_brownian_motion(
            (rows, cols), octaves=3, base_scale=0.03, persistence=0.5
        )
        # Scale noise to a fraction of total relief
        heightmap += (noise_broad - 0.5) * relief * 0.15

        # Add finer variation
        noise_fine = self.noise.fractal_brownian_motion(
            (rows, cols), octaves=4, base_scale=0.1, persistence=0.4
        )
        heightmap += (noise_fine - 0.5) * relief * 0.05

        # Clamp to valid range
        heightmap = np.clip(heightmap, base_elevation, peak_elevation)

        return heightmap, resolution

    def riverbank(
        self,
        width_inches: float,
        height_inches: float,
        left_profile: str = "undercut",
        right_profile: str = "slope",
        right_slope_ratio: float = 2.0,
        water_level: float = 0.5,
        resolution: float = 0.05,
    ) -> Tuple[np.ndarray, float]:
        """Generate a riverbank cross-section extruded along length.

        Args:
            width_inches: X dimension (bank to bank)
            height_inches: Maximum Z relief
            left_profile: "undercut" or "slope"
            right_profile: "undercut" or "slope"
            right_slope_ratio: Rise:run for sloped side
            water_level: Water surface elevation (inches from base)
            resolution: Grid spacing in inches

        Returns:
            (heightmap, resolution)
        """
        cols = max(4, int(width_inches / resolution))
        rows = max(4, int(width_inches / resolution))  # square-ish section

        x_norm = np.linspace(0, 1, cols)
        y_norm = np.linspace(0, 1, rows)
        yy, xx = np.meshgrid(y_norm, x_norm, indexing='ij')

        heightmap = np.full((rows, cols), water_level)

        # Channel profile: V or U shape in the middle
        center = 0.5
        channel_width = 0.3  # fraction of total width

        for j in range(cols):
            x = x_norm[j]
            if x < center - channel_width / 2:
                # Left bank
                dist_from_channel = (center - channel_width / 2) - x
                bank_width = center - channel_width / 2
                if bank_width > 0:
                    t = dist_from_channel / bank_width
                    if left_profile == "undercut":
                        # Concave profile (undercut)
                        profile = t ** 0.6
                    else:
                        profile = t
                    heightmap[:, j] = water_level + profile * (height_inches - water_level)
            elif x > center + channel_width / 2:
                # Right bank
                dist_from_channel = x - (center + channel_width / 2)
                bank_width = 1.0 - (center + channel_width / 2)
                if bank_width > 0:
                    t = dist_from_channel / bank_width
                    if right_profile == "undercut":
                        profile = t ** 0.6
                    else:
                        # Linear slope
                        profile = t
                    heightmap[:, j] = water_level + profile * (height_inches - water_level)
            else:
                # Channel bottom
                heightmap[:, j] = water_level * 0.3

        # Add noise variation along the length (Y direction)
        noise = self.noise.fractal_brownian_motion(
            (rows, cols), octaves=3, base_scale=0.05, persistence=0.4
        )
        heightmap += (noise - 0.5) * height_inches * 0.08

        heightmap = np.clip(heightmap, 0, height_inches)
        return heightmap, resolution

    def cliff(
        self,
        width_inches: float,
        height_inches: float,
        cliff_angle: float = 80.0,
        overhang_depth: float = 0.0,
        talus_angle: float = 35.0,
        resolution: float = 0.05,
    ) -> Tuple[np.ndarray, float]:
        """Generate a cliff face with optional talus slope at base.

        Args:
            width_inches: X dimension (along cliff face)
            height_inches: Maximum Z relief
            cliff_angle: Cliff face angle from horizontal (degrees)
            overhang_depth: Depth of overhang at top (inches, 0 = none)
            talus_angle: Angle of rubble slope at base (degrees)
            resolution: Grid spacing in inches

        Returns:
            (heightmap, resolution)
        """
        cols = max(4, int(width_inches / resolution))
        # Depth determined by cliff geometry
        depth_inches = height_inches / max(np.tan(np.radians(min(cliff_angle, 89))), 0.1)
        depth_inches = max(depth_inches, 2.0)
        rows = max(4, int(depth_inches / resolution))

        y_norm = np.linspace(0, 1, rows)
        x_norm = np.linspace(0, 1, cols)
        yy, xx = np.meshgrid(y_norm, x_norm, indexing='ij')

        # Cliff profile: steep rise
        cliff_slope = np.tan(np.radians(min(cliff_angle, 89)))
        talus_slope = np.tan(np.radians(talus_angle))

        # Transition point between talus and cliff
        talus_height = height_inches * 0.25
        talus_run = talus_height / talus_slope if talus_slope > 0 else 0
        talus_frac = talus_run / depth_inches

        heightmap = np.zeros((rows, cols))
        for i in range(rows):
            y = y_norm[i]
            if y < talus_frac:
                # Talus slope
                heightmap[i, :] = (y / talus_frac) * talus_height
            else:
                # Cliff face
                t = (y - talus_frac) / (1.0 - talus_frac) if talus_frac < 1.0 else 0
                heightmap[i, :] = talus_height + t * (height_inches - talus_height)

        # Add noise for rough cliff texture
        noise = self.noise.ridge_noise(
            (rows, cols), octaves=4, base_scale=0.08, persistence=0.5, sharpness=2.0
        )
        heightmap += (noise - 0.5) * height_inches * 0.1

        heightmap = np.clip(heightmap, 0, height_inches)
        return heightmap, resolution

    def valley(
        self,
        width_inches: float,
        length_inches: float,
        depth_inches: float,
        valley_shape: str = "v",
        resolution: float = 0.05,
    ) -> Tuple[np.ndarray, float]:
        """Generate a valley profile.

        Args:
            width_inches: X dimension (across valley)
            length_inches: Y dimension (along valley)
            depth_inches: Valley depth from rim to floor
            valley_shape: "v" for V-shaped, "u" for U-shaped
            resolution: Grid spacing

        Returns:
            (heightmap, resolution)
        """
        cols = max(4, int(width_inches / resolution))
        rows = max(4, int(length_inches / resolution))

        x_norm = np.linspace(0, 1, cols)
        y_norm = np.linspace(0, 1, rows)
        yy, xx = np.meshgrid(y_norm, x_norm, indexing='ij')

        # Distance from center line (normalized 0-1)
        dist = np.abs(xx - 0.5) * 2.0  # 0 at center, 1 at edges

        if valley_shape == "u":
            # U-shaped: flat bottom, steep sides
            safe_dist = np.maximum(dist - 0.3, 0) / 0.7
            profile = np.where(dist < 0.3, 0, safe_dist ** 0.8)
        else:
            # V-shaped: linear sides
            profile = dist

        heightmap = profile * depth_inches

        # Add noise
        noise = self.noise.fractal_brownian_motion(
            (rows, cols), octaves=3, base_scale=0.04, persistence=0.45
        )
        heightmap += (noise - 0.5) * depth_inches * 0.1

        heightmap = np.clip(heightmap, 0, depth_inches)
        return heightmap, resolution
