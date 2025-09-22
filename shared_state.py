from __future__ import annotations

from threading import RLock
from typing import Dict, TypedDict


class Row(TypedDict):
    number: str  # logical index as string (e.g., "1")
    timestamp: str  # stored in brackets, e.g., "[00:00:01.000]"
    en: str  # English text
    zh: str  # Chinese text


_lock = RLock()
_data: Dict[int, Row] = {}


def initialize() -> None:
    """
    Initialize (or reset) the in-memory store.
    """
    global _data
    with _lock:
        _data = {}


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
