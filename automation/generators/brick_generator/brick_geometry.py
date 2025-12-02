"""
Brick Geometry Generator Library v3.0.0

Pure Python geometry generation for parametric brick walls.
No FreeCAD dependencies - designed for testing and reuse.

Supported bond patterns:
- Stretcher (Running) Bond: Each course offset by half brick
- English Bond: Alternating courses of stretchers and headers
- Flemish Bond: Each course alternates stretchers and headers
- Common Bond: N stretcher courses followed by 1 header course (configurable)

Returns lists of brick definitions ready for FreeCAD instantiation or other use.

Version: 3.0.0
Date: 2025-11-26
"""

import math
from typing import List, Dict, Tuple, NamedTuple


class BrickDef(NamedTuple):
    """Represents a single brick in the wall."""
    index: int                    # Sequential brick number
    u: float                      # Position along width (local coords)
    v: float                      # Position along height (local coords)
    course: int                   # Which course (0-indexed from bottom)
    brick_type: str               # 'stretcher' or 'header'
    width: float                  # Brick dimension along U
    height: float                 # Brick dimension along V (always same)
    depth: float                  # Brick dimension perpendicular to wall


class BrickGeometry:
    """
    Generates brick wall geometry for a rectangular wall face.
    
    Wall coordinate system:
    - U axis: horizontal (left to right), length u_length
    - V axis: vertical (bottom to top), length v_length
    - Normal: perpendicular to wall (out)
    """
    
    def __init__(self, u_length: float, v_length: float,
                 brick_width: float, brick_height: float, brick_depth: float,
                 mortar: float, bond_type: str = 'stretcher',
                 common_bond_count: int = 5):
        """
        Initialize brick geometry generator.
        
        Args:
            u_length: Wall width (mm)
            v_length: Wall height (mm)
            brick_width: Brick width along wall (mm) - stretcher orientation
            brick_height: Brick height (always along V) (mm)
            brick_depth: Brick depth perpendicular to wall (mm)
            mortar: Mortar joint thickness (mm)
            bond_type: 'stretcher', 'english', 'flemish', or 'common'
            common_bond_count: For common bond, number of stretcher courses between headers
        """
        self.u_length = u_length
        self.v_length = v_length
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.brick_depth = brick_depth
        self.mortar = mortar
        self.bond_type = bond_type.lower()
        self.common_bond_count = common_bond_count
        
        # Validate inputs
        if any(x <= 0 for x in [u_length, v_length, brick_width, brick_height, brick_depth, mortar]):
            raise ValueError("All dimensions must be positive")
        
        if self.bond_type not in ['stretcher', 'english', 'flemish', 'common']:
            raise ValueError(f"Unknown bond type: {bond_type}")
        
        if self.bond_type == 'common' and common_bond_count < 1:
            raise ValueError("common_bond_count must be at least 1")
        
        # Pre-calculate spacing
        self.stretcher_spacing_u = brick_width + mortar
        self.header_spacing_u = brick_depth + mortar
        self.course_spacing_v = brick_height + mortar
        
        # Calculate coverage metrics
        self.num_courses = math.ceil(v_length / self.course_spacing_v) + 2
        
    def generate(self) -> Dict:
        """
        Generate complete brick layout.
        
        Returns:
            Dictionary with:
                'bricks': List of BrickDef objects
                'metadata': Dict with generation metadata
        """
        if self.bond_type == 'stretcher':
            bricks = self._generate_stretcher_bond()
        elif self.bond_type == 'english':
            bricks = self._generate_english_bond()
        elif self.bond_type == 'flemish':
            bricks = self._generate_flemish_bond()
        elif self.bond_type == 'common':
            bricks = self._generate_common_bond()
        
        # Add sequential indices
        for i, brick in enumerate(bricks):
            bricks[i] = brick._replace(index=i)
        
        return {
            'bricks': bricks,
            'metadata': {
                'bond_type': self.bond_type,
                'num_courses': self.num_courses,
                'total_bricks': len(bricks),
                'u_length': self.u_length,
                'v_length': self.v_length,
                'brick_width': self.brick_width,
                'brick_height': self.brick_height,
                'brick_depth': self.brick_depth,
                'mortar': self.mortar,
            }
        }
    
    def _generate_stretcher_bond(self) -> List[BrickDef]:
        """
        Stretcher (Running) Bond.
        Each course offset by half brick width.
        All bricks are stretchers.
        """
        bricks = []
        
        for course in range(self.num_courses):
            v = course * self.course_spacing_v
            
            # Offset alternating courses by half stretcher width
            offset = (self.stretcher_spacing_u / 2) if (course % 2) else 0
            
            u = offset - self.stretcher_spacing_u  # Start before wall edge
            
            while u < self.u_length + self.stretcher_spacing_u:
                brick = BrickDef(
                    index=0,  # Will be filled in by generate()
                    u=u,
                    v=v,
                    course=course,
                    brick_type='stretcher',
                    width=self.brick_width,
                    height=self.brick_height,
                    depth=self.brick_depth
                )
                bricks.append(brick)
                u += self.stretcher_spacing_u
        
        return bricks
    
    def _generate_english_bond(self) -> List[BrickDef]:
        """
        English Bond.
        Alternating courses of stretchers and headers.
        """
        bricks = []
        
        for course in range(self.num_courses):
            v = course * self.course_spacing_v
            is_header_course = (course % 2) == 1
            
            if is_header_course:
                # Header course
                u = -self.header_spacing_u
                while u < self.u_length + self.header_spacing_u:
                    brick = BrickDef(
                        index=0,
                        u=u,
                        v=v,
                        course=course,
                        brick_type='header',
                        width=self.brick_depth,  # Headers are rotated
                        height=self.brick_height,
                        depth=self.brick_width
                    )
                    bricks.append(brick)
                    u += self.header_spacing_u
            else:
                # Stretcher course
                u = -self.stretcher_spacing_u
                while u < self.u_length + self.stretcher_spacing_u:
                    brick = BrickDef(
                        index=0,
                        u=u,
                        v=v,
                        course=course,
                        brick_type='stretcher',
                        width=self.brick_width,
                        height=self.brick_height,
                        depth=self.brick_depth
                    )
                    bricks.append(brick)
                    u += self.stretcher_spacing_u
        
        return bricks
    
    def _generate_flemish_bond(self) -> List[BrickDef]:
        """
        Flemish Bond.
        Each course alternates individual stretchers and headers.
        Pattern: Stretcher, Header, Stretcher, Header, ... across each course.
        """
        bricks = []
        
        for course in range(self.num_courses):
            v = course * self.course_spacing_v
            
            # Determine if we start with stretcher or header
            # Typical pattern: even courses start with stretcher, odd with header
            start_with_stretcher = (course % 2) == 0
            
            u = -self.stretcher_spacing_u
            is_stretcher = start_with_stretcher
            
            while u < self.u_length + self.header_spacing_u:
                if is_stretcher:
                    brick = BrickDef(
                        index=0,
                        u=u,
                        v=v,
                        course=course,
                        brick_type='stretcher',
                        width=self.brick_width,
                        height=self.brick_height,
                        depth=self.brick_depth
                    )
                    bricks.append(brick)
                    u += self.stretcher_spacing_u
                else:
                    brick = BrickDef(
                        index=0,
                        u=u,
                        v=v,
                        course=course,
                        brick_type='header',
                        width=self.brick_depth,
                        height=self.brick_height,
                        depth=self.brick_width
                    )
                    bricks.append(brick)
                    u += self.header_spacing_u
                
                is_stretcher = not is_stretcher
        
        return bricks
    
    def _generate_common_bond(self) -> List[BrickDef]:
        """
        Common Bond.
        N stretcher courses followed by 1 header course, repeating.
        N = self.common_bond_count
        """
        bricks = []
        course = 0
        
        while course < self.num_courses:
            # Generate stretcher courses
            for _ in range(self.common_bond_count):
                if course >= self.num_courses:
                    break
                
                v = course * self.course_spacing_v
                
                # Offset alternating stretcher courses by half width
                offset = (self.stretcher_spacing_u / 2) if (_ % 2) else 0
                u = offset - self.stretcher_spacing_u
                
                while u < self.u_length + self.stretcher_spacing_u:
                    brick = BrickDef(
                        index=0,
                        u=u,
                        v=v,
                        course=course,
                        brick_type='stretcher',
                        width=self.brick_width,
                        height=self.brick_height,
                        depth=self.brick_depth
                    )
                    bricks.append(brick)
                    u += self.stretcher_spacing_u
                
                course += 1
            
            # Generate header course
            if course < self.num_courses:
                v = course * self.course_spacing_v
                u = -self.header_spacing_u
                
                while u < self.u_length + self.header_spacing_u:
                    brick = BrickDef(
                        index=0,
                        u=u,
                        v=v,
                        course=course,
                        brick_type='header',
                        width=self.brick_depth,
                        height=self.brick_height,
                        depth=self.brick_width
                    )
                    bricks.append(brick)
                    u += self.header_spacing_u
                
                course += 1
        
        return bricks
