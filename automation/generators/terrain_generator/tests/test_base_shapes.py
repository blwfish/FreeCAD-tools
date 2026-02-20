# Tests for base shape generation

import numpy as np
import pytest
from terrain_generator.geometry.noise_functions import NoiseGenerator
from terrain_generator.geometry.base_shapes import BaseShapeGenerator


@pytest.fixture
def shapes():
    noise = NoiseGenerator(seed=42)
    return BaseShapeGenerator(noise)


class TestHillside:
    def test_basic_generation(self, shapes):
        hm, res = shapes.hillside(
            width_inches=6.0, length_inches=6.0,
            base_elevation=0.0, peak_elevation=4.0,
            resolution=0.1,
        )
        assert hm.shape[0] > 0
        assert hm.shape[1] > 0
        assert res == 0.1

    def test_elevation_range(self, shapes):
        hm, _ = shapes.hillside(
            width_inches=6.0, length_inches=6.0,
            base_elevation=2.0, peak_elevation=8.0,
            resolution=0.1,
        )
        assert np.min(hm) >= 2.0
        assert np.max(hm) <= 8.0

    def test_slope_direction(self, shapes):
        """Slope should increase along the dominant direction."""
        hm, _ = shapes.hillside(
            width_inches=6.0, length_inches=12.0,
            base_elevation=0.0, peak_elevation=6.0,
            slope_direction=0.0,  # +Y direction
            resolution=0.2,
        )
        # Average of first few rows should be lower than last few rows
        avg_front = np.mean(hm[:5, :])
        avg_back = np.mean(hm[-5:, :])
        assert avg_back > avg_front

    def test_resolution_affects_grid_size(self, shapes):
        hm1, _ = shapes.hillside(6, 6, 0, 4, resolution=0.1)
        hm2, _ = shapes.hillside(6, 6, 0, 4, resolution=0.2)
        assert hm1.shape[0] > hm2.shape[0]
        assert hm1.shape[1] > hm2.shape[1]

    def test_seed_reproducibility(self):
        """Same seed should produce identical output."""
        noise1 = NoiseGenerator(seed=123)
        noise2 = NoiseGenerator(seed=123)
        s1 = BaseShapeGenerator(noise1)
        s2 = BaseShapeGenerator(noise2)

        hm1, _ = s1.hillside(6, 6, 0, 4, resolution=0.2)
        hm2, _ = s2.hillside(6, 6, 0, 4, resolution=0.2)
        np.testing.assert_array_equal(hm1, hm2)


class TestRiverbank:
    def test_basic_generation(self, shapes):
        hm, res = shapes.riverbank(
            width_inches=6.0, height_inches=4.0, resolution=0.1
        )
        assert hm.shape[0] > 0
        assert hm.shape[1] > 0

    def test_channel_lower_than_banks(self, shapes):
        hm, _ = shapes.riverbank(
            width_inches=8.0, height_inches=4.0, resolution=0.1
        )
        center_col = hm.shape[1] // 2
        edge_col = 0
        # Center (channel) should be lower than edge (bank)
        assert np.mean(hm[:, center_col]) < np.mean(hm[:, edge_col])


class TestCliff:
    def test_basic_generation(self, shapes):
        hm, res = shapes.cliff(
            width_inches=6.0, height_inches=6.0, resolution=0.1
        )
        assert hm.shape[0] > 0
        assert hm.shape[1] > 0

    def test_height_range(self, shapes):
        hm, _ = shapes.cliff(
            width_inches=6.0, height_inches=6.0, resolution=0.1
        )
        assert np.min(hm) >= 0
        assert np.max(hm) <= 6.0 * 1.15  # Allow some noise overshoot


class TestValley:
    def test_basic_generation(self, shapes):
        hm, _ = shapes.valley(
            width_inches=8.0, length_inches=8.0,
            depth_inches=3.0, resolution=0.1
        )
        assert hm.shape[0] > 0
        assert hm.shape[1] > 0

    def test_center_lower_than_edges(self, shapes):
        hm, _ = shapes.valley(
            width_inches=8.0, length_inches=8.0,
            depth_inches=3.0, valley_shape="v", resolution=0.1
        )
        center_col = hm.shape[1] // 2
        avg_center = np.mean(hm[:, center_col])
        avg_edge = np.mean(hm[:, 0])
        assert avg_center < avg_edge

    def test_u_vs_v_shape(self, shapes):
        hm_v, _ = shapes.valley(8, 8, 3, valley_shape="v", resolution=0.1)
        hm_u, _ = shapes.valley(8, 8, 3, valley_shape="u", resolution=0.1)
        # U-shaped should have flatter bottom (lower std in center)
        center = hm_v.shape[1] // 2
        band = 3
        std_v = np.std(hm_v[:, center-band:center+band])
        std_u = np.std(hm_u[:, center-band:center+band])
        assert std_u < std_v
