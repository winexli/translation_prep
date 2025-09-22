#!/usr/bin/env python3
from add_entries import run_add_flow
from shared_state import initialize


def main() -> None:
    initialize()
    print("Subtitle manager ready.")
    print(
        "Tip: When pasting multiple lines, finish with Ctrl-D (macOS/Linux) "
        "or Ctrl-Z then Enter (Windows)."
    )
    run_add_flow()


if __name__ == "__main__":
    main()
