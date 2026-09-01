from pathlib import Path

TIMESTAMP_FMT = "%Y_%m_%d_%H_%M_%S"
GAME_SAVE_DIR = Path.home() / "AppData" / "LocalLow" / "noio" / "Kingdom"
SAVES_DIR = GAME_SAVE_DIR / "saves dump"
SAVE_FILE = "storage_v34_AUTO.dat"