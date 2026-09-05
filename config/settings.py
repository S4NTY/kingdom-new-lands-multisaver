import inspect
import json
from pathlib import Path


class Settings:
    """Application settings persisted in a JSON file next to this module."""

    TIMESTAMP_FMT = "%Y_%m_%d_%H_%M_%S"
    GAME_SAVE_DIR = Path.home() / "AppData" / "LocalLow" / "noio" / "Kingdom"
    SAVES_DIR = GAME_SAVE_DIR / "saves dump"
    SAVE_FILE = "storage_v34_AUTO.dat"
    SETTINGS_FILE = "settings.json"

    def load(self) -> None:
        """Load persisted settings, preserving the types of default values."""
        settings_path = Path(self.SETTINGS_FILE)

        if not settings_path.is_file():
            return

        data = json.loads(settings_path.read_text(encoding="utf-8"))

        if not isinstance(data, dict):
            raise ValueError(f"Settings file must contain a JSON object: {settings_path}")

        for name, value in data.items():
            if not name.isupper() or not hasattr(self, name):
                continue

            current_value = getattr(self, name)
            if isinstance(current_value, Path):
                value = Path(value)
            setattr(self, name, value)

    def export(self) -> None:
        """Write the current public settings to the JSON settings file."""
        settings_path = Path(self.SETTINGS_FILE)
        data = {
            name: str(value) if isinstance(value, Path) else value
            for name, value in inspect.getmembers(self)
            if name.isupper() and not inspect.isroutine(value)
        }

        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=4) + "\n",
            encoding="utf-8",
        )


settings = Settings()
