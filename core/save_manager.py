import json
from datetime import datetime
from pathlib import Path
from typing import List

from config import settings
from .models import SaveEntry


class SaveManager:
    def __init__(self, game_save_dir: Path, saves_dir: Path):
        self.saves_dir = saves_dir
        self.game_save_dir = game_save_dir

    def list_saves(self) -> List[SaveEntry]:
        """Get all entries sorted by timestamp (newest first).

        Returns:
            List[SaveEntry]: A list of SaveEntry objects representing the saves.
        """
        if not self.saves_dir.is_dir():
            return []

        entries = []
        for dat_path in self.saves_dir.glob("*.dat"):
            entry = self._parse_entry(dat_path)
            if entry is not None:
                entries.append(entry)

        return sorted(entries, reverse=True)

    def create_save(self, comment: str="") -> SaveEntry:
        pass

    def restore_save(self, entry: SaveEntry) -> SaveEntry:
        pass

    def update_comment(self, entry: SaveEntry, comment: str) -> SaveEntry:
        pass

    def delete_save(self, entry: SaveEntry) -> SaveEntry:
        pass

    @staticmethod
    def _parse_entry(dat_path: Path) -> SaveEntry | None:
        """Parse a .dat file and its corresponding .json metadata file into a SaveEntry.
        
        Args:
            dat_path (Path): The path to the .dat file.

        Returns:
            SaveEntry | None: The parsed SaveEntry or None if parsing fails.
        """
        meta_path = dat_path.with_suffix(".json")

        try:
            timestamp = datetime.strptime(dat_path.stem, settings.TIMESTAMP_FMT)
            if meta_path.is_file():
                metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            else:
                metadata = {}
        except (ValueError, OSError, json.JSONDecodeError):
            return None

        return SaveEntry(
            path=dat_path,
            meta_path=meta_path,
            timestamp=timestamp,
            comment=metadata.get("comment", ""),
        )
