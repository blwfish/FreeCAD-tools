# Integration tests — full pipeline from params to mesh

import numpy as np
import os
import tempfile
import pytest
from terrain_generator import TerrainGenerator


@pytest.fixture
def gen():
    return TerrainGenerator(seed=42)


class TestFullPipeline:
    def test_hillside_generates(self, gen):
        result = gen.generate({
            "feature_type": "hillside",
            "dimensions": {"width_inches": 6, "length_inches": 6, "height_inches": 4},
            "geology": {"rock_type": "sandstone"},
            "seed": 42,
        })
        assert "error" not in result
        assert result["vertices"].shape[1] == 3
        assert result["faces"].shape[1] == 3
        assert result["mesh_stats"]["valid"]

    def test_riverbank_generates(self, gen):
        result = gen.generate({
            "feature_type": "riverbank",
            "dimensions": {"width_inches": 8, "length_inches": 8, "height_inches": 4},
            "geology": {"rock_type": "shale"},
        })
        assert "error" not in result
        assert result["mesh_stats"]["valid"]

    def test_cliff_generates(self, gen):
        result = gen.generate({
            "feature_type": "cliff",
            "dimensions": {"width_inches": 6, "length_inches": 6, "height_inches": 6},
            "geology": {"rock_type": "limestone"},
        })
        assert "error" not in result
        assert result["mesh_stats"]["valid"]

    def test_valley_generates(self, gen):
        result = gen.generate({
            "feature_type": "valley",
            "dimensions": {"width_inches": 8, "length_inches": 8, "height_inches": 3},
            "geology": {"rock_type": "granite"},
        })
        assert "error" not in result
        assert result["mesh_stats"]["valid"]

    def test_seed_reproducibility(self):
        """Same seed should produce identical meshes."""
        params = {
            "feature_type": "hillside",
            "dimensions": {"width_inches": 6, "length_inches": 6, "height_inches": 4},
            "seed": 999,
        }
        g1 = TerrainGenerator(seed=999)
        g2 = TerrainGenerator(seed=999)
        r1 = g1.generate(params)
        r2 = g2.generate(params)
        np.testing.assert_array_equal(r1["heightmap"], r2["heightmap"])
        np.testing.assert_array_equal(r1["vertices"], r2["vertices"])

    def test_different_seeds_differ(self):
        params = {
            "feature_type": "hillside",
            "dimensions": {"width_inches": 6, "length_inches": 6, "height_inches": 4},
        }
        r1 = TerrainGenerator(seed=1).generate(params)
        r2 = TerrainGenerator(seed=2).generate(params)
        assert not np.array_equal(r1["heightmap"], r2["heightmap"])


class TestExport:
    def test_stl_export(self, gen):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.stl")
            result = gen.generate(
                {"feature_type": "hillside",
                 "dimensions": {"width_inches": 4, "length_inches": 4, "height_inches": 2},
                 "resolution": 0.2},
                export_path=path,
            )
            assert "error" not in result
            assert result["export"] is not None
            assert os.path.exists(result["export"]["mesh_file"])
            assert result["export"]["mesh_size_bytes"] > 0
            # Metadata sidecar should exist
            assert os.path.exists(result["export"]["metadata_file"])

    def test_obj_export(self, gen):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.obj")
            result = gen.generate(
                {"feature_type": "cliff",
                 "dimensions": {"width_inches": 4, "length_inches": 4, "height_inches": 3},
                 "resolution": 0.2},
                export_path=path,
                export_format="obj",
            )
            assert "error" not in result
            assert result["export"]["mesh_file"].endswith(".obj")
            assert os.path.exists(result["export"]["mesh_file"])


class TestValidation:
    def test_invalid_dimensions_rejected(self, gen):
        result = gen.generate({
            "feature_type": "hillside",
            "dimensions": {"width_inches": -5, "length_inches": 6, "height_inches": 4},
        })
        assert "error" in result

    def test_oversized_warns(self, gen):
        result = gen.generate({
            "feature_type": "hillside",
            "dimensions": {"width_inches": 6, "length_inches": 6, "height_inches": 5},
            "resolution": 0.2,
        })
        # Height 5" > CNC Z travel 3" should produce a warning
        warnings = result.get("validation", {}).get("warnings", [])
        z_warnings = [w for w in warnings if "Z travel" in w]
        assert len(z_warnings) > 0

    def test_unknown_rock_type_rejected(self, gen):
        result = gen.generate({
            "feature_type": "hillside",
            "dimensions": {"width_inches": 6, "length_inches": 6, "height_inches": 4},
            "geology": {"rock_type": "unobtainium"},
        })
        assert "error" in result


class TestPreview:
    def test_preview_coarser(self, gen):
        params = {
            "feature_type": "hillside",
            "dimensions": {"width_inches": 6, "length_inches": 6, "height_inches": 4},
            "resolution": 0.1,
        }
        full = gen.generate(params)
        preview = gen.generate_preview(params)
        assert preview["resolution"] > full["resolution"]
        assert preview["mesh_stats"]["vertex_count"] < full["mesh_stats"]["vertex_count"]
