import json
from pathlib import Path
from typing import Any


class KingdomSave:
    """Universal access to Kingdom: New Lands save parameters."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"Save file not found: {self.path}")

        if not self.path.is_file():
            raise ValueError(f"Path is not a file: {self.path}")

        self._raw: dict[str, Any] = {}
        self._objects: dict[str, dict] = {}

        self._load()

    def _load(self) -> None:
        with open(self.path, "r", encoding="utf-8") as f:
            self._raw = json.load(f)

        for obj in self._raw.get("objects", []):
            name = obj.get("name")
            if not name:
                continue

            for comp in obj.get("componentData2", []):
                raw_data = comp.get("data")
                if not raw_data:
                    continue
                try:
                    parsed = json.loads(raw_data)
                    self._objects[name] = parsed
                    break
                except (json.JSONDecodeError, TypeError):
                    continue

    def get(self, object_name: str, key: str, default=None) -> Any:
        """Universal access: save.get('Director', 'currentDay')"""
        return self._objects.get(object_name, {}).get(key, default)

    def raw_object(self, object_name: str) -> dict:
        """Return the entire parsed object by name."""
        return self._objects.get(object_name, {})

    def get_base_data(self) -> str:
        """Return the entire parsed base data."""
        lines = [
            f"Land: {self.get('Game', 'land') + 1}",
            f"Current Day: {self.get('Director', 'currentDay') + 1}",
        ]
        return "\n".join(lines)
