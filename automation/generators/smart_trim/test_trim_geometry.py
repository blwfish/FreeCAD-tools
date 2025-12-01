"""
Test Suite for trim_geometry.py v1.2.0

Tests corner detection, angle calculation, and trim generation.
Can be run standalone or from FreeCAD.

Usage:
    python3 test_trim_geometry.py
    
Or from FreeCAD Python console:
    exec(open('test_trim_geometry.py').read())
"""

import sys
import math

# Try to import FreeCAD
try:
    import FreeCAD as App
    import Part
    IN_FREECAD = True
except ImportError:
    IN_FREECAD = False
    print("Warning: FreeCAD not available - some tests will be skipped")

# Import the library
try:
    import trim_geometry as tg
except ImportError:
    print("ERROR: Cannot import trim_geometry.py")
    print("Make sure trim_geometry.py is in the same directory")
    sys.exit(1)


class TestResults:
    """Simple test result tracker."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.failures = []
    
    def add_pass(self, test_name):
        self.passed += 1
        print(f"  ✓ {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.failures.append((test_name, error))
        print(f"  ✗ {test_name}: {error}")
    
    def add_skip(self, test_name, reason):
        self.skipped += 1
        print(f"  ⊘ {test_name} (skipped: {reason})")
    
    def summary(self):
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*72}")
        print(f"Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"  Failed: {self.failed}")
            for name, error in self.failures:
                print(f"    - {name}: {error}")
        if self.skipped > 0:
            print(f"  Skipped: {self.skipped}")
        print(f"{'='*72}\n")
        return self.failed == 0


# ==============================================================================
# TEST FUNCTIONS
# ==============================================================================

def test_rectangle_corners(results):
    """Test corner detection on a simple rectangle."""
    if not IN_FREECAD:
        results.add_skip("Rectangle corners", "FreeCAD not available")
        return
    
    # Create rectangle
    v1 = App.Vector(0, 0, 0)
    v2 = App.Vector(100, 0, 0)
    v3 = App.Vector(100, 50, 0)
    v4 = App.Vector(0, 50, 0)
    
    edges = [
        Part.LineSegment(v1, v2).toShape(),
        Part.LineSegment(v2, v3).toShape(),
        Part.LineSegment(v3, v4).toShape(),
        Part.LineSegment(v4, v1).toShape(),
    ]
    
    wire = Part.Wire(edges)
    face = Part.Face(wire)
    
    # Test corner detection
    corners = tg.detect_corners(face)
    
    if len(corners) != 4:
        results.add_fail("Rectangle corners", f"Expected 4 corners, got {len(corners)}")
        return
    
    # Check all are external 90°
    for i, corner in enumerate(corners):
        if corner.corner_type != tg.CornerType.EXTERNAL:
            results.add_fail("Rectangle corners", 
                           f"Corner {i+1} not external: {corner.corner_type}")
            return
        if not (89.5 < corner.angle < 90.5):
            results.add_fail("Rectangle corners",
                           f"Corner {i+1} angle {corner.angle}° not ~90°")
            return
        if not (44.5 < corner.miter_angle() < 45.5):
            results.add_fail("Rectangle corners",
                           f"Corner {i+1} miter {corner.miter_angle()}° not ~45°")
            return
    
    results.add_pass("Rectangle corners")


def test_hexagon_corners(results):
    """Test corner detection on a regular hexagon."""
    if not IN_FREECAD:
        results.add_skip("Hexagon corners", "FreeCAD not available")
        return
    
    # Create hexagon
    center = App.Vector(50, 50, 0)
    radius = 30
    
    vertices = []
    for i in range(6):
        angle = i * 60 * math.pi / 180
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        vertices.append(App.Vector(x, y, 0))
    
    edges = []
    for i in range(6):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % 6]
        edges.append(Part.LineSegment(v1, v2).toShape())
    
    wire = Part.Wire(edges)
    face = Part.Face(wire)
    
    # Test
    corners = tg.detect_corners(face)
    
    if len(corners) != 6:
        results.add_fail("Hexagon corners", f"Expected 6 corners, got {len(corners)}")
        return
    
    # Check all are external 120°
    for i, corner in enumerate(corners):
        if corner.corner_type != tg.CornerType.EXTERNAL:
            results.add_fail("Hexagon corners",
                           f"Corner {i+1} not external")
            return
        if not (119.5 < corner.angle < 120.5):
            results.add_fail("Hexagon corners",
                           f"Corner {i+1} angle {corner.angle}° not ~120°")
            return
        if not (59.5 < corner.miter_angle() < 60.5):
            results.add_fail("Hexagon corners",
                           f"Corner {i+1} miter {corner.miter_angle()}° not ~60°")
            return
    
    results.add_pass("Hexagon corners")


def test_lshape_corners(results):
    """Test corner detection on L-shaped face (internal corner)."""
    if not IN_FREECAD:
        results.add_skip("L-shape corners", "FreeCAD not available")
        return
    
    # Create L-shape
    v1 = App.Vector(0, 0, 0)
    v2 = App.Vector(50, 0, 0)
    v3 = App.Vector(50, 30, 0)
    v4 = App.Vector(100, 30, 0)
    v5 = App.Vector(100, 60, 0)
    v6 = App.Vector(0, 60, 0)
    
    edges = [
        Part.LineSegment(v1, v2).toShape(),
        Part.LineSegment(v2, v3).toShape(),
        Part.LineSegment(v3, v4).toShape(),
        Part.LineSegment(v4, v5).toShape(),
        Part.LineSegment(v5, v6).toShape(),
        Part.LineSegment(v6, v1).toShape(),
    ]
    
    wire = Part.Wire(edges)
    face = Part.Face(wire)
    
    # Test
    corners = tg.detect_corners(face)
    
    if len(corners) != 6:
        results.add_fail("L-shape corners", f"Expected 6 corners, got {len(corners)}")
        return
    
    # Count external vs internal
    external = sum(1 for c in corners if c.corner_type == tg.CornerType.EXTERNAL)
    internal = sum(1 for c in corners if c.corner_type == tg.CornerType.INTERNAL)
    
    if external != 5:
        results.add_fail("L-shape corners", f"Expected 5 external, got {external}")
        return
    if internal != 1:
        results.add_fail("L-shape corners", f"Expected 1 internal, got {internal}")
        return
    
    # Find the internal corner (should be 270°)
    internal_corner = [c for c in corners if c.corner_type == tg.CornerType.INTERNAL][0]
    if not (269.5 < internal_corner.angle < 270.5):
        results.add_fail("L-shape corners",
                       f"Internal angle {internal_corner.angle}° not ~270°")
        return
    
    results.add_pass("L-shape corners")


def test_profile_creation(results):
    """Test trim profile generation."""
    if not IN_FREECAD:
        results.add_skip("Profile creation", "FreeCAD not available")
        return
    
    # Test rectangular profile
    try:
        rect_profile = tg.create_simple_rectangular_profile(2.0, 5.0)
        if not rect_profile.isClosed():
            results.add_fail("Profile creation", "Rectangular profile not closed")
            return
        results.add_pass("Profile creation (rectangular)")
    except Exception as e:
        results.add_fail("Profile creation (rectangular)", str(e))
        return
    
    # Test beveled profile
    try:
        bevel_profile = tg.create_beveled_profile(2.0, 5.0, 0.5)
        if not bevel_profile.isClosed():
            results.add_fail("Profile creation", "Beveled profile not closed")
            return
        results.add_pass("Profile creation (beveled)")
    except Exception as e:
        results.add_fail("Profile creation (beveled)", str(e))


def test_analysis_function(results):
    """Test the complete analysis function."""
    if not IN_FREECAD:
        results.add_skip("Analysis function", "FreeCAD not available")
        return
    
    # Create simple rectangle
    v1 = App.Vector(0, 0, 0)
    v2 = App.Vector(100, 0, 0)
    v3 = App.Vector(100, 50, 0)
    v4 = App.Vector(0, 50, 0)
    
    edges = [
        Part.LineSegment(v1, v2).toShape(),
        Part.LineSegment(v2, v3).toShape(),
        Part.LineSegment(v3, v4).toShape(),
        Part.LineSegment(v4, v1).toShape(),
    ]
    
    wire = Part.Wire(edges)
    face = Part.Face(wire)
    
    # Test analysis
    try:
        analysis = tg.analyze_face_for_trim(face)
        
        if analysis['num_corners'] != 4:
            results.add_fail("Analysis function", "Wrong corner count")
            return
        if analysis['num_external'] != 4:
            results.add_fail("Analysis function", "Wrong external count")
            return
        if analysis['num_internal'] != 0:
            results.add_fail("Analysis function", "Wrong internal count")
            return
        
        results.add_pass("Analysis function")
    except Exception as e:
        results.add_fail("Analysis function", str(e))


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================

def run_tests():
    """Run all tests and print results."""
    print(f"\n{'='*72}")
    print("TRIM GEOMETRY TEST SUITE v1.2.0")
    print(f"{'='*72}\n")
    
    results = TestResults()
    
    print("Running tests...\n")
    
    test_rectangle_corners(results)
    test_hexagon_corners(results)
    test_lshape_corners(results)
    test_profile_creation(results)
    test_analysis_function(results)
    
    return results.summary()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
