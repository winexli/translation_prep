from __future__ import annotations

import re
from typing import List, Optional, Tuple

import shared_state


# Matches: [HH:MM:SS] or [HH:MM:SS.mmm] with '.' or ',' for millis
TIMESTAMP_RE = re.compile(
    r"^\s*\[(?P<ts>\d{2}:\d{2}:\d{2}(?:[.,]\d{1,3})?)\]\s*(?P<text>.+?)\s*$"
)

# -------------------------
# Input helpers & parsers
# -------------------------


def _read_stdin_multiline(header: str) -> List[str]:
    """
    Read multi-line user input until EOF (Ctrl-D on Unix/macOS, Ctrl-Z+Enter on Windows).
    Empty lines are allowed and preserved for parsing decisions; we skip them later.
    """
    print(header)
    print("(Finish input with Ctrl-D on macOS/Linux or Ctrl-Z then Enter on Windows.)")
    lines: List[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            print()  # newline after EOF to keep output tidy
            break
        lines.append(line)
    return lines


def _parse_option1_line(s: str) -> Optional[Tuple[str, str]]:
    """
    Parse a line like:
        [00:09:42.35] one of the things...
    Return (normalized_timestamp, english_text) or None if not matched.
    """
    m = TIMESTAMP_RE.match(s)
    if not m:
        return None
    ts = m.group("ts").replace(",", ".")
    # Normalize to 3-digit milliseconds if present (pad or trim)
    if "." in ts:
        hhmmss, ms = ts.split(".")
        ms = (ms + "000")[:3]
        ts = f"{hhmmss}.{ms}"
    else:
        ts = f"{ts}.000"
    text = m.group("text").strip()
    return ts, text


def _parse_option2_line(s: str) -> Optional[Tuple[int, str]]:
    """
    Parse a line like:
        1 今天我想说的是
    Return (row_number, zh_text) or None if not matched.
    """
    s = s.strip()
    if not s:
        return None
    # Split at first whitespace
    m = re.match(r"^\s*(\d+)\s+(.+?)\s*$", s)
    if not m:
        return None
    number = int(m.group(1))
    zh = m.group(2).strip()
    return number, zh


# -------------------------
# Menu prompt with retry loop
# -------------------------


def _prompt_menu_choice(max_invalid: int = 5) -> Optional[str]:
    """
    Prints the menu once, then loops asking 'Say that again?' until the user
    enters '1' or '2'. If the user enters neither more than `max_invalid` times,
    prints 'Alright. Bye!' and returns None.
    """
    print("What is your input content?")
    print("Option 1: Timestamp and English")
    print("Option 2: Number and Chinese")

    invalid_count = 0
    while True:
        choice = input().strip()
        if choice in ("1", "2"):
            return choice

        invalid_count += 1
        if invalid_count > max_invalid:
            print("Alright. Bye!")
            return None

        print("Say that again?")


# -------------------------
# Option handlers
# -------------------------


def handle_option_1() -> None:
    """
    Ingest lines of the form:
        [00:09:42.35] one of the things...
    Creates new rows with timestamp + English, leaves zh empty.
    """
    lines = _read_stdin_multiline(
        "Paste lines for Option 1 ([HH:MM:SS(.mmm)] English):"
    )
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        parsed = _parse_option1_line(line)
        if not parsed:
            print(f"Skipping (unrecognized): {raw}")
            continue

        ts, en = parsed
        idx = shared_state.next_index()
        row = shared_state.Row(
            number=str(idx),
            timestamp=f"[{ts}]",
            en=en,
            zh="",
        )
        shared_state.set_row(idx, row)
        print(f"Added #{idx}: {row['timestamp']} {row['en']}")


def handle_option_2() -> None:
    """
    Ingest lines of the form:
        1 今天我想说的是
    Updates the zh field of an existing row by number.
    """
    lines = _read_stdin_multiline("Paste lines for Option 2 (<number> <Chinese>):")
    data = shared_state.get_data()
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        parsed = _parse_option2_line(line)
        if not parsed:
            print(f"Skipping (unrecognized): {raw}")
            continue

        number, zh = parsed
        row = data.get(number)
        if not row:
            print(f"Row #{number} not found; skipping.")
            continue

        updated = shared_state.Row(
            number=row["number"],
            timestamp=row["timestamp"],
            en=row["en"],
            zh=zh,
        )
        shared_state.set_row(number, updated)
        print(f"Updated #{number} zh: {zh}")


# -------------------------
# Top-level flow
# -------------------------


def run_add_flow() -> None:
    """
    Top-level interaction loop.
    """
    # New initial step: ask if it's time to add stuff
    print("Time to add stuff?")
    print("yes or no")
    first = input().strip().lower()

    if first == "no":
        print("Okie. Bye!")
        data = shared_state.get_data()
        if not data:
            print("Btw, your current dictionary is still empty.")
        else:
            last_index = max(data.keys())
            last_row = data[last_index]
            print("Btw, here are the last row of your current dictionary.")
            print(last_row)
        return
    elif first == "yes":
        # Proceed into the normal menu flow
        pass
    else:
        print("Say that again?")
        print("Alright. Bye!")
        return

    while True:
        choice = _prompt_menu_choice()
        if choice is None:
            return  # already printed "Alright. Bye!"

        if choice == "1":
            handle_option_1()
        else:
            handle_option_2()

        print("Wanna add more stuff? (yes/no)")
        again = input().strip().lower()
        if again not in ("y", "yes"):
            print("Okay. Done.")
            data = shared_state.get_data()
            if not data:
                print("Btw, your current dictionary is still empty.")
            else:
                last_index = max(data.keys())
                last_row = data[last_index]
                print("Btw, here are the last row of your current dictionary:")
                print(last_row)
            return
