# Noise Functions for Terrain Generation
# Multi-scale noise for natural topographic variation.

import numpy as np
from typing import Optional


class NoiseGenerator:
    """Procedural noise for terrain displacement.

    Uses layered Perlin-style noise (via numpy gradient interpolation)
    to create natural-looking surface variation at multiple scales.
    """

    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.default_rng(seed)

    def _perlin_2d(self, shape: tuple, scale: float, seed_offset: int = 0) -> np.ndarray:
        """Generate 2D Perlin-like noise using gradient interpolation.

        Args:
            shape: (rows, cols) output shape
            scale: Frequency — higher = more detail, lower = broader features
            seed_offset: Added to internal state for independent layers

        Returns:
            2D array of noise values in [-1, 1]
        """
        rows, cols = shape
        # Grid of integer coordinates at the given scale
        freq_r = max(2, int(rows * scale))
        freq_c = max(2, int(cols * scale))

        # Random gradients at grid vertices
        rng = np.random.default_rng(self.rng.integers(0, 2**31) + seed_offset)
        angles = rng.uniform(0, 2 * np.pi, (freq_r + 1, freq_c + 1))
        gradients = np.stack([np.cos(angles), np.sin(angles)], axis=-1)

        # Sample coordinates mapped to gradient grid
        y_coords = np.linspace(0, freq_r - 1, rows)
        x_coords = np.linspace(0, freq_c - 1, cols)
        yy, xx = np.meshgrid(y_coords, x_coords, indexing='ij')

        # Integer and fractional parts
        y0 = np.floor(yy).astype(int)
        x0 = np.floor(xx).astype(int)
        y1 = y0 + 1
        x1 = x0 + 1

        # Fractional position within cell
        fy = yy - y0
        fx = xx - x0

        # Smoothstep interpolation (Perlin fade function)
        uy = fy * fy * (3 - 2 * fy)
        ux = fx * fx * (3 - 2 * fx)

        # Dot products with gradient vectors at each corner
        def dot_grad(gy, gx, dy, dx):
            g = gradients[gy, gx]
            return g[..., 0] * dx + g[..., 1] * dy

        n00 = dot_grad(y0, x0, fy, fx)
        n10 = dot_grad(y1, x0, fy - 1, fx)
        n01 = dot_grad(y0, x1, fy, fx - 1)
        n11 = dot_grad(y1, x1, fy - 1, fx - 1)

        # Bilinear interpolation
        nx0 = n00 + ux * (n01 - n00)
        nx1 = n10 + ux * (n11 - n10)
        result = nx0 + uy * (nx1 - nx0)

        return result

    def fractal_brownian_motion(
        self,
        shape: tuple,
        octaves: int = 4,
        base_scale: float = 0.05,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
    ) -> np.ndarray:
        """Generate fractal Brownian motion (fBm) noise.

        Layers multiple octaves of noise at increasing frequency and
        decreasing amplitude for natural-looking terrain variation.

        Args:
            shape: (rows, cols) output dimensions
            octaves: Number of noise layers
            base_scale: Frequency of the lowest octave
            persistence: Amplitude decay per octave (0-1)
            lacunarity: Frequency multiplier per octave

        Returns:
            2D array normalized to [0, 1]
        """
        result = np.zeros(shape)
        amplitude = 1.0
        scale = base_scale
        max_amp = 0.0

        for i in range(octaves):
            result += amplitude * self._perlin_2d(shape, scale, seed_offset=i * 1000)
            max_amp += amplitude
            amplitude *= persistence
            scale *= lacunarity

        # Normalize to [0, 1]
        result = (result / max_amp + 1.0) / 2.0
        return np.clip(result, 0.0, 1.0)

    def ridge_noise(
        self,
        shape: tuple,
        octaves: int = 4,
        base_scale: float = 0.05,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
        sharpness: float = 2.0,
    ) -> np.ndarray:
        """Generate ridged multifractal noise.

        Similar to fBm but produces sharp ridges and valleys,
        useful for rocky/mountainous terrain features.

        Args:
            shape: (rows, cols) output dimensions
            octaves: Number of noise layers
            base_scale: Frequency of the lowest octave
            persistence: Amplitude decay per octave
            lacunarity: Frequency multiplier per octave
            sharpness: Ridge sharpness exponent (higher = sharper)

        Returns:
            2D array normalized to [0, 1]
        """
        result = np.zeros(shape)
        amplitude = 1.0
        scale = base_scale
        max_amp = 0.0

        for i in range(octaves):
            noise = self._perlin_2d(shape, scale, seed_offset=i * 1000 + 500)
            # Absolute value creates ridges, invert so ridges are high
            ridge = 1.0 - np.abs(noise)
            ridge = ridge ** sharpness
            result += amplitude * ridge
            max_amp += amplitude
            amplitude *= persistence
            scale *= lacunarity

        result /= max_amp
        return np.clip(result, 0.0, 1.0)
