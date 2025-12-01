"""
Smart Trim Geometry Library v1.0.1

Pure Python geometry functions for detecting and classifying edges for trim application.
Used by both clapboard_trim and shingle_trim generators.

No dependencies on FreeCAD.Part, FreeCAD.Vector, etc.
Uses standard Python types (tuples, dicts, lists) for I/O.

Version History:
- 1.0.1: Removed filter_edges_for_trim (replaced by is_perimeter_edge in macro)
         The bbox-based perimeter check is more robust than signature matching
- 1.0.0: Initial release

Edge classification:
- VERTICAL: edges aligned with the wall's vertical axis (within angle_tolerance)
- HORIZONTAL: edges perpendicular to vertical (within angle_tolerance)
- GABLE: diagonal edges (neither vertical nor horizontal)

Trim types:
- corner_trim: applied to VERTICAL edges
- eave_trim: applied to HORIZONTAL edges
- gable_trim: applied to GABLE edges
"""

import math
from typing import List, Tuple, Dict, Optional, Literal


# Edge classification types
EdgeType = Literal['vertical', 'horizontal', 'gable']


def vector_normalize(v: Tuple[float, float, float]) -> Tuple[float, float, float]:
    """
    Normalize a 3D vector to unit length.
    
    Args:
        v: Tuple of (x, y, z)
    
    Returns:
        Normalized tuple, or (0, 0, 0) if input is zero vector
    """
    length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if length < 1e-10:
        return (0, 0, 0)
    return (v[0]/length, v[1]/length, v[2]/length)


def vector_dot(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
    """Dot product of two 3D vectors."""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]


def vector_angle_degrees(v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
    """
    Calculate angle between two vectors in degrees.
    
    Args:
        v1, v2: Unit vectors (or will be normalized)
    
    Returns:
        Angle in degrees (0-180)
    """
    v1_norm = vector_normalize(v1)
    v2_norm = vector_normalize(v2)
    
    dot = vector_dot(v1_norm, v2_norm)
    # Clamp to [-1, 1] to avoid numerical errors in acos
    dot = max(-1.0, min(1.0, dot))
    
    radians = math.acos(dot)
    return math.degrees(radians)


def classify_edge(edge_direction: Tuple[float, float, float],
                 vertical_axis: str = 'z',
                 angle_tolerance: float = 5.0) -> EdgeType:
    """
    Classify an edge as vertical, horizontal, or gable based on its direction.
    
    Args:
        edge_direction: Normalized direction vector of the edge (x, y, z)
        vertical_axis: 'x', 'y', or 'z' - the axis that represents "up"
        angle_tolerance: Degrees - edges within this angle are classified as vertical/horizontal
    
    Returns:
        'vertical', 'horizontal', or 'gable'
    
    Logic:
        - If edge is parallel to vertical_axis → VERTICAL
        - If edge is perpendicular to vertical_axis → HORIZONTAL
        - Otherwise → GABLE
    """
    # Define vertical and horizontal direction vectors
    if vertical_axis == 'z':
        vertical = (0, 0, 1)
        horizontal = (0, 1, 0)  # Could be x or y, pick one reference
    elif vertical_axis == 'y':
        vertical = (0, 1, 0)
        horizontal = (1, 0, 0)
    elif vertical_axis == 'x':
        vertical = (1, 0, 0)
        horizontal = (0, 1, 0)
    else:
        raise ValueError(f"vertical_axis must be 'x', 'y', or 'z', got {vertical_axis}")
    
    # Normalize edge direction
    edge_norm = vector_normalize(edge_direction)
    
    # Angle to vertical axis
    angle_to_vertical = vector_angle_degrees(edge_norm, vertical)
    
    # An edge is vertical if it's parallel (0°) or antiparallel (180°) to vertical axis
    if angle_to_vertical < angle_tolerance or angle_to_vertical > (180 - angle_tolerance):
        return 'vertical'
    
    # An edge is horizontal if it's perpendicular (90°) to vertical axis
    # Allow tolerance around 90°
    if abs(angle_to_vertical - 90.0) < angle_tolerance:
        return 'horizontal'
    
    # Otherwise it's a gable edge
    return 'gable'


def classify_edges(edges: List[Dict], 
                  vertical_axis: str = 'z',
                  angle_tolerance: float = 5.0) -> List[Tuple[int, EdgeType]]:
    """
    Classify multiple edges.
    
    Args:
        edges: List of edge dicts, each with 'start' and 'end' keys (tuples of x,y,z)
        vertical_axis: 'x', 'y', or 'z'
        angle_tolerance: Degrees
    
    Returns:
        List of (edge_index, classification) tuples
    """
    results = []
    
    for i, edge in enumerate(edges):
        start = edge.get('start', (0, 0, 0))
        end = edge.get('end', (0, 0, 0))
        
        # Calculate direction vector
        direction = (
            end[0] - start[0],
            end[1] - start[1],
            end[2] - start[2]
        )
        
        classification = classify_edge(direction, vertical_axis, angle_tolerance)
        results.append((i, classification))
    
    return results


def filter_edges_for_trim(edges, face_wires=None, 
                         vertical_axis='z',
                         skip_bottom=True,
                         bottom_tolerance=1.0) -> List[Tuple[int, bool]]:
    """
    Filter edges to identify which should get trim.
    
    Skip rules:
    - Bottom edge (minimum position on vertical axis)
    - Edges that are part of holes (door/window openings)
    
    Args:
        edges: List of edge dicts with 'start', 'end', 'edge_obj' keys
        face_wires: List of FreeCAD wire objects from a face (wires[0] is outer, rest are holes)
        vertical_axis: 'x', 'y', or 'z'
        skip_bottom: If True, skip the bottom edge
        bottom_tolerance: Distance tolerance to identify bottom edge
    
    Returns:
        List of (edge_index, should_have_trim) tuples
    """
    results = []
    
    # Get the bounding box from edges to find bottom
    if edges:
        xs = [e['start'][0] for e in edges] + [e['end'][0] for e in edges]
        ys = [e['start'][1] for e in edges] + [e['end'][1] for e in edges]
        zs = [e['start'][2] for e in edges] + [e['end'][2] for e in edges]
        
        bbox = {
            'x_min': min(xs), 'x_max': max(xs),
            'y_min': min(ys), 'y_max': max(ys),
            'z_min': min(zs), 'z_max': max(zs),
        }
    else:
        return results
    
    # Get hole edge signatures from hole wires (provided by macro)
    hole_edge_signatures = set()
    if face_wires and len(face_wires) > 0:
        for hole_wire in face_wires:
            for hole_edge in hole_wire.Edges:
                try:
                    start = hole_edge.valueAt(hole_edge.FirstParameter)
                    end = hole_edge.valueAt(hole_edge.LastParameter)
                    # Round to 2 decimal places (0.01mm tolerance) for more lenient matching
                    sig = (
                        round(start.x, 2), round(start.y, 2), round(start.z, 2),
                        round(end.x, 2), round(end.y, 2), round(end.z, 2)
                    )
                    hole_edge_signatures.add(sig)
                    rev_sig = (
                        round(end.x, 2), round(end.y, 2), round(end.z, 2),
                        round(start.x, 2), round(start.y, 2), round(start.z, 2)
                    )
                    hole_edge_signatures.add(rev_sig)
                except:
                    pass
    
    for i, edge in enumerate(edges):
        should_trim = True
        
        # Skip bottom edge
        if skip_bottom:
            start = edge.get('start', (0, 0, 0))
            end = edge.get('end', (0, 0, 0))
            
            # Get min position on vertical axis
            if vertical_axis == 'z':
                v_min = bbox.get('z_min', 0)
                start_v = start[2]
                end_v = end[2]
            elif vertical_axis == 'y':
                v_min = bbox.get('y_min', 0)
                start_v = start[1]
                end_v = end[1]
            else:  # 'x'
                v_min = bbox.get('x_min', 0)
                start_v = start[0]
                end_v = end[0]
            
            # If both endpoints are at the minimum, skip this edge
            if abs(start_v - v_min) < bottom_tolerance and abs(end_v - v_min) < bottom_tolerance:
                should_trim = False
                results.append((i, should_trim))
                continue
        
        # Check if this edge is part of a hole using traditional hole wires
        if 'edge_obj' in edge and hole_edge_signatures:
            edge_obj = edge['edge_obj']
            try:
                start = edge_obj.valueAt(edge_obj.FirstParameter)
                end = edge_obj.valueAt(edge_obj.LastParameter)
                sig = (
                    round(start.x, 2), round(start.y, 2), round(start.z, 2),
                    round(end.x, 2), round(end.y, 2), round(end.z, 2)
                )
                rev_sig = (
                    round(end.x, 2), round(end.y, 2), round(end.z, 2),
                    round(start.x, 2), round(start.y, 2), round(start.z, 2)
                )
                
                if sig in hole_edge_signatures or rev_sig in hole_edge_signatures:
                    should_trim = False
            except:
                pass
        
        results.append((i, should_trim))
    
    return results


def get_edge_midpoint(edge: Dict) -> Tuple[float, float, float]:
    """Get the midpoint of an edge."""
    start = edge.get('start', (0, 0, 0))
    end = edge.get('end', (0, 0, 0))
    return (
        (start[0] + end[0]) / 2,
        (start[1] + end[1]) / 2,
        (start[2] + end[2]) / 2
    )


def get_edge_length(edge: Dict) -> float:
    """Get the length of an edge."""
    start = edge.get('start', (0, 0, 0))
    end = edge.get('end', (0, 0, 0))
    return math.sqrt(
        (end[0] - start[0])**2 +
        (end[1] - start[1])**2 +
        (end[2] - start[2])**2
    )


def validate_trim_parameters(trim_width: float, 
                            trim_thickness: float) -> Tuple[bool, List[str]]:
    """
    Validate trim parameters.
    
    Args:
        trim_width: Width of trim profile in mm
        trim_thickness: Thickness of trim in mm
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if trim_width <= 0:
        errors.append(f"trim_width must be positive, got {trim_width}")
    
    if trim_thickness <= 0:
        errors.append(f"trim_thickness must be positive, got {trim_thickness}")
    
    return len(errors) == 0, errors
