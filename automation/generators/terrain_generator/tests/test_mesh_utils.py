# Tests for mesh utilities

import numpy as np
import os
import tempfile
import pytest
from terrain_generator.geometry.mesh_utils import MeshUtils


class TestHeightmapToMesh:
    def test_basic_conversion(self):
        hm = np.array([[0, 1], [1, 2]], dtype=float)
        verts, faces = MeshUtils.heightmap_to_mesh(hm, resolution=1.0)
        assert verts.shape[1] == 3
        assert faces.shape[1] == 3
        assert len(verts) > 0
        assert len(faces) > 0

    def test_closed_mesh_has_sides_and_bottom(self):
        hm = np.ones((5, 5)) * 2.0
        verts_closed, faces_closed = MeshUtils.heightmap_to_mesh(
            hm, resolution=1.0, closed=True
        )
        verts_open, faces_open = MeshUtils.heightmap_to_mesh(
            hm, resolution=1.0, closed=False
        )
        # Closed should have more vertices (top + bottom) and faces (sides + bottom)
        assert len(verts_closed) > len(verts_open)
        assert len(faces_closed) > len(faces_open)

    def test_base_thickness(self):
        hm = np.ones((5, 5)) * 3.0
        verts, _ = MeshUtils.heightmap_to_mesh(hm, resolution=1.0, base_thickness=0.5)
        z_min = np.min(verts[:, 2])
        z_max = np.max(verts[:, 2])
        assert z_min == pytest.approx(3.0 - 0.5, abs=0.01)
        assert z_max == pytest.approx(3.0, abs=0.01)

    def test_resolution_affects_vertex_count(self):
        hm = np.ones((100, 100)) * 1.0
        v1, _ = MeshUtils.heightmap_to_mesh(hm, resolution=0.1, closed=False)
        hm2 = np.ones((50, 50)) * 1.0
        v2, _ = MeshUtils.heightmap_to_mesh(hm2, resolution=0.2, closed=False)
        assert len(v1) > len(v2)


class TestValidation:
    def test_valid_mesh(self):
        hm = np.random.default_rng(42).uniform(0, 3, (20, 20))
        verts, faces = MeshUtils.heightmap_to_mesh(hm, 0.5)
        result = MeshUtils.validate_mesh(verts, faces)
        assert result["valid"]
        assert result["vertex_count"] > 0
        assert result["face_count"] > 0
        assert len(result["bounding_box"]) == 3

    def test_nan_vertices_detected(self):
        verts = np.array([[0, 0, 0], [1, np.nan, 0], [1, 1, 0]], dtype=float)
        faces = np.array([[0, 1, 2]])
        result = MeshUtils.validate_mesh(verts, faces)
        assert not result["valid"]
        assert any("NaN" in i for i in result["issues"])

    def test_degenerate_face_detected(self):
        verts = np.array([[0, 0, 0], [0, 0, 0], [1, 1, 0]], dtype=float)
        faces = np.array([[0, 1, 2]])
        result = MeshUtils.validate_mesh(verts, faces)
        assert any("degenerate" in i for i in result["issues"])


class TestExport:
    def test_stl_export(self):
        hm = np.random.default_rng(42).uniform(0, 2, (10, 10))
        verts, faces = MeshUtils.heightmap_to_mesh(hm, 0.5)
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
            path = f.name
        try:
            result = MeshUtils.export_stl(verts, faces, path)
            assert os.path.exists(path)
            assert result["size_bytes"] > 0
        finally:
            os.unlink(path)

    def test_obj_export(self):
        hm = np.random.default_rng(42).uniform(0, 2, (10, 10))
        verts, faces = MeshUtils.heightmap_to_mesh(hm, 0.5)
        with tempfile.NamedTemporaryFile(suffix=".obj", delete=False) as f:
            path = f.name
        try:
            result = MeshUtils.export_obj(verts, faces, path)
            assert os.path.exists(path)
            assert result["size_bytes"] > 0
            # OBJ should contain vertex and face lines
            with open(path) as f:
                content = f.read()
            assert content.count("\nv ") > 0
            assert content.count("\nf ") > 0
        finally:
            os.unlink(path)

    def test_ascii_stl_export(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
        faces = np.array([[0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3]])
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
            path = f.name
        try:
            result = MeshUtils.export_stl(verts, faces, path, binary=False)
            with open(path) as f:
                content = f.read()
            assert "solid terrain" in content
            assert "facet normal" in content
        finally:
            os.unlink(path)
