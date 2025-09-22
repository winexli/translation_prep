from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import shared_state

# Absolute export directory (as requested)
EXPORT_DIR = Path("/Users/wine/Desktop")


def run_export_flow() -> None:
    """
    Prompt the user for what to export. Accepts a single integer 1..7.
    If invalid once, ask again. If invalid twice total, say 'Alright. Bye!' and exit.
    On success, write the file to EXPORT_DIR and print the success line, then return.
    """
    print("I wonder what I should export… 0_o")
    print("Option 1: Full_Dictionary.md")
    print("Option 2: Number_English.md")
    print("Option 3: Number_Chinese.md")
    print("Option 4: Timestamp_Chinese.txt")
    print("Option 5: Timestamp_English.txt")
    print("Option 6: CHI.srt")
    print("Option 7: ENG.srt")

    attempts = 0
    while True:
        choice = input().strip()
        if choice in {str(i) for i in range(1, 8)}:
            _handle_export_choice(int(choice))
            print("Export finished >< See you next time~~")
            return
        attempts += 1
        if attempts >= 2:
            print("Alright. Bye!")
            return
        print("Say that again?")


def _handle_export_choice(n: int) -> None:
    data = shared_state.get_data()
    plate = shared_state.get_plate() or "unknown"
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    if n == 1:
        # Full_Dictionary.md (markdown table with Number | Timestamp | English | Chinese)
        path = EXPORT_DIR / f"{plate}_Full_Dictionary.md"
        content = _make_markdown_table(
            headers=["Number", "Timestamp", "English", "Chinese"],
            rows=[
                (str(k), v["timestamp"], v["en"], v["zh"])
                for k, v in sorted(data.items(), key=lambda kv: kv[0])
            ],
        )
        path.write_text(content, encoding="utf-8")

    elif n == 2:
        # Number_English.md (markdown table Number | English)
        path = EXPORT_DIR / f"{plate}_Number_English.md"
        content = _make_markdown_table(
            headers=["Number", "English"],
            rows=[
                (str(k), v["en"]) for k, v in sorted(data.items(), key=lambda kv: kv[0])
            ],
        )
        path.write_text(content, encoding="utf-8")

    elif n == 3:
        # Number_Chinese.md (markdown table Number | Chinese)
        path = EXPORT_DIR / f"{plate}_Number_Chinese.md"
        content = _make_markdown_table(
            headers=["Number", "Chinese"],
            rows=[
                (str(k), v["zh"]) for k, v in sorted(data.items(), key=lambda kv: kv[0])
            ],
        )
        path.write_text(content, encoding="utf-8")

    elif n == 4:
        # Timestamp_Chinese.txt (markdown table Timestamp | Chinese)
        path = EXPORT_DIR / f"{plate}_Timestamp_Chinese.txt"
        content = _make_markdown_table(
            headers=["Timestamp", "Chinese"],
            rows=[
                (v["timestamp"], v["zh"])
                for _, v in sorted(data.items(), key=lambda kv: kv[0])
            ],
        )
        path.write_text(content, encoding="utf-8")

    elif n == 5:
        # Timestamp_English.txt (markdown table Timestamp | English)
        path = EXPORT_DIR / f"{plate}_Timestamp_English.txt"
        content = _make_markdown_table(
            headers=["Timestamp", "English"],
            rows=[
                (v["timestamp"], v["en"])
                for _, v in sorted(data.items(), key=lambda kv: kv[0])
            ],
        )
        path.write_text(content, encoding="utf-8")

    elif n == 6:
        # CHI.srt (SRT using timestamp + zh)
        path = EXPORT_DIR / f"{plate}_CHI.srt"
        srt = _make_srt(data, text_key="zh")
        path.write_text(srt, encoding="utf-8")

    elif n == 7:
        # ENG.srt (SRT using timestamp + en)
        path = EXPORT_DIR / f"{plate}_ENG.srt"
        srt = _make_srt(data, text_key="en")
        path.write_text(srt, encoding="utf-8")

    else:
        # Should not occur; handled by caller
        pass


def _make_markdown_table(headers: List[str], rows: List[Tuple[str, ...]]) -> str:
    """
    Produce a GitHub-flavored markdown table string for given headers and rows.
    Empty entries are kept as empty cells.
    """
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join("---" for _ in headers) + " |"
    row_lines = []
    for row in rows:
        cells = ["" if (cell is None) else str(cell) for cell in row]
        row_lines.append("| " + " | ".join(cells) + " |")
    return "\n".join([header_line, sep_line, *row_lines]) + "\n"


def _make_srt(data: Dict[int, shared_state.Row], text_key: str) -> str:
    """
    Create SRT text using each row's single timestamp as the start time.
    The end time is (next row's start minus 1ms), or start+2s for the last row.
    """
    items = sorted(data.items(), key=lambda kv: kv[0])
    # Parse timestamps into datetimes (base date arbitrary)
    starts = []
    for _, row in items:
        starts.append(_parse_timestamp(row["timestamp"]))

    lines: List[str] = []
    for i, (idx, row) in enumerate(items, start=1):
        start_dt = starts[i - 1]
        if i - 1 < len(items) - 1:
            end_dt = starts[i] - timedelta(milliseconds=1)
        else:
            end_dt = start_dt + timedelta(seconds=2)

        start_str = _fmt_srt_time(start_dt)
        end_str = _fmt_srt_time(end_dt)
        text = row.get(text_key, "") or ""

        lines.append(str(i))
        lines.append(f"{start_str} --> {end_str}")
        lines.append(text)
        lines.append("")

    return "\n".join(lines).rstrip() + ("\n" if lines else "")


def _parse_timestamp(bracketed_ts: str) -> datetime:
    """
    Convert a stored timestamp like "[HH:MM:SS.mmm]" into a datetime with ms.
    """
    s = bracketed_ts.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    if "," in s:
        s = s.replace(",", ".")
    return datetime.strptime(s, "%H:%M:%S.%f")


def _fmt_srt_time(dt: datetime) -> str:
    """
    Format datetime to SRT timestamp: HH:MM:SS,mmm
    """
    return dt.strftime("%H:%M:%S,") + f"{int(dt.microsecond / 1000):03d}"
