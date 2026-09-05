import json
from pathlib import Path

import pytest

from core.kingdom_save import KingdomSave


def write_save(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


class TestKingdomSave:
    def test_raises_when_save_file_does_not_exist(self, tmp_path: Path):
        path = tmp_path / "missing.dat"

        with pytest.raises(FileNotFoundError, match="Save file not found"):
            KingdomSave(path)

    def test_raises_when_path_is_not_a_file(self, tmp_path: Path):
        path = tmp_path / "save.dat"
        path.mkdir()

        with pytest.raises(ValueError, match="Path is not a file"):
            KingdomSave(path)

    def test_loads_object_data_from_first_valid_component(self, tmp_path: Path):
        path = tmp_path / "save.dat"
        write_save(
            path,
            {
                "objects": [
                    {
                        "name": "Director",
                        "componentData2": [
                            {"data": ""},
                            {"data": "{invalid json"},
                            {"data": json.dumps({"currentDay": 12})},
                            {"data": json.dumps({"currentDay": 99})},
                        ],
                    }
                ]
            },
        )

        save = KingdomSave(path)

        assert save.get("Director", "currentDay") == 12
        assert save.raw_object("Director") == {"currentDay": 12}

    def test_skips_objects_without_names_and_invalid_components(self, tmp_path: Path):
        path = tmp_path / "save.dat"
        write_save(
            path,
            {
                "objects": [
                    {"componentData2": [{"data": json.dumps({"value": 1})}]},
                    {
                        "name": "Invalid",
                        "componentData2": [{"data": 123}, {"data": "{bad"}],
                    },
                ]
            },
        )

        save = KingdomSave(path)

        assert save.raw_object("Invalid") == {}
        assert save.raw_object("Unnamed") == {}

    def test_returns_default_for_missing_object_or_key(self, tmp_path: Path):
        path = tmp_path / "save.dat"
        write_save(
            path,
            {
                "objects": [
                    {
                        "name": "Game",
                        "componentData2": [{"data": json.dumps({"land": 2})}],
                    }
                ]
            },
        )

        save = KingdomSave(path)

        assert save.get("Game", "missing", "fallback") == "fallback"
        assert save.get("Missing", "value", 42) == 42

    def test_get_base_data_formats_land_and_day(self, tmp_path: Path):
        path = tmp_path / "save.dat"
        write_save(
            path,
            {
                "objects": [
                    {
                        "name": "Game",
                        "componentData2": [{"data": json.dumps({"land": 2})}],
                    },
                    {
                        "name": "Director",
                        "componentData2": [{"data": json.dumps({"currentDay": 18})}],
                    },
                ]
            },
        )

        save = KingdomSave(path)

        assert save.get_base_data() == "Land: 3\nCurrent Day: 17"

    def test_propagates_invalid_save_json(self, tmp_path: Path):
        path = tmp_path / "save.dat"
        path.write_text("{invalid json", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            KingdomSave(path)
