import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from config.settings import settings
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

    def create_save(self, comment: str = "") -> SaveEntry | None:
        """Move save file to dump dir with new .json metadata file.

        Args:
            comment (str, optional): file comment. Defaults to "".

        Returns:
            SaveEntry | None: new save entry obj.
        """
        source = self.game_save_dir / settings.SAVE_FILE
        if not source.is_file():
            return None

        self.saves_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now()
        stem = timestamp.strftime(settings.TIMESTAMP_FMT)

        dat_path = self.saves_dir / f"{stem}.dat"
        json_path = self.saves_dir / f"{stem}.json"

        shutil.copy2(source, dat_path)
        json_path.write_text(
            json.dumps({"comment": comment}, ensure_ascii=False),
            encoding="utf-8"
        )

        return SaveEntry(
            path=dat_path,
            meta_path=json_path,
            timestamp=timestamp,
            comment=comment,
        )

    def restore_save(self, entry: SaveEntry) -> SaveEntry | None:
        """Move save file from dump dir to game save dir

         Args:
            entry: entry to restore save.

        Returns:
            SaveEntry | None: save entry obj.
        """
        if not entry.path.is_file():
            return None
        
        destination = self.game_save_dir / settings.SAVE_FILE
        
        if destination.exists():
            destination.unlink()
        
        shutil.copy2(entry.path, destination)
        return entry

    def update_save(self, entry: SaveEntry, comment: str) -> SaveEntry | None:
        """Update comment for an existing backup entry.

        Args:
            entry: backup entry to update.
            comment: new comment value.

        Returns:
            SaveEntry | None: updated entry or None if backup file is missing.
        """
        if not entry.path.is_file():
            return None

        entry.meta_path.parent.mkdir(parents=True, exist_ok=True)
        entry.meta_path.write_text(
            json.dumps({"comment": comment}, ensure_ascii=False),
            encoding="utf-8"
        )

        entry.comment = comment    
        return entry

    def delete_save(self, entry: SaveEntry):
        """Delete a save backup and its metadata file.

        Args:
            entry: backup entry to delete.

        Raises:
            FileNotFoundError: if the backup data file is missing.
        """
        if not entry.path.exists():
            raise FileNotFoundError(f"Save backup not found: {entry.path}")

        if entry.path.is_file():
            entry.path.unlink()

        if entry.meta_path.is_file():
            entry.meta_path.unlink()

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
