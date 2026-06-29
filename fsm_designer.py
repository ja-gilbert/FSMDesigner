"""
FSM Designer

This serves as the entry point for the FSM Designer.

It prompts the user for a binary string, then for the machine type (Moore or
Mealy), and hands off to run the machine. The actual FSM simulation is not
built yet; for now the run step is a placeholder.
"""

from mealy_machine import generate_mealy_fsm


def get_binary_string() -> str:
    while True:
        binary_string = input("Enter a binary string: ")
        if binary_string and all(bit in "01" for bit in binary_string):
            return binary_string
        print("Invalid input - use only 0s and 1s (e.g. 101010).")


def select_machine_type() -> str:
    canonical = {"1": "moore", "moore": "moore", "2": "mealy", "mealy": "mealy"}
    while True:
        choice = input("Select machine type - [1] Moore or [2] Mealy: ").strip().lower()
        if choice in canonical:
            return canonical[choice]
        print("Invalid choice - enter 'moore'/'1' or 'mealy'/'2'.")


def main():
    binary_string = get_binary_string()
    machine_type = select_machine_type()
    if machine_type == "mealy":
        generate_mealy_fsm(binary_string)
    else:
        print("Moore machine not implemented yet.")


if __name__ == "__main__":
    main()
