from utils import state_letter, longest_prefix_match, validate_binary_seq

class MooreMachine:
    def __init__(self):
        self.name = ""
        self.matched = ""
        self.output = 0
        self.nextOn0 = ""
        self.nextOn1 = ""

def build_moore_fsm(seq):
    """Build the Moore sequence-detector states for ``seq`` and return them."""
    validate_binary_seq(seq)
    n = len(seq)
    states = []

    for i in range(n + 1):
        s = MooreMachine()
        s.name = state_letter(i)
        s.matched = seq[:i]
        s.output = 1 if i == n else 0
        states.append(s)

    # Transitions
    for i in range(n + 1):
        for bit in ['0', '1']:
            candidate = states[i].matched + bit
            next_len = longest_prefix_match(seq, candidate)
            next_state = state_letter(next_len)

            if bit == '0':
                states[i].nextOn0 = next_state
            else:
                states[i].nextOn1 = next_state

    return states


def generate_moore_fsm(seq):
    """Build the Moore FSM for ``seq`` and print its transition table."""
    states = build_moore_fsm(seq)

    print("\nTransition Table (Moore)")
    print("-----------------------------------------------------")
    print(f"{'State':<8}{'W=0 -> Next':<16}{'W=1 -> Next':<16}{'Z'}")
    print("-----------------------------------------------------")

    for state in states:
        print(f"{state.name:<8}{state.nextOn0:<16}{state.nextOn1:<16}{state.output}")