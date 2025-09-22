# translation_prep
Here’s a full `README.md` you can copy and paste directly:

```markdown
# Subtitle Management System

A modular Python-based CLI system for managing subtitles.  
It helps you take raw transcript text (with timestamps), structure it, attach bilingual translations (English + Chinese), persist across sessions, and export into different formats.

---

## Features

- **Interactive entry flow**
  - Add timestamped English lines.
  - Attach Chinese lines to existing entries by number.
- **Persistent storage**
  - Dictionaries are tied to a *plate number* (like a project/session ID).
  - Each run starts by asking for a plate number:
    - If a dictionary with that name exists, it is loaded.
    - If not, a new one is created.
- **Automatic saving**
  - Whenever you exit, the dictionary is saved locally (JSON in `data/`).
- **Export options**
  - After finishing entry, the system asks what you’d like to export:
    1. `Full_Dictionary.md` – all fields as a Markdown table.
    2. `Number_English.cvs` – number + English only.
    3. `Number_Chinese.cvs` – number + Chinese only.
    4. `Timestamp_Chinese.txt` – timestamp + Chinese.
    5. `Timestamp_English.txt` – timestamp + English.
    6. `CHI.srt` – timestamped SRT (Chinese).
    7. `ENG.srt` – timestamped SRT (English).
  - All exports are saved to **`/Users/wine/Desktop`**.

---

## Project Structure

```

translation\_prep/
├── main.py          # Entry point: handles plate number selection & save
├── add\_entries.py   # Interactive flows for adding English/Chinese lines
├── shared\_state.py  # Thread-safe store, JSON persistence by plate number
├── export\_utils.py  # Export logic for Markdown/CSV/TXT/SRT
└── data/            # Auto-created folder for persistent dictionaries

````

---

## Usage

1. **Run the program**:
   ```bash
   python3 main.py
````

2. **Plate number**:
   Enter a string (e.g., `ABC123`).

   * If it exists, you’ll continue where you left off.
   * If not, a new dictionary will be created.

3. **Add entries**:

   * Choose whether to add timestamped English or numbered Chinese.
   * Paste multiple lines, finish with:

     * `Ctrl-D` on macOS/Linux
     * `Ctrl-Z` + `Enter` on Windows

4. **Finish**:

   * When you choose not to add more, you’ll see the last row.
   * Then you’ll be asked which export format you want.

5. **Export**:

   * Enter the number of the export type.
   * The file is saved to `/Users/wine/Desktop`.

---

## Example Flow

```
$ python3 main.py
Hi there! What is your plate number?
ABC123
Awesome!  New dictionary ABC123 created! : )
Subtitle manager ready.
Tip: When pasting multiple lines, finish with Ctrl-D (macOS/Linux) or Ctrl-Z then Enter (Windows).
Time to add stuff?
yes or no
yes
What is your input content?
Option 1: Timestamp and English
Option 2: Number and Chinese
```

Later:

```
Okay. Done.
Btw, here is the last row of your current dictionary.
{'number': '1', 'timestamp': '[00:00:01.000]', 'en': 'Hello world', 'zh': ''}
I wonder what I should export… 0_o
Option 1: Full_Dictionary.md
Option 2: Number_English.cvs
...
```

---

## Requirements

* Python **3.8+**
* No external dependencies (`pip install` not required).

*(If you are on Python 3.7, install `typing_extensions` to support `TypedDict`.)*

```bash
pip install typing_extensions
```

---

## Notes

* All dictionaries are stored in `data/` as JSON.
* Exports always go to `/Users/wine/Desktop`.
* SRT exports automatically calculate end times as the start time of the next entry minus 1 ms (or +2 seconds for the last entry).
