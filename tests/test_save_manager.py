import json

import pytest
from pathlib import Path
from datetime import datetime

from core.models import SaveEntry
from core.save_manager import SaveManager

DEFAULT_GAME_DIR = "kingdom"
DEFAULT_SAVES_DIR = "saves dump"

def backup_name(timestamp: datetime) -> str:
    return timestamp.strftime("%Y_%m_%d_%H_%M_%S")

def game_save_dir_path(tmp_path: Path) -> Path:
    return tmp_path / DEFAULT_GAME_DIR

def saves_dir_path(tmp_path: Path) -> Path:
    return game_save_dir_path(tmp_path) / DEFAULT_SAVES_DIR

def write_backup(saves_dir: Path, timestamp: datetime, comment: str = "") -> SaveEntry:
    file_name = backup_name(timestamp)
    dat_path = saves_dir / f"{file_name}.dat"
    json_path = saves_dir / f"{file_name}.json"
    dat_path.write_bytes(b"0")
    json_path.write_text(json.dumps({"comment": comment}))
    return SaveEntry(path=dat_path, meta_path=json_path, timestamp=timestamp, comment=comment)

@pytest.fixture
def saves_dir(tmp_path: Path) -> Path:
    saves_dir = saves_dir_path(tmp_path)
    saves_dir.mkdir(parents=True, exist_ok=True)
    return saves_dir

@pytest.fixture
def manager(saves_dir: Path) -> SaveManager:
    game_dir = saves_dir.parent
    return SaveManager(game_save_dir=game_dir, saves_dir=saves_dir)


class TestListSaves:
    def test_returns_empty_list_when_saves_dir_does_not_exist(self, tmp_path: Path):
        manager = SaveManager(game_save_dir=game_save_dir_path(tmp_path),
                              saves_dir=saves_dir_path(tmp_path))

        assert manager.list_saves() == []

    def test_returns_empty_list_when_no_saves(self, manager: SaveManager):
        assert manager.list_saves() == []

    def test_returns_entries_for_existing_backup(self, manager: SaveManager, saves_dir: Path):
        ts = datetime(2026, 1, 2, 3,4,5)
        comment = "island 2 day 7"
        write_backup(saves_dir, ts, comment)

        entries = manager.list_saves()
        assert len(entries) == 1

        entry = entries[0]
        assert entry.path.name == "2026_1_2_3_4_5.dat"
        assert entry.meta_path.name == "2026_1_2_3_4_5.json"
        assert entry.timestamp == ts
        assert entry.comment == comment

    def test_returns_newest_first(self, manager: SaveManager, saves_dir: Path):
        write_backup(saves_dir, datetime(2026, 1, 1, 1,1,1), "old")
        write_backup(saves_dir, datetime(2026, 1, 1, 1,1,2), "new")

        entries = manager.list_saves()
        assert len(entries) == 2
        assert entries[0].timestamp > entries[1].timestamp
