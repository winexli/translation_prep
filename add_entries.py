# Update add_entries.py to include the "Wanna add more stuff?" loop per spec.
from pathlib import Path

project_dir = Path("/mnt/data/subtitle_project")
project_dir.mkdir(parents=True, exist_ok=True)

updated_add_entries_code = r'''# add_entries.py
from __future__ import annotations
import re
from typing import Optional, Tuple
import sys
import shared_state

TIMESTAMP_RE = re.compile(r'^\s*\[([0-9]{2}:[0-9]{2}:[0-9]{2}(?:[.,][0-9]{1,3})?)\]\s*(.*?)\s*$')

def run_add_flow() -> None:
    # Initial entry point (Step 1)
    print("Time to add stuff?")
    ans = input().strip().lower()
    if ans == "no":
        print("Okie. Bye!")
        return
    if ans != "yes":
        print("Say that again?")
        return

    # Main loop: after each successful add/update, ask if user wants to add more
    while True:
        # Ask options
        print("What is your input content?\nOption 1: Timestamp and English\nOption 2: Number and Chinese")
        opt = input().strip()
        if opt == "1":
            success = handle_option_1()
        elif opt == "2":
            success = handle_option_2()
        else:
            print("Say that again?")
            return

        # After completing the chosen option, we already printed a confirmation.
        # Now ask whether to continue.
        print("Wanna add more stuff?")
        again = input().strip().lower()
        if again == "no":
            print("Okie. Bye!")
            return
        if again != "yes":
            print("Say that again?")
            return
        # If "yes", the loop repeats and we ask options again.

def handle_option_1() -> bool:
    """
    Option 1 expects multiline input like:
        [00:09:42.35] one of the things...
    User can paste multiple lines, end with EOF (Ctrl-D on macOS/Linux, Ctrl-Z then Enter on Windows).
    """
    print("Paste your lines for Option 1 (Timestamp and English). Press Ctrl-D (macOS/Linux) or Ctrl-Z then Enter (Windows) to finish:")
    lines = _read_stdin_multiline()
    if not lines:
        print("Added Option 1 entries.")  # still print confirmation even if nothing added
        return True

    for raw in lines:
        if not raw.strip():
            continue
        ts, en = _parse_option1_line(raw)
        if ts is None:
            continue  # silently skip malformed lines
        idx = shared_state.next_index()
        # Store timestamp with brackets, per Part 1 shape: "[hh:mm:ss.xx]"
        row = {
            "number": str(idx),
            "timestamp": f"[{ts}]",
            "en": en,
            "zh": "",
        }
        shared_state.set_row(idx, row)
    print("Added Option 1 entries.")
    return True

def handle_option_2() -> bool:
    """
    Option 2 expects multiline input like:
        1 今天我想说的是
    """
    print("Paste your lines for Option 2 (Number and Chinese). Press Ctrl-D (macOS/Linux) or Ctrl-Z then Enter (Windows) to finish:")
    lines = _read_stdin_multiline()
    if not lines:
        print("Updated Chinese text for matching numbers.")
        return True

    data = shared_state.get_data()
    for raw in lines:
        if not raw.strip():
            continue
        num, zh = _parse_option2_line(raw)
        if num is None:
            continue
        try:
            idx = int(num)
        except ValueError:
            continue
        if idx in data:
            row = data[idx].copy()
            row["zh"] = zh
            shared_state.set_row(idx, row)
    print("Updated Chinese text for matching numbers.")
    return True

def _read_stdin_multiline():
    # Read until EOF for flexible pasting
    try:
        content = sys.stdin.read()
    except KeyboardInterrupt:
        return []
    if content is None:
        return []
    return content.splitlines()

def _parse_option1_line(s: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (timestamp_without_brackets, english) or (None, None) if malformed.
    Ensures trimming of both parts.
    """
    m = TIMESTAMP_RE.match(s)
    if not m:
        return None, None
    ts = m.group(1).replace(',', '.')  # normalize comma/period for fractional seconds
    en = m.group(2).strip()
    return ts.strip(), en

def _parse_option2_line(s: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Splits "number Chinese text" into (number, chinese).
    First token = number; rest joined as Chinese text. Trims both ends.
    """
    parts = s.strip().split(None, 1)
    if len(parts) < 2:
        return None, None
    number, zh = parts[0].strip(), parts[1].strip()
    return number, zh
'''

(add_entries_path := project_dir / "add_entries.py").write_text(updated_add_entries_code, encoding="utf-8")

str(add_entries_path)
