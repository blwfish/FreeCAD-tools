# Mesh Utilities
# Heightmap to mesh conversion, validation, optimization, and export.

import numpy as np
from typing import Optional, Tuple, Dict, Any, List


class MeshUtils:
    """Convert heightmaps to triangle meshes and perform mesh operations.

    Handles the critical step of turning 2D heightmap data into
    watertight 3D meshes suitable for CNC machining.
    """

    @staticmethod
    def heightmap_to_mesh(
        heightmap: np.ndarray,
        resolution: float,
        base_thickness: float = 0.25,
        closed: bool = True,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert a 2D heightmap to a triangle mesh.

        Creates a mesh with the terrain surface on top, flat bottom,
        and side walls (if closed=True) forming a watertight solid.

        Args:
            heightmap: 2D array of Z elevations (inches)
            resolution: Grid spacing in inches
            base_thickness: Thickness of material below lowest point (inches)
            closed: If True, add bottom face and side walls for watertight mesh

        Returns:
            (vertices, faces) — vertices is Nx3 float array,
            faces is Mx3 int array of vertex indices
        """
        rows, cols = heightmap.shape
        z_min = np.min(heightmap)
        z_base = z_min - base_thickness

        # --- Top surface vertices ---
        top_vertices = []
        for i in range(rows):
            for j in range(cols):
                x = j * resolution
                y = i * resolution
                z = heightmap[i, j]
                top_vertices.append([x, y, z])

        top_vertices = np.array(top_vertices, dtype=np.float64)
        n_top = len(top_vertices)

        # --- Top surface faces (two triangles per grid cell) ---
        top_faces = []
        for i in range(rows - 1):
            for j in range(cols - 1):
                # Vertex indices in the top surface grid
                v00 = i * cols + j
                v01 = i * cols + (j + 1)
                v10 = (i + 1) * cols + j
                v11 = (i + 1) * cols + (j + 1)
                # Two triangles (consistent winding for outward normals)
                top_faces.append([v00, v10, v01])
                top_faces.append([v01, v10, v11])

        if not closed:
            return top_vertices, np.array(top_faces, dtype=np.int32)

        # --- Bottom surface ---
        bottom_vertices = []
        for i in range(rows):
            for j in range(cols):
                x = j * resolution
                y = i * resolution
                bottom_vertices.append([x, y, z_base])

        bottom_vertices = np.array(bottom_vertices, dtype=np.float64)

        # Bottom faces (reversed winding for outward normals pointing down)
        bottom_faces = []
        for i in range(rows - 1):
            for j in range(cols - 1):
                v00 = n_top + i * cols + j
                v01 = n_top + i * cols + (j + 1)
                v10 = n_top + (i + 1) * cols + j
                v11 = n_top + (i + 1) * cols + (j + 1)
                bottom_faces.append([v00, v01, v10])
                bottom_faces.append([v01, v11, v10])

        # --- Side walls ---
        side_faces = []

        # Front wall (i=0)
        for j in range(cols - 1):
            t0 = j
            t1 = j + 1
            b0 = n_top + j
            b1 = n_top + j + 1
            side_faces.append([t0, t1, b0])
            side_faces.append([t1, b1, b0])

        # Back wall (i=rows-1)
        for j in range(cols - 1):
            t0 = (rows - 1) * cols + j
            t1 = (rows - 1) * cols + j + 1
            b0 = n_top + (rows - 1) * cols + j
            b1 = n_top + (rows - 1) * cols + j + 1
            side_faces.append([t0, b0, t1])
            side_faces.append([t1, b0, b1])

        # Left wall (j=0)
        for i in range(rows - 1):
            t0 = i * cols
            t1 = (i + 1) * cols
            b0 = n_top + i * cols
            b1 = n_top + (i + 1) * cols
            side_faces.append([t0, b0, t1])
            side_faces.append([t1, b0, b1])

        # Right wall (j=cols-1)
        for i in range(rows - 1):
            t0 = i * cols + (cols - 1)
            t1 = (i + 1) * cols + (cols - 1)
            b0 = n_top + i * cols + (cols - 1)
            b1 = n_top + (i + 1) * cols + (cols - 1)
            side_faces.append([t0, t1, b0])
            side_faces.append([t1, b1, b0])

        # Combine all geometry
        vertices = np.vstack([top_vertices, bottom_vertices])
        faces = np.array(top_faces + bottom_faces + side_faces, dtype=np.int32)

        return vertices, faces

    @staticmethod
    def validate_mesh(
        vertices: np.ndarray,
        faces: np.ndarray,
    ) -> Dict[str, Any]:
        """Validate mesh geometry for CNC suitability.

        Args:
            vertices: Nx3 vertex positions
            faces: Mx3 face vertex indices

        Returns:
            Dict with validation results:
            - valid: bool
            - vertex_count: int
            - face_count: int
            - bounding_box: [x, y, z] dimensions
            - issues: list of warning strings
        """
        issues = []
        n_verts = len(vertices)
        n_faces = len(faces)

        # Check for NaN/Inf
        if np.any(~np.isfinite(vertices)):
            issues.append("Vertices contain NaN or Inf values")

        # Check face indices
        if np.any(faces < 0) or np.any(faces >= n_verts):
            issues.append("Face indices reference non-existent vertices")

        # Check for degenerate faces (zero area)
        if n_faces > 0:
            v0 = vertices[faces[:, 0]]
            v1 = vertices[faces[:, 1]]
            v2 = vertices[faces[:, 2]]
            crosses = np.cross(v1 - v0, v2 - v0)
            areas = np.linalg.norm(crosses, axis=1) / 2.0
            degenerate = np.sum(areas < 1e-10)
            if degenerate > 0:
                issues.append(f"{degenerate} degenerate (zero-area) faces")

        # Bounding box
        bb_min = np.min(vertices, axis=0)
        bb_max = np.max(vertices, axis=0)
        bb_size = bb_max - bb_min

        return {
            "valid": len(issues) == 0,
            "vertex_count": n_verts,
            "face_count": n_faces,
            "bounding_box": bb_size.tolist(),
            "bounding_box_min": bb_min.tolist(),
            "bounding_box_max": bb_max.tolist(),
            "issues": issues,
        }

    @staticmethod
    def decimate_mesh(
        vertices: np.ndarray,
        faces: np.ndarray,
        target_faces: Optional[int] = None,
        reduction: Optional[float] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Reduce mesh face count while preserving shape.

        Uses vertex clustering for simplicity and speed.
        For better quality decimation, use trimesh if available.

        Args:
            vertices: Nx3 vertex positions
            faces: Mx3 face vertex indices
            target_faces: Absolute target face count
            reduction: Reduction ratio 0-1 (e.g. 0.5 = keep 50%)

        Returns:
            (vertices, faces) — simplified mesh
        """
        try:
            import trimesh
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            if target_faces is not None:
                target = target_faces
            elif reduction is not None:
                target = int(len(faces) * reduction)
            else:
                target = len(faces) // 2

            target = max(target, 4)
            simplified = mesh.simplify_quadric_decimation(target)
            return np.array(simplified.vertices), np.array(simplified.faces)
        except ImportError:
            # Fallback: uniform subsampling (crude but works)
            if target_faces is not None:
                ratio = target_faces / len(faces)
            elif reduction is not None:
                ratio = reduction
            else:
                ratio = 0.5

            # Skip every N-th face
            step = max(1, int(1.0 / ratio))
            kept_faces = faces[::step]
            # Reindex vertices to remove unused
            used_verts = np.unique(kept_faces)
            vert_map = np.full(len(vertices), -1, dtype=np.int32)
            vert_map[used_verts] = np.arange(len(used_verts))
            new_vertices = vertices[used_verts]
            new_faces = vert_map[kept_faces]
            return new_vertices, new_faces

    @staticmethod
    def export_stl(
        vertices: np.ndarray,
        faces: np.ndarray,
        filepath: str,
        binary: bool = True,
    ) -> Dict[str, Any]:
        """Export mesh to STL file.

        Args:
            vertices: Nx3 vertex positions
            faces: Mx3 face vertex indices
            filepath: Output file path
            binary: If True, write binary STL (smaller); else ASCII

        Returns:
            Dict with export info (filepath, size_bytes, format)
        """
        try:
            import trimesh
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            mesh.export(filepath, file_type='stl')
        except ImportError:
            # Manual STL writer
            import struct
            import os

            # Compute face normals
            v0 = vertices[faces[:, 0]]
            v1 = vertices[faces[:, 1]]
            v2 = vertices[faces[:, 2]]
            normals = np.cross(v1 - v0, v2 - v0)
            norms = np.linalg.norm(normals, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            normals = normals / norms

            if binary:
                with open(filepath, 'wb') as f:
                    # Header (80 bytes)
                    header = b'Terrain Generator v0.1.0' + b'\0' * 56
                    f.write(header[:80])
                    # Number of triangles
                    f.write(struct.pack('<I', len(faces)))
                    # Triangles
                    for idx in range(len(faces)):
                        n = normals[idx]
                        f.write(struct.pack('<fff', n[0], n[1], n[2]))
                        for vi in faces[idx]:
                            v = vertices[vi]
                            f.write(struct.pack('<fff', v[0], v[1], v[2]))
                        f.write(struct.pack('<H', 0))  # attribute byte count
            else:
                with open(filepath, 'w') as f:
                    f.write('solid terrain\n')
                    for idx in range(len(faces)):
                        n = normals[idx]
                        f.write(f'  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n')
                        f.write('    outer loop\n')
                        for vi in faces[idx]:
                            v = vertices[vi]
                            f.write(f'      vertex {v[0]:.6e} {v[1]:.6e} {v[2]:.6e}\n')
                        f.write('    endloop\n')
                        f.write('  endfacet\n')
                    f.write('endsolid terrain\n')

        import os
        size = os.path.getsize(filepath)
        return {
            "filepath": filepath,
            "size_bytes": size,
            "format": "binary STL" if binary else "ASCII STL",
        }

    @staticmethod
    def export_obj(
        vertices: np.ndarray,
        faces: np.ndarray,
        filepath: str,
    ) -> Dict[str, Any]:
        """Export mesh to OBJ file.

        Args:
            vertices: Nx3 vertex positions
            faces: Mx3 face vertex indices (0-indexed)
            filepath: Output file path

        Returns:
            Dict with export info
        """
        with open(filepath, 'w') as f:
            f.write('# Terrain Generator v0.1.0\n')
            f.write(f'# Vertices: {len(vertices)}, Faces: {len(faces)}\n')
            for v in vertices:
                f.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
            for face in faces:
                # OBJ uses 1-indexed faces
                f.write(f'f {face[0]+1} {face[1]+1} {face[2]+1}\n')

        import os
        size = os.path.getsize(filepath)
        return {
            "filepath": filepath,
            "size_bytes": size,
            "format": "OBJ",
        }
