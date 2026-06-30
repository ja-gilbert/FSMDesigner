from utils import state_letter, longest_prefix_match, validate_binary_seq

class MealyMachine:
    def __init__(self):
        self.name = ""
        self.matched = ""
        self.output = 0
        self.outputOn0 = 0
        self.outputOn1 = 0
        self.nextOn0 = ""
        self.nextOn1 = ""
    
def build_mealy_fsm(seq):
    """Build the Mealy sequence-detector states for ``seq`` and return them."""
    validate_binary_seq(seq)
    n = len(seq)
    states = []

    # Create n states (0 .. n-1)
    for i in range(n):
        s = MealyMachine()
        s.name = state_letter(i)
        s.matched = seq[:i]
        s.output = 0
        s.outputOn0 = 0
        s.outputOn1 = 0
        states.append(s)
        
    # Build transitions
    for i in range(n):
        for bit in ['0', '1']:
            candidate = states[i].matched + bit
            next_len = longest_prefix_match(seq, candidate)

            # output logic - 1 if we just completed the pattern.
            output_value = 1 if candidate == seq else 0

            # Ensure that the next_len stays within bounds
            if next_len >= n:
                next_len = longest_prefix_match(seq, seq[1:])

            next_state = state_letter(next_len)

            if bit == '0':
                states[i].nextOn0 = next_state
                states[i].outputOn0 = output_value
            else:
                states[i].nextOn1 = next_state
                states[i].outputOn1 = output_value

    return states


def print_mealy_table(states):
    """Print the transition table for already-built Mealy ``states``."""
    print("\nTransition Table (Mealy)")
    print("-----------------------------------------------------")
    print(f"{'State':<8}{'W=0 -> Next':<16}{'W=1 -> Next':<16}{'Z(0 1)'}")
    print("-----------------------------------------------------")

    for state in states:
        print(f"{state.name:<8}{state.nextOn0:<16}{state.nextOn1:<16}{state.outputOn0} {state.outputOn1}")


def generate_mealy_fsm(seq):
    """Build the Mealy FSM for ``seq`` and print its transition table."""
    print_mealy_table(build_mealy_fsm(seq))