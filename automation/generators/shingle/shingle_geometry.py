"""
Shingle Geometry Library v5.0.0

Pure Python geometry functions for shingle generation.
These functions are testable without FreeCAD and can be used in pytest.

No dependencies on FreeCAD.Part, FreeCAD.Vector, etc.
Uses standard Python types (tuples, dicts, lists) for I/O.

v5.0.0: Added bounding-box based orientation detection for reliable
        eave-to-ridge direction finding. Also added Z-based valley/ridge
        detection for smart trim functionality.
"""

import math
from typing import List, Tuple, Dict, Optional


def validate_parameters(shingle_width: float, shingle_height: float, 
                       material_thickness: float, shingle_exposure: float) -> Tuple[bool, List[str]]:
    """
    Validate shingle parameters for physical and geometric soundness.
    
    Args:
        shingle_width: Width of each shingle in mm
        shingle_height: Height (length) of each shingle in mm
        material_thickness: Thickness of shingle material in mm
        shingle_exposure: Exposed portion per course in mm
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if shingle_width <= 0:
        errors.append(f"shingle_width must be positive, got {shingle_width}")
    
    if shingle_height <= 0:
        errors.append(f"shingle_height must be positive, got {shingle_height}")
    
    if material_thickness <= 0:
        errors.append(f"material_thickness must be positive, got {material_thickness}")
    
    if shingle_exposure <= 0:
        errors.append(f"shingle_exposure must be positive, got {shingle_exposure}")
    
    if shingle_exposure > shingle_height:
        errors.append(f"shingle_exposure ({shingle_exposure}) cannot exceed shingle_height ({shingle_height})")
    
    if material_thickness > shingle_height:
        errors.append(f"material_thickness ({material_thickness}) cannot exceed shingle_height ({shingle_height})")
    
    return len(errors) == 0, errors


def validate_stagger_pattern(pattern: str) -> Tuple[bool, str]:
    """
    Validate stagger pattern is one of the supported types.
    
    Args:
        pattern: Stagger pattern name
    
    Returns:
        Tuple of (is_valid, error_message if invalid)
    """
    valid_patterns = ["half", "third", "none"]
    
    if pattern not in valid_patterns:
        return False, f"Invalid stagger pattern '{pattern}'. Must be one of: {', '.join(valid_patterns)}"
    
    return True, ""


def calculate_stagger_offset(row: int, pattern: str, shingle_width: float) -> float:
    """
    Calculate horizontal stagger offset for a given row.
    
    Args:
        row: Row number (0-indexed)
        pattern: Stagger pattern ("half", "third", or "none")
        shingle_width: Width of each shingle in mm
    
    Returns:
        Stagger offset in mm
    """
    if pattern == "half":
        return (row % 2) * (shingle_width / 2.0)
    elif pattern == "third":
        return (row % 3) * (shingle_width / 3.0)
    else:  # "none"
        return 0.0


def calculate_layout(face_width: float, face_height: float, 
                     shingle_width: float, shingle_exposure: float,
                     stagger_pattern: str = "half") -> Dict:
    """
    Calculate shingle layout parameters for a roof face.
    
    Args:
        face_width: Width of roof face (mm)
        face_height: Height of roof face (mm, along slope)
        shingle_width: Width of each shingle (mm)
        shingle_exposure: Exposed portion per course (mm)
        stagger_pattern: Stagger pattern type
    
    Returns:
        Dict with layout info:
            - num_courses: Number of courses needed
            - shingles_per_course: Number of shingles per course
            - max_stagger: Maximum stagger offset (mm)
            - total_width_needed: Total width coverage needed
            - total_shingles_before_trim: Total shingle count before trimming
    """
    # Calculate number of courses
    # Add 3 extra to ensure full coverage with overlap
    num_courses = int(math.ceil(face_height / shingle_exposure)) + 3
    
    # Calculate maximum stagger offset
    if stagger_pattern == "half":
        max_stagger = shingle_width / 2.0
    elif stagger_pattern == "third":
        max_stagger = shingle_width / 3.0
    else:
        max_stagger = 0.0
    
    # Calculate width coverage needed
    # Start at -max_stagger and cover to face_width + max_stagger
    total_width_needed = face_width + 2 * max_stagger
    
    # Calculate shingles per course
    # Add 3 for safety margin
    shingles_per_course = int(math.ceil(total_width_needed / shingle_width)) + 3
    
    total_shingles = num_courses * shingles_per_course
    
    return {
        'num_courses': num_courses,
        'shingles_per_course': shingles_per_course,
        'max_stagger': max_stagger,
        'total_width_needed': total_width_needed,
        'total_shingles_before_trim': total_shingles
    }


def validate_face_geometry(face_width: float, face_height: float) -> Tuple[bool, List[str]]:
    """
    Validate face dimensions for shingling.
    
    Args:
        face_width: Width of face (mm)
        face_height: Height of face (mm)
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if face_width <= 0:
        errors.append(f"Face width must be positive, got {face_width}")
    
    if face_height <= 0:
        errors.append(f"Face height must be positive, got {face_height}")
    
    # Warn if face is very small (less than one shingle)
    if face_width < 5 or face_height < 5:
        errors.append(f"Face dimensions ({face_width}x{face_height}mm) are very small for shingling")
    
    return len(errors) == 0, errors


def is_planar(points: List[Tuple[float, float, float]], tolerance: float = 0.01) -> bool:
    """
    Check if a set of 3D points are coplanar within tolerance.
    
    Args:
        points: List of (x, y, z) tuples
        tolerance: Distance tolerance in mm
    
    Returns:
        True if points are coplanar within tolerance
    """
    if len(points) < 4:
        return True  # 3 or fewer points are always coplanar
    
    # Use first 3 points to define the plane
    p0 = points[0]
    p1 = points[1]
    p2 = points[2]
    
    # Vectors in the plane
    v1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    v2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
    
    # Normal to the plane (cross product)
    normal = (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )
    
    # Normalize
    norm_length = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
    if norm_length < 0.001:
        return False  # Degenerate plane (collinear points)
    
    normal = (normal[0] / norm_length, normal[1] / norm_length, normal[2] / norm_length)
    
    # Check distance from each remaining point to the plane
    plane_d = -(normal[0] * p0[0] + normal[1] * p0[1] + normal[2] * p0[2])
    
    for point in points[3:]:
        distance = abs(normal[0] * point[0] + normal[1] * point[1] + normal[2] * point[2] + plane_d)
        if distance > tolerance:
            return False
    
    return True


def calculate_face_bounds(points: List[Tuple[float, float, float]]) -> Dict:
    """
    Calculate bounding box from a set of 3D points.
    
    Args:
        points: List of (x, y, z) tuples
    
    Returns:
        Dict with bounds: {'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'}
    """
    if not points:
        raise ValueError("Cannot calculate bounds from empty point list")
    
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    z_coords = [p[2] for p in points]
    
    return {
        'x_min': min(x_coords),
        'x_max': max(x_coords),
        'y_min': min(y_coords),
        'y_max': max(y_coords),
        'z_min': min(z_coords),
        'z_max': max(z_coords)
    }


def detect_face_orientation(bbox: Dict) -> Tuple[str, str]:
    """
    Detect orientation of a planar face based on bounding box extents.
    
    Args:
        bbox: Dict with 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'
    
    Returns:
        Tuple of (vertical_axis, horizontal_axis) where axes are 'x', 'y', or 'z'
    """
    x_extent = bbox.get('x_max', 0) - bbox.get('x_min', 0)
    y_extent = bbox.get('y_max', 0) - bbox.get('y_min', 0)
    z_extent = bbox.get('z_max', 0) - bbox.get('z_min', 0)
    
    tolerance = 0.1  # mm
    
    # Find which axis has near-zero extent (normal to face)
    # The other two define vertical and horizontal directions
    
    if x_extent < tolerance:
        # YZ plane (normal is X)
        if y_extent >= z_extent:
            return 'z', 'y'  # Vertical = Z, Horizontal = Y
        else:
            return 'y', 'z'  # Vertical = Y, Horizontal = Z
    
    elif y_extent < tolerance:
        # XZ plane (normal is Y)
        if x_extent >= z_extent:
            return 'z', 'x'  # Vertical = Z, Horizontal = X
        else:
            return 'x', 'z'  # Vertical = X, Horizontal = Z
    
    elif z_extent < tolerance:
        # XY plane (normal is Z)
        if x_extent >= y_extent:
            return 'y', 'x'  # Vertical = Y, Horizontal = X
        else:
            return 'x', 'y'  # Vertical = X, Horizontal = Y
    
    else:
        # All three have extent - tilted face
        # Use largest as vertical
        if z_extent >= y_extent and z_extent >= x_extent:
            if x_extent > y_extent:
                return 'z', 'x'
            else:
                return 'z', 'y'
        elif y_extent >= x_extent and y_extent >= z_extent:
            if x_extent > z_extent:
                return 'y', 'x'
            else:
                return 'y', 'z'
        else:
            if y_extent > z_extent:
                return 'x', 'y'
            else:
                return 'x', 'z'


def validate_face_for_shingling(points: List[Tuple[float, float, float]],
                               min_width: float = 5.0,
                               min_height: float = 5.0) -> Tuple[bool, List[str]]:
    """
    Comprehensive validation of a face for shingling.
    
    Args:
        points: List of face vertices (x, y, z) tuples
        min_width: Minimum face width in mm
        min_height: Minimum face height in mm
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check we have at least 4 vertices (a quad)
    if len(points) < 4:
        errors.append(f"Face has {len(points)} vertices, need at least 4")
        return False, errors
    
    # Check planarity
    if not is_planar(points):
        errors.append("Face is not planar - cannot generate shingles")
        return False, errors
    
    # Check bounds
    bbox = calculate_face_bounds(points)
    x_extent = bbox['x_max'] - bbox['x_min']
    y_extent = bbox['y_max'] - bbox['y_min']
    z_extent = bbox['z_max'] - bbox['z_min']
    
    # Find the two significant extents (normal to face has minimal extent)
    extents = sorted([x_extent, y_extent, z_extent])
    
    if extents[1] < min_width or extents[2] < min_height:
        errors.append(f"Face too small: {extents[1]:.1f}x{extents[2]:.1f}mm, need {min_width}x{min_height}mm minimum")
    
    # Warn about very small faces
    if extents[2] < 10:
        errors.append(f"Face height {extents[2]:.1f}mm is very small for realistic shingling")
    
    return len(errors) == 0, errors


def get_orientation_description(vertical_axis: str, horizontal_axis: str) -> str:
    """
    Get human-readable description of face orientation.
    
    Args:
        vertical_axis: 'x', 'y', or 'z'
        horizontal_axis: 'x', 'y', or 'z'
    
    Returns:
        String description like "XZ plane" or "tilted face"
    """
    axes = {vertical_axis, horizontal_axis}
    
    if axes == {'x', 'z'}:
        return "XZ plane"
    elif axes == {'y', 'z'}:
        return "YZ plane"
    elif axes == {'x', 'y'}:
        return "XY plane"
    else:
        return f"tilted {vertical_axis}{horizontal_axis} face"


def calculate_shingle_position(row: int, col: int, 
                              shingle_width: float, shingle_height: float,
                              shingle_exposure: float, stagger_pattern: str) -> Tuple[float, float]:
    """
    Calculate the U,V position of a shingle in the layout.
    
    Args:
        row: Row index (0 = bottom)
        col: Column index (0 = left)
        shingle_width: Width of shingle (mm)
        shingle_height: Height of shingle (mm)
        shingle_exposure: Exposed portion per course (mm)
        stagger_pattern: Stagger pattern type
    
    Returns:
        Tuple of (u_position, v_position) in mm
    """
    # Calculate stagger
    stagger = calculate_stagger_offset(row, stagger_pattern, shingle_width)
    
    # U position (horizontal)
    u = col * shingle_width + stagger
    
    # V position (vertical, starting one course below origin)
    v = row * shingle_exposure - shingle_exposure
    
    return u, v


def validate_collar_margin(shingle_width: float, shingle_height: float) -> float:
    """
    Calculate appropriate collar margin for trimming excess shingles.
    
    Args:
        shingle_width: Width of shingle (mm)
        shingle_height: Height of shingle (mm)
    
    Returns:
        Recommended collar margin in mm
    """
    # Margin should be 3x the largest dimension to capture stagger
    return max(shingle_width, shingle_height) * 3


def should_clip_shingles(material_thickness: float) -> bool:
    """
    Determine if individual shingles should be clipped to face boundary.
    
    Clipping is necessary when shingles would overhang significantly,
    which is problematic for 3D printing (supports on flat surfaces).
    
    Args:
        material_thickness: Thickness of shingle material (mm)
    
    Returns:
        True if shingles should be clipped (material_thickness < 1mm typical)
    """
    # If material is very thin, clipping is essential for print support placement
    # Threshold: 1mm (anything thinner needs careful support management)
    return material_thickness < 1.0


def calculate_shingle_clip_volume(face_bounds: Dict,
                                  material_thickness: float) -> Dict:
    """
    Calculate the volume for clipping shingles to face boundary.

    Creates a "clipping box" that represents the valid region for shingles
    (the face + a small margin for material thickness).

    Args:
        face_bounds: Dict with 'x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max'
        material_thickness: Thickness of material (mm)

    Returns:
        Dict describing the clipping volume:
            - bounds: expanded bounds with material_thickness margin
            - needs_clipping: whether clipping is necessary
    """
    margin = material_thickness  # Only expand by actual material thickness

    return {
        'x_min': face_bounds.get('x_min', 0) - margin,
        'x_max': face_bounds.get('x_max', 0) + margin,
        'y_min': face_bounds.get('y_min', 0) - margin,
        'y_max': face_bounds.get('y_max', 0) + margin,
        'z_min': face_bounds.get('z_min', 0) - margin,
        'z_max': face_bounds.get('z_max', 0) + margin,
        'needs_clipping': True
    }


# =============================================================================
# Bounding-Box Based Orientation Detection (v5.0.0)
# =============================================================================

def find_eave_and_ridge_vertices(vertices: List[Tuple[float, float, float]],
                                  z_tolerance: float = 0.1) -> Dict:
    """
    Find the eave (lowest Z) and ridge (highest Z) vertices of a roof face.

    This is the foundation for bounding-box based orientation detection.
    Instead of relying on normals (which can point either way), we use
    the physical geometry: water flows downhill, so the lowest Z vertices
    are the eave and highest Z are the ridge.

    Args:
        vertices: List of (x, y, z) tuples representing face vertices
        z_tolerance: Tolerance for grouping vertices at same Z level (mm)

    Returns:
        Dict with:
            - eave_vertices: List of vertices at the lowest Z level
            - ridge_vertices: List of vertices at the highest Z level
            - eave_z: Z coordinate of eave
            - ridge_z: Z coordinate of ridge
            - eave_center: (x, y, z) centroid of eave vertices
            - ridge_center: (x, y, z) centroid of ridge vertices
            - slope_rise: Vertical rise from eave to ridge (ridge_z - eave_z)
    """
    if not vertices:
        raise ValueError("Cannot find eave/ridge from empty vertex list")

    # Find Z range
    z_coords = [v[2] for v in vertices]
    z_min = min(z_coords)
    z_max = max(z_coords)

    # Group vertices by Z level
    eave_vertices = [v for v in vertices if abs(v[2] - z_min) <= z_tolerance]
    ridge_vertices = [v for v in vertices if abs(v[2] - z_max) <= z_tolerance]

    # Calculate centroids
    def centroid(verts):
        n = len(verts)
        if n == 0:
            return (0, 0, 0)
        return (
            sum(v[0] for v in verts) / n,
            sum(v[1] for v in verts) / n,
            sum(v[2] for v in verts) / n
        )

    eave_center = centroid(eave_vertices)
    ridge_center = centroid(ridge_vertices)

    return {
        'eave_vertices': eave_vertices,
        'ridge_vertices': ridge_vertices,
        'eave_z': z_min,
        'ridge_z': z_max,
        'eave_center': eave_center,
        'ridge_center': ridge_center,
        'slope_rise': z_max - z_min
    }


def calculate_upslope_direction(vertices: List[Tuple[float, float, float]],
                                 z_tolerance: float = 0.1) -> Tuple[float, float, float]:
    """
    Calculate the unit vector pointing up the roof slope (eave to ridge).

    This is the key function for orientation detection. By using vertex
    Z coordinates instead of face normals, we get a reliable "up the roof"
    direction regardless of how the geometry was constructed.

    Args:
        vertices: List of (x, y, z) tuples representing face vertices
        z_tolerance: Tolerance for grouping vertices at same Z level (mm)

    Returns:
        Tuple (x, y, z) unit vector pointing from eave toward ridge
    """
    eave_ridge = find_eave_and_ridge_vertices(vertices, z_tolerance)

    eave = eave_ridge['eave_center']
    ridge = eave_ridge['ridge_center']

    # Vector from eave to ridge
    dx = ridge[0] - eave[0]
    dy = ridge[1] - eave[1]
    dz = ridge[2] - eave[2]

    # Normalize
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    if length < 0.001:
        # Flat roof - no slope, return arbitrary up direction
        return (0, 0, 1)

    return (dx / length, dy / length, dz / length)


def calculate_across_roof_direction(vertices: List[Tuple[float, float, float]],
                                     upslope: Tuple[float, float, float],
                                     face_normal: Tuple[float, float, float],
                                     eave_vertices: List[Tuple[float, float, float]] = None) -> Tuple[float, float, float]:
    """
    Calculate the unit vector pointing across the roof (parallel to eave edge).

    Uses the actual eave edge direction when available, falling back to
    cross product method if eave has only one vertex.

    Args:
        vertices: List of (x, y, z) tuples (used for context, not calculation)
        upslope: Unit vector pointing up the slope
        face_normal: Unit vector normal to the face
        eave_vertices: List of vertices at the eave level (lowest Z)

    Returns:
        Tuple (x, y, z) unit vector pointing across the roof (U direction)
    """
    # Primary method: use the eave edge direction directly
    # This ensures U is truly horizontal along the eave, not a computed perpendicular
    if eave_vertices and len(eave_vertices) >= 2:
        # Find two eave vertices that are furthest apart (the eave edge endpoints)
        max_dist = 0
        best_pair = (eave_vertices[0], eave_vertices[1]) if len(eave_vertices) >= 2 else None

        for i, v1 in enumerate(eave_vertices):
            for v2 in eave_vertices[i+1:]:
                dx = v2[0] - v1[0]
                dy = v2[1] - v1[1]
                dz = v2[2] - v1[2]
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                if dist > max_dist:
                    max_dist = dist
                    best_pair = (v1, v2)

        if best_pair and max_dist > 0.001:
            v1, v2 = best_pair
            ux = v2[0] - v1[0]
            uy = v2[1] - v1[1]
            uz = v2[2] - v1[2]

            # Normalize
            length = math.sqrt(ux*ux + uy*uy + uz*uz)
            if length > 0.001:
                u_candidate = (ux / length, uy / length, uz / length)

                # Establish canonical direction: U should point in a consistent
                # "positive" direction. We define this as:
                # 1. If eave runs mainly in Y, U should point +Y
                # 2. If eave runs mainly in X, U should point +X
                # This ensures both sides of a gable roof have shingles
                # laid out in the same direction along the eave.

                # Find which horizontal axis the eave primarily runs along
                abs_x = abs(u_candidate[0])
                abs_y = abs(u_candidate[1])

                if abs_y >= abs_x:
                    # Eave runs mainly in Y direction - ensure +Y
                    if u_candidate[1] < 0:
                        u_candidate = (-u_candidate[0], -u_candidate[1], -u_candidate[2])
                else:
                    # Eave runs mainly in X direction - ensure +X
                    if u_candidate[0] < 0:
                        u_candidate = (-u_candidate[0], -u_candidate[1], -u_candidate[2])

                return u_candidate

    # Fallback: cross product method (for single-point eaves or degenerate cases)
    # Cross product: normal × upslope gives across direction
    ux = face_normal[1] * upslope[2] - face_normal[2] * upslope[1]
    uy = face_normal[2] * upslope[0] - face_normal[0] * upslope[2]
    uz = face_normal[0] * upslope[1] - face_normal[1] * upslope[0]

    # Normalize
    length = math.sqrt(ux*ux + uy*uy + uz*uz)
    if length < 0.001:
        # Degenerate case - upslope parallel to normal (shouldn't happen on real roof)
        return (1, 0, 0)

    return (ux / length, uy / length, uz / length)


def get_roof_coordinate_system(vertices: List[Tuple[float, float, float]],
                                face_normal: Tuple[float, float, float],
                                z_tolerance: float = 0.1) -> Dict:
    """
    Get a complete coordinate system for a roof face using bounding-box method.

    This replaces normal-based orientation detection with a more reliable
    approach based on vertex Z coordinates.

    Args:
        vertices: List of (x, y, z) tuples representing face vertices
        face_normal: Unit vector normal to the face (from FreeCAD)
        z_tolerance: Tolerance for grouping vertices at same Z level (mm)

    Returns:
        Dict with:
            - origin: (x, y, z) starting point (lowest-Z corner vertex)
            - u_vec: (x, y, z) unit vector across the roof (width direction)
            - v_vec: (x, y, z) unit vector up the slope (height direction)
            - normal: (x, y, z) corrected face normal (pointing outward)
            - eave_ridge_info: Dict from find_eave_and_ridge_vertices
    """
    if len(vertices) < 3:
        raise ValueError(f"Need at least 3 vertices, got {len(vertices)}")

    # Get eave/ridge info
    eave_ridge = find_eave_and_ridge_vertices(vertices, z_tolerance)

    # Calculate upslope direction (V)
    v_vec = calculate_upslope_direction(vertices, z_tolerance)

    # Calculate across direction (U) - using actual eave edge direction
    u_vec = calculate_across_roof_direction(vertices, v_vec, face_normal,
                                            eave_vertices=eave_ridge['eave_vertices'])

    # Verify coordinate system handedness
    # U × V should point in the same direction as face_normal (outward)
    # If not, flip U to make it so (preserving the outward normal)
    cross = (
        u_vec[1] * v_vec[2] - u_vec[2] * v_vec[1],
        u_vec[2] * v_vec[0] - u_vec[0] * v_vec[2],
        u_vec[0] * v_vec[1] - u_vec[1] * v_vec[0]
    )

    # Check if U × V agrees with face_normal direction
    dot = (face_normal[0] * cross[0] +
           face_normal[1] * cross[1] +
           face_normal[2] * cross[2])

    if dot < 0:
        # U × V points inward - flip U to fix handedness
        # This keeps the face_normal (outward) and V (upslope) correct
        u_vec = (-u_vec[0], -u_vec[1], -u_vec[2])

    # Use the original face_normal (it points outward from the geometry)
    corrected_normal = face_normal

    # Find origin: prefer corner vertex (2 edges) at lowest Z
    # For now, just use the first eave vertex
    origin = eave_ridge['eave_vertices'][0] if eave_ridge['eave_vertices'] else vertices[0]

    return {
        'origin': origin,
        'u_vec': u_vec,
        'v_vec': v_vec,
        'normal': corrected_normal,
        'eave_ridge_info': eave_ridge
    }


# =============================================================================
# Smart Trim: Valley/Ridge Detection (v5.0.0)
# =============================================================================

def find_coincident_edges(face1_edges: List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]],
                          face2_edges: List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]],
                          tolerance: float = 0.5) -> List[Dict]:
    """
    Find edges that are shared (coincident) between two faces.

    Args:
        face1_edges: List of edges as ((x1,y1,z1), (x2,y2,z2)) tuples
        face2_edges: List of edges as ((x1,y1,z1), (x2,y2,z2)) tuples
        tolerance: Distance tolerance for considering vertices coincident (mm)

    Returns:
        List of dicts describing coincident edges:
            - edge1: The edge from face1
            - edge2: The edge from face2
            - midpoint: (x, y, z) midpoint of the shared edge
            - length: Length of the shared edge
    """
    def points_coincident(p1, p2, tol):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        dz = p1[2] - p2[2]
        return math.sqrt(dx*dx + dy*dy + dz*dz) <= tol

    def edges_coincident(e1, e2, tol):
        # Check if e1 endpoints match e2 endpoints (in either order)
        return ((points_coincident(e1[0], e2[0], tol) and points_coincident(e1[1], e2[1], tol)) or
                (points_coincident(e1[0], e2[1], tol) and points_coincident(e1[1], e2[0], tol)))

    coincident = []
    for e1 in face1_edges:
        for e2 in face2_edges:
            if edges_coincident(e1, e2, tolerance):
                # Calculate midpoint and length
                mid = (
                    (e1[0][0] + e1[1][0]) / 2,
                    (e1[0][1] + e1[1][1]) / 2,
                    (e1[0][2] + e1[1][2]) / 2
                )
                dx = e1[1][0] - e1[0][0]
                dy = e1[1][1] - e1[0][1]
                dz = e1[1][2] - e1[0][2]
                length = math.sqrt(dx*dx + dy*dy + dz*dz)

                coincident.append({
                    'edge1': e1,
                    'edge2': e2,
                    'midpoint': mid,
                    'length': length
                })

    return coincident


def classify_roof_intersection(face1_vertices: List[Tuple[float, float, float]],
                                face2_vertices: List[Tuple[float, float, float]],
                                shared_edge: Tuple[Tuple[float, float, float], Tuple[float, float, float]],
                                z_tolerance: float = 0.1) -> Dict:
    """
    Classify a roof intersection as valley or ridge based on Z coordinates.

    The key insight: at a shared edge between two roof faces:
    - If the NON-SHARED vertices of both faces are BELOW the shared edge → RIDGE/HIP
    - If the NON-SHARED vertices of both faces are ABOVE the shared edge → VALLEY

    This is geometrically unambiguous and doesn't depend on normal directions.

    Args:
        face1_vertices: Vertices of first face
        face2_vertices: Vertices of second face
        shared_edge: The edge shared by both faces ((x1,y1,z1), (x2,y2,z2))
        z_tolerance: Tolerance for considering vertices "on" the edge (mm)

    Returns:
        Dict with:
            - classification: 'valley', 'ridge', or 'ambiguous'
            - shared_edge_z: Average Z of shared edge
            - face1_other_z: Average Z of non-shared vertices of face1
            - face2_other_z: Average Z of non-shared vertices of face2
            - confidence: 'high', 'medium', or 'low'
    """
    # Get Z of shared edge
    edge_z = (shared_edge[0][2] + shared_edge[1][2]) / 2

    def is_on_edge(vertex, edge, tol):
        # Check if vertex is one of the edge endpoints
        for ep in edge:
            dx = vertex[0] - ep[0]
            dy = vertex[1] - ep[1]
            dz = vertex[2] - ep[2]
            if math.sqrt(dx*dx + dy*dy + dz*dz) <= tol:
                return True
        return False

    # Find non-shared vertices for each face
    face1_other = [v for v in face1_vertices if not is_on_edge(v, shared_edge, z_tolerance * 5)]
    face2_other = [v for v in face2_vertices if not is_on_edge(v, shared_edge, z_tolerance * 5)]

    if not face1_other or not face2_other:
        return {
            'classification': 'ambiguous',
            'shared_edge_z': edge_z,
            'face1_other_z': None,
            'face2_other_z': None,
            'confidence': 'low',
            'reason': 'Could not identify non-shared vertices'
        }

    # Average Z of non-shared vertices
    face1_other_z = sum(v[2] for v in face1_other) / len(face1_other)
    face2_other_z = sum(v[2] for v in face2_other) / len(face2_other)

    # Classification logic
    face1_below = face1_other_z < edge_z - z_tolerance
    face1_above = face1_other_z > edge_z + z_tolerance
    face2_below = face2_other_z < edge_z - z_tolerance
    face2_above = face2_other_z > edge_z + z_tolerance

    if face1_below and face2_below:
        # Both faces slope DOWN from the shared edge → RIDGE/HIP
        classification = 'ridge'
        confidence = 'high'
    elif face1_above and face2_above:
        # Both faces slope UP from the shared edge → VALLEY
        classification = 'valley'
        confidence = 'high'
    elif (face1_below and face2_above) or (face1_above and face2_below):
        # One up, one down - this is unusual but could be a complex intersection
        classification = 'ambiguous'
        confidence = 'low'
    else:
        # Near-flat or edge case
        classification = 'ambiguous'
        confidence = 'medium'

    return {
        'classification': classification,
        'shared_edge_z': edge_z,
        'face1_other_z': face1_other_z,
        'face2_other_z': face2_other_z,
        'confidence': confidence
    }


def calculate_dihedral_angle(face1_normal: Tuple[float, float, float],
                              face2_normal: Tuple[float, float, float]) -> Dict:
    """
    Calculate the dihedral angle between two face normals.

    Args:
        face1_normal: Unit normal vector of first face
        face2_normal: Unit normal vector of second face

    Returns:
        Dict with:
            - angle_degrees: Angle between normals (0-180)
            - angle_radians: Same in radians
            - trim_angle_degrees: The angle to cut each side (angle/2 or 90-angle/2)
    """
    # Dot product of normals
    dot = (face1_normal[0] * face2_normal[0] +
           face1_normal[1] * face2_normal[1] +
           face1_normal[2] * face2_normal[2])

    # Clamp to [-1, 1] for numerical stability
    dot = max(-1.0, min(1.0, dot))

    angle_rad = math.acos(dot)
    angle_deg = math.degrees(angle_rad)

    # The trim angle is typically half the dihedral angle
    # For a 90° dihedral, each piece is cut at 45°
    trim_angle = angle_deg / 2

    return {
        'angle_degrees': angle_deg,
        'angle_radians': angle_rad,
        'trim_angle_degrees': trim_angle
    }


def analyze_roof_intersection(face1_vertices: List[Tuple[float, float, float]],
                               face1_normal: Tuple[float, float, float],
                               face1_edges: List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]],
                               face2_vertices: List[Tuple[float, float, float]],
                               face2_normal: Tuple[float, float, float],
                               face2_edges: List[Tuple[Tuple[float, float, float], Tuple[float, float, float]]],
                               tolerance: float = 0.5) -> Dict:
    """
    Complete analysis of the intersection between two roof faces.

    Combines edge detection, valley/ridge classification, and angle calculation.

    Args:
        face1_vertices: Vertices of first face
        face1_normal: Normal of first face
        face1_edges: Edges of first face
        face2_vertices: Vertices of second face
        face2_normal: Normal of second face
        face2_edges: Edges of second face
        tolerance: Distance tolerance for edge matching (mm)

    Returns:
        Dict with complete intersection analysis:
            - has_shared_edge: Whether faces share an edge
            - shared_edges: List of shared edges found
            - classification: 'valley', 'ridge', or 'ambiguous'
            - dihedral_angle: Angle information dict
            - trim_recommendation: Human-readable trim advice
    """
    # Find shared edges
    shared = find_coincident_edges(face1_edges, face2_edges, tolerance)

    if not shared:
        return {
            'has_shared_edge': False,
            'shared_edges': [],
            'classification': 'none',
            'dihedral_angle': None,
            'trim_recommendation': 'Faces do not share an edge'
        }

    # Use the longest shared edge for analysis
    longest_edge = max(shared, key=lambda e: e['length'])

    # Classify the intersection
    classification = classify_roof_intersection(
        face1_vertices, face2_vertices,
        longest_edge['edge1'],
        tolerance
    )

    # Calculate dihedral angle
    dihedral = calculate_dihedral_angle(face1_normal, face2_normal)

    # Generate recommendation
    if classification['classification'] == 'valley':
        rec = f"VALLEY: Cut shingles at {dihedral['trim_angle_degrees']:.1f}° from each side"
    elif classification['classification'] == 'ridge':
        rec = f"RIDGE/HIP: Cut shingles at {dihedral['trim_angle_degrees']:.1f}° from each side"
    else:
        rec = f"AMBIGUOUS: Dihedral angle is {dihedral['angle_degrees']:.1f}°, verify visually"

    return {
        'has_shared_edge': True,
        'shared_edges': shared,
        'classification': classification['classification'],
        'classification_details': classification,
        'dihedral_angle': dihedral,
        'trim_recommendation': rec
    }
