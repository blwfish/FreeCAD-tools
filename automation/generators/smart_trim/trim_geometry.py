"""
Trim Geometry Library
====================

Pure Python geometry library for architectural trim generation.
Provides corner detection, classification, and trim piece geometry generation.

This library works with FreeCAD Part::TopoShape objects but contains no FreeCAD
dependencies in the core geometry functions - similar to clapboard_geometry.py.

Author: Brian White
Version: 1.0.0
License: MIT
"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import math


class CornerType(Enum):
    """Types of corners detected in face boundaries."""
    EXTERNAL = "external"  # Convex corner (< 180°)
    INTERNAL = "internal"  # Concave corner (> 180°)
    STRAIGHT = "straight"  # Collinear edges (~180°)


@dataclass
class Corner:
    """Represents a detected corner in a face boundary."""
    position: Tuple[float, float, float]  # 3D coordinates (x, y, z)
    corner_type: CornerType
    angle: float  # Interior angle in degrees
    edge_before: object  # FreeCAD Edge leading into corner
    edge_after: object   # FreeCAD Edge leading out of corner
    
    def miter_angle(self) -> float:
        """Calculate the miter cut angle for this corner."""
        # For a corner with interior angle α, each miter piece is cut at α/2
        return self.angle / 2.0


def get_face_boundary_edges(face) -> List:
    """
    Extract ordered boundary edges from a face.
    
    Args:
        face: FreeCAD Face object
        
    Returns:
        List of Edge objects forming the face boundary, in order
    """
    # Get the outer wire of the face
    outer_wire = face.OuterWire
    
    if not outer_wire.isClosed():
        raise ValueError("Face outer wire is not closed - cannot detect corners")
    
    # Return ordered edges
    return outer_wire.OrderedEdges


def get_edge_vector(edge, at_end: bool = False):
    """
    Get the direction vector of an edge at its start or end.
    
    Args:
        edge: FreeCAD Edge object
        at_end: If True, get vector at end; if False, get vector at start
        
    Returns:
        FreeCAD.Vector representing edge direction
    """
    if at_end:
        # Get tangent at the end of the edge
        return edge.tangentAt(edge.LastParameter)
    else:
        # Get tangent at the start of the edge
        return edge.tangentAt(edge.FirstParameter)


def calculate_interior_angle(edge_before, edge_after, face=None) -> float:
    """
    Calculate the interior angle between two consecutive edges.
    
    The interior angle is the angle measured on the "inside" of the polygon.
    
    Key insight: getAngle() gives the turn angle (0-180°).
    - For external corners (convex): interior_angle = 180° - turn_angle  
    - For internal corners (concave): interior_angle = 180° + turn_angle
    
    Args:
        edge_before: Edge leading into the corner
        edge_after: Edge leading out of the corner
        face: Optional face object (currently unused)
        
    Returns:
        Interior angle in degrees (0-360)
    """
    # Get direction vectors
    vec_in = get_edge_vector(edge_before, at_end=True)
    vec_out = get_edge_vector(edge_after, at_end=False)
    
    # getAngle() returns the turn angle (always 0-180°)
    turn_angle_rad = vec_in.getAngle(vec_out)
    turn_angle_deg = math.degrees(turn_angle_rad)
    
    # Use cross product to determine turn direction
    cross = vec_in.cross(vec_out)
    
    # For a face in the XY plane with normal pointing up (+Z):
    # - Positive Z cross product → left turn → external corner (convex)
    # - Negative Z cross product → right turn → internal corner (concave)
    
    if cross.z > 0:
        # External corner (convex): interior = 180 - turn
        return 180.0 - turn_angle_deg
    else:
        # Internal corner (concave): interior = 180 + turn
        return 180.0 + turn_angle_deg


def classify_corner(angle: float, tolerance: float = 5.0) -> CornerType:
    """
    Classify a corner based on its interior angle.
    
    Args:
        angle: Interior angle in degrees
        tolerance: Degrees of tolerance for "straight" classification
        
    Returns:
        CornerType enum value
    """
    if abs(angle - 180.0) < tolerance:
        return CornerType.STRAIGHT
    elif angle < 180.0:
        return CornerType.EXTERNAL
    else:
        return CornerType.INTERNAL


def detect_corners(face, angle_tolerance: float = 5.0) -> List[Corner]:
    """
    Detect all corners in a face boundary and classify them.
    
    Args:
        face: FreeCAD Face object
        angle_tolerance: Tolerance in degrees for classifying straight corners
        
    Returns:
        List of Corner objects, ordered around the face boundary
    """
    edges = get_face_boundary_edges(face)
    corners = []
    
    num_edges = len(edges)
    
    for i in range(num_edges):
        edge_before = edges[i]
        edge_after = edges[(i + 1) % num_edges]  # Wrap around to first edge
        
        # Get the vertex position where these edges meet
        # The end vertex of edge_before should match start vertex of edge_after
        vertex_pos = edge_before.valueAt(edge_before.LastParameter)
        position = (vertex_pos.x, vertex_pos.y, vertex_pos.z)
        
        # Calculate interior angle
        angle = calculate_interior_angle(edge_before, edge_after)
        
        # Classify the corner
        corner_type = classify_corner(angle, angle_tolerance)
        
        # Create Corner object
        corner = Corner(
            position=position,
            corner_type=corner_type,
            angle=angle,
            edge_before=edge_before,
            edge_after=edge_after
        )
        
        corners.append(corner)
    
    return corners


def filter_corners_for_trim(corners: List[Corner], 
                            include_straight: bool = False) -> List[Corner]:
    """
    Filter corners to only those that need trim pieces.
    
    Args:
        corners: List of all detected corners
        include_straight: If True, include straight corners in results
        
    Returns:
        List of corners that need trim (typically external and internal only)
    """
    if include_straight:
        return corners
    else:
        return [c for c in corners if c.corner_type != CornerType.STRAIGHT]


def analyze_face_for_trim(face, angle_tolerance: float = 5.0) -> Dict:
    """
    Complete analysis of a face for trim placement.
    
    Args:
        face: FreeCAD Face object
        angle_tolerance: Tolerance for straight corner detection
        
    Returns:
        Dictionary with analysis results:
        - 'all_corners': All detected corners
        - 'external_corners': External corners only
        - 'internal_corners': Internal corners only
        - 'trim_corners': Corners needing trim (external + internal)
        - 'straight_edges': Edges between straight corners
    """
    corners = detect_corners(face, angle_tolerance)
    
    external = [c for c in corners if c.corner_type == CornerType.EXTERNAL]
    internal = [c for c in corners if c.corner_type == CornerType.INTERNAL]
    trim_corners = external + internal
    
    return {
        'all_corners': corners,
        'external_corners': external,
        'internal_corners': internal,
        'trim_corners': trim_corners,
        'num_corners': len(corners),
        'num_external': len(external),
        'num_internal': len(internal),
    }


# ============================================================================
# TRIM PROFILE GENERATION
# ============================================================================

def create_simple_rectangular_profile(width: float, height: float):
    """
    Create a simple rectangular trim profile.
    
    Args:
        width: Profile width (perpendicular to wall)
        height: Profile height (parallel to wall)
        
    Returns:
        FreeCAD Wire representing the profile cross-section
    """
    import Part
    import FreeCAD as App
    
    # Simple rectangle profile
    v1 = App.Vector(0, 0, 0)
    v2 = App.Vector(width, 0, 0)
    v3 = App.Vector(width, height, 0)
    v4 = App.Vector(0, height, 0)
    
    edges = [
        Part.LineSegment(v1, v2).toShape(),
        Part.LineSegment(v2, v3).toShape(),
        Part.LineSegment(v3, v4).toShape(),
        Part.LineSegment(v4, v1).toShape(),
    ]
    
    return Part.Wire(edges)


def create_beveled_profile(width: float, height: float, bevel: float):
    """
    Create a beveled trim profile (chamfered edge).
    
    Args:
        width: Profile width
        height: Profile height  
        bevel: Bevel distance (cut at 45°)
        
    Returns:
        FreeCAD Wire representing the beveled profile
    """
    import Part
    import FreeCAD as App
    
    # Beveled rectangle with 45° chamfer on outer edge
    v1 = App.Vector(0, 0, 0)
    v2 = App.Vector(width - bevel, 0, 0)
    v3 = App.Vector(width, bevel, 0)
    v4 = App.Vector(width, height, 0)
    v5 = App.Vector(0, height, 0)
    
    edges = [
        Part.LineSegment(v1, v2).toShape(),
        Part.LineSegment(v2, v3).toShape(),
        Part.LineSegment(v3, v4).toShape(),
        Part.LineSegment(v4, v5).toShape(),
        Part.LineSegment(v5, v1).toShape(),
    ]
    
    return Part.Wire(edges)


# ============================================================================
# TRIM GENERATION
# ============================================================================

def create_straight_trim_segment(edge, profile_wire, face=None, name: str = "TrimSegment"):
    """
    Create a straight trim piece by sweeping a profile along an edge.
    
    The profile is positioned and oriented relative to the edge, with the
    trim extending perpendicular to the face.
    
    Args:
        edge: FreeCAD Edge to sweep along
        profile_wire: Profile cross-section (Wire)
        face: Optional Face for orientation (needed for proper positioning)
        name: Name for the resulting shape
        
    Returns:
        FreeCAD solid object (swept profile)
    """
    import Part
    import FreeCAD as App
    
    # Create path from edge
    path = Part.Wire([edge])
    
    # Get edge tangent at start
    tangent = edge.tangentAt(edge.FirstParameter)
    tangent.normalize()
    
    # Get face normal if available, otherwise use Z-up
    if face:
        # Get face normal at a point on the edge
        edge_start = edge.valueAt(edge.FirstParameter)
        u, v = face.Surface.parameter(edge_start)
        normal = face.normalAt(u, v)
        normal.normalize()
    else:
        normal = App.Vector(0, 0, 1)
    
    # Calculate binormal (perpendicular to both tangent and normal)
    # This is the direction the trim extends FROM the wall
    binormal = tangent.cross(normal)
    binormal.normalize()
    
    # Position profile at edge start
    # The profile should be positioned so it extends outward from the face
    # Profile is defined with base at origin, extending in +X and +Y
    # We need to:
    # 1. Rotate profile so its "width" direction aligns with binormal (outward from wall)
    # 2. Rotate profile so its "height" direction aligns with normal (up the wall)
    # 3. Position it at the edge
    
    # Create placement matrix
    # X axis = binormal (trim extends outward)
    # Y axis = tangent (along edge)
    # Z axis = normal (up the wall)
    
    # But wait - profile is in XY plane, so we need:
    # Profile X (width) → binormal (outward from wall)
    # Profile Y (height) → normal (up/along wall)
    # Sweep direction → tangent (along edge)
    
    placement = App.Placement()
    placement.Base = edge.valueAt(edge.FirstParameter)
    
    # Create rotation from profile orientation to edge orientation
    # Profile is in XY plane, we want X→binormal, Y→normal, Z→tangent
    from FreeCAD import Rotation, Matrix
    
    # Build rotation matrix
    # Columns are the new basis vectors
    m = Matrix()
    m.A11, m.A21, m.A31 = binormal.x, binormal.y, binormal.z
    m.A12, m.A22, m.A32 = normal.x, normal.y, normal.z  
    m.A13, m.A23, m.A33 = tangent.x, tangent.y, tangent.z
    m.A14, m.A24, m.A34, m.A44 = 0, 0, 0, 1
    
    placement.Matrix = m
    
    # Transform profile to positioned orientation
    oriented_profile = profile_wire.copy()
    oriented_profile.Placement = placement
    
    # Now sweep the oriented profile along the path
    # Use makePipeShell with solid=True, isFrenet=True for proper orientation
    try:
        sweep = oriented_profile.makePipeShell([path], True, True)
        return sweep
    except Exception as e:
        # Fallback: simpler sweep if the above fails
        print(f"Warning: Advanced sweep failed ({e}), using simple sweep")
        sweep = profile_wire.makePipeShell([path], True, False)
        return sweep


def create_mitered_corner_piece(corner: Corner, profile_wire, 
                                edge_length_before: float = 10.0,
                                edge_length_after: float = 10.0):
    """
    Create a mitered corner trim piece.
    
    Args:
        corner: Corner object with angle and edge information
        profile_wire: Profile cross-section
        edge_length_before: Length of trim extending before corner
        edge_length_after: Length of trim extending after corner
        
    Returns:
        Tuple of (piece_before, piece_after) - two mitered trim pieces
    """
    import Part
    import FreeCAD as App
    
    # This is a placeholder - full implementation requires:
    # 1. Extract partial edges before/after corner
    # 2. Create swept geometry for each
    # 3. Apply miter cuts at the proper angles
    # 4. Return both pieces
    
    # TODO: Implement full mitered corner generation
    raise NotImplementedError("Mitered corner generation not yet implemented")


# ============================================================================
# COMPLETE TRIM GENERATION
# ============================================================================

def generate_trim_for_face(face, profile_wire, 
                          include_corners: bool = True,
                          corner_treatment: str = "mitered") -> List:
    """
    Generate complete trim for a face boundary.
    
    Args:
        face: FreeCAD Face object
        profile_wire: Trim profile cross-section
        include_corners: Whether to generate corner pieces
        corner_treatment: "mitered" or "straight" corners
        
    Returns:
        List of trim piece solids
    """
    # Analyze the face
    analysis = analyze_face_for_trim(face)
    corners = analysis['all_corners']
    
    trim_pieces = []
    
    # Generate straight segments between corners
    edges = get_face_boundary_edges(face)
    
    for edge in edges:
        segment = create_straight_trim_segment(edge, profile_wire, face)
        trim_pieces.append(segment)
    
    # TODO: Add corner piece generation when mitered corners are implemented
    
    return trim_pieces


# Example usage when called from FreeCAD macro:
"""
import FreeCAD as App
import trim_corner_detection as tcd

# Get selected face
sel = Gui.Selection.getSelectionEx()
if sel and sel[0].HasSubObjects:
    face = sel[0].SubObjects[0]
    
    # Analyze the face
    analysis = tcd.analyze_face_for_trim(face)
    
    print(f"Found {analysis['num_corners']} corners:")
    print(f"  - {analysis['num_external']} external corners")
    print(f"  - {analysis['num_internal']} internal corners")
    
    # Process each corner that needs trim
    for corner in analysis['trim_corners']:
        print(f"Corner at {corner.position}:")
        print(f"  Type: {corner.corner_type.value}")
        print(f"  Angle: {corner.angle:.1f}°")
        print(f"  Miter cut: {corner.miter_angle():.1f}°")
"""
