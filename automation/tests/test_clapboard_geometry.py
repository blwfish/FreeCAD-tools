"""
Test suite for clapboard_geometry.py

Run with: pytest tests/test_clapboard_geometry.py -v
"""

import pytest
import math
from clapboard_geometry import (
    check_for_degenerate_edges,
    check_for_duplicate_edges,
    validate_wire_geometry,
    detect_face_orientation,
    is_building_corner,
    calculate_clapboard_courses,
    validate_parameters,
    get_face_orientation_description
)


class TestDegenerateEdges:
    """Test detection of zero-length edges."""
    
    def test_no_degenerate_edges(self):
        """Should return empty list for valid edges."""
        edges = [
            {'length': 10.0},
            {'length': 5.5},
            {'length': 0.1}
        ]
        result = check_for_degenerate_edges(edges)
        assert result == []
    
    def test_single_degenerate_edge(self):
        """Should detect single zero-length edge."""
        edges = [
            {'length': 10.0},
            {'length': 0.0005},  # Below 0.001 tolerance
            {'length': 5.0}
        ]
        result = check_for_degenerate_edges(edges)
        assert len(result) == 1
        assert result[0][0] == 1  # Edge index
    
    def test_multiple_degenerate_edges(self):
        """Should detect multiple degenerate edges."""
        edges = [
            {'length': 0.0},
            {'length': 10.0},
            {'length': 0.0008},
            {'length': 5.0}
        ]
        result = check_for_degenerate_edges(edges)
        assert len(result) == 2
        assert result[0][0] == 0
        assert result[1][0] == 2
    
    def test_edge_at_tolerance_boundary(self):
        """Should handle edge exactly at tolerance."""
        edges = [
            {'length': 0.001},  # Exactly at tolerance
            {'length': 0.0009}  # Just below
        ]
        result = check_for_degenerate_edges(edges)
        assert len(result) == 1  # Only the one below tolerance


class TestDuplicateEdges:
    """Test detection of overlapping edges."""
    
    def test_no_duplicate_edges(self):
        """Should return empty list for non-overlapping edges."""
        edges = [
            {'start': (0, 0, 0), 'end': (10, 0, 0)},
            {'start': (10, 0, 0), 'end': (20, 0, 0)},
            {'start': (0, 10, 0), 'end': (0, 20, 0)}
        ]
        result = check_for_duplicate_edges(edges)
        assert result == []
    
    def test_identical_edges_same_direction(self):
        """Should detect identical edges in same direction."""
        edges = [
            {'start': (0, 0, 0), 'end': (10, 0, 0)},
            {'start': (0, 0, 0), 'end': (10, 0, 0)},  # Duplicate
            {'start': (20, 0, 0), 'end': (30, 0, 0)}
        ]
        result = check_for_duplicate_edges(edges)
        assert len(result) == 1
        assert result[0] == (0, 1)
    
    def test_identical_edges_reversed(self):
        """Should detect identical edges in opposite directions."""
        edges = [
            {'start': (0, 0, 0), 'end': (10, 0, 0)},
            {'start': (10, 0, 0), 'end': (0, 0, 0)},  # Same edge, reversed
            {'start': (20, 0, 0), 'end': (30, 0, 0)}
        ]
        result = check_for_duplicate_edges(edges)
        assert len(result) == 1
        assert result[0] == (0, 1)
    
    def test_near_duplicate_edges_within_tolerance(self):
        """Should detect nearly-identical edges within tolerance."""
        edges = [
            {'start': (0, 0, 0), 'end': (10, 0, 0)},
            {'start': (0.0005, 0.0005, 0), 'end': (10.0005, 0.0005, 0)},  # Within tolerance
            {'start': (20, 0, 0), 'end': (30, 0, 0)}
        ]
        result = check_for_duplicate_edges(edges)
        assert len(result) == 1


class TestWireValidation:
    """Test complete wire geometry validation."""
    
    def test_valid_wire(self):
        """Should validate a good wire."""
        edges = [
            {'length': 10.0, 'start': (0, 0, 0), 'end': (10, 0, 0)},
            {'length': 10.0, 'start': (10, 0, 0), 'end': (10, 10, 0)},
            {'length': 10.0, 'start': (10, 10, 0), 'end': (0, 10, 0)},
            {'length': 10.0, 'start': (0, 10, 0), 'end': (0, 0, 0)}
        ]
        is_valid, errors = validate_wire_geometry(edges, "TestWire")
        assert is_valid
        assert errors == []
    
    def test_invalid_wire_degenerate_edge(self):
        """Should report degenerate edge."""
        edges = [
            {'length': 10.0, 'start': (0, 0, 0), 'end': (10, 0, 0)},
            {'length': 0.0, 'start': (10, 0, 0), 'end': (10, 0, 0)},
        ]
        is_valid, errors = validate_wire_geometry(edges, "TestWire")
        assert not is_valid
        assert any("degenerate" in err.lower() for err in errors)
    
    def test_invalid_wire_duplicate_edges(self):
        """Should report duplicate edges."""
        edges = [
            {'length': 10.0, 'start': (0, 0, 0), 'end': (10, 0, 0)},
            {'length': 10.0, 'start': (0, 0, 0), 'end': (10, 0, 0)},  # Duplicate
        ]
        is_valid, errors = validate_wire_geometry(edges, "TestWire")
        assert not is_valid
        assert any("duplicate" in err.lower() for err in errors)


class TestFaceOrientation:
    """Test face orientation detection."""
    
    def test_xy_plane_face(self):
        """Should detect XY plane (Z extent near zero)."""
        bbox = {'x_min': 0, 'x_max': 100, 'y_min': 0, 'y_max': 100, 'z_min': 0, 'z_max': 0.05}
        vert, horiz, normal = detect_face_orientation(bbox)
        assert vert == 'y'
        assert horiz == 'x'
        assert normal == 'z'
    
    def test_xz_plane_face(self):
        """Should detect XZ plane (Y extent near zero)."""
        bbox = {'x_min': 0, 'x_max': 100, 'y_min': 0, 'y_max': 0.05, 'z_min': 0, 'z_max': 50}
        vert, horiz, normal = detect_face_orientation(bbox)
        assert vert == 'z'
        assert horiz == 'x'
        assert normal == 'y'
    
    def test_yz_plane_face(self):
        """Should detect YZ plane (X extent near zero)."""
        bbox = {'x_min': 0, 'x_max': 0.05, 'y_min': 0, 'y_max': 100, 'z_min': 0, 'z_max': 50}
        vert, horiz, normal = detect_face_orientation(bbox)
        assert vert == 'z'
        assert horiz == 'y'
        assert normal == 'x'
    
    def test_tilted_face_uses_largest_extent(self):
        """Should use largest extent as vertical for tilted faces."""
        bbox = {'x_min': 0, 'x_max': 50, 'y_min': 0, 'y_max': 30, 'z_min': 0, 'z_max': 100}
        vert, horiz, normal = detect_face_orientation(bbox)
        assert vert == 'z'  # Z is largest


class TestBuildingCorner:
    """Test corner detection."""
    
    def test_corner_at_x_min(self):
        """Should detect corner at X minimum."""
        bbox = {'x_min': 0, 'x_max': 100, 'y_min': 0, 'y_max': 50}
        assert is_building_corner(0.0, bbox, 'x') == True
    
    def test_corner_at_x_max(self):
        """Should detect corner at X maximum."""
        bbox = {'x_min': 0, 'x_max': 100, 'y_min': 0, 'y_max': 50}
        assert is_building_corner(100.0, bbox, 'x') == True
    
    def test_interior_not_corner(self):
        """Should not detect interior positions as corners."""
        bbox = {'x_min': 0, 'x_max': 100, 'y_min': 0, 'y_max': 50}
        assert is_building_corner(50.0, bbox, 'x') == False
    
    def test_corner_with_tolerance(self):
        """Should respect tolerance."""
        bbox = {'x_min': 0, 'x_max': 100, 'y_min': 0, 'y_max': 50}
        assert is_building_corner(0.5, bbox, 'x', tolerance=1.0) == True  # Within tolerance
        assert is_building_corner(0.5, bbox, 'x', tolerance=0.1) == False  # Outside tolerance


class TestClapboardCourses:
    """Test clapboard course calculation."""
    
    def test_exact_fit(self):
        """Should calculate courses for exact fit."""
        courses = calculate_clapboard_courses(100.0, 10.0)
        assert courses == 10
    
    def test_with_remainder(self):
        """Should round up for partial course."""
        courses = calculate_clapboard_courses(105.0, 10.0)
        assert courses == 11  # 10.5 rounds up to 11
    
    def test_single_course(self):
        """Should handle small walls."""
        courses = calculate_clapboard_courses(5.0, 10.0)
        assert courses == 1
    
    def test_zero_height(self):
        """Should handle zero-height walls."""
        courses = calculate_clapboard_courses(0.0, 10.0)
        assert courses == 0
    
    def test_invalid_parameters(self):
        """Should raise on invalid parameters."""
        with pytest.raises(ValueError):
            calculate_clapboard_courses(-10.0, 1.0)
        
        with pytest.raises(ValueError):
            calculate_clapboard_courses(100.0, -1.0)
        
        with pytest.raises(ValueError):
            calculate_clapboard_courses(100.0, 0.0)


class TestParameterValidation:
    """Test parameter validation."""
    
    def test_valid_parameters(self):
        """Should accept valid parameters."""
        is_valid, errors = validate_parameters(0.8, 0.2)
        assert is_valid
        assert errors == []
    
    def test_zero_height(self):
        """Should reject zero height."""
        is_valid, errors = validate_parameters(0.0, 0.2)
        assert not is_valid
        assert any("height" in err.lower() for err in errors)
    
    def test_zero_thickness(self):
        """Should reject zero thickness."""
        is_valid, errors = validate_parameters(0.8, 0.0)
        assert not is_valid
        assert any("thickness" in err.lower() for err in errors)
    
    def test_thickness_exceeds_height(self):
        """Should reject thickness > height."""
        is_valid, errors = validate_parameters(0.5, 0.8)
        assert not is_valid
        assert any("exceed" in err.lower() for err in errors)
    
    def test_negative_parameters(self):
        """Should reject negative parameters."""
        is_valid, errors = validate_parameters(-0.8, 0.2)
        assert not is_valid
        
        is_valid, errors = validate_parameters(0.8, -0.2)
        assert not is_valid


class TestOrientationDescription:
    """Test human-readable orientation descriptions."""
    
    def test_xz_plane_description(self):
        """Should describe XZ plane."""
        desc = get_face_orientation_description('z', 'x')
        assert 'XZ' in desc or 'xz' in desc.lower()
    
    def test_yz_plane_description(self):
        """Should describe YZ plane."""
        desc = get_face_orientation_description('z', 'y')
        assert 'YZ' in desc or 'yz' in desc.lower()
    
    def test_xy_plane_description(self):
        """Should describe XY plane."""
        desc = get_face_orientation_description('y', 'x')
        assert 'XY' in desc or 'xy' in desc.lower()


# Integration tests
class TestIntegration:
    """Integration tests combining multiple functions."""
    
    def test_typical_wall_scenario(self):
        """Test a typical wall geometry scenario."""
        # 59.56mm tall wall, 1.75mm clapboard height
        wall_height = 59.56
        clapboard_height = 1.75
        
        courses = calculate_clapboard_courses(wall_height, clapboard_height)
        assert courses == 35  # 59.56 / 1.75 = 34, rounds up to 35
        
        # Validate parameters
        is_valid, errors = validate_parameters(clapboard_height, 0.2)
        assert is_valid
    
    def test_face_with_bay_window(self):
        """Test face detection for a bay window."""
        # Bay window face in XZ plane
        bbox = {
            'x_min': 0, 'x_max': 30,      # 30mm wide
            'y_min': 0, 'y_max': 0.05,    # Nearly flat (wall thickness)
            'z_min': 0, 'z_max': 40       # 40mm tall
        }
        
        vert, horiz, normal = detect_face_orientation(bbox)
        assert vert == 'z'
        assert horiz == 'x'
        assert normal == 'y'
        
        # Check that corners would be detected
        assert is_building_corner(0.0, bbox, 'x') == True
        assert is_building_corner(30.0, bbox, 'x') == True
        assert is_building_corner(15.0, bbox, 'x') == False
