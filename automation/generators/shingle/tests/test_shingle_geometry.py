"""
Test suite for shingle_geometry.py

Run with: pytest test_shingle_geometry.py -v

Tests all pure geometry functions without requiring FreeCAD.
"""

import pytest
import math
from shingle_geometry import (
    validate_parameters,
    validate_stagger_pattern,
    calculate_stagger_offset,
    calculate_layout,
    validate_face_geometry,
    is_planar,
    calculate_face_bounds,
    detect_face_orientation,
    validate_face_for_shingling,
    get_orientation_description,
    calculate_shingle_position,
    validate_collar_margin,
)


class TestParameterValidation:
    """Tests for validate_parameters()"""
    
    def test_valid_parameters(self):
        """Standard valid parameters should pass"""
        is_valid, errors = validate_parameters(
            shingle_width=10.0,
            shingle_height=20.0,
            material_thickness=0.5,
            shingle_exposure=15.0
        )
        assert is_valid
        assert len(errors) == 0
    
    def test_zero_width_rejected(self):
        """Zero width should fail"""
        is_valid, errors = validate_parameters(0, 20.0, 0.5, 15.0)
        assert not is_valid
        assert any("width" in e.lower() for e in errors)
    
    def test_negative_height_rejected(self):
        """Negative height should fail"""
        is_valid, errors = validate_parameters(10.0, -20.0, 0.5, 15.0)
        assert not is_valid
        assert any("height" in e.lower() for e in errors)
    
    def test_zero_thickness_rejected(self):
        """Zero thickness should fail"""
        is_valid, errors = validate_parameters(10.0, 20.0, 0, 15.0)
        assert not is_valid
        assert any("thickness" in e.lower() for e in errors)
    
    def test_zero_exposure_rejected(self):
        """Zero exposure should fail"""
        is_valid, errors = validate_parameters(10.0, 20.0, 0.5, 0)
        assert not is_valid
        assert any("exposure" in e.lower() for e in errors)
    
    def test_exposure_exceeds_height_rejected(self):
        """Exposure cannot exceed height"""
        is_valid, errors = validate_parameters(10.0, 20.0, 0.5, 25.0)
        assert not is_valid
        assert any("exposure" in e.lower() and "exceed" in e.lower() for e in errors)
    
    def test_thickness_exceeds_height_rejected(self):
        """Thickness cannot exceed height"""
        is_valid, errors = validate_parameters(10.0, 20.0, 25.0, 15.0)
        assert not is_valid
        assert any("thickness" in e.lower() and "exceed" in e.lower() for e in errors)


class TestStaggerPattern:
    """Tests for stagger pattern validation and calculation"""
    
    def test_valid_half_pattern(self):
        """'half' pattern should be valid"""
        is_valid, msg = validate_stagger_pattern("half")
        assert is_valid
    
    def test_valid_third_pattern(self):
        """'third' pattern should be valid"""
        is_valid, msg = validate_stagger_pattern("third")
        assert is_valid
    
    def test_valid_none_pattern(self):
        """'none' pattern should be valid"""
        is_valid, msg = validate_stagger_pattern("none")
        assert is_valid
    
    def test_invalid_pattern_rejected(self):
        """Invalid pattern should fail"""
        is_valid, msg = validate_stagger_pattern("diagonal")
        assert not is_valid
        assert "Invalid" in msg
    
    def test_half_stagger_row_0(self):
        """Half stagger row 0 should be 0"""
        offset = calculate_stagger_offset(0, "half", 10.0)
        assert offset == 0.0
    
    def test_half_stagger_row_1(self):
        """Half stagger row 1 should be half width"""
        offset = calculate_stagger_offset(1, "half", 10.0)
        assert offset == 5.0
    
    def test_half_stagger_row_2(self):
        """Half stagger row 2 should be 0 (repeats pattern)"""
        offset = calculate_stagger_offset(2, "half", 10.0)
        assert offset == 0.0
    
    def test_third_stagger_row_0(self):
        """Third stagger row 0 should be 0"""
        offset = calculate_stagger_offset(0, "third", 12.0)
        assert offset == 0.0
    
    def test_third_stagger_row_1(self):
        """Third stagger row 1 should be one third width"""
        offset = calculate_stagger_offset(1, "third", 12.0)
        assert offset == 4.0
    
    def test_third_stagger_row_2(self):
        """Third stagger row 2 should be two thirds width"""
        offset = calculate_stagger_offset(2, "third", 12.0)
        assert offset == 8.0
    
    def test_third_stagger_row_3(self):
        """Third stagger row 3 should repeat to 0"""
        offset = calculate_stagger_offset(3, "third", 12.0)
        assert offset == 0.0
    
    def test_none_stagger_all_rows(self):
        """'none' pattern should always be 0"""
        for row in range(5):
            offset = calculate_stagger_offset(row, "none", 10.0)
            assert offset == 0.0


class TestLayout:
    """Tests for calculate_layout()"""
    
    def test_basic_layout(self):
        """Standard layout calculation"""
        layout = calculate_layout(
            face_width=100.0,
            face_height=100.0,
            shingle_width=10.0,
            shingle_exposure=15.0,
            stagger_pattern="half"
        )
        assert layout['num_courses'] > 0
        assert layout['shingles_per_course'] > 0
        assert layout['max_stagger'] == 5.0  # half of 10
        assert layout['total_shingles_before_trim'] > 0
    
    def test_layout_with_third_stagger(self):
        """Layout with third stagger pattern"""
        layout = calculate_layout(
            face_width=100.0,
            face_height=100.0,
            shingle_width=12.0,
            shingle_exposure=15.0,
            stagger_pattern="third"
        )
        assert layout['max_stagger'] == 4.0  # one third of 12
    
    def test_layout_with_no_stagger(self):
        """Layout with no stagger"""
        layout = calculate_layout(
            face_width=100.0,
            face_height=100.0,
            shingle_width=10.0,
            shingle_exposure=15.0,
            stagger_pattern="none"
        )
        assert layout['max_stagger'] == 0.0
    
    def test_layout_courses_covers_height(self):
        """Number of courses should cover face height"""
        layout = calculate_layout(
            face_width=100.0,
            face_height=150.0,
            shingle_width=10.0,
            shingle_exposure=20.0
        )
        # At least 150/20 = 7.5, so 8+ courses (plus 3 extra)
        assert layout['num_courses'] >= 11
    
    def test_layout_shingles_per_course_covers_width(self):
        """Shingles per course should cover face width with stagger"""
        layout = calculate_layout(
            face_width=100.0,
            face_height=100.0,
            shingle_width=10.0,
            shingle_exposure=15.0,
            stagger_pattern="half"
        )
        # Width needed = 100 + 2*5 = 110, so 110/10 = 11 shingles (plus 3 extra)
        assert layout['shingles_per_course'] >= 14


class TestFaceGeometry:
    """Tests for face geometry validation"""
    
    def test_valid_face_size(self):
        """Face with valid dimensions should pass"""
        is_valid, errors = validate_face_geometry(100.0, 150.0)
        assert is_valid
    
    def test_zero_width_rejected(self):
        """Zero width should fail"""
        is_valid, errors = validate_face_geometry(0, 100.0)
        assert not is_valid
    
    def test_negative_height_rejected(self):
        """Negative height should fail"""
        is_valid, errors = validate_face_geometry(100.0, -50.0)
        assert not is_valid
    
    def test_very_small_face_warning(self):
        """Face smaller than 5x5mm should generate warning"""
        is_valid, errors = validate_face_geometry(3.0, 3.0)
        assert len(errors) > 0
        assert any("small" in e.lower() for e in errors)


class TestPlanarity:
    """Tests for is_planar()"""
    
    def test_xy_plane_coplanar(self):
        """Four points on XY plane should be coplanar"""
        points = [
            (0, 0, 0),
            (10, 0, 0),
            (10, 10, 0),
            (0, 10, 0)
        ]
        assert is_planar(points)
    
    def test_xz_plane_coplanar(self):
        """Four points on XZ plane should be coplanar"""
        points = [
            (0, 0, 0),
            (10, 0, 0),
            (10, 0, 10),
            (0, 0, 10)
        ]
        assert is_planar(points)
    
    def test_yz_plane_coplanar(self):
        """Four points on YZ plane should be coplanar"""
        points = [
            (0, 0, 0),
            (0, 10, 0),
            (0, 10, 10),
            (0, 0, 10)
        ]
        assert is_planar(points)
    
    def test_tilted_plane_coplanar(self):
        """Four points on a tilted plane should be coplanar"""
        # Points on plane z = x + y
        points = [
            (0, 0, 0),
            (10, 0, 10),
            (10, 10, 20),
            (0, 10, 10)
        ]
        assert is_planar(points)
    
    def test_non_coplanar_points_rejected(self):
        """Non-coplanar points should fail"""
        points = [
            (0, 0, 0),
            (10, 0, 0),
            (10, 10, 0),
            (0, 0, 10)  # This point is off the plane
        ]
        assert not is_planar(points, tolerance=0.01)
    
    def test_three_points_always_coplanar(self):
        """Three points are always coplanar"""
        points = [
            (0, 0, 0),
            (10, 5, 7),
            (3, 9, 2)
        ]
        assert is_planar(points)
    
    def test_empty_list_edge_case(self):
        """Edge case: less than 4 points should return True"""
        assert is_planar([])
        assert is_planar([(0, 0, 0)])


class TestBounds:
    """Tests for calculate_face_bounds()"""
    
    def test_simple_square_bounds(self):
        """Simple square should have correct bounds"""
        points = [
            (0, 0, 0),
            (10, 0, 0),
            (10, 10, 0),
            (0, 10, 0)
        ]
        bounds = calculate_face_bounds(points)
        assert bounds['x_min'] == 0
        assert bounds['x_max'] == 10
        assert bounds['y_min'] == 0
        assert bounds['y_max'] == 10
        assert bounds['z_min'] == 0
        assert bounds['z_max'] == 0
    
    def test_bounds_with_negative_coords(self):
        """Bounds should work with negative coordinates"""
        points = [
            (-5, -5, 0),
            (5, -5, 0),
            (5, 5, 0),
            (-5, 5, 0)
        ]
        bounds = calculate_face_bounds(points)
        assert bounds['x_min'] == -5
        assert bounds['x_max'] == 5
        assert bounds['y_min'] == -5
        assert bounds['y_max'] == 5


class TestOrientationDetection:
    """Tests for detect_face_orientation()"""
    
    def test_xy_plane_detected(self):
        """XY plane (z extent ~ 0) should be detected"""
        bbox = {
            'x_min': 0, 'x_max': 100,
            'y_min': 0, 'y_max': 150,
            'z_min': 0, 'z_max': 0.05  # Nearly zero
        }
        vert, horiz = detect_face_orientation(bbox)
        assert vert == 'y' or vert == 'x'  # One of them is vertical
        assert horiz != vert  # Other is horizontal
    
    def test_xz_plane_detected(self):
        """XZ plane (y extent ~ 0) should be detected"""
        bbox = {
            'x_min': 0, 'x_max': 100,
            'y_min': 0, 'y_max': 0.05,  # Nearly zero
            'z_min': 0, 'z_max': 150
        }
        vert, horiz = detect_face_orientation(bbox)
        assert vert == 'z' or vert == 'x'
        assert horiz != vert
    
    def test_yz_plane_detected(self):
        """YZ plane (x extent ~ 0) should be detected"""
        bbox = {
            'x_min': 0, 'x_max': 0.05,  # Nearly zero
            'y_min': 0, 'y_max': 100,
            'z_min': 0, 'z_max': 150
        }
        vert, horiz = detect_face_orientation(bbox)
        assert vert == 'z' or vert == 'y'
        assert horiz != vert


class TestFaceValidation:
    """Tests for validate_face_for_shingling()"""
    
    def test_valid_rectangular_face(self):
        """Standard rectangular face should be valid"""
        points = [
            (0, 0, 0),
            (100, 0, 0),
            (100, 150, 0),
            (0, 150, 0)
        ]
        is_valid, errors = validate_face_for_shingling(points)
        assert is_valid
        assert len(errors) == 0
    
    def test_too_few_vertices_rejected(self):
        """Face with less than 4 vertices should fail"""
        points = [
            (0, 0, 0),
            (10, 0, 0),
            (10, 10, 0)
        ]
        is_valid, errors = validate_face_for_shingling(points)
        assert not is_valid
        assert any("vertices" in e.lower() for e in errors)
    
    def test_non_planar_face_rejected(self):
        """Non-planar face should fail"""
        points = [
            (0, 0, 0),
            (100, 0, 0),
            (100, 100, 0),
            (50, 50, 100)  # Non-coplanar
        ]
        is_valid, errors = validate_face_for_shingling(points)
        assert not is_valid
        assert any("planar" in e.lower() for e in errors)
    
    def test_very_small_face_warning(self):
        """Face smaller than minimum should generate errors"""
        points = [
            (0, 0, 0),
            (3, 0, 0),
            (3, 3, 0),
            (0, 3, 0)
        ]
        is_valid, errors = validate_face_for_shingling(points, min_width=5, min_height=5)
        # Could be invalid or valid with warnings depending on implementation
        # At minimum, errors should be reported
        assert len(errors) > 0


class TestOrientationDescription:
    """Tests for get_orientation_description()"""
    
    def test_xy_plane_description(self):
        """XY plane should be described correctly"""
        desc = get_orientation_description('y', 'x')
        assert "XY" in desc
    
    def test_xz_plane_description(self):
        """XZ plane should be described correctly"""
        desc = get_orientation_description('z', 'x')
        assert "XZ" in desc
    
    def test_yz_plane_description(self):
        """YZ plane should be described correctly"""
        desc = get_orientation_description('z', 'y')
        assert "YZ" in desc


class TestShinglePosition:
    """Tests for calculate_shingle_position()"""
    
    def test_row_0_col_0_no_stagger(self):
        """Row 0, Col 0 with no stagger should be at origin"""
        u, v = calculate_shingle_position(0, 0, 10.0, 20.0, 15.0, "none")
        assert u == 0.0
        assert v == -15.0  # One course below origin
    
    def test_row_0_col_1_no_stagger(self):
        """Row 0, Col 1 should be at shingle width"""
        u, v = calculate_shingle_position(0, 1, 10.0, 20.0, 15.0, "none")
        assert u == 10.0
        assert v == -15.0
    
    def test_row_1_col_0_half_stagger(self):
        """Row 1, Col 0 with half stagger should offset by width/2"""
        u, v = calculate_shingle_position(1, 0, 10.0, 20.0, 15.0, "half")
        assert u == 5.0  # Half stagger
        assert v == 0.0  # At exposure height
    
    def test_vertical_positions_increase(self):
        """Vertical positions should increase with rows"""
        v0 = calculate_shingle_position(0, 0, 10.0, 20.0, 15.0, "none")[1]
        v1 = calculate_shingle_position(1, 0, 10.0, 20.0, 15.0, "none")[1]
        v2 = calculate_shingle_position(2, 0, 10.0, 20.0, 15.0, "none")[1]
        assert v1 > v0
        assert v2 > v1


class TestCollarMargin:
    """Tests for validate_collar_margin()"""
    
    def test_reasonable_margin(self):
        """Collar margin should be reasonable"""
        margin = validate_collar_margin(10.0, 20.0)
        # Should be 3x largest, so 3 * 20 = 60
        assert margin == 60.0
    
    def test_margin_depends_on_larger_dimension(self):
        """Margin should use largest dimension"""
        margin_small = validate_collar_margin(5.0, 10.0)  # 3 * 10 = 30
        margin_large = validate_collar_margin(20.0, 10.0)  # 3 * 20 = 60
        assert margin_large > margin_small


# Integration tests
class TestIntegration:
    """Integration tests combining multiple functions"""
    
    def test_full_validation_pipeline(self):
        """Test a complete validation pipeline"""
        # Parameters
        is_valid, _ = validate_parameters(10.0, 20.0, 0.5, 15.0)
        assert is_valid
        
        # Face
        face_points = [(0, 0, 0), (100, 0, 0), (100, 150, 0), (0, 150, 0)]
        is_valid, _ = validate_face_for_shingling(face_points)
        assert is_valid
        
        # Layout
        layout = calculate_layout(100.0, 150.0, 10.0, 15.0)
        assert layout['num_courses'] > 0
        assert layout['shingles_per_course'] > 0
    
    def test_realistic_roof_scenario(self):
        """Test a realistic roof geometry"""
        # 500mm wide, 300mm tall roof face at 30 degrees
        face_points = [
            (0, 0, 0),
            (500, 0, 0),
            (500, 250, 150),
            (0, 250, 150)
        ]
        
        # Should be planar (tilted)
        assert is_planar(face_points, tolerance=0.01)
        
        # Should be valid for shingling
        is_valid, errors = validate_face_for_shingling(face_points)
        assert is_valid, f"Face invalid: {errors}"
        
        # Should detect orientation
        bounds = calculate_face_bounds(face_points)
        vert, horiz = detect_face_orientation(bounds)
        assert vert in ['x', 'y', 'z']
        assert horiz in ['x', 'y', 'z']
        assert vert != horiz
        
        # Should calculate reasonable layout
        layout = calculate_layout(500.0, 300.0, 10.0, 15.0)
        assert layout['num_courses'] >= 20


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
