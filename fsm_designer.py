"""
FSM Designer

This serves as the entry point for the FSM Designer.

It prompts the user for a binary string, then for the machine type (Moore or
Mealy), and hands off to run the machine. The actual FSM simulation is not
built yet; for now the run step is a placeholder.
"""


def get_binary_string() -> str:
    while True:
        binary_string = input("Enter a binary string: ")
        if all(bit in "01" for bit in binary_string):
            return binary_string
        print("Invalid input - use only 0s and 1s (e.g. 101010).")


def select_machine_type() -> str:
    while True:
        choice = input("Select machine type - [1] Moore or [2] Mealy: ").strip().lower()
        if choice in ["1", "2", "moore", "mealy"]:
            return choice
        print("Invalid choice - enter 'moore'/'1' or 'mealy'/'2'.")


def main():
    binary_string = get_binary_string()
    machine_type = select_machine_type()
    print(f"Running {machine_type} machine with input: {binary_string}")


if __name__ == "__main__":
    main()
