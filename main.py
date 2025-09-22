# main.py
from shared_state import initialize, get_data
from add_entries import run_add_flow

def main():
    initialize()
    print("Yay! I'm ready!")
    run_add_flow()

if __name__ == "__main__":
    main()
