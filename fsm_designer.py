"""FSM Designer — entry point.

Prompts the user for a binary string, then for the machine type (Moore or
Mealy), and hands off to run the machine. The actual FSM simulation is not
built yet; for now the run step is a placeholder.
"""


def get_binary_string() -> str:
    """Prompt until the user enters a non-empty string of only 0s and 1s."""
    while True:
        value = input("Enter a binary string (0s and 1s): ").strip()
        if value and set(value) <= {"0", "1"}:
            return value
        print("Invalid input - use only 0s and 1s (e.g. 101010).")


def select_machine_type() -> str:
    """Prompt until the user picks a machine type. Returns 'moore' or 'mealy'."""
    while True:
        choice = input("Select machine type - [1] Moore or [2] Mealy: ").strip().lower()
        if choice in ("1", "moore"):
            return "moore"
        if choice in ("2", "mealy"):
            return "mealy"
        print("Invalid choice - enter 'moore'/'1' or 'mealy'/'2'.")


def main() -> None:
    binary_string = get_binary_string()
    machine_type = select_machine_type()

    # TODO: build the actual FSM here (Moore vs Mealy simulation).
    print(f"Running {machine_type.capitalize()} machine on input: {binary_string}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
