from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

@dataclass
class SaveEntry:
    path: Path              # Path to .dat
    meta_path: Path         # Path to meta .json
    timestamp: datetime
    comment: str = ""
