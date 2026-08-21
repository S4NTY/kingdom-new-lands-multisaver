from typing import List
from pathlib import Path
from .models import SaveEntry


class SaveManager:
    def __init__(self, game_save_dir: Path, saves_dir: Path):
        self.saves_dir = saves_dir
        self.game_save_dir = game_save_dir

    def list_saves(self) -> List[SaveEntry]:
        pass

    def create_save(self, comment: str="") -> SaveEntry:
        pass

    def restore_save(self, entry: SaveEntry) -> SaveEntry:
        pass

    def update_comment(self, entry: SaveEntry, comment: str) -> SaveEntry:
        pass

    def delete_save(self, entry: SaveEntry) -> SaveEntry:
        pass
