# Tests for jointing pattern generation

import numpy as np
import pytest
from terrain_generator.geometry.jointing import JointingGenerator


@pytest.fixture
def jointing():
    return JointingGenerator(rng=np.random.default_rng(42))


class TestJointing:
    def test_joints_reduce_surface(self, jointing):
        """Jointing should carve grooves, reducing heightmap values."""
        hm = np.ones((100, 100)) * 5.0
        result = jointing.apply_jointing(
            hm, resolution=0.1,
            primary_angle=60.0, primary_spacing=1.0,
            primary_depth=0.05, primary_width=0.03,
        )
        # Some cells should be lower (carved)
        assert np.min(result) < 5.0
        # But grooves shouldn't be deeper than the original depth
        assert np.min(result) >= 5.0 - 0.05 - 0.01  # small tolerance

    def test_secondary_joints(self, jointing):
        """Secondary joints should add additional grooves."""
        hm = np.ones((100, 100)) * 5.0
        result_primary = jointing.apply_jointing(
            hm, resolution=0.1,
            primary_angle=60.0, primary_spacing=1.0,
            primary_depth=0.05,
        )
        result_both = jointing.apply_jointing(
            hm, resolution=0.1,
            primary_angle=60.0, primary_spacing=1.0,
            primary_depth=0.05,
            secondary_angle=90.0, secondary_spacing=1.5,
        )
        # More grooves → more cells below 5.0
        primary_carved = np.sum(result_primary < 4.99)
        both_carved = np.sum(result_both < 4.99)
        assert both_carved >= primary_carved

    def test_spacing_affects_groove_count(self, jointing):
        """Tighter spacing should produce more grooves."""
        hm = np.ones((100, 100)) * 5.0
        result_tight = jointing.apply_jointing(
            hm, resolution=0.1,
            primary_angle=45.0, primary_spacing=0.5,
            primary_depth=0.03,
        )
        result_wide = jointing.apply_jointing(
            hm, resolution=0.1,
            primary_angle=45.0, primary_spacing=2.0,
            primary_depth=0.03,
        )
        tight_carved = np.sum(result_tight < 4.99)
        wide_carved = np.sum(result_wide < 4.99)
        assert tight_carved > wide_carved

    def test_output_shape_preserved(self, jointing):
        """Jointing should not change array shape."""
        hm = np.ones((80, 120)) * 3.0
        result = jointing.apply_jointing(
            hm, resolution=0.1,
            primary_angle=60.0, primary_spacing=1.0,
        )
        assert result.shape == hm.shape


class TestWeatheringRoughness:
    def test_adds_variation(self, jointing):
        hm = np.ones((100, 100)) * 5.0
        result = jointing.generate_weathering_roughness(
            hm, resolution=0.1, intensity=0.5
        )
        # Should not be perfectly flat anymore
        assert np.std(result) > 0

    def test_intensity_scales(self, jointing):
        hm = np.ones((100, 100)) * 5.0
        low = jointing.generate_weathering_roughness(hm, 0.1, intensity=0.1)
        high = jointing.generate_weathering_roughness(hm, 0.1, intensity=1.0)
        assert np.std(high) > np.std(low)

    def test_zero_intensity_no_change(self, jointing):
        hm = np.ones((50, 50)) * 3.0
        result = jointing.generate_weathering_roughness(hm, 0.1, intensity=0.0)
        np.testing.assert_array_equal(result, hm)
