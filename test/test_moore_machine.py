"""
Tests for the Moore sequence-detector builder in ``moore_machine``.
``build_moore_fsm`` returns the list of states (without printing); these tests
assert on that returned structure - the transitions and per-state outputs.
"""
import os
import sys

import pytest

# Make ``import moore_machine`` work no matter how the suite is launched: the module lives one
# directory up from this test file.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from moore_machine import build_moore_fsm  # noqa: E402


# The detector for "1011" has 5 states (A..E): n+1, where E is the accept state.
# Expected transitions and the per-state output for each state, in order.
#   name: (nextOn0, nextOn1, output)
EXPECTED_1011 = {
    "A": ("A", "B", 0),
    "B": ("C", "B", 0),
    "C": ("A", "D", 0),
    "D": ("C", "E", 0),
    "E": ("C", "B", 1),  # accept state - output lives on the state, not the edge
}


def test_state_names_and_matched_prefixes():
    states = build_moore_fsm("1011")
    assert [s.name for s in states] == ["A", "B", "C", "D", "E"]
    # Each state i represents having matched the first i chars of the pattern.
    assert [s.matched for s in states] == ["", "1", "10", "101", "1011"]


@pytest.mark.parametrize("name,nextOn0,nextOn1,output", [
    (name, *vals) for name, vals in EXPECTED_1011.items()
])
def test_transitions_and_outputs_for_1011(name, nextOn0, nextOn1, output):
    states = {s.name: s for s in build_moore_fsm("1011")}
    state = states[name]
    assert state.nextOn0 == nextOn0
    assert state.nextOn1 == nextOn1
    assert state.output == output


def test_only_accept_state_outputs_one():
    # Exactly one state (the last, fully-matched one) has output 1.
    states = build_moore_fsm("1011")
    ones = [s.name for s in states if s.output == 1]
    assert ones == ["E"]


@pytest.mark.parametrize("seq,expected_states", [
    ("1", 2),
    ("11", 3),
    ("1011", 5),
])
def test_state_count_is_pattern_length_plus_one(seq, expected_states):
    # A Moore detector needs one extra accept state: n+1 states.
    assert len(build_moore_fsm(seq)) == expected_states


def test_single_bit_pattern():
    # "1": states A (start) and B (accept, output 1). A 1 reaches the accept state.
    states = build_moore_fsm("1")
    assert [s.name for s in states] == ["A", "B"]
    a, b = states
    assert (a.nextOn0, a.nextOn1) == ("A", "B")
    assert a.output == 0
    assert (b.nextOn0, b.nextOn1) == ("A", "B")
    assert b.output == 1


def test_overlapping_pattern():
    # "11" exercises longest_prefix_match: from the accept state C, another 1 keeps
    # the overlap and stays in C, while a 0 resets to the start.
    states = {s.name: s for s in build_moore_fsm("11")}
    assert states["A"].nextOn1 == "B"
    assert states["B"].nextOn1 == "C"
    assert states["C"].nextOn1 == "C"
    assert states["C"].nextOn0 == "A"
    assert states["C"].output == 1


@pytest.mark.parametrize("bad", ["", "abc", "012", " 10", "10 ", "2"])
def test_rejects_non_binary_seq(bad):
    # The builder validates its own input rather than producing a degenerate machine.
    with pytest.raises(ValueError):
        build_moore_fsm(bad)
