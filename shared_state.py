from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock
from typing import Dict, Optional, TypedDict


class Row(TypedDict):
    number: str  # logical index as string (e.g., "1")
    timestamp: str  # stored in brackets, e.g., "[00:00:01.000]"
    en: str  # English text
    zh: str  # Chinese text


_lock = RLock()
_data: Dict[int, Row] = {}
_plate: Optional[str] = None

_DATA_DIR = Path(os.environ.get("SUBTITLE_DATA_DIR", "data"))


def _path_for(plate: str) -> Path:
    safe = plate.strip().replace("/", "_").replace("\\", "_")
    return _DATA_DIR / f"{safe}.json"


def initialize(plate: str) -> bool:
    """
    Initialize the in-memory store for the given plate number.
    Creates the data directory if needed.
    Returns True if an existing dictionary was loaded, False if a new one was created.
    """
    global _data, _plate
    with _lock:
        _plate = plate.strip()
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        p = _path_for(_plate)
        if p.exists():
            try:
                payload = json.loads(p.read_text(encoding="utf-8"))
                # Convert keys back to ints
                loaded = {int(k): v for k, v in payload.get("data", {}).items()}
                _data = loaded
                return True
            except Exception:
                # If loading fails, start fresh but don't crash.
                _data = {}
                return False
        else:
            _data = {}
            return False


def get_plate() -> Optional[str]:
    return _plate


def get_data() -> Dict[int, Row]:
    """
    Return the underlying store (by reference).
    Callers should use set_row for writes to keep locking consistent.
    """
    return _data


def set_row(index: int, row: Row) -> None:
    """
    Atomically set/replace a row at the given index.
    """
    with _lock:
        _data[index] = row


def next_index() -> int:
    """
    Return the next available integer index (1-based).
    """
    with _lock:
        if not _data:
            return 1
        return max(_data.keys()) + 1


def save() -> None:
    """
    Persist the current dictionary to disk under the active plate.
    No-op if plate is not initialized.
    """
    with _lock:
        if not _plate:
            return
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        p = _path_for(_plate)
        # Serialize with string keys to be JSON-friendly; keep order stable.
        serializable = {str(k): _data[k] for k in sorted(_data.keys())}
        payload = {"plate": _plate, "data": serializable}
        p.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
