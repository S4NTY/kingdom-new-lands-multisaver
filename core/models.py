from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

@dataclass(order=True)
class SaveEntry:
    timestamp: datetime
    path: Path              # Path to .dat
    meta_path: Path         # Path to meta .json
    comment: str = ""
