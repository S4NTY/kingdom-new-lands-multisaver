import json
from unittest.mock import patch

import pytest
from pathlib import Path
from datetime import datetime

from core.models import SaveEntry
from core.save_manager import SaveManager
from config.settings import settings

DEFAULT_GAME_DIR = "kingdom"
DEFAULT_SAVES_DIR = "saves dump"

def backup_name(timestamp: datetime) -> str:
    return timestamp.strftime(settings.TIMESTAMP_FMT)

def game_save_dir_path(tmp_path: Path) -> Path:
    return tmp_path / DEFAULT_GAME_DIR

def saves_dir_path(tmp_path: Path) -> Path:
    return game_save_dir_path(tmp_path) / DEFAULT_SAVES_DIR

def write_save(game_save_dir: Path) -> None:
    dat_path = game_save_dir / settings.SAVE_FILE
    dat_path.write_bytes(b"0")

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
def game_save_dir(tmp_path: Path) -> Path:
    game_save_dir = game_save_dir_path(tmp_path)
    game_save_dir.mkdir(parents=True, exist_ok=True)
    return game_save_dir

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
        assert entry.path.name == "2026_01_02_03_04_05.dat"
        assert entry.meta_path.name == "2026_01_02_03_04_05.json"
        assert entry.timestamp == ts
        assert entry.comment == comment

    def test_returns_newest_first(self, manager: SaveManager, saves_dir: Path):
        write_backup(saves_dir, datetime(2026, 1, 1, 1,1,2), "old")
        write_backup(saves_dir, datetime(2026, 1, 1, 1,1,1), "new")

        entries = manager.list_saves()
        assert len(entries) == 2
        assert entries[0].timestamp > entries[1].timestamp


class TestCreateSave:
    def test_returns_none_if_game_save_dir_does_not_exist(self, tmp_path: Path):
        manager = SaveManager(game_save_dir=game_save_dir_path(tmp_path),
                              saves_dir=saves_dir_path(tmp_path))

        assert manager.create_save() is None

    def test_returns_none_if_save_does_not_exist(self, manager: SaveManager):
        assert manager.create_save() is None

    def test_returns_entry_for_existing_save(self, manager: SaveManager):
        write_save(manager.game_save_dir)
        source_dat = manager.game_save_dir / settings.SAVE_FILE
        fixed_now = datetime(2026, 2, 3, 4, 5, 6)

        with patch("core.save_manager.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            entry = manager.create_save(comment="island 3")

        assert entry is not None
        assert entry.timestamp == fixed_now
        assert entry.comment == "island 3"

        dat_path = manager.saves_dir / "2026_02_03_04_05_06.dat"
        json_path = manager.saves_dir / "2026_02_03_04_05_06.json"
        assert dat_path.is_file()
        assert json_path.is_file()
        assert dat_path.read_bytes() == b"0"
        assert json.loads(json_path.read_text(encoding="utf-8")) == {"comment": "island 3"}
        assert source_dat.exists()


class TestRestoreSave:
    def test_restore_none_if_entry_invalid(self, manager: SaveManager):
        result = manager.restore_save(SaveEntry(
            path=Path("nonexistent"),
            meta_path=Path("nonexistent.json"),
            timestamp=datetime.now(),
            comment=""
        ))

        assert result is None

    def test_returns_entry_for_existing_save(self, manager: SaveManager, saves_dir: Path):
        timestamp = datetime(2026, 2, 3, 4, 5, 6)
        comment = "island 3"
        meta_file_name = f"{backup_name(timestamp)}.json"
        entry = write_backup(saves_dir, timestamp, comment)
        result = manager.restore_save(entry)

        assert result is not None
        assert result == entry
        assert (manager.game_save_dir / settings.SAVE_FILE).exists()
        assert (manager.game_save_dir / meta_file_name).exists() == False


class TestUpdateSave:
    def test_returns_none_if_entry_invalid(self, manager: SaveManager):
        assert manager.update_save(SaveEntry(
            path=Path("nonexistent"),
            meta_path=Path("nonexistent.json"),
            timestamp=datetime.now(),
            comment=""), "new comment") is None
 
    def test_returns_new_entry_after_update(self, manager: SaveManager, saves_dir: Path):
        timestamp = datetime(2026, 2, 3, 4, 5, 6)
        comment = "island 1"
        new_comment = "island 2"

        entry = write_backup(saves_dir, timestamp, comment)
        new_entry = manager.update_save(entry, new_comment)

        assert new_entry is not None
        assert new_entry.comment == new_comment
        assert new_entry.meta_path.exists()
        assert json.loads(new_entry.meta_path.read_text(encoding="utf-8")) == {"comment": new_comment}


class TestDeleteSave:
    def test_returns_none_if_entry_invalid(self, manager: SaveManager):
        with pytest.raises(FileNotFoundError):
            manager.delete_save(SaveEntry(
                path=Path("nonexistent"),
                meta_path=Path("nonexistent.json"),
                timestamp=datetime.now(),
                comment=""))

    def test_removes_dat_and_json(self, manager: SaveManager, saves_dir: Path):
        entry = write_backup(saves_dir, datetime(2026, 2, 3, 4, 5, 6), "island 3")

        manager.delete_save(entry)

        assert not entry.path.exists()
        assert not entry.meta_path.exists()

    def test_entry_disappears_from_list_saves(self, manager: SaveManager, saves_dir: Path):
        entry = write_backup(saves_dir, datetime(2026, 2, 3, 4, 5, 6), "island 3")

        assert manager.list_saves() != []
        manager.delete_save(entry)
        assert manager.list_saves() == []

    def test_deleting_again_raises_file_not_found(self, manager: SaveManager, saves_dir: Path):
        entry = write_backup(saves_dir, datetime(2026, 2, 3, 4, 5, 6), "island 3")
        manager.delete_save(entry)

        with pytest.raises(FileNotFoundError):
            manager.delete_save(entry)
