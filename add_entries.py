from __future__ import annotations
import re
from typing import Optional, Tuple
import sys
import shared_state

TIMESTAMP_RE = re.compile(
    r"^\s*\[([0-9]{2}:[0-9]{2}:[0-9]{2}(?:[.,][0-9]{1,3})?)\]\s*(.*?)\s*$"
)


def run_add_flow() -> None:
    """
    Top-level interaction loop for Part 2.
    All user interaction is initiated by main.py calling this function.
    """
    print("Time to add stuff?")
    ans = input().strip().lower()
    if ans == "no":
        print("Okie. Bye!")
        return
    if ans != "yes":
        print("Say that again?")
        return

    # Enter the repeatable add-more loop
    while True:
        # Ask options
        print(
            "What is your input content?\nOption 1: Timestamp and English\nOption 2: Number and Chinese"
        )
        opt = input().strip()
        if opt == "1":
            handle_option_1()
        elif opt == "2":
            handle_option_2()
        else:
            print("Say that again?")
            return

        # After confirming success, ask if they want to add more
        print("Wanna add more stuff?")
        more = input().strip().lower()
        if more == "yes":
            continue
        elif more == "no":
            print("Okie. Bye!")
            return
        else:
            print("Say that again?")
            return


def handle_option_1() -> None:
    """
    Option 1 expects multiline input like:
        [00:09:42.35] one of the things...
    Paste multiple lines, end with EOF (Ctrl-D macOS/Linux, Ctrl-Z then Enter Windows).
    """
    print(
        "Paste your lines for Option 1 (Timestamp and English). Press Ctrl-D (macOS/Linux) or Ctrl-Z then Enter (Windows) to finish:"
    )
    lines = _read_stdin_multiline()
    if not lines:
        return

    for raw in lines:
        if not raw.strip():
            continue
        ts, en = _parse_option1_line(raw)
        if ts is None:
            continue
        idx = shared_state.next_index()
        row = {
            "number": str(idx),
            "timestamp": f"[{ts}]",
            "en": en,
            "zh": "",
        }
        shared_state.set_row(idx, row)
    print("Added Option 1 entries.")


def handle_option_2() -> None:
    """
    Option 2 expects multiline input like:
        1 今天我想说的是
    """
    print(
        "Paste your lines for Option 2 (Number and Chinese). Press Ctrl-D (macOS/Linux) or Ctrl-Z then Enter (Windows) to finish:"
    )
    lines = _read_stdin_multiline()
    if not lines:
        return

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


def _read_stdin_multiline():
    try:
        content = sys.stdin.read()
    except KeyboardInterrupt:
        return []
    if content is None:
        return []
    return content.splitlines()


def _parse_option1_line(s: str) -> Tuple[Optional[str], Optional[str]]:
    m = TIMESTAMP_RE.match(s)
    if not m:
        return None, None
    ts = m.group(1).replace(",", ".")
    en = m.group(2).strip()
    return ts.strip(), en


def _parse_option2_line(s: str) -> Tuple[Optional[str], Optional[str]]:
    parts = s.strip().split(None, 1)
    if len(parts) < 2:
        return None, None
    number, zh = parts[0].strip(), parts[1].strip()
    return number, zh
