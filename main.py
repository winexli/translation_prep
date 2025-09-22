#!/usr/bin/env python3
from add_entries import run_add_flow
from shared_state import initialize, save, get_plate


def main() -> None:
    print("Hi there! What is your plate number?")
    plate = input().strip()

    existed = initialize(plate)
    if existed:
        print(f"OK! Let's work on {plate} : )")
    else:
        print(f"Awesome!  New dictionary {plate} created! : )")

    print("Subtitle manager ready.")
    print(
        "Tip: When pasting multiple lines, finish with Ctrl-D (macOS/Linux) "
        "or Ctrl-Z then Enter (Windows)."
    )

    try:
        run_add_flow()
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl-C
        print()
    finally:
        save()
        print(f"Woohoo! {get_plate()} just got stored! : )")


if __name__ == "__main__":
    main()
