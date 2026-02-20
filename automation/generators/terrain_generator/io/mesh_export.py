# Mesh Export
# Handles exporting generated terrain meshes to various formats
# with metadata sidecar files.

import json
import os
import time
from typing import Dict, Any, Optional
import numpy as np

from ..geometry.mesh_utils import MeshUtils


class MeshExporter:
    """Export terrain meshes to STL/OBJ with metadata.

    Generates:
    - Mesh file (STL binary/ASCII or OBJ)
    - Metadata JSON sidecar file
    """

    @staticmethod
    def export(
        vertices: np.ndarray,
        faces: np.ndarray,
        filepath: str,
        spec: Dict[str, Any],
        format: str = "stl",
        binary: bool = True,
    ) -> Dict[str, Any]:
        """Export mesh to file with metadata sidecar.

        Args:
            vertices: Nx3 vertex positions
            faces: Mx3 face vertex indices
            filepath: Output file path (extension may be adjusted)
            spec: Full terrain specification (for metadata)
            format: "stl" or "obj"
            binary: If True and format is STL, write binary

        Returns:
            Dict with export results including file paths and stats
        """
        # Ensure directory exists
        out_dir = os.path.dirname(filepath)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # Adjust extension
        base, _ = os.path.splitext(filepath)
        if format == "obj":
            mesh_path = base + ".obj"
            export_info = MeshUtils.export_obj(vertices, faces, mesh_path)
        else:
            mesh_path = base + ".stl"
            export_info = MeshUtils.export_stl(vertices, faces, mesh_path, binary=binary)

        # Validate the exported mesh
        validation = MeshUtils.validate_mesh(vertices, faces)

        # Compute bounding box
        bb_min = np.min(vertices, axis=0)
        bb_max = np.max(vertices, axis=0)
        bb_size = bb_max - bb_min

        # Write metadata sidecar
        metadata = {
            "generator_version": "0.1.0",
            "generation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "terrain_spec": _sanitize_spec(spec),
            "mesh_stats": {
                "vertex_count": len(vertices),
                "face_count": len(faces),
                "bounding_box_inches": bb_size.tolist(),
                "bounding_box_min": bb_min.tolist(),
                "bounding_box_max": bb_max.tolist(),
            },
            "validation": validation,
            "export": {
                "format": export_info["format"],
                "filepath": export_info["filepath"],
                "size_bytes": export_info["size_bytes"],
            },
            "cad_integration": {
                "freecad_import_notes": (
                    "Import via Mesh workbench: mesh_operations import_mesh. "
                    "Then convert to solid: mesh_operations mesh_to_solid. "
                    "Units are inches."
                ),
                "cnc_notes": (
                    f"Bounding box: {bb_size[0]:.2f} x {bb_size[1]:.2f} x {bb_size[2]:.2f} inches. "
                    f"Tool access verified for {spec.get('cnc_constraints', {}).get('max_tool_diameter', 0.25)}\" endmill."
                ),
            },
        }

        meta_path = base + "_metadata.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return {
            "mesh_file": export_info["filepath"],
            "metadata_file": meta_path,
            "mesh_size_bytes": export_info["size_bytes"],
            "vertex_count": len(vertices),
            "face_count": len(faces),
            "bounding_box_inches": bb_size.tolist(),
            "valid": validation["valid"],
            "issues": validation["issues"],
        }


def _sanitize_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Remove non-serializable items from spec for JSON output."""
    result = {}
    for key, val in spec.items():
        if isinstance(val, dict):
            result[key] = _sanitize_spec(val)
        elif isinstance(val, (list, tuple)):
            result[key] = [_sanitize_item(v) for v in val]
        else:
            result[key] = _sanitize_item(val)
    return result


def _sanitize_item(val):
    if isinstance(val, np.ndarray):
        return val.tolist()
    if isinstance(val, (np.float32, np.float64)):
        return float(val)
    if isinstance(val, (np.int32, np.int64)):
        return int(val)
    return val
