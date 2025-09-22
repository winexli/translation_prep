# shared_state.py
from __future__ import annotations
from typing import Dict, TypedDict
from threading import RLock

class Row(TypedDict):
    number: str
    timestamp: str
    en: str
    zh: str

_lock = RLock()
_data: Dict[int, Row] = {}

def initialize() -> None:
    global _data
    with _lock:
        _data = {}

def get_data() -> Dict[int, Row]:
    return _data

def set_row(index: int, row: Row) -> None:
    with _lock:
        _data[index] = row

def next_index() -> int:
    with _lock:
        return (max(_data.keys(), default=0) + 1)
