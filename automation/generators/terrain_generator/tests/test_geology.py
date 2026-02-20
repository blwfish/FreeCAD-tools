# Tests for geology knowledge base

import pytest
from terrain_generator.constraints.geology_knowledge import (
    GeologyKnowledge, ROCK_TYPES, HO_SCALE
)


class TestRockTypes:
    def test_all_known_types_exist(self):
        for name in ["sandstone", "shale", "limestone", "granite", "schist"]:
            rt = GeologyKnowledge.get_rock_type(name)
            assert rt.name == name

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match="Unknown rock type"):
            GeologyKnowledge.get_rock_type("unobtainium")

    def test_ho_spacing_conversion(self):
        rt = GeologyKnowledge.get_rock_type("sandstone")
        lo, hi = rt.jointing_spacing_ho_inches
        # Sandstone: 6-18 proto feet → should be 0.8-2.5" HO
        assert 0.5 < lo < 1.5
        assert 1.5 < hi < 3.5

    def test_default_jointing_angle(self):
        rt = GeologyKnowledge.get_rock_type("sandstone")
        assert rt.jointing_angle_range[0] <= rt.default_jointing_angle <= rt.jointing_angle_range[1]

    def test_list_rock_types(self):
        types = GeologyKnowledge.list_rock_types()
        assert len(types) >= 5
        assert "sandstone" in types


class TestJointingValidation:
    def test_valid_angle_returns_none(self):
        result = GeologyKnowledge.validate_jointing_angle("sandstone", 60.0)
        assert result is None

    def test_extreme_angle_warns(self):
        result = GeologyKnowledge.validate_jointing_angle("sandstone", 5.0)
        assert result is not None
        assert "outside plausible range" in result

    def test_borderline_angle_ok(self):
        # Sandstone range is 45-75, so 40 is within tolerance (range - 10)
        result = GeologyKnowledge.validate_jointing_angle("sandstone", 40.0)
        assert result is None


class TestScaleConversion:
    def test_proto_to_ho(self):
        # 87.1" prototype = 1" HO
        result = GeologyKnowledge.proto_to_ho(87.1 / 12.0)  # 87.1 inches = 7.258 feet
        assert abs(result - 1.0) < 0.01

    def test_ho_to_proto(self):
        result = GeologyKnowledge.ho_to_proto(1.0)  # 1 HO inch
        assert abs(result - 87.1 / 12.0) < 0.01

    def test_roundtrip(self):
        original = 10.0  # 10 proto feet
        ho = GeologyKnowledge.proto_to_ho(original)
        back = GeologyKnowledge.ho_to_proto(ho)
        assert abs(back - original) < 0.001


class TestMaterials:
    def test_known_materials(self):
        for name in ["xps_foam", "mdf", "plywood"]:
            mat = GeologyKnowledge.get_material(name)
            assert "name" in mat
            assert mat["max_depth_per_pass_inches"] > 0

    def test_unknown_material_raises(self):
        with pytest.raises(ValueError, match="Unknown material"):
            GeologyKnowledge.get_material("titanium")
