"""Tiny atomic JSON persistence so the live bot survives restarts with its risk state intact."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict


class StateStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def load(self) -> Dict[str, Any]:
        try:
            return json.loads(self.path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save(self, data: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), prefix=self.path.name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as fh:
                json.dump(data, fh, indent=2, default=str)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, self.path)  # atomic on POSIX and Windows
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
